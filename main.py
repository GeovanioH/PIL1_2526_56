from fastapi import FastAPI
# On va chercher le routeur qu'on a créé dans le fichier users.py
from backend.app.routers.users import router as users_router

app = FastAPI(
    title="Plateforme d'Entraide - Backend",
    description="API pour la gestion des profils (compétences, lacunes, disponibilités)",
    version="1.0.0"
)

# On inclut le routeur des utilisateurs dans notre application principale
app.include_router(users_router)

@app.get("/")
def read_root():
    return {"message": "Bienvenue sur l'API d'entraide ! Le backend fonctionne correctement."}