import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import date, datetime
import calendar

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Expense Tracker",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="collapsed",
)

API_BASE = "http://localhost:5000/api"

# ── Material Design CSS ─────────────────────────────────────────────────────────
st.markdown("""
<style>
  /* ── Google Fonts ── */
  @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap');

  /* ── Global reset ── */
  html, body, [class*="css"] {
    font-family: 'Roboto', sans-serif;
  }

  /* ── App background ── */
  .stApp {
    background-color: #F5F5F5;
  }

  /* ── Hide default Streamlit chrome ── */
  #MainMenu, footer, header { visibility: hidden; }

  /* ── Top app bar ── */
  .md-app-bar {
    background: linear-gradient(135deg, #1565C0 0%, #1976D2 100%);
    padding: 16px 24px;
    border-radius: 0 0 4px 4px;
    box-shadow: 0 2px 4px rgba(0,0,0,.24), 0 4px 8px rgba(0,0,0,.12);
    margin-bottom: 24px;
    display: flex;
    align-items: center;
    gap: 12px;
  }
  .md-app-bar h1 {
    color: white;
    font-size: 22px;
    font-weight: 500;
    margin: 0;
    letter-spacing: .4px;
  }
  .md-app-bar span { font-size: 28px; }

  /* ── Material card ── */
  .md-card {
    background: #ffffff;
    border-radius: 8px;
    padding: 20px 24px;
    box-shadow: 0 1px 3px rgba(0,0,0,.12), 0 2px 4px rgba(0,0,0,.08);
    margin-bottom: 16px;
  }
  .md-card-title {
    font-size: 16px;
    font-weight: 500;
    color: #1565C0;
    margin-bottom: 12px;
    display: flex;
    align-items: center;
    gap: 8px;
    border-bottom: 1px solid #E3F2FD;
    padding-bottom: 8px;
  }

  /* ── Metric cards row ── */
  .md-metric-card {
    background: #ffffff;
    border-radius: 8px;
    padding: 16px 20px;
    box-shadow: 0 1px 3px rgba(0,0,0,.12), 0 2px 4px rgba(0,0,0,.08);
    text-align: center;
    border-top: 3px solid #1976D2;
  }
  .md-metric-label {
    font-size: 12px;
    font-weight: 500;
    color: #757575;
    text-transform: uppercase;
    letter-spacing: .8px;
    margin-bottom: 4px;
  }
  .md-metric-value {
    font-size: 28px;
    font-weight: 700;
    color: #1565C0;
  }
  .md-metric-sub {
    font-size: 12px;
    color: #9E9E9E;
    margin-top: 2px;
  }

  /* ── Category chips ── */
  .chip {
    display: inline-block;
    padding: 3px 10px;
    border-radius: 12px;
    font-size: 11px;
    font-weight: 500;
    color: white;
  }

  /* ── Success / error banners ── */
  .md-success {
    background: #E8F5E9;
    border-left: 4px solid #4CAF50;
    padding: 10px 16px;
    border-radius: 0 4px 4px 0;
    color: #2E7D32;
    margin: 8px 0;
    font-size: 14px;
  }
  .md-error {
    background: #FFEBEE;
    border-left: 4px solid #F44336;
    padding: 10px 16px;
    border-radius: 0 4px 4px 0;
    color: #C62828;
    margin: 8px 0;
    font-size: 14px;
  }

  /* ── Streamlit widget tweaks ── */
  div[data-baseweb="tab-list"] {
    background: #ffffff;
    border-radius: 8px 8px 0 0;
    padding: 0 8px;
    box-shadow: 0 1px 3px rgba(0,0,0,.12);
    gap: 4px;
  }
  button[data-baseweb="tab"] {
    font-family: 'Roboto', sans-serif !important;
    font-size: 14px !important;
    font-weight: 500 !important;
    color: #616161 !important;
    text-transform: uppercase;
    letter-spacing: .5px;
    padding: 12px 20px !important;
    border-radius: 4px 4px 0 0 !important;
  }
  button[data-baseweb="tab"][aria-selected="true"] {
    color: #1565C0 !important;
    border-bottom: 2px solid #1565C0 !important;
  }
  div[data-testid="stForm"] {
    background: transparent;
  }
  .stButton button {
    background: #1976D2 !important;
    color: white !important;
    border: none !important;
    border-radius: 4px !important;
    font-family: 'Roboto', sans-serif !important;
    font-size: 14px !important;
    font-weight: 500 !important;
    letter-spacing: .5px !important;
    padding: 8px 24px !important;
    box-shadow: 0 2px 4px rgba(25,118,210,.4) !important;
    text-transform: uppercase;
    transition: all .2s ease;
  }
  .stButton button:hover {
    background: #1565C0 !important;
    box-shadow: 0 4px 8px rgba(25,118,210,.4) !important;
  }
  div[data-testid="stDataFrame"] {
    border-radius: 8px;
    overflow: hidden;
    box-shadow: 0 1px 3px rgba(0,0,0,.12);
  }
</style>
""", unsafe_allow_html=True)

# ── Category colour palette ─────────────────────────────────────────────────────
CATEGORY_COLORS = {
    "Food":          "#FF7043",
    "Transport":     "#42A5F5",
    "Entertainment": "#AB47BC",
    "Shopping":      "#26C6DA",
    "Bills":         "#EF5350",
    "Health":        "#66BB6A",
    "Other":         "#8D6E63",
}

# ── Helpers ─────────────────────────────────────────────────────────────────────

def category_chip(category: str) -> str:
    colour = CATEGORY_COLORS.get(category, "#9E9E9E")
    return f'<span class="chip" style="background:{colour};">{category}</span>'


def fetch_categories():
    try:
        r = requests.get(f"{API_BASE}/categories", timeout=5)
        if r.status_code == 200:
            return r.json().get("categories", [])
    except requests.exceptions.ConnectionError:
        pass
    return ["Food", "Transport", "Entertainment", "Shopping", "Bills", "Health", "Other"]


def fetch_expenses(month=None, year=None):
    params = {}
    if month:
        params["month"] = month
    if year:
        params["year"] = year
    try:
        r = requests.get(f"{API_BASE}/expenses", params=params, timeout=5)
        if r.status_code == 200:
            return r.json().get("expenses", [])
    except requests.exceptions.ConnectionError:
        st.error("⚠️ Cannot connect to backend. Make sure the Flask API is running on port 5000.")
    return []


def fetch_summary(month, year):
    try:
        r = requests.get(f"{API_BASE}/expenses/summary",
                         params={"month": month, "year": year}, timeout=5)
        if r.status_code == 200:
            return r.json()
    except requests.exceptions.ConnectionError:
        pass
    return None


def add_expense_api(payload):
    try:
        r = requests.post(f"{API_BASE}/expenses", json=payload, timeout=5)
        return r.status_code == 201, r.json()
    except requests.exceptions.ConnectionError:
        return False, {"error": "Cannot connect to backend API."}


def delete_expense_api(expense_id):
    try:
        r = requests.delete(f"{API_BASE}/expenses/{expense_id}", timeout=5)
        return r.status_code == 200
    except requests.exceptions.ConnectionError:
        return False


# ── App bar ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="md-app-bar">
  <span>💰</span>
  <h1>Expense Tracker</h1>
</div>
""", unsafe_allow_html=True)

# ── Month / year selector (shared state) ────────────────────────────────────────
today = date.today()
col_m, col_y, _ = st.columns([2, 2, 8])
with col_m:
    month_names = list(calendar.month_name)[1:]
    selected_month_name = st.selectbox(
        "Month", month_names, index=today.month - 1, key="month_select"
    )
    selected_month = month_names.index(selected_month_name) + 1
with col_y:
    selected_year = st.selectbox(
        "Year", list(range(today.year - 2, today.year + 1))[::-1],
        index=0, key="year_select"
    )

# ── Tabs ────────────────────────────────────────────────────────────────────────
tab_expenses, tab_analytics = st.tabs(["📋  Expenses", "📊  Analytics"])

# ════════════════════════════════════════════════════════════════════════════════
# TAB 1 – EXPENSES
# ════════════════════════════════════════════════════════════════════════════════
with tab_expenses:
    col_form, col_gap, col_table = st.columns([4, 1, 7])

    # ── Add Expense form ───────────────────────────────────────────────────────
    with col_form:
        st.markdown('<div class="md-card"><div class="md-card-title">➕ Add New Expense</div>', unsafe_allow_html=True)

        categories = fetch_categories()

        with st.form("add_expense_form", clear_on_submit=True):
            amount = st.number_input(
                "Amount ($)", min_value=0.01, max_value=99999.99,
                step=0.01, format="%.2f", key="form_amount"
            )
            category = st.selectbox("Category", categories, key="form_category")
            description = st.text_input("Description", max_chars=100, key="form_desc")
            expense_date = st.date_input("Date", value=today, key="form_date")

            submitted = st.form_submit_button("Add Expense", use_container_width=True)
            if submitted:
                if not description.strip():
                    st.markdown('<div class="md-error">⚠️ Description cannot be empty.</div>',
                                unsafe_allow_html=True)
                else:
                    ok, resp = add_expense_api({
                        "amount": amount,
                        "category": category,
                        "description": description.strip(),
                        "date": expense_date.isoformat(),
                    })
                    if ok:
                        st.markdown(
                            f'<div class="md-success">✅ Expense of <strong>${amount:.2f}</strong>'
                            f' ({category}) added!</div>',
                            unsafe_allow_html=True
                        )
                        st.rerun()
                    else:
                        st.markdown(
                            f'<div class="md-error">❌ {resp.get("error", "Failed to add expense.")}</div>',
                            unsafe_allow_html=True
                        )

        st.markdown("</div>", unsafe_allow_html=True)

        # Monthly summary mini-card
        summary = fetch_summary(selected_month, selected_year)
        if summary:
            st.markdown(f"""
            <div class="md-card" style="margin-top:0;">
              <div class="md-card-title">📅 {selected_month_name} {selected_year} Summary</div>
              <div style="display:flex;gap:16px;flex-wrap:wrap;">
                <div class="md-metric-card" style="flex:1;min-width:80px;border-color:#1976D2;">
                  <div class="md-metric-label">Total Spent</div>
                  <div class="md-metric-value" style="font-size:20px;">${summary['total']:.2f}</div>
                </div>
                <div class="md-metric-card" style="flex:1;min-width:80px;border-color:#7B1FA2;">
                  <div class="md-metric-label">Transactions</div>
                  <div class="md-metric-value" style="font-size:20px;color:#7B1FA2;">{summary['count']}</div>
                </div>
              </div>
            </div>
            """, unsafe_allow_html=True)

    # ── Expenses table ─────────────────────────────────────────────────────────
    with col_table:
        st.markdown('<div class="md-card">', unsafe_allow_html=True)
        st.markdown(
            f'<div class="md-card-title">🧾 Expenses — {selected_month_name} {selected_year}</div>',
            unsafe_allow_html=True
        )

        expenses_data = fetch_expenses(month=selected_month, year=selected_year)

        if not expenses_data:
            st.info("No expenses recorded for this period. Add your first expense! 👆")
        else:
            df = pd.DataFrame(expenses_data)

            # Category chips column (HTML render)
            chip_col = df["category"].apply(category_chip)

            display_df = pd.DataFrame({
                "Date":        pd.to_datetime(df["date"]).dt.strftime("%d %b %Y"),
                "Category":    df["category"],
                "Description": df["description"],
                "Amount":      df["amount"].apply(lambda x: f"${x:.2f}"),
            })

            st.dataframe(
                display_df,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Amount": st.column_config.TextColumn("Amount", width="small"),
                    "Category": st.column_config.TextColumn("Category", width="medium"),
                    "Date": st.column_config.TextColumn("Date", width="small"),
                }
            )

            # Delete row
            st.markdown("---")
            st.markdown('<div style="font-size:13px;color:#757575;font-weight:500;">🗑️ Delete an expense</div>',
                        unsafe_allow_html=True)

            delete_options = {
                f"{e['date']} | {e['category']} | {e['description']} | ${e['amount']:.2f}": e["id"]
                for e in expenses_data
            }
            selected_label = st.selectbox(
                "Select expense to delete", list(delete_options.keys()),
                key="delete_select", label_visibility="collapsed"
            )
            if st.button("Delete Selected", key="delete_btn"):
                if delete_expense_api(delete_options[selected_label]):
                    st.markdown('<div class="md-success">✅ Expense deleted.</div>', unsafe_allow_html=True)
                    st.rerun()
                else:
                    st.markdown('<div class="md-error">❌ Failed to delete expense.</div>',
                                unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════════
# TAB 2 – ANALYTICS
# ════════════════════════════════════════════════════════════════════════════════
with tab_analytics:
    summary = fetch_summary(selected_month, selected_year)
    expenses_data = fetch_expenses(month=selected_month, year=selected_year)

    if not expenses_data:
        st.info(f"No expenses recorded for {selected_month_name} {selected_year}. Add some expenses first! 👆")
    else:
        df = pd.DataFrame(expenses_data)
        df["amount"] = df["amount"].astype(float)
        df["date_dt"] = pd.to_datetime(df["date"])

        # ── Top metric strip ────────────────────────────────────────────────────
        avg_per_day = summary["total"] / max(df["date_dt"].nunique(), 1) if summary else 0
        top_category = max(summary["by_category"], key=summary["by_category"].get) if summary and summary["by_category"] else "N/A"
        top_cat_amount = summary["by_category"].get(top_category, 0) if summary else 0

        m1, m2, m3, m4 = st.columns(4)
        metrics = [
            (m1, "Total Spent", f"${summary['total']:.2f}", f"{summary['count']} transactions", "#1976D2"),
            (m2, "Daily Average", f"${avg_per_day:.2f}", "per active day", "#7B1FA2"),
            (m3, "Top Category", top_category, f"${top_cat_amount:.2f}", "#E65100"),
            (m4, "Month", f"{selected_month_name[:3]} {selected_year}", "selected period", "#2E7D32"),
        ]
        for col, label, val, sub, color in metrics:
            with col:
                st.markdown(f"""
                <div class="md-metric-card" style="border-color:{color};">
                  <div class="md-metric-label">{label}</div>
                  <div class="md-metric-value" style="color:{color};">{val}</div>
                  <div class="md-metric-sub">{sub}</div>
                </div>
                """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # ── Charts row ──────────────────────────────────────────────────────────
        chart_col1, chart_col2 = st.columns(2)

        # Pie chart – spending by category
        with chart_col1:
            st.markdown('<div class="md-card"><div class="md-card-title">🥧 Spending by Category</div>',
                        unsafe_allow_html=True)
            cat_totals = df.groupby("category")["amount"].sum().reset_index()
            cat_totals.columns = ["Category", "Amount"]
            colours = [CATEGORY_COLORS.get(c, "#9E9E9E") for c in cat_totals["Category"]]

            fig_pie = px.pie(
                cat_totals, values="Amount", names="Category",
                color="Category",
                color_discrete_map=CATEGORY_COLORS,
                hole=0.4,
            )
            fig_pie.update_traces(
                textposition="outside",
                textinfo="percent+label",
                hovertemplate="<b>%{label}</b><br>$%{value:.2f}<br>%{percent}<extra></extra>",
            )
            fig_pie.update_layout(
                showlegend=True,
                legend=dict(orientation="v", x=1.0, y=0.5),
                margin=dict(l=0, r=0, t=10, b=10),
                height=300,
                font=dict(family="Roboto, sans-serif"),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
            )
            st.plotly_chart(fig_pie, use_container_width=True, config={"displayModeBar": False})
            st.markdown("</div>", unsafe_allow_html=True)

        # Bar chart – spending by category
        with chart_col2:
            st.markdown('<div class="md-card"><div class="md-card-title">📊 Category Breakdown</div>',
                        unsafe_allow_html=True)
            cat_sorted = cat_totals.sort_values("Amount", ascending=True)
            colours_bar = [CATEGORY_COLORS.get(c, "#9E9E9E") for c in cat_sorted["Category"]]

            fig_bar = go.Figure(go.Bar(
                x=cat_sorted["Amount"],
                y=cat_sorted["Category"],
                orientation="h",
                marker_color=colours_bar,
                text=cat_sorted["Amount"].apply(lambda v: f"${v:.2f}"),
                textposition="outside",
                hovertemplate="<b>%{y}</b><br>$%{x:.2f}<extra></extra>",
            ))
            fig_bar.update_layout(
                xaxis=dict(title="Amount ($)", gridcolor="#F5F5F5"),
                yaxis=dict(title=""),
                margin=dict(l=0, r=40, t=10, b=40),
                height=300,
                font=dict(family="Roboto, sans-serif"),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
            )
            st.plotly_chart(fig_bar, use_container_width=True, config={"displayModeBar": False})
            st.markdown("</div>", unsafe_allow_html=True)

        # ── Daily spending trend ─────────────────────────────────────────────────
        st.markdown('<div class="md-card"><div class="md-card-title">📈 Daily Spending Trend</div>',
                    unsafe_allow_html=True)
        daily = df.groupby("date_dt")["amount"].sum().reset_index()
        daily.columns = ["Date", "Amount"]
        daily = daily.sort_values("Date")
        daily["Cumulative"] = daily["Amount"].cumsum()

        fig_trend = go.Figure()
        fig_trend.add_trace(go.Bar(
            x=daily["Date"], y=daily["Amount"],
            name="Daily Spend",
            marker_color="#90CAF9",
            hovertemplate="<b>%{x|%d %b}</b><br>Daily: $%{y:.2f}<extra></extra>",
        ))
        fig_trend.add_trace(go.Scatter(
            x=daily["Date"], y=daily["Cumulative"],
            name="Cumulative",
            line=dict(color="#1565C0", width=2),
            mode="lines+markers",
            marker=dict(size=6),
            hovertemplate="<b>%{x|%d %b}</b><br>Cumulative: $%{y:.2f}<extra></extra>",
            yaxis="y2",
        ))
        fig_trend.update_layout(
            yaxis=dict(title="Daily ($)", gridcolor="#F5F5F5"),
            yaxis2=dict(title="Cumulative ($)", overlaying="y", side="right", gridcolor="rgba(0,0,0,0)"),
            xaxis=dict(title="", gridcolor="#F5F5F5"),
            legend=dict(orientation="h", x=0, y=1.1),
            margin=dict(l=0, r=0, t=10, b=40),
            height=260,
            font=dict(family="Roboto, sans-serif"),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            hovermode="x unified",
        )
        st.plotly_chart(fig_trend, use_container_width=True, config={"displayModeBar": False})
        st.markdown("</div>", unsafe_allow_html=True)

        # ── Category detail table ───────────────────────────────────────────────
        st.markdown('<div class="md-card"><div class="md-card-title">📋 Category Summary</div>',
                    unsafe_allow_html=True)
        cat_summary = df.groupby("category").agg(
            Total=("amount", "sum"),
            Count=("amount", "count"),
            Average=("amount", "mean"),
            Max=("amount", "max"),
        ).reset_index()
        cat_summary.columns = ["Category", "Total ($)", "# Transactions", "Avg ($)", "Max ($)"]
        total_all = cat_summary["Total ($)"].sum()
        cat_summary["Share (%)"] = (cat_summary["Total ($)"] / total_all * 100).round(1)
        cat_summary = cat_summary.sort_values("Total ($)", ascending=False)
        for col in ["Total ($)", "Avg ($)", "Max ($)"]:
            cat_summary[col] = cat_summary[col].apply(lambda v: f"${v:.2f}")
        cat_summary["Share (%)"] = cat_summary["Share (%)"].apply(lambda v: f"{v}%")

        st.dataframe(cat_summary, use_container_width=True, hide_index=True)
        st.markdown("</div>", unsafe_allow_html=True)
