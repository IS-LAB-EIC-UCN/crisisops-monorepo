from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from sqlalchemy.orm import Session

from crisisops.core.database import get_db
from crisisops.modules.evacuation.exceptions import (
    AdmisionNoEncontrada,
    OcupacionInconsistente,
    RefugioNoEncontrado,
    SalidaYaRegistrada,
)
from crisisops.modules.evacuation.models import EvacuationStatus
from crisisops.modules.evacuation.repository import SalidaRepository, SituacionRepository
from crisisops.modules.evacuation.schemas import (
    EvacuationOut,
    SalidaIn,
    SalidaOut,
    SituacionRefugioOut,
)
from crisisops.modules.evacuation.service import SalidaService, SituacionService

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

@router.get("/health", tags=["Health"])
def health_check() -> dict:
    return {"status": "ok"}


def get_salida_service(db: Annotated[Session, Depends(get_db)]) -> SalidaService:
    return SalidaService(SalidaRepository(db))


@router.post(
    "/shelters/{refugio_id}/departures",
    response_model=SalidaOut,
    status_code=status.HTTP_200_OK,
    summary="Registrar la salida de una persona o grupo (Historia 3)",
    responses={
        404: {"description": "Refugio o admisión no encontrados"},
        409: {"description": "La salida ya fue registrada o la ocupación es inconsistente"},
    },
)
def registrar_salida(
    refugio_id: Annotated[int, Path(gt=0, description="ID del refugio")],
    datos: SalidaIn,
    service: Annotated[SalidaService, Depends(get_salida_service)],
) -> SalidaOut:
    """
    POST /shelters/{id}/departures.
    Libera inmediatamente los cupos de la admisión indicada.
    """
    try:
        return service.registrar_salida(refugio_id=refugio_id, admision_id=datos.admission_id)
    except (RefugioNoEncontrado, AdmisionNoEncontrada) as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error)) from error
    except (SalidaYaRegistrada, OcupacionInconsistente) as error:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(error)) from error
