from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.notification import Notification
from app.schemas.user import UserResponse, UserUpdateRequest
from app.services.security_service import get_current_user


router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=UserResponse)
def get_my_profile(current_user: User = Depends(get_current_user)):
    return current_user


@router.put("/me", response_model=UserResponse)
def update_my_profile(
    update_data: UserUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if update_data.telephone and update_data.telephone != current_user.telephone:
        existing = db.query(User).filter(User.telephone == update_data.telephone).first()
        if existing:
            raise HTTPException(status_code=400, detail="Ce numéro de téléphone est déjà utilisé")

    for field, value in update_data.model_dump(exclude_unset=True).items():
        setattr(current_user, field, value)

    db.commit()
    db.refresh(current_user)
    return current_user


@router.delete("/me", status_code=204)
def delete_my_account(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Suppression du compte de l'utilisateur connecté."""
    db.delete(current_user)
    db.commit()


@router.get("/{user_id}", response_model=UserResponse)
def get_user_profile(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur introuvable")
    return user


# ── NOTIFICATIONS ─────────────────────────────────────────────────────────────

@router.get("/me/notifications")
def get_my_notifications(
    page: int = 1,
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Récupère les notifications de l'utilisateur (lues et non lues)."""
    notifs = db.query(Notification).filter(
        Notification.user_id == current_user.id
    ).order_by(Notification.created_at.desc()).offset((page - 1) * limit).limit(limit).all()

    unread_count = db.query(Notification).filter(
        Notification.user_id == current_user.id,
        Notification.lu == False
    ).count()

    return {
        "notifications": [
            {
                "id": n.id,
                "type": n.type,
                "contenu": n.contenu,
                "reference_id": n.reference_id,
                "lu": n.lu,
                "created_at": n.created_at
            }
            for n in notifs
        ],
        "unread_count": unread_count
    }


@router.put("/me/notifications/{notif_id}/lu")
def mark_notification_read(
    notif_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    notif = db.query(Notification).filter(
        Notification.id == notif_id,
        Notification.user_id == current_user.id
    ).first()
    if not notif:
        raise HTTPException(status_code=404, detail="Notification introuvable")

    notif.lu = True
    db.commit()
    return {"message": "Notification marquée comme lue"}


@router.put("/me/notifications/tout-lire")
def mark_all_notifications_read(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db.query(Notification).filter(
        Notification.user_id == current_user.id,
        Notification.lu == False
    ).update({"lu": True})
    db.commit()
    return {"message": "Toutes les notifications marquées comme lues"}
