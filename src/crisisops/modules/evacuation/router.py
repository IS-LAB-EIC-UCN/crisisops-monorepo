from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query, status
from sqlalchemy.orm import Session

from crisisops.core.database import get_db
from crisisops.modules.evacuation.models import (
    EvacuationStatus,
    ShelterAvailability,
)
from crisisops.modules.evacuation.repository import SituacionRepository
from crisisops.modules.evacuation.schemas import (
    EvacuationOut,
    SituacionRefugioOut,
    ShelterAvailabilityUpdate,
    ShelterAvailabilityOut,
)
from crisisops.modules.evacuation.service import SituacionService

router = APIRouter(prefix="/evacuation", tags=["Grupo E - Evacuación, refugios y alertas"])


def get_situacion_service(
    db: Annotated[Session, Depends(get_db)],
) -> SituacionService:
    repository = SituacionRepository(db)
    return SituacionService(repository)


@router.get("/evacuations", response_model=list[EvacuationOut])
def consultar_evacuaciones_vigentes(
    service: Annotated[SituacionService, Depends(get_situacion_service)],
    status: Annotated[
        EvacuationStatus,
        Query(description="Estado de la evacuación a consultar (ej. ACTIVE)"),
    ] = EvacuationStatus.ACTIVE,
) -> list[EvacuationOut]:
    """
    Contrato principal del Ticket Clase 15:
    GET /evacuations?status=ACTIVE
    """
    ordenes = service.listar_evacuaciones_vigentes(filtro_status=status)
    return [EvacuationOut.model_validate(o) for o in ordenes]


@router.get(
    "/refugios/{refugio_id}/situacion",
    response_model=SituacionRefugioOut,
)
def obtener_situacion_refugio(
    refugio_id: Annotated[int, Path(gt=0, description="ID del refugio")],
    service: Annotated[SituacionService, Depends(get_situacion_service)],
) -> SituacionRefugioOut:
    """
    Endpoint del recorrido descrito en el diagrama de la Clase 15:
    GET /refugios/{refugio_id}/situacion
    """
    return service.obtener_vigente(refugio_id=refugio_id)

@router.patch(
    "/refugios/{refugio_id}/disponibilidad",
    response_model=ShelterAvailabilityOut,
    status_code=status.HTTP_200_OK,
)
def actualizar_disponibilidad_refugio(
    refugio_id: Annotated[int, Path(gt=0, description="ID del refugio")],
    datos: ShelterAvailabilityUpdate,
    service: Annotated[SituacionService, Depends(get_situacion_service)],
) -> ShelterAvailabilityOut:
    refugio = service.actualizar_disponibilidad_refugio(
        refugio_id=refugio_id,
        disponibilidad=datos.availability,
    )
    return ShelterAvailabilityOut.model_validate(refugio)

@router.get("/health", tags=["Health"])
def health_check() -> dict:
    return {"status": "ok"}