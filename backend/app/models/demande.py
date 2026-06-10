from sqlalchemy import Column, Integer, String, Text, JSON, ForeignKey, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class Demande(Base):

    __tablename__ = "demandes"

    id = Column(Integer, primary_key=True, index=True)
    titre = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    matieres = Column(JSON, nullable=True, default=list)
    disponibilites = Column(JSON, nullable=True, default=list)
    format = Column(String(50), nullable=False, default="les deux")

    # Statut : "ouverte", "en_cours", "cloturee"
    statut = Column(String(50), nullable=False, default="ouverte")

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    user = relationship("User", back_populates="demandes")
    reponses = relationship("ReponseDemande", back_populates="demande", cascade="all, delete-orphan")
