from datetime import date
from typing import Any

from fastapi import HTTPException, status

from crisisops.modules.resources.models import Resource, implementos
from crisisops.modules.resources.repository import ResourcesRepository
from crisisops.modules.resources.schemas import ImplementoIn, ImplementoOut


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

    def listar_recursos_por_tipo(
        self,
        tipo: str | None = None,
    ) -> dict[str, list[dict[str, Any]]]:
        recursos = self.repository.obtener_todos(tipo=tipo)
        agrupados: dict[str, list[dict[str, Any]]] = {
            "VEHICULO": [],
            "IMPLEMENTO": [],
        }
        for recurso in recursos:
            categoria = str(recurso.get("tipoRecurso", "OTRO")).upper()
            if categoria not in agrupados:
                agrupados[categoria] = []
            agrupados[categoria].append(recurso)

        if tipo:
            clave = tipo.upper()
            return {clave: agrupados.get(clave, [])}

        return agrupados

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