from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from crisisops.modules.operations.models import (
    Mission,
    MissionPersonnelRequirement,
    MissionResourceRequirement,
    MissionStatus,
    Operation,
)
from crisisops.shared.enums import Priority


class OperationsRepository:
    """Acceso a persistencia del módulo operations."""

    def __init__(self, db_session: Session) -> None:
        self.db = db_session

    # HU-01: operaciones

    def create_operation(
        self,
        emergency_id: int,
        name: str,
        priority: Priority,
    ) -> Operation:
        operation = Operation(
            emergency_id=emergency_id,
            name=name,
            priority=priority,
        )
        self.db.add(operation)
        self.db.flush()
        self.db.refresh(operation)
        return operation

    def get_operation(self, operation_id: int) -> Operation | None:
        return self.db.get(Operation, operation_id)

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

    def commit(self) -> None:
        self.db.commit()

    def rollback(self) -> None:
        self.db.rollback()
