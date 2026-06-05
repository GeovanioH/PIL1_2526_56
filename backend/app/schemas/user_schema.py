#Importation des fonctions à utiliser des bibliothèques Pydantic et typing
from pydantic import BaseModel, EmailStr
from typing import List, Optional

#Création d'un nouveau type de variable où l'utilisateur remplit des infos
class ProfileBase(BaseModel):
    name: str
    email: EmailStr
    bio: Optional[str] = None
    competences: List[str] = []
    lacunes: List[str] = []
    disponibilites: List[str] = []

# Création d'un nouveau type de variable qui servira pour les mises à jour ou modifications d'infos
class ProfileUpdate(BaseModel):
    name: Optional[str] = None
    bio: Optional[str] = None
    competences: Optional[List[str]] = None
    lacunes: Optional[List[str]] = None
    disponibilites: Optional[List[str]] = None