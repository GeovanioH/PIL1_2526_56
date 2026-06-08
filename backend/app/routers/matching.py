from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.services.matching_service import calculate_matching_score, get_matching_details
from app.services.security_service import get_current_user


router = APIRouter(
    prefix="/matching",
    tags=["Matching"]
)


@router.get("/")
def get_matches(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    CDC : propose les combinaisons mentor-mentoré les plus pertinentes.
    Critères : compatibilité compétences/lacunes, disponibilités, filière, niveau.
    Retourne : nom, photo, matières communes, disponibilités communes, score.
    """
    users = db.query(User).filter(User.id != current_user.id).all()

    matches = []
    for user in users:
        score = calculate_matching_score(current_user, user)
        details = get_matching_details(current_user, user)

        matches.append({
            "user_id": user.id,
            "nom": user.nom,
            "prenom": user.prenom,
            "filiere": user.filiere,
            "niveau": user.niveau,
            # CDC : photo de profil dans les résultats
            "photo_url": user.photo_url,
            # CDC : matières / compétences en commun
            "matieres_communes": details["matieres_communes"],
            # CDC : disponibilités communes
            "disponibilites_communes": details["disponibilites_communes"],
            # CDC : score de compatibilité
            "score": score
        })

    # Trier du meilleur score au plus faible
    matches.sort(key=lambda x: x["score"], reverse=True)

    return matches
