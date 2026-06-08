from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from jose import jwt
from passlib.context import CryptContext
from app.database import get_db
from app.models.user import User
from app.schemas.user import RegisterRequest, LoginRequest
from dotenv import load_dotenv
import os
from fastapi.security import OAuth2PasswordRequestForm


load_dotenv()

router = APIRouter(
    prefix="/auth",
    tags=["Auth"]
)

# Configuration JWT
SECRET_KEY = os.getenv("SECRET_KEY")

ALGORITHM = os.getenv(
    "ALGORITHM",
    "HS256"
)

ACCESS_TOKEN_EXPIRE_MINUTES = 60

# En production :
# Utiliser une SECRET_KEY longue et sécurisée
# Réduire la durée du token
# Utiliser des variables d'environnement protégées


# Configuration bcrypt
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)

# En production :
# Augmenter le coût bcrypt selon les performances serveur


# Hash du mot de passe
def hash_password(password: str):
    return pwd_context.hash(password)


# Vérification mot de passe
def verify_password(
    plain_password: str,
    hashed_password: str
):
    return pwd_context.verify(
        plain_password,
        hashed_password
    )


# Génération JWT
def create_access_token(data: dict):

    to_encode = data.copy()

    expire = datetime.utcnow() + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )

    to_encode.update({
        "exp": expire
    })

    encoded_jwt = jwt.encode(
        to_encode,
        SECRET_KEY,
        algorithm=ALGORITHM
    )

    return encoded_jwt


# Route inscription
@router.post("/register")
def register(
    user_data: RegisterRequest,
    db: Session = Depends(get_db)
):

    existing_user = db.query(User).filter(
        User.email == user_data.email
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Email déjà utilisé"
        )

    hashed_password = hash_password(
        user_data.password
    )

    new_user = User(
        nom=user_data.nom,
        prenom=user_data.prenom,
        email=user_data.email,
        telephone=user_data.telephone,
        password_hash=hashed_password,
        filiere=user_data.filiere,
        niveau=user_data.niveau,
        bio=user_data.bio,
        photo_url=user_data.photo_url,
        competences=user_data.competences,
        lacunes=user_data.lacunes,
        disponibilites=user_data.disponibilites
    )

    db.add(new_user)

    db.commit()

    db.refresh(new_user)

    return {
        "message": "Utilisateur créé avec succès"
    }


# Route connexion
@router.post("/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):

    user = db.query(User).filter(
        User.email == form_data.username
    ).first()

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Email ou mot de passe invalide"
        )

    valid_password = verify_password(
    form_data.password,
    user.password_hash
        )

    if not valid_password:
        raise HTTPException(
            status_code=401,
            detail="Email ou mot de passe invalide"
        )

    access_token = create_access_token(
        data={
    "user_id": user.id
    }
    )

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }
