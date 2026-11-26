"""Contratos de consulta de disponibilidad para el módulo operations (HU-03)."""

from datetime import datetime
from typing import Protocol


class ResourceAvailabilityGateway(Protocol):
    def find_available(
        self, resource_type: str, start_time: datetime, end_time: datetime
    ) -> int:
        """Cantidad de recursos disponibles del tipo solicitado en el intervalo."""
        ...


class PersonnelAvailabilityGateway(Protocol):
    def find_eligible(self, profile: str, start_time: datetime, end_time: datetime) -> int:
        """Cantidad de personas elegibles para el perfil y el intervalo."""
        ...
