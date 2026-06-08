from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import Text
from sqlalchemy import JSON
from sqlalchemy.orm import relationship
from app.database import Base


class User(Base):

    __tablename__ = "users"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    nom = Column(
        String(255),
        nullable=False
    )

    prenom = Column(
        String(255),
        nullable=False
    )

    email = Column(
        String(255),
        unique=True,
        nullable=False,
        index=True
    )

    telephone = Column(
        String(50),
        nullable=False
    )

    password_hash = Column(
        String(255),
        nullable=False
    )

    filiere = Column(
        String(255),
        nullable=False
    )

    niveau = Column(
        String(100),
        nullable=False
    )

    bio = Column(
        Text,
        nullable=True
    )

    photo_url = Column(
        String(500),
        nullable=True
    )
    competences = Column(
        JSON, 
        nullable=True
    )

    lacunes = Column(
        JSON, 
        nullable=True
    )

    disponibilites = Column(
        JSON,
        nullable=True
    )
    offres = relationship(
    "Offre",
    back_populates="user"
    )

    demandes = relationship(
        "Demande",
        back_populates="user"
    )
