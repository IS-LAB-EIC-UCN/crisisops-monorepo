from collections.abc import Callable

from crisisops.core.exceptions import DomainError
from crisisops.modules.operations.models import Operation
from crisisops.modules.operations.repository import OperationsRepository
from crisisops.modules.operations.schemas import OperationCreate


class EmergencyNotFound(DomainError):
    """La emergencia indicada no existe en Grupo A."""

    status_code = 422


class EmergencyNotActive(DomainError):
    """La emergencia existe, pero su estado no permite crear operaciones."""

    status_code = 409


class EmergencyUnavailable(DomainError):
    """No se pudo consultar a Grupo A (caído o aún no integrado)."""

    status_code = 503


class OperationNotFound(DomainError):
    """No existe una operación con el id consultado."""

    status_code = 404


def get_emergency_status_from_group_a(emergency_id: int) -> str | None:
    """Consulta el estado en Grupo A. Mientras A no esté integrado en develop, no responde."""
    raise ConnectionError("El módulo de emergencias (Grupo A) aún no está integrado.")


class OperationsService:
    """Casos de uso y reglas de negocio del módulo operations."""

    def __init__(
        self,
        get_emergency_status: Callable[[int], str | None],
        repository: OperationsRepository,
    ) -> None:
        self._get_emergency_status = get_emergency_status
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
