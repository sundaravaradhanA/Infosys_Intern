from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta

from app.database import get_db
from app.models import Reward
from app.schemas import RewardCreate, RewardResponse

router = APIRouter(
    prefix="/rewards",
    tags=["Rewards"]
)


# GET ALL REWARDS
@router.get("/", response_model=list[RewardResponse])
def get_rewards(
    user_id: int = Query(..., description="User ID"),
    db: Session = Depends(get_db)
):
    """Get all rewards for a user"""

    rewards = db.query(Reward).filter(
        Reward.user_id == user_id
    ).order_by(Reward.earned_date.desc()).all()

    return rewards


# CREATE REWARD
@router.post("/", response_model=RewardResponse)
def create_reward(reward: RewardCreate, db: Session = Depends(get_db)):
    """Create a new reward"""

    if reward.points <= 0:
        raise HTTPException(
            status_code=400,
            detail="Points must be greater than 0"
        )

    new_reward = Reward(
        user_id=reward.user_id,
        points=reward.points,
        description=reward.description,
        earned_date=datetime.utcnow(),
        expires_date=datetime.utcnow() + timedelta(days=365)
    )

    db.add(new_reward)
    db.commit()
    db.refresh(new_reward)

    return new_reward


# UPDATE REWARD POINTS
@router.put("/{reward_id}", response_model=RewardResponse)
def update_reward(
    reward_id: int,
    points: int = Query(..., description="Updated points value"),
    db: Session = Depends(get_db)
):
    """Update reward points"""

    reward = db.query(Reward).filter(
        Reward.id == reward_id
    ).first()

    if not reward:
        raise HTTPException(
            status_code=404,
            detail="Reward not found"
        )

    reward.points = points

    db.commit()
    db.refresh(reward)

    return reward


# DELETE REWARD
@router.delete("/{reward_id}")
def delete_reward(
    reward_id: int,
    db: Session = Depends(get_db)
):
    """Delete a reward"""

    reward = db.query(Reward).filter(
        Reward.id == reward_id
    ).first()

    if not reward:
        raise HTTPException(
            status_code=404,
            detail="Reward not found"
        )

    db.delete(reward)
    db.commit()

    return {"message": "Reward deleted successfully"}


# GET TOTAL POINTS
@router.get("/total-points")
def get_total_points(
    user_id: int = Query(..., description="User ID"),
    db: Session = Depends(get_db)
):
    """Get total reward points for a user"""

    total = db.query(func.sum(Reward.points)).filter(
        Reward.user_id == user_id
    ).scalar()

    return {"total_points": total or 0}