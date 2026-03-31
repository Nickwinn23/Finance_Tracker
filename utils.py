import pandas as pd
import sqlite3

CATEGORY_BUCKETS = {
    "Groceries": "Needs",
    "Transportation": "Needs",
    "Health & Fitness": "Needs",
    "Bills & Utilities": "Needs",
    "Dining Out": "Wants",
    "Entertainment": "Wants",
    "Shopping": "Wants",
    "Savings": "Savings",
    "Other": "Needs"
}

@st.cache_data
def load_data():
    conn = sqlite3.connect("finances.db")
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            description TEXT,
            category TEXT,
            amount REAL,
            payment_method TEXT,
            notes TEXT
        )
    ''')
    conn.commit()
    df = pd.read_sql_query("SELECT * FROM expenses ORDER BY date DESC", conn)
    conn.close()
    if not df.empty:
        df["date"] = pd.to_datetime(df["date"], format='mixed').dt.date
    return df

def seed_sample_data():
    conn = sqlite3.connect("finances.db")
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS expenses (id INTEGER PRIMARY KEY AUTOINCREMENT, date TEXT, description TEXT, category TEXT, amount REAL, payment_method TEXT, notes TEXT)")
    conn.commit()
    c.execute("SELECT COUNT(*) FROM expenses")
    count = c.fetchone()[0]

    if True:
        c.execute("DELETE FROM expenses")
        import random
        from datetime import date, timedelta
        sample_expenses = [
            ("Groceries", 85.50, "Debit Card", "Groceries"),
            ("Rent", 1500.00, "Credit Card", "Bills & Utilities"),
            ("Netflix", 15.99, "Credit Card", "Entertainment"),
            ("Gym membership", 30.00, "Credit Card", "Health & Fitness"),
            ("Dining Out", 45.00, "Credit Card", "Dining Out"),
            ("Groceries", 92.30, "Debit Card", "Groceries"),
            ("Uber", 18.50, "Credit Card", "Transportation"),
            ("Shopping", 120.00, "Credit Card", "Shopping"),
            ("Electric bill", 95.00, "Debit Card", "Bills & Utilities"),
            ("Savings", 200.00, "Debit Card", "Savings"),
            ("Dining Out", 38.00, "Cash", "Dining Out"),
            ("Groceries", 76.40, "Debit Card", "Groceries"),
            ("Entertainment", 55.00, "Credit Card", "Entertainment"),
            ("Transportation", 45.00, "Debit Card", "Transportation"),
            ("Shopping", 89.99, "Credit Card", "Shopping"),
            ("Savings", 150.00, "Debit Card", "Savings"),
            ("Dining Out", 62.00, "Credit Card", "Dining Out"),
            ("Groceries", 110.20, "Debit Card", "Groceries"),
            ("Health & Fitness", 25.00, "Cash", "Health & Fitness"),
            ("Bills & Utilities", 80.00, "Debit Card", "Bills & Utilities"),
        ]
        today = date.today()
        for description, amount, payment, category in sample_expenses:
            expense_date = today - timedelta(days=random.randint(0, 60))
            c.execute('''
                INSERT INTO expenses (date, description, category, amount, payment_method, notes)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (str(expense_date), description, category, amount, payment, "Sample data"))
        conn.commit()
    conn.close()

def get_week_label(date):
    start = date - pd.Timedelta(days=date.dayofweek)
    end = start + pd.Timedelta(days=6)
    return f"{start.strftime('%b %d')} - {end.strftime('%b %d, %Y')}"

def filter_data(df, time_filter, selected_period):
    if df.empty:
        return df

    df = df.copy()
    df["date"] = pd.to_datetime(df["date"], format='mixed')

    if time_filter == "Weekly":
        df["period"] = df["date"].apply(get_week_label)
    elif time_filter == "Monthly":
        df["period"] = df["date"].dt.strftime("%B %Y")
    elif time_filter == "Yearly":
        df["period"] = df["date"].dt.strftime("%Y")

    return df[df["period"] == selected_period].drop(columns=["period"])

def get_periods(df, time_filter):
    if df.empty:
        return []

    df = df.copy()
    df["date"] = pd.to_datetime(df["date"], format='mixed')

    if time_filter == "Weekly":
        df["week_start"] = df["date"] - pd.to_timedelta(df["date"].dt.dayofweek, unit='d')
        df["period"] = df["date"].apply(get_week_label)
        order = df.drop_duplicates("period").sort_values("week_start", ascending=False)
        return order["period"].tolist()
    elif time_filter == "Monthly":
        df["month_start"] = df["date"].dt.to_period("M").dt.to_timestamp()
        df["period"] = df["date"].dt.strftime("%B %Y")
        order = df.drop_duplicates("period").sort_values("month_start", ascending=False)
        return order["period"].tolist()
    elif time_filter == "Yearly":
        periods = df["date"].dt.strftime("%Y")
        return sorted(periods.unique().tolist(), reverse=True)