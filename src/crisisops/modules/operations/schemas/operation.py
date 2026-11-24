"""Esquemas Pydantic públicos del módulo.

Los contratos consumidos por otros módulos deben mantenerse pequeños,
explícitos y versionables.
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

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
