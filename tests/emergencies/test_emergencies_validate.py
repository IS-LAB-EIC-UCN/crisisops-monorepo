"""HU-01: validar un reporte de emergencia (REPORTED -> VALIDATED)."""

import pytest

from crisisops.modules.emergencies.enums import EmergencyStatus
from crisisops.modules.emergencies.exceptions import (
    EmergencyNotFound,
    EmergencyValidationError,
    InvalidStateTransition,
)
from crisisops.modules.emergencies.models import Emergency
from crisisops.modules.emergencies.service import EmergenciesService

URL_CREATION = "/api/v1/emergencies"

COMPLETE_REPORT = {
    "type": "FIRE",
    "reported_by": "operator1",
    "title": "Incendio forestal en cerro",
    "description": "Incendio forestal cercano a viviendas, con avance rapido por el viento. " * 3,
    "location_description": "Zona A, La Serena",
    "severity": "HIGH",
}

INCOMPLETE_REPORT = {"type": "FIRE", "reported_by": "operator1"}


def _register(client, payload) -> int:
    response = client.post(URL_CREATION, json=payload)
    assert response.status_code == 201, response.text
    return response.json()["id"]


def test_complete_report_is_validated(client, db_session):
    emergency_id = _register(client, COMPLETE_REPORT)

    emergency = EmergenciesService(db_session).validate_emergency(emergency_id)

    assert emergency.status == EmergencyStatus.VALIDATED


def test_incomplete_report_is_rejected_and_stays_reported(client, db_session):
    emergency_id = _register(client, INCOMPLETE_REPORT)

    with pytest.raises(EmergencyValidationError):
        EmergenciesService(db_session).validate_emergency(emergency_id)

    assert db_session.get(Emergency, emergency_id).status == EmergencyStatus.REPORTED


def test_already_validated_report_cannot_be_validated_again(client, db_session):
    emergency_id = _register(client, COMPLETE_REPORT)
    service = EmergenciesService(db_session)
    service.validate_emergency(emergency_id)

    with pytest.raises(InvalidStateTransition):
        service.validate_emergency(emergency_id)


def test_unknown_emergency_cannot_be_validated(db_session):
    with pytest.raises(EmergencyNotFound):
        EmergenciesService(db_session).validate_emergency(9999)