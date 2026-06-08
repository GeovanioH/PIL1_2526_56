from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class ReponseDemande(Base):
    """
    CDC : "Les utilisateurs doivent pouvoir répondre à des demandes de mentorat
    ciblant leurs compétences."
    """
    __tablename__ = "reponses_demandes"

    id = Column(Integer, primary_key=True, index=True)

    demande_id = Column(Integer, ForeignKey("demandes.id", ondelete="CASCADE"), nullable=False)
    repondant_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    message = Column(Text, nullable=True)

    # "en_attente", "acceptee", "refusee"
    statut = Column(String(50), nullable=False, default="en_attente")

    created_at = Column(DateTime, server_default=func.now())

    demande = relationship("Demande", back_populates="reponses")
    repondant = relationship("User", back_populates="reponses_demandes")
