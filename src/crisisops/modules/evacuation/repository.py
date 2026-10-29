from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from crisisops.modules.evacuation.models import (
    EvacuationOrder,
    PeopleMovement,
    Shelter,
    ShelterAvailability,
)


class SituacionRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_evacuations_by_status(self, status: str) -> list[EvacuationOrder]:
        stmt = select(EvacuationOrder).where(EvacuationOrder.status == status)
        return list(self.db.scalars(stmt).all())

    def actualizar_disponibilidad_refugio(
        self, refugio_id: int, disponibilidad: ShelterAvailability
    ) -> Shelter | None:
        refugio = self.db.get(Shelter, refugio_id)

        if refugio is None:
            return None

        refugio.availability = disponibilidad.value
        self.db.commit()
        self.db.refresh(refugio)

        return refugio

    def get_vigente(
        self, refugio_id: int, ventana_tiempo: datetime
    ) -> tuple[Shelter | None, list[EvacuationOrder], list[PeopleMovement]]:

        refugio = self.db.get(Shelter, refugio_id)

        stmt_evacuaciones = select(EvacuationOrder)
        evacuaciones = list(self.db.scalars(stmt_evacuaciones).all())

        stmt_movimientos = select(PeopleMovement).where(
            PeopleMovement.recorded_at >= ventana_tiempo
        )
        if refugio is not None:
            stmt_movimientos = stmt_movimientos.where(
                (PeopleMovement.shelter_id == refugio_id)
                | (PeopleMovement.location == refugio.location)
            )
        movimientos = list(self.db.scalars(stmt_movimientos).all())

        return refugio, evacuaciones, movimientos