from sqlalchemy import select

from crisisops.modules.personnel.models import (
    AssignmentStatus,
    Certification,
    PersonnelAssignment,
    Responder,
    ResponderSkill,
    Shift,
    Skill,
)


class PersonnelRepository:
    """Acceso a persistencia del módulo personnel."""

    def __init__(self, db):
        self.db = db

    # ---------- H01 ----------
    def get_overlapping_assignments(
        self, responder_id, start_time, end_time, exclude_assignment_id=None
    ):
        """Asignaciones activas del brigadista que se solapan con [start_time, end_time)."""
        stmt = select(PersonnelAssignment).where(
            PersonnelAssignment.responder_id == responder_id,
            PersonnelAssignment.status.not_in(
                [AssignmentStatus.COMPLETED, AssignmentStatus.CANCELLED]
            ),
        )
        return [
            a
            for a in self.db.scalars(stmt)
            if a.overlaps(start_time, end_time) and a.id != exclude_assignment_id
        ]

    def create_assignment(self, assignment: PersonnelAssignment) -> PersonnelAssignment:
        """Guarda una nueva asignación en la base de datos."""
        self.db.add(assignment)
        self.db.commit()
        self.db.refresh(assignment)
        return assignment

    # ---------- H02 (T2.3) ----------
    def get_active_responders(self):
        """Brigadistas activos."""
        return list(self.db.scalars(select(Responder).where(Responder.is_active.is_(True))))

    def get_skill(self, skill_code):
        """Competencia por código, o None."""
        return self.db.scalars(select(Skill).where(Skill.code == skill_code)).first()

    def responder_has_skill(self, responder_id, skill_code):
        """ResponderSkill si el brigadista tiene la competencia, o None."""
        stmt = select(ResponderSkill).where(
            ResponderSkill.responder_id == responder_id,
            ResponderSkill.skill_code == skill_code,
        )
        return self.db.scalars(stmt).first()

    def get_valid_certification(self, responder_id, skill_code, start_time, end_time):
        """Certificación vigente durante todo [start_time, end_time), o None."""
        stmt = select(Certification).where(
            Certification.responder_id == responder_id,
            Certification.skill_code == skill_code,
            Certification.issued_at <= start_time,
            Certification.expires_at >= end_time,
        )
        return self.db.scalars(stmt).first()

    def get_covering_shift(self, responder_id, start_time, end_time):
        """Turno que cubre completamente [start_time, end_time), o None."""
        stmt = select(Shift).where(
            Shift.responder_id == responder_id,
            Shift.start_time <= start_time,
            Shift.end_time >= end_time,
        )
        return self.db.scalars(stmt).first()