
from crisisops.core.exceptions import DomainError


class RefugioNoEncontrado(DomainError):
    def __init__(self, refugio_id: int) -> None:
        super().__init__(f"Refugio con id {refugio_id} no encontrado.")


class AdmisionNoEncontrada(DomainError):
    def __init__(self, admision_id: int, refugio_id: int) -> None:
        super().__init__(
            f"No existe la admisión {admision_id} en el refugio {refugio_id}."
        )


class SalidaYaRegistrada(DomainError):
    def __init__(self, admision_id: int) -> None:
        super().__init__(
            f"La admisión {admision_id} ya tiene una salida registrada; "
            "no se pueden liberar cupos dos veces."
        )


class OcupacionInconsistente(DomainError):
    def __init__(self, refugio_id: int, ocupacion: int, personas: int) -> None:
        super().__init__(
            f"La ocupación del refugio {refugio_id} ({ocupacion}) es menor que las "
            f"personas de la admisión ({personas}); la salida dejaría ocupación negativa."
        )
