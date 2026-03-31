import streamlit as st
import smtplib
import json
import schedule
import time
import threading
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import load_data, get_week_label, CATEGORY_BUCKETS
from components import render_sidebar

st.set_page_config(layout="wide")
render_sidebar()

def load_config():
    with open("config.json", "r") as f:
        return json.load(f)

def send_email(config):
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart
    msg = MIMEMultipart()
    msg["From"] = config["email"]
    msg["To"] = config["recipient_email"]
    msg["Subject"] = "💰 Time to log your weekly expenses!"
    body = f"""
    Hi there!

    This is your weekly reminder to log your expenses.

    Click the link below to open your Finance Tracker and log this week's spending:

    {config["app_url"]}

    Happy tracking!
    """
    msg.attach(MIMEText(body, "plain"))
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(config["email"], config["app_password"])
        server.sendmail(config["email"], config["recipient_email"], msg.as_string())

def run_scheduler(config):
    schedule.every().sunday.at("09:00").do(send_email, config=config)
    while True:
        schedule.run_pending()
        time.sleep(60)

st.title("📧 Reports & Trends")

# --- Email Setup ---
try:
    config = load_config()
    st.header("⚙️ Email Settings")
    st.info(f"Sending reminders from: **{config['email']}** to **{config['recipient_email']}**")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("▶️ Enable Weekly Reminder"):
            if "scheduler_running" not in st.session_state:
                st.session_state.scheduler_running = True
                thread = threading.Thread(target=run_scheduler, args=(config,), daemon=True)
                thread.start()
                st.success("✅ Weekly reminder enabled! You'll get an email every Sunday at 9:00 AM.")
            else:
                st.warning("Scheduler is already running!")
    with col2:
        if st.button("📨 Send Test Email Now"):
            with st.spinner("Sending..."):
                try:
                    send_email(config)
                    st.success("✅ Test email sent! Check your inbox.")
                except Exception as e:
                    st.error(f"❌ Failed to send email: {e}")
except FileNotFoundError:
    st.info("ℹ️ Email reminders are configured via GitHub Actions. No setup needed here.")

st.divider()

# --- Load Data ---
df = load_data()

if df.empty:
    st.info("No expenses logged yet. Head to the main page to add some!")
else:
    df["date"] = pd.to_datetime(df["date"], format='mixed')
    df["week"] = df["date"].apply(get_week_label)
    df["week_start"] = df["date"] - pd.to_timedelta(df["date"].dt.dayofweek, unit='d')
    df["month"] = df["date"].dt.strftime("%B %Y")
    df["month_start"] = df["date"].dt.to_period("M").dt.to_timestamp()
    df["bucket"] = df["category"].map(CATEGORY_BUCKETS)

    today = pd.Timestamp.now()
    current_week_label = get_week_label(today)
    current_month = today.strftime("%B %Y")
    last_week_label = get_week_label(today - pd.Timedelta(weeks=1))
    last_month = (today - pd.DateOffset(months=1)).strftime("%B %Y")

    this_week_df = df[df["week"] == current_week_label]
    last_week_df = df[df["week"] == last_week_label]
    this_month_df = df[df["month"] == current_month]
    last_month_df = df[df["month"] == last_month]

    # --- Weekly Summary ---
    st.header("📅 This Week's Summary")
    st.caption(current_week_label)
    if this_week_df.empty:
        st.info("No expenses logged this week yet.")
    else:
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Spent", f"${this_week_df['amount'].sum():.2f}")
        col2.metric("# of Expenses", len(this_week_df))
        col3.metric("Largest Expense", f"${this_week_df['amount'].max():.2f}")
        st.write("**Breakdown by Category:**")
        category_summary = this_week_df.groupby("category")["amount"].sum().reset_index()
        category_summary.columns = ["Category", "Total ($)"]
        category_summary["Total ($)"] = category_summary["Total ($)"].apply(lambda x: f"${x:.2f}")
        st.dataframe(category_summary, use_container_width=True, hide_index=True)

    st.divider()

    # --- Week over Week ---
    st.header("📊 Week over Week Comparison")
    this_week_total = this_week_df["amount"].sum()
    last_week_total = last_week_df["amount"].sum()
    week_diff = this_week_total - last_week_total
    col1, col2, col3 = st.columns(3)
    col1.metric("This Week", f"${this_week_total:.2f}")
    col2.metric("Last Week", f"${last_week_total:.2f}")
    col3.metric("Difference", f"${abs(week_diff):.2f}",
                delta=f"{'▲' if week_diff > 0 else '▼'} {'more' if week_diff > 0 else 'less'} than last week",
                delta_color="inverse" if week_diff > 0 else "normal")

    st.divider()

    # --- Monthly Progress ---
    st.header("📆 Monthly Progress")
    this_month_total = this_month_df["amount"].sum()
    last_month_total = last_month_df["amount"].sum()
    month_diff = this_month_total - last_month_total
    col1, col2, col3 = st.columns(3)
    col1.metric(f"{current_month}", f"${this_month_total:.2f}")
    col2.metric(f"{last_month}", f"${last_month_total:.2f}")
    col3.metric("Difference", f"${abs(month_diff):.2f}",
                delta=f"{'▲' if month_diff > 0 else '▼'} {'more' if month_diff > 0 else 'less'} than last month",
                delta_color="inverse" if month_diff > 0 else "normal")

    st.divider()

    # --- Overall Spending Trend ---
    st.header("📈 Overall Spending Trend")
    weekly_totals = df.groupby(["week_start", "week"])["amount"].sum().reset_index()
    weekly_totals = weekly_totals.sort_values("week_start")

    if len(weekly_totals) >= 2:
        first_half = weekly_totals["amount"].iloc[:len(weekly_totals)//2].mean()
        second_half = weekly_totals["amount"].iloc[len(weekly_totals)//2:].mean()
        trend_diff = second_half - first_half
        trend_pct = (trend_diff / first_half * 100) if first_half > 0 else 0

        if trend_diff > 0:
            st.warning(f"⚠️ Your spending has been trending **up {trend_pct:.1f}%** over time. Keep an eye on it!")
        else:
            st.success(f"✅ Your spending has been trending **down {abs(trend_pct):.1f}%** over time. Great work!")

    fig_trend = px.line(
        weekly_totals.sort_values("week_start"),
        x="week", y="amount",
        markers=True,
        labels={"amount": "Amount ($)", "week": "Week"},
        color_discrete_sequence=["#00C853"]
    )
    fig_trend.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#FAFAFA"),
        xaxis=dict(type="category", categoryorder="array",
                   categoryarray=weekly_totals.sort_values("week_start")["week"].tolist()),
        height=250,
        margin=dict(t=20, b=0, l=0, r=0)
    )
    st.plotly_chart(fig_trend, use_container_width=True)

    st.divider()

    # --- 50/30/20 Consistency ---
    st.header("⚖️ 50/30/20 Consistency Over Time")
    weekly_buckets = df.groupby(["week_start", "week", "bucket"])["amount"].sum().reset_index()
    weekly_bucket_totals = df.groupby(["week_start", "week"])["amount"].sum().reset_index()
    weekly_bucket_totals.columns = ["week_start", "week", "total"]
    weekly_buckets = weekly_buckets.merge(weekly_bucket_totals, on=["week_start", "week"])
    weekly_buckets["pct"] = weekly_buckets["amount"] / weekly_buckets["total"] * 100
    weekly_buckets = weekly_buckets.sort_values("week_start")

    targets = {"Needs": 50, "Wants": 30, "Savings": 20}
    colors = {"Needs": "#00C853", "Wants": "#2196F3", "Savings": "#FF9800"}

    ordered_weeks = weekly_buckets.drop_duplicates("week").sort_values("week_start")["week"].tolist()

    fig_budget_trend = go.Figure()
    for bucket, target in targets.items():
        bucket_data = weekly_buckets[weekly_buckets["bucket"] == bucket].sort_values("week_start")
        fig_budget_trend.add_trace(go.Scatter(
            x=bucket_data["week"],
            y=bucket_data["pct"],
            mode="lines+markers",
            name=bucket,
            line=dict(color=colors[bucket])
        ))
        fig_budget_trend.add_hline(
            y=target,
            line_dash="dash",
            line_color=colors[bucket],
            annotation_text=f"{bucket} target ({target}%)",
            annotation_position="right"
        )

    fig_budget_trend.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#FAFAFA"),
        xaxis=dict(type="category", categoryorder="array", categoryarray=ordered_weeks),
        yaxis=dict(title="%", range=[0, 110]),
        height=300,
        margin=dict(t=20, b=0, l=0, r=0),
        legend=dict(orientation="h", yanchor="bottom", y=1.02)
    )
    st.plotly_chart(fig_budget_trend, use_container_width=True)

    if len(weekly_buckets) >= 2:
        for bucket, target in targets.items():
            bucket_data = weekly_buckets[weekly_buckets["bucket"] == bucket]
            if not bucket_data.empty:
                avg_pct = bucket_data["pct"].mean()
                diff = avg_pct - target
                if abs(diff) <= 5:
                    st.success(f"✅ **{bucket}**: You're averaging {avg_pct:.1f}% — right on track with the {target}% target!")
                elif bucket == "Savings":
                    if diff > 5:
                        st.success(f"✅ **{bucket}**: You're averaging {avg_pct:.1f}% — {diff:.1f}% over the {target}% target. Great work!")
                    else:
                        st.warning(f"⚠️ **{bucket}**: You're averaging {avg_pct:.1f}% — {abs(diff):.1f}% under the {target}% target. Try to save more!")
                else:
                    if diff > 5:
                        st.warning(f"⚠️ **{bucket}**: You're averaging {avg_pct:.1f}% — {diff:.1f}% over the {target}% target.")
                    else:
                        st.info(f"ℹ️ **{bucket}**: You're averaging {avg_pct:.1f}% — {abs(diff):.1f}% under the {target}% target.")

    st.divider()

    # --- Savings Tracking ---
    st.header("💰 Savings Tracking")
    savings_df = df[df["bucket"] == "Savings"]

    if savings_df.empty:
        st.warning("⚠️ No savings logged yet. Try adding expenses under the Savings category!")
    else:
        weekly_savings = savings_df.groupby(["week_start", "week"])["amount"].sum().reset_index()
        weekly_savings = weekly_savings.sort_values("week_start")
        total_savings = savings_df["amount"].sum()
        this_month_savings = savings_df[savings_df["date"].dt.strftime("%B %Y") == current_month]["amount"].sum()
        savings_pct = (this_month_savings / this_month_total * 100) if this_month_total > 0 else 0

        col1, col2, col3 = st.columns(3)
        col1.metric("Total Savings", f"${total_savings:.2f}")
        col2.metric("This Month", f"${this_month_savings:.2f}")
        col3.metric("Savings Rate", f"{savings_pct:.1f}%",
                    delta="on track" if savings_pct >= 20 else "below 20% target",
                    delta_color="normal" if savings_pct >= 20 else "inverse")

        if savings_pct >= 20:
            st.success(f"✅ You're saving {savings_pct:.1f}% of your spending this month — meeting the 20% target!")
        else:
            st.warning(f"⚠️ You're saving {savings_pct:.1f}% this month — try to get closer to the 20% target.")

        fig_savings = px.bar(
            weekly_savings.sort_values("week_start"),
            x="week", y="amount",
            labels={"amount": "Amount ($)", "week": "Week"},
            color_discrete_sequence=["#00C853"]
        )
        fig_savings.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#FAFAFA"),
            xaxis=dict(type="category", categoryorder="array",
                       categoryarray=weekly_savings.sort_values("week_start")["week"].tolist()),
            height=250,
            margin=dict(t=20, b=0, l=0, r=0)
        )
        st.plotly_chart(fig_savings, use_container_width=True)