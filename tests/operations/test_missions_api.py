import pytest
from sqlalchemy.orm import Session

from crisisops.modules.operations.models import (
    Mission,
    MissionPersonnelRequirement,
    MissionResourceRequirement,
)

URL_OPERATIONS = "/api/v1/operations"


@pytest.fixture()
def existing_operation(api_client) -> dict:
    """Crea una operación base sobre una emergencia activa."""
    response = api_client.post(
        URL_OPERATIONS,
        json={
            "emergency_id": 1,
            "name": "Operación de prueba",
            "priority": "HIGH",
        },
    )
    assert response.status_code == 201
    return response.json()


def create_mission(api_client, operation_id: int) -> dict:
    """Crea una misión y comprueba la respuesta antes de devolverla."""
    response = api_client.post(
        f"{URL_OPERATIONS}/{operation_id}/missions",
        json={"name": "Misión de prueba", "priority": "HIGH"},
    )
    assert response.status_code == 201
    return response.json()


def test_create_mission_returns_201_and_planned(
    api_client,
    existing_operation,
    db_session: Session,
) -> None:
    mission = create_mission(api_client, existing_operation["id"])

    assert mission["operation_id"] == existing_operation["id"]
    assert mission["status"] == "PLANNED"
    assert mission["resource_requirements"] == []
    assert mission["personnel_requirements"] == []
    assert db_session.query(Mission).count() == 1


def test_create_mission_for_missing_operation_returns_404_without_saving(
    api_client,
    db_session: Session,
) -> None:
    response = api_client.post(
        f"{URL_OPERATIONS}/99999/missions",
        json={"name": "Misión sin operación", "priority": "LOW"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "La operación 99999 no existe."
    assert db_session.query(Mission).count() == 0


@pytest.mark.parametrize(
    ("payload", "expected_field"),
    [
        (
            {"type": "RESOURCE", "resource_type": "VEHICULO", "quantity": 2},
            "resource_type",
        ),
        (
            {"type": "PERSONNEL", "profile": "PARAMEDIC", "quantity": 3},
            "profile",
        ),
    ],
)
def test_add_valid_requirement_returns_201(
    api_client,
    existing_operation,
    payload: dict,
    expected_field: str,
) -> None:
    mission = create_mission(api_client, existing_operation["id"])

    response = api_client.post(
        f"{URL_OPERATIONS}/missions/{mission['id']}/requirements",
        json=payload,
    )

    assert response.status_code == 201
    requirement = response.json()
    assert requirement["mission_id"] == mission["id"]
    assert requirement[expected_field] == payload[expected_field]
    assert requirement["quantity"] == payload["quantity"]


@pytest.mark.parametrize(
    ("payload", "expected_detail"),
    [
        (
            {"type": "RESOURCE", "resource_type": "SUBMARINO", "quantity": 1},
            "no existe en el catálogo de Grupo B",
        ),
        (
            {"type": "PERSONNEL", "profile": "ASTRONAUTA", "quantity": 1},
            "no existe en el catálogo de Grupo C",
        ),
    ],
)
def test_add_unknown_catalog_value_returns_422_without_saving(
    api_client,
    existing_operation,
    db_session: Session,
    payload: dict,
    expected_detail: str,
) -> None:
    mission = create_mission(api_client, existing_operation["id"])

    response = api_client.post(
        f"{URL_OPERATIONS}/missions/{mission['id']}/requirements",
        json=payload,
    )

    assert response.status_code == 422
    assert expected_detail in response.json()["detail"]
    assert db_session.query(MissionResourceRequirement).count() == 0
    assert db_session.query(MissionPersonnelRequirement).count() == 0


@pytest.mark.parametrize(
    ("requirement_type", "field", "catalog_code"),
    [
        ("RESOURCE", "resource_type", "IMPLEMENTO"),
        ("PERSONNEL", "profile", "FIREFIGHTER"),
    ],
)
@pytest.mark.parametrize("quantity", [0, -1, -10])
def test_add_requirement_with_invalid_quantity_returns_422_without_saving(
    api_client,
    existing_operation,
    db_session: Session,
    requirement_type: str,
    field: str,
    catalog_code: str,
    quantity: int,
) -> None:
    mission = create_mission(api_client, existing_operation["id"])
    payload = {
        "type": requirement_type,
        field: catalog_code,
        "quantity": quantity,
    }

    response = api_client.post(
        f"{URL_OPERATIONS}/missions/{mission['id']}/requirements",
        json=payload,
    )

    assert response.status_code == 422
    assert db_session.query(MissionResourceRequirement).count() == 0
    assert db_session.query(MissionPersonnelRequirement).count() == 0


def test_get_mission_returns_200_with_resource_and_personnel_requirements(
    api_client,
    existing_operation,
) -> None:
    mission = create_mission(api_client, existing_operation["id"])
    mission_id = mission["id"]

    resource_response = api_client.post(
        f"{URL_OPERATIONS}/missions/{mission_id}/requirements",
        json={
            "type": "RESOURCE",
            "resource_type": "IMPLEMENTO",
            "quantity": 4,
        },
    )
    personnel_response = api_client.post(
        f"{URL_OPERATIONS}/missions/{mission_id}/requirements",
        json={
            "type": "PERSONNEL",
            "profile": "FIREFIGHTER",
            "quantity": 2,
        },
    )

    assert resource_response.status_code == 201
    assert personnel_response.status_code == 201

    response = api_client.get(f"{URL_OPERATIONS}/missions/{mission_id}")

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == mission_id
    assert len(data["resource_requirements"]) == 1
    assert data["resource_requirements"][0]["resource_type"] == "IMPLEMENTO"
    assert data["resource_requirements"][0]["quantity"] == 4
    assert len(data["personnel_requirements"]) == 1
    assert data["personnel_requirements"][0]["profile"] == "FIREFIGHTER"
    assert data["personnel_requirements"][0]["quantity"] == 2


def test_get_missing_mission_returns_404(api_client) -> None:
    response = api_client.get(f"{URL_OPERATIONS}/missions/99999")

    assert response.status_code == 404
    assert response.json()["detail"] == "La misión 99999 no existe."


def test_add_resource_requirement_when_group_b_is_down_returns_503_without_saving(
    api_client,
    existing_operation,
    resource_catalog,
    db_session: Session,
) -> None:
    mission = create_mission(api_client, existing_operation["id"])
    resource_catalog.available = False

    response = api_client.post(
        f"{URL_OPERATIONS}/missions/{mission['id']}/requirements",
        json={"type": "RESOURCE", "resource_type": "VEHICULO", "quantity": 1},
    )

    assert response.status_code == 503
    assert db_session.query(MissionResourceRequirement).count() == 0


def test_add_personnel_requirement_when_group_c_is_down_returns_503_without_saving(
    api_client,
    existing_operation,
    personnel_catalog,
    db_session: Session,
) -> None:
    mission = create_mission(api_client, existing_operation["id"])
    personnel_catalog.available = False

    response = api_client.post(
        f"{URL_OPERATIONS}/missions/{mission['id']}/requirements",
        json={"type": "PERSONNEL", "profile": "PARAMEDIC", "quantity": 1},
    )

    assert response.status_code == 503
    assert db_session.query(MissionPersonnelRequirement).count() == 0
