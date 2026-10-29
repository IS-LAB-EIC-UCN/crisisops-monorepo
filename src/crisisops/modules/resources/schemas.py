"""Esquemas Pydantic públicos del módulo.

Los contratos consumidos por otros módulos deben mantenerse pequeños,
explícitos y versionables.
"""
from datetime import date
from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class ResourceStatus(StrEnum):
    DISPONIBLE = "DISPONIBLE"
    RESERVED = "RESERVED"
    DEPLOYED = "DEPLOYED"
    MAINTENANCE = "MAINTENANCE"
    EN_MANTENIMIENTO = "EN MANTENIMIENTO"
    OUT_OF_SERVICE = "OUT_OF_SERVICE"


class ResourceType(StrEnum):
    IMPLEMENTO = "IMPLEMENTO"
    VEHICULO = "VEHICULO"


class ResourceBaseOut(BaseModel):
    idRecurso: int = Field(validation_alias="id")
    nombreRecurso: str = Field(validation_alias="name")
    fechaIngreso: date = Field(validation_alias="fecha_ingreso")
    estadoRecurso: str = Field(validation_alias="estado_recurso")
    peso: float
    tipoRecurso: Literal["IMPLEMENTO", "VEHICULO"] = "IMPLEMENTO"

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class ImplementoOut(ResourceBaseOut):
    tipoRecurso: Literal["IMPLEMENTO"] = "IMPLEMENTO"
    tipoImplemento: str = Field(validation_alias="tipo_implemento")
    anio: int = Field(validation_alias="año")
    tipoUso: str = Field(validation_alias="tipo_uso")
    estadoFisico: str = Field(validation_alias="estado_fisico")


class VehiculoOut(ResourceBaseOut):
    tipoRecurso: Literal["VEHICULO"] = "VEHICULO"
    patente: str
    capacidad: int
    modelo: str
    tipoVehiculo: str = Field(validation_alias="tipo_vehiculo")
    anio: int = Field(validation_alias="año")
    ubicacion: str
    ultimaMantencion: date = Field(validation_alias="ultima_mantencion")
    ancho: float
    largo: float
    altura: float

class ImplementoIn(BaseModel):
    nombreRecurso: str = Field(min_length=1, max_length=100)
    estadoRecurso: ResourceStatus
    peso: float = Field(gt=0)
    tipoRecurso: Literal["IMPLEMENTO"]
    tipoImplemento: str = Field(min_length=1, max_length=100)
    tipoUso: str = Field(min_length=1, max_length=100)
    estadoFisico: str = Field(min_length=1, max_length=100)
    anio: int | None = Field(default=None, ge=1900)


ResourceDetailOut = ImplementoOut | VehiculoOut | ResourceBaseOut

#-----HU10----

class CambioEstadoOut(BaseModel):
    idRecurso: int
    nombreRecurso: str
    estadoAnterior: str
    estadoActual: str