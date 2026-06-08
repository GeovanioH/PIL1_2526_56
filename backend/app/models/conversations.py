from sqlalchemy import Column, Integer, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True)

    created_at = Column(DateTime, server_default=func.now())

    # relations ORM
    messages = relationship(
        "Message",
        back_populates="conversation",
        cascade="all, delete"
    )

    participants = relationship(
        "ParticipantConversation",
        back_populates="conversation",
        cascade="all, delete"
    )