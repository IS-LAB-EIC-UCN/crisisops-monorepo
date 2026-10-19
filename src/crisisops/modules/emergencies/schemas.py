"""Esquemas Pydantic públicos del módulo.

Los contratos consumidos por otros módulos deben mantenerse pequeños,
explícitos y versionables.
"""
from pydantic import BaseModel, ConfigDict, Field
from crisisops.modules.emergencies.enums import EmergencyType, EmergencyStatus
from crisisops.shared.enums import Severity
from datetime import UTC,datetime


class EmergencyCreate(BaseModel):

    type: EmergencyType

    type_detail: str|None = Field(
        default=None, max_length=150, description="Requerido/util cuando type=OTHER"
    )
    title: str | None = Field(default=None,min_length=5, max_length=150)

    description: str | None = Field(default=None,min_length=10)

    severity : Severity | None = None

    location_description: str | None = Field(
        default=None,
        min_length=3,
        max_length=250,
        description="Ubicacion"
    )

    reported_by : str

class EmergencyRead(BaseModel):

    model_config = ConfigDict(from_attributes=True) #Pydantic solo sabe estrcuturar datos cuando se les pasa un diccionario, los ORM guardan datos como atributos

    id: int
    type: EmergencyType
    title: str | None
    type_detail: str | None
    description: str | None
    severity: Severity | None
    location_description: str | None
    status: EmergencyStatus
    reported_by: str
    created_at: datetime
    updated_at: datetime

