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
