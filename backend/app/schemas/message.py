from pydantic import BaseModel


class MessageCreate(BaseModel):
    contenu: str


class MessageResponse(BaseModel):
    id: int
    contenu: str
    expediteur_id: int
    conversation_id: int

    class Config:
        from_attributes = True