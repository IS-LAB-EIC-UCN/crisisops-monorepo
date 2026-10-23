from collections.abc import Sequence
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from crisisops.modules.resources.models import Resource, Vehiculo, implementos


class ResourcesRepository:

    def __init__(self, db: Session) -> None:
        self.db = db

    def obtener_disponibles(
        self,
        tipo: str | None = None,
        capacidad_minima: int | None = None,
    ) -> Sequence[Any]:
        query = select(Resource).where(
            Resource.estado_recurso == "DISPONIBLE"
        )

        if tipo:
            tipo_upper = tipo.upper()
            if tipo_upper == "VEHICULO":
                query = query.join(Vehiculo, Resource.id == Vehiculo.id_recursos)
            elif tipo_upper == "IMPLEMENTO":
                query = query.join(implementos, Resource.id == implementos.id_recursos)

        if capacidad_minima is not None:
            if not tipo or tipo.upper() != "VEHICULO":
                query = query.join(Vehiculo, Resource.id == Vehiculo.id_recursos)
            query = query.where(Vehiculo.capacidad >= capacidad_minima)

        result = self.db.scalars(query).all()
        return result

    def obtener_todos(self, tipo: str | None = None) -> list[Any]:
        query = select(Resource)

        if tipo:
            tipo_upper = tipo.upper()
            if tipo_upper == "VEHICULO":
                query = query.join(Vehiculo, Resource.id == Vehiculo.id_recursos)
            elif tipo_upper == "IMPLEMENTO":
                query = query.join(implementos, Resource.id == implementos.id_recursos)

        return list(self.db.scalars(query).all())

    def obtener_por_id(self, id_recurso: int) -> Any | None:
        return self.db.get(Resource, id_recurso)