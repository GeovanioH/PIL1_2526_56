from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from dotenv import load_dotenv
import os

load_dotenv()

# URL PostgreSQL
DATABASE_URL = os.getenv("DATABASE_URL")

# URL publique du backend (pour construire les liens des fichiers uploadés).
# En local : http://127.0.0.1:8000 ; en ligne : l'URL Render (variable d'env PUBLIC_URL).
PUBLIC_URL = os.getenv("PUBLIC_URL", "http://127.0.0.1:8000").rstrip("/")

# Vérifie que la variable existe
if not DATABASE_URL:
    raise ValueError(
        "DATABASE_URL est absente du fichier .env"
    )

# Engine SQLAlchemy
engine = create_engine(
    DATABASE_URL,
    # Affiche les requêtes SQL — False pour de meilleures performances
    echo=False,
    # Nombre de connexions permanentes
    pool_size=10,
    # Connexions supplémentaires temporaires
    max_overflow=10,
    # Vérifie que la connexion est encore valide avant usage
    pool_pre_ping=True,
)

# Factory de sessions SQLAlchemy
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Base ORM pour tous les modèles
Base = declarative_base()


def get_db():
    """
    Générateur : crée une session DB par requête
    et la ferme automatiquement après usage.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
