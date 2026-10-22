from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from crisisops.core.database import get_db
from crisisops.modules.resources.repository import ResourcesRepository
from crisisops.modules.resources.schemas import ResourceDetailOut
from crisisops.modules.resources.service import ResourcesService

router = APIRouter(prefix="/inventario/recursos", tags=["Grupo B - Recursos y equipamiento"])


def obtener_servicio_recursos(db: Session = Depends(get_db)) -> ResourcesService:
    repository = ResourcesRepository(db)
    return ResourcesService(repository)


@router.get("/health")
def module_health() -> dict[str, str]:
    """Endpoint mínimo para verificar que el módulo quedó integrado."""
    return {"status": "ok", "module": "resources"}


# GET /inventario/recursos/disponibles
@router.get(
    "/disponibles",
    response_model=list[ResourceDetailOut],
    status_code=status.HTTP_200_OK,
    summary="Listar todos los recursos disponibles en el momento",
)
def get_recursos_disponibles(
    tipo: str | None = Query(default=None, description="Filtrar por tipo (ej: VEHICULO, IMPLEMENTO)"),
    capacidad: int | None = Query(default=None, ge=1, description="Capacidad humana mínima"),
    service: ResourcesService = Depends(obtener_servicio_recursos),
) -> list:
    return service.listar_recursos_disponibles(tipo=tipo, capacidad_min=capacidad)


# GET /inventario/recursos/tipo
@router.get(
    "/tipo",
    response_model=dict[str, list[ResourceDetailOut]],
    status_code=status.HTTP_200_OK,
    summary="Listar todos los recursos estructurados por tipo",
)
def get_recursos_por_tipo(
    tipo: str | None = Query(default=None, description="Filtrar un tipo específico"),
    service: ResourcesService = Depends(obtener_servicio_recursos),
) -> dict:
    return service.listar_recursos_por_tipo(tipo=tipo)


# GET /inventario/recursos/{id}
@router.get(
    "/{id}",
    response_model=ResourceDetailOut,
    status_code=status.HTTP_200_OK,
    responses={404: {"description": "Recurso no encontrado"}},
    summary="Listar toda la información de un recurso en específico",
)
def get_recurso_por_id(
    id: int,
    service: ResourcesService = Depends(obtener_servicio_recursos),
) -> dict:
    return service.obtener_recurso_por_id(id_recurso=id)
