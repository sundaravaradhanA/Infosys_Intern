from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class CategoryRuleBase(BaseModel):
    category: str
    keyword_pattern: Optional[str] = None
    merchant_pattern: Optional[str] = None
    priority: int = 0
    is_active: bool = True

class CategoryRuleCreate(CategoryRuleBase):
    pass

class CategoryRuleUpdate(BaseModel):
    category: Optional[str] = None
    keyword_pattern: Optional[str] = None
    merchant_pattern: Optional[str] = None
    priority: Optional[int] = None
    is_active: Optional[bool] = None

class CategoryRuleResponse(CategoryRuleBase):
    id: int
    user_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

# Predefined categories
PREDEFINED_CATEGORIES = [
    {"name": "Food & Dining", "icon": "restaurant", "color": "#FF6B6B"},
    {"name": "Shopping", "icon": "shopping_cart", "color": "#4ECDC4"},
    {"name": "Transportation", "icon": "car", "color": "#45B7D1"},
    {"name": "Entertainment", "icon": "film", "color": "#F7DC6F"},
    {"name": "Bills & Utilities", "icon": "lightning", "color": "#BB8FCE"},
    {"name": "Health & Fitness", "icon": "health", "color": "#85C1E2"},
    {"name": "Travel", "icon": "flight", "color": "#F8B88B"},
    {"name": "Income", "icon": "trending_up", "color": "#52C41A"},
    {"name": "Transfer", "icon": "swap", "color": "#1890FF"},
    {"name": "Other", "icon": "more_horiz", "color": "#BFBFBF"},
]
