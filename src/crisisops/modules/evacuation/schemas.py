from datetime import datetime

from pydantic import BaseModel, ConfigDict

from crisisops.modules.evacuation.models import EvacuationStatus


class EvacuationOut(BaseModel):

    model_config = ConfigDict(from_attributes=True)

    id: int
    emergency_id: str
    status: EvacuationStatus
    people_in_motion: int


class MovimientoPersonasOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    emergency_id: int | None
    people_count: int
    location: str
    recorded_at: datetime


class SituacionRefugioOut(BaseModel):

    refugio_id: int
    nombre: str
    capacidad: int
    ocupacion_actual: int
    personas_en_movimiento: int
    cupos_disponibles: int
    alerta_sobrecupo: bool
    evacuaciones_activas: list[EvacuationOut]
    movimientos_recientes: list[MovimientoPersonasOut]