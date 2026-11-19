from sqlalchemy import select
from sqlalchemy.orm import selectinload

from crisisops.modules.operations.models import (
    Mission,
    MissionPersonnelRequirement,
    MissionResourceRequirement,
    MissionStatus,
)
from crisisops.modules.operations.repository.operation import OperationsRepository
from crisisops.shared.enums import Priority


class MissionsRepository(OperationsRepository):
    """Acceso a persistencia de misiones y requisitos (HU-02). Hereda sesión, commit y rollback."""

    # HU-02: misiones

    def create_mission(
        self,
        operation_id: int,
        name: str,
        priority: Priority,
        status: MissionStatus,
    ) -> Mission:
        mission = Mission(
            operation_id=operation_id,
            name=name,
            priority=priority,
            status=status,
        )
        self.db.add(mission)
        self.db.flush()
        self.db.refresh(mission)
        return mission

    def get_mission(self, mission_id: int) -> Mission | None:
        statement = (
            select(Mission)
            .where(Mission.id == mission_id)
            .options(
                selectinload(Mission.resource_requirements),
                selectinload(Mission.personnel_requirements),
            )
        )
        return self.db.scalars(statement).one_or_none()

    # HU-02: requisitos

    def add_resource_requirement(
        self,
        mission_id: int,
        resource_type: str,
        quantity: int,
    ) -> MissionResourceRequirement:
        requirement = MissionResourceRequirement(
            mission_id=mission_id,
            resource_type=resource_type,
            quantity=quantity,
        )
        self.db.add(requirement)
        self.db.flush()
        self.db.refresh(requirement)
        return requirement

    def add_personnel_requirement(
        self,
        mission_id: int,
        profile: str,
        quantity: int,
    ) -> MissionPersonnelRequirement:
        requirement = MissionPersonnelRequirement(
            mission_id=mission_id,
            profile=profile,
            quantity=quantity,
        )
        self.db.add(requirement)
        self.db.flush()
        self.db.refresh(requirement)
        return requirement
