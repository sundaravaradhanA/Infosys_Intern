"""
Seed sample data for Milestone 2 testing
Adds transactions, budgets, category rules, and alerts for user_id 1
"""
import sys
sys.path.insert(0, '.')

from app.database import SessionLocal
from app.models import Transaction, Budget, CategoryRule, Alert
from datetime import datetime, timedelta
import random

def seed_transactions():
    db = SessionLocal()
    
    # Sample transactions for user_id 1, accounts 12 and 13 - 3 months
    transactions_data = [
        # JANUARY 2026
        {"account_id": 12, "description": "January Salary", "amount": 75000.0, "category": "Income", "days_ago": 60},
        {"account_id": 12, "description": "Zomato Order", "amount": -350.0, "category": "Food & Dining", "days_ago": 55},
        {"account_id": 12, "description": "Swiggy Order", "amount": -280.0, "category": "Food & Dining", "days_ago": 52},
        {"account_id": 12, "description": "Amazon Shopping", "amount": -1500.0, "category": "Shopping", "days_ago": 50},
        {"account_id": 12, "description": "Flipkart Purchase", "amount": -900.0, "category": "Shopping", "days_ago": 48},
        {"account_id": 12, "description": "Electricity Bill", "amount": -1200.0, "category": "Bills & Utilities", "days_ago": 45},
        {"account_id": 12, "description": "Water Bill", "amount": -300.0, "category": "Bills & Utilities", "days_ago": 44},
        {"account_id": 12, "description": "Internet Bill", "amount": -799.0, "category": "Bills & Utilities", "days_ago": 43},
        {"account_id": 12, "description": "Mobile Recharge", "amount": -499.0, "category": "Bills & Utilities", "days_ago": 42},
        {"account_id": 12, "description": "Uber Ride", "amount": -180.0, "category": "Transportation", "days_ago": 40},
        {"account_id": 12, "description": "Ola Ride", "amount": -150.0, "category": "Transportation", "days_ago": 38},
        {"account_id": 12, "description": "Petrol Pump", "amount": -1800.0, "category": "Transportation", "days_ago": 35},
        {"account_id": 12, "description": "Metro Card Recharge", "amount": -500.0, "category": "Transportation", "days_ago": 33},
        {"account_id": 12, "description": "Netflix Subscription", "amount": -499.0, "category": "Entertainment", "days_ago": 30},
        {"account_id": 12, "description": "Spotify Premium", "amount": -129.0, "category": "Entertainment", "days_ago": 28},
        {"account_id": 12, "description": "Movie Tickets", "amount": -450.0, "category": "Entertainment", "days_ago": 25},
        {"account_id": 12, "description": "Gym Membership", "amount": -1500.0, "category": "Health & Fitness", "days_ago": 22},
        {"account_id": 12, "description": "Medicine Purchase", "amount": -350.0, "category": "Health & Fitness", "days_ago": 20},
        {"account_id": 13, "description": "Freelance Income", "amount": 25000.0, "category": "Income", "days_ago": 58},
        {"account_id": 13, "description": "Business Credit", "amount": 50000.0, "category": "Income", "days_ago": 55},
        {"account_id": 13, "description": "Vendor Payment", "amount": -12000.0, "category": "Shopping", "days_ago": 50},
        {"account_id": 13, "description": "Office Supplies", "amount": -2000.0, "category": "Shopping", "days_ago": 45},
        {"account_id": 13, "description": "Restaurant Dinner", "amount": -1500.0, "category": "Food & Dining", "days_ago": 42},
        {"account_id": 13, "description": "Coffee Shop", "amount": -200.0, "category": "Food & Dining", "days_ago": 40},
        {"account_id": 13, "description": "Gas Bill", "amount": -700.0, "category": "Bills & Utilities", "days_ago": 38},
        {"account_id": 13, "description": "Phone Bill", "amount": -299.0, "category": "Bills & Utilities", "days_ago": 35},
        {"account_id": 13, "description": "Car Insurance", "amount": -5000.0, "category": "Bills & Utilities", "days_ago": 30},
        {"account_id": 13, "description": "Taxi to Airport", "amount": -700.0, "category": "Transportation", "days_ago": 25},
        {"account_id": 13, "description": "Train Tickets", "amount": -1000.0, "category": "Travel", "days_ago": 22},
        {"account_id": 13, "description": "Bus Tickets", "amount": -350.0, "category": "Travel", "days_ago": 20},
        {"account_id": 13, "description": "Doctor Visit", "amount": -800.0, "category": "Health & Fitness", "days_ago": 18},
        {"account_id": 13, "description": "Dental Checkup", "amount": -1800.0, "category": "Health & Fitness", "days_ago": 15},
        
        # FEBRUARY 2026
        {"account_id": 12, "description": "February Salary", "amount": 78000.0, "category": "Income", "days_ago": 30},
        {"account_id": 12, "description": "Zomato Order", "amount": -420.0, "category": "Food & Dining", "days_ago": 28},
        {"account_id": 12, "description": "Swiggy Order", "amount": -310.0, "category": "Food & Dining", "days_ago": 25},
        {"account_id": 12, "description": "Amazon Shopping", "amount": -2500.0, "category": "Shopping", "days_ago": 22},
        {"account_id": 12, "description": "Flipkart Purchase", "amount": -1800.0, "category": "Shopping", "days_ago": 20},
        {"account_id": 12, "description": "Electricity Bill", "amount": -1500.0, "category": "Bills & Utilities", "days_ago": 18},
        {"account_id": 12, "description": "Water Bill", "amount": -350.0, "category": "Bills & Utilities", "days_ago": 17},
        {"account_id": 12, "description": "Internet Bill", "amount": -999.0, "category": "Bills & Utilities", "days_ago": 16},
        {"account_id": 12, "description": "Mobile Recharge", "amount": -599.0, "category": "Bills & Utilities", "days_ago": 15},
        {"account_id": 12, "description": "Uber Ride", "amount": -250.0, "category": "Transportation", "days_ago": 12},
        {"account_id": 12, "description": "Ola Ride", "amount": -180.0, "category": "Transportation", "days_ago": 10},
        {"account_id": 12, "description": "Petrol Pump", "amount": -2000.0, "category": "Transportation", "days_ago": 8},
        {"account_id": 12, "description": "Metro Card Recharge", "amount": -500.0, "category": "Transportation", "days_ago": 5},
        {"account_id": 12, "description": "Netflix Subscription", "amount": -499.0, "category": "Entertainment", "days_ago": 3},
        {"account_id": 12, "description": "Spotify Premium", "amount": -129.0, "category": "Entertainment", "days_ago": 2},
        {"account_id": 12, "description": "Movie Tickets", "amount": -600.0, "category": "Entertainment", "days_ago": 1},
        {"account_id": 12, "description": "Gym Membership", "amount": -1500.0, "category": "Health & Fitness", "days_ago": 0},
        {"account_id": 12, "description": "Medicine Purchase", "amount": -450.0, "category": "Health & Fitness", "days_ago": 0},
        {"account_id": 13, "description": "Freelance Income", "amount": 28000.0, "category": "Income", "days_ago": 28},
        {"account_id": 13, "description": "Business Credit", "amount": 55000.0, "category": "Income", "days_ago": 25},
        {"account_id": 13, "description": "Vendor Payment", "amount": -15000.0, "category": "Shopping", "days_ago": 22},
        {"account_id": 13, "description": "Office Supplies", "amount": -2500.0, "category": "Shopping", "days_ago": 20},
        {"account_id": 13, "description": "Restaurant Dinner", "amount": -1800.0, "category": "Food & Dining", "days_ago": 18},
        {"account_id": 13, "description": "Coffee Shop", "amount": -250.0, "category": "Food & Dining", "days_ago": 15},
        {"account_id": 13, "description": "Gas Bill", "amount": -800.0, "category": "Bills & Utilities", "days_ago": 12},
        {"account_id": 13, "description": "Phone Bill", "amount": -399.0, "category": "Bills & Utilities", "days_ago": 10},
        {"account_id": 13, "description": "Car Insurance", "amount": -5000.0, "category": "Bills & Utilities", "days_ago": 8},
        {"account_id": 13, "description": "Taxi to Airport", "amount": -800.0, "category": "Transportation", "days_ago": 5},
        {"account_id": 13, "description": "Train Tickets", "amount": -1200.0, "category": "Travel", "days_ago": 3},
        {"account_id": 13, "description": "Bus Tickets", "amount": -400.0, "category": "Travel", "days_ago": 2},
        {"account_id": 13, "description": "Doctor Visit", "amount": -1000.0, "category": "Health & Fitness", "days_ago": 1},
        {"account_id": 13, "description": "Dental Checkup", "amount": -2000.0, "category": "Health & Fitness", "days_ago": 0},
        {"account_id": 13, "description": "Concert Tickets", "amount": -3500.0, "category": "Entertainment", "days_ago": 0},
        
        # MARCH 2026
        {"account_id": 12, "description": "March Salary", "amount": 80000.0, "category": "Income", "days_ago": 0},
        {"account_id": 12, "description": "Zomato Order", "amount": -450.0, "category": "Food & Dining", "days_ago": 0},
        {"account_id": 12, "description": "Swiggy Order", "amount": -320.0, "category": "Food & Dining", "days_ago": 0},
        {"account_id": 12, "description": "Amazon Shopping", "amount": -3000.0, "category": "Shopping", "days_ago": 0},
        {"account_id": 12, "description": "Flipkart Purchase", "amount": -2000.0, "category": "Shopping", "days_ago": 0},
        {"account_id": 12, "description": "Electricity Bill", "amount": -1800.0, "category": "Bills & Utilities", "days_ago": 0},
        {"account_id": 12, "description": "Water Bill", "amount": -400.0, "category": "Bills & Utilities", "days_ago": 0},
        {"account_id": 12, "description": "Internet Bill", "amount": -1099.0, "category": "Bills & Utilities", "days_ago": 0},
        {"account_id": 12, "description": "Mobile Recharge", "amount": -699.0, "category": "Bills & Utilities", "days_ago": 0},
        {"account_id": 12, "description": "Uber Ride", "amount": -300.0, "category": "Transportation", "days_ago": 0},
        {"account_id": 12, "description": "Ola Ride", "amount": -200.0, "category": "Transportation", "days_ago": 0},
        {"account_id": 12, "description": "Petrol Pump", "amount": -2500.0, "category": "Transportation", "days_ago": 0},
        {"account_id": 12, "description": "Metro Card Recharge", "amount": -600.0, "category": "Transportation", "days_ago": 0},
        {"account_id": 12, "description": "Netflix Subscription", "amount": -499.0, "category": "Entertainment", "days_ago": 0},
        {"account_id": 12, "description": "Spotify Premium", "amount": -149.0, "category": "Entertainment", "days_ago": 0},
        {"account_id": 12, "description": "Movie Tickets", "amount": -700.0, "category": "Entertainment", "days_ago": 0},
        {"account_id": 12, "description": "Gym Membership", "amount": -1600.0, "category": "Health & Fitness", "days_ago": 0},
        {"account_id": 12, "description": "Medicine Purchase", "amount": -500.0, "category": "Health & Fitness", "days_ago": 0},
        {"account_id": 12, "description": "Flight Booking", "amount": -8500.0, "category": "Travel", "days_ago": 0},
        {"account_id": 12, "description": "Hotel Booking", "amount": -12000.0, "category": "Travel", "days_ago": 0},
        {"account_id": 13, "description": "Freelance Income", "amount": 30000.0, "category": "Income", "days_ago": 0},
        {"account_id": 13, "description": "Business Credit", "amount": 60000.0, "category": "Income", "days_ago": 0},
        {"account_id": 13, "description": "Vendor Payment", "amount": -18000.0, "category": "Shopping", "days_ago": 0},
        {"account_id": 13, "description": "Office Supplies", "amount": -3000.0, "category": "Shopping", "days_ago": 0},
        {"account_id": 13, "description": "Restaurant Dinner", "amount": -2000.0, "category": "Food & Dining", "days_ago": 0},
        {"account_id": 13, "description": "Coffee Shop", "amount": -300.0, "category": "Food & Dining", "days_ago": 0},
        {"account_id": 13, "description": "Gas Bill", "amount": -900.0, "category": "Bills & Utilities", "days_ago": 0},
        {"account_id": 13, "description": "Phone Bill", "amount": -499.0, "category": "Bills & Utilities", "days_ago": 0},
        {"account_id": 13, "description": "Car Insurance", "amount": -5500.0, "category": "Bills & Utilities", "days_ago": 0},
        {"account_id": 13, "description": "Taxi to Airport", "amount": -900.0, "category": "Transportation", "days_ago": 0},
        {"account_id": 13, "description": "Train Tickets", "amount": -1500.0, "category": "Travel", "days_ago": 0},
        {"account_id": 13, "description": "Bus Tickets", "amount": -500.0, "category": "Travel", "days_ago": 0},
        {"account_id": 13, "description": "Doctor Visit", "amount": -1200.0, "category": "Health & Fitness", "days_ago": 0},
        {"account_id": 13, "description": "Dental Checkup", "amount": -2500.0, "category": "Health & Fitness", "days_ago": 0},
        {"account_id": 13, "description": "Concert Tickets", "amount": -4000.0, "category": "Entertainment", "days_ago": 0},
        {"account_id": 13, "description": "IPL Match", "amount": -3000.0, "category": "Entertainment", "days_ago": 0},
    ]
    
    # Clear existing transactions for these accounts
    db.query(Transaction).filter(Transaction.account_id.in_([12, 13])).delete()
    
    # Add new transactions
    base_date = datetime.now()
    for txn_data in transactions_data:
        days_ago = txn_data.get("days_ago", 0)
        txn = Transaction(
            account_id=txn_data["account_id"],
            description=txn_data["description"],
            amount=txn_data["amount"],
            category=txn_data["category"],
            created_at=base_date - timedelta(days=days_ago)
        )
        db.add(txn)
    
    db.commit()
    print(f"✅ Added {len(transactions_data)} transactions")
    db.close()

def seed_budgets():
    db = SessionLocal()
    
    # Sample budgets for user_id 1 - multiple months
    budgets_data = [
        # January 2026 budgets
        {"category": "Food & Dining", "limit_amount": 5000, "month": "2026-01"},
        {"category": "Shopping", "limit_amount": 15000, "month": "2026-01"},
        {"category": "Transportation", "limit_amount": 5000, "month": "2026-01"},
        {"category": "Bills & Utilities", "limit_amount": 8000, "month": "2026-01"},
        {"category": "Entertainment", "limit_amount": 3000, "month": "2026-01"},
        {"category": "Health & Fitness", "limit_amount": 5000, "month": "2026-01"},
        {"category": "Travel", "limit_amount": 20000, "month": "2026-01"},
        
        # February 2026 budgets
        {"category": "Food & Dining", "limit_amount": 6000, "month": "2026-02"},
        {"category": "Shopping", "limit_amount": 18000, "month": "2026-02"},
        {"category": "Transportation", "limit_amount": 6000, "month": "2026-02"},
        {"category": "Bills & Utilities", "limit_amount": 9000, "month": "2026-02"},
        {"category": "Entertainment", "limit_amount": 3500, "month": "2026-02"},
        {"category": "Health & Fitness", "limit_amount": 5500, "month": "2026-02"},
        {"category": "Travel", "limit_amount": 25000, "month": "2026-02"},
        
        # March 2026 budgets
        {"category": "Food & Dining", "limit_amount": 7000, "month": "2026-03"},
        {"category": "Shopping", "limit_amount": 20000, "month": "2026-03"},
        {"category": "Transportation", "limit_amount": 7000, "month": "2026-03"},
        {"category": "Bills & Utilities", "limit_amount": 10000, "month": "2026-03"},
        {"category": "Entertainment", "limit_amount": 4000, "month": "2026-03"},
        {"category": "Health & Fitness", "limit_amount": 6000, "month": "2026-03"},
        {"category": "Travel", "limit_amount": 30000, "month": "2026-03"},
    ]
    
    # Clear existing budgets for user 1
    db.query(Budget).filter(Budget.user_id == 1).delete()
    
    # Add new budgets
    for budget_data in budgets_data:
        budget = Budget(
            user_id=1,
            category=budget_data["category"],
            limit_amount=budget_data["limit_amount"],
            spent_amount=0,
            month=budget_data["month"]
        )
        db.add(budget)
    
    db.commit()
    print(f"✅ Added {len(budgets_data)} budgets")
    db.close()

def seed_category_rules():
    db = SessionLocal()
    
    # Sample category rules for user_id 1
    rules_data = [
        {"category": "Food & Dining", "keyword_pattern": "zomato", "merchant_pattern": None, "priority": 10},
        {"category": "Food & Dining", "keyword_pattern": "swiggy", "merchant_pattern": None, "priority": 10},
        {"category": "Food & Dining", "keyword_pattern": "restaurant", "merchant_pattern": None, "priority": 5},
        {"category": "Food & Dining", "keyword_pattern": "dinner", "merchant_pattern": None, "priority": 5},
        {"category": "Food & Dining", "keyword_pattern": "coffee", "merchant_pattern": None, "priority": 5},
        {"category": "Shopping", "keyword_pattern": "amazon", "merchant_pattern": None, "priority": 10},
        {"category": "Shopping", "keyword_pattern": "flipkart", "merchant_pattern": None, "priority": 10},
        {"category": "Shopping", "keyword_pattern": "vendor", "merchant_pattern": None, "priority": 10},
        {"category": "Shopping", "keyword_pattern": "office supplies", "merchant_pattern": None, "priority": 10},
        {"category": "Bills & Utilities", "keyword_pattern": "electricity", "merchant_pattern": None, "priority": 10},
        {"category": "Bills & Utilities", "keyword_pattern": "water bill", "merchant_pattern": None, "priority": 10},
        {"category": "Bills & Utilities", "keyword_pattern": "internet", "merchant_pattern": None, "priority": 10},
        {"category": "Bills & Utilities", "keyword_pattern": "mobile recharge", "merchant_pattern": None, "priority": 10},
        {"category": "Bills & Utilities", "keyword_pattern": "gas bill", "merchant_pattern": None, "priority": 10},
        {"category": "Bills & Utilities", "keyword_pattern": "phone bill", "merchant_pattern": None, "priority": 10},
        {"category": "Bills & Utilities", "keyword_pattern": "car insurance", "merchant_pattern": None, "priority": 10},
        {"category": "Transportation", "keyword_pattern": "uber", "merchant_pattern": None, "priority": 10},
        {"category": "Transportation", "keyword_pattern": "ola", "merchant_pattern": None, "priority": 10},
        {"category": "Transportation", "keyword_pattern": "petrol", "merchant_pattern": None, "priority": 10},
        {"category": "Transportation", "keyword_pattern": "metro", "merchant_pattern": None, "priority": 10},
        {"category": "Transportation", "keyword_pattern": "taxi", "merchant_pattern": None, "priority": 10},
        {"category": "Entertainment", "keyword_pattern": "netflix", "merchant_pattern": None, "priority": 10},
        {"category": "Entertainment", "keyword_pattern": "spotify", "merchant_pattern": None, "priority": 10},
        {"category": "Entertainment", "keyword_pattern": "movie", "merchant_pattern": None, "priority": 5},
        {"category": "Entertainment", "keyword_pattern": "concert", "merchant_pattern": None, "priority": 10},
        {"category": "Entertainment", "keyword_pattern": "ipl", "merchant_pattern": None, "priority": 10},
        {"category": "Health & Fitness", "keyword_pattern": "gym", "merchant_pattern": None, "priority": 10},
        {"category": "Health & Fitness", "keyword_pattern": "medicine", "merchant_pattern": None, "priority": 10},
        {"category": "Health & Fitness", "keyword_pattern": "doctor", "merchant_pattern": None, "priority": 10},
        {"category": "Health & Fitness", "keyword_pattern": "dental", "merchant_pattern": None, "priority": 10},
        {"category": "Travel", "keyword_pattern": "flight", "merchant_pattern": None, "priority": 10},
        {"category": "Travel", "keyword_pattern": "hotel", "merchant_pattern": None, "priority": 10},
        {"category": "Travel", "keyword_pattern": "train", "merchant_pattern": None, "priority": 10},
        {"category": "Travel", "keyword_pattern": "bus", "merchant_pattern": None, "priority": 10},
    ]
    
    # Clear existing rules for user 1
    db.query(CategoryRule).filter(CategoryRule.user_id == 1).delete()
    
    # Add new rules
    for rule_data in rules_data:
        rule = CategoryRule(
            user_id=1,
            category=rule_data["category"],
            keyword_pattern=rule_data["keyword_pattern"],
            merchant_pattern=rule_data["merchant_pattern"],
            priority=rule_data["priority"],
            is_active=True
        )
        db.add(rule)
    
    db.commit()
    print(f"✅ Added {len(rules_data)} category rules")
    db.close()

def seed_alerts():
    db = SessionLocal()
    
    # Sample alerts for user_id 1
    alerts_data = [
        {
            "title": "Welcome to Budget Tracker",
            "message": "Start creating budgets to track your spending!",
            "alert_type": "info"
        },
        {
            "title": "New Category Rules Added",
            "message": "We've added auto-categorization rules for your transactions.",
            "alert_type": "info"
        },
        {
            "title": "Budget Exceeded: Shopping",
            "message": "You've exceeded your monthly budget for Shopping. Spent: ₹21,800.00, Limit: ₹10,000.00",
            "alert_type": "budget_exceeded"
        },
        {
            "title": "Budget Exceeded: Entertainment",
            "message": "You've exceeded your monthly budget for Entertainment. Spent: ₹7,228.00, Limit: ₹3,000.00",
            "alert_type": "budget_exceeded"
        },
        {
            "title": "Budget Exceeded: Bills & Utilities",
            "message": "You've exceeded your monthly budget for Bills & Utilities. Spent: ₹9,647.00, Limit: ₹8,000.00",
            "alert_type": "budget_exceeded"
        },
        {
            "title": "Budget Exceeded: Travel",
            "message": "You've exceeded your monthly budget for Travel. Spent: ₹22,100.00, Limit: ₹15,000.00",
            "alert_type": "budget_exceeded"
        },
    ]
    
    # Clear existing alerts for user 1
    db.query(Alert).filter(Alert.user_id == 1).delete()
    
    # Add new alerts
    for alert_data in alerts_data:
        alert = Alert(
            user_id=1,
            title=alert_data["title"],
            message=alert_data["message"],
            alert_type=alert_data["alert_type"],
            is_read=False
        )
        db.add(alert)
    
    db.commit()
    print(f"✅ Added {len(alerts_data)} alerts")
    db.close()

if __name__ == "__main__":
    print("Seeding comprehensive sample data for user_id 1...")
    print("-" * 50)
    seed_category_rules()
    seed_transactions()
    seed_budgets()
    seed_alerts()
    print("-" * 50)
    print("✅ Sample data seeding completed!")
    print("\nData includes:")
    print("- 3 months of transactions (January, February, March 2026)")
    print("- 21 budgets (7 per month)")
    print("- 33 category rules")
    print("- 6 alerts (including budget exceeded)")
