from crisisops.modules.emergencies.models import Emergency
from sqlalchemy.orm import Session
from crisisops.modules.emergencies.schemas import EmergencyCreate



class EmergenciesRepository:
    """Acceso a persistencia del módulo emergencies."""

    def __init__(self, db: Session) -> None:
        self.db = db





    def get(self, emergency_id: int)-> Emergency | None:
        return self.db.get(Emergency, emergency_id)





    def add(self,emergency: EmergencyCreate) -> Emergency:
        self.db.add(emergency)
        self.db.flush()

        return emergency





    def update(self,emergency: Emergency) -> Emergency:
        self.db.add(emergency)
        self.db.flush()
        return emergency