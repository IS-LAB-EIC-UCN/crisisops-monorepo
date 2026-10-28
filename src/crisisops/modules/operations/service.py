from collections.abc import Callable

from crisisops.core.exceptions import DomainError


class EmergencyNotFound(DomainError):
    status_code = 422


class EmergencyNotActive(DomainError):
    status_code = 409


class EmergencyUnavailable(DomainError):
    status_code = 503


class OperationsService:
    """Casos de uso y reglas de negocio del módulo operations."""

    def __init__(self, get_emergency_status: Callable[[int], str | None]) -> None:
        self._get_emergency_status = get_emergency_status

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
