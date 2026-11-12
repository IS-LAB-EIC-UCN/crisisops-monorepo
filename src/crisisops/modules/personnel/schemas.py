from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


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

class EligibilityQuery(BaseModel):
    start_time: datetime
    end_time: datetime
    required_skills: list[str] = Field(default_factory=list)

class ResponderOut(BaseModel):
    id: int
    name: str
    badge_number: str
    role: str
    is_active: bool
    model_config = ConfigDict(from_attributes=True)