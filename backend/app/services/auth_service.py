from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException, status

from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta

# Configuration du hachage des mots de passe
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Configuration temporaire du JWT (Secrète pour les signatures)
SECRET_KEY = "SUPER_SECRET_KEY_A_CHANGER_PLUS_TARD"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# --- Fonctions utilitaires pour les mots de passe ---
def hash_password(password: str) -> str:
    """Hache un mot de passe en texte brut"""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Vérifie si un mot de passe brut correspond au hachage"""
    return pwd_context.verify(plain_password, hashed_password)

# --- Fonctions utilitaires pour les Jetons JWT ---
def create_access_token(data: dict) -> str:
    """Génère un token JWT valide pour une durée déterminée"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# On définit où FastAPI doit chercher le token (ici, sur la route /login)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def get_current_user(token: str = Depends(oauth2_scheme)):
    """
    Fonction de dépendance pour vérifier le token de l'utilisateur.
    Pour l'instant, elle simule une validation simple.
    """
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token d'authentification manquant ou invalide",
            headers={"WWW-Authenticate": "Bearer"},
        )
    # Plus tard, on décodera le token JWT ici pour récupérer le vrai utilisateur
    return {"id": 1, "username": "utilisateur_test"}