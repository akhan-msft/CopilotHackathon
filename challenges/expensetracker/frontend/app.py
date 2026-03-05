import os
import streamlit as st
import requests
import pandas as pd
from datetime import date
import plotly.express as px
import plotly.graph_objects as go

BACKEND_URL = os.environ.get("BACKEND_URL", "http://localhost:5000")

st.set_page_config(page_title="Expense Tracker", page_icon="💰", layout="wide")
st.title("💰 Expense Tracker")


def get_categories():
    try:
        response = requests.get(f"{BACKEND_URL}/categories", timeout=5)
        return response.json()
    except Exception:
        return ["Food", "Transport", "Entertainment", "Shopping", "Bills", "Other"]


def get_expenses():
    try:
        response = requests.get(f"{BACKEND_URL}/expenses", timeout=5)
        return response.json()
    except Exception:
        st.error("⚠️ Could not connect to backend. Make sure Flask is running on port 5000.")
        return []


def get_summary():
    try:
        response = requests.get(f"{BACKEND_URL}/expenses/summary", timeout=5)
        return response.json()
    except Exception:
        return None


def add_expense(amount, category, description, expense_date):
    payload = {
        "amount": amount,
        "category": category,
        "description": description,
        "date": expense_date.strftime("%Y-%m-%d"),
    }
    response = requests.post(f"{BACKEND_URL}/expenses", json=payload, timeout=5)
    return response


def delete_expense(expense_id):
    response = requests.delete(f"{BACKEND_URL}/expenses/{expense_id}", timeout=5)
    return response


categories = get_categories()

# ── Add Expense Form ──────────────────────────────────────────────────────────
st.header("➕ Add New Expense")
with st.form("add_expense_form", clear_on_submit=True):
    col1, col2 = st.columns(2)
    with col1:
        amount = st.number_input("Amount ($)", min_value=0.01, step=0.01, format="%.2f")
        category = st.selectbox("Category", categories)
    with col2:
        description = st.text_input("Description")
        expense_date = st.date_input("Date", value=date.today())

    submitted = st.form_submit_button("Add Expense", use_container_width=True)
    if submitted:
        if amount and amount > 0:
            resp = add_expense(amount, category, description, expense_date)
            if resp.status_code == 201:
                st.success(f"✅ Expense of ${amount:.2f} added successfully!")
                st.rerun()
            else:
                st.error(f"Failed to add expense: {resp.json().get('error', 'Unknown error')}")
        else:
            st.warning("Please enter a valid amount greater than 0.")

st.divider()

# Fetch all expenses once and reuse across summary and list sections
expenses = get_expenses()
df_all = pd.DataFrame(expenses) if expenses else pd.DataFrame()

# ── Summary Section ───────────────────────────────────────────────────────────
summary = get_summary()
if summary:
    st.header("📊 Monthly Summary")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("💵 Monthly Total", f"${summary['monthly_total']:.2f}")
    with col2:
        st.metric("🧾 Number of Expenses", summary["expense_count"])
    with col3:
        if summary["expense_count"] > 0:
            avg = summary["monthly_total"] / summary["expense_count"]
            st.metric("📈 Average per Expense", f"${avg:.2f}")
        else:
            st.metric("📈 Average per Expense", "$0.00")

    # ── Chart 1: Donut – spending by category ─────────────────────────────────
    category_totals = summary["category_totals"]
    non_zero = {k: v for k, v in category_totals.items() if v > 0}
    if non_zero:
        st.subheader("🏷️ Spending by Category")
        chart_col, table_col = st.columns([2, 1])
        with chart_col:
            fig_pie = px.pie(
                names=list(non_zero.keys()),
                values=list(non_zero.values()),
                title=f"Category Breakdown – {summary['month']}",
                hole=0.35,
            )
            fig_pie.update_traces(textposition="inside", textinfo="percent+label")
            fig_pie.update_layout(showlegend=True, margin=dict(t=40, b=10, l=10, r=10))
            st.plotly_chart(fig_pie, use_container_width=True)
        with table_col:
            df_cat = pd.DataFrame(
                [{"Category": k, "Total ($)": f"{v:.2f}"} for k, v in non_zero.items()]
            )
            st.dataframe(df_cat, hide_index=True, use_container_width=True)

    # ── Chart 2: Bar – daily spending for current month ───────────────────────
    if not df_all.empty:
        current_month = summary["month"]
        df_month = df_all[df_all["date"].str.startswith(current_month)].copy()
        if not df_month.empty:
            st.subheader("📅 Daily Spending This Month")
            df_daily = (
                df_month.groupby("date")["amount"].sum().reset_index()
                .rename(columns={"date": "Date", "amount": "Total ($)"})
                .sort_values("Date")
            )
            fig_bar = px.bar(
                df_daily,
                x="Date",
                y="Total ($)",
                title=f"Daily Spending – {current_month}",
                text_auto=".2f",
                color="Total ($)",
                color_continuous_scale="Blues",
            )
            fig_bar.update_layout(coloraxis_showscale=False, margin=dict(t=40, b=10))
            st.plotly_chart(fig_bar, use_container_width=True)

st.divider()

# ── Expense List ──────────────────────────────────────────────────────────────
st.header("📋 All Expenses")
if not df_all.empty:
    df_sorted = df_all.sort_values("date", ascending=False).reset_index(drop=True)

    for _, row in df_sorted.iterrows():
        with st.container():
            c1, c2, c3, c4, c5 = st.columns([2, 1, 2, 1, 1])
            c1.write(f"**{row['description'] or '(no description)'}**")
            c2.write(f"💲{row['amount']:.2f}")
            c3.write(f"🏷️ {row['category']}")
            c4.write(f"📅 {row['date']}")
            if c5.button("🗑️ Delete", key=row["id"]):
                resp = delete_expense(row["id"])
                if resp.status_code == 200:
                    st.success("Expense deleted.")
                    st.rerun()
                else:
                    st.error("Failed to delete expense.")
    st.divider()
    st.caption(f"Showing {len(df_all)} expense(s) total.")
else:
    st.info("No expenses recorded yet. Add your first expense above!")
