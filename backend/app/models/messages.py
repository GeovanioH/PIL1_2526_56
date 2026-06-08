from sqlalchemy import Column, Integer, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)

    conversation_id = Column(
        Integer,
        ForeignKey("conversations.id", ondelete="CASCADE"),
        nullable=False
    )

    expediteur_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )

    contenu = Column(Text, nullable=False)

    lu = Column(Boolean, default=False)

    envoye_a = Column(DateTime, server_default=func.now())

    conversation = relationship(
        "Conversation",
        back_populates="messages"
    )

    expediteur = relationship(
        "User",
        foreign_keys=[expediteur_id]
    )