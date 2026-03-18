from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models.bill import Bill
from app.models.alert import Alert


def check_upcoming_bills():
    db: Session = SessionLocal()

    today = datetime.utcnow()
    reminder_date = today + timedelta(days=2)

    bills = db.query(Bill).filter(
        Bill.due_date <= reminder_date,
        Bill.status == "upcoming"
    ).all()

    for bill in bills:

        message = f"{bill.biller_name} is due on {bill.due_date.date()}"

        alert = Alert(
            user_id=bill.user_id,
            title="Bill Reminder",
            message=message,
            alert_type="bill_reminder",
            is_read=False
        )

        db.add(alert)

        print(f"Reminder created for bill: {bill.biller_name}")

    db.commit()
    db.close()


def start_scheduler():
    scheduler = BackgroundScheduler()

    # Run reminder job every 24 hours
    scheduler.add_job(check_upcoming_bills, "interval", seconds=30)

    scheduler.start()