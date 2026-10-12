from crisisops.modules.emergencies.models import Emergency
from sqlalchemy.orm import Session

class EmergenciesRepository:
    """Acceso a persistencia del módulo emergencies."""
    def __init__(self, db: Session) -> None:
        self.db = db

    def get(self, emergency_id: int)-> Emergency | None:
        return self.db.get(Emergency, emergency_id)