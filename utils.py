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

def load_data():
    conn = sqlite3.connect("finances.db")
    df = pd.read_sql_query("SELECT * FROM expenses ORDER BY date DESC", conn)
    conn.close()
    if not df.empty:
        df["date"] = pd.to_datetime(df["date"], format='mixed').dt.date
    return df

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