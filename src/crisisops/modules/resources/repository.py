from collections.abc import Sequence
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from crisisops.modules.resources.models import Resource, Vehiculo, implementos

from crisisops.modules.personnel.models import Certification, Responder, ResponderSkill, Skill

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

    def obtener_implemento(self, id_recurso: int) -> implementos | None:
        return self.db.get(implementos, id_recurso)

    def obtener_operador_por_id(self, responder_id: int) -> Responder | None:
        return self.db.get(Responder, responder_id)

    def obtener_habilidad_por_codigo(self, skill_code: str) -> Skill | None:
        stmt = select(Skill).where(Skill.code == skill_code)
        return self.db.scalar(stmt)

    def operador_tiene_habilidad(self, responder_id: int, skill_code: str) -> bool:
        stmt = select(ResponderSkill).where(
            ResponderSkill.responder_id == responder_id,
            ResponderSkill.skill_code == skill_code,
        )
        return self.db.scalar(stmt) is not None

    def obtener_certificaciones_operador(
        self, responder_id: int, skill_code: str
    ) -> Sequence[Certification]:
        stmt = select(Certification).where(
            Certification.responder_id == responder_id,
            Certification.skill_code == skill_code,
        )
        return self.db.scalars(stmt).all()