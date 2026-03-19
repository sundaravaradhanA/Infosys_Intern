from sqlalchemy import Column, Integer, String, Numeric, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.database import Base


class Budget(Base):
    __tablename__ = "budgets"

    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "category",
            "month",
            name="uq_budget_user_category_month"
        ),
    )

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    category = Column(String, nullable=False, index=True)

    # ✅ budget limit (FIXED NAME USED IN SCHEDULER)
    limit_amount = Column(Numeric(12, 2), nullable=False)

    # ✅ amount already spent (default safe)
    spent_amount = Column(Numeric(12, 2), default=0, nullable=False)

    # ✅ month format: YYYY-MM
    month = Column(String(7), nullable=False, index=True)

    # Relationships
    user = relationship("User", back_populates="budgets")

    # ✅ OPTIONAL: helper method (useful in future)
    def is_exceeded(self):
        return float(self.spent_amount) > float(self.limit_amount)