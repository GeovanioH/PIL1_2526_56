from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional
from datetime import datetime


class RegisterRequest(BaseModel):
    nom: str
    prenom: str
    email: EmailStr
    telephone: str
    password: str
    filiere: str
    niveau: str
    bio: Optional[str] = None
    photo_url: Optional[str] = None
    competences: Optional[list[str]] = None
    lacunes: Optional[list[str]] = None
    disponibilites: Optional[list[str]] = None

    @field_validator("password")
    @classmethod
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError("Le mot de passe doit contenir au moins 8 caractères")
        return v

    @field_validator("telephone")
    @classmethod
    def validate_telephone(cls, v):
        # Accepte formats internationaux : +22960XXXXXX, 06XXXXXXXX, etc.
        cleaned = v.replace(" ", "").replace("-", "")
        if not (cleaned.lstrip("+").isdigit() and 8 <= len(cleaned.lstrip("+")) <= 15):
            raise ValueError("Numéro de téléphone invalide")
        return cleaned


class LoginRequest(BaseModel):
    identifiant: str
    password: str


class UserUpdateRequest(BaseModel):
    nom: Optional[str] = None
    prenom: Optional[str] = None
    telephone: Optional[str] = None
    filiere: Optional[str] = None
    niveau: Optional[str] = None
    bio: Optional[str] = None
    photo_url: Optional[str] = None
    competences: Optional[list[str]] = None
    lacunes: Optional[list[str]] = None
    disponibilites: Optional[list[str]] = None


class UserResponse(BaseModel):
    id: int
    nom: str
    prenom: str
    email: str
    telephone: str
    filiere: str
    niveau: str
    bio: Optional[str] = None
    photo_url: Optional[str] = None
    competences: Optional[list[str]] = None
    lacunes: Optional[list[str]] = None
    disponibilites: Optional[list[str]] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True
