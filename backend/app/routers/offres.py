from fastapi import (
    APIRouter,
    Depends
)

from sqlalchemy.orm import Session

from app.database import get_db

from app.models.offre import Offre
from app.models.user import User

from app.services.security_service import (
    get_current_user
)

router = APIRouter(
    prefix="/offres",
    tags=["Offres"]
)


@router.post("/")
def create_offre(
    titre: str,
    description: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    nouvelle_offre = Offre(
        titre=titre,
        description=description,
        user_id=current_user.id
    )

    db.add(nouvelle_offre)

    db.commit()

    db.refresh(nouvelle_offre)

    return nouvelle_offre


@router.get("/")
def get_offres(
    db: Session = Depends(get_db)
):

    offres = db.query(Offre).all()

    return offres