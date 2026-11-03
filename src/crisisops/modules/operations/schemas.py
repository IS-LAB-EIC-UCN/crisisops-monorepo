"""Esquemas Pydantic públicos del módulo.

Los contratos consumidos por otros módulos deben mantenerse pequeños,
explícitos y versionables.
"""

from datetime import datetime
from enum import StrEnum
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field

from crisisops.modules.operations.models import MissionStatus
from crisisops.shared.enums import Priority


class OperationCreate(BaseModel):
    """Datos que debe recibir el backend para crear una operación."""

    model_config = ConfigDict(str_strip_whitespace=True)

    emergency_id: int = Field(gt=0)
    name: str = Field(min_length=1, max_length=150)
    priority: Priority


class OperationResponse(BaseModel):
    """Datos de una operación que devuelve la API al crearla o al consultarla por id."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    emergency_id: int
    name: str
    priority: Priority
    created_at: datetime


class RequirementType(StrEnum):
    RESOURCE = "RESOURCE"
    PERSONNEL = "PERSONNEL"


class ResourceRequirementCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    type: Literal[RequirementType.RESOURCE] = RequirementType.RESOURCE
    resource_type: str = Field(min_length=1, max_length=100)
    quantity: int = Field(ge=1, description="Debe ser mayor o igual a 1")


class PersonnelRequirementCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)
    type: Literal[RequirementType.PERSONNEL] = RequirementType.PERSONNEL
    profile: str = Field(min_length=1, max_length=100)
    quantity: int = Field(ge=1, description="Debe ser mayor o igual a 1")


RequirementCreate = Annotated[
    ResourceRequirementCreate | PersonnelRequirementCreate,
    Field(discriminator="type"),
]


class ResourceRequirementResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    mission_id: int
    resource_type: str
    quantity: int


class PersonnelRequirementResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    mission_id: int
    profile: str
    quantity: int


RequirementResponse = ResourceRequirementResponse | PersonnelRequirementResponse


# --- HU-02: Misiones ---
class MissionCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)
    name: str = Field(min_length=1, max_length=150)
    priority: Priority


class MissionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    operation_id: int
    name: str
    priority: Priority
    status: MissionStatus
    created_at: datetime
    resource_requirements: list[ResourceRequirementResponse] = []
    personnel_requirements: list[PersonnelRequirementResponse] = []
