from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from typing import Optional

from app.database import get_db
from app.models.offre import Offre
from app.models.reponse_offre import ReponseOffre
from app.models.notification import Notification
from app.models.user import User
from app.schemas.offre_demande import (
    OffreCreate, OffreUpdate, OffreResponse,
    ReponseCreate, ReponseOffreResponse, ReponseStatutUpdate
)
from app.services.security_service import get_current_user


router = APIRouter(prefix="/offres", tags=["Offres"])


# ── CRÉER UNE OFFRE ───────────────────────────────────────────────────────────

@router.post("/", response_model=OffreResponse, status_code=201)
def create_offre(
    offre_data: OffreCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Empêche de publier deux fois la même offre (mêmes matières + dispos + format)
    new_mat = sorted(offre_data.matieres or [])
    new_dispo = sorted(offre_data.disponibilites or [])
    new_fmt = offre_data.format or "les deux"
    for o in db.query(Offre).filter(Offre.user_id == current_user.id).all():
        if (sorted(o.matieres or []) == new_mat
                and sorted(o.disponibilites or []) == new_dispo
                and (o.format or "les deux") == new_fmt):
            raise HTTPException(
                status_code=400,
                detail="Tu as déjà publié cette offre (même matière et mêmes disponibilités)."
            )

    nouvelle_offre = Offre(
        titre=offre_data.titre,
        description=offre_data.description,
        matieres=offre_data.matieres or [],
        disponibilites=offre_data.disponibilites or [],
        format=offre_data.format or "les deux",
        statut="ouverte",
        user_id=current_user.id
    )
    db.add(nouvelle_offre)
    db.commit()
    db.refresh(nouvelle_offre)

    # Notifier tous les autres utilisateurs de la nouvelle offre
    autres = db.query(User).filter(User.id != current_user.id).all()
    for u in autres:
        db.add(Notification(
            user_id=u.id,
            type="nouvelle_offre",
            contenu=f"{current_user.prenom} a publié une nouvelle offre de mentorat",
            reference_id=nouvelle_offre.id
        ))
    if autres:
        db.commit()

    return nouvelle_offre


# ── LISTER LES OFFRES (avec pagination + filtres) ────────────────────────────

@router.get("/", response_model=list[OffreResponse])
def get_offres(
    matiere: Optional[str] = Query(None),
    format: Optional[str] = Query(None),
    statut: Optional[str] = Query(None, description="ouverte | en_cours | cloturee"),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """CDC : rechercher des offres par matière, format, disponibilité."""
    query = db.query(Offre)

    if format:
        query = query.filter(Offre.format == format)
    if statut:
        query = query.filter(Offre.statut == statut)

    offres = query.offset((page - 1) * limit).limit(limit).all()

    if matiere:
        offres = [o for o in offres if o.matieres and matiere in o.matieres]

    return offres


# ── DÉTAIL D'UNE OFFRE ────────────────────────────────────────────────────────

@router.get("/{offre_id}", response_model=OffreResponse)
def get_offre(offre_id: int, db: Session = Depends(get_db)):
    offre = db.query(Offre).filter(Offre.id == offre_id).first()
    if not offre:
        raise HTTPException(status_code=404, detail="Offre introuvable")
    return offre


# ── MODIFIER UNE OFFRE ────────────────────────────────────────────────────────

@router.put("/{offre_id}", response_model=OffreResponse)
def update_offre(
    offre_id: int,
    update_data: OffreUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    offre = db.query(Offre).filter(Offre.id == offre_id).first()
    if not offre:
        raise HTTPException(status_code=404, detail="Offre introuvable")
    if offre.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Vous ne pouvez modifier que vos propres offres")

    for field, value in update_data.model_dump(exclude_unset=True).items():
        setattr(offre, field, value)

    db.commit()
    db.refresh(offre)
    return offre


# ── SUPPRIMER UNE OFFRE ───────────────────────────────────────────────────────

@router.delete("/{offre_id}", status_code=204)
def delete_offre(
    offre_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    offre = db.query(Offre).filter(Offre.id == offre_id).first()
    if not offre:
        raise HTTPException(status_code=404, detail="Offre introuvable")
    if offre.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Vous ne pouvez supprimer que vos propres offres")

    db.delete(offre)
    db.commit()


# ── RÉPONDRE À UNE OFFRE ─────────────────────────────────────────────────────

@router.post("/{offre_id}/repondre", response_model=ReponseOffreResponse, status_code=201)
def repondre_offre(
    offre_id: int,
    payload: ReponseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    CDC : "Les utilisateurs doivent pouvoir répondre à des offres de mentorat
    ciblant leurs lacunes."
    """
    offre = db.query(Offre).filter(Offre.id == offre_id).first()
    if not offre:
        raise HTTPException(status_code=404, detail="Offre introuvable")
    if offre.user_id == current_user.id:
        raise HTTPException(status_code=400, detail="Vous ne pouvez pas répondre à votre propre offre")

    # Vérifier si déjà répondu
    existant = db.query(ReponseOffre).filter(
        ReponseOffre.offre_id == offre_id,
        ReponseOffre.repondant_id == current_user.id
    ).first()
    if existant:
        raise HTTPException(status_code=400, detail="Vous avez déjà répondu à cette offre")

    reponse = ReponseOffre(
        offre_id=offre_id,
        repondant_id=current_user.id,
        message=payload.message,
        statut="en_attente"
    )
    db.add(reponse)

    # Notifier le propriétaire de l'offre
    notif = Notification(
        user_id=offre.user_id,
        type="reponse_offre",
        contenu=f"{current_user.prenom} {current_user.nom} a répondu à votre offre « {offre.titre} »",
        reference_id=offre_id
    )
    db.add(notif)

    db.commit()
    db.refresh(reponse)
    return reponse


# ── LISTER LES RÉPONSES À UNE OFFRE ──────────────────────────────────────────

@router.get("/{offre_id}/reponses", response_model=list[ReponseOffreResponse])
def get_reponses_offre(
    offre_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    offre = db.query(Offre).filter(Offre.id == offre_id).first()
    if not offre:
        raise HTTPException(status_code=404, detail="Offre introuvable")
    if offre.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Accès réservé au propriétaire de l'offre")

    return db.query(ReponseOffre).filter(ReponseOffre.offre_id == offre_id).all()


# ── ACCEPTER / REFUSER UNE RÉPONSE ────────────────────────────────────────────

@router.put("/{offre_id}/reponses/{reponse_id}/statut", response_model=ReponseOffreResponse)
def update_statut_reponse_offre(
    offre_id: int,
    reponse_id: int,
    payload: ReponseStatutUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if payload.statut not in ("acceptee", "refusee"):
        raise HTTPException(status_code=400, detail="Statut invalide : 'acceptee' ou 'refusee'")

    offre = db.query(Offre).filter(Offre.id == offre_id).first()
    if not offre or offre.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Accès interdit")

    reponse = db.query(ReponseOffre).filter(
        ReponseOffre.id == reponse_id,
        ReponseOffre.offre_id == offre_id
    ).first()
    if not reponse:
        raise HTTPException(status_code=404, detail="Réponse introuvable")

    reponse.statut = payload.statut
    db.commit()
    db.refresh(reponse)
    return reponse
