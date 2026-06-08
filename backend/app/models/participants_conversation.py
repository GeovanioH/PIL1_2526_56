from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class ParticipantConversation(Base):
    __tablename__ = "participants_conversation"

    id = Column(Integer, primary_key=True, index=True)

    conversation_id = Column(
        Integer,
        ForeignKey("conversations.id", ondelete="CASCADE"),
        nullable=False
    )

    utilisateur_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )

    conversation = relationship(
        "Conversation",
        back_populates="participants"
    )

    user = relationship(
        "User",
        foreign_keys=[utilisateur_id]
    )