from fastapi import APIRouter, HTTPException, status

from crisisops.core.exceptions import DomainError
from crisisops.modules.operations.dependencies import ServiceDEP
from crisisops.modules.operations.schemas.operation import OperationCreate, OperationResponse

router = APIRouter(prefix="/operations", tags=["Grupo D - Operaciones y despacho"])


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
