"""
Budget Service for Monthly Budget Computation and Tracking
Handles budget aggregation, progress calculation, and overspending detection
"""
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models import Budget, Transaction, Account, Alert
from typing import List, Dict, Optional, Tuple
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class BudgetService:
    """Handles budget computation and tracking"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_user_accounts(self, user_id: int) -> List[int]:
        """Get all account IDs for a user"""
        accounts = self.db.query(Account).filter(Account.user_id == user_id).all()
        return [account.id for account in accounts]
    
    def calculate_spent_amount(self, user_id: int, category: str, month: str, year: int) -> float:
        """
        Calculate the total spent amount for a specific category in a month
        Only considers debit transactions (negative amounts)
        """
        account_ids = self.get_user_accounts(user_id)
        
        if not account_ids:
            return 0.0
        
        # Parse month string (format: "2024-01")
        try:
            month_int = int(month.split('-')[1])
        except (ValueError, IndexError):
            month_int = datetime.now().month
        
        # Query transactions for the category in the specified month/year
        # Only consider negative amounts (debits)
        result = self.db.query(func.sum(Transaction.amount)).filter(
            Transaction.account_id.in_(account_ids),
            Transaction.category == category,
            func.extract('month', Transaction.created_at) == month_int,
            func.extract('year', Transaction.created_at) == year,
            Transaction.amount < 0  # Only debits
        ).scalar()
        
        spent = abs(result) if result else 0.0
        return round(spent, 2)
    
    def calculate_all_category_spending(self, user_id: int, month: str, year: int) -> Dict[str, float]:
        """
        Calculate spending for all categories in a given month
        Returns dict of category -> amount
        """
        account_ids = self.get_user_accounts(user_id)
        
        if not account_ids:
            return {}
        
        try:
            month_int = int(month.split('-')[1])
        except (ValueError, IndexError):
            month_int = datetime.now().month
        
        # Query all categories with their total spending
        results = self.db.query(
            Transaction.category,
            func.sum(func.abs(Transaction.amount))
        ).filter(
            Transaction.account_id.in_(account_ids),
            func.extract('month', Transaction.created_at) == month_int,
            func.extract('year', Transaction.created_at) == year,
            Transaction.amount < 0,
            Transaction.category.isnot(None)
        ).group_by(Transaction.category).all()
        
        return {category: round(amount, 2) for category, amount in results if category}
    
    def calculate_progress_percentage(self, spent_amount: float, limit_amount: float) -> float:
        """Calculate budget progress percentage"""
        if limit_amount <= 0:
            return 0.0
        percentage = (spent_amount / limit_amount) * 100
        return round(min(percentage, 100.0), 2)
    
    def is_over_budget(self, spent_amount: float, limit_amount: float) -> bool:
        """Check if spending exceeds budget limit"""
        return spent_amount > limit_amount
    
    def recalculate_budget(self, budget_id: int, user_id: int) -> Optional[Budget]:
        """Recalculate spent_amount for a specific budget"""
        budget = self.db.query(Budget).filter(
            Budget.id == budget_id,
            Budget.user_id == user_id
        ).first()
        
        if not budget:
            return None
        
        # Parse month and year from budget.month string
        try:
            month_str = budget.month  # Format: "2024-01"
            parts = month_str.split('-')
            year = int(parts[0])
            month = parts[1] if len(parts) > 1 else f"{datetime.now().month:02d}"
        except (ValueError, IndexError):
            now = datetime.now()
            year = now.year
            month = f"{now.month:02d}"
        
        # Calculate new spent amount
        spent_amount = self.calculate_spent_amount(user_id, budget.category, month, year)
        budget.spent_amount = spent_amount
        
        self.db.commit()
        self.db.refresh(budget)
        
        logger.info(f"Recalculated budget {budget_id}: spent={spent_amount}, limit={budget.limit_amount}")
        return budget
    
    def recalculate_all_budgets(self, user_id: int, month: str) -> List[Budget]:
        """Recalculate all budgets for a user for a specific month"""
        try:
            year = int(month.split('-')[0])
        except (ValueError, IndexError):
            year = datetime.now().year
        
        budgets = self.db.query(Budget).filter(
            Budget.user_id == user_id,
            Budget.month == month
        ).all()
        
        for budget in budgets:
            month_num = int(month.split('-')[1]) if '-' in month else datetime.now().month
            budget.spent_amount = self.calculate_spent_amount(user_id, budget.category, month, year)
        
        self.db.commit()
        
        logger.info(f"Recalculated {len(budgets)} budgets for user {user_id} month {month}")
        return budgets
    
    def get_budget_with_progress(self, budget_id: int, user_id: int) -> Optional[Dict]:
        """Get budget with progress percentage and status"""
        budget = self.db.query(Budget).filter(
            Budget.id == budget_id,
            Budget.user_id == user_id
        ).first()
        
        if not budget:
            return None
        
        # Recalculate to get latest
        budget = self.recalculate_budget(budget_id, user_id)
        
        progress = self.calculate_progress_percentage(budget.spent_amount, budget.limit_amount)
        is_over = self.is_over_budget(budget.spent_amount, budget.limit_amount)
        
        return {
            "id": budget.id,
            "user_id": budget.user_id,
            "category": budget.category,
            "limit_amount": budget.limit_amount,
            "spent_amount": budget.spent_amount,
            "month": budget.month,
            "progress_percentage": progress,
            "is_over_budget": is_over,
            "remaining_amount": round(budget.limit_amount - budget.spent_amount, 2)
        }
    
    def get_all_budgets_with_progress(self, user_id: int, month: Optional[str] = None) -> List[Dict]:
        """Get all budgets with progress information"""
        if month is None:
            month = f"{datetime.now().year}-{datetime.now().month:02d}"
        
        try:
            year = int(month.split('-')[0])
        except (ValueError, IndexError):
            year = datetime.now().year
        
        budgets = self.db.query(Budget).filter(
            Budget.user_id == user_id,
            Budget.month == month
        ).all()
        
        result = []
        for budget in budgets:
            month_num = int(month.split('-')[1]) if '-' in month else datetime.now().month
            spent = self.calculate_spent_amount(user_id, budget.category, month, year)
            budget.spent_amount = spent
            self.db.commit()
            
            progress = self.calculate_progress_percentage(spent, budget.limit_amount)
            is_over = self.is_over_budget(spent, budget.limit_amount)
            
            result.append({
                "id": budget.id,
                "user_id": budget.user_id,
                "category": budget.category,
                "limit_amount": budget.limit_amount,
                "spent_amount": spent,
                "month": budget.month,
                "progress_percentage": progress,
                "is_over_budget": is_over,
                "remaining_amount": round(budget.limit_amount - spent, 2)
            })
        
        return result
    
    def create_budget(self, user_id: int, category: str, limit_amount: float, month: str) -> Budget:
        """Create a new budget"""
        # Check if budget already exists
        existing = self.db.query(Budget).filter(
            Budget.user_id == user_id,
            Budget.category == category,
            Budget.month == month
        ).first()
        
        if existing:
            raise ValueError(f"Budget already exists for {category} in {month}")
        
        # Calculate initial spent amount
        try:
            year = int(month.split('-')[0])
        except (ValueError, IndexError):
            year = datetime.now().year
        
        spent_amount = self.calculate_spent_amount(user_id, category, month, year)
        
        budget = Budget(
            user_id=user_id,
            category=category,
            limit_amount=limit_amount,
            spent_amount=spent_amount,
            month=month
        )
        
        self.db.add(budget)
        self.db.commit()
        self.db.refresh(budget)
        
        logger.info(f"Created budget: {category} = {limit_amount} for {month}")
        return budget
    
    def update_budget(self, budget_id: int, user_id: int, **kwargs) -> Optional[Budget]:
        """Update an existing budget"""
        budget = self.db.query(Budget).filter(
            Budget.id == budget_id,
            Budget.user_id == user_id
        ).first()
        
        if not budget:
            return None
        
        for key, value in kwargs.items():
            if hasattr(budget, key) and value is not None:
                setattr(budget, key, value)
        
        self.db.commit()
        self.db.refresh(budget)
        
        logger.info(f"Updated budget {budget_id}")
        return budget
    
    def delete_budget(self, budget_id: int, user_id: int) -> bool:
        """Delete a budget"""
        budget = self.db.query(Budget).filter(
            Budget.id == budget_id,
            Budget.user_id == user_id
        ).first()
        
        if budget:
            self.db.delete(budget)
            self.db.commit()
            logger.info(f"Deleted budget {budget_id}")
            return True
        return False
