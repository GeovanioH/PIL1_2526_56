import os
import uuid

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.notification import Notification
from app.models.blocage import Blocage
from app.schemas.user import UserResponse, UserUpdateRequest
from app.services.security_service import get_current_user


router = APIRouter(prefix="/users", tags=["Users"])


# ── UPLOAD DE LA PHOTO DE PROFIL ───────────────────────────────────────────────

@router.post("/me/photo")
def upload_photo(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Reçoit une image, la sauvegarde dans /uploads et stocke son URL."""
    ext = os.path.splitext(file.filename or "")[1].lower()
    if ext not in (".jpg", ".jpeg", ".png", ".gif", ".webp"):
        raise HTTPException(status_code=400, detail="Format d'image non supporté (JPG, PNG, GIF, WEBP)")

    os.makedirs("uploads", exist_ok=True)
    filename = f"{uuid.uuid4().hex}{ext}"
    path = os.path.join("uploads", filename)

    contenu = file.file.read()
    if len(contenu) > 2 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="Image trop lourde (2 Mo maximum)")
    with open(path, "wb") as f:
        f.write(contenu)

    current_user.photo_url = f"http://127.0.0.1:8000/uploads/{filename}"
    db.commit()
    return {"photo_url": current_user.photo_url}


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


# ── BLOCAGE D'UTILISATEURS ─────────────────────────────────────────────────────

@router.post("/me/block/{user_id}", status_code=201)
def block_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Bloque un utilisateur : plus de messagerie ni de matching entre les deux."""
    if user_id == current_user.id:
        raise HTTPException(status_code=400, detail="Vous ne pouvez pas vous bloquer vous-même")

    cible = db.query(User).filter(User.id == user_id).first()
    if not cible:
        raise HTTPException(status_code=404, detail="Utilisateur introuvable")

    existant = db.query(Blocage).filter(
        Blocage.bloqueur_id == current_user.id,
        Blocage.bloque_id == user_id
    ).first()
    if not existant:
        db.add(Blocage(bloqueur_id=current_user.id, bloque_id=user_id))
        db.commit()

    return {"message": "Utilisateur bloqué"}


@router.delete("/me/block/{user_id}", status_code=204)
def unblock_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Débloque un utilisateur."""
    db.query(Blocage).filter(
        Blocage.bloqueur_id == current_user.id,
        Blocage.bloque_id == user_id
    ).delete()
    db.commit()


@router.get("/me/blocks")
def get_my_blocks(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Liste des ids d'utilisateurs que j'ai bloqués."""
    rows = db.query(Blocage.bloque_id).filter(Blocage.bloqueur_id == current_user.id).all()
    return {"blocked_ids": [r[0] for r in rows]}


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
