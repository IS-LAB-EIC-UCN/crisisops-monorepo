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
        exclude_assignment_id: int | None = None,
    ) -> None:
        """Verifica que un brigadista no tenga asignaciones activas solapadas."""

        conflicting_assignments = self.repository.get_overlapping_assignments(
            responder_id=responder_id,
            start_time=start_time,
            end_time=end_time,
            exclude_assignment_id=exclude_assignment_id,
        )

        if conflicting_assignments:
            raise DomainError(
                f"El personal con ID {responder_id} ya posee una asignación "
                "activa que se solapa en este rango horario."
            )

    def create_assignment(
        self,
        responder_id: int,
        data: AssignmentCreate,
    ) -> PersonnelAssignment:
        """Valida y crea una nueva asignación para un brigadista."""

        self._assert_no_overlap(
            responder_id,
            data.start_at,
            data.end_at,
        )

        assignment = PersonnelAssignment(
            responder_id=responder_id,
            mission_id=data.mission_id,
            start_at=data.start_at,
            end_at=data.end_at,
        )

        return self.repository.create_assignment(assignment)

    def get_eligible_responders(
        self,
        required_skills,
        start_time,
        end_time,
    ):
        """
        Retorna solamente el personal que cumple los criterios
        de elegibilidad para una misión.

        RN-4: tener un turno que cubra el período solicitado.
        RN-2: poseer todas las competencias requeridas.
        RN-3: tener certificaciones vigentes cuando sean necesarias.
        RN-1: no tener asignaciones activas solapadas.
        """

        eligible_responders = []

        responders = self.repository.get_active_responders()

        for responder in responders:

           
        
            covering_shift = self.repository.get_covering_shift(
                responder.id,
                start_time,
                end_time,
            )

            if covering_shift is None:
                continue

            skills_valid = True

           
            for required_skill in required_skills:

            
                responder_skill = self.repository.responder_has_skill(
                    responder.id,
                    required_skill,
                )

                
                if responder_skill is None:
                    skills_valid = False
                    break

                
                skill = self.repository.get_skill(required_skill)

                
                if skill is not None and skill.requires_certification:

                    certification = (
                        self.repository.get_valid_certification(
                            responder.id,
                            required_skill,
                            start_time,
                            end_time,
                        )
                    )

                    
                    if certification is None:
                        skills_valid = False
                        break

        
            if not skills_valid:
                continue

          
            overlapping_assignments = (
                self.repository.get_overlapping_assignments(
                    responder_id=responder.id,
                    start_time=start_time,
                    end_time=end_time,
                )
            )

           
            if overlapping_assignments:
                continue

            
            eligible_responders.append(responder)

        return eligible_responders