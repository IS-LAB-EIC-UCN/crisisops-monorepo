from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, model_validator


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


class AvailableRespondersResponse(BaseModel):
    count: int
    responders: list[ResponderOut]


class BrigadeValidationRequest(BaseModel):
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
    is_valid: bool = Field(
        ...,
        description="True si la brigada cubre todas las competencias; False en caso contrario",
    )
    missing_skills: list[str] = Field(
        default_factory=list,
        description="Lista de competencias faltantes (vacía si la cobertura es completa)",
    )


class SkillAssign(BaseModel):
    skill_code: str = Field(
        ...,
        min_length=1,
        description="Código de la competencia a asignar",
    )


class CertificationCreate(BaseModel):
    skill_code: str = Field(
        ...,
        min_length=1,
        description="Código de la competencia certificada",
    )
    issued_at: datetime = Field(
        ...,
        description="Fecha y hora de emisión",
    )
    expires_at: datetime = Field(
        ...,
        description="Fecha y hora de expiración",
    )

    @model_validator(mode="after")
    def validate_dates(self) -> "CertificationCreate":
        if self.expires_at <= self.issued_at:
            raise ValueError("expires_at debe ser posterior a issued_at")
        return self


class CertificationResponse(BaseModel):
    id: int
    responder_id: int
    skill_code: str
    issued_at: datetime
    expires_at: datetime

    model_config = ConfigDict(from_attributes=True)

