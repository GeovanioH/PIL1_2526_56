from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="IFRI_MentorLink API",
    version="1.0.0",
    description="IFRI_MentorLink API")

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


from app.routers import auth, users, matching, messages

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