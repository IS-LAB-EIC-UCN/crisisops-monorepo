from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from crisisops.core.database import get_db
from crisisops.core.exceptions import DomainError

from . import repository, schemas, service

router = APIRouter(prefix="/personnel", tags=["Grupo C - Personal y brigadas"])

@router.get("/health")
def module_health() -> dict[str, str]:
    """Endpoint mínimo para verificar que el módulo quedó integrado."""
    return {"status": "ok", "module": "personnel"}

@router.post(
    "/responders/{responder_id}/assignments", 
    response_model=schemas.AssignmentResponse, 
    status_code=status.HTTP_201_CREATED
)
def create_responder_assignment(
    responder_id: int,
    assignment: schemas.AssignmentCreate,
    db: Session = Depends(get_db)  # noqa: B008
):
    """
    Crea una nueva asignación para un brigadista.
    Retorna error 422 si existe solapamiento de turnos.
    """
    try:
        repo = repository.PersonnelRepository(db)
        svc = service.PersonnelService(repo)
        
        new_assignment = svc.create_assignment(responder_id, assignment)
        return new_assignment
        
    except DomainError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        ) from e