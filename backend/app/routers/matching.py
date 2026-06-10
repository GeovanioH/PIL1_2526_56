from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.offre import Offre
from app.models.blocage import Blocage
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
    CDC : propose les mentors via leurs OFFRES publiées.
    Une carte = une offre. Si un mentor publie 2 offres, il apparaît 2 fois,
    chaque carte portant la matière de l'offre concernée.
    Critères du score : compétences/lacunes, disponibilités, filière, niveau.
    """
    # IDs bloqués (dans les deux sens) : on ne se propose pas mutuellement
    bloques = {r[0] for r in db.query(Blocage.bloque_id).filter(Blocage.bloqueur_id == current_user.id).all()}
    bloques |= {r[0] for r in db.query(Blocage.bloqueur_id).filter(Blocage.bloque_id == current_user.id).all()}

    # Toutes les offres des autres utilisateurs
    offres = db.query(Offre).filter(Offre.user_id != current_user.id).all()

    # Cache des scores/détails par utilisateur (identiques pour toutes ses offres)
    cache = {}
    matches = []
    for offre in offres:
        user = offre.user
        if not user or user.id in bloques:
            continue

        if user.id not in cache:
            cache[user.id] = (
                calculate_matching_score(current_user, user),
                get_matching_details(current_user, user),
            )
        score, details = cache[user.id]

        matches.append({
            "user_id": user.id,
            "nom": user.nom,
            "prenom": user.prenom,
            "filiere": user.filiere,
            "niveau": user.niveau,
            "photo_url": user.photo_url,
            # Offre à l'origine de cette carte
            "offre_id": offre.id,
            "offre_titre": offre.titre,
            "matiere": offre.matieres or [],            # matière(s) de CETTE offre
            "format": offre.format,
            "disponibilites": offre.disponibilites or [],
            # Détails de compatibilité (pour la fiche profil)
            "matieres_communes": details["matieres_communes"],
            "disponibilites_communes": details["disponibilites_communes"],
            "score": score,
        })

    # Trier du meilleur score au plus faible
    matches.sort(key=lambda x: x["score"], reverse=True)

    return matches
