from sqlalchemy import Column, Integer, String, Numeric, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class Bill(Base):
    __tablename__ = "bills"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    name = Column(String, nullable=False)
    amount = Column(Numeric(10, 2), nullable=False)
    due_date = Column(DateTime, nullable=True)

    # ✅ FIX 1: Add missing column
    is_paid = Column(Boolean, default=False)

    # ✅ FIX 2: Add relationship (VERY IMPORTANT)
    user = relationship("User", back_populates="bills")