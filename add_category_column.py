from app.database import engine
import psycopg2

# Connect directly to PostgreSQL to add column
conn = psycopg2.connect(
    host="localhost",
    database="banking_db",
    user="postgres",
    password="sundar@2005"
)

cur = conn.cursor()

# Add category column if it doesn't exist
try:
    cur.execute("ALTER TABLE transactions ADD COLUMN category VARCHAR;")
    conn.commit()
    print("Added 'category' column to transactions table")
except Exception as e:
    print(f"Column might already exist: {e}")

cur.close()
conn.close()

# Now update categories
from app.database import SessionLocal
from app.models.transaction import Transaction

db = SessionLocal()
txns = db.query(Transaction).all()

categories = {
    'Salary Credit': 'Income',
    'Electricity Bill': 'Utilities',
    'Online Shopping': 'Shopping',
    'Business Credit': 'Income',
    'Vendor Payment': 'Business',
    'Rent Payment': 'Housing',
    'Grocery': 'Food',
    'Freelance Income': 'Income',
    'Mobile Recharge': 'Utilities',
    'Office Supplies': 'Business',
    'Internet Bill': 'Utilities',
    'Fuel': 'Transport',
    'Restaurant': 'Food',
    'EMI Payment': 'Finance',
    'Marketing Expenses': 'Business',
    'Insurance Premium': 'Finance',
    'Software Subscription': 'Technology'
}

for t in txns:
    if t.description in categories:
        t.category = categories[t.description]
    else:
        t.category = 'Other'
    db.add(t)

db.commit()
print(f'Updated {len(txns)} transactions with categories')
db.close()
