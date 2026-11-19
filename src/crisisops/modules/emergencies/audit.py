"""
Registro de auditoría de la emergencia.
record_audit_event, NO hace commit: la entrada queda 
en la sesión y se confirma ( o se deshace) junto con
el cambio que la originó, dentor de _transactional.
"""
from datetime import datetime
from enum import StrEnum
from typing import Any

from sqlalchemy.orm import Session

from crisisops.modules.emergencies.enums import AuditAction, EmergencyStatus, Role
from crisisops.modules.emergencies.models import EmergencyAuditLog


def _plain(value: Any) -> Any:
    """Convierte enums y fechas a tipos que Json puede guardar."""
    if isinstance(value,datetime):
        return value.isoformat()
    if isinstance(value, StrEnum):
        return value.value
    return value

def record_audit_event(
    db: Session,
    *,
    emergency_id: int,
    action: AuditAction,
    actor: str,
    actor_role: Role,
    previous_status: EmergencyStatus | None = None,
    new_status: EmergencyStatus | None = None,
    reason: str | None = None,
    changes: dict[str, tuple[Any, Any]] | None = None,
) -> EmergencyAuditLog:
    """'changes' mapea campo -> (valor_anterior, valor_nuevo)."""
    entry = EmergencyAuditLog(
        emergency_id=emergency_id,
        action=action,
        actor=actor,
        actor_role=actor_role,
        previous_status=previous_status,
        new_status=new_status,
        reason=reason,
        changes=(
            {
                field: {"before": _plain(before), "after": _plain(after)}
                for field, (before, after) in changes.items()
            }
            if changes
            else None
        ),
        
    )
    db.add(entry)
    return entry

    