from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class MessageCreate(BaseModel):
    contenu: str


class MessageResponse(BaseModel):
    id: int
    contenu: str
    expediteur_id: int
    conversation_id: int
    lu: bool
    envoye_a: Optional[datetime] = None

    class Config:
        from_attributes = True


class ConversationResponse(BaseModel):
    id: int
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True
