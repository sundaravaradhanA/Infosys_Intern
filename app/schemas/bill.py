from pydantic import BaseModel, Field
from datetime import datetime


class BillBase(BaseModel):
    biller_name: str = Field(..., min_length=1, description="Name of the bill")
    amount_due: float = Field(..., gt=0, description="Bill amount must be positive")
    due_date: datetime


class BillCreate(BillBase):
    user_id: int


class BillUpdate(BaseModel):
    biller_name: str = Field(..., min_length=1)
    amount_due: float = Field(..., gt=0)
    due_date: datetime
    auto_pay: bool = False


class BillResponse(BillBase):
    id: int
    user_id: int
    status: str
    auto_pay: bool = False
    category: str = "Bills"
    is_paid: bool = False

    class Config:
        from_attributes = True
