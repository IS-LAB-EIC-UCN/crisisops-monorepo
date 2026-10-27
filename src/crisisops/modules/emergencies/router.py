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
    "/{emergency_id}/validate",
    response_model = EmergencyRead,
    status_code = status.HTTP_200_OK,
    summary = "Validar o rechazar una emergencia",
    description= ("approved=True valida el reporte (reported -> validated)"
                  "approved=False lo rechaza (reported -> rejected) y exige un motivo  reason"
                  "requiere un rol correcto para realizar operación"),
)

def validate_emergency(
    emergency_id: int,
    payload: ValidationDecision, #ValidationDecision contiene la decisión si se aprueba o rechaza la validación y el motivo.
    actor_role: Role, 
    db: Session = Depends(get_db), #Llamamos a la función db en database.py, depends toma lo que se le pase y lo inyecta como parámetro
    #Acá puede ir otro parámetro como User que use depends y se le pasa una función que verifique si el
    #usuario actual pertenece a los roles en _OPERATOR_UP
) -> EmergencyRead: #Esto indica que se devuelve una  clase EmergencyRead en schemas.py que hereda de BaseModel de pydantic
    emergency = EmergenciesService(db).validate_emergency(emergency_id, payload, actor_role) 
    return EmergencyRead.model_validate(emergency) #se valida

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