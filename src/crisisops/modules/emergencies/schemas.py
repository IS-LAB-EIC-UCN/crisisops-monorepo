"""Esquemas Pydantic públicos del módulo.

Los contratos consumidos por otros módulos deben mantenerse pequeños,
explícitos y versionables.
"""
from pydantic import BaseModel, ConfigDict, Field
from crisisops.modules.emergencies.enums import EmergencyType, EmergencyStatus
from datetime import UTC, datetime

class ValidationDecision(BaseModel):
    approved: bool
    reason: str | None = Field(
        default=None, description="Obligatorio cuanndo approved =false porque indica el movito del rechazo"
    )

#PODEMOS TENER OTRA CLASE BASEMODEL, QUE SEA PARA CUANDO SE CREA UNA EMERGENCIA PARA IDENTIFICAR LOS TIPOS VALIDOS DE CAMPOS
#PARA UNA EMERGENCIA RECIEN CREADA.

class EmergencyRead(BaseModel):

    model_config = ConfigDict(from_attributes=True)

    id: int
    type: EmergencyType
    type_detail: str | None
    description: str
    location_description: str
    status: EmergencyStatus
    reported_by: str
    created_at: datetime
    updated_at: datetime


