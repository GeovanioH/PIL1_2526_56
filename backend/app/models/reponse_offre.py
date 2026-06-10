from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class ReponseOffre(Base):
    """
    CDC : "Les utilisateurs doivent pouvoir répondre à des offres de mentorat
    ciblant leurs lacunes."
    """
    __tablename__ = "reponses_offres"

    id = Column(Integer, primary_key=True, index=True)

    offre_id = Column(Integer, ForeignKey("offres.id", ondelete="CASCADE"), nullable=False)
    repondant_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    message = Column(Text, nullable=True)

    # "en_attente", "acceptee", "refusee"
    statut = Column(String(50), nullable=False, default="en_attente")

    created_at = Column(DateTime, server_default=func.now())

    offre = relationship("Offre", back_populates="reponses")
    repondant = relationship("User", back_populates="reponses_offres")
