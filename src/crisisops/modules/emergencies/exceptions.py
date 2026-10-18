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
