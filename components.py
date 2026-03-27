import streamlit as st

def check_password():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    if not st.session_state.authenticated:
        st.markdown("""
            <div style='text-align: center; padding: 3rem 0;'>
                <h1 style='color: #00C853; font-size: 2rem;'>💰 Finance Tracker</h1>
                <p style='color: #FAFAFA;'>Your money, your control.</p>
            </div>
        """, unsafe_allow_html=True)

        with st.form("login_form"):
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Login")
            if submitted:
                if password == st.secrets["app_password"]:
                    st.session_state.authenticated = True
                    st.rerun()
                else:
                    st.error("❌ Incorrect password")
        return False
    return True

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
                <p style='color: #888; font-size: 0.8rem;'>👤 Nick</p>
            </div>
        """, unsafe_allow_html=True)

        st.page_link("app.py", label="🏠 Log Expense")
        st.page_link("pages/1_My_Expenses.py", label="📋 My Expenses")
        st.page_link("pages/2_Dashboard.py", label="📊 Dashboard")
        st.page_link("pages/3_Reports.py", label="📧 Reports")