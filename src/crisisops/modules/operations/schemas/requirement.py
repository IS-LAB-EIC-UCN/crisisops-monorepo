from enum import StrEnum
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field


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
