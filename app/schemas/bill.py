from pydantic import BaseModel
from datetime import datetime


class BillCreate(BaseModel):
    user_id: int
    name: str
    amount: float
    due_date: datetime


class BillUpdate(BaseModel):
    name: str
    amount: float
    due_date: datetime


class BillResponse(BaseModel):
    id: int
    user_id: int
    name: str
    amount: float
    due_date: datetime
    is_paid: bool

    class Config:
        from_attributes = True