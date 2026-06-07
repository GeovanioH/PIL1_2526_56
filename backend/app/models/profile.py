#Importation des fonctions à utiliser des bibliothèques sqlachemy et database
from sqlalchemy import Column, Integer, String, ForeignKey
from database import Base  

#Création du nouveau type de variable Competence et de la table competences avec ses attributs et la clé étrangère de la table users
class Competence(Base):
    __tablename__ = "competences"
    id = Column(Integer, primary_key=True, index=True)
    nom = Column(String, nullable=False)        
    niveau = Column(String, nullable=True)      
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

#Création du nouveau type de variable Lacune et de la table lacunes avec ses attributs et la clé étrangère de la table users
class Lacune(Base):
    __tablename__ = "lacunes"
    id = Column(Integer, primary_key=True, index=True)
    nom = Column(String, nullable=False)       
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

#Création du nouveau type de variable Disponibilite et de la table disponibilites avec ses attributs et la clé étrangère de la table users
class Disponibilite(Base):
    __tablename__ = "disponibilites"
    id = Column(Integer, primary_key=True, index=True)
    jour = Column(String, nullable=False)   
    creneau = Column(String, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)