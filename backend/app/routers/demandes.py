from fastapi import (
    APIRouter,
    Depends
)

from sqlalchemy.orm import Session

from app.database import get_db

from app.models.demande import Demande
from app.models.user import User

from app.services.security_service import (
    get_current_user
)

router = APIRouter(
    prefix="/demandes",
    tags=["Demandes"]
)


@router.post("/")
def create_demande(
    titre: str,
    description: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    nouvelle_demande = Demande(
        titre=titre,
        description=description,
        user_id=current_user.id
    )

    db.add(nouvelle_demande)

    db.commit()

    db.refresh(nouvelle_demande)

    return nouvelle_demande


@router.get("/")
def get_demandes(
    db: Session = Depends(get_db)
):

    demandes = db.query(Demande).all()

    return demandes