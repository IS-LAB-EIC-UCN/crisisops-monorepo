"""
Los roles llegan en la cabecera X-Actor-Role y NO están verificados: esta regla modela el
flujo de trabajo del equipo, no es seguridad (la seguridad real vendrá con el login común).
"""

import pytest
from sqlalchemy import func, select

from crisisops.modules.emergencies.actor import CurrentUser
from crisisops.modules.emergencies.enums import EmergencyStatus, Role
from crisisops.modules.emergencies.exceptions import UnauthorizedAction
from crisisops.modules.emergencies.models import Emergency, EmergencyAuditLog
from crisisops.modules.emergencies.schemas import EmergencyCreate, ValidationDecision
from crisisops.modules.emergencies.service import EmergenciesService

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


def _count(db_session, model) -> int:
    return db_session.scalar(select(func.count()).select_from(model))


def test_operator_can_register_and_edit(anonymous_client, headers_for):
    operator = headers_for("OPERATOR")

    created = anonymous_client.post(URL, json=MINIMAL_REPORT, headers=operator)
    assert created.status_code == 201, created.text

    edited = anonymous_client.patch(
        f"{URL}/{created.json()['id']}", json={"severity": "LOW"}, headers=operator
    )
    assert edited.status_code == 200, edited.text


def test_operator_cannot_validate(anonymous_client, db_session, headers_for):
    emergency_id = anonymous_client.post(
        URL, json=COMPLETE_REPORT, headers=headers_for("OPERATOR")
    ).json()["id"]

    response = anonymous_client.post(
        f"{URL}/{emergency_id}/validate", json={"approved": True}, headers=headers_for("OPERATOR")
    )

    assert response.status_code == 403
    body = response.json()
    assert body["error"] == "unauthorized_action"
    assert "OPERATOR" in body["message"]
    db_session.expire_all()
    assert db_session.get(Emergency, emergency_id).status == EmergencyStatus.REPORTED


def test_coordinator_can_register_edit_and_validate(anonymous_client, headers_for):
    coordinator = headers_for("COORDINATOR")

    created = anonymous_client.post(URL, json=COMPLETE_REPORT, headers=coordinator)
    assert created.status_code == 201, created.text
    emergency_id = created.json()["id"]

    assert anonymous_client.patch(
        f"{URL}/{emergency_id}", json={"severity": "CRITICAL"}, headers=coordinator
    ).status_code == 200
    validated = anonymous_client.post(
        f"{URL}/{emergency_id}/validate", json={"approved": True}, headers=coordinator
    )
    assert validated.status_code == 200, validated.text
    assert validated.json()["status"] == "VALIDATED"


def test_supervisor_cannot_register_edit_or_validate(anonymous_client, db_session, headers_for):
    emergency_id = anonymous_client.post(
        URL, json=COMPLETE_REPORT, headers=headers_for("OPERATOR")
    ).json()["id"]
    supervisor = headers_for("SUPERVISOR")

    register = anonymous_client.post(URL, json=MINIMAL_REPORT, headers=supervisor)
    edit = anonymous_client.patch(
        f"{URL}/{emergency_id}", json={"severity": "LOW"}, headers=supervisor
    )
    validate = anonymous_client.post(
        f"{URL}/{emergency_id}/validate", json={"approved": True}, headers=supervisor
    )

    assert (register.status_code, edit.status_code, validate.status_code) == (403, 403, 403)
    assert _count(db_session, Emergency) == 1  # el rechazo no creó nada


def test_supervisor_can_read_completeness_and_audit(anonymous_client, headers_for):
    emergency_id = anonymous_client.post(
        URL, json=COMPLETE_REPORT, headers=headers_for("OPERATOR")
    ).json()["id"]
    supervisor = headers_for("SUPERVISOR")

    fields = anonymous_client.get(f"{URL}/{emergency_id}/fields", headers=supervisor)
    audit = anonymous_client.get(f"{URL}/{emergency_id}/audit", headers=supervisor)

    assert (fields.status_code, audit.status_code) == (200, 200)


def test_forbidden_action_leaves_no_audit_entry(anonymous_client, db_session, headers_for):
    anonymous_client.post(URL, json=MINIMAL_REPORT, headers=headers_for("SUPERVISOR"))

    assert _count(db_session, EmergencyAuditLog) == 0


def test_role_rule_lives_in_the_service_not_only_in_the_endpoint(db_session):
    # Cualquier otro módulo que llame al servicio también queda sujeto a la regla.
    service = EmergenciesService(db_session)
    operator = CurrentUser("operador1", Role.OPERATOR)
    emergency = service.create_emergency(EmergencyCreate.model_validate(COMPLETE_REPORT), operator)

    with pytest.raises(UnauthorizedAction):
        service.validate_emergency(emergency.id, ValidationDecision(approved=True), operator)

    assert db_session.get(Emergency, emergency.id).status == EmergencyStatus.REPORTED