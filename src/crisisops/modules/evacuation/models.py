from datetime import datetime
from enum import StrEnum

from sqlalchemy import DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from crisisops.core.database import Base


class EvacuationStatus(StrEnum):
    DRAFT = "DRAFT"
    ISSUED = "ISSUED"
    ACTIVE = "ACTIVE"
    LIFTED = "LIFTED"
    CANCELLED = "CANCELLED"


class ShelterStatus(StrEnum):
    PLANNED = "PLANNED"
    OPEN = "OPEN"
    FULL = "FULL"
    CLOSED = "CLOSED"


class ShelterAvailability(StrEnum):
    ENABLED = "ENABLED"
    DISABLED = "DISABLED"


class EvacuationOrder(Base):
    """Modelo para el contrato principal GET /evacuations?status=ACTIVE."""

    __tablename__ = "evacuation_orders"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    emergency_id: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    status: Mapped[str] = mapped_column(
        String(30), nullable=False, default=EvacuationStatus.ACTIVE.value
    )
    people_in_motion: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )


class Shelter(Base):
    """Tabla shelters definida en el ticket de la Clase 15."""

    __tablename__ = "shelters"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    location: Mapped[str] = mapped_column(String(150), nullable=False)
    capacity: Mapped[int] = mapped_column(Integer, nullable=False)
    current_occupancy: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    status: Mapped[str] = mapped_column(
        String(30), nullable=False, default=ShelterStatus.OPEN.value
    )
    availability: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default=ShelterAvailability.ENABLED.value,
        server_default=ShelterAvailability.ENABLED.value,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )


class PeopleMovement(Base):
    """Tabla people_movement definida en el ticket de la Clase 15."""

    __tablename__ = "people_movement"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    emergency_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    shelter_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("shelters.id"), nullable=True
    )
    people_count: Mapped[int] = mapped_column(Integer, nullable=False)
    location: Mapped[str] = mapped_column(String(150), nullable=False)
    recorded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )