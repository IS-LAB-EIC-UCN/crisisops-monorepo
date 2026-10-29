from datetime import datetime
from enum import StrEnum

from sqlalchemy import DateTime, ForeignKey, String, func
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from crisisops.core.database import Base
from crisisops.shared.enums import Priority


class MissionStatus(StrEnum):
    """Estados de una misión. Toda misión nace en PLANNED."""

    PLANNED = "PLANNED"
    READY = "READY"
    DISPATCHED = "DISPATCHED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


def enum_column(enum_type: type[StrEnum]) -> SAEnum:
    """Columna de texto que solo acepta los valores del enum."""
    return SAEnum(enum_type, native_enum=False, length=20, validate_strings=True)


class Operation(Base):
    """Operación creada para atender una emergencia de A. Agrupa misiones."""

    __tablename__ = "operations"

    id: Mapped[int] = mapped_column(primary_key=True)
    # Ref. externa: Grupo A (emergencies.id). Solo ID, sin FK hasta acordarla.
    emergency_id: Mapped[int] = mapped_column(nullable=False)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    priority: Mapped[Priority] = mapped_column(enum_column(Priority), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    missions: Mapped[list["Mission"]] = relationship(back_populates="operation")


class Mission(Base):
    """Misión de una operación, con sus requisitos de recursos y personal."""

    __tablename__ = "missions"

    id: Mapped[int] = mapped_column(primary_key=True)
    operation_id: Mapped[int] = mapped_column(ForeignKey("operations.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    priority: Mapped[Priority] = mapped_column(enum_column(Priority), nullable=False)
    status: Mapped[MissionStatus] = mapped_column(
        enum_column(MissionStatus), nullable=False, default=MissionStatus.PLANNED
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    operation: Mapped["Operation"] = relationship(back_populates="missions")
    resource_requirements: Mapped[list["MissionResourceRequirement"]] = relationship(
        back_populates="mission"
    )
    personnel_requirements: Mapped[list["MissionPersonnelRequirement"]] = relationship(
        back_populates="mission"
    )


class MissionResourceRequirement(Base):
    """Recursos que necesita una misión: tipo y cantidad."""

    __tablename__ = "mission_resource_requirements"

    id: Mapped[int] = mapped_column(primary_key=True)
    mission_id: Mapped[int] = mapped_column(ForeignKey("missions.id"), nullable=False)
    # Ref. externa: Grupo B (catálogo de tipos de recurso). Solo código, sin FK.
    resource_type: Mapped[str] = mapped_column(String(100), nullable=False)
    quantity: Mapped[int] = mapped_column(nullable=False)

    mission: Mapped["Mission"] = relationship(back_populates="resource_requirements")
    assignments: Mapped[list["MissionResourceAssignment"]] = relationship(
        back_populates="requirement"
    )


class MissionPersonnelRequirement(Base):
    """Personal que necesita una misión: perfil y cantidad."""

    __tablename__ = "mission_personnel_requirements"

    id: Mapped[int] = mapped_column(primary_key=True)
    mission_id: Mapped[int] = mapped_column(ForeignKey("missions.id"), nullable=False)
    # Ref. externa: Grupo C (catálogo de perfiles de personal). Solo código, sin FK.
    profile: Mapped[str] = mapped_column(String(100), nullable=False)
    quantity: Mapped[int] = mapped_column(nullable=False)

    mission: Mapped["Mission"] = relationship(back_populates="personnel_requirements")
    assignments: Mapped[list["MissionPersonnelAssignment"]] = relationship(
        back_populates="requirement"
    )


class MissionResourceAssignment(Base):
    """Recurso de B que cubre un requisito. released_at NULL = asignación activa."""

    __tablename__ = "mission_resource_assignments"

    id: Mapped[int] = mapped_column(primary_key=True)
    requirement_id: Mapped[int] = mapped_column(
        ForeignKey("mission_resource_requirements.id"), nullable=False
    )
    # Ref. externa: Grupo B (recursos.id). Solo ID, sin FK hasta acordarla.
    resource_id: Mapped[int] = mapped_column(nullable=False)
    assigned_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    released_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    requirement: Mapped["MissionResourceRequirement"] = relationship(back_populates="assignments")


class MissionPersonnelAssignment(Base):
    """Persona de C que cubre un requisito. released_at NULL = asignación activa."""

    __tablename__ = "mission_personnel_assignments"

    id: Mapped[int] = mapped_column(primary_key=True)
    requirement_id: Mapped[int] = mapped_column(
        ForeignKey("mission_personnel_requirements.id"), nullable=False
    )
    # Ref. externa: Grupo C (responders.id). Solo ID, sin FK hasta acordarla.
    responder_id: Mapped[int] = mapped_column(nullable=False)
    assigned_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    released_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    requirement: Mapped["MissionPersonnelRequirement"] = relationship(back_populates="assignments")
