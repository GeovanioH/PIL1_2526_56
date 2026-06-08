from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pydantic import BaseModel, field_validator
from typing import Optional
from datetime import datetime

from app.database import get_db
from app.models.user import User
from app.schemas.user import RegisterRequest
from app.services.security_service import (
    create_access_token,
    create_refresh_token,
    create_password_reset_token,
    get_current_user,
)

from passlib.context import CryptContext


router = APIRouter(prefix="/auth", tags=["Auth"])

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


# ── INSCRIPTION ───────────────────────────────────────────────────────────────

@router.post("/register", status_code=201)
def register(user_data: RegisterRequest, db: Session = Depends(get_db)):
    # CDC : unicité email
    if db.query(User).filter(User.email == user_data.email).first():
        raise HTTPException(status_code=400, detail="Cet email est déjà utilisé")

    # CDC : unicité téléphone
    if db.query(User).filter(User.telephone == user_data.telephone).first():
        raise HTTPException(status_code=400, detail="Ce numéro de téléphone est déjà utilisé")

    new_user = User(
        nom=user_data.nom,
        prenom=user_data.prenom,
        email=user_data.email,
        telephone=user_data.telephone,
        password_hash=hash_password(user_data.password),
        filiere=user_data.filiere,
        niveau=user_data.niveau,
        bio=user_data.bio,
        photo_url=user_data.photo_url,
        competences=user_data.competences or [],
        lacunes=user_data.lacunes or [],
        disponibilites=user_data.disponibilites or [],
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {"message": "Compte créé avec succès", "user_id": new_user.id}


# ── CONNEXION ─────────────────────────────────────────────────────────────────

@router.post("/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """CDC : connexion par email OU numéro de téléphone."""
    identifiant = form_data.username

    user = db.query(User).filter(
        (User.email == identifiant) | (User.telephone == identifiant)
    ).first()

    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Identifiant ou mot de passe invalide")

    access_token = create_access_token(data={"user_id": user.id})
    refresh_token = create_refresh_token()

    # Persiste le refresh token en base
    user.refresh_token = refresh_token
    db.commit()

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


# ── REFRESH TOKEN ─────────────────────────────────────────────────────────────

class RefreshRequest(BaseModel):
    refresh_token: str


@router.post("/refresh")
def refresh_token(payload: RefreshRequest, db: Session = Depends(get_db)):
    """
    Échange un refresh token valide contre un nouvel access token.
    Évite la déconnexion forcée après 60 min.
    """
    user = db.query(User).filter(User.refresh_token == payload.refresh_token).first()
    if not user:
        raise HTTPException(status_code=401, detail="Refresh token invalide ou expiré")

    new_access_token = create_access_token(data={"user_id": user.id})
    new_refresh_token = create_refresh_token()

    user.refresh_token = new_refresh_token
    db.commit()

    return {
        "access_token": new_access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer"
    }


# ── DÉCONNEXION ───────────────────────────────────────────────────────────────

@router.post("/logout")
def logout(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Invalide le refresh token côté serveur."""
    current_user.refresh_token = None
    db.commit()
    return {"message": "Déconnecté avec succès"}


# ── MOT DE PASSE OUBLIÉ ───────────────────────────────────────────────────────

class ForgotPasswordRequest(BaseModel):
    email: str


@router.post("/forgot-password")
def forgot_password(payload: ForgotPasswordRequest, db: Session = Depends(get_db)):
    """
    CDC : option de réinitialisation du mot de passe.
    Génère un token et le stocke en base.
    En production, ce token serait envoyé par email.
    """
    user = db.query(User).filter(User.email == payload.email).first()

    # Réponse identique que l'utilisateur existe ou non (anti-énumération)
    if user:
        token, expires = create_password_reset_token()
        user.reset_token = token
        user.reset_token_expires = expires
        db.commit()

        # TODO production : envoyer l'email avec le token
        # En dev : on retourne le token directement pour les tests
        return {
            "message": "Si cet email existe, un lien de réinitialisation a été envoyé.",
            "dev_token": token  # À SUPPRIMER en production
        }

    return {"message": "Si cet email existe, un lien de réinitialisation a été envoyé."}


# ── RÉINITIALISATION DU MOT DE PASSE ─────────────────────────────────────────

class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str

    @field_validator("new_password")
    @classmethod
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError("Le mot de passe doit contenir au moins 8 caractères")
        return v


@router.post("/reset-password")
def reset_password(payload: ResetPasswordRequest, db: Session = Depends(get_db)):
    """CDC : réinitialisation du mot de passe via token."""
    user = db.query(User).filter(User.reset_token == payload.token).first()

    if not user:
        raise HTTPException(status_code=400, detail="Token invalide ou expiré")

    if user.reset_token_expires and datetime.utcnow() > user.reset_token_expires:
        user.reset_token = None
        user.reset_token_expires = None
        db.commit()
        raise HTTPException(status_code=400, detail="Token invalide ou expiré")

    user.password_hash = hash_password(payload.new_password)
    user.reset_token = None
    user.reset_token_expires = None
    user.refresh_token = None  # Invalide toutes les sessions actives
    db.commit()

    return {"message": "Mot de passe réinitialisé avec succès"}


# ── CHANGEMENT DE MOT DE PASSE (utilisateur connecté) ────────────────────────

class ChangePasswordRequest(BaseModel):
    ancien_mot_de_passe: str
    nouveau_mot_de_passe: str

    @field_validator("nouveau_mot_de_passe")
    @classmethod
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError("Le mot de passe doit contenir au moins 8 caractères")
        return v


@router.put("/change-password")
def change_password(
    payload: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not verify_password(payload.ancien_mot_de_passe, current_user.password_hash):
        raise HTTPException(status_code=400, detail="Ancien mot de passe incorrect")

    current_user.password_hash = hash_password(payload.nouveau_mot_de_passe)
    db.commit()

    return {"message": "Mot de passe modifié avec succès"}
