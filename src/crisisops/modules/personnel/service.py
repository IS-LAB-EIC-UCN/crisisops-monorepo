from crisisops.core.exceptions import DomainError
from crisisops.modules.personnel.models import PersonnelAssignment
from crisisops.modules.personnel.repository import PersonnelRepository
from crisisops.modules.personnel.schemas import AssignmentCreate


from datetime import datetime
from typing import List, Optional



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



    def __init__(self, repository: PersonnelRepository):
        self.repository = repository

    def get_eligible_responders(
        self,
        start_time: datetime,
        end_time: datetime,
        required_skills: Optional[List[str]] = None
    ) -> List:
        """
        Retorna únicamente el personal que cumple con los 4 criterios de elegibilidad :
        - RN-1: Sin solapamiento de horarios.
        - RN-2: Posee las habilidades (skills) requeridas.
        - RN-3: Cuenta con certificación válida y no vencida.
        - RN-4: Turno o disponibilidad activa.
        """
        all_responders = self.repository.get_all_active_responders()
        eligible_responders = []

        for responder in all_responders:
            responder_id = responder.id

            # RN-1
            overlapping = self.repository.get_overlapping_assignments(
                responder_id=responder_id,
                start_time=start_time,
                end_time=end_time
            )
            if overlapping:
                continue  

            # RN-4
            covering_shift = self.repository.get_covering_shift(
                responder_id=responder_id,
                start_time=start_time,
                end_time=end_time
            )
            if not covering_shift:
                continue  

            # RN-3
            valid_cert = self.repository.get_valid_certification(
                responder_id=responder_id,
                check_date=start_time
            )
            if not valid_cert:
                continue  

            # RN-2
            if required_skills:
                missing_skill = False
                for skill in required_skills:
                    has_skill = self.repository.responder_has_skill(
                        responder_id=responder_id,
                        skill_name=skill
                    )
                    if not has_skill:
                        missing_skill = True
                        break
                if missing_skill:
                    continue  

            #  se añade a la lista de elegibles
            eligible_responders.append(responder)

        return eligible_responders