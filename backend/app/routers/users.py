from fastapi import APIRouter, Depends, HTTPException, status
# On importe nos schémas tout neufs !
from backend.app.schemas.user_schema import ProfileBase, ProfileUpdate
from backend.app.services.auth_service import get_current_user

router = APIRouter(
    prefix="/users",
    tags=["users"]
)

# Simulation d'une base de données temporaire pour nos tests
fake_profile_db = {
    "name": "Jean Dupont",
    "email": "jean.dupont@example.com",
    "bio": "Étudiant en informatique passionné d'IA",
    "competences": ["Python", "FastAPI"],
    "lacunes": ["React", "PostgreSQL"],
    "disponibilites": ["Lundi soir", "Mercredi après-midi"]
}

@router.get("/me", response_model=ProfileBase)
def get_my_profile(current_user: dict = Depends(get_current_user)):
    """
    Récupère le profil de l'utilisateur connecté
    """
    # Pour l'instant, on renvoie notre faux profil qui respecte la structure ProfileBase
    return fake_profile_db

@router.put("/me", response_model=ProfileBase)
def update_my_profile(profile_data: ProfileUpdate, current_user: dict = Depends(get_current_user)):
    # On met à jour uniquement les champs envoyés par l'utilisateur
    for key, value in profile_data.dict(exclude_unset=True).items():
        fake_profile_db[key] = value
        
    return fake_profile_db

@router.get("/{id}", response_model=ProfileBase)
def get_user_profile(id: int):
    if id != 1:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    return fake_profile_db