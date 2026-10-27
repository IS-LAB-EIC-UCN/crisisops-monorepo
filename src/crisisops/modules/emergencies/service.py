#from crisisops.modules.emergencies.rules import find_field_issues
from crisisops.modules.emergencies.enums import EmergencyStatus, Role
from typing import ParamSpec, TypeVar
from functools import wraps
from collections.abc import Callable
from crisisops.modules.emergencies.models import Emergency
from crisisops.modules.emergencies.schemas import EmergencyCreate, ValidationDecision
from crisisops.modules.emergencies.exceptions import EmergencyNotFound, InvalidStateTransition, ExceptionActionRequiresJustification, EmergencyValidationError
from crisisops.modules.emergencies.validators import schemas_validate_emergency
from crisisops.modules.emergencies.repository import EmergenciesRepository



from sqlalchemy.orm import Session

'''
Esto es un decorador, envuelve un metodo para que haga commit() si todo sale bien
y rollback() si algo falla. Los parámetros P (nombre que representa los parámetros de una función cualquiera) 
y R (representa el tipo de devuelve la función).

func que aparece en wraps(func) primeramente, es la función original que vamos a envolver, en este primer caso validate_emergency.
Callable(P,R), es algo que se puede llamar que tiene parámetos de entrada y que devuelve R
-> Callable(P,R), Devuelve otra función con los mismo parámetros y el mismo retornno

def wrapper(...) es la función que realmente se ejecutará cada vez que se llame al metodo decorado.

EJEMPLO: AL LLAMAR EMERGENCIESSERVICE.validate_emergency en realidad corre wrapper(self, parametros que le pasamos a la funcion
validation_emergency) ejecuta el método y, según el resultado, hace el commit o rollback.

LO DEJO TODO COMENTADO  PARA ANALIZARLO Y DECIDIR SI SE OCUPA O SE BUSCA OTRA FORMA PARA REALIZAR TODA LA OPERACIÓN
QUE REQUIERE INTERACTUAR CON LA BASE DE DATOS Y POSIBLE ERRORES.
'''
P = ParamSpec("P")
R = TypeVar("R")

def _transactional(func: Callable[P,R]) -> Callable[P,R]:

    @wraps(func)
    def wrapper(self: "EmergenciesService", *args: P.args, **kwargs: P.kwargs) -> R:
        try:
            result = func(self, *args, **kwargs) #ejercita el método original
            self.db.commit() #Si no hubo error, confirma los cambios
            return result #devuelve lo que devolvio el metodo
        except Exception:
            self.db.rollback() #si hubo culquier error, deshace todo
            raise #propaga el mismo error
    return wrapper

VALIDATE_ROLES = (Role.OPERATOR)


class EmergenciesService:
    """Casos de uso y reglas de negocio del módulo emergencies."""

    def __init__(self, db: Session) -> None:
        self.db = db
        self.repo = EmergenciesRepository(db) 

    #Lectura
    def get_or_raise(self,emergency_id: int) -> Emergency:
        emergency = self.repo.get(emergency_id)
        if emergency is None:
            raise EmergencyNotFound(f"No existe una emergencia con id={emergency_id}")
        return emergency

    #función para registrar una emergencia
    @_transactional
    def create_emergency(self, payload: EmergencyCreate) -> Emergency:
        
        emergency = Emergency(
            title = payload.title,
            type = payload.type,
            type_detail = payload.type_detail,
            description = payload.description,
            severity = payload.severity,
            location_description = payload.location_description,
            status = EmergencyStatus.REPORTED,
            reported_by = payload.reported_by

        )

        self.repo.add(emergency)

        return emergency

    #función para detecta campos faltantes, incompletos o que no cumplen lo requisitos.
    @_transactional
    def check_emergency_completeness(self, emergency_id: int) -> dict:

        emergency = self.get_or_raise(emergency_id)

        if emergency is None:
            raise EmergencyNotFound(
                f"No existe la emergencia {emergency_id}"
            )
        try:
            schemas_validate_emergency(emergency)

        except EmergencyValidationError as e:

            return{
                "emergency_id": emergency_id,
                "ready_for_validation": False,
                "errors_fields": e.errors
            }
        
        return{
            "emergency_id": emergency_id,
            "ready_for_validation": True,
            "errors_fields": {}
        }
            

    #función para validar una emergencia
    @_transactional
    def validate_emergency(self, emergency_id: int, decision: ValidationDecision, actor_role: Role) -> Emergency:

        emergency = self.get_or_raise(emergency_id) #obtenemos la emergencia que deseamos validar por medio de su ID

        schemas_validate_emergency(emergency) #Esta función se encarga de validar que la emergencia tenga los campos requeridos para su validación, en el caso que no lo tenga devuelve un diccionario con los campos requeridos o faltantes

        target = EmergencyStatus.VALIDATED if decision.approved else EmergencyStatus.REJECTED #Almacena el status VALIDATED en el caso que la decision sea True, en caso contario REJECTED.


        if not decision.approved and not decision.reason: #si la decision es REJECTED, se debe adjuntar un razón en caso contrario se produce un error
            raise ExceptionActionRequiresJustification(
                "Rechazar una reporte requiere indicar el motivo (reason)."
            )

        if emergency.status != EmergencyStatus.REPORTED: #El status para la validación debe ser REPORTED, no puede ser por ejemplo: CANCELLED
            
            raise InvalidStateTransition(

                f"No es posible validar la emergencia {emergency_id}: estado actual es"
                f"{emergency.status.value}, se esperaba REPORTED"
            )

        emergency.status = target #se asigna a la emergencia su nuevo status
        
        return emergency
    
        
        