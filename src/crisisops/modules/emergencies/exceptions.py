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


'''Error para emergencia no encontrada'''
class EmergencyNotFound(DomainError):
    http_status = 404
    code = "emergency_not_found"

'''Error validación emergencia para su posterior validacion'''

class EmergencyValidationError(DomainError):
    http_status = 422
    code = "emergency_validation_error"

    def __init__(self, errors: list[dict]) -> None: #Pasamos como vimos en Validators.py un diccionario con los errores relacionados con Pydantic.
        super().__init__(
            "La emergencia no cumple los requisitos de validación" #Se adjunto un mensaje explicativo
        )
        self.errors = errors # se guarda el diccionario en el atributo errors

class InvalidStateTransition(DomainError):
    '''Se intento una transición invalida, por ejemplo VALIDATED desde CLOSE'''
    http_status = 409
    code = "invalid_state_transition"

class ExceptionActionRequiresJustification(DomainError):
    '''Se necesita justificación para una acción, por ejemplo REJECTED un reporte necesita una razón (reason)'''
    http_status = 422
    code = "justification_required"