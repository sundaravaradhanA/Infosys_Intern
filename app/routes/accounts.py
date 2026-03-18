from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Account
from app.schemas import AccountCreate, AccountResponse

router = APIRouter()

@router.get("/", response_model=list[AccountResponse])
def get_accounts(
    user_id: int = Query(1, description="User ID"),
    db: Session = Depends(get_db)
):
    """Get all accounts for a user"""
    return db.query(Account).filter(Account.user_id == user_id).all()

@router.post("/", response_model=AccountResponse)
def create_account(account: AccountCreate, db: Session = Depends(get_db)):
    """Create a new account"""
    new_account = Account(
        user_id=account.user_id,
        bank_name=account.bank_name,
        account_type=account.account_type,
        balance=account.balance
    )
    db.add(new_account)
    db.commit()
    db.refresh(new_account)
    return new_account

@router.get("/{account_id}", response_model=AccountResponse)
def get_account(
    account_id: int,
    user_id: int = Query(1),
    db: Session = Depends(get_db)
):
    """Get a specific account"""
    account = db.query(Account).filter(
        Account.id == account_id,
        Account.user_id == user_id
    ).first()
    
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    
    return account
