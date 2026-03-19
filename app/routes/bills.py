from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import datetime

from app.database import get_db
from app.models.bill import Bill
from app.schemas.bill import BillCreate, BillUpdate, BillResponse

router = APIRouter(tags=["Bills"])


# ================= HELPER FUNCTION =================
def determine_bill_status(bill: Bill) -> str:
    """
    Determine bill status dynamically:
    - Paid → if is_paid True OR status == "paid"
    - Upcoming → future due date
    - Pending → past due date and not paid
    """
    now = datetime.utcnow()

    # Paid
    if hasattr(bill, "is_paid") and bill.is_paid:
        return "Paid"
    if hasattr(bill, "status") and bill.status and bill.status.lower() == "paid":
        return "Paid"

    # Upcoming
    if bill.due_date > now:
        return "Upcoming"

    # Pending
    return "Pending"


# ================= CREATE BILL =================
@router.post("/", response_model=BillResponse)
def create_bill(bill: BillCreate, db: Session = Depends(get_db)):

    if not bill.biller_name.strip():
        raise HTTPException(status_code=400, detail="Biller name cannot be empty")

    if bill.amount_due <= 0:
        raise HTTPException(status_code=400, detail="Amount must be positive")

    new_bill = Bill(
        user_id=bill.user_id,
        biller_name=bill.biller_name,
        amount_due=bill.amount_due,
        due_date=bill.due_date,
        status="Upcoming",   # ✅ consistent casing
        auto_pay=False,
        is_paid=False        # ✅ ensure exists
    )

    db.add(new_bill)
    db.commit()
    db.refresh(new_bill)

    return new_bill


# ================= GET BILLS =================
@router.get("/", response_model=list[BillResponse])
def get_bills(user_id: int = Query(...), db: Session = Depends(get_db)):

    bills = db.query(Bill).filter(Bill.user_id == user_id).all()

    for bill in bills:
        # ✅ dynamically assign correct status
        bill.status = determine_bill_status(bill)

    db.commit()

    return bills


# ================= UPDATE BILL =================
@router.put("/{bill_id}", response_model=BillResponse)
def update_bill(
    bill_id: int,
    bill: BillUpdate,
    db: Session = Depends(get_db)
):

    existing_bill = db.query(Bill).filter(Bill.id == bill_id).first()

    if not existing_bill:
        raise HTTPException(status_code=404, detail="Bill not found")

    if not bill.biller_name.strip():
        raise HTTPException(status_code=400, detail="Biller name cannot be empty")

    if bill.amount_due <= 0:
        raise HTTPException(status_code=400, detail="Amount must be positive")

    existing_bill.biller_name = bill.biller_name
    existing_bill.amount_due = bill.amount_due
    existing_bill.due_date = bill.due_date
    existing_bill.auto_pay = bill.auto_pay

    db.commit()
    db.refresh(existing_bill)

    return existing_bill


# ================= MARK BILL AS PAID =================
@router.patch("/{bill_id}/pay")
def pay_bill(
    bill_id: int,
    user_id: int = Query(...),
    db: Session = Depends(get_db)
):

    bill = db.query(Bill).filter(
        Bill.id == bill_id,
        Bill.user_id == user_id
    ).first()

    if not bill:
        raise HTTPException(status_code=404, detail="Bill not found")

    # ✅ mark as paid
    if hasattr(bill, "is_paid"):
        bill.is_paid = True

    bill.status = "Paid"

    db.commit()

    return {"message": "Bill marked as paid"}


# ================= DELETE BILL =================
@router.delete("/{bill_id}")
def delete_bill(
    bill_id: int,
    user_id: int = Query(...),
    db: Session = Depends(get_db)
):

    bill = db.query(Bill).filter(
        Bill.id == bill_id,
        Bill.user_id == user_id
    ).first()

    if not bill:
        raise HTTPException(status_code=404, detail="Bill not found")

    db.delete(bill)
    db.commit()

    return {"message": "Bill deleted successfully"}