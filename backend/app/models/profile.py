from sqlalchemy import Column, Integer, String, ForeignKey
from database import Base  # On importe la Base que vous avez configurée au J1

class Competence(Base):
    __tablename__ = "competences"

    id = Column(Integer, primary_key=True, index=True)
    nom = Column(String, nullable=False)        # Ex: "Python", "FastAPI"
    niveau = Column(String, nullable=True)      # Ex: "Débutant", "Intermédiaire"
    
    # Clé étrangère reliée à l'utilisateur (table "users")
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)


class Lacune(Base):
    __tablename__ = "lacunes"

    id = Column(Integer, primary_key=True, index=True)
    nom = Column(String, nullable=False)        # Ex: "PostgreSQL", "React"
    
    # Clé étrangère reliée à l'utilisateur
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)


class Disponibilite(Base):
    __tablename__ = "disponibilites"

    id = Column(Integer, primary_key=True, index=True)
    jour = Column(String, nullable=False)       # Ex: "Lundi", "Mardi"
    creneau = Column(String, nullable=False)    # Ex: "Matin", "Soir"
    
    # Clé étrangère reliée à l'utilisateur
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)