import sqlite3
import random
from datetime import date, timedelta

categories = {
    "Groceries": "Needs",
    "Transportation": "Needs",
    "Health & Fitness": "Needs",
    "Bills & Utilities": "Needs",
    "Dining Out": "Wants",
    "Entertainment": "Wants",
    "Shopping": "Wants",
    "Savings": "Savings"
}

sample_expenses = [
    ("Groceries", 85.50, "Debit Card"),
    ("Rent", 1500.00, "Credit Card"),
    ("Netflix", 15.99, "Credit Card"),
    ("Gym membership", 30.00, "Credit Card"),
    ("Dining Out", 45.00, "Credit Card"),
    ("Groceries", 92.30, "Debit Card"),
    ("Uber", 18.50, "Credit Card"),
    ("Shopping", 120.00, "Credit Card"),
    ("Electric bill", 95.00, "Debit Card"),
    ("Savings", 200.00, "Debit Card"),
    ("Dining Out", 38.00, "Cash"),
    ("Groceries", 76.40, "Debit Card"),
    ("Entertainment", 55.00, "Credit Card"),
    ("Transportation", 45.00, "Debit Card"),
    ("Shopping", 89.99, "Credit Card"),
    ("Savings", 150.00, "Debit Card"),
    ("Dining Out", 62.00, "Credit Card"),
    ("Groceries", 110.20, "Debit Card"),
    ("Health & Fitness", 25.00, "Cash"),
    ("Bills & Utilities", 80.00, "Debit Card"),
]

conn = sqlite3.connect("finances.db")
c = conn.cursor()

today = date.today()
for i, (description, amount, payment) in enumerate(sample_expenses):
    expense_date = today - timedelta(days=random.randint(0, 60))
    category = next((cat for cat in categories if cat.lower() in description.lower()), "Groceries")
    c.execute('''
        INSERT INTO expenses (date, description, category, amount, payment_method, notes)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (str(expense_date), description, category, amount, payment, "Sample data"))

conn.commit()
conn.close()
print("Sample data created successfully!")