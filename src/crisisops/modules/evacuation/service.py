from datetime import UTC, datetime, timedelta

from fastapi import HTTPException, status

from crisisops.modules.evacuation.models import (
    EvacuationOrder,
    EvacuationStatus,
    Shelter,
    ShelterAvailability,
)
from crisisops.modules.evacuation.repository import SituacionRepository
from crisisops.modules.evacuation.schemas import (
    EvacuationOut,
    MovimientoPersonasOut,
    SituacionRefugioOut,
)


class SituacionService:
    def __init__(self, repository: SituacionRepository) -> None:
        self.repository = repository

    def listar_evacuaciones_vigentes(
        self, filtro_status: EvacuationStatus
    ) -> list[EvacuationOrder]:
        """
        Regla de negocio:
        Al consultar la información de evacuaciones, el sistema debe filtrar y retornar
        únicamente aquellas órdenes vinculadas a emergencias que se encuentren en estado
        ACTIVE (Activa / Vigente). Las órdenes en estado LIFTED o CANCELLED no deben
        ser incluidas.
        """
        if filtro_status in (EvacuationStatus.LIFTED, EvacuationStatus.CANCELLED):
            return []

        if filtro_status != EvacuationStatus.ACTIVE:
            return []

        estados_excluidos = (
            EvacuationStatus.LIFTED.value,
            EvacuationStatus.CANCELLED.value,
        )
        ordenes = self.repository.get_evacuations_by_status(EvacuationStatus.ACTIVE.value)
        return [
            orden
            for orden in ordenes
            if orden.status == EvacuationStatus.ACTIVE.value
            and orden.status not in estados_excluidos
        ]

    def obtener_vigente(self, refugio_id: int) -> SituacionRefugioOut:
        """
        Aplica la regla de negocio del diagrama:
        - Verifica que el refugio exista.
        - Filtra solo lo vigente (evacuaciones/emergencias ACTIVE y movimientos últimos 15 min).
        - Calcula cupos_disponibles y alerta_sobrecupo.
        """
        hace_15_min = datetime.now(UTC) - timedelta(minutes=15)
        refugio, evacuaciones, movimientos = self.repository.get_vigente(
            refugio_id=refugio_id, ventana_tiempo=hace_15_min
        )

        if refugio is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Refugio con id {refugio_id} no encontrado.",
            )

        evacuaciones_vigentes = [
            ev
            for ev in evacuaciones
            if ev.status == EvacuationStatus.ACTIVE.value
        ]

        personas_en_movimiento = sum(m.people_count for m in movimientos)
        cupos_disponibles = max(0, refugio.capacity - refugio.current_occupancy)
        alerta_sobrecupo = (
            refugio.current_occupancy + personas_en_movimiento
        ) > refugio.capacity

        return SituacionRefugioOut(
            refugio_id=refugio.id,
            nombre=refugio.name,
            capacidad=refugio.capacity,
            ocupacion_actual=refugio.current_occupancy,
            personas_en_movimiento=personas_en_movimiento,
            cupos_disponibles=cupos_disponibles,
            alerta_sobrecupo=alerta_sobrecupo,
            evacuaciones_activas=[
                EvacuationOut.model_validate(ev) for ev in evacuaciones_vigentes
            ],
            movimientos_recientes=[
                MovimientoPersonasOut.model_validate(m) for m in movimientos
            ],
        )
    
    def actualizar_disponibilidad_refugio(self, refugio_id: int, disponibilidad: ShelterAvailability) -> Shelter:
        refugio = self.repository.actualizar_disponibilidad_refugio(
            refugio_id=refugio_id,
            disponibilidad=disponibilidad,
        )

        if refugio is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Refugio con id {refugio_id} no encontrado.",
            )

        return refugio