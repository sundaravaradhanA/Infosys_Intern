"""
Alert Service for Overspending Detection and Alert Management
Handles budget exceeded alerts and notification management
"""
from sqlalchemy.orm import Session
from app.models import Alert, Budget
from typing import List, Optional, Dict
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class AlertService:
    """Handles alert generation and management"""
    
    # Alert types
    ALERT_TYPE_BUDGET_EXCEEDED = "budget_exceeded"
    ALERT_TYPE_INFO = "info"
    ALERT_TYPE_WARNING = "warning"
    ALERT_TYPE_ERROR = "error"
    
    def __init__(self, db: Session):
        self.db = db
    
    def check_budget_exceeded(self, budget_id: int, user_id: int) -> Optional[Alert]:
        """
        Check if a budget is exceeded and create an alert if needed
        Returns the alert if created, None if not exceeded or alert already exists
        """
        budget = self.db.query(Budget).filter(
            Budget.id == budget_id,
            Budget.user_id == user_id
        ).first()
        
        if not budget:
            return None
        
        # Check if over budget
        if budget.spent_amount <= budget.limit_amount:
            return None
        
        # Check if alert already exists for this budget
        existing_alert = self.db.query(Alert).filter(
            Alert.user_id == user_id,
            Alert.alert_type == self.ALERT_TYPE_BUDGET_EXCEEDED,
            Alert.title.like(f"%{budget.category}%"),
            Alert.created_at >= self._get_month_start(budget.month)
        ).first()
        
        if existing_alert:
            logger.info(f"Alert already exists for budget {budget_id}")
            return None
        
        # Create new alert
        alert = self.create_budget_exceeded_alert(
            user_id=user_id,
            category=budget.category,
            spent_amount=budget.spent_amount,
            limit_amount=budget.limit_amount,
            month=budget.month
        )
        
        return alert
    
    def _get_month_start(self, month_str: str) -> datetime:
        """Get the start of the month for the given month string"""
        try:
            year, month = month_str.split('-')
            return datetime(int(year), int(month), 1)
        except (ValueError, IndexError):
            return datetime(datetime.now().year, datetime.now().month, 1)
    
    def create_budget_exceeded_alert(
        self,
        user_id: int,
        category: str,
        spent_amount: float,
        limit_amount: float,
        month: str
    ) -> Alert:
        """Create a budget exceeded alert"""
        over_amount = spent_amount - limit_amount
        
        alert = Alert(
            user_id=user_id,
            title=f"Budget Exceeded: {category}",
            message=f"You've exceeded your {category} budget for {month}. Spent: ₹{spent_amount:.2f}, Limit: ₹{limit_amount:.2f}, Over by: ₹{over_amount:.2f}",
            alert_type=self.ALERT_TYPE_BUDGET_EXCEEDED,
            is_read=False
        )
        
        self.db.add(alert)
        self.db.commit()
        self.db.refresh(alert)
        
        logger.info(f"Created budget exceeded alert for user {user_id}, category {category}")
        return alert
    
    def check_all_budgets(self, user_id: int) -> List[Alert]:
        """Check all user budgets for overspending and create alerts"""
        budgets = self.db.query(Budget).filter(Budget.user_id == user_id).all()
        
        alerts_created = []
        for budget in budgets:
            alert = self.check_budget_exceeded(budget.id, user_id)
            if alert:
                alerts_created.append(alert)
        
        return alerts_created
    
    def get_user_alerts(self, user_id: int, unread_only: bool = False) -> List[Alert]:
        """Get all alerts for a user"""
        query = self.db.query(Alert).filter(Alert.user_id == user_id)
        
        if unread_only:
            query = query.filter(Alert.is_read == False)
        
        return query.order_by(Alert.created_at.desc()).all()
    
    def get_unread_count(self, user_id: int) -> int:
        """Get count of unread alerts for a user"""
        return self.db.query(Alert).filter(
            Alert.user_id == user_id,
            Alert.is_read == False
        ).count()
    
    def mark_as_read(self, alert_id: int, user_id: int) -> Optional[Alert]:
        """Mark an alert as read"""
        alert = self.db.query(Alert).filter(
            Alert.id == alert_id,
            Alert.user_id == user_id
        ).first()
        
        if not alert:
            return None
        
        alert.is_read = True
        self.db.commit()
        self.db.refresh(alert)
        
        logger.info(f"Marked alert {alert_id} as read")
        return alert
    
    def mark_all_as_read(self, user_id: int) -> int:
        """Mark all alerts as read for a user"""
        count = self.db.query(Alert).filter(
            Alert.user_id == user_id,
            Alert.is_read == False
        ).update({"is_read": True})
        
        self.db.commit()
        
        logger.info(f"Marked {count} alerts as read for user {user_id}")
        return count
    
    def delete_alert(self, alert_id: int, user_id: int) -> bool:
        """Delete an alert"""
        alert = self.db.query(Alert).filter(
            Alert.id == alert_id,
            Alert.user_id == user_id
        ).first()
        
        if alert:
            self.db.delete(alert)
            self.db.commit()
            logger.info(f"Deleted alert {alert_id}")
            return True
        return False
    
    def create_alert(
        self,
        user_id: int,
        title: str,
        message: str,
        alert_type: str = "info"
    ) -> Alert:
        """Create a generic alert"""
        alert = Alert(
            user_id=user_id,
            title=title,
            message=message,
            alert_type=alert_type,
            is_read=False
        )
        
        self.db.add(alert)
        self.db.commit()
        self.db.refresh(alert)
        
        logger.info(f"Created alert: {title} for user {user_id}")
        return alert
    
    def get_alert_with_details(self, alert_id: int, user_id: int) -> Optional[Dict]:
        """Get alert with formatted details"""
        alert = self.db.query(Alert).filter(
            Alert.id == alert_id,
            Alert.user_id == user_id
        ).first()
        
        if not alert:
            return None
        
        return {
            "id": alert.id,
            "user_id": alert.user_id,
            "title": alert.title,
            "message": alert.message,
            "alert_type": alert.alert_type,
            "is_read": alert.is_read,
            "created_at": alert.created_at.isoformat() if alert.created_at else None
        }
