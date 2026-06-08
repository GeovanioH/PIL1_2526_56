from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.services.matching_service import (
    calculate_matching_score
)
from app.services.security_service import (
    get_current_user
)

router = APIRouter(
    prefix="/matching",
    tags=["Matching"]
)


@router.get("/")
def get_matches(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    users = db.query(User).all()

    matches = []

    for user in users:

        # Éviter de se matcher soi-même
        if user.id == current_user.id:
            continue

        score = calculate_matching_score(
            current_user,
            user
        )

        matches.append({
            "user_id": user.id,
            "nom": user.nom,
            "prenom": user.prenom,
            "filiere": user.filiere,
            "niveau": user.niveau,
            "score": score
        })

    # Trier du meilleur score au plus faible
    sorted_matches = sorted(
        matches,
        key=lambda x: x["score"],
        reverse=True
    )

    return sorted_matches