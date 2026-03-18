from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models import CategoryRule
from app.schemas.category_rule import (
    CategoryRuleCreate, 
    CategoryRuleUpdate, 
    CategoryRuleResponse,
    PREDEFINED_CATEGORIES
)

router = APIRouter()

@router.get("/categories")
def get_predefined_categories():
    """Get list of predefined categories"""
    return PREDEFINED_CATEGORIES

@router.get("/categories/rules", response_model=List[CategoryRuleResponse])
def get_category_rules(db: Session = Depends(get_db), user_id: int = 1):
    """Get all category rules for a user"""
    rules = db.query(CategoryRule).filter(CategoryRule.user_id == user_id).all()
    return rules

@router.post("/categories/rules", response_model=CategoryRuleResponse)
def create_category_rule(rule: CategoryRuleCreate, db: Session = Depends(get_db), user_id: int = 1):
    """Create a new category rule"""
    new_rule = CategoryRule(
        user_id=user_id,
        category=rule.category,
        keyword_pattern=rule.keyword_pattern,
        merchant_pattern=rule.merchant_pattern,
        priority=rule.priority,
        is_active=rule.is_active
    )
    db.add(new_rule)
    db.commit()
    db.refresh(new_rule)
    return new_rule

@router.put("/categories/rules/{rule_id}", response_model=CategoryRuleResponse)
def update_category_rule(rule_id: int, rule: CategoryRuleUpdate, db: Session = Depends(get_db)):
    """Update an existing category rule"""
    db_rule = db.query(CategoryRule).filter(CategoryRule.id == rule_id).first()
    if not db_rule:
        raise HTTPException(status_code=404, detail="Category rule not found")
    
    if rule.category is not None:
        db_rule.category = rule.category
    if rule.keyword_pattern is not None:
        db_rule.keyword_pattern = rule.keyword_pattern
    if rule.merchant_pattern is not None:
        db_rule.merchant_pattern = rule.merchant_pattern
    if rule.priority is not None:
        db_rule.priority = rule.priority
    if rule.is_active is not None:
        db_rule.is_active = rule.is_active
    
    db.commit()
    db.refresh(db_rule)
    return db_rule

@router.delete("/categories/rules/{rule_id}")
def delete_category_rule(rule_id: int, db: Session = Depends(get_db)):
    """Delete a category rule"""
    db_rule = db.query(CategoryRule).filter(CategoryRule.id == rule_id).first()
    if not db_rule:
        raise HTTPException(status_code=404, detail="Category rule not found")
    
    db.delete(db_rule)
    db.commit()
    return {"message": "Category rule deleted successfully"}
