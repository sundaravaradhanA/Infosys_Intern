from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import datetime

from app.database import get_db
from app.models.bill import Bill
from app.schemas.bill import BillCreate, BillUpdate, BillResponse

router = APIRouter(tags=["Bills"])


# ================= HELPER FUNCTION =================
def determine_bill_status(bill: Bill) -> str:
    now = datetime.utcnow()

    if bill.is_paid:
        return "Paid"

    if bill.due_date and bill.due_date > now:
        return "Upcoming"

    return "Pending"


# ================= CREATE BILL =================
@router.post("/", response_model=BillResponse)
def create_bill(bill: BillCreate, db: Session = Depends(get_db)):

    if not bill.name.strip():
        raise HTTPException(status_code=400, detail="Bill name cannot be empty")

    if bill.amount <= 0:
        raise HTTPException(status_code=400, detail="Amount must be positive")

    new_bill = Bill(
        user_id=bill.user_id,
        name=bill.name,             # ✅ FIXED
        amount=bill.amount,         # ✅ FIXED
        due_date=bill.due_date,
        is_paid=False               # ✅ FIXED
    )

    db.add(new_bill)
    db.commit()
    db.refresh(new_bill)

    return new_bill


# ================= GET BILLS =================
@router.get("/", response_model=list[BillResponse])
def get_bills(user_id: int = Query(...), db: Session = Depends(get_db)):

    bills = db.query(Bill).filter(Bill.user_id == user_id).all()

    # Add dynamic status (not stored in DB)
    for bill in bills:
        bill.status = determine_bill_status(bill)

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

    if not bill.name.strip():
        raise HTTPException(status_code=400, detail="Bill name cannot be empty")

    if bill.amount <= 0:
        raise HTTPException(status_code=400, detail="Amount must be positive")

    existing_bill.name = bill.name              # ✅ FIXED
    existing_bill.amount = bill.amount          # ✅ FIXED
    existing_bill.due_date = bill.due_date

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

    bill.is_paid = True   # ✅ FIXED

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