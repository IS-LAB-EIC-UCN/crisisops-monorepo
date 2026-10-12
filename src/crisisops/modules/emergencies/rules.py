from dataclasses import dataclass
from crisisops.modules.emergencies.enums import EmergencyType
from crisisops.modules.emergencies.models import Emergency
#Estos son los campos necesarios para la validación, se puede agregar mas
#Se dejaron description y location_description por ahora.
MIN_LENGTH_BY_FIELD = {"description": 50, "location_description":10}

#Se usa dataclasses para que sea mas ordenado y frozen=True para que el objeto
#sea solo de lectura, no se pueda modificar despues.
@dataclass(frozen=True)
class FieldIssue:
    field: str
    #code, ayuda para cuando el que llame la función sepa el porque habia problemas
    #con el campo X, o por que esa faltante o porque no cumplia el minimo de largo
    #Por ahora puede tomar 3 valores falante, demasiado_corto o requerido_cuando_OTHER
    code: str
    message: str

def find_field_issues(emergency: Emergency) -> list[FieldIssue]:
    """Devuelve Todos los campos que faltan o son inválidos para poder evaluar
    el reporte"""

    issues: list[FieldIssue] = []

    for name, min_length in MIN_LENGTH_BY_FIELD.items():
        value = getattr(emergency, name, None)
        #si es faltante
        if value is None or not value.strip():
            issues.append(FieldIssue(name, "faltante",  "es obligatorio"))
        #si no cumple el largo minimo
        elif len(value.strip()) < min_length:
            issues.append(FieldIssue(name, "demasiado_corto", f"debe tener al menos {min_length} caracteres"))
    #Acá es para el caso que  el tipo sea "OTHER" pero no tenga type_detail, lo que es necesario
    #para la validación
    if emergency.type == EmergencyType.OTHER and not (Emergency.type_detail or "").strip():
        issues.append(FieldIssue("type_detail", "requerido_cuando_other", "es obligatorio si type=OTHER"))

    return issues


