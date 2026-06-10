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
    afficher_telephone: Optional[bool] = False

    @field_validator("password")
    @classmethod
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError("Le mot de passe doit contenir au moins 8 caractères")
        return v

    @field_validator("telephone")
    @classmethod
    def validate_telephone(cls, v):
        cleaned = "".join(c for c in (v or "") if c.isdigit())
        if len(cleaned) != 10:
            raise ValueError("Le numéro de téléphone doit contenir exactement 10 chiffres")
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
    afficher_telephone: Optional[bool] = None

    @field_validator("telephone")
    @classmethod
    def validate_telephone(cls, v):
        if v is None:
            return v
        cleaned = "".join(c for c in v if c.isdigit())
        if len(cleaned) != 10:
            raise ValueError("Le numéro de téléphone doit contenir exactement 10 chiffres")
        return cleaned


class UserResponse(BaseModel):
    id: int
    nom: str
    prenom: str
    email: str
    telephone: Optional[str] = None       # masqué si l'utilisateur ne l'affiche pas
    filiere: str
    niveau: str
    bio: Optional[str] = None
    photo_url: Optional[str] = None
    competences: Optional[list[str]] = None
    lacunes: Optional[list[str]] = None
    disponibilites: Optional[list[str]] = None
    afficher_telephone: Optional[bool] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True
