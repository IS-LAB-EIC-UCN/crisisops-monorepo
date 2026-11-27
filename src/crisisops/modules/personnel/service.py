from datetime import UTC, datetime

from crisisops.core.exceptions import DomainError
from crisisops.modules.personnel.models import (
    Certification,
    PersonnelAssignment,
    Responder,
    ResponderSkill,
)
from crisisops.modules.personnel.repository import PersonnelRepository
from crisisops.modules.personnel.schemas import AssignmentCreate, CertificationCreate


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

    def filter_available_on_shift(
        self, moment: datetime | None = None
    ) -> list[Responder]:
        """Retorna el personal de turno y disponible en el momento indicado."""
        target_moment = moment or datetime.now(UTC)
        return self.repository.get_available_on_shift_responders(target_moment)

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

    def add_skill_to_responder(self, responder_id: int, skill_code: str) -> ResponderSkill:
        responder = self.repository.get_responder(responder_id)
        if responder is None:
            raise DomainError(f"El brigadista con ID {responder_id} no existe.")

        existing = self.repository.responder_has_skill(responder_id, skill_code)
        if existing is not None:
            raise DomainError(f"La competencia {skill_code} ya está asociada al brigadista.")

        skill = self.repository.get_skill(skill_code)
        if skill is None:
            raise DomainError(f"La competencia {skill_code} no existe.")

        assoc = ResponderSkill(responder_id=responder_id, skill_code=skill_code)
        return self.repository.add_responder_skill(assoc)

    def add_certification(self, responder_id: int, data: CertificationCreate) -> Certification:
        responder = self.repository.get_responder(responder_id)
        if responder is None:
            raise DomainError(f"El brigadista con ID {responder_id} no existe.")

        skill = self.repository.get_skill(data.skill_code)
        if skill is None:
            raise DomainError(f"La competencia {data.skill_code} no existe.")

        cert = Certification(
            responder_id=responder_id,
            skill_code=data.skill_code,
            issued_at=data.issued_at,
            expires_at=data.expires_at,
        )
        return self.repository.add_certification(cert)
