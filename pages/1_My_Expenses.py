import streamlit as st
import sqlite3
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import load_data, filter_data, get_periods
from components import render_sidebar, check_password

st.set_page_config(layout="wide")
if not check_password():
    st.stop()
render_sidebar()

st.title("📋 My Expenses")

df = load_data()

if df.empty:
    st.info("No expenses logged yet. Head to the main page to add some!")
else:
    time_filter = st.radio("View by:", ["Weekly", "Monthly", "Yearly"], horizontal=True)
    periods = get_periods(df, time_filter)
    selected_period = st.selectbox("Select period:", periods)
    filtered_df = filter_data(df, time_filter, selected_period)

    st.write("✏️ Edit any cell directly in the table. Hit **Save Changes** when done.")

    edited_df = st.data_editor(
        filtered_df,
        use_container_width=True,
        num_rows="dynamic",
        column_config={
            "id": None,
            "date": st.column_config.DateColumn("Date"),
            "amount": st.column_config.NumberColumn("Amount ($)", format="$%.2f"),
            "category": st.column_config.SelectboxColumn("Category", options=[
                "Groceries",
                "Dining Out",
                "Transportation",
                "Shopping",
                "Entertainment",
                "Health & Fitness",
                "Bills & Utilities",
                "Savings",
                "Other"
            ]),
            "payment_method": st.column_config.SelectboxColumn("Payment Method", options=[
                "Cash",
                "Credit Card",
                "Debit Card",
                "Other"
            ]),
        }
    )

    if st.button("💾 Save Changes"):
        conn = sqlite3.connect("finances.db")
        c = conn.cursor()
        for _, row in edited_df.iterrows():
            c.execute('''
                UPDATE expenses
                SET date=?, description=?, category=?, amount=?, payment_method=?, notes=?
                WHERE id=?
            ''', (str(row["date"]), row["description"], row["category"],
                  row["amount"], row["payment_method"], row["notes"], row["id"]))
        conn.commit()
        conn.close()
        st.success("✅ Changes saved!")
        st.rerun()