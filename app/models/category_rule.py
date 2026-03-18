from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class CategoryRule(Base):
    __tablename__ = "category_rules"
    __table_args__ = (
        Index('ix_categoryrule_user_id', 'user_id'),
        Index('ix_categoryrule_keyword_pattern', 'keyword_pattern'),
        Index('ix_categoryrule_priority', 'priority'),
    )
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    category = Column(String, nullable=False, index=True)
    keyword_pattern = Column(String, nullable=True, index=True)
    merchant_pattern = Column(String, nullable=True)
    priority = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="category_rules")
