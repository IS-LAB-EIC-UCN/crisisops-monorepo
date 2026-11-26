"""Comprueba los contratos simulados de consulta de disponibilidad."""

from datetime import UTC, datetime, timedelta

import pytest

from crisisops.modules.operations.gateways import (
    PersonnelAvailabilityGateway,
    ResourceAvailabilityGateway,
)
from crisisops.modules.operations.simulated import (
    SimulatedPersonnelAvailability,
    SimulatedResourceAvailability,
)

START = datetime(2026, 11, 27, 10, tzinfo=UTC)
END = START + timedelta(hours=2)


def test_simulated_gateways_return_counts_without_changing_their_data() -> None:
    resources: ResourceAvailabilityGateway = SimulatedResourceAvailability({"VEHICULO": 2})
    personnel: PersonnelAvailabilityGateway = SimulatedPersonnelAvailability({"PARAMEDIC": 1})

    assert resources.find_available("VEHICULO", START, END) == 2
    assert resources.find_available("IMPLEMENTO", START, END) == 0
    assert personnel.find_eligible("PARAMEDIC", START, END) == 1
    assert personnel.find_eligible("DRIVER", START, END) == 0
    assert resources.find_available("VEHICULO", START, END) == 2
    assert personnel.find_eligible("PARAMEDIC", START, END) == 1


def test_simulated_gateways_can_fail_like_an_unavailable_group() -> None:
    resources = SimulatedResourceAvailability({"VEHICULO": 2})
    personnel = SimulatedPersonnelAvailability({"PARAMEDIC": 1})
    resources.available = False
    personnel.available = False

    with pytest.raises(ConnectionError, match="Grupo B"):
        resources.find_available("VEHICULO", START, END)
    with pytest.raises(ConnectionError, match="Grupo C"):
        personnel.find_eligible("PARAMEDIC", START, END)
