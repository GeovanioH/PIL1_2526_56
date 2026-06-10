from pydantic import BaseModel, EmailStr


class RegisterRequest(BaseModel):
    nom: str
    prenom: str
    email: EmailStr
    telephone: str
    password: str
    filiere: str
    niveau: str
    bio: str | None = None
    photo_url: str | None = None


class LoginRequest(BaseModel):
    email: EmailStr
    password: str
