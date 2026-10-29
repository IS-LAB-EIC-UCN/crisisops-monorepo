from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from crisisops.modules.evacuation.models import (
    EvacuationOrder,
    PeopleMovement,
    Shelter,
    ShelterAdmission,
)


class SituacionRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_evacuations_by_status(self, status: str) -> list[EvacuationOrder]:
        stmt = select(EvacuationOrder).where(EvacuationOrder.status == status)
        return list(self.db.scalars(stmt).all())

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


class SalidaRepository:
    """Persistencia de la Historia 3: registrar salidas de un refugio."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def get_refugio_bloqueado(self, refugio_id: int) -> Shelter | None:

        stmt = select(Shelter).where(Shelter.id == refugio_id).with_for_update()
        return self.db.scalars(stmt).first()

    def get_admision_bloqueada(self, admision_id: int) -> ShelterAdmission | None:
        stmt = (
            select(ShelterAdmission)
            .where(ShelterAdmission.id == admision_id)
            .with_for_update()
        )
        return self.db.scalars(stmt).first()

    def confirmar(self) -> None:
        self.db.commit()

    def deshacer(self) -> None:
        self.db.rollback()
