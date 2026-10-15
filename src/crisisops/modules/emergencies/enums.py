from enum import StrEnum

class EmergencyType(StrEnum):
    FIRE = "FIRE"
    FLODD = "FLOODD"
    EARTHQUAKE = "EARTHQUAKE"
    LANDSLIDE = "LANDSLIDE"
    MAJOR_ACCIDENT = "MAJOR_ACCIDENT"
    HAZMAT = "HAZMAT"
    OTHER = "OTHER"

class EmergencyStatus(StrEnum):
    REPORTED = "REPORTED"
    VALIDATED = "VALIDATED"
    REJECTED = "REJECTED"
    ACTIVE = "ACTIVE"
    CONTROLLED = "CONTROLLED"
    CLOSED = "CLOSED"
    CANCELLED = "CANCELLED"

class Role(StrEnum):
    #Por ahora solo operador porque  debemos definir que otros 
    #roles puede tener el sistema

    OPERATOR = "OPERATOR"

class Severity(StrEnum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"