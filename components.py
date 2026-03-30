import streamlit as st

def render_sidebar():
    st.markdown("""
        <style>
            [data-testid="stSidebarNav"] {
                display: none;
            }
        </style>
    """, unsafe_allow_html=True)

    with st.sidebar:
        st.markdown("""
            <div style='text-align: center; padding: 1rem 0;'>
                <h1 style='color: #00C853; font-size: 1.8rem; margin-bottom: 0;'>💰 Finance Tracker</h1>
                <p style='color: #FAFAFA; font-size: 0.85rem; margin-top: 0.2rem;'>Your money, your control.</p>
                <hr style='border-color: #00C853; margin: 0.8rem 0;'>
            </div>
        """, unsafe_allow_html=True)

        st.page_link("app.py", label="🏠 Home")
        st.page_link("pages/0_Log_Expense.py", label="📝 Log Expense")
        st.page_link("pages/1_My_Expenses.py", label="📋 My Expenses")
        st.page_link("pages/2_Dashboard.py", label="📊 Dashboard")
        st.page_link("pages/3_Reports.py", label="📧 Reports")