from fastapi import APIRouter, Depends
from crisisops.core.database import get_db
from crisisops.modules.emergencies.service import EmergenciesService
from crisisops.modules.emergencies.enums import Role
from crisisops.modules.emergencies.schemas import ValidationDecision, EmergencyRead
from sqlalchemy.orm import Session

router = APIRouter(prefix="/emergencies", tags=["Grupo A - Emergencias y evaluación"])

'''
Estos son los roles que esta autorizados para realizar X operación
en este caso se puede utilizar para validar_reporte
pero como no tenemos aun la tabla de Usuarios que deberia tener
el rol/cargo del usuario entonces por esto solo lo hacemos 
indicando manualmente que rol tiene el que esta validando
_OPERATOR_UP = (Role.OPERATOR)
'''


@router.get("/health")
def module_health() -> dict[str, str]:
    """Endpoint mínimo para verificar que el módulo quedó integrado."""
    return {"status": "ok", "module": "emergencies"}

@router.post(
    "{emergency_id}/validate", 
    response_model=EmergencyRead,
    summary="Validar o rechar una emergencia",
    description=("approved=True valida el reporte (reported -> validated)."
                 "aproved=false lo rechaza (reported->rejected) y exige una motivo 'reason"
                 'requiere un rol correcto para realizar operación'),
)

def validate_emergency(
    emergency_id: int,
    payload: ValidationDecision, #ValidationDecision, contiene la decisión si se aprueba o rechaza la validación y el motivo
    actor_role: Role,
    db: Session = Depends(get_db), #llamamos a la función db en database.py, depends toma lo que se le pase y lo inyecta como parámetro
    
    #Acá puede ir otro parámetro como User que use depends y se le pase una función que verifique si el 
    #usuario actual pertenece a los roles en _OPERATOR_UP
) -> EmergencyRead: #esto indica que se devuelve una clase EmergencyRead en schemas.py que hereda de BaseModel de pydantic 
    #que valida lo que se devuelve.
    emergency = EmergenciesService(db).validate_emergency(emergency_id, payload,actor_role)
    return EmergencyRead.model_validate(emergency) #se valida
    


