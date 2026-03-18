from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.bill import Bill
from app.schemas.bill import BillCreate, BillUpdate, BillResponse
from app.services.bill_status import determine_bill_status

router = APIRouter(tags=["Bills"])


# CREATE BILL
@router.post("/", response_model=BillResponse)
def create_bill(bill: BillCreate, db: Session = Depends(get_db)):

    # Validate biller name
    if not bill.biller_name.strip():
        raise HTTPException(status_code=400, detail="Biller name cannot be empty")

    # Validate amount
    if bill.amount_due <= 0:
        raise HTTPException(status_code=400, detail="Amount must be positive")

    new_bill = Bill(
        user_id=bill.user_id,
        biller_name=bill.biller_name,
        amount_due=bill.amount_due,
        due_date=bill.due_date,
        status="upcoming",
        auto_pay=False
    )

    db.add(new_bill)
    db.commit()
    db.refresh(new_bill)

    return new_bill


# GET BILLS
@router.get("/", response_model=list[BillResponse])
def get_bills(user_id: int = Query(...), db: Session = Depends(get_db)):

    bills = db.query(Bill).filter(Bill.user_id == user_id).all()

    for bill in bills:
        bill.status = determine_bill_status(bill)

    db.commit()

    return bills


# UPDATE BILL
@router.put("/{bill_id}", response_model=BillResponse)
def update_bill(
    bill_id: int,
    bill: BillUpdate,
    db: Session = Depends(get_db)
):

    existing_bill = db.query(Bill).filter(Bill.id == bill_id).first()

    if not existing_bill:
        raise HTTPException(status_code=404, detail="Bill not found")

    # Validate biller name
    if not bill.biller_name.strip():
        raise HTTPException(status_code=400, detail="Biller name cannot be empty")

    # Validate amount
    if bill.amount_due <= 0:
        raise HTTPException(status_code=400, detail="Amount must be positive")

    existing_bill.biller_name = bill.biller_name
    existing_bill.amount_due = bill.amount_due
    existing_bill.due_date = bill.due_date
    existing_bill.auto_pay = bill.auto_pay

    db.commit()
    db.refresh(existing_bill)

    return existing_bill


# MARK BILL AS PAID
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

    bill.status = "paid"

    db.commit()

    return {"message": "Bill marked as paid"}


# DELETE BILL
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
