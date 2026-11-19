from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from crisisops.core.database import Base

if TYPE_CHECKING:
    from crisisops.modules.operations.models.assignment import (
        MissionPersonnelAssignment,
        MissionResourceAssignment,
    )
    from crisisops.modules.operations.models.mission import Mission


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
