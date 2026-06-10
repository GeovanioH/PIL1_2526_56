import os
import uuid

from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect, Query, UploadFile, File
from sqlalchemy.orm import Session
from sqlalchemy.sql import func

from app.database import get_db, SessionLocal, PUBLIC_URL
from app.models.conversations import Conversation
from app.models.messages import Message
from app.models.participants_conversation import ParticipantConversation
from app.models.notification import Notification
from app.models.user import User
from app.models.blocage import Blocage
from app.schemas.message import MessageCreate, MessageResponse
from app.services.security_service import get_current_user, get_user_from_websocket_token
from app.websockets import manager


router = APIRouter(prefix="/conversations", tags=["Conversations"])


def _get_participant_ids(conversation: Conversation) -> list:
    return [p.utilisateur_id for p in conversation.participants]


def _blocked_related_ids(db: Session, user_id: int) -> set:
    """Ids des utilisateurs en relation de blocage avec user_id (dans un sens ou l'autre)."""
    ids = {r[0] for r in db.query(Blocage.bloque_id).filter(Blocage.bloqueur_id == user_id).all()}
    ids |= {r[0] for r in db.query(Blocage.bloqueur_id).filter(Blocage.bloque_id == user_id).all()}
    return ids


def _cutoff(db: Session, conversation_id: int, user_id: int):
    """Date de suppression de la conversation par cet utilisateur (None si non supprimée).
    Il ne voit que les messages postérieurs à cette date."""
    part = db.query(ParticipantConversation).filter(
        ParticipantConversation.conversation_id == conversation_id,
        ParticipantConversation.utilisateur_id == user_id
    ).first()
    return part.supprime_le if part else None


def _destinataires_a_notifier(db: Session, conversation: Conversation, sender_id: int) -> list:
    """Destinataires pour qui le prochain message sera le premier VISIBLE :
    nouveau contact, ou conversation qu'ils avaient supprimée. À appeler AVANT
    d'ajouter le nouveau message."""
    a_notifier = []
    for pid in _get_participant_ids(conversation):
        if pid == sender_id:
            continue
        cutoff = _cutoff(db, conversation.id, pid)
        q = db.query(Message).filter(Message.conversation_id == conversation.id)
        if cutoff:
            q = q.filter(Message.envoye_a > cutoff)
        if q.first() is None:
            a_notifier.append(pid)
    return a_notifier


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

    ids_a_ajouter = set(participant_ids)
    ids_a_ajouter.add(current_user.id)

    # Réutilise une conversation existante avec exactement les mêmes participants
    # (évite les doublons après une suppression). On la ré-affiche pour l'utilisateur.
    mes_convs = db.query(ParticipantConversation.conversation_id).filter(
        ParticipantConversation.utilisateur_id == current_user.id
    ).all()
    for (cid,) in mes_convs:
        pids = {p.utilisateur_id for p in db.query(ParticipantConversation).filter(
            ParticipantConversation.conversation_id == cid
        ).all()}
        if pids == ids_a_ajouter:
            # On réutilise l'id, sans toucher à la date de suppression :
            # l'utilisateur repart "à neuf" (il ne reverra pas l'ancien historique).
            return {"message": "Conversation existante", "conversation_id": cid}

    conversation = Conversation()
    db.add(conversation)
    db.commit()
    db.refresh(conversation)

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
    cutoffs = {p.conversation_id: p.supprime_le for p in participations}

    conversation_ids = list(cutoffs.keys())
    conversations = db.query(Conversation).filter(Conversation.id.in_(conversation_ids)).all()

    # Blocages dans chaque sens
    j_ai_bloque = {r[0] for r in db.query(Blocage.bloque_id).filter(Blocage.bloqueur_id == current_user.id).all()}
    m_ont_bloque = {r[0] for r in db.query(Blocage.bloqueur_id).filter(Blocage.bloque_id == current_user.id).all()}

    result = []
    for conv in conversations:
        cutoff = cutoffs.get(conv.id)

        # Dernier message VISIBLE pour moi (postérieur à ma suppression éventuelle)
        last_q = db.query(Message).filter(Message.conversation_id == conv.id)
        if cutoff:
            last_q = last_q.filter(Message.envoye_a > cutoff)
        last = last_q.order_by(Message.envoye_a.desc()).first()

        # Si j'ai supprimé et qu'aucun nouveau message n'est arrivé : conversation masquée
        if cutoff and last is None:
            continue

        participant_ids = _get_participant_ids(conv)
        autres = set(participant_ids) - {current_user.id}
        bloque_par_moi = bool(j_ai_bloque.intersection(autres))
        bloque_par_autre = bool(m_ont_bloque.intersection(autres))

        # Messages non lus (seulement ceux visibles pour moi)
        unread_q = db.query(Message).filter(
            Message.conversation_id == conv.id,
            Message.expediteur_id != current_user.id,
            Message.lu == False
        )
        if cutoff:
            unread_q = unread_q.filter(Message.envoye_a > cutoff)
        unread = unread_q.count()

        result.append({
            "id": conv.id,
            "created_at": conv.created_at,
            "participants": _get_participant_ids(conv),
            "messages_non_lus": unread,
            "dernier_message": (
                (last.contenu or ("📎 " + (last.fichier_nom or "Fichier"))) if last else None
            ),
            "dernier_message_at": last.envoye_a if last else None,
            "bloque_par_moi": bloque_par_moi,
            "bloque_par_autre": bloque_par_autre,
        })

    # Les conversations avec activité la plus récente en premier
    result.sort(
        key=lambda c: c["dernier_message_at"] or c["created_at"],
        reverse=True
    )

    return result


# ── SUPPRIMER UNE CONVERSATION ────────────────────────────────────────────────

@router.delete("/{conversation_id}", status_code=204)
def delete_conversation(
    conversation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Supprime la conversation UNIQUEMENT pour l'utilisateur courant
    (l'autre participant la conserve). Elle réapparaîtra s'il reçoit un nouveau message.
    """
    participation = db.query(ParticipantConversation).filter(
        ParticipantConversation.conversation_id == conversation_id,
        ParticipantConversation.utilisateur_id == current_user.id
    ).first()
    if not participation:
        raise HTTPException(status_code=404, detail="Conversation introuvable")

    # On mémorise la date (horloge BD, comme envoye_a) : les messages antérieurs
    # ne seront plus visibles pour moi.
    participation.supprime_le = func.now()
    db.commit()


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

    # Blocage : impossible d'écrire à un utilisateur bloqué (ou qui nous a bloqué)
    autres_ids = set(_get_participant_ids(conversation)) - {current_user.id}
    if _blocked_related_ids(db, current_user.id).intersection(autres_ids):
        raise HTTPException(status_code=403, detail="Messagerie indisponible : utilisateur bloqué")

    # Notifier chaque destinataire pour qui CE message est le premier VISIBLE :
    # nouveau contact, ou conversation qu'il avait supprimée (= nouvelle conversation chez lui).
    a_notifier = _destinataires_a_notifier(db, conversation, current_user.id)

    message = Message(
        contenu=payload.contenu,
        expediteur_id=current_user.id,
        conversation_id=conversation_id
    )
    db.add(message)

    for participant_id in a_notifier:
        db.add(Notification(
            user_id=participant_id,
            type="nouveau_message",
            contenu=f"{current_user.prenom} {current_user.nom} vous a envoyé un message",
            reference_id=conversation_id
        ))

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


# ── ENVOYER UN FICHIER (pièce jointe) ─────────────────────────────────────────

_EXT_AUTORISEES = {
    ".jpg", ".jpeg", ".png", ".gif", ".webp",
    ".pdf", ".doc", ".docx", ".ppt", ".pptx", ".xls", ".xlsx",
    ".txt", ".csv", ".zip", ".rar",
    # Audio (messages vocaux)
    ".webm", ".ogg", ".oga", ".mp3", ".wav", ".m4a", ".aac",
}


@router.post("/{conversation_id}/messages/fichier", response_model=MessageResponse)
async def send_file_message(
    conversation_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation introuvable")
    if current_user.id not in _get_participant_ids(conversation):
        raise HTTPException(status_code=403, detail="Vous n'êtes pas participant de cette conversation")

    autres_ids = set(_get_participant_ids(conversation)) - {current_user.id}
    if _blocked_related_ids(db, current_user.id).intersection(autres_ids):
        raise HTTPException(status_code=403, detail="Messagerie indisponible : utilisateur bloqué")

    ext = os.path.splitext(file.filename or "")[1].lower()
    if ext not in _EXT_AUTORISEES:
        raise HTTPException(status_code=400, detail="Type de fichier non autorisé")

    contenu_fichier = file.file.read()
    if len(contenu_fichier) > 5 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="Fichier trop lourd (5 Mo maximum)")

    os.makedirs("uploads", exist_ok=True)
    filename = f"{uuid.uuid4().hex}{ext}"
    with open(os.path.join("uploads", filename), "wb") as f:
        f.write(contenu_fichier)

    fichier_url = f"{PUBLIC_URL}/uploads/{filename}"

    # Notifier les destinataires pour qui ce sera le premier message visible
    a_notifier = _destinataires_a_notifier(db, conversation, current_user.id)

    message = Message(
        contenu="",
        expediteur_id=current_user.id,
        conversation_id=conversation_id,
        fichier_url=fichier_url,
        fichier_nom=file.filename,
    )
    db.add(message)

    for participant_id in a_notifier:
        db.add(Notification(
            user_id=participant_id,
            type="nouveau_message",
            contenu=f"{current_user.prenom} {current_user.nom} vous a envoyé un fichier",
            reference_id=conversation_id
        ))

    db.commit()
    db.refresh(message)

    await manager.broadcast(conversation_id, {
        "id": message.id,
        "contenu": message.contenu,
        "expediteur_id": message.expediteur_id,
        "conversation_id": conversation_id,
        "envoye_a": message.envoye_a.isoformat() if message.envoye_a else None,
        "fichier_url": message.fichier_url,
        "fichier_nom": message.fichier_nom,
    })

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

    # On ne montre que les messages postérieurs à une éventuelle suppression côté utilisateur
    cutoff = _cutoff(db, conversation_id, current_user.id)
    msg_q = db.query(Message).filter(Message.conversation_id == conversation_id)
    if cutoff:
        msg_q = msg_q.filter(Message.envoye_a > cutoff)

    messages = msg_q.order_by(Message.envoye_a.asc()).offset((page - 1) * limit).limit(limit).all()

    # Marquer comme lus
    for msg in messages:
        if msg.expediteur_id != current_user.id and not msg.lu:
            msg.lu = True
    db.commit()

    return messages


# ── MODIFIER UN MESSAGE ───────────────────────────────────────────────────────

@router.put("/{conversation_id}/messages/{message_id}", response_model=MessageResponse)
async def edit_message(
    conversation_id: int,
    message_id: int,
    payload: MessageCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    message = db.query(Message).filter(
        Message.id == message_id,
        Message.conversation_id == conversation_id
    ).first()
    if not message:
        raise HTTPException(status_code=404, detail="Message introuvable")
    if message.expediteur_id != current_user.id:
        raise HTTPException(status_code=403, detail="Vous ne pouvez modifier que vos propres messages")

    message.contenu = payload.contenu
    db.commit()
    db.refresh(message)

    await manager.broadcast(conversation_id, {
        "event": "edit",
        "id": message.id,
        "contenu": message.contenu
    })
    return message


# ── SUPPRIMER UN MESSAGE ──────────────────────────────────────────────────────

@router.delete("/{conversation_id}/messages/{message_id}", status_code=204)
async def delete_message(
    conversation_id: int,
    message_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    message = db.query(Message).filter(
        Message.id == message_id,
        Message.conversation_id == conversation_id
    ).first()
    if not message:
        raise HTTPException(status_code=404, detail="Message introuvable")
    if message.expediteur_id != current_user.id:
        raise HTTPException(status_code=403, detail="Vous ne pouvez supprimer que vos propres messages")

    db.delete(message)
    db.commit()

    await manager.broadcast(conversation_id, {"event": "delete", "id": message_id})


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
