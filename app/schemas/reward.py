from pydantic import BaseModel
from datetime import datetime


class RewardBase(BaseModel):
    points: int
    description: str
    expires_date: datetime | None = None


class RewardCreate(RewardBase):
    user_id: int


class RewardUpdate(BaseModel):
    points: int | None = None
    description: str | None = None
    expires_date: datetime | None = None


class RewardResponse(RewardBase):
    id: int
    user_id: int
    earned_date: datetime

    class Config:
        from_attributes = True
