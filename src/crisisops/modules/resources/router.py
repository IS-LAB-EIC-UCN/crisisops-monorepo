from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from crisisops.core.database import get_db
from crisisops.core.exceptions import DomainError
from crisisops.modules.resources.repository import ResourcesRepository
from crisisops.modules.resources.schemas import ImplementoIn, ImplementoOut, ResourceDetailOut
from crisisops.modules.resources.service import ResourcesService
from crisisops.modules.resources.schemas import CambioEstadoOut

router = APIRouter(prefix="/resources", tags=["Grupo B - Recursos y equipamiento"])


def obtener_servicio_recursos(db: Annotated[Session, Depends(get_db)]) -> ResourcesService:
    repository = ResourcesRepository(db)
    return ResourcesService(repository)

ServiceDEP = Annotated[ResourcesService, Depends(obtener_servicio_recursos)]

@router.get("/health")
def module_health() -> dict[str, str]:
    """Endpoint mínimo para verificar que el módulo quedó integrado."""
    return {"status": "ok", "module": "resources"}


# GET /resources/disponibles
@router.get(
    "/disponibles",
    response_model=list[ResourceDetailOut],
    status_code=status.HTTP_200_OK,
    summary="Listar todos los recursos disponibles en el momento",
)
def get_recursos_disponibles(
    service: ServiceDEP,
    tipo: str | None = Query(default=None, 
                             description="Filtrar por tipo (ej: VEHICULO, IMPLEMENTO)"),
    capacidad: int | None = Query(default=None, ge=1, 
                                  description="Capacidad humana mínima")
    ) -> list:
    return service.listar_recursos_disponibles(tipo=tipo, capacidad_min=capacidad)


# GET /resources/{id}
@router.get(
    "/{id}",
    response_model=ResourceDetailOut,
    status_code=status.HTTP_200_OK,
    responses={404: {"description": "Recurso no encontrado"}},
    summary="Listar toda la información de un recurso en específico",
)
def get_recurso_por_id(
    service: ServiceDEP,
    id: int
) -> dict:
    return service.obtener_recurso_por_id(id_recurso=id)

# POST /resources
@router.post(
    "",
    response_model=ImplementoOut,
    status_code= status.HTTP_201_CREATED,
    responses={400: {"description": "Estado inicial inválido"}},
    summary="Registrar un nuevo recurso con su ficha",
)
def registrar_recurso(datos: ImplementoIn, service: ServiceDEP) -> ImplementoOut:
    try:
        return service.registrar_implemento(datos)
    except DomainError as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error)) from error

@router.post(
    "/{id}/mantenimiento",
    response_model=CambioEstadoOut,
    status_code=status.HTTP_200_OK,
    responses={404: {"description": "Recurso no encontrado"},
               409: {"description": "El recurso no está disponible"}},
    summary="Enviar un recurso a mantenimiento",
)
def enviar_a_mantenimiento(id: int, service: ServiceDEP) -> CambioEstadoOut:
    return service.enviar_a_mantenimiento(id)


@router.post(
    "/{id}/retorno-servicio",
    response_model=CambioEstadoOut,
    status_code=status.HTTP_200_OK,
    responses={404: {"description": "Recurso no encontrado"},
               409: {"description": "El recurso no está en mantenimiento"}},
    summary="Retornar un recurso de mantenimiento a servicio",
)
def retornar_a_servicio(id: int, service: ServiceDEP) -> CambioEstadoOut:
    return service.retornar_a_servicio(id)