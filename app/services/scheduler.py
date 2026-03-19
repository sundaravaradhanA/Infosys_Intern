import time
import threading
from datetime import datetime
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models import Account, Budget, Transaction, Alert, Bill


# ---------------- HELPER: PREVENT DUPLICATE ALERTS ----------------
def alert_exists(db: Session, user_id: int, title: str):
    return db.query(Alert).filter(
        Alert.user_id == user_id,
        Alert.title == title,
        Alert.is_read == False
    ).first()


# ---------------- LOW BALANCE ----------------
def check_low_balance(db: Session):
    accounts = db.query(Account).all()

    for acc in accounts:
        if float(acc.balance) < 5000:
            title = "Account Balance Low"

            if not alert_exists(db, acc.user_id, title):
                alert = Alert(
                    user_id=acc.user_id,
                    title=title,
                    message="Your account balance is below ₹5,000. Please recharge soon.",
                    alert_type="warning",
                    is_read=False,
                    created_at=datetime.utcnow()
                )
                db.add(alert)


# ---------------- BUDGET EXCEEDED ----------------
from datetime import datetime

def check_budget_exceeded(db: Session):
    current_month = datetime.utcnow().strftime("%Y-%m")

    budgets = db.query(Budget).filter(
        Budget.month == current_month
    ).all()

    for budget in budgets:
        transactions = db.query(Transaction).join(Account).filter(
            Transaction.category == budget.category,
            Account.user_id == budget.user_id
        ).all()

        total_spent = sum(float(t.amount) for t in transactions)

        # ✅ Unique title per month + category
        title = f"Budget Exceeded: {budget.category} ({current_month})"

        if total_spent > float(budget.limit_amount):

            existing = db.query(Alert).filter(
                Alert.user_id == budget.user_id,
                Alert.title == title,
                Alert.is_read == False
            ).first()

            if not existing:
                alert = Alert(
                    user_id=budget.user_id,
                    title=title,
                    message=f"{budget.category} budget exceeded. Spent ₹{total_spent:.2f}, Limit ₹{budget.limit_amount}",
                    alert_type="budget_exceeded",
                    is_read=False,
                    created_at=datetime.utcnow()
                )
                db.add(alert)

# ---------------- BILL DUE ----------------
def check_bill_due(db: Session):
    today = datetime.utcnow().date()

    bills = db.query(Bill).all()

    for bill in bills:
        if bill.due_date and bill.due_date.date() <= today:
            title = f"Bill Due: {bill.name}"

            if not alert_exists(db, bill.user_id, title):
                alert = Alert(
                    user_id=bill.user_id,
                    title=title,
                    message=f"{bill.name} is due today!",
                    alert_type="bill_due",
                    is_read=False,
                    created_at=datetime.utcnow()
                )
                db.add(alert)


# ---------------- MAIN SCHEDULER LOOP ----------------
def run_scheduler():
    while True:
        db = SessionLocal()

        try:
            print("Running background job...")

            check_low_balance(db)
            check_budget_exceeded(db)
            check_bill_due(db)

            db.commit()

        except Exception as e:
            db.rollback()
            print("Scheduler error:", e)

        finally:
            db.close()

        # ⏱ Run every 3 hours
        time.sleep(60 * 60 * 3)


# ---------------- START THREAD ----------------
def start_scheduler():
    thread = threading.Thread(target=run_scheduler, daemon=True)
    thread.start()