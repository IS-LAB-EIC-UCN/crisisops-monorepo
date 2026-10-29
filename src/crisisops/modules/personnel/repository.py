from datetime import datetime
from sqlalchemy import or_, select

from crisisops.modules.personnel.models import (
    AssignmentStatus,
    Certification,
    PersonnelAssignment,
    ResponderSkill,
    Shift,
)


class PersonnelRepository:
    """Acceso a persistencia del módulo personnel."""
 
    def __init__(self, db):
        self.db = db
 
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

    
    #H02 - T2.3 responder_has_skill(), get_valid_certification() y get_covering_shift()
    def responder_has_skill(self, responder_id, skill_id) -> bool:
        """True si el brigadista posee la competencia."""
        stmt = select(ResponderSkill).where(
            ResponderSkill.responder_id == responder_id,
            ResponderSkill.skill_id == skill_id,
        )
        return self.db.scalars(stmt).first() is not None

    def get_valid_certification(
        self, responder_id, skill_id, start_time, end_time
    ):
        """Certificación vigente durante todo [start_time, end_time), o None."""
        stmt = select(Certification).where(
            Certification.responder_id == responder_id,
            Certification.skill_id == skill_id,
            Certification.issued_at <= start_time,
            or_(
                Certification.expires_at.is_(None),
                Certification.expires_at >= end_time,
            ),
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
###### fin t2.3