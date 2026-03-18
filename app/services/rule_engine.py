"""
Rule Engine Service for Automatic Transaction Categorization
Handles priority-based matching with keyword and merchant patterns
"""
from sqlalchemy.orm import Session
from app.models import CategoryRule
from typing import Optional, List
import logging

logger = logging.getLogger(__name__)


class RuleEngine:
    """Handles automatic transaction categorization based on rules"""
    
    # Default categories when no rule matches
    DEFAULT_CATEGORY = "Uncategorized"
    
    # Priority levels for rule matching
    PRIORITY_EXACT_MERCHANT = 100
    PRIORITY_PARTIAL_MERCHANT = 75
    PRIORITY_EXACT_KEYWORD = 50
    PRIORITY_PARTIAL_KEYWORD = 25
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_all_active_rules(self, user_id: int) -> List[CategoryRule]:
        """Fetch all active rules for a user, ordered by priority (descending)"""
        return self.db.query(CategoryRule).filter(
            CategoryRule.user_id == user_id,
            CategoryRule.is_active == True
        ).order_by(CategoryRule.priority.desc()).all()
    
    def match_rule(self, description: str, merchant: Optional[str] = None, user_id: int = 1) -> Optional[str]:
        """
        Match a transaction against user's rules
        Returns the matched category or None
        """
        if not description and not merchant:
            return self.DEFAULT_CATEGORY
        
        # Normalize inputs
        description = description.lower().strip() if description else ""
        merchant = merchant.lower().strip() if merchant else ""
        
        # Get all rules for user
        rules = self.get_all_active_rules(user_id)
        
        matched_category = None
        highest_priority = -1
        
        for rule in rules:
            rule_priority = rule.priority or 0
            
            # Check merchant pattern (higher priority)
            if rule.merchant_pattern:
                merchant_pattern = rule.merchant_pattern.lower().strip()
                
                # Exact merchant match
                if merchant and merchant == merchant_pattern:
                    if rule_priority > highest_priority:
                        matched_category = rule.category
                        highest_priority = rule_priority
                # Partial merchant match
                elif merchant and merchant_pattern in merchant:
                    if rule_priority > highest_priority:
                        matched_category = rule.category
                        highest_priority = rule_priority
                # Also check in description
                elif merchant_pattern in description:
                    if rule_priority > highest_priority:
                        matched_category = rule.category
                        highest_priority = rule_priority
            
            # Check keyword pattern
            if rule.keyword_pattern:
                keyword_pattern = rule.keyword_pattern.lower().strip()
                
                # Exact keyword match
                if keyword_pattern == description:
                    if rule_priority > highest_priority:
                        matched_category = rule.category
                        highest_priority = rule_priority
                # Partial keyword match
                elif keyword_pattern in description:
                    if rule_priority > highest_priority:
                        matched_category = rule.category
                        highest_priority = rule_priority
        
        if matched_category:
            logger.info(f"Rule matched: '{description}' -> '{matched_category}' (priority: {highest_priority})")
            return matched_category
        
        logger.info(f"No rule matched for: '{description}', returning default")
        return self.DEFAULT_CATEGORY
    
    def categorize_transaction(self, description: str, merchant: Optional[str] = None, user_id: int = 1) -> str:
        """
        Main entry point for categorizing a transaction
        Returns the category string
        """
        category = self.match_rule(description, merchant, user_id)
        return category if category else self.DEFAULT_CATEGORY
    
    def create_rule(
        self,
        user_id: int,
        category: str,
        keyword_pattern: Optional[str] = None,
        merchant_pattern: Optional[str] = None,
        priority: int = 0
    ) -> CategoryRule:
        """Create a new category rule"""
        # Auto-set priority if not provided
        if priority == 0:
            if merchant_pattern:
                priority = self.PRIORITY_PARTIAL_MERCHANT
            elif keyword_pattern:
                priority = self.PRIORITY_PARTIAL_KEYWORD
        
        rule = CategoryRule(
            user_id=user_id,
            category=category,
            keyword_pattern=keyword_pattern,
            merchant_pattern=merchant_pattern,
            priority=priority,
            is_active=True
        )
        
        self.db.add(rule)
        self.db.commit()
        self.db.refresh(rule)
        
        logger.info(f"Created category rule: {category} with keyword='{keyword_pattern}', merchant='{merchant_pattern}'")
        return rule
    
    def delete_rule(self, rule_id: int, user_id: int) -> bool:
        """Delete a category rule"""
        rule = self.db.query(CategoryRule).filter(
            CategoryRule.id == rule_id,
            CategoryRule.user_id == user_id
        ).first()
        
        if rule:
            self.db.delete(rule)
            self.db.commit()
            logger.info(f"Deleted category rule: {rule_id}")
            return True
        return False
    
    def update_rule(self, rule_id: int, user_id: int, **kwargs) -> Optional[CategoryRule]:
        """Update an existing rule"""
        rule = self.db.query(CategoryRule).filter(
            CategoryRule.id == rule_id,
            CategoryRule.user_id == user_id
        ).first()
        
        if not rule:
            return None
        
        for key, value in kwargs.items():
            if hasattr(rule, key) and value is not None:
                setattr(rule, key, value)
        
        self.db.commit()
        self.db.refresh(rule)
        
        logger.info(f"Updated category rule: {rule_id}")
        return rule


# Standalone function for use in routes
def auto_categorize(description: str, merchant: Optional[str] = None, user_id: int = 1, db: Session = None) -> str:
    """
    Standalone function to categorize a transaction
    Can be used directly without instantiating the class
    """
    if db is None:
        from app.database import SessionLocal
        db = SessionLocal()
        should_close = True
    else:
        should_close = False
    
    try:
        engine = RuleEngine(db)
        return engine.categorize_transaction(description, merchant, user_id)
    finally:
        if should_close:
            db.close()
