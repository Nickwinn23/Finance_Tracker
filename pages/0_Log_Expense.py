import streamlit as st
import sqlite3
import pandas as pd
from datetime import date as date_type
from components import render_sidebar

st.set_page_config(layout="wide")
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
st.header("Log Expenses")

CATEGORIES = [
    "Groceries", "Dining Out", "Transportation", "Shopping",
    "Entertainment", "Health & Fitness", "Bills & Utilities", "Savings", "Other"
]
PAYMENT_METHODS = ["Cash", "Credit Card", "Debit Card", "Other"]

if "expense_rows" not in st.session_state:
    st.session_state.expense_rows = [{"date": date_type.today(), "description": "", "category": "Groceries", "amount": 0.0, "payment_method": "Cash", "notes": ""}]

def add_row():
    st.session_state.expense_rows.append({"date": date_type.today(), "description": "", "category": "Groceries", "amount": 0.0, "payment_method": "Cash", "notes": ""})

def remove_row(index):
    st.session_state.expense_rows.pop(index)
    st.rerun()

for i, row in enumerate(st.session_state.expense_rows):
    with st.container():
        st.markdown(f"**Expense {i + 1}**")
        col1, col2, col3, col4, col5, col6, col7 = st.columns([2, 3, 2, 2, 2, 2, 1])
        with col1:
            st.session_state.expense_rows[i]["date"] = st.date_input("Date", value=row["date"], key=f"date_{i}")
        with col2:
            st.session_state.expense_rows[i]["description"] = st.text_input("Description", value=row["description"], key=f"desc_{i}")
        with col3:
            st.session_state.expense_rows[i]["category"] = st.selectbox("Category", CATEGORIES, index=CATEGORIES.index(row["category"]), key=f"cat_{i}")
        with col4:
            st.session_state.expense_rows[i]["amount"] = st.number_input("Amount ($)", min_value=0.0, value=row["amount"], format="%.2f", key=f"amt_{i}")
        with col5:
            st.session_state.expense_rows[i]["payment_method"] = st.selectbox("Payment", PAYMENT_METHODS, index=PAYMENT_METHODS.index(row["payment_method"]), key=f"pay_{i}")
        with col6:
            st.session_state.expense_rows[i]["notes"] = st.text_input("Notes", value=row["notes"], key=f"notes_{i}")
        with col7:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("🗑️", key=f"del_{i}", help="Remove this row"):
                remove_row(i)
        st.markdown("---")

col1, col2 = st.columns([1, 5])
with col1:
    st.button("➕ Add Row", on_click=add_row)
with col2:
    if st.button("💾 Save All Expenses"):
        conn = sqlite3.connect("finances.db")
        c = conn.cursor()
        saved = 0
        for row in st.session_state.expense_rows:
            if row["description"] and row["amount"] > 0:
                c.execute('''
                    INSERT INTO expenses (date, description, category, amount, payment_method, notes)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (str(row["date"]), row["description"], row["category"], row["amount"], row["payment_method"], row["notes"]))
                saved += 1
        conn.commit()
        conn.close()
        st.session_state.expense_rows = [{"date": date_type.today(), "description": "", "category": "Groceries", "amount": 0.0, "payment_method": "Cash", "notes": ""}]
        st.success(f"✅ {saved} expense(s) saved successfully!")
        st.rerun()