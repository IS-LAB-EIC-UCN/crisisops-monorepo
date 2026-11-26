from crisisops.core.exceptions import DomainError
from crisisops.modules.personnel.models import PersonnelAssignment, ResponderSkill
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
    #------H06 (T6.1)--------
    def register_responder_skill(
        self, responder_id: int, skill_code: str
    ) -> ResponderSkill:
        if self.repository.get_responder(responder_id) is None:
            raise DomainError(f"Brigadista con ID {responder_id} no encontrado.")

        if self.repository.get_skill(skill_code) is None:
            raise DomainError(f"Competencia {skill_code} no encontrada.")

        return self.repository.add_responder_skill(responder_id, skill_code)
    #fin H06 (T6.1)----------
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

        # ajustes H06 (T6.2)--------
        eligible_responders = []

        # RN-2: cada candidato posee todas las competencias solicitadas.
        responders = self.repository.find_active_responders_by_skills(required_skills)
        if not responders:
            return eligible_responders

        # RN-3: el requisito de certificación depende de la competencia.
        skills_requiring_certification = []
        for skill_code in dict.fromkeys(required_skills):
            skill = self.repository.get_skill(skill_code)
            if skill is not None and skill.requires_certification:
                skills_requiring_certification.append(skill_code)

        for responder in responders:

           
        
            covering_shift = self.repository.get_covering_shift(
                responder.id,
                start_time,
                end_time,
            )

            if covering_shift is None:
                continue

            # RN-3: cada certificación exigida debe cubrir todo el período.
            certifications_valid = all(
                self.repository.get_valid_certification(
                    responder.id,
                    skill_code,
                    start_time,
                    end_time,
                )
                is not None
                for skill_code in skills_requiring_certification
            )
            if not certifications_valid:
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

    def validate_brigade_coverage(
        self,
        responder_ids: list[int],
        required_skills: list[str],
    ) -> list[str]:
        """
        Comprueba que la brigada cubra cada competencia requerida al menos una vez.

        Retorna la lista de competencias faltantes (vacía si la brigada es apta).
        """
        missing_skills = []

        for skill in required_skills:
            covered = any(
                self.repository.responder_has_skill(responder_id, skill) is not None
                for responder_id in responder_ids
            )
            if not covered and skill not in missing_skills:
                missing_skills.append(skill)

        return missing_skills