from datetime import datetime

from pydantic import BaseModel, Field


class AssignmentCreate(BaseModel):
    start_time: datetime = Field(..., description="Fecha y hora de inicio de la asignación")
    end_time: datetime = Field(..., description="Fecha y hora de fin de la asignación")
    # Puedes agregar otros campos necesarios según su modelo (ej. rol, ubicación, etc.)

class AssignmentResponse(BaseModel):
    id: int
    responder_id: int
    start_time: datetime
    end_time: datetime
    
    class Config:
        from_attributes = True