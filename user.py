#Importation des fonctions et blocs de données à utiliser des bibliothèques et fichiers
from fastapi import APIRouter, Depends, HTTPException, status
from backend.app.schemas.user import ProfileBase, ProfileUpdate
from backend.app.services.security_service import get_current_user, verify_admin_role

router = APIRouter(
    prefix="/users",
    tags=["users"]
)

# Création d'un profil-test pour simuler la base en attendant
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
#Mise à jour s'il y a lieu des données de l'utilisation
@router.put("/me", response_model=ProfileBase)
def update_my_profile(profile_data: ProfileUpdate, current_user: dict = Depends(get_current_user)):
    for key, value in profile_data.dict(exclude_unset=True).items():
        fake_profile_db[key] = value
    return fake_profile_db

@router.get("/{id}", response_model=ProfileBase)
def get_user_profile(id: int):
    if id != 1:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    return fake_profile_db

@router.get("/admin/all")
def get_all_profiles(admin_user: dict = Depends(verify_admin_role));
    return{"message": "Accès autorisé","profiles": [fake_profile_db]}