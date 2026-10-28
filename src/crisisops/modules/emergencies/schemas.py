"""Esquemas Pydantic públicos del módulo.

Los contratos consumidos por otros módulos deben mantenerse pequeños,
explícitos y versionables.
"""
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from crisisops.modules.emergencies.enums import EmergencyStatus, EmergencyType
from crisisops.shared.enums import Severity


class ValidationDecision(BaseModel):

    approved: bool
    reason: str|None = Field(default=None, description=
    "Obligatorio cuando approved=False porque indica el motivo del rechazo")


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




class EmergencyUpdate(BaseModel):
    type: EmergencyType | None = None

    type_detail: str | None = Field(
        default=None,
        max_length=150
    )

    title: str | None = Field(
        default=None,
        min_length=5,
        max_length=150
    )

    description: str | None = Field(
        default=None,
        min_length=10
    )

    severity: Severity | None = None

    location_description: str | None = Field(
        default=None,
        min_length=3,
        max_length=250
    )

class EmergencyRead(BaseModel):

    model_config = ConfigDict(from_attributes=True) #Pydantic solo sabe estrcuturar datos cuando se
    # les pasa un diccionario, los ORM guardan datos como atributos

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

'''La clase EmergencyValidate la utilizamos para validar que la Emergencia consultada 
   tenga los datos necesarios para pasar a su validación. 
   La función que obtiene los errores en el caso que 
   la emergencia requiera datos es schemas_validate_emergency(emergency: Emergency) -> None:
   presente en el archivo validators.py
'''
class EmergencyValidate(BaseModel):

    model_config = ConfigDict(from_attributes=True)

    type: EmergencyType
    title: str = Field(min_length=15)
    type_detail: str | None
    description: str = Field(min_length=100)
    severity: Severity
    location_description: str=Field(min_length=5)
    status: EmergencyStatus
    reported_by: str
    created_at: datetime
    
