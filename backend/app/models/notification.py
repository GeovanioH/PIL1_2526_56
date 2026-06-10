from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class Notification(Base):
    """
    Notifications persistantes — stocke les notifications non lues
    même quand l'utilisateur est déconnecté.
    """
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    # "nouveau_message", "reponse_offre", "reponse_demande", "match"
    type = Column(String(100), nullable=False)

    contenu = Column(String(500), nullable=False)

    # ID de la ressource liée (conversation, offre, demande...)
    reference_id = Column(Integer, nullable=True)

    lu = Column(Boolean, default=False, nullable=False)

    created_at = Column(DateTime, server_default=func.now())

    user = relationship("User", back_populates="notifications")
