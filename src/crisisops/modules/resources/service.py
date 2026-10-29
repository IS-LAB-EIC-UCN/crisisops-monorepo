import logging
from datetime import date
from typing import Any

from fastapi import HTTPException, status

from crisisops.modules.resources.models import Resource, implementos
from crisisops.modules.resources.repository import ResourcesRepository
from crisisops.modules.resources.schemas import (
    CambioEstadoOut,
    ImplementoIn,
    ImplementoOut,
    ResourceStatus,
)

logger = logging.getLogger(__name__)

class ResourcesService:

    def __init__(self, repository: ResourcesRepository) -> None:
        self.repository = repository

    def listar_recursos_disponibles(
        self,
        tipo: str | None = None,
        capacidad_min: int | None = None,
    ) -> list[dict[str, Any]]:
        return self.repository.obtener_disponibles(
            tipo=tipo, capacidad_minima=capacidad_min
        )

    def obtener_recurso_por_id(self, id_recurso: int) -> dict[str, Any]:
        recurso = self.repository.obtener_por_id(id_recurso)
        if not recurso:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Recurso con id {id_recurso} no encontrado.",
            )
        return recurso

    def registrar_implemento(self, datos: ImplementoIn) -> ImplementoOut:
        fecha_ingreso = date.today()
        recurso = Resource(
            name=datos.nombreRecurso,
            fecha_ingreso=fecha_ingreso,
            estado_recurso=datos.estadoRecurso.value,
            peso=datos.peso,
        )

        implemento = implementos(
            tipo_implemento=datos.tipoImplemento,
            año=datos.anio or fecha_ingreso.year,
            tipo_uso=datos.tipoUso,
            estado_fisico=datos.estadoFisico,
        )

        self.repository.guardar_implemento(recurso, implemento)

        return ImplementoOut(
            idRecurso=recurso.id,
            nombreRecurso=recurso.name,
            fechaIngreso=recurso.fecha_ingreso,
            estadoRecurso=recurso.estado_recurso,
            peso=recurso.peso,
            tipoImplemento=implemento.tipo_implemento,
            anio=implemento.año,
            tipoUso=implemento.tipo_uso,
            estadoFisico=implemento.estado_fisico,
        )

    
    def enviar_a_mantenimiento(self, id_recurso: int) -> CambioEstadoOut:
        return self._cambiar_estado(
        id_recurso,
        desde=ResourceStatus.DISPONIBLE,
        hacia=ResourceStatus.EN_MANTENIMIENTO,
        accion="enviar a mantenimiento",
    )

    def retornar_a_servicio(self, id_recurso: int) -> CambioEstadoOut:
        return self._cambiar_estado(
            id_recurso,
            desde=ResourceStatus.EN_MANTENIMIENTO,
            hacia=ResourceStatus.DISPONIBLE,
            accion="retornar a servicio",
        )

    def _cambiar_estado(
        self, id_recurso: int, desde: ResourceStatus, hacia: ResourceStatus, accion: str
    ) -> CambioEstadoOut:
        if not self.repository.cambiar_estado(id_recurso, desde.value, hacia.value):
            recurso = self.repository.obtener_por_id(id_recurso)
            if recurso is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Recurso con id {id_recurso} no encontrado.",
                )
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    f"No se puede {accion}: el recurso está en estado "
                    f"'{recurso.estado_recurso}' y debe estar en '{desde.value}'."
                ),
            )
        recurso = self.repository.obtener_por_id(id_recurso)
        logger.info("Recurso %s: %s -> %s", id_recurso, desde.value, hacia.value)
        return CambioEstadoOut(
            idRecurso=recurso.id,
            nombreRecurso=recurso.name,
            estadoAnterior=desde.value,
            estadoActual=hacia.value,
        )