from sqlalchemy import Column, Integer, String, Text, JSON, ForeignKey, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class Offre(Base):

    __tablename__ = "offres"

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
    user = relationship("User", back_populates="offres")
    reponses = relationship("ReponseOffre", back_populates="offre", cascade="all, delete-orphan")
