from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from crisisops.core.database import get_db
from crisisops.core.exceptions import DomainError
from crisisops.modules.personnel.repository import PersonnelRepository
from crisisops.modules.personnel.schemas import (
    AssignmentCreate,
    AssignmentResponse,
    EligibilityQuery,
    ResponderOut,
)
from crisisops.modules.personnel.service import PersonnelService

router = APIRouter(prefix="/personnel", tags=["Grupo C - Personal y brigadas"])

def get_personnel_service(db: Session = Depends(get_db)) -> PersonnelService:  # noqa: B008
    repository = PersonnelRepository(db)
    return PersonnelService(repository)

@router.get("/health")
def module_health() -> dict[str, str]:
    """Endpoint mínimo para verificar que el módulo quedó integrado."""
    return {"status": "ok", "module": "personnel"}

@router.post(
    "/responders/{responder_id}/assignments", 
    response_model=AssignmentResponse, 
    status_code=status.HTTP_201_CREATED
)
def create_responder_assignment(
    responder_id: int,
    assignment_in: AssignmentCreate,
    service: PersonnelService = Depends(get_personnel_service)  # noqa: B008
):    
    """Crea una nueva asignación validando que no se solape con las existentes."""
    try:
        return service.create_assignment(responder_id, assignment_in)
    except DomainError as e:
        # Retorna error 422 si hay solapamiento, cumpliendo el criterio de aceptación
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e)
        ) from e
    except ValueError as e:
        # Retorna error 422 si la fecha de inicio es mayor o igual a la de fin
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e)
        ) from e

@router.post(
    "/responders/eligible",
    response_model=list[ResponderOut],
    status_code=status.HTTP_200_OK,
    summary="Buscar personal elegible por disponibilidad y competencias"
)
def find_eligible_responders(
    query: EligibilityQuery,
    service: PersonnelService = Depends(get_personnel_service)  # noqa: B008
):
    """
    Retorna la lista de brigadistas que cumplen con las competencias requeridas,
    tienen un turno que cubre el período, poseen certificación vigente y no 
    tienen asignaciones solapadas.
    """
    if query.start_time >= query.end_time:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, 
            detail="La fecha de inicio debe ser anterior a la fecha de fin"
        )
    
    # Se asume la firma implementada por Gabriel en T2.4
    responders = service.get_eligible_responders(
        required_skills=query.required_skills,
        start_time=query.start_time,
        end_time=query.end_time
    )
    
    return responders