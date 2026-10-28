import pytest

URL = "/api/v1/operations"
PAYLOAD = {"emergency_id": 1, "name": "Evacuación del edificio", "priority": "HIGH"}


def test_create_operation_with_active_emergency_returns_201(api_client, operation_count) -> None:
    response = api_client.post(URL, json=PAYLOAD)

    assert response.status_code == 201
    data = response.json()
    assert data["id"] is not None
    assert data["emergency_id"] == 1
    assert data["name"] == "Evacuación del edificio"
    assert data["priority"] == "HIGH"
    assert data["created_at"] is not None
    assert operation_count() == 1


def test_create_operation_with_missing_emergency_returns_422(api_client, operation_count) -> None:
    response = api_client.post(URL, json={**PAYLOAD, "emergency_id": 999})

    assert response.status_code == 422
    assert response.json()["detail"] == "La emergencia 999 no existe."
    assert operation_count() == 0


@pytest.mark.parametrize(
    ("emergency_id", "status"),
    [(2, "CLOSED"), (3, "REPORTED"), (4, "REJECTED")],
)
def test_create_operation_with_inactive_emergency_returns_409(
    api_client, operation_count, emergency_id: int, status: str
) -> None:
    response = api_client.post(URL, json={**PAYLOAD, "emergency_id": emergency_id})

    assert response.status_code == 409
    assert response.json()["detail"] == (
        f"La emergencia {emergency_id} no está activa (estado: {status})."
    )
    assert operation_count() == 0


def test_create_operation_when_group_a_is_down_returns_503(
    api_client, emergency_service, operation_count
) -> None:
    emergency_service.available = False

    response = api_client.post(URL, json=PAYLOAD)

    assert response.status_code == 503
    assert operation_count() == 0


def test_group_a_not_integrated_yet_returns_503(client, operation_count) -> None:
    response = client.post(URL, json=PAYLOAD)

    assert response.status_code == 503
    assert operation_count() == 0


@pytest.mark.parametrize(
    "change",
    [{"emergency_id": 0}, {"name": "   "}, {"name": "x" * 151}, {"priority": "URGENT"}],
)
def test_create_operation_with_invalid_payload_returns_422(
    api_client, operation_count, change: dict
) -> None:
    response = api_client.post(URL, json={**PAYLOAD, **change})

    assert response.status_code == 422
    assert operation_count() == 0


def test_get_existing_operation_returns_200(api_client) -> None:
    created = api_client.post(URL, json=PAYLOAD).json()

    response = api_client.get(f"{URL}/{created['id']}")

    assert response.status_code == 200
    assert response.json() == created


def test_get_missing_operation_returns_404(api_client) -> None:
    response = api_client.get(f"{URL}/999")

    assert response.status_code == 404
    assert response.json()["detail"] == "La operación 999 no existe."
