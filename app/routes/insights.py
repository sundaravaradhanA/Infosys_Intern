from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, case
from typing import Optional
from app.database import get_db
from app.models import Transaction, Account, Budget

router = APIRouter(tags=["Insights"])


# ================= EXISTING APIs =================

@router.get("/spending-by-category")
def get_spending_by_category(
    user_id: int = Query(1),
    month: Optional[str] = None,
    db: Session = Depends(get_db)
):
    accounts = db.query(Account).filter(Account.user_id == user_id).all()
    account_ids = [a.id for a in accounts]

    if not account_ids:
        return []

    query = db.query(
        Transaction.category,
        func.sum(func.abs(Transaction.amount)).label('amount')
    ).filter(
        Transaction.account_id.in_(account_ids),
        Transaction.amount < 0
    )

    if month:
        query = query.filter(func.to_char(Transaction.created_at, 'YYYY-MM') == month)

    results = query.group_by(Transaction.category).all()

    return [
        {"category": r.category or "Uncategorized", "amount": float(r.amount)}
        for r in results
    ]


@router.get("/income-by-category")
def get_income_by_category(
    user_id: int = Query(1),
    month: Optional[str] = None,
    db: Session = Depends(get_db)
):
    accounts = db.query(Account).filter(Account.user_id == user_id).all()
    account_ids = [a.id for a in accounts]

    if not account_ids:
        return []

    query = db.query(
        Transaction.category,
        func.sum(Transaction.amount).label('amount')
    ).filter(
        Transaction.account_id.in_(account_ids),
        Transaction.amount > 0
    )

    if month:
        query = query.filter(func.to_char(Transaction.created_at, 'YYYY-MM') == month)

    results = query.group_by(Transaction.category).all()

    return [
        {"category": r.category or "Uncategorized", "amount": float(r.amount)}
        for r in results
    ]


@router.get("/monthly-summary")
def get_monthly_summary(
    user_id: int = Query(1),
    month: Optional[str] = None,
    db: Session = Depends(get_db)
):
    accounts = db.query(Account).filter(Account.user_id == user_id).all()
    account_ids = [a.id for a in accounts]

    if not account_ids:
        return {"total_income": 0, "total_expense": 0, "balance": 0}

    income_query = db.query(func.coalesce(func.sum(Transaction.amount), 0)).filter(
        Transaction.account_id.in_(account_ids),
        Transaction.amount > 0
    )

    expense_query = db.query(func.coalesce(func.sum(func.abs(Transaction.amount)), 0)).filter(
        Transaction.account_id.in_(account_ids),
        Transaction.amount < 0
    )

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
    user_id: int = Query(1),
    category: str = Query(...),
    months: int = Query(6),
    db: Session = Depends(get_db)
):
    accounts = db.query(Account).filter(Account.user_id == user_id).all()
    account_ids = [a.id for a in accounts]

    if not account_ids:
        return []

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


# ================= NEW REQUIRED APIs =================

# 1. Cashflow
@router.get("/cashflow")
def get_cashflow(
    user_id: int = Query(1),
    db: Session = Depends(get_db)
):
    accounts = db.query(Account).filter(Account.user_id == user_id).all()
    account_ids = [a.id for a in accounts]

    if not account_ids:
        return []

    results = db.query(
        func.to_char(Transaction.created_at, 'YYYY-MM').label('month'),
        func.sum(
            case((Transaction.amount > 0, Transaction.amount), else_=0)
        ).label("income"),
        func.sum(
            case((Transaction.amount < 0, func.abs(Transaction.amount)), else_=0)
        ).label("expense")
    ).filter(
        Transaction.account_id.in_(account_ids)
    ).group_by(
        func.to_char(Transaction.created_at, 'YYYY-MM')
    ).order_by(
        func.to_char(Transaction.created_at, 'YYYY-MM')
    ).all()

    return [
        {
            "month": r.month,
            "income": float(r.income or 0),
            "expense": float(r.expense or 0)
        }
        for r in results
    ]


# 2. Top merchants
@router.get("/top-merchants")
def get_top_merchants(
    user_id: int = Query(1),
    db: Session = Depends(get_db)
):
    accounts = db.query(Account).filter(Account.user_id == user_id).all()
    account_ids = [a.id for a in accounts]

    if not account_ids:
        return []

    results = db.query(
        Transaction.description,
        func.sum(func.abs(Transaction.amount)).label("total_spent")
    ).filter(
        Transaction.account_id.in_(account_ids),
        Transaction.amount < 0
    ).group_by(
        Transaction.description
    ).order_by(
        func.sum(func.abs(Transaction.amount)).desc()
    ).limit(5).all()

    return [
        {
            "merchant": r.description or "Unknown",
            "total_spent": float(r.total_spent)
        }
        for r in results
    ]


# 3. Category spend
@router.get("/category-spend")
def get_category_spend(
    user_id: int = Query(1),
    db: Session = Depends(get_db)
):
    return get_spending_by_category(user_id, None, db)


@router.get("/burn-rate")
def get_burn_rate(
    user_id: int = Query(1),
    db: Session = Depends(get_db)
):
    budgets = db.query(Budget).filter(Budget.user_id == user_id).all()

    accounts = db.query(Account).filter(Account.user_id == user_id).all()
    account_ids = [a.id for a in accounts]

    result = []

    for b in budgets:
        # ✅ Correct field from your model
        budget_amount = float(b.limit_amount)

        # 🔥 Calculate spent dynamically (more accurate)
        spent = db.query(func.sum(func.abs(Transaction.amount))).filter(
    Transaction.account_id.in_(account_ids),
    Transaction.category == b.category,
    Transaction.amount < 0,
    func.to_char(Transaction.created_at, 'YYYY-MM') == b.month   # ✅ ADD THIS LINE
).scalar() or 0

        spent = float(spent)

        usage = (spent / budget_amount) * 100 if budget_amount else 0

        result.append({
            "category": b.category,
            "budget": budget_amount,
            "spent": spent,
            "usage_percent": round(usage, 2),
            "month": b.month
        })

    return result