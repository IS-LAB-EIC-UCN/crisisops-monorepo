from collections.abc import Sequence
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy import select, update

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

    def guardar_implemento(self, recurso: Resource, implemento: implementos) -> Resource:
        self.db.add(recurso)
        self.db.flush()
        implemento.id_recursos = recurso.id
        self.db.add(implemento)
        self.db.commit()
        self.db.refresh(recurso)
        self.db.refresh(implemento)

        return recurso
    
    #def de cambio de estado de recurso
    def cambiar_estado(self, id_recurso: int, desde: str, hacia: str) -> bool:
        try:
            resultado = self.db.execute(
                update(Resource)
                .where(Resource.id == id_recurso, Resource.estado_recurso == desde)
                .values(estado_recurso=hacia)
            )
            self.db.commit()
        except Exception:
            self.db.rollback()
            raise
        return resultado.rowcount == 1