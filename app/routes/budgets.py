from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional

from app.database import get_db
from app.models import Budget, Transaction, Account, Alert
from app.schemas.budget import BudgetCreate, BudgetUpdate, BudgetResponse, BudgetWithProgress

router = APIRouter(tags=["Budgets"])


# GET ALL BUDGETS
@router.get("/", response_model=list[BudgetWithProgress])
def get_budgets(
    user_id: int,
    month: Optional[str] = None,
    db: Session = Depends(get_db)
):

    query = db.query(Budget).filter(Budget.user_id == user_id)

    if month:
        query = query.filter(Budget.month == month)

    budgets = query.all()

    result = []

    for budget in budgets:

        # Get all accounts of this user
        accounts = db.query(Account).filter(Account.user_id == user_id).all()
        account_ids = [a.id for a in accounts]

        # Calculate spending
        spent = db.query(
            func.coalesce(func.sum(func.abs(Transaction.amount)), 0)
        ).filter(
            Transaction.account_id.in_(account_ids),
            Transaction.category == budget.category,
            Transaction.amount < 0
        ).scalar() or 0

        spent = float(spent)

        limit_amount = float(budget.limit_amount)

        # Calculate progress
        if limit_amount > 0:
            progress = (spent / limit_amount) * 100
        else:
            progress = 0

        remaining = limit_amount - spent
        is_over_budget = spent > limit_amount

        # Create alert if overspent
        if is_over_budget:

            existing_alert = db.query(Alert).filter(
                Alert.user_id == user_id,
                Alert.alert_type == "budget_exceeded",
                Alert.title.contains(budget.category)
            ).first()

            if not existing_alert:
                alert = Alert(
                    user_id=user_id,
                    title=f"Budget Exceeded: {budget.category}",
                    message=f"You spent ₹{spent:.2f} but budget was ₹{limit_amount:.2f}",
                    alert_type="budget_exceeded"
                )
                db.add(alert)
                db.commit()

        result.append(
            BudgetWithProgress(
                id=budget.id,
                user_id=budget.user_id,
                category=budget.category,
                limit_amount=limit_amount,
                spent_amount=spent,
                month=budget.month,
                progress_percentage=round(progress, 2),
                remaining_amount=round(remaining, 2),
                is_over_budget=is_over_budget
            )
        )

    return result


# CREATE BUDGET
@router.post("/", response_model=BudgetResponse)
def create_budget(budget: BudgetCreate, db: Session = Depends(get_db)):

    existing = db.query(Budget).filter(
        Budget.user_id == budget.user_id,
        Budget.category == budget.category,
        Budget.month == budget.month
    ).first()

    if existing:
        raise HTTPException(
            status_code=400,
            detail="Budget already exists for this category and month"
        )

    new_budget = Budget(
        user_id=budget.user_id,
        category=budget.category,
        limit_amount=budget.limit_amount,
        spent_amount=0,
        month=budget.month
    )

    db.add(new_budget)
    db.commit()
    db.refresh(new_budget)

    return new_budget


# UPDATE BUDGET
@router.put("/{budget_id}", response_model=BudgetResponse)
def update_budget(
    budget_id: int,
    budget: BudgetUpdate,
    user_id: int = Query(...),
    db: Session = Depends(get_db)
):

    db_budget = db.query(Budget).filter(
        Budget.id == budget_id,
        Budget.user_id == user_id
    ).first()

    if not db_budget:
        raise HTTPException(status_code=404, detail="Budget not found")

    if budget.category is not None:
        db_budget.category = budget.category

    if budget.limit_amount is not None:
        db_budget.limit_amount = budget.limit_amount

    if budget.month is not None:
        db_budget.month = budget.month

    db.commit()
    db.refresh(db_budget)

    return db_budget


# DELETE BUDGET
@router.delete("/{budget_id}")
def delete_budget(
    budget_id: int,
    user_id: int = Query(...),
    db: Session = Depends(get_db)
):

    db_budget = db.query(Budget).filter(
        Budget.id == budget_id,
        Budget.user_id == user_id
    ).first()

    if not db_budget:
        raise HTTPException(status_code=404, detail="Budget not found")

    db.delete(db_budget)
    db.commit()

    return {"message": "Budget deleted successfully"}


# RECALCULATE BUDGETS
@router.post("/recalculate")
def recalculate_budgets(
    user_id: int = Query(...),
    month: Optional[str] = None,
    db: Session = Depends(get_db)
):

    budgets = db.query(Budget).filter(Budget.user_id == user_id).all()

    if month:
        budgets = [b for b in budgets if b.month == month]

    updated = 0

    for budget in budgets:

        accounts = db.query(Account).filter(Account.user_id == user_id).all()
        account_ids = [a.id for a in accounts]

        spent = db.query(
            func.coalesce(func.sum(func.abs(Transaction.amount)), 0)
        ).filter(
            Transaction.account_id.in_(account_ids),
            Transaction.category == budget.category,
            Transaction.amount < 0
        ).scalar() or 0

        budget.spent_amount = float(spent)

        db.commit()
        updated += 1

    return {"message": f"Recalculated {updated} budgets"}