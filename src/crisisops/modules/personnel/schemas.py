from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class AssignmentCreate(BaseModel):
    mission_id: int | None = None
    start_at: datetime
    end_at: datetime

class AssignmentResponse(BaseModel):
    id: int
    responder_id: int
    mission_id: int | None
    start_at: datetime
    end_at: datetime
    status: str

    model_config = ConfigDict(from_attributes=True)

class EligibilityQuery(BaseModel):
    start_time: datetime
    end_time: datetime
    required_skills: list[str] = Field(default_factory=list)

class ResponderOut(BaseModel):
    id: int
    name: str
    badge_number: str
    role: str
    is_active: bool
    model_config = ConfigDict(from_attributes=True)


class BrigadeValidationRequest(BaseModel):
    """Solicitud para comprobar la cobertura de competencias de una brigada (H03 - T3.1)."""
    responder_ids: list[int] = Field(
        ...,
        min_length=1,
        description="Lista de identificadores de brigadistas que conforman la brigada",
    )
    required_skills: list[str] = Field(
        ...,
        min_length=1,
        description="Lista de competencias/habilidades requeridas para la misión",
    )


class BrigadeValidationResponse(BaseModel):
    """Resultado de la validación de cobertura de brigada para los criterios de H03."""
    is_valid: bool = Field(
        ...,
        description="True si la brigada cubre todas las competencias; False en caso contrario",
    )
    missing_skills: list[str] = Field(
        default_factory=list,
        description="Lista de competencias faltantes (vacía si la cobertura es completa)",
    )
