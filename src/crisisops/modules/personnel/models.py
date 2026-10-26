"""Modelos ORM propiedad de este módulo.

Regla: este archivo no debe importar modelos ORM de otros módulos sin una
decisión arquitectónica común documentada.
"""

#PersonnelAssignment (metodo overlaps [start,end) ) T1.2

import enum
from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, Enum, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column

from crisisops.core.database import Base  # VERIFICAR el nombre/ruta real


class AssignmentStatus(enum.StrEnum):
    RESERVED = "RESERVED"
    ACTIVE = "ACTIVE"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


class PersonnelAssignment(Base):
    __tablename__ = "personnel_assignments"  # COINCIDIR CON LA TABLA EN MIGRACION

    __table_args__ = (
        CheckConstraint("start_at < end_at", name="ck_assignment_start_before_end"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    responder_id: Mapped[int] = mapped_column(
        ForeignKey("responders.id"), nullable=False, index=True
    )
    # Referencia a la misión del Grupo D: solo un identificador, SIN ForeignKey
    mission_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    start_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    end_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    status: Mapped[AssignmentStatus] = mapped_column(
        Enum(AssignmentStatus), nullable=False, default=AssignmentStatus.ACTIVE
    )

    def overlaps(self, start: datetime, end: datetime) -> bool:
        """True si esta asignación se solapa con [start, end).
        intervalos semiabiertos. El inicio se incluye y el
        fin no, así que 08:00-12:00 y 12:00-16:00 NO se solapan.
        """
        if start >= end:
            raise ValueError("start debe ser anterior a end")
        return self.start_at < end and start < self.end_at