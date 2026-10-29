from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from crisisops.core.database import get_db
from crisisops.core.exceptions import DomainError
from crisisops.modules.operations.repository import OperationsRepository
from crisisops.modules.operations.schemas import OperationCreate, OperationResponse
from crisisops.modules.operations.service import (
    OperationsService,
    get_emergency_status_from_group_a,
)

router = APIRouter(prefix="/operations", tags=["Grupo D - Operaciones y despacho"])


def get_operations_service(
    db: Annotated[Session, Depends(get_db)],
) -> OperationsService:
    """Crea el caso de uso para cada petición usando el repositorio local."""
    repository = OperationsRepository(db)
    return OperationsService(get_emergency_status_from_group_a, repository)


ServiceDEP = Annotated[OperationsService, Depends(get_operations_service)]


@router.get("/health")
def module_health() -> dict[str, str]:
    """Endpoint mínimo para verificar que el módulo quedó integrado."""
    return {"status": "ok", "module": "operations"}


@router.post(
    "",
    response_model=OperationResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        409: {"description": "La emergencia no está activa."},
        422: {"description": "Datos inválidos o la emergencia no existe."},
        503: {"description": "No se pudo consultar la emergencia en Grupo A."},
    },
    summary="Crear una operación vinculada a una emergencia válida",
)
def create_operation(
    payload: OperationCreate,
    service: ServiceDEP,
) -> OperationResponse:
    """Crea una operación solo si la emergencia existe y está activa."""
    try:
        operation = service.create_operation(payload)
    except DomainError as error:
        raise HTTPException(
            status_code=getattr(error, "status_code", status.HTTP_400_BAD_REQUEST),
            detail=str(error),
        ) from error

    return OperationResponse.model_validate(operation)


@router.get(
    "/{operation_id}",
    response_model=OperationResponse,
    status_code=status.HTTP_200_OK,
    responses={404: {"description": "Operación no encontrada."}},
    summary="Consultar una operación por su ID local",
)
def get_operation_by_id(
    operation_id: int,
    service: ServiceDEP,
) -> OperationResponse:
    """Devuelve una operación específica según su identificador local."""
    try:
        operation = service.get_operation(operation_id)
    except DomainError as error:
        raise HTTPException(
            status_code=getattr(error, "status_code", status.HTTP_400_BAD_REQUEST),
            detail=str(error),
        ) from error

    return OperationResponse.model_validate(operation)
