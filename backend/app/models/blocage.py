from sqlalchemy import Column, Integer, ForeignKey, DateTime, UniqueConstraint
from sqlalchemy.sql import func
from app.database import Base


class Blocage(Base):
    """
    Un utilisateur (bloqueur) en bloque un autre (bloqué).
    Empêche la messagerie entre les deux et les retire du matching.
    """
    __tablename__ = "blocages"

    id = Column(Integer, primary_key=True, index=True)

    bloqueur_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    bloque_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    created_at = Column(DateTime, server_default=func.now())

    __table_args__ = (
        UniqueConstraint("bloqueur_id", "bloque_id", name="uq_blocage"),
    )
