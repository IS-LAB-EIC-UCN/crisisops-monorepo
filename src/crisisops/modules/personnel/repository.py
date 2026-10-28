from sqlalchemy import select
 
from crisisops.modules.personnel.models import PersonnelAssignment
 
 
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
            PersonnelAssignment.status != "RELEASED",
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
 