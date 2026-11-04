from collections.abc import Callable

from crisisops.core.exceptions import DomainError
from crisisops.modules.operations.models import (
    Mission,
    MissionPersonnelRequirement,
    MissionResourceRequirement,
    MissionStatus,
    Operation,
)
from crisisops.modules.operations.repository import OperationsRepository
from crisisops.modules.operations.schemas import (
    MissionCreate,
    OperationCreate,
    PersonnelRequirementCreate,
    RequirementCreate,
    ResourceRequirementCreate,
)


class EmergencyNotFound(DomainError):
    """La emergencia indicada no existe en Grupo A."""

    status_code = 422


class EmergencyNotActive(DomainError):
    """La emergencia existe, pero su estado no permite crear operaciones."""

    status_code = 409


class EmergencyUnavailable(DomainError):
    """No se pudo consultar a Grupo A (caído o aún no integrado)."""

    status_code = 503


class OperationNotFound(DomainError):
    """No existe una operación con el id consultado."""

    status_code = 404


class MissionNotFound(DomainError):
    """No existe una misión con el id consultado."""

    status_code = 404


class InvalidCatalogItem(DomainError):
    """El tipo de recurso o perfil no existe en el catálogo de Grupo B o C."""

    status_code = 422


class CatalogUnavailable(DomainError):
    """No se pudo consultar el catálogo de Grupo B o C."""

    status_code = 503


def get_emergency_status_from_group_a(emergency_id: int) -> str | None:
    """Consulta el estado en Grupo A. Mientras A no esté integrado en develop, no responde."""
    raise ConnectionError("El módulo de emergencias (Grupo A) aún no está integrado.")


def get_resource_types_from_group_b() -> set[str]:
    """Consulta los tipos de recurso de Grupo B. Mientras B no los exponga, no responde."""
    raise ConnectionError("El catálogo de tipos de recurso (Grupo B) aún no está disponible.")


def get_personnel_profiles_from_group_c() -> set[str]:
    """Consulta los perfiles (skills) de Grupo C. Mientras C no los exponga, no responde."""
    raise ConnectionError("El catálogo de perfiles de personal (Grupo C) aún no está disponible.")


class OperationsService:
    """Casos de uso y reglas de negocio del módulo operations."""

    def __init__(
        self,
        get_emergency_status: Callable[[int], str | None],
        repository: OperationsRepository,
        get_resource_types: Callable[[], set[str]] = get_resource_types_from_group_b,
        get_personnel_profiles: Callable[[], set[str]] = get_personnel_profiles_from_group_c,
    ) -> None:
        self._get_emergency_status = get_emergency_status
        self._get_resource_types = get_resource_types
        self._get_personnel_profiles = get_personnel_profiles
        self.repository = repository

    def validate_emergency(self, emergency_id: int) -> None:
        try:
            status = self._get_emergency_status(emergency_id)
        except (ConnectionError, TimeoutError) as error:
            raise EmergencyUnavailable(
                f"No se pudo consultar la emergencia {emergency_id}."
            ) from error

        if status is None:
            raise EmergencyNotFound(f"La emergencia {emergency_id} no existe.")
        if status != "ACTIVE":
            raise EmergencyNotActive(
                f"La emergencia {emergency_id} no está activa (estado: {status})."
            )

    def create_operation(self, data: OperationCreate) -> Operation:
        self.validate_emergency(data.emergency_id)
        try:
            operation = self.repository.create_operation(
                emergency_id=data.emergency_id, name=data.name, priority=data.priority
            )
            self.repository.commit()
        except Exception:
            self.repository.rollback()
            raise
        return operation

    def get_operation(self, operation_id: int) -> Operation:
        operation = self.repository.get_operation(operation_id)
        if operation is None:
            raise OperationNotFound(f"La operación {operation_id} no existe.")
        return operation

    def create_mission(self, operation_id: int, data: MissionCreate) -> Mission:
        """Crea una misión en estado PLANNED si existe la operación."""
        self.get_operation(operation_id)

        try:
            mission = self.repository.create_mission(
                operation_id=operation_id,
                name=data.name,
                priority=data.priority,
                status=MissionStatus.PLANNED,
            )
            self.repository.commit()
        except Exception:
            self.repository.rollback()
            raise

        return mission

    def get_mission(self, mission_id: int) -> Mission:
        """Consulta una misión por ID con sus requisitos asociados."""
        mission = self.repository.get_mission(mission_id)
        if mission is None:
            raise MissionNotFound(f"La misión {mission_id} no existe.")
        return mission

    def add_requirement(
        self,
        mission_id: int,
        data: RequirementCreate,
    ) -> MissionResourceRequirement | MissionPersonnelRequirement:
        """Agrega un requisito de recurso o personal validando los catálogos."""
        self.get_mission(mission_id)

        try:
            if isinstance(data, ResourceRequirementCreate):
                try:
                    valid_resource_types = self._get_resource_types()
                except (ConnectionError, TimeoutError) as error:
                    raise CatalogUnavailable(
                        "No se pudo consultar el catálogo de Grupo B."
                    ) from error

                if data.resource_type not in valid_resource_types:
                    raise InvalidCatalogItem(
                        f"El tipo de recurso '{data.resource_type}' "
                        "no existe en el catálogo de Grupo B."
                    )

                requirement = self.repository.add_resource_requirement(
                    mission_id=mission_id,
                    resource_type=data.resource_type,
                    quantity=data.quantity,
                )
            elif isinstance(data, PersonnelRequirementCreate):
                try:
                    valid_personnel_profiles = self._get_personnel_profiles()
                except (ConnectionError, TimeoutError) as error:
                    raise CatalogUnavailable(
                        "No se pudo consultar el catálogo de Grupo C."
                    ) from error

                if data.profile not in valid_personnel_profiles:
                    raise InvalidCatalogItem(
                        f"El perfil de personal '{data.profile}' "
                        "no existe en el catálogo de Grupo C."
                    )

                requirement = self.repository.add_personnel_requirement(
                    mission_id=mission_id,
                    profile=data.profile,
                    quantity=data.quantity,
                )
            else:
                raise InvalidCatalogItem("Tipo de requisito no soportado.")

            self.repository.commit()
        except Exception:
            self.repository.rollback()
            raise

        return requirement
