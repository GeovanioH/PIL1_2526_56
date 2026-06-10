from sqlalchemy import Column, Integer, DateTime, ForeignKey
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

    # Suppression "côté utilisateur" : date à laquelle CE participant a supprimé la
    # conversation. Il ne verra plus que les messages postérieurs à cette date — un
    # nouveau message apparaît alors comme une nouvelle conversation. L'autre garde tout.
    supprime_le = Column(DateTime, nullable=True)

    conversation = relationship(
        "Conversation",
        back_populates="participants"
    )

    user = relationship(
        "User",
        foreign_keys=[utilisateur_id],
        back_populates="participations"
    )
