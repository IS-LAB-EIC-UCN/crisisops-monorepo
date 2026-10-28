import pytest

from crisisops.core.exceptions import DomainError
from crisisops.modules.operations import service as operations_service_module
from crisisops.modules.operations.models import Operation
from crisisops.modules.operations.service import (
    EmergencyNotActive,
    EmergencyNotFound,
    EmergencyUnavailable,
    OperationsService,
)


def test_active_emergency_allows_continuation() -> None:
    consulted_ids = []

    def get_status(emergency_id: int) -> str:
        consulted_ids.append(emergency_id)
        return "ACTIVE"

    OperationsService(get_status, repository=None).validate_emergency(42)

    assert consulted_ids == [42]


@pytest.mark.parametrize(
    ("status", "expected_error", "http_status"),
    [
        (None, EmergencyNotFound, 404),
        ("CLOSED", EmergencyNotActive, 409),
        ("REPORTED", EmergencyNotActive, 409),
        ("REJECTED", EmergencyNotActive, 409),
    ],
)
def test_invalid_emergency_raises_domain_error(
    status: str | None, expected_error: type[DomainError], http_status: int
) -> None:
    def get_status(_emergency_id: int) -> str | None:
        return status

    with pytest.raises(expected_error) as caught:
        OperationsService(get_status, repository=None).validate_emergency(42)

    assert caught.value.status_code == http_status


@pytest.mark.parametrize("failure", [ConnectionError, TimeoutError])
def test_unavailable_emergency_service_raises_503(failure: type[Exception]) -> None:
    def get_status(_emergency_id: int) -> str:
        raise failure("Grupo A no disponible")

    with pytest.raises(EmergencyUnavailable) as caught:
        OperationsService(get_status, repository=None).validate_emergency(42)

    assert caught.value.status_code == 503
    assert isinstance(caught.value.__cause__, failure)


def test_create_operation_with_valid_emergency_returns_201(
    client,
    db_session,
    monkeypatch,
) -> None:
    def fake_get_status(_emergency_id: int) -> str:
        return "ACTIVE"

    monkeypatch.setattr(
        operations_service_module,
        "get_emergency_status_from_group_a",
        fake_get_status,
    )

    response = client.post(
        "/api/v1/operations",
        json={"emergency_id": 1, "name": "Evacuación del edificio", "priority": "HIGH"},
    )

    assert response.status_code == 201
    data = response.json()
    assert data["emergency_id"] == 1
    assert data["name"] == "Evacuación del edificio"
    assert data["priority"] == "HIGH"
    assert db_session.query(Operation).count() == 1


def test_create_operation_with_missing_emergency_returns_404(
    client,
    db_session,
    monkeypatch,
) -> None:
    def fake_get_status(_emergency_id: int) -> str | None:
        return None

    monkeypatch.setattr(
        operations_service_module,
        "get_emergency_status_from_group_a",
        fake_get_status,
    )

    response = client.post(
        "/api/v1/operations",
        json={"emergency_id": 999, "name": "Operación sin emergencia", "priority": "MEDIUM"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "La emergencia 999 no existe."
    assert db_session.query(Operation).count() == 0


def test_create_operation_with_closed_emergency_returns_409(
    client,
    db_session,
    monkeypatch,
) -> None:
    def fake_get_status(_emergency_id: int) -> str:
        return "CLOSED"

    monkeypatch.setattr(
        operations_service_module,
        "get_emergency_status_from_group_a",
        fake_get_status,
    )

    response = client.post(
        "/api/v1/operations",
        json={"emergency_id": 2, "name": "Operación cerrada", "priority": "LOW"},
    )

    assert response.status_code == 409
    assert response.json()["detail"] == "La emergencia 2 no está activa (estado: CLOSED)."
    assert db_session.query(Operation).count() == 0
