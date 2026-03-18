"""
Database setup script - Creates database, tables, and seed data
"""
import sys
import os
sys.path.insert(0, '.')

from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import sessionmaker
from app.database import Base
from app.models.user import User
from app.models.account import Account
from app.models.transaction import Transaction
from app.models.budget import Budget
from app.models.category_rule import CategoryRule
from app.models.alert import Alert
from app.models.bill import Bill
from app.models.reward import Reward
from app.services.security import hash_password
from datetime import datetime, timedelta
import random

# Database URL - update with your PostgreSQL credentials
DATABASE_URL = "postgresql://postgres:hasiniyelugam71025@localhost:5432/banking_db"

# Create engine
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def create_database():
    """Create the database if it doesn't exist"""
    # Connect to default postgres database to create our database
    default_db_url = "postgresql://postgres:hasiniyelugam71025@localhost:5432/postgres"
    default_engine = create_engine(default_db_url)
    
    with default_engine.connect() as conn:
        # Check if database exists
        result = conn.execute(text("SELECT 1 FROM pg_database WHERE datname = 'banking_db'"))
        if not result.fetchone():
            conn.execute(text("CREATE DATABASE banking_db"))
            print("✅ Database 'banking_db' created")
        else:
            print("✅ Database 'banking_db' already exists")
    default_engine.dispose()

def create_tables():
    """Drop and recreate all database tables"""
    # Drop all existing tables
    print("🔄 Dropping existing tables...")
    Base.metadata.drop_all(bind=engine)
    print("🔄 Creating tables...")
    Base.metadata.create_all(bind=engine)
    print("✅ All tables created successfully")

def seed_data():
    """Seed all data in a single session"""
    db = SessionLocal()
    
    # Create users data
    users_data = [
        {
            "name": "Hasini Yelugam",
            "email": "hasini@gmail.com",
            "password": "1234",
            "phone": "7842549340",
            "kyc_status": "Verified"
        },
        {
            "name": "John Smith",
            "email": "john.smith@email.com",
            "password": "password123",
            "phone": "9876543210",
            "kyc_status": "Verified"
        },
        {
            "name": "Sarah Johnson",
            "email": "sarah.j@email.com",
            "password": "sarah2024",
            "phone": "9123456789",
            "kyc_status": "Verified"
        },
        {
            "name": "Mike Wilson",
            "email": "mike.wilson@email.com",
            "password": "mike123",
            "phone": "9988776655",
            "kyc_status": "Pending"
        },
        {
            "name": "Emily Davis",
            "email": "emily.davis@email.com",
            "password": "emily2024",
            "phone": "9876123456",
            "kyc_status": "Verified"
        },
    ]
    
    users = []
    for user_data in users_data:
        user_data["password"] = hash_password(user_data["password"])
        user = User(**user_data)
        db.add(user)
        users.append(user)
    
    db.commit()
    print(f"✅ Added {len(users)} users")
    
    # Refresh to get IDs
    for user in users:
        db.refresh(user)
    
    # Create accounts for each user
    accounts_data = []
    account_types = ["Savings", "Checking", "Business", "Credit Card"]
    bank_names = ["State Bank of India", "HDFC Bank", "ICICI Bank", "Axis Bank", "Punjab National Bank"]
    
    for user in users:
        # Each user gets 2-3 accounts
        num_accounts = random.randint(2, 3)
        for i in range(num_accounts):
            account = Account(
                user_id=user.id,
                bank_name=bank_names[len(accounts_data) % len(bank_names)],
                account_type=account_types[len(accounts_data) % len(account_types)],
                balance=random.randint(10000, 500000)
            )
            db.add(account)
            accounts_data.append(account)
    
    db.commit()
    print(f"✅ Added {len(accounts_data)} accounts")
    
    # Refresh accounts to get IDs
    for account in accounts_data:
        db.refresh(account)
    
    # Seed transactions
    categories = [
        "Income", "Food & Dining", "Shopping", "Bills & Utilities",
        "Transportation", "Entertainment", "Health & Fitness", "Travel",
        "Groceries", "Education", "Investments", "Transfer"
    ]
    
    merchants = {
        "Income": ["Salary", "Freelance", "Business Credit", "Investment Returns", "Dividend"],
        "Food & Dining": ["Zomato", "Swiggy", "Domino's", "Restaurant", "Coffee Shop", "McDonald's", "KFC"],
        "Shopping": ["Amazon", "Flipkart", "Myntra", "Reliance Digital", "Shopify Store"],
        "Bills & Utilities": ["Electricity Bill", "Water Bill", "Internet Bill", "Mobile Recharge", "Gas Bill", "DTH Recharge"],
        "Transportation": ["Uber", "Ola", "Petrol Pump", "Metro Card", "Parking", "Taxi"],
        "Entertainment": ["Netflix", "Spotify", "Movie Tickets", "Concerts", "Gaming", "Amazon Prime"],
        "Health & Fitness": ["Gym Membership", "Medicine", "Doctor Visit", "Health Insurance", "Dental"],
        "Travel": ["Flight Booking", "Hotel Booking", "Train Tickets", "Bus Tickets", "Cab Booking"],
        "Groceries": ["BigBasket", "Zepto", "DMart", "Reliance Fresh", "Nature's Basket"],
        "Education": ["Coursera", "Udemy", "Books", "Tuition", "Online Course"],
        "Investments": ["SIP", "FD", "RD", "Stocks", "Mutual Fund"],
        "Transfer": ["UPI Transfer", "NEFT", "IMPS", "Wallet Load"]
    }
    
    # Generate transactions for the past 6 months
    base_date = datetime.now()
    transactions_count = 0
    
    for account in accounts_data:
        # Generate 15-30 transactions per account
        num_transactions = random.randint(15, 30)
        
        for i in range(num_transactions):
            # Random category
            category = random.choice(categories)
            
            # Decide if income or expense (15% chance of income)
            is_income = random.random() < 0.15
            
            if is_income:
                amount = random.uniform(5000, 100000)
            else:
                if category == "Income":
                    amount = -random.uniform(5000, 100000)
                else:
                    amount = -random.uniform(100, 15000)
            
            # Random merchant
            merchant = random.choice(merchants.get(category, ["General"]))
            
            # Random date within last 6 months
            days_ago = random.randint(0, 180)
            
            txn = Transaction(
                account_id=account.id,
                description=merchant,
                amount=round(amount, 2),
                category=category,
                created_at=base_date - timedelta(days=days_ago)
            )
            db.add(txn)
            transactions_count += 1
    
    db.commit()
    print(f"✅ Added {transactions_count} transactions")
    
    # Seed budgets
    budget_categories = [
        "Food & Dining", "Shopping", "Bills & Utilities", "Transportation",
        "Entertainment", "Health & Fitness", "Travel", "Groceries", "Education"
    ]
    
    months = ["2026-01", "2026-02", "2026-03"]
    
    for user in users:
        for month in months:
            # Create 5-7 budgets per user per month
            num_budgets = random.randint(5, 7)
            selected_categories = random.sample(budget_categories, num_budgets)
            
            for category in selected_categories:
                budget = Budget(
                    user_id=user.id,
                    category=category,
                    limit_amount=random.randint(3000, 25000),
                    spent_amount=random.randint(0, 15000),
                    month=month
                )
                db.add(budget)
    
    db.commit()
    print(f"✅ Added budgets for all users")
    
    # Seed category rules
    rules_data = [
        {"category": "Food & Dining", "keyword_pattern": "zomato", "priority": 10},
        {"category": "Food & Dining", "keyword_pattern": "swiggy", "priority": 10},
        {"category": "Food & Dining", "keyword_pattern": "restaurant", "priority": 5},
        {"category": "Food & Dining", "keyword_pattern": "domino", "priority": 10},
        {"category": "Shopping", "keyword_pattern": "amazon", "priority": 10},
        {"category": "Shopping", "keyword_pattern": "flipkart", "priority": 10},
        {"category": "Shopping", "keyword_pattern": "myntra", "priority": 10},
        {"category": "Bills & Utilities", "keyword_pattern": "electricity", "priority": 10},
        {"category": "Bills & Utilities", "keyword_pattern": "water bill", "priority": 10},
        {"category": "Bills & Utilities", "keyword_pattern": "internet", "priority": 10},
        {"category": "Transportation", "keyword_pattern": "uber", "priority": 10},
        {"category": "Transportation", "keyword_pattern": "ola", "priority": 10},
        {"category": "Transportation", "keyword_pattern": "petrol", "priority": 10},
        {"category": "Entertainment", "keyword_pattern": "netflix", "priority": 10},
        {"category": "Entertainment", "keyword_pattern": "spotify", "priority": 10},
        {"category": "Entertainment", "keyword_pattern": "movie", "priority": 5},
        {"category": "Health & Fitness", "keyword_pattern": "gym", "priority": 10},
        {"category": "Health & Fitness", "keyword_pattern": "medicine", "priority": 10},
        {"category": "Health & Fitness", "keyword_pattern": "doctor", "priority": 10},
        {"category": "Travel", "keyword_pattern": "flight", "priority": 10},
        {"category": "Travel", "keyword_pattern": "hotel", "priority": 10},
        {"category": "Travel", "keyword_pattern": "train", "priority": 10},
        {"category": "Groceries", "keyword_pattern": "bigbasket", "priority": 10},
        {"category": "Groceries", "keyword_pattern": "zepto", "priority": 10},
        {"category": "Education", "keyword_pattern": "coursera", "priority": 10},
        {"category": "Education", "keyword_pattern": "udemy", "priority": 10},
    ]
    
    for user in users:
        for rule_data in rules_data:
            rule = CategoryRule(
                user_id=user.id,
                category=rule_data["category"],
                keyword_pattern=rule_data["keyword_pattern"],
                priority=rule_data["priority"],
                is_active=True
            )
            db.add(rule)
    
    db.commit()
    print(f"✅ Added category rules for all users")
    
    # Seed alerts
    alert_templates = [
        {"title": "Welcome to Digital Banking!", "message": "Thank you for joining us. Start tracking your finances today!", "alert_type": "info"},
        {"title": "New Feature Available", "message": "Check out our new budget tracking feature!", "alert_type": "info"},
        {"title": "Account Balance Low", "message": "Your account balance is below ₹5,000. Please recharge soon.", "alert_type": "warning"},
        {"title": "Budget Exceeded", "message": "You've exceeded your monthly budget for Shopping.", "alert_type": "budget_exceeded"},
        {"title": "Transaction Alert", "message": "A new transaction of ₹500 was made from your account.", "alert_type": "transaction"},
        {"title": "Reward Points Earned", "message": "You've earned 100 reward points! Check your rewards section.", "alert_type": "reward"},
    ]
    
    for user in users:
        # Add 3-5 alerts per user
        num_alerts = random.randint(3, 5)
        selected_alerts = random.sample(alert_templates, num_alerts)
        
        for alert_data in selected_alerts:
            alert = Alert(
                user_id=user.id,
                title=alert_data["title"],
                message=alert_data["message"],
                alert_type=alert_data["alert_type"],
                is_read=random.choice([True, False])
            )
            db.add(alert)
    
    db.commit()
    print(f"✅ Added alerts for all users")
    
    # Seed rewards
    rewards_data = [
        {"points": 500, "description": "Sign-up Bonus"},
        {"points": 200, "description": "First Transaction"},
        {"points": 100, "description": "Daily Login"},
        {"points": 300, "description": "Budget Created"},
        {"points": 150, "description": "Profile Updated"},
    ]
    
    for user in users:
        for reward_data in rewards_data:
            earned_date = datetime.now() - timedelta(days=random.randint(1, 60))
            expires_date = earned_date + timedelta(days=365)
            reward = Reward(
                user_id=user.id,
                points=reward_data["points"],
                description=reward_data["description"],
                earned_date=earned_date,
                expires_date=expires_date
            )
            db.add(reward)
    
    db.commit()
    print(f"✅ Added rewards for all users")
    
    db.close()
    return len(users)

if __name__ == "__main__":
    print("=" * 60)
    print("DATABASE SETUP - Creating Banking Database")
    print("=" * 60)
    
    # Step 1: Create database
    print("\n📦 Step 1: Creating Database...")
    create_database()
    
    # Step 2: Create tables
    print("\n📋 Step 2: Creating Tables...")
    create_tables()
    
    # Step 3: Seed all data
    print("\n🌱 Step 3: Seeding Data...")
    num_users = seed_data()
    
    print("\n" + "=" * 60)
    print("✅ DATABASE SETUP COMPLETED SUCCESSFULLY!")
    print("=" * 60)
    print("\nYour Login Credentials:")
    print("  Email: hasini@gmail.com")
    print("  Password: 1234")
    print("  Full Name: Hasini Yelugam")
    print("  Phone: 7842549340")
    print("\nThe database now contains:")
    print(f"  - {num_users} users (including your account)")
    print("  - Multiple accounts per user")
    print("  - Hundreds of transactions across 6 months")
    print("  - Budgets for multiple months")
    print("  - Category rules for auto-categorization")
    print("  - Alerts and rewards")
    print("=" * 60)
