from collections.abc import Callable

from crisisops.modules.operations.exceptions import (
    EmergencyNotActive,
    EmergencyNotFound,
    EmergencyUnavailable,
    OperationNotFound,
)
from crisisops.modules.operations.integrations import (
    get_personnel_profiles_from_group_c,
    get_resource_types_from_group_b,
)
from crisisops.modules.operations.models import Operation
from crisisops.modules.operations.repository.operation import OperationsRepository
from crisisops.modules.operations.schemas.operation import OperationCreate


class OperationsService:
    """Casos de uso y reglas de negocio del módulo operations."""

    def __init__(
        self,
        get_emergency_status: Callable[[int], str | None],
        repository: OperationsRepository,
        get_resource_types: Callable[[], set[str]] = get_resource_types_from_group_b,
        get_personnel_profiles: Callable[[], set[str]] = get_personnel_profiles_from_group_c,
    ) -> None:
        self._get_emergency_status = get_emergency_status
        self._get_resource_types = get_resource_types
        self._get_personnel_profiles = get_personnel_profiles
        self.repository = repository

    def validate_emergency(self, emergency_id: int) -> None:
        try:
            status = self._get_emergency_status(emergency_id)
        except (ConnectionError, TimeoutError) as error:
            raise EmergencyUnavailable(
                f"No se pudo consultar la emergencia {emergency_id}."
            ) from error

        if status is None:
            raise EmergencyNotFound(f"La emergencia {emergency_id} no existe.")
        if status != "ACTIVE":
            raise EmergencyNotActive(
                f"La emergencia {emergency_id} no está activa (estado: {status})."
            )

    def create_operation(self, data: OperationCreate) -> Operation:
        self.validate_emergency(data.emergency_id)
        try:
            operation = self.repository.create_operation(
                emergency_id=data.emergency_id, name=data.name, priority=data.priority
            )
            self.repository.commit()
        except Exception:
            self.repository.rollback()
            raise
        return operation

    def get_operation(self, operation_id: int) -> Operation:
        operation = self.repository.get_operation(operation_id)
        if operation is None:
            raise OperationNotFound(f"La operación {operation_id} no existe.")
        return operation
