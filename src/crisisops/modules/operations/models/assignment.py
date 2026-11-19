from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from crisisops.core.database import Base

if TYPE_CHECKING:
    from crisisops.modules.operations.models.requirement import (
        MissionPersonnelRequirement,
        MissionResourceRequirement,
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
