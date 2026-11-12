"""Formato de las respuestas de error del módulo de emergencias."""

URL = "/api/v1/emergencies"


def test_validate_incomplete_report_lists_missing_fields(client):

    payload = {
        "type": "FIRE",
        "date_time": "2026-10-20T10:00:00Z",
        "reported_by": "operator1",
    }

    created = client.post(URL, json=payload)
    
    emergency_id = created.json()["id"]

    response = client.post(
        f"{URL}/{emergency_id}/validate",
        params={"actor_role": "OPERATOR"},
        json={"approved": True},
    )

    body = response.json()
    assert response.status_code == 422
    assert body["error"] == "emergency_validation_error"
    assert "title" in body["errors"]
    assert "description" in body["errors"]


def test_unknown_emergency_returns_404_with_error_code(client):
    response = client.get(f"{URL}/9999/fields")

    assert response.status_code == 404
    assert response.json()["error"] == "emergency_not_found"

def test_registration_requires_date_time(client):
    response = client.post(URL, json={"type": "FIRE", "reported_by": "operator1"})

    assert response.status_code == 422