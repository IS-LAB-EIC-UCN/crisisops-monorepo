import pytest
from sqlalchemy import select

from crisisops.modules.emergencies.enums import EmergencyStatus
from crisisops.modules.emergencies.exceptions import (
EmergencyNotFound,
InvalidStateTransition,
InvalidEmergencyUpdate,
)
from crisisops.modules.emergencies.models import Emergency
from crisisops.modules.emergencies.schemas import (
    EmergencyCreate,
    EmergencyUpdate,
)
from crisisops.modules.emergencies.service import EmergenciesService

URL = "/api/v1/emergencies"

VALID_REPORT = {
"type": "FIRE",
"reported_by": "operator1",
"title": "Incendio de prueba",
"description": "Reporte inicial de una emergencia de prueba.",
"location_description": "Zona A, La Serena",
}

def create_emergency(client) -> int:
    response = client.post(URL, json=VALID_REPORT)
    assert response.status_code == 201, response.text
    return response.json()["id"]

def test_update_reported_emergency(client, db_session):
    emergency_id = create_emergency(client)
    payload = {"title": "Incendio actualizado"}

    response = client.patch(
        f"{URL}/{emergency_id}",
        json=payload,
    )

    assert response.status_code == 200, response.text
    assert response.json()["title"] == payload["title"]

    db_session.expire_all()
    saved = db_session.get(Emergency, emergency_id)

    assert saved is not None
    assert saved.title == payload["title"]

def test_update_only_changes_sent_fields(client):
    emergency_id = create_emergency(client)

    response = client.patch(
        f"{URL}/{emergency_id}",
        json={"title": "Nuevo título"},
    )

    assert response.status_code == 200, response.text
    body = response.json()

    assert body["title"] == "Nuevo título"
    assert body["description"] == VALID_REPORT["description"]
    assert body["location_description"] == (
        VALID_REPORT["location_description"]
    )


def test_empty_update_is_rejected(db_session):
    emergency = EmergenciesService(db_session).create_emergency(
        EmergencyCreate.model_validate(VALID_REPORT)
    )
    service = EmergenciesService(db_session)

    with pytest.raises(InvalidEmergencyUpdate):
        service.update_emergency(
            emergency.id,
            EmergencyUpdate(),
        )


def test_update_nonexistent_emergency(db_session):
    service = EmergenciesService(db_session)

    with pytest.raises(EmergencyNotFound):
        service.update_emergency(
            9999,
            EmergencyUpdate(title="Título actualizado"),
        )

def test_validated_emergency_cannot_be_updated(client, db_session):
        emergency_id = create_emergency(client)
        emergency = db_session.get(Emergency, emergency_id)

        assert emergency is not None
        emergency.status = EmergencyStatus.VALIDATED
        db_session.commit()

        response = client.patch(
            f"{URL}/{emergency_id}",
            json={"title": "No debería cambiar"},
        )

        assert response.status_code == 409, response.text

def test_rejected_emergency_cannot_be_updated(client, db_session):
        emergency_id = create_emergency(client)
        emergency = db_session.get(Emergency, emergency_id)

        assert emergency is not None
        emergency.status = EmergencyStatus.REJECTED
        db_session.commit()

        response = client.patch(
            f"{URL}/{emergency_id}",
            json={"title": "No debería cambiar"},
        )

        assert response.status_code == 409, response.text