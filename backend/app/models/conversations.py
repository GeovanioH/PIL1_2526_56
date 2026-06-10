from sqlalchemy import Column, Integer, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class Conversation(Base):

    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True)

    created_at = Column(DateTime, server_default=func.now())

    # Relation vers les messages de la conversation
    messages = relationship(
        "Message",
        back_populates="conversation",
        cascade="all, delete"
    )

    # Relation vers la table de liaison participants_conversation
    participants = relationship(
        "ParticipantConversation",
        back_populates="conversation",
        cascade="all, delete"
    )
