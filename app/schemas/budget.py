from pydantic import BaseModel
from typing import Optional

class BudgetBase(BaseModel):
    category: str
    limit_amount: float
    month: str

class BudgetCreate(BudgetBase):
    user_id: int

class BudgetUpdate(BaseModel):
    category: Optional[str] = None
    limit_amount: Optional[float] = None
    month: Optional[str] = None

class BudgetResponse(BudgetBase):
    id: int
    user_id: int
    spent_amount: float
    
    class Config:
        from_attributes = True

class BudgetWithProgress(BudgetResponse):
    """Budget response with progress information"""
    progress_percentage: float = 0.0
    is_over_budget: bool = False
    remaining_amount: float = 0.0
    
    class Config:
        from_attributes = True
