import pytest

from crisisops.core.exceptions import DomainError
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
        (None, EmergencyNotFound, 422),
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
