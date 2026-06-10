import os

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from app.database import Base, engine

# Import tous les modèles pour que SQLAlchemy crée les tables
from app.models.user import User
from app.models.offre import Offre
from app.models.demande import Demande
from app.models.conversations import Conversation
from app.models.messages import Message
from app.models.participants_conversation import ParticipantConversation
from app.models.notification import Notification
from app.models.reponse_offre import ReponseOffre
from app.models.reponse_demande import ReponseDemande
from app.models.blocage import Blocage

from app.routers import auth, users, matching, messages, offres, demandes

# Création automatique des tables
Base.metadata.create_all(bind=engine)

# Migration légère : ajoute les colonnes de pièce jointe si la table messages existe déjà
from sqlalchemy import text
with engine.begin() as conn:
    conn.execute(text("ALTER TABLE messages ADD COLUMN IF NOT EXISTS fichier_url VARCHAR(500)"))
    conn.execute(text("ALTER TABLE messages ADD COLUMN IF NOT EXISTS fichier_nom VARCHAR(255)"))
    conn.execute(text("ALTER TABLE participants_conversation ADD COLUMN IF NOT EXISTS supprime_le TIMESTAMP"))
    conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS afficher_telephone BOOLEAN DEFAULT FALSE"))

app = FastAPI(
    title="IFRI_MentorLink API",
    version="2.0.0",
    description=(
        "API REST de la plateforme de mentorat IFRI_MentorLink. "
        "Met en relation mentors et mentorés parmi les étudiants de l'IFRI."
    )
)

# ── CORS ──────────────────────────────────────────────────────────────────────
# À restreindre sur le domaine du frontend en production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── FICHIERS UPLOADÉS (photos de profil) ───────────────────────────────────────
os.makedirs("uploads", exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")


# ── HANDLER D'ERREURS GLOBAL ──────────────────────────────────────────────────

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Retourne des erreurs JSON propres au lieu des stack traces brutes."""
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Erreur interne du serveur",
            "type": type(exc).__name__
        }
    )


# ── ROUTES ────────────────────────────────────────────────────────────────────

@app.get("/")
def root():
    return {"message": "IFRI_MentorLink API running", "status": "ok", "version": "2.0.0"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}


app.include_router(auth.router)
app.include_router(users.router)
app.include_router(matching.router)
app.include_router(offres.router)
app.include_router(demandes.router)
app.include_router(messages.router)
