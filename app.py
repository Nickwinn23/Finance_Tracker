import sqlite3
import pandas as pd
import streamlit as st

st.set_page_config(layout="wide")

from components import render_sidebar, check_password
if not check_password():
    st.stop()
render_sidebar()

def init_db():
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
    conn.close()

init_db()

st.title("💰 Personal Finance Tracker")
st.header("Log an Expense")

with st.form("expense_form"):
    date = st.date_input("Date")
    description = st.text_input("Item / Description")
    category = st.selectbox("Category", [
        "Groceries",
        "Dining Out",
        "Transportation",
        "Shopping",
        "Entertainment",
        "Health & Fitness",
        "Bills & Utilities",
        "Savings",
        "Other"
    ])
    amount = st.number_input("Amount ($)", min_value=0.0, format="%.2f")
    payment_method = st.selectbox("Payment Method", [
        "Cash",
        "Credit Card",
        "Debit Card",
        "Other"
    ])
    notes = st.text_input("Notes (optional)")

    submitted = st.form_submit_button("Add Expense")

    if submitted:
        conn = sqlite3.connect("finances.db")
        c = conn.cursor()
        c.execute('''
            INSERT INTO expenses (date, description, category, amount, payment_method, notes)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (str(date), description, category, amount, payment_method, notes))
        conn.commit()
        conn.close()
        st.success(f"✅ Expense of ${amount:.2f} for '{description}' saved!")