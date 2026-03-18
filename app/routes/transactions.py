from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Transaction, CategoryRule, Account
from app.schemas import TransactionCreate, TransactionResponse, TransactionUpdate
from typing import Optional

router = APIRouter()

def auto_categorize_transaction(description: str, db: Session):
    """Automatically categorize transaction based on rules"""
    if not description:
        return None
    
    # Get all active rules ordered by priority (highest first)
    rules = db.query(CategoryRule).filter(
        CategoryRule.is_active == True
    ).order_by(CategoryRule.priority.desc()).all()
    
    description_lower = description.lower().strip()
    
    for rule in rules:
        # Check keyword pattern (exact match, case-insensitive)
        if rule.keyword_pattern and rule.keyword_pattern.lower() in description_lower:
            return rule.category
        # Check merchant pattern (partial match, case-insensitive)
        if rule.merchant_pattern and rule.merchant_pattern.lower() in description_lower:
            return rule.category
    
    return None

@router.get("/", response_model=list[TransactionResponse])
def get_transactions(
    user_id: int = Query(1, description="User ID"),
    account_id: Optional[int] = Query(None, description="Filter by account ID"),
    category: Optional[str] = Query(None, description="Filter by category"),
    skip: int = Query(0, description="Number of records to skip"),
    limit: int = Query(50, description="Max records to return"),
    db: Session = Depends(get_db)
):
    """Get all transactions for a user, optionally filtered with pagination"""
    # Get accounts for the user
    accounts = db.query(Account).filter(Account.user_id == user_id).all()
    account_ids = [a.id for a in accounts]
    
    if not account_ids:
        return []
    
    query = db.query(Transaction).filter(Transaction.account_id.in_(account_ids))
    
    if account_id:
        query = query.filter(Transaction.account_id == account_id)
    
    if category:
        query = query.filter(Transaction.category == category)
    
    # Apply pagination
    transactions = query.order_by(Transaction.created_at.desc()).offset(skip).limit(limit).all()
    
    return transactions

@router.get("/count")
def get_transactions_count(
    user_id: int = Query(1, description="User ID"),
    account_id: Optional[int] = Query(None, description="Filter by account ID"),
    category: Optional[str] = Query(None, description="Filter by category"),
    db: Session = Depends(get_db)
):
    """Get total count of transactions for pagination"""
    # Get accounts for the user
    accounts = db.query(Account).filter(Account.user_id == user_id).all()
    account_ids = [a.id for a in accounts]
    
    if not account_ids:
        return {"total": 0}
    
    query = db.query(Transaction).filter(Transaction.account_id.in_(account_ids))
    
    if account_id:
        query = query.filter(Transaction.account_id == account_id)
    
    if category:
        query = query.filter(Transaction.category == category)
    
    total = query.count()
    return {"total": total}

@router.post("/", response_model=TransactionResponse)
def create_transaction(txn: TransactionCreate, db: Session = Depends(get_db)):
    """Create a new transaction with auto-categorization"""
    # Auto-categorize if no category provided
    category = txn.category
    if not category:
        category = auto_categorize_transaction(txn.description, db)
    
    new_txn = Transaction(
        account_id=txn.account_id,
        description=txn.description,
        amount=txn.amount,
        category=category
    )
    db.add(new_txn)
    db.commit()
    db.refresh(new_txn)
    return new_txn

@router.put("/{transaction_id}/category", response_model=TransactionResponse)
def update_transaction_category(
    transaction_id: int,
    update_data: TransactionUpdate,
    save_as_rule: bool = Query(False, description="Save as new category rule"),
    db: Session = Depends(get_db)
):
    """Update transaction category"""
    txn = db.query(Transaction).filter(Transaction.id == transaction_id).first()
    if not txn:
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    if update_data.category is not None:
        old_category = txn.category
        txn.category = update_data.category
        
        # Save as rule if requested
        if save_as_rule and txn.description:
            # Use first word of description as keyword
            keyword = txn.description.split()[0] if txn.description else None
            if keyword:
                # Check if rule already exists
                existing_rule = db.query(CategoryRule).filter(
                    CategoryRule.keyword_pattern.ilike(keyword)
                ).first()
                
                if not existing_rule:
                    # Get user_id from account
                    account = db.query(Account).filter(Account.id == txn.account_id).first()
                    if account:
                        new_rule = CategoryRule(
                            user_id=account.user_id,
                            category=update_data.category,
                            keyword_pattern=keyword,
                            priority=1,
                            is_active=True
                        )
                        db.add(new_rule)
                        db.commit()
    
    db.commit()
    db.refresh(txn)
    return txn

@router.post("/categorize-all")
def categorize_all_transactions(
    user_id: int = Query(1),
    db: Session = Depends(get_db)
):
    """Apply auto-categorization to all uncategorized transactions"""
    # Get accounts for the user
    accounts = db.query(Account).filter(Account.user_id == user_id).all()
    account_ids = [a.id for a in accounts]
    
    if not account_ids:
        return {"message": "No accounts found"}
    
    transactions = db.query(Transaction).filter(
        Transaction.account_id.in_(account_ids),
        Transaction.category == None
    ).all()
    
    count = 0
    for txn in transactions:
        category = auto_categorize_transaction(txn.description, db)
        if category:
            txn.category = category
            count += 1
    
    db.commit()
    return {"message": f"Categorized {count} transactions"}

@router.get("/uncategorized")
def get_uncategorized_transactions(
    user_id: int = Query(1),
    db: Session = Depends(get_db)
):
    """Get all uncategorized transactions"""
    # Get accounts for the user
    accounts = db.query(Account).filter(Account.user_id == user_id).all()
    account_ids = [a.id for a in accounts]
    
    if not account_ids:
        return []
    
    return db.query(Transaction).filter(
        Transaction.account_id.in_(account_ids),
        Transaction.category == None
    ).order_by(Transaction.created_at.desc()).all()
