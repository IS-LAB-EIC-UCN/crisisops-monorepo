from crisisops.core.exceptions import DomainError
from crisisops.modules.personnel.models import PersonnelAssignment
from crisisops.modules.personnel.repository import PersonnelRepository
from crisisops.modules.personnel.schemas import AssignmentCreate


class PersonnelService:
    """Casos de uso y reglas de negocio del módulo personnel."""

    def __init__(self, repository: PersonnelRepository):
        self.repository = repository

    def _assert_no_overlap(
        self, 
        responder_id: int, 
        start_time, 
        end_time, 
        exclude_assignment_id: int = None
    ) -> None:
       
        conflicting_assignments = self.repository.get_overlapping_assignments(
            responder_id=responder_id,
            start_time=start_time,
            end_time=end_time,
            exclude_assignment_id=exclude_assignment_id
        )

       
        if conflicting_assignments:
            raise DomainError(
                f"El personal con ID {responder_id} ya posee una asignación "
                "activa que se solapa en este rango horario."
            )
    def create_assignment(self, responder_id: int, data: AssignmentCreate) -> PersonnelAssignment:
        """Valida y crea una nueva asignación para un brigadista."""
        
        self._assert_no_overlap(responder_id, data.start_at, data.end_at)
        
        assignment = PersonnelAssignment(
            responder_id=responder_id,
            mission_id=data.mission_id,
            start_at=data.start_at,
            end_at=data.end_at
        )
        
        return self.repository.create_assignment(assignment)
