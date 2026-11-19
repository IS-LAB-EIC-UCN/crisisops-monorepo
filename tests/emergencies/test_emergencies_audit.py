"""HU-03: trazabilidad de la emergencia (quién, cuándo y qué cambió).

La auditoría solo se agrega y se confirma en la misma transacción que el cambio.
"""

from datetime import datetime

from sqlalchemy import func, select

from crisisops.modules.emergencies.enums import AuditAction, EmergencyStatus, Role
from crisisops.modules.emergencies.models import EmergencyAuditLog

URL = "/api/v1/emergencies"

COMPLETE_REPORT = {
    "type": "FIRE",
    "date_time": "2026-10-20T10:00:00Z",
    "reported_by": "operator1",
    "title": "Incendio forestal en cerro",
    "description": "Incendio forestal cercano a viviendas, con avance rapido por el viento. " * 3,
    "location_description": "Zona A, La Serena",
    "severity": "HIGH",
}
MINIMAL_REPORT = {"type": "FIRE", "date_time": "2026-10-20T10:00:00Z", "reported_by": "operator1"}


def _create(client, payload=None) -> int:
    response = client.post(URL, json=payload or COMPLETE_REPORT)
    assert response.status_code == 201, response.text
    return response.json()["id"]


def _logs(db_session, emergency_id: int) -> list[EmergencyAuditLog]:
    db_session.expire_all()
    statement = (
        select(EmergencyAuditLog)
        .where(EmergencyAuditLog.emergency_id == emergency_id)
        .order_by(EmergencyAuditLog.id)
    )
    return list(db_session.scalars(statement))


def test_creation_is_audited_with_actor_and_role(client, db_session):
    emergency_id = _create(client)

    (log,) = _logs(db_session, emergency_id)

    assert log.action == AuditAction.CREATED
    assert log.actor == "coordinador1"
    assert log.actor_role == Role.COORDINATOR
    assert log.previous_status is None
    assert log.new_status == EmergencyStatus.REPORTED
    assert log.occurred_at is not None


def test_update_records_before_and_after_of_changed_fields(client, db_session):
    emergency_id = _create(client)

    response = client.patch(f"{URL}/{emergency_id}", json={"title": "Incendio actualizado"})
    assert response.status_code == 200, response.text

    update_log = _logs(db_session, emergency_id)[-1]
    assert update_log.action == AuditAction.UPDATED
    assert update_log.changes == {
        "title": {"before": "Incendio forestal en cerro", "after": "Incendio actualizado"}
    }


def test_update_records_every_changed_field_including_a_first_severity(client, db_session):
    emergency_id = _create(client, MINIMAL_REPORT)

    client.patch(
        f"{URL}/{emergency_id}",
        json={"title": "Inundación en el sector sur", "severity": "CRITICAL"},
    )

    changes = _logs(db_session, emergency_id)[-1].changes
    assert changes["severity"] == {"before": None, "after": "CRITICAL"}
    assert changes["title"] == {"before": None, "after": "Inundación en el sector sur"}


def test_update_that_changes_nothing_is_not_audited(client, db_session):
    emergency_id = _create(client)

    client.patch(f"{URL}/{emergency_id}", json={"title": COMPLETE_REPORT["title"]})

    assert [log.action for log in _logs(db_session, emergency_id)] == [AuditAction.CREATED]


def test_validation_is_audited_with_status_transition(client, db_session):
    emergency_id = _create(client)

    response = client.post(f"{URL}/{emergency_id}/validate", json={"approved": True})
    assert response.status_code == 200, response.text

    log = _logs(db_session, emergency_id)[-1]
    assert log.action == AuditAction.VALIDATED
    assert (log.previous_status, log.new_status) == (
        EmergencyStatus.REPORTED,
        EmergencyStatus.VALIDATED,
    )


def test_rejection_is_audited_with_its_reason(client, db_session):
    emergency_id = _create(client)

    response = client.post(
        f"{URL}/{emergency_id}/validate", json={"approved": False, "reason": "Reporte duplicado"}
    )
    assert response.status_code == 200, response.text

    log = _logs(db_session, emergency_id)[-1]
    assert log.action == AuditAction.REJECTED
    assert log.reason == "Reporte duplicado"
    assert log.new_status == EmergencyStatus.REJECTED


def test_failed_validation_leaves_no_audit_entry(client, db_session):
    emergency_id = _create(client, MINIMAL_REPORT)

    response = client.post(f"{URL}/{emergency_id}/validate", json={"approved": True})
    assert response.status_code == 422

    assert [log.action for log in _logs(db_session, emergency_id)] == [AuditAction.CREATED]


def test_read_only_endpoint_does_not_write_audit(client, db_session):
    emergency_id = _create(client)

    client.get(f"{URL}/{emergency_id}/fields")

    assert db_session.scalar(select(func.count()).select_from(EmergencyAuditLog)) == 1


def test_audit_endpoint_answers_who_when_and_what_changed(client, anonymous_client, headers_for):
    emergency_id = _create(client)
    anonymous_client.patch(
        f"{URL}/{emergency_id}",
        json={"title": "Incendio forestal en el cerro norte"},
        headers=headers_for("OPERATOR", "maria.perez"),
    )

    response = client.get(f"{URL}/{emergency_id}/audit")

    assert response.status_code == 200, response.text
    created, updated = response.json()
    assert (created["actor"], created["actor_role"]) == ("coordinador1", "COORDINATOR")
    assert updated["action"] == "UPDATED"
    assert updated["actor"] == "maria.perez"  # quién
    assert updated["actor_role"] == "OPERATOR"  # con qué rol
    assert datetime.fromisoformat(updated["occurred_at"])  # cuándo
    assert updated["changes"]["title"]["after"] == "Incendio forestal en el cerro norte"  # qué


def test_audit_endpoint_returns_chronological_trail(client):
    emergency_id = _create(client)
    client.patch(f"{URL}/{emergency_id}", json={"title": "Incendio forestal en el cerro norte"})
    client.post(f"{URL}/{emergency_id}/validate", json={"approved": True})

    response = client.get(f"{URL}/{emergency_id}/audit")

    assert response.status_code == 200, response.text
    assert [entry["action"] for entry in response.json()] == ["CREATED", "UPDATED", "VALIDATED"]


def test_audit_of_unknown_emergency_returns_404(client):
    assert client.get(f"{URL}/9999/audit").status_code == 404