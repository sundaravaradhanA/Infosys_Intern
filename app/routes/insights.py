from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional
from app.database import get_db
from app.models import Transaction, Account

router = APIRouter()

@router.get("/spending-by-category")
def get_spending_by_category(
    user_id: int = Query(1, description="User ID"),
    month: Optional[str] = Query(None, description="Month in YYYY-MM format"),
    db: Session = Depends(get_db)
):
    """Get spending by category for a user, optionally filtered by month"""
    # Get accounts for the user
    accounts = db.query(Account).filter(Account.user_id == user_id).all()
    account_ids = [a.id for a in accounts]
    
    if not account_ids:
        return []
    
    # Base query for transactions - expenses are negative amounts
    query = db.query(
        Transaction.category,
        func.sum(func.abs(Transaction.amount)).label('amount')
    ).filter(
        Transaction.account_id.in_(account_ids),
        Transaction.amount < 0  # Expenses (negative amounts)
    )
    
    # Filter by month if provided
    if month:
        query = query.filter(func.to_char(Transaction.created_at, 'YYYY-MM') == month)
    
    # Group by category
    results = query.group_by(Transaction.category).all()
    
    return [
        {"category": r.category or "Uncategorized", "amount": float(r.amount)}
        for r in results
    ]

@router.get("/income-by-category")
def get_income_by_category(
    user_id: int = Query(1, description="User ID"),
    month: Optional[str] = Query(None, description="Month in YYYY-MM format"),
    db: Session = Depends(get_db)
):
    """Get income by category for a user, optionally filtered by month"""
    # Get accounts for the user
    accounts = db.query(Account).filter(Account.user_id == user_id).all()
    account_ids = [a.id for a in accounts]
    
    if not account_ids:
        return []
    
    # Base query for transactions - income are positive amounts
    query = db.query(
        Transaction.category,
        func.sum(Transaction.amount).label('amount')
    ).filter(
        Transaction.account_id.in_(account_ids),
        Transaction.amount > 0  # Income (positive amounts)
    )
    
    # Filter by month if provided
    if month:
        query = query.filter(func.to_char(Transaction.created_at, 'YYYY-MM') == month)
    
    # Group by category
    results = query.group_by(Transaction.category).all()
    
    return [
        {"category": r.category or "Uncategorized", "amount": float(r.amount)}
        for r in results
    ]

@router.get("/monthly-summary")
def get_monthly_summary(
    user_id: int = Query(1, description="User ID"),
    month: Optional[str] = Query(None, description="Month in YYYY-MM format"),
    db: Session = Depends(get_db)
):
    """Get monthly summary including total income, expenses, and balance"""
    # Get accounts for the user
    accounts = db.query(Account).filter(Account.user_id == user_id).all()
    account_ids = [a.id for a in accounts]
    
    if not account_ids:
        return {"total_income": 0, "total_expense": 0, "balance": 0}
    
    # Get total income (positive amounts)
    income_query = db.query(func.coalesce(func.sum(Transaction.amount), 0)).filter(
        Transaction.account_id.in_(account_ids),
        Transaction.amount > 0
    )
    
    # Get total expenses (negative amounts)
    expense_query = db.query(func.coalesce(func.sum(func.abs(Transaction.amount)), 0)).filter(
        Transaction.account_id.in_(account_ids),
        Transaction.amount < 0
    )
    
    # Filter by month if provided
    if month:
        income_query = income_query.filter(func.to_char(Transaction.created_at, 'YYYY-MM') == month)
        expense_query = expense_query.filter(func.to_char(Transaction.created_at, 'YYYY-MM') == month)
    
    total_income = float(income_query.scalar() or 0)
    total_expense = float(expense_query.scalar() or 0)
    
    return {
        "total_income": total_income,
        "total_expense": total_expense,
        "balance": total_income - total_expense,
        "month": month
    }

@router.get("/category-trend")
def get_category_trend(
    user_id: int = Query(1, description="User ID"),
    category: str = Query(..., description="Category to get trend for"),
    months: int = Query(6, description="Number of months to look back"),
    db: Session = Depends(get_db)
):
    """Get spending trend for a specific category over time"""
    # Get accounts for the user
    accounts = db.query(Account).filter(Account.user_id == user_id).all()
    account_ids = [a.id for a in accounts]
    
    if not account_ids:
        return []
    
    # Get spending by month for the category (expenses are negative)
    results = db.query(
        func.to_char(Transaction.created_at, 'YYYY-MM').label('month'),
        func.sum(func.abs(Transaction.amount)).label('amount')
    ).filter(
        Transaction.account_id.in_(account_ids),
        Transaction.category == category,
        Transaction.amount < 0
    ).group_by(
        func.to_char(Transaction.created_at, 'YYYY-MM')
    ).order_by(
        func.to_char(Transaction.created_at, 'YYYY-MM').desc()
    ).limit(months).all()
    
    return [
        {"month": r.month, "amount": float(r.amount)}
        for r in results
    ]
