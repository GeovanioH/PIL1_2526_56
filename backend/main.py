#Importer les fonctions et fichiers des bibliothèques et dossier
from fastapi import FastAPI
from backend.app.routers.users import router as users_router

#Création de l'application et insération dans la variable app
app = FastAPI(
    title="Plateforme d'Entraide - Backend",
    description="API pour la gestion des profils (compétences, lacunes, disponibilités)",
    version="1.0.0"
)

# On inclut le routeur des utilisateurs dans notre application principale
app.include_router(users_router)

#Message d'accueil à l'utilisateur
@app.get("/")
def read_root():
    return {"message": "Bienvenue sur l'API d'entraide ! Le backend fonctionne correctement."}