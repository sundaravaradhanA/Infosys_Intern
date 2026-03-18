from pydantic import BaseModel
from datetime import datetime

class AlertBase(BaseModel):
    title: str
    message: str
    alert_type: str

class AlertCreate(AlertBase):
    user_id: int

class AlertResponse(AlertBase):
    id: int
    user_id: int
    is_read: bool
    created_at: datetime
    
    class Config:
        from_attributes = True
