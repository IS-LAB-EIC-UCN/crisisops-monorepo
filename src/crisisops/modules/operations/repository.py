from sqlalchemy.orm import Session

from crisisops.modules.operations.models import Operation
from crisisops.shared.enums import Priority


class OperationsRepository:
    """Acceso a persistencia del módulo operations."""

    def __init__(self, db_session: Session) -> None:
        self.db = db_session

    def create_operation(self, emergency_id: int, name: str, priority: Priority) -> Operation:
        operation = Operation(emergency_id=emergency_id, name=name, priority=priority)
        self.db.add(operation)
        self.db.flush()
        self.db.refresh(operation)
        return operation

    def get_operation(self, operation_id: int) -> Operation | None:
        return self.db.get(Operation, operation_id)

    def commit(self) -> None:
        self.db.commit()

    def rollback(self) -> None:
        self.db.rollback()
