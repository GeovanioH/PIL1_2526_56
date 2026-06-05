from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException, status

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