from pydantic import BaseModel, Field


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