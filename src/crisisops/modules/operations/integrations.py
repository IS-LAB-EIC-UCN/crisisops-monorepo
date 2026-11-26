from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.exc import TimeoutError as SQLAlchemyTimeoutError
from sqlalchemy.orm import Session

from crisisops.modules.emergencies.exceptions import (
    EmergencyNotFound as GroupAEmergencyNotFound,
)
from crisisops.modules.emergencies.service import EmergenciesService


def get_emergency_status_from_group_a(db: Session, emergency_id: int) -> str | None:
    """Consulta el estado de una emergencia usando el servicio real de Grupo A."""
    try:
        emergency = EmergenciesService(db).get_or_raise(emergency_id)
    except GroupAEmergencyNotFound:
        return None
    except SQLAlchemyTimeoutError as error:
        raise TimeoutError(
            f"Se agotó el tiempo consultando la emergencia {emergency_id} en Grupo A."
        ) from error
    except SQLAlchemyError as error:
        raise ConnectionError(
            f"No se pudo consultar la emergencia {emergency_id} en Grupo A."
        ) from error

    return emergency.status.value


def get_resource_types_from_group_b() -> set[str]:
    """Consulta los tipos de recurso de Grupo B. Mientras B no los exponga, no responde."""
    raise ConnectionError("El catálogo de tipos de recurso (Grupo B) aún no está disponible.")


def get_personnel_profiles_from_group_c() -> set[str]:
    """Consulta los perfiles (skills) de Grupo C. Mientras C no los exponga, no responde."""
    raise ConnectionError("El catálogo de perfiles de personal (Grupo C) aún no está disponible.")
