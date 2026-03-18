from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime

class Reward(Base):
    __tablename__ = "rewards"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    points = Column(Integer)
    description = Column(String)
    earned_date = Column(DateTime, default=datetime.utcnow)
    expires_date = Column(DateTime)
    
    # Relationships
    user = relationship("User", back_populates="rewards")
