from datetime import date, datetime, timezone
from typing import Any

from fastapi import HTTPException, status

from crisisops.modules.resources.models import Resource, implementos
from crisisops.modules.resources.repository import ResourcesRepository
from crisisops.modules.resources.schemas import ImplementoIn, ImplementoOut, ValidacionCertificacionIn, ValidacionCertificacionOut
from crisisops.core.exceptions import DomainError

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

    def obtener_recurso_por_id(self, id_recurso: int) -> ImplementoOut | Resource:
        recurso = self.repository.obtener_por_id(id_recurso)
        if not recurso:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Recurso con id {id_recurso} no encontrado.",
            )
        implemento = self.repository.obtener_implemento(id_recurso)

        if implemento is not None:
            return self._a_implemento_out(recurso, implemento)
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

        return self._a_implemento_out(recurso, implemento)

    @staticmethod
    def _a_implemento_out(recurso: Resource, implemento: implementos) -> ImplementoOut:
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

    def validar_certificacion_operador(
        self, datos: ValidacionCertificacionIn
    ) -> ValidacionCertificacionOut:
        operador = self.repository.obtener_operador_por_id(datos.responder_id)
        if not operador:
            raise DomainError(f"El operador con ID {datos.responder_id} no existe.")

        if not operador.is_active:
            raise DomainError(f"El operador con ID {datos.responder_id} se encuentra inactivo.")

        habilidad = self.repository.obtener_habilidad_por_codigo(datos.skill_code)
        if not habilidad:
            raise DomainError(f"La habilidad '{datos.skill_code}' no existe.")

        if not self.repository.operador_tiene_habilidad(datos.responder_id, datos.skill_code):
            raise DomainError(
                f"El operador {datos.responder_id} no posee la habilidad requerida '{datos.skill_code}'."
            )

        certificaciones = self.repository.obtener_certificaciones_operador(
            datos.responder_id, datos.skill_code
        )
        if not certificaciones:
            raise DomainError(
                f"El operador {datos.responder_id} no cuenta con certificación para '{datos.skill_code}'."
            )

        ahora = datetime.now(timezone.utc)
        vigente = any(
            (c.issued_at.replace(tzinfo=timezone.utc) if c.issued_at.tzinfo is None else c.issued_at)
            <= ahora
            < (c.expires_at.replace(tzinfo=timezone.utc) if c.expires_at.tzinfo is None else c.expires_at)
            for c in certificaciones
        )
        if not vigente:
            raise DomainError(
                f"La certificación del operador {datos.responder_id} para '{datos.skill_code}' está vencida o no vigente."
            )

        return ValidacionCertificacionOut(
            valido=True,
            responder_id=datos.responder_id,
            skill_code=datos.skill_code,
            mensaje="Certificación válida.",
        )