"""HU-02: consultar el estado y el nivel de severidad de una emergencia."""

URL = "/api/v1/emergencies"

REPORT_WITH_SEVERITY = {
    "type": "FIRE",
    "date_time": "2026-10-20T10:00:00Z",
    "reported_by": "operator1",
    "title": "Incendio forestal en cerro",
    "description": ("Incendio forestal cercano a "
                    "viviendas, con avance rapido "
                    "por el viento. El fuego avanza "
                    "rápidamente debido a fuertes "
                    "vientos y representa un riesgo "
                    "para la población y las estructuras "
                    "cercanas."
                    ),
    "location_description": "Zona A, La Serena",
    "severity": "HIGH",
}

MINIMAL_REPORT = {"type": "FLOOD", 
                  "date_time": "2026-10-20T10:00:00Z",
                  "reported_by": "operator1",
                  }

def _create(client, payload) -> int:
    response = client.post(URL, json= payload)
    assert response.status_code == 201, response.text
    return response.json()["id"]

def test_query_returns_status_and_severity(client):
    emergency_id = _create(client, REPORT_WITH_SEVERITY)

    response = client.get(f"{URL}/{emergency_id}")

    assert response.status_code == 200, response.text
    body = response.json()
    assert body["id"] == emergency_id
    assert body["status"] == "REPORTED"
    assert body["severity"] == "HIGH"
    assert body["updated_at"] is not None

def test_query_without_assigned_severity_returns_null(client):
    emergency_id = _create(client, MINIMAL_REPORT)

    body = client.get(f"{URL}/{emergency_id}").json()

    assert body["status"] == "REPORTED"
    assert body["severity"] is None

def test_query_reflects_a_severity_update(client):
    emergency_id = _create(client, MINIMAL_REPORT)

    client.patch(f"{URL}/{emergency_id}", json={"severity": "CRITICAL"})

    assert client.get(f"{URL}/{emergency_id}").json()["severity"] == "CRITICAL"

def test_query_reflects_the_new_status_after_validation(client):
    emergency_id = _create(client,REPORT_WITH_SEVERITY)
    validation = client.post(
        f"{URL}/{emergency_id}/validate",
        params={"actor_role": "OPERATOR"},
        json={"approved": True},
    )

    assert validation.status_code == 200, validation.text

    assert client.get(f"{URL}/{emergency_id}").json()["status"] == "VALIDATED"

def test_query_of_unknown_emergency_returns_404(client):
    response = client.get(f"{URL}/9999")

    assert response.status_code == 404
    assert response.json()["error"] == "emergency_not_found"

def test_query_with_non_numeric_id_is_rejected(client):
    assert client.get(f"{URL}/abc").status_code == 422

def test_module_health_is_not_shadowed_by_the_id_route(client):
    assert client.get(f"{URL}/health").status_code == 200