from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import Base, engine
from app.models.user import User
from app.routers import auth, users, matching, messages ,offres, demandes
from app.models.offre import Offre
from app.models.demande import Demande

# Création automatique des tables SQLAlchemy
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="IFRI_MentorLink API",
    version="1.0.0",
    description="IFRI_MentorLink API"
)

# Middleware CORS
# allow_origins=["*"] en développement
# À restreindre en production avec l'URL du frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {
        "message": "IFRI_MentorLink API running",
        "status": "ok",
        "version": "1.0.0"
    }

@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }

# Inclusion des routers
app.include_router(auth.router)
app.include_router(matching.router)
app.include_router(offres.router)
app.include_router(demandes.router)
app.include_router(messages.router)
#app.include_router(users.router)