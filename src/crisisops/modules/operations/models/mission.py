from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from crisisops.core.database import Base
from crisisops.modules.operations.models.enums import MissionStatus, enum_column
from crisisops.shared.enums import Priority

if TYPE_CHECKING:
    from crisisops.modules.operations.models.operation import Operation
    from crisisops.modules.operations.models.requirement import (
        MissionPersonnelRequirement,
        MissionResourceRequirement,
    )


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
