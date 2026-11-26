"""Verifica el contrato de respuesta de disponibilidad antes de crear el endpoint."""

import pytest
from pydantic import ValidationError

from crisisops.modules.operations.schemas.availability import MissionAvailabilityResponse


def test_availability_response_distinguishes_resource_and_personnel_requirements() -> None:
    response = MissionAvailabilityResponse.model_validate(
        {
            "mission_id": 7,
            "ready_to_reserve": False,
            "requirements": [
                {
                    "type": "RESOURCE",
                    "requirement_id": 11,
                    "resource_type": "VEHICULO",
                    "required_quantity": 2,
                    "available_quantity": 1,
                    "is_available": False,
                },
                {
                    "type": "PERSONNEL",
                    "requirement_id": 12,
                    "profile": "PARAMEDIC",
                    "required_quantity": 1,
                    "available_quantity": 1,
                    "is_available": True,
                },
            ],
        }
    )

    data = response.model_dump(mode="json")
    assert data["requirements"][0]["resource_type"] == "VEHICULO"
    assert data["requirements"][1]["profile"] == "PARAMEDIC"
    assert data["ready_to_reserve"] is False


def test_availability_response_explains_a_mission_without_requirements() -> None:
    response = MissionAvailabilityResponse(
        mission_id=7,
        ready_to_reserve=False,
        reason="La misión no tiene requisitos.",
    )

    assert response.requirements == []
    assert response.reason == "La misión no tiene requisitos."


def test_availability_response_rejects_negative_available_quantity() -> None:
    with pytest.raises(ValidationError):
        MissionAvailabilityResponse.model_validate(
            {
                "mission_id": 7,
                "ready_to_reserve": False,
                "requirements": [
                    {
                        "type": "RESOURCE",
                        "requirement_id": 11,
                        "resource_type": "VEHICULO",
                        "required_quantity": 1,
                        "available_quantity": -1,
                        "is_available": False,
                    }
                ],
            }
        )
