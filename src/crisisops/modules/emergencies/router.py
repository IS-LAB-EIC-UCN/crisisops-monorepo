from fastapi import APIRouter, Depends, status
from crisisops.core.database import get_db
from crisisops.modules.emergencies.service import EmergenciesService
from crisisops.modules.emergencies.enums import Role
from crisisops.modules.emergencies.schemas import EmergencyRead, EmergencyCreate, ValidationDecision
from sqlalchemy.orm import Session


router = APIRouter(prefix="/emergencies", tags=["Grupo A - Emergencias y evaluación"])


@router.get("/health")
def module_health() -> dict[str, str]:
    """Endpoint mínimo para verificar que el módulo quedó integrado."""
    return {"status": "ok", "module": "emergencies"}


@router.get(
    "/{emergency_id}/fields",
    status_code=status.HTTP_200_OK,
    summary = "Consultar si una emergencia esta completa para su posterior validación",
    description = (
        "Revisa los campos obligatorios de una emergencia"
        "e informa cuáles están incompletos o inválidos."
        "No modifica el estado de la emergencia."
    ),

)

def check_emergency_completeness_validation(
    emergency_id: int,
    db: Session = Depends(get_db)
) -> dict:
    return EmergenciesService(db).check_emergency_completeness(emergency_id)


@router.post(
    "",
    response_model = EmergencyRead,
    status_code = status.HTTP_201_CREATED,
    summary="Crear una emegencia",
    description="Se crea una emergencia, se envía la información y se valida a travez de EmergencyCreate con pydance"
)

def create_emegency(
    payload : EmergencyCreate,
    db: Session = Depends(get_db)
) -> EmergencyRead:
    
    emergency = EmergenciesService(db).create_emergency(payload)
    return EmergencyRead.model_validate(emergency)