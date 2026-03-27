import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import load_data, filter_data, get_periods, CATEGORY_BUCKETS
from components import render_sidebar, check_password

st.set_page_config(layout="wide")
if not check_password():
    st.stop()
render_sidebar()

st.title("📊 Dashboard")

df = load_data()

if df.empty:
    st.info("No expenses logged yet. Head to the main page to add some!")
else:
    time_filter = st.radio("View by:", ["Weekly", "Monthly", "Yearly"], horizontal=True)
    periods = get_periods(df, time_filter)
    selected_period = st.selectbox("Select period:", periods)
    filtered_df = filter_data(df, time_filter, selected_period)

    if filtered_df.empty:
        st.info("No expenses found for this period.")
    else:
        filtered_df = filtered_df.copy()
        filtered_df["date"] = pd.to_datetime(filtered_df["date"], format='mixed').dt.date
        filtered_df["date_str"] = filtered_df["date"].astype(str)
        filtered_df["bucket"] = filtered_df["category"].map(CATEGORY_BUCKETS)

        total = filtered_df["amount"].sum()
        num_expenses = len(filtered_df)
        largest = filtered_df["amount"].max()
        top_category = filtered_df.groupby("category")["amount"].sum().idxmax()

        # --- Bucket totals for 50/30/20 ---
        bucket_totals = filtered_df.groupby("bucket")["amount"].sum()
        needs_pct = (bucket_totals.get("Needs", 0) / total * 100) if total > 0 else 0
        wants_pct = (bucket_totals.get("Wants", 0) / total * 100) if total > 0 else 0
        savings_pct = (bucket_totals.get("Savings", 0) / total * 100) if total > 0 else 0

        # --- Layout ---
        left_col, right_col = st.columns([1, 2])

        with left_col:
            # Metrics
            st.metric("Total Spent", f"${total:.2f}")
            st.metric("# of Expenses", num_expenses)
            st.metric("Largest Expense", f"${largest:.2f}")
            st.metric("Top Category", top_category)

            st.markdown("---")

            # Pie Chart
            st.markdown("##### Spending by Category")
            fig_pie = px.pie(
                filtered_df,
                values="amount",
                names="category",
                hole=0.3,
                color_discrete_sequence=px.colors.sequential.Greens_r
            )
            fig_pie.update_layout(
                margin=dict(t=0, b=0, l=0, r=0),
                showlegend=True,
                height=250,
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#FAFAFA")
            )
            st.plotly_chart(fig_pie, use_container_width=True)

        with right_col:
            # Line Chart
            st.markdown("##### Spending Over Time")
            daily = filtered_df.groupby("date_str")["amount"].sum().reset_index()
            fig_line = px.line(
                daily, x="date_str", y="amount",
                markers=True,
                labels={"amount": "Amount ($)", "date_str": "Date"},
                color_discrete_sequence=["#00C853"]
            )
            fig_line.update_layout(
                margin=dict(t=0, b=0, l=0, r=0),
                height=200,
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#FAFAFA"),
                xaxis=dict(type="category")
            )
            st.plotly_chart(fig_line, use_container_width=True)

            # Biggest Expenses
            st.markdown("##### Biggest Expenses")
            biggest = filtered_df.nlargest(5, "amount")[["date", "description", "category", "amount"]]
            biggest["amount"] = biggest["amount"].apply(lambda x: f"${x:.2f}")
            st.dataframe(biggest, use_container_width=True, hide_index=True)

            st.markdown("---")

            # 50/30/20 Chart
            st.markdown("##### 50/30/20 Budget Rule")
            targets = {"Needs": 50, "Wants": 30, "Savings": 20}
            actuals = {"Needs": needs_pct, "Wants": wants_pct, "Savings": savings_pct}

            fig_budget = go.Figure()

            for bucket, target in targets.items():
                actual = actuals[bucket]
                color = "#00C853" if actual <= target else "#FF5252"
                fig_budget.add_trace(go.Bar(
                    name=f"{bucket} (target {target}%)",
                    x=[bucket],
                    y=[actual],
                    marker_color=color,
                    text=f"{actual:.1f}%",
                    textposition="outside"
                ))
                fig_budget.add_shape(
                    type="line",
                    x0=-0.5 + list(targets.keys()).index(bucket),
                    x1=0.5 + list(targets.keys()).index(bucket),
                    y0=target,
                    y1=target,
                    line=dict(color="#FAFAFA", width=2, dash="dash")
                )

            fig_budget.update_layout(
                margin=dict(t=20, b=0, l=0, r=0),
                height=220,
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#FAFAFA"),
                showlegend=False,
                yaxis=dict(title="%", range=[0, 110]),
                barmode="group"
            )
            st.plotly_chart(fig_budget, use_container_width=True)
            st.caption("🟢 Green = within target  🔴 Red = over target  ⬜ Dashed line = target %")