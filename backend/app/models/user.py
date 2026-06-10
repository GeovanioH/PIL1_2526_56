from sqlalchemy import Column, Integer, String, Text, JSON, Boolean, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class User(Base):

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    nom = Column(String(255), nullable=False)
    prenom = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    telephone = Column(String(50), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    filiere = Column(String(255), nullable=False)
    niveau = Column(String(100), nullable=False)
    bio = Column(Text, nullable=True)
    photo_url = Column(String(500), nullable=True)
    competences = Column(JSON, nullable=True, default=list)
    lacunes = Column(JSON, nullable=True, default=list)
    disponibilites = Column(JSON, nullable=True, default=list)

    # L'utilisateur choisit d'afficher (ou non) son numéro sur son profil public
    afficher_telephone = Column(Boolean, default=False, nullable=False)

    # Reset mot de passe
    reset_token = Column(String(255), nullable=True)
    reset_token_expires = Column(DateTime, nullable=True)

    # Refresh token
    refresh_token = Column(String(500), nullable=True)

    created_at = Column(DateTime, server_default=func.now())

    # Relations
    offres = relationship("Offre", back_populates="user", cascade="all, delete-orphan")
    demandes = relationship("Demande", back_populates="user", cascade="all, delete-orphan")
    participations = relationship("ParticipantConversation", back_populates="user", cascade="all, delete-orphan")
    notifications = relationship("Notification", back_populates="user", cascade="all, delete-orphan")
    reponses_offres = relationship("ReponseOffre", back_populates="repondant", cascade="all, delete-orphan")
    reponses_demandes = relationship("ReponseDemande", back_populates="repondant", cascade="all, delete-orphan")
