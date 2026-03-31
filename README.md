# 💰 Finance Tracker

A full-stack personal finance web application built in Python and SQL. Designed and developed from scratch to track personal expenses, visualize spending habits, and maintain a customizable budget rule.

Live demo: `https://financetracker-av5vxkk2bqn6vs7z6stqvi.streamlit.app/Dashboard`

---

## Overview

Finance Tracker started as a personal challenge to build a practical, real-world application using Python and SQL. Every feature was deliberately designed around a real use case: making it easy to log, review, and reflect on personal spending habits.

The app follows a customizable budgeting philosophy, splitting expenses into Needs, Wants, and Savings, with fully adjustable targets and real-time visual feedback on whether spending aligns with those goals.

---

## Why This Was Built

I wanted to build a simple finance tracking tool that contains features that work for my situation. This tool aligns with my financial habits and is customizable if I ever need to change them. This app also enforces consistency to sit down each week, reflect on what was spent, and check whether spending aligns with goals. I can keep track if I am spending money properly, and saving money efficiently.

Beyond the practical use case, this project was an opportunity to build something real. Designing the data model, building the dashboard, wiring up automated email reminders, and deploying a live application taught me a useful set of skills. The fact that I actually use it every week makes it even more rewarding.
---

## Preview (Test Data)

![Finance Tracker Dashboard](assets/dashboard.png)

---

## What Was Built

**Expense Logging**
A clean form-based interface for logging multiple expenses at once by description, category, amount, payment method, and date. Data is stored in a local SQLite database and instantly reflected across all pages.

**Dynamic Dashboard**
An interactive multi-panel dashboard built with Plotly, featuring spending breakdowns by category, spending trends over time, biggest expenses, and a real-time budget rule chart. The dashboard supports weekly, monthly, and yearly filtering with period selection.

**Spending Reports**
A dedicated reports page that surfaces deeper insights including overall spending trends, week-over-week and month-over-month comparisons, budget rule consistency tracking over time, and savings rate analysis.

**Expense Management**
A spreadsheet-style editable table powered by Streamlit's `st.data_editor` that allows direct in-place editing and deletion of past expenses with time-period filtering.

**Weekly Email Reminders**
An automated email reminder system built with Python's `smtplib` and Gmail SMTP. A GitHub Actions workflow fires once a week, sending a reminder to log that week's expenses, no third-party services required.

**Landing Page**
A public-facing landing page that showcases the app with live sample data and an interactive budget rule customizer, built to demonstrate the app's capabilities without exposing any personal data.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend & Backend | Python, Streamlit |
| Database | SQLite |
| Charts & Visualization | Plotly |
| Data Processing | Pandas |
| Email | smtplib, Gmail SMTP |
| Scheduling | GitHub Actions |

---

## Project Structure
```
Finance_Tracker/
│
├── app.py                  ← Public landing page with live sample data
├── utils.py                ← Shared data loading, filtering, and category mapping
├── components.py           ← Sidebar navigation and authentication
├── send_reminder.py        ← Standalone email reminder script for GitHub Actions
├── create_sample_data.py   ← Sample data generator for demo purposes
├── requirements.txt        ← Python dependencies
│
├── pages/
│   ├── 0_Log_Expense.py    ← Multi-row expense entry form
│   ├── 1_My_Expenses.py    ← Editable expense table with time filters
│   ├── 2_Dashboard.py      ← Interactive charts and metrics
│   └── 3_Reports.py        ← Trend analysis and email reminders
│
└── .streamlit/
    └── config.toml         ← Dark mode theme configuration
---