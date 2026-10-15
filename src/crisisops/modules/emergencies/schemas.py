"""Esquemas Pydantic públicos del módulo.

Los contratos consumidos por otros módulos deben mantenerse pequeños,
explícitos y versionables.
"""
from pydantic import BaseModel, ConfigDict, Field
from crisisops.modules.emergencies.enums import EmergencyType, EmergencyStatus

from crisisops.shared.enums import Severity
from datetime import UTC, datetime

class ValidationDecision(BaseModel):
    approved: bool
    reason: str | None = Field(
        default=None, description="Obligatorio cuanndo approved =false porque indica el movito del rechazo"
    )

#PODEMOS TENER OTRA CLASE BASEMODEL, QUE SEA PARA CUANDO SE CREA UNA EMERGENCIA PARA IDENTIFICAR LOS TIPOS VALIDOS DE CAMPOS
#PARA UNA EMERGENCIA RECIEN CREADA.


class EmergencyCreate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    type: EmergencyType

    type_detail: str | None = Field(
        default=None
    )
    title: str

    severity: Severity | None = Field(
        default=None
    )

    description: str | None

    location_description: str | None

    reported_by: str




class EmergencyRead(BaseModel):

    model_config = ConfigDict(from_attributes=True) #Pydantic solo sabe estrcuturar datos cuando se les pasa un diccionario, los ORM guardan datos como atributos
    

    id: int
    type: EmergencyType
    title : str|None
    type_detail: str | None
    description: str | None
    severity: Severity
    location_description: str | None
    status: EmergencyStatus
    reported_by: str
    created_at: datetime
    updated_at: datetime


    


