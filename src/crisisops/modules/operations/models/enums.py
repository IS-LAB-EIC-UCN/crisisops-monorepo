from enum import StrEnum

from sqlalchemy import Enum as SAEnum


class MissionStatus(StrEnum):
    """Estados de una misión. Toda misión nace en PLANNED."""

    PLANNED = "PLANNED"
    READY = "READY"
    DISPATCHED = "DISPATCHED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


def enum_column(enum_type: type[StrEnum]) -> SAEnum:
    """Columna de texto que solo acepta los valores del enum."""
    return SAEnum(enum_type, native_enum=False, length=20, validate_strings=True)
