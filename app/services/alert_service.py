"""
Alert Service for Overspending Detection and Alert Management
Handles budget exceeded, low balance, and bill due alerts
"""

from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models import Alert, Budget, Account, Transaction, Bill
from typing import List, Optional, Dict
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class AlertService:
    """Handles alert generation and management"""

    # Alert types
    ALERT_TYPE_BUDGET_EXCEEDED = "budget_exceeded"
    ALERT_TYPE_LOW_BALANCE = "low_balance"
    ALERT_TYPE_BILL_DUE = "bill_due"
    ALERT_TYPE_INFO = "info"

    def __init__(self, db: Session):
        self.db = db

    # ================= BUDGET EXCEEDED =================
    def check_budget_exceeded(self, budget_id: int, user_id: int) -> Optional[Alert]:
        budget = self.db.query(Budget).filter(
            Budget.id == budget_id,
            Budget.user_id == user_id
        ).first()

        if not budget:
            return None

        if float(budget.spent_amount) <= float(budget.limit_amount):
            return None

        # Prevent duplicate per month
        existing = self.db.query(Alert).filter(
            Alert.user_id == user_id,
            Alert.alert_type == self.ALERT_TYPE_BUDGET_EXCEEDED,
            Alert.title.like(f"%{budget.category}%"),
            Alert.created_at >= self._get_month_start(budget.month)
        ).first()

        if existing:
            return None

        return self.create_budget_exceeded_alert(
            user_id,
            budget.category,
            float(budget.spent_amount),
            float(budget.limit_amount),
            budget.month
        )

    def create_budget_exceeded_alert(self, user_id, category, spent, limit, month):
        over = spent - limit

        alert = Alert(
            user_id=user_id,
            title=f"Budget Exceeded: {category}",
            message=f"{category} budget exceeded for {month}. Spent ₹{spent}, Limit ₹{limit}, Over ₹{over}",
            alert_type=self.ALERT_TYPE_BUDGET_EXCEEDED,
            is_read=False
        )

        self.db.add(alert)
        self.db.commit()
        self.db.refresh(alert)

        return alert

    # ================= LOW BALANCE =================
    def check_low_balance(self, user_id: int) -> List[Alert]:
        alerts = []
        today = datetime.utcnow().date()

        accounts = self.db.query(Account).filter(Account.user_id == user_id).all()

        for acc in accounts:
            if acc.balance < 1000:

                # Prevent duplicate per day
                existing = self.db.query(Alert).filter(
                    Alert.user_id == user_id,
                    Alert.alert_type == self.ALERT_TYPE_LOW_BALANCE,
                    Alert.title == f"Low Balance: {acc.name}",
                    func.date(Alert.created_at) == today
                ).first()

                if existing:
                    continue

                alert = Alert(
                    user_id=user_id,
                    title=f"Low Balance: {acc.name}",
                    message=f"Your account '{acc.name}' balance is low (₹{acc.balance})",
                    alert_type=self.ALERT_TYPE_LOW_BALANCE,
                    is_read=False
                )

                self.db.add(alert)
                alerts.append(alert)

        self.db.commit()
        return alerts

    # ================= BILL DUE (🔥 FIXED STRONG DUPLICATE LOGIC) =================
    def check_bill_due(self, user_id: int) -> List[Alert]:
        alerts = []
        upcoming = datetime.utcnow() + timedelta(days=3)
        today = datetime.utcnow().date()

        bills = self.db.query(Bill).filter(
            Bill.user_id == user_id,
            Bill.due_date <= upcoming
        ).all()

        for bill in bills:

            # Handle both schema types
            is_unpaid = False
            if hasattr(bill, "is_paid"):
                is_unpaid = (bill.is_paid == False)
            elif hasattr(bill, "status"):
                is_unpaid = (bill.status != "Paid")

            if not is_unpaid:
                continue

            # 🔥 STRONG duplicate prevention (per bill per day)
            existing = self.db.query(Alert).filter(
                Alert.user_id == user_id,
                Alert.alert_type == self.ALERT_TYPE_BILL_DUE,
                Alert.message.contains(bill.biller_name),
                func.date(Alert.created_at) == today
            ).first()

            if existing:
                continue

            alert = Alert(
                user_id=user_id,
                title=f"Bill Due: {bill.biller_name}",
                message=f"{bill.biller_name} bill of ₹{bill.amount_due} is due on {bill.due_date.date()}",
                alert_type=self.ALERT_TYPE_BILL_DUE,
                is_read=False
            )

            self.db.add(alert)
            alerts.append(alert)

        self.db.commit()
        return alerts

    # ================= RUN ALL CHECKS =================
    def generate_all_alerts(self, user_id: int) -> Dict:
        created = []

        budgets = self.db.query(Budget).filter(Budget.user_id == user_id).all()
        for b in budgets:
            alert = self.check_budget_exceeded(b.id, user_id)
            if alert:
                created.append(alert)

        created += self.check_low_balance(user_id)
        created += self.check_bill_due(user_id)

        return {
            "alerts_created": len(created)
        }

    # ================= HELPERS =================
    def _get_month_start(self, month_str: str) -> datetime:
        try:
            year, month = month_str.split('-')
            return datetime(int(year), int(month), 1)
        except:
            return datetime.utcnow()

    # ================= ALERT MANAGEMENT =================
    def get_user_alerts(self, user_id: int, unread_only: bool = False):
        query = self.db.query(Alert).filter(Alert.user_id == user_id)

        if unread_only:
            query = query.filter(Alert.is_read == False)

        return query.order_by(Alert.created_at.desc()).all()

    def get_unread_count(self, user_id: int):
        return self.db.query(Alert).filter(
            Alert.user_id == user_id,
            Alert.is_read == False
        ).count()

    def mark_as_read(self, alert_id: int, user_id: int):
        alert = self.db.query(Alert).filter(
            Alert.id == alert_id,
            Alert.user_id == user_id
        ).first()

        if not alert:
            return None

        alert.is_read = True
        self.db.commit()
        return alert

    def mark_all_as_read(self, user_id: int):
        count = self.db.query(Alert).filter(
            Alert.user_id == user_id,
            Alert.is_read == False
        ).update({"is_read": True})

        self.db.commit()
        return count

    def delete_alert(self, alert_id: int, user_id: int):
        alert = self.db.query(Alert).filter(
            Alert.id == alert_id,
            Alert.user_id == user_id
        ).first()

        if alert:
            self.db.delete(alert)
            self.db.commit()
            return True
        return False