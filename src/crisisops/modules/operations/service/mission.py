from crisisops.modules.operations.exceptions import (
    CatalogUnavailable,
    InvalidCatalogItem,
    MissionNotFound,
)
from crisisops.modules.operations.models import (
    Mission,
    MissionPersonnelRequirement,
    MissionResourceRequirement,
    MissionStatus,
)
from crisisops.modules.operations.schemas.mission import MissionCreate
from crisisops.modules.operations.schemas.requirement import (
    PersonnelRequirementCreate,
    RequirementCreate,
    ResourceRequirementCreate,
)
from crisisops.modules.operations.service.operation import OperationsService


class MissionsService(OperationsService):
    """Casos de uso de misiones y requisitos (HU-02). Hereda constructor y get_operation."""

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
