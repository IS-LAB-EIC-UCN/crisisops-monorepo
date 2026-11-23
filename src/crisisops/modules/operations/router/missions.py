from fastapi import APIRouter, HTTPException, status

from crisisops.core.exceptions import DomainError
from crisisops.modules.operations.dependencies import MissionsServiceDEP
from crisisops.modules.operations.models import MissionResourceRequirement
from crisisops.modules.operations.schemas.mission import MissionCreate, MissionResponse
from crisisops.modules.operations.schemas.requirement import (
    PersonnelRequirementResponse,
    RequirementCreate,
    RequirementResponse,
    ResourceRequirementResponse,
)

router = APIRouter(prefix="/operations", tags=["Grupo D - Operaciones y despacho"])


@router.post(
    "/{operation_id}/missions",
    response_model=MissionResponse,
    status_code=status.HTTP_201_CREATED,
    responses={404: {"description": "Operación no encontrada."}},
    summary="Crear una misión asociada a una operación existente",
)
def create_mission(
    operation_id: int,
    payload: MissionCreate,
    service: MissionsServiceDEP,
) -> MissionResponse:
    """Crea una misión en estado inicial PLANNED."""
    try:
        mission = service.create_mission(operation_id, payload)
    except DomainError as error:
        raise HTTPException(
            status_code=getattr(error, "status_code", status.HTTP_400_BAD_REQUEST),
            detail=str(error),
        ) from error

    return MissionResponse.model_validate(mission)


@router.post(
    "/missions/{mission_id}/requirements",
    response_model=RequirementResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        404: {"description": "Misión no encontrada."},
        422: {"description": "Requisito inválido."},
        503: {"description": "Catálogo no disponible."},
    },
    summary="Agregar un requisito de recurso o personal a una misión",
)
def add_mission_requirement(
    mission_id: int,
    payload: RequirementCreate,
    service: MissionsServiceDEP,
) -> ResourceRequirementResponse | PersonnelRequirementResponse:
    """Agrega un requisito validando cantidad y catálogo."""
    try:
        requirement = service.add_requirement(mission_id, payload)
    except DomainError as error:
        raise HTTPException(
            status_code=getattr(error, "status_code", status.HTTP_400_BAD_REQUEST),
            detail=str(error),
        ) from error

    if isinstance(requirement, MissionResourceRequirement):
        return ResourceRequirementResponse.model_validate(requirement)

    return PersonnelRequirementResponse.model_validate(requirement)


@router.get(
    "/missions/{mission_id}",
    response_model=MissionResponse,
    status_code=status.HTTP_200_OK,
    responses={404: {"description": "Misión no encontrada."}},
    summary="Consultar una misión por ID con sus requisitos",
)
def get_mission_by_id(
    mission_id: int,
    service: MissionsServiceDEP,
) -> MissionResponse:
    """Devuelve la misión y los requisitos de recursos y personal."""
    try:
        mission = service.get_mission(mission_id)
    except DomainError as error:
        raise HTTPException(
            status_code=getattr(error, "status_code", status.HTTP_400_BAD_REQUEST),
            detail=str(error),
        ) from error

    return MissionResponse.model_validate(mission)
