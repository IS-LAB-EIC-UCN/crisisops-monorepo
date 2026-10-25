from crisisops.core.exceptions import DomainError
from crisisops.modules.personnel import schemas
from crisisops.modules.personnel.repository import PersonnelRepository


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
        # T1.4 - Validación de solapamiento de Gabriel
        conflicting_assignments = self.repository.get_overlapping_assignments(
            responder_id=responder_id,
            start_time=start_time,
            end_time=end_time,
            exclude_assignment_id=exclude_assignment_id
        )

        if conflicting_assignments:
            # Nota: Lanza un DomainError, esto es importante para tu router
            raise DomainError(
                f"El personal con ID {responder_id} ya posee una asignación activa "
                "que se solapa en este rango horario."
            )

    def create_assignment(
        self, 
        responder_id: int, 
        assignment: schemas.AssignmentCreate
    ):
        # 1. Validar solapamiento llamando al método interno (T1.4)
        self._assert_no_overlap(
            responder_id=responder_id, 
            start_time=assignment.start_time, 
            end_time=assignment.end_time
        )
        
        # 2. Si no hay error, crear la asignación en la base de datos (T1.3 de Catalina R.)
        return self.repository.create_assignment(responder_id, assignment)