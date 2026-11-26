from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from crisisops.modules.operations.models import MissionStatus
from crisisops.modules.operations.schemas.requirement import (
    PersonnelRequirementResponse,
    ResourceRequirementResponse,
)
from crisisops.shared.enums import Priority


# --- HU-02: Misiones ---
class MissionCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)
    name: str = Field(min_length=1, max_length=150)
    priority: Priority


class MissionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    operation_id: int
    name: str
    priority: Priority
    status: MissionStatus
    created_at: datetime
    resource_requirements: list[ResourceRequirementResponse] = []
    personnel_requirements: list[PersonnelRequirementResponse] = []
