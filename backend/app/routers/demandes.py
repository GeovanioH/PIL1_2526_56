from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from typing import Optional

from app.database import get_db
from app.models.demande import Demande
from app.models.reponse_demande import ReponseDemande
from app.models.notification import Notification
from app.models.user import User
from app.schemas.offre_demande import (
    DemandeCreate, DemandeUpdate, DemandeResponse,
    ReponseCreate, ReponseDemandeResponse, ReponseStatutUpdate
)
from app.services.security_service import get_current_user


router = APIRouter(prefix="/demandes", tags=["Demandes"])


@router.post("/", response_model=DemandeResponse, status_code=201)
def create_demande(
    demande_data: DemandeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    nouvelle_demande = Demande(
        titre=demande_data.titre,
        description=demande_data.description,
        matieres=demande_data.matieres or [],
        disponibilites=demande_data.disponibilites or [],
        format=demande_data.format or "les deux",
        statut="ouverte",
        user_id=current_user.id
    )
    db.add(nouvelle_demande)
    db.commit()
    db.refresh(nouvelle_demande)
    return nouvelle_demande


@router.get("/", response_model=list[DemandeResponse])
def get_demandes(
    matiere: Optional[str] = Query(None),
    format: Optional[str] = Query(None),
    statut: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    query = db.query(Demande)
    if format:
        query = query.filter(Demande.format == format)
    if statut:
        query = query.filter(Demande.statut == statut)

    demandes = query.offset((page - 1) * limit).limit(limit).all()

    if matiere:
        demandes = [d for d in demandes if d.matieres and matiere in d.matieres]

    return demandes


@router.get("/{demande_id}", response_model=DemandeResponse)
def get_demande(demande_id: int, db: Session = Depends(get_db)):
    demande = db.query(Demande).filter(Demande.id == demande_id).first()
    if not demande:
        raise HTTPException(status_code=404, detail="Demande introuvable")
    return demande


@router.put("/{demande_id}", response_model=DemandeResponse)
def update_demande(
    demande_id: int,
    update_data: DemandeUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    demande = db.query(Demande).filter(Demande.id == demande_id).first()
    if not demande:
        raise HTTPException(status_code=404, detail="Demande introuvable")
    if demande.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Vous ne pouvez modifier que vos propres demandes")

    for field, value in update_data.model_dump(exclude_unset=True).items():
        setattr(demande, field, value)

    db.commit()
    db.refresh(demande)
    return demande


@router.delete("/{demande_id}", status_code=204)
def delete_demande(
    demande_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    demande = db.query(Demande).filter(Demande.id == demande_id).first()
    if not demande:
        raise HTTPException(status_code=404, detail="Demande introuvable")
    if demande.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Vous ne pouvez supprimer que vos propres demandes")

    db.delete(demande)
    db.commit()


@router.post("/{demande_id}/repondre", response_model=ReponseDemandeResponse, status_code=201)
def repondre_demande(
    demande_id: int,
    payload: ReponseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    CDC : "Les utilisateurs doivent pouvoir répondre à des demandes de mentorat
    ciblant leurs compétences."
    """
    demande = db.query(Demande).filter(Demande.id == demande_id).first()
    if not demande:
        raise HTTPException(status_code=404, detail="Demande introuvable")
    if demande.user_id == current_user.id:
        raise HTTPException(status_code=400, detail="Vous ne pouvez pas répondre à votre propre demande")

    existant = db.query(ReponseDemande).filter(
        ReponseDemande.demande_id == demande_id,
        ReponseDemande.repondant_id == current_user.id
    ).first()
    if existant:
        raise HTTPException(status_code=400, detail="Vous avez déjà répondu à cette demande")

    reponse = ReponseDemande(
        demande_id=demande_id,
        repondant_id=current_user.id,
        message=payload.message,
        statut="en_attente"
    )
    db.add(reponse)

    notif = Notification(
        user_id=demande.user_id,
        type="reponse_demande",
        contenu=f"{current_user.prenom} {current_user.nom} a répondu à votre demande « {demande.titre} »",
        reference_id=demande_id
    )
    db.add(notif)

    db.commit()
    db.refresh(reponse)
    return reponse


@router.get("/{demande_id}/reponses", response_model=list[ReponseDemandeResponse])
def get_reponses_demande(
    demande_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    demande = db.query(Demande).filter(Demande.id == demande_id).first()
    if not demande:
        raise HTTPException(status_code=404, detail="Demande introuvable")
    if demande.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Accès réservé au propriétaire de la demande")

    return db.query(ReponseDemande).filter(ReponseDemande.demande_id == demande_id).all()


@router.put("/{demande_id}/reponses/{reponse_id}/statut", response_model=ReponseDemandeResponse)
def update_statut_reponse_demande(
    demande_id: int,
    reponse_id: int,
    payload: ReponseStatutUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if payload.statut not in ("acceptee", "refusee"):
        raise HTTPException(status_code=400, detail="Statut invalide")

    demande = db.query(Demande).filter(Demande.id == demande_id).first()
    if not demande or demande.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Accès interdit")

    reponse = db.query(ReponseDemande).filter(
        ReponseDemande.id == reponse_id,
        ReponseDemande.demande_id == demande_id
    ).first()
    if not reponse:
        raise HTTPException(status_code=404, detail="Réponse introuvable")

    reponse.statut = payload.statut
    db.commit()
    db.refresh(reponse)
    return reponse
