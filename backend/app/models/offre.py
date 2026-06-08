from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey
)

from sqlalchemy.orm import relationship

from app.database import Base


class Offre(Base):

    __tablename__ = "offres"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    titre = Column(
        String,
        nullable=False
    )

    description = Column(
        String,
        nullable=False
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    user = relationship(
        "User",
        back_populates="offres"
    )