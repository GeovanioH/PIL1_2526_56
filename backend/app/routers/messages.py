from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect, Query
from sqlalchemy.orm import Session

from app.database import get_db, SessionLocal
from app.models.conversations import Conversation
from app.models.messages import Message
from app.models.participants_conversation import ParticipantConversation
from app.models.notification import Notification
from app.models.user import User
from app.schemas.message import MessageCreate, MessageResponse
from app.services.security_service import get_current_user, get_user_from_websocket_token
from app.websockets import manager


router = APIRouter(prefix="/conversations", tags=["Conversations"])


def _get_participant_ids(conversation: Conversation) -> list:
    return [p.utilisateur_id for p in conversation.participants]


# ── CRÉER UNE CONVERSATION ────────────────────────────────────────────────────

@router.post("/", status_code=201)
def create_conversation(
    participant_ids: list[int],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    participants = db.query(User).filter(User.id.in_(participant_ids)).all()
    if len(participants) != len(participant_ids):
        raise HTTPException(status_code=404, detail="Un ou plusieurs participants sont introuvables")

    conversation = Conversation()
    db.add(conversation)
    db.commit()
    db.refresh(conversation)

    ids_a_ajouter = set(participant_ids)
    ids_a_ajouter.add(current_user.id)

    for uid in ids_a_ajouter:
        db.add(ParticipantConversation(conversation_id=conversation.id, utilisateur_id=uid))

    db.commit()
    db.refresh(conversation)

    return {"message": "Conversation créée avec succès", "conversation_id": conversation.id}


# ── LISTE DES CONVERSATIONS ───────────────────────────────────────────────────

@router.get("/")
def get_user_conversations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    participations = db.query(ParticipantConversation).filter(
        ParticipantConversation.utilisateur_id == current_user.id
    ).all()

    conversation_ids = [p.conversation_id for p in participations]
    conversations = db.query(Conversation).filter(Conversation.id.in_(conversation_ids)).all()

    result = []
    for conv in conversations:
        # Compter les messages non lus
        unread = db.query(Message).filter(
            Message.conversation_id == conv.id,
            Message.expediteur_id != current_user.id,
            Message.lu == False
        ).count()

        result.append({
            "id": conv.id,
            "created_at": conv.created_at,
            "participants": _get_participant_ids(conv),
            "messages_non_lus": unread
        })

    return result


# ── ENVOYER UN MESSAGE ────────────────────────────────────────────────────────

@router.post("/{conversation_id}/messages", response_model=MessageResponse)
async def send_message(
    conversation_id: int,
    payload: MessageCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation introuvable")

    if current_user.id not in _get_participant_ids(conversation):
        raise HTTPException(status_code=403, detail="Vous n'êtes pas participant de cette conversation")

    message = Message(
        contenu=payload.contenu,
        expediteur_id=current_user.id,
        conversation_id=conversation_id
    )
    db.add(message)

    # Notifications persistantes pour les participants hors ligne
    for participant_id in _get_participant_ids(conversation):
        if participant_id != current_user.id:
            notif = Notification(
                user_id=participant_id,
                type="nouveau_message",
                contenu=f"{current_user.prenom} {current_user.nom} vous a envoyé un message",
                reference_id=conversation_id
            )
            db.add(notif)

    db.commit()
    db.refresh(message)

    # Diffusion temps réel
    await manager.broadcast(
        conversation_id,
        {
            "id": message.id,
            "contenu": message.contenu,
            "expediteur_id": message.expediteur_id,
            "conversation_id": conversation_id,
            "envoye_a": message.envoye_a.isoformat() if message.envoye_a else None
        }
    )

    return message


# ── HISTORIQUE DES MESSAGES (avec pagination) ─────────────────────────────────

@router.get("/{conversation_id}/messages", response_model=list[MessageResponse])
def get_messages(
    conversation_id: int,
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation introuvable")
    if current_user.id not in _get_participant_ids(conversation):
        raise HTTPException(status_code=403, detail="Accès interdit")

    messages = db.query(Message).filter(
        Message.conversation_id == conversation_id
    ).order_by(Message.envoye_a.asc()).offset((page - 1) * limit).limit(limit).all()

    # Marquer comme lus
    for msg in messages:
        if msg.expediteur_id != current_user.id and not msg.lu:
            msg.lu = True
    db.commit()

    return messages


# ── WEBSOCKET AVEC AUTHENTIFICATION ──────────────────────────────────────────

@router.websocket("/ws/{conversation_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    conversation_id: int,
    token: str = Query(...)
):
    """
    CDC : notifications en temps réel.
    Sécurité : le token JWT est passé en query param ?token=...
    Le client doit s'y connecter ainsi :
    ws://api/conversations/ws/42?token=eyJ...
    """
    db = SessionLocal()
    try:
        user = get_user_from_websocket_token(token, db)
        if user is None:
            await websocket.close(code=4001)
            return

        # Vérifier que l'utilisateur est participant
        participation = db.query(ParticipantConversation).filter(
            ParticipantConversation.conversation_id == conversation_id,
            ParticipantConversation.utilisateur_id == user.id
        ).first()

        if not participation:
            await websocket.close(code=4003)
            return

        await manager.connect(conversation_id, websocket)
        try:
            while True:
                # On écoute mais on n'attend rien d'actif du client via WS
                # (les messages sont envoyés via POST /messages)
                data = await websocket.receive_text()
                # "typing" indicator
                if data == "typing":
                    await manager.broadcast(conversation_id, {
                        "event": "typing",
                        "user_id": user.id,
                        "prenom": user.prenom
                    })
        except WebSocketDisconnect:
            manager.disconnect(conversation_id, websocket)
    finally:
        db.close()
