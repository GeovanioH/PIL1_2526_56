from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.pool import QueuePool
from dotenv import load_dotenv
import os

load_dotenv()

# URL PostgreSQL
DATABASE_URL = os.getenv("DATABASE_URL")

# Vérifie que la variable existe
if not DATABASE_URL:
    raise ValueError(
        "DATABASE_URL est absente du fichier .env"
    )

# Engine SQLAlchemy
engine = create_engine(

    DATABASE_URL,
    # Affiche les requêtes SQL
    echo=True,
    # Nombre de connexions permanentes
    pool_size=10,
    # Connexions supplémentaires temporaires
    max_overflow=10,
    # Vérifie que la connexion est encore valide
    pool_pre_ping=True,

    # EN PRODUCTION
    # En production :
    # echo=False
    # pool_size=20 ou plus
    # Ajouter :
    # pool_recycle=3600
    # Utiliser variables environnement sécurisées
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
    Crée une session DB par requête
    puis la ferme automatiquement.
    """
    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()
