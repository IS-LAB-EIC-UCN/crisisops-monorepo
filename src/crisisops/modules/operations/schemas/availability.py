"""Contratos de respuesta para la consulta de disponibilidad de una misión (HU-03)."""

from typing import Annotated, Literal

from pydantic import BaseModel, Field

from crisisops.modules.operations.schemas.requirement import RequirementType


class ResourceAvailability(BaseModel):
    type: Literal[RequirementType.RESOURCE] = RequirementType.RESOURCE
    requirement_id: int
    resource_type: str
    required_quantity: int = Field(ge=1)
    available_quantity: int = Field(ge=0)
    is_available: bool


class PersonnelAvailability(BaseModel):
    type: Literal[RequirementType.PERSONNEL] = RequirementType.PERSONNEL
    requirement_id: int
    profile: str
    required_quantity: int = Field(ge=1)
    available_quantity: int = Field(ge=0)
    is_available: bool


AvailabilityItem = Annotated[
    ResourceAvailability | PersonnelAvailability,
    Field(discriminator="type"),
]


class MissionAvailabilityResponse(BaseModel):
    """Resultado de solo lectura; no confirma ni crea reservas."""

    mission_id: int
    ready_to_reserve: bool
    requirements: list[AvailabilityItem] = Field(default_factory=list)
    reason: str | None = None
