from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.conversations import Conversation
from app.models.messages import Message
from app.models.user import User
from app.schemas.message import MessageCreate, MessageResponse
from app.services.security_service import get_current_user
from app.websockets import manager


router = APIRouter(
    prefix="/conversations",
    tags=["Conversations"]
)


@router.post("/")
def create_conversation(
    participant_ids: list[int],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    participants = db.query(User).filter(
        User.id.in_(participant_ids)
    ).all()

    if len(participants) != len(participant_ids):
        raise HTTPException(
            status_code=404,
            detail="Un ou plusieurs participants sont introuvables"
        )

    conversation = Conversation()

    db.add(conversation)
    db.commit()
    db.refresh(conversation)

    conversation.participants.extend(participants)

    if current_user not in conversation.participants:
        conversation.participants.append(current_user)

    db.commit()
    db.refresh(conversation)

    return {
        "message": "Conversation créée avec succès",
        "conversation_id": conversation.id
    }


@router.post(
    "/{conversation_id}/messages",
    response_model=MessageResponse
)
async def send_message(
    conversation_id: int,
    payload: MessageCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_id
    ).first()

    if not conversation:
        raise HTTPException(
            status_code=404,
            detail="Conversation introuvable"
        )

    participant_ids = [
        participant.id
        for participant in conversation.participants
    ]

    if current_user.id not in participant_ids:
        raise HTTPException(
            status_code=403,
            detail="Vous n'êtes pas participant de cette conversation"
        )

    message = Message(
        contenu=payload.contenu,
        expediteur_id=current_user.id,
        conversation_id=conversation_id
    )

    db.add(message)
    db.commit()
    db.refresh(message)

    await manager.broadcast(
        conversation_id,
        {
            "contenu": message.contenu,
            "expediteur_id": message.expediteur_id,
            "conversation_id": conversation_id
        }
    )

    return message


@router.get(
    "/{conversation_id}/messages",
    response_model=list[MessageResponse]
)
def get_messages(
    conversation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_id
    ).first()

    if not conversation:
        raise HTTPException(
            status_code=404,
            detail="Conversation introuvable"
        )

    participant_ids = [
        participant.id
        for participant in conversation.participants
    ]

    if current_user.id not in participant_ids:
        raise HTTPException(
            status_code=403,
            detail="Accès interdit"
        )

    messages = db.query(Message).filter(
        Message.conversation_id == conversation_id
    ).all()

    return messages

@router.get("/")
def get_user_conversations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    conversations = db.query(Conversation).filter(
        Conversation.participants.any(id=current_user.id)
    ).all()

    return conversations

@router.websocket("/ws/{conversation_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    conversation_id: int
):

    await manager.connect(conversation_id, websocket)

    try:

        while True:

            data = await websocket.receive_text()

            await manager.broadcast(
                conversation_id,
                {
                    "message": data
                }
            )

    except WebSocketDisconnect:

        manager.disconnect(conversation_id, websocket)