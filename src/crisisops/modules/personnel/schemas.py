from datetime import datetime

from pydantic import BaseModel, ConfigDict


class AssignmentCreate(BaseModel):
    mission_id: int | None = None
    start_at: datetime
    end_at: datetime

class AssignmentResponse(BaseModel):
    id: int
    responder_id: int
    mission_id: int | None
    start_at: datetime
    end_at: datetime
    status: str

    model_config = ConfigDict(from_attributes=True)