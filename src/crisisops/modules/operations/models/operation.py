from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from crisisops.core.database import Base
from crisisops.modules.operations.models.enums import enum_column
from crisisops.shared.enums import Priority

if TYPE_CHECKING:
    from crisisops.modules.operations.models.mission import Mission


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
