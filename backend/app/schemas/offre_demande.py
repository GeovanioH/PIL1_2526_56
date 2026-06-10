from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class OffreCreate(BaseModel):
    titre: str
    description: Optional[str] = None
    matieres: Optional[list[str]] = None
    disponibilites: Optional[list[str]] = None
    format: Optional[str] = "les deux"


class OffreUpdate(BaseModel):
    titre: Optional[str] = None
    description: Optional[str] = None
    matieres: Optional[list[str]] = None
    disponibilites: Optional[list[str]] = None
    format: Optional[str] = None
    statut: Optional[str] = None  # "ouverte", "en_cours", "cloturee"


class OffreResponse(BaseModel):
    id: int
    titre: str
    description: Optional[str] = None
    matieres: Optional[list[str]] = None
    disponibilites: Optional[list[str]] = None
    format: Optional[str] = None
    statut: str
    user_id: int
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class DemandeCreate(BaseModel):
    titre: str
    description: Optional[str] = None
    matieres: Optional[list[str]] = None
    disponibilites: Optional[list[str]] = None
    format: Optional[str] = "les deux"


class DemandeUpdate(BaseModel):
    titre: Optional[str] = None
    description: Optional[str] = None
    matieres: Optional[list[str]] = None
    disponibilites: Optional[list[str]] = None
    format: Optional[str] = None
    statut: Optional[str] = None  # "ouverte", "en_cours", "cloturee"


class DemandeResponse(BaseModel):
    id: int
    titre: str
    description: Optional[str] = None
    matieres: Optional[list[str]] = None
    disponibilites: Optional[list[str]] = None
    format: Optional[str] = None
    statut: str
    user_id: int
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ── RÉPONSES AUX OFFRES / DEMANDES ───────────────────────────────────────────

class ReponseCreate(BaseModel):
    message: Optional[str] = None


class ReponseOffreResponse(BaseModel):
    id: int
    offre_id: int
    repondant_id: int
    message: Optional[str] = None
    statut: str
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ReponseDemandeResponse(BaseModel):
    id: int
    demande_id: int
    repondant_id: int
    message: Optional[str] = None
    statut: str
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ReponseStatutUpdate(BaseModel):
    statut: str  # "acceptee" ou "refusee"
