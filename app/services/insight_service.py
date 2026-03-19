from sqlalchemy.orm import Session
from sqlalchemy import func, case
from app.models.transaction import Transaction
from app.models.budget import Budget


# 1. Cashflow (income vs expense per month)
def get_cashflow(db: Session, user_id: int):
    data = db.query(
        func.date_trunc('month', Transaction.date).label("month"),
        func.sum(
            case((Transaction.type == "income", Transaction.amount), else_=0)
        ).label("income"),
        func.sum(
            case((Transaction.type == "expense", Transaction.amount), else_=0)
        ).label("expense")
    ).filter(
        Transaction.user_id == user_id
    ).group_by("month").all()

    return [
        {
            "month": str(row.month),
            "income": float(row.income or 0),
            "expense": float(row.expense or 0)
        }
        for row in data
    ]


# 2. Top merchants
def get_top_merchants(db: Session, user_id: int):
    data = db.query(
        Transaction.merchant,
        func.sum(Transaction.amount).label("total_spent")
    ).filter(
        Transaction.user_id == user_id,
        Transaction.type == "expense"
    ).group_by(
        Transaction.merchant
    ).order_by(
        func.sum(Transaction.amount).desc()
    ).limit(5).all()

    return [
        {
            "merchant": row.merchant,
            "total_spent": float(row.total_spent)
        }
        for row in data
    ]


# 3. Category-wise spend
def get_category_spend(db: Session, user_id: int):
    data = db.query(
        Transaction.category,
        func.sum(Transaction.amount).label("total")
    ).filter(
        Transaction.user_id == user_id,
        Transaction.type == "expense"
    ).group_by(Transaction.category).all()

    return [
        {
            "category": row.category,
            "total": float(row.total)
        }
        for row in data
    ]


# 4. Burn rate (budget usage %)
def get_burn_rate(db: Session, user_id: int):
    budgets = db.query(Budget).filter(Budget.user_id == user_id).all()

    result = []

    for b in budgets:
        spent = db.query(func.sum(Transaction.amount)).filter(
            Transaction.user_id == user_id,
            Transaction.category == b.category,
            Transaction.type == "expense"
        ).scalar() or 0

        usage = (spent / b.amount) * 100 if b.amount else 0

        result.append({
            "category": b.category,
            "budget": float(b.amount),
            "spent": float(spent),
            "usage_percent": round(usage, 2)
        })

    return result