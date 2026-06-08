from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import jwt
from jwt.exceptions import PyJWTError as JWTError
from app.services.auth_service import SECRET_KEY, ALGORITHM

# FastAPI va chercher le token sur la route de connexion d'Huriel
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

def get_current_user(token: str = Depends(oauth2_scheme)):

    #Décode le token JWT pour authentifier l'utilisateur et sécuriser l'accès aux routes de l'API.
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token invalide ou expiré",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # Décodage du jeton avec la clé et l'algorithme d'auth_service
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        
        if email is None:
            raise credentials_exception
            
        # On retourne un dictionnaire contenant l'identité de l'utilisateur connecté
        return {"email": email, "id": 1}
        
    except JWTError:
        raise credentials_exception
def verify_admin_role(current_user: dict = Depends(get_current_user)):
    """
    Vérifie si l'utilisateur connecté possède le rôle 'admin'.
    Renvoie une erreur 403 si l'accès est refusé.
    """
    # Pour l'instant, on simule le rôle de l'utilisateur
    user_role = current_user.get("role", "user")
    
    if user_role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Action interdite : droits d'administrateur requis"
        )
    return current_user