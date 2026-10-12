'''
Como no se si esto debe ir en exception de la carpeta core y si se debe integrar aparte DE nuestro modulo y si eso requiere
coordinación con otros modulos, lo escribo
aquí para ir analizando.
'''

class DomainError(Exception):
    """Error esperado de negocio que puede traducirse a una respuesta HTTP controlada."""
    http_status: int = 400
    code: str = "domain_error"

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message

class InvalidStateTransition(DomainError):
    """Se intento ua transición invalida, por ejemplo VALIDATED DESDE CLOSE"""
    http_status = 409
    code = "invalid_state_transition"

class ExceptionalActionRequiresJustification(DomainError):
    '''Se necesita justificación para una acción, por ejemplo REJECTED un reporte necesitsa un razon (reason)'''
    http_status = 422
    code = ("justification_required")

class EmergencyNotFound(DomainError):
    http_status = 404
    code = "emergency_not_found"

class UnauthorizedAction(DomainError):
    http_status = 403
    code = "unathorized_action"

class MissingRequiredData(DomainError):
    http_status = 400
    code = "missing_require_data"
    
