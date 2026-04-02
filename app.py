import streamlit as st
import sqlite3
import pandas as pd
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from utils import load_data, CATEGORY_BUCKETS, seed_sample_data
from components import render_sidebar

st.set_page_config(layout="wide", page_title="Finance Tracker", page_icon="💰")
render_sidebar()
seed_sample_data()

df = load_data()

if not df.empty:
    df["date"] = pd.to_datetime(df["date"], format='mixed')
    df["bucket"] = df["category"].map(CATEGORY_BUCKETS)
    today = pd.Timestamp.now()
    this_week = df[df["date"] >= today - pd.Timedelta(days=7)]
    this_month = df[df["date"].dt.strftime("%B %Y") == today.strftime("%B %Y")]
    last_month = df[df["date"].dt.strftime("%B %Y") == (today - pd.DateOffset(months=1)).strftime("%B %Y")]
    total = this_month["amount"].sum()
    last_total = last_month["amount"].sum()
    month_diff_pct = ((total - last_total) / last_total * 100) if last_total > 0 else 0
    week_total = this_week["amount"].sum()
    last_week = df[df["date"] >= today - pd.Timedelta(days=14)]
    last_week = last_week[last_week["date"] < today - pd.Timedelta(days=7)]
    last_week_total = last_week["amount"].sum()
    week_diff_pct = ((week_total - last_week_total) / last_week_total * 100) if last_week_total > 0 else 0
    savings_total = this_month[this_month["bucket"] == "Savings"]["amount"].sum()
    savings_pct = (savings_total / total * 100) if total > 0 else 0
else:
    week_total = month_diff_pct = week_diff_pct = savings_pct = total = 0

if "needs_pct" not in st.session_state:
    st.session_state.needs_pct = 50
if "wants_pct" not in st.session_state:
    st.session_state.wants_pct = 30
if "savings_pct_target" not in st.session_state:
    st.session_state.savings_pct_target = 20

st.markdown("""
    <style>
        .hero { text-align: center; padding: 3rem 2rem 2rem; }
        .logo-text { font-size: 48px; font-weight: 500; color: #00C853; letter-spacing: 0.12em; text-transform: uppercase; margin-bottom: 1rem; }
        .hero-title { font-size: 24px; font-weight: 500; color: #FAFAFA; line-height: 1.15; margin-bottom: 0.5rem; }
        .hero-title span { color: #00C853; }
        .hero-sub { font-size: 16px; color: #888; margin-bottom: 2rem; }
        .stat-card { background: #1A1F2E; border-radius: 12px; padding: 1.2rem; border-left: 3px solid #00C853; }
        .stat-label { font-size: 12px; color: #888; margin-bottom: 4px; }
        .stat-value { font-size: 24px; font-weight: 500; color: #00C853; }
        .stat-sub { font-size: 11px; color: #666; margin-top: 2px; }
        .feature-card { background: #1A1F2E; border-radius: 12px; padding: 1.2rem; border: 0.5px solid #2a2f3e; height: 100%; }
        .feature-title { font-size: 14px; font-weight: 500; color: #FAFAFA; margin-bottom: 4px; }
        .feature-desc { font-size: 12px; color: #888; line-height: 1.5; }
        .section-title { font-size: 18px; font-weight: 500; color: #FAFAFA; margin-bottom: 4px; }
        .section-sub { font-size: 13px; color: #888; margin-bottom: 1.5rem; }
        .divider { border: none; border-top: 0.5px solid #2a2f3e; margin: 2rem 0; }
        .finance-title { font-size: 48px; font-weight: 500; color: #00C853; text-align: center; padding: 2rem 0 0.5rem; }
        .finance-sub { font-size: 16px; color: #888; text-align: center; margin-bottom: 2rem; }
    </style>
""", unsafe_allow_html=True)

st.markdown("""
    <div class="hero">
        <div class="logo-text">💰 Finance Tracker</div>
        <div class="hero-title">Your money,<br><span>your control.</span></div>
        <div class="hero-sub">Track spending, follow your budget rule, and build better habits.</div>
    </div>
""", unsafe_allow_html=True)

st.markdown("""
    <div style='background:#1A1F2E; border-left: 3px solid #00C853; border-radius: 8px; padding: 0.8rem 1.2rem; margin-bottom: 1.5rem;'>
        <p style='color:#FAFAFA; font-size:13px; margin:0; font-weight:500;'>📊 Live Demo</p>
        <p style='color:#888; font-size:12px; margin:4px 0 0;'>This is a portfolio demo running on sample data. The full app runs locally with real personal finance data, password protection, and automated weekly email reminders.
            Feel free to explore the features!</p>
    </div>
""", unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)
with col1:
    week_arrow = "↓" if week_diff_pct < 0 else "↑"
    st.markdown(f"""
        <div class="stat-card">
            <div class="stat-label">This week</div>
            <div class="stat-value">${week_total:,.2f}</div>
            <div class="stat-sub">{week_arrow} {abs(week_diff_pct):.1f}% vs last week</div>
        </div>
    """, unsafe_allow_html=True)
with col2:
    month_arrow = "↓" if month_diff_pct < 0 else "↑"
    st.markdown(f"""
        <div class="stat-card">
            <div class="stat-label">This month</div>
            <div class="stat-value">${total:,.2f}</div>
            <div class="stat-sub">{month_arrow} {abs(month_diff_pct):.1f}% vs last month</div>
        </div>
    """, unsafe_allow_html=True)
with col3:
    st.markdown(f"""
        <div class="stat-card">
            <div class="stat-label">Savings rate</div>
            <div class="stat-value">{savings_pct:.1f}%</div>
            <div class="stat-sub">Target: {st.session_state.savings_pct_target}%</div>
        </div>
    """, unsafe_allow_html=True)

st.markdown("<hr class='divider'>", unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)
with col1:
    st.markdown("""
        <div class="feature-card">
            <div class="feature-title">📋 Log expenses</div>
            <div class="feature-desc">Quickly add expenses by category, amount, and payment method.</div>
        </div>
    """, unsafe_allow_html=True)
with col2:
    st.markdown("""
        <div class="feature-card">
            <div class="feature-title">📊 Live dashboard</div>
            <div class="feature-desc">See your spending patterns with interactive charts and insights.</div>
        </div>
    """, unsafe_allow_html=True)
with col3:
    st.markdown("""
        <div class="feature-card">
            <div class="feature-title">📧 Weekly reminders</div>
            <div class="feature-desc">Get an automatic email every Sunday to log your weekly expenses.</div>
        </div>
    """, unsafe_allow_html=True)

st.markdown("<hr class='divider'>", unsafe_allow_html=True)

st.markdown("""
    <div class="section-title">Customize your budget rule</div>
    <div class="section-sub">Adjust the sliders — they automatically balance to 100%.</div>
""", unsafe_allow_html=True)

col1, col2 = st.columns([2, 1])

with col1:
    needs = st.slider("Needs %", 0, 100, st.session_state.needs_pct, key="needs_slider")
    wants = st.slider("Wants %", 0, 100, st.session_state.wants_pct, key="wants_slider")
    savings = st.slider("Savings %", 0, 100, st.session_state.savings_pct_target, key="savings_slider")

    total_pct = needs + wants + savings

    if total_pct != 100:
        st.markdown(f"""
            <div style='color:#FF5252; font-size:12px; margin-top:4px;'>
                ⚠️ Total is {total_pct}% — adjust sliders to reach exactly 100%
            </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
            <div style='color:#00C853; font-size:12px; margin-top:4px;'>
                ✅ Total is 100%
            </div>
        """, unsafe_allow_html=True)
        st.session_state.needs_pct = needs
        st.session_state.wants_pct = wants
        st.session_state.savings_pct_target = savings

with col2:
    all_total = df["amount"].sum() if not df.empty else 0
    if not df.empty and all_total > 0:
        df_buckets = df.copy()
        df_buckets["bucket"] = df_buckets["category"].map(CATEGORY_BUCKETS)
        bucket_totals = df_buckets.groupby("bucket")["amount"].sum()
        needs_actual = (bucket_totals.get("Needs", 0) / all_total * 100)
        wants_actual = (bucket_totals.get("Wants", 0) / all_total * 100)
        savings_actual = (bucket_totals.get("Savings", 0) / all_total * 100)

        for label, actual, target, color in [
            ("Needs", needs_actual, needs, "#00C853"),
            ("Wants", wants_actual, wants, "#2196F3"),
            ("Savings", savings_actual, savings, "#FFA726")
        ]:
            if label == "Savings":
                bar_color = color if actual >= target else "#FF5252"
            else:
                bar_color = color if actual <= target else "#FF5252"
            st.markdown(f"""
                <div style='margin-bottom:12px;'>
                    <div style='display:flex; justify-content:space-between; font-size:12px; color:#888; margin-bottom:4px;'>
                        <span>{label}</span>
                        <span>{actual:.1f}% / {target}% target</span>
                    </div>
                    <div style='background:#1A1F2E; border-radius:4px; height:8px; overflow:hidden;'>
                        <div style='width:{min(actual, 100):.1f}%; background:{bar_color}; height:8px; border-radius:4px;'></div>
                    </div>
                </div>
            """, unsafe_allow_html=True)