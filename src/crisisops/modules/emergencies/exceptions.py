from typing import Any


class DomainError(Exception):
    """Error esperado de negocio que puede traducirse a una respuesta HTTP controlada."""

    http_status: int = 400
    code: str = "domain_error"

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


class EmergencyNotFound(DomainError):
    """Error para emergencia no encontrada."""

    http_status = 404
    code = "emergency_not_found"


class EmergencyValidationError(DomainError):
    """Error de validación de una emergencia."""

    http_status = 422
    code = "emergency_validation_error"

    def __init__(self, errors: list[dict[str, Any]]) -> None:
        super().__init__(
            "La emergencia no cumple los requisitos de validación"
        )
        self.errors = errors


class InvalidStateTransition(DomainError):
    """Se intentó una transición de estado inválida."""

    http_status = 409
    code = "invalid_state_transition"


class ExceptionActionRequiresJustification(DomainError):
    """Se necesita una justificación para realizar una acción."""

    http_status = 422
    code = "justification_required"


class InvalidEmergencyUpdate(DomainError):
    """La actualización de la emergencia no es válida."""

    http_status = 422
    code = "invalid_emergency_update"