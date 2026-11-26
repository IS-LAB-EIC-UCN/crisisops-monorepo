"""Consultas simuladas de B y C para desarrollar HU-03 sin reservar elementos."""

from datetime import datetime


class SimulatedResourceAvailability:
    def __init__(self, available_by_type: dict[str, int]) -> None:
        self.available_by_type = available_by_type.copy()
        self.available = True

    def find_available(
        self, resource_type: str, start_time: datetime, end_time: datetime
    ) -> int:
        """Devuelve la cantidad configurada, sin modificar reservas ni inventario."""
        if not self.available:
            raise ConnectionError("Grupo B no disponible")
        return self.available_by_type.get(resource_type, 0)


class SimulatedPersonnelAvailability:
    def __init__(self, eligible_by_profile: dict[str, int]) -> None:
        self.eligible_by_profile = eligible_by_profile.copy()
        self.available = True

    def find_eligible(self, profile: str, start_time: datetime, end_time: datetime) -> int:
        """Devuelve la cantidad configurada, sin crear asignaciones de personal."""
        if not self.available:
            raise ConnectionError("Grupo C no disponible")
        return self.eligible_by_profile.get(profile, 0)
