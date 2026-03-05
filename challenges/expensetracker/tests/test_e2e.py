"""
End-to-end tests for the Expense Tracker application.

Two layers of coverage:
  1. API layer  – exercises the live Flask backend via HTTP (fast, reliable)
  2. UI layer   – exercises the live Streamlit frontend via Playwright (browser)

Core user stories validated:
  US1 – Add a new expense with amount, category, and description
  US2 – View all expenses in a list format
  US3 – See total spending for the current month
  US4 – View spending breakdown by category
  US5 – Delete expenses
"""
import time
from datetime import datetime

import pytest
import requests as http


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

TODAY = datetime.now().strftime("%Y-%m-%d")
CURRENT_MONTH = datetime.now().strftime("%Y-%m")


def add_expense(api_url, amount, category, description="test", date=TODAY):
    resp = http.post(
        f"{api_url}/expenses",
        json={"amount": amount, "category": category,
              "description": description, "date": date},
    )
    resp.raise_for_status()
    return resp.json()


def _wait_for_text(page, text: str, timeout: int = 15_000):
    page.get_by_text(text, exact=False).first.wait_for(
        state="visible", timeout=timeout
    )


# ─────────────────────────────────────────────────────────────────────────────
# API-level E2E tests  (fast, no browser required)
# ─────────────────────────────────────────────────────────────────────────────

class TestE2EApi:
    """Full round-trip tests through the live Flask server."""

    # US1 – Add expense
    def test_us1_add_expense_full_fields(self, api_url):
        exp = add_expense(api_url, 49.99, "Food", "Dinner out", TODAY)
        assert exp["amount"] == 49.99
        assert exp["category"] == "Food"
        assert exp["description"] == "Dinner out"
        assert exp["date"] == TODAY
        assert "id" in exp

    def test_us1_add_expense_all_categories(self, api_url):
        for cat in ["Food", "Transport", "Entertainment", "Shopping", "Bills", "Other"]:
            exp = add_expense(api_url, 1.0, cat)
            assert exp["category"] == cat

    def test_us1_rejects_negative_amount(self, api_url):
        resp = http.post(f"{api_url}/expenses",
                         json={"amount": -10, "category": "Food"})
        assert resp.status_code == 400

    def test_us1_rejects_invalid_category(self, api_url):
        resp = http.post(f"{api_url}/expenses",
                         json={"amount": 10, "category": "Vacation"})
        assert resp.status_code == 400

    # US2 – List expenses
    def test_us2_list_is_empty_initially(self, api_url):
        expenses = http.get(f"{api_url}/expenses").json()
        assert expenses == []

    def test_us2_list_returns_all_added_expenses(self, api_url):
        add_expense(api_url, 10.0, "Food", "item A")
        add_expense(api_url, 20.0, "Bills", "item B")
        add_expense(api_url, 30.0, "Transport", "item C")
        expenses = http.get(f"{api_url}/expenses").json()
        assert len(expenses) == 3

    def test_us2_list_items_have_required_fields(self, api_url):
        add_expense(api_url, 5.0, "Other", "check fields")
        item = http.get(f"{api_url}/expenses").json()[0]
        for field in ("id", "amount", "category", "description", "date"):
            assert field in item

    # US3 – Monthly total
    def test_us3_monthly_total_sums_this_month(self, api_url):
        add_expense(api_url, 100.0, "Food", date=TODAY)
        add_expense(api_url, 50.0, "Bills", date=TODAY)
        summary = http.get(f"{api_url}/expenses/summary").json()
        assert summary["monthly_total"] == 150.0

    def test_us3_monthly_total_excludes_past_months(self, api_url):
        add_expense(api_url, 500.0, "Shopping", date=TODAY)
        add_expense(api_url, 9999.0, "Shopping", date="2020-01-15")
        summary = http.get(f"{api_url}/expenses/summary").json()
        assert summary["monthly_total"] == 500.0

    def test_us3_summary_reports_correct_month(self, api_url):
        summary = http.get(f"{api_url}/expenses/summary").json()
        assert summary["month"] == CURRENT_MONTH

    def test_us3_summary_expense_count(self, api_url):
        add_expense(api_url, 10.0, "Food", date=TODAY)
        add_expense(api_url, 20.0, "Food", date=TODAY)
        summary = http.get(f"{api_url}/expenses/summary").json()
        assert summary["expense_count"] == 2

    # US4 – Category breakdown
    def test_us4_category_breakdown_contains_all_categories(self, api_url):
        summary = http.get(f"{api_url}/expenses/summary").json()
        expected = {"Food", "Transport", "Entertainment", "Shopping", "Bills", "Other"}
        assert expected == set(summary["category_totals"].keys())

    def test_us4_category_totals_are_accurate(self, api_url):
        add_expense(api_url, 30.0, "Food", date=TODAY)
        add_expense(api_url, 20.0, "Food", date=TODAY)
        add_expense(api_url, 15.0, "Transport", date=TODAY)
        totals = http.get(f"{api_url}/expenses/summary").json()["category_totals"]
        assert totals["Food"] == 50.0
        assert totals["Transport"] == 15.0
        assert totals["Entertainment"] == 0

    def test_us4_category_totals_only_current_month(self, api_url):
        add_expense(api_url, 80.0, "Bills", date=TODAY)
        add_expense(api_url, 999.0, "Bills", date="2023-03-01")
        totals = http.get(f"{api_url}/expenses/summary").json()["category_totals"]
        assert totals["Bills"] == 80.0

    # US5 – Delete expense
    def test_us5_delete_removes_the_expense(self, api_url):
        exp = add_expense(api_url, 25.0, "Entertainment")
        resp = http.delete(f"{api_url}/expenses/{exp['id']}")
        assert resp.status_code == 200
        ids = [e["id"] for e in http.get(f"{api_url}/expenses").json()]
        assert exp["id"] not in ids

    def test_us5_delete_only_removes_target(self, api_url):
        keep = add_expense(api_url, 10.0, "Food", "keep me")
        gone = add_expense(api_url, 99.0, "Shopping", "delete me")
        http.delete(f"{api_url}/expenses/{gone['id']}")
        ids = [e["id"] for e in http.get(f"{api_url}/expenses").json()]
        assert keep["id"] in ids
        assert gone["id"] not in ids

    def test_us5_delete_nonexistent_returns_404(self, api_url):
        resp = http.delete(f"{api_url}/expenses/nonexistent-id")
        assert resp.status_code == 404

    def test_us5_monthly_total_decreases_after_delete(self, api_url):
        e1 = add_expense(api_url, 100.0, "Food", date=TODAY)
        add_expense(api_url, 50.0, "Bills", date=TODAY)
        http.delete(f"{api_url}/expenses/{e1['id']}")
        summary = http.get(f"{api_url}/expenses/summary").json()
        assert summary["monthly_total"] == 50.0


# ─────────────────────────────────────────────────────────────────────────────
# UI-level E2E tests  (Playwright – real browser against live Streamlit)
# ─────────────────────────────────────────────────────────────────────────────

@pytest.fixture()
def page_loaded(page, ui_url):
    """Navigate to the Streamlit app and wait for it to be interactive."""
    page.goto(ui_url)
    page.get_by_text("Add New Expense", exact=False).first.wait_for(
        state="visible", timeout=30_000
    )
    return page


class TestE2EUI:
    """Browser-based end-to-end tests using Playwright."""

    # US1 – Add expense via the form
    def test_us1_add_expense_form_visible(self, page_loaded):
        assert page_loaded.get_by_text("Add New Expense").first.is_visible()
        assert page_loaded.get_by_text("Amount ($)").first.is_visible()
        assert page_loaded.get_by_text("Category").first.is_visible()

    def test_us1_add_expense_shows_success_message(self, page_loaded, api_url):
        page = page_loaded
        # Fill in Amount
        page.get_by_label("Amount ($)").fill("35.50")
        # Fill in Description
        page.get_by_label("Description").fill("Coffee and snacks")
        # Submit
        page.get_by_role("button", name="Add Expense").click()
        # After a successful add, Streamlit reruns and the item appears in the list.
        # Wait for the description to show up in the expense list.
        page.get_by_text("Coffee and snacks", exact=False).first.wait_for(
            state="visible", timeout=20_000
        )

    # US2 – Expense list is displayed
    def test_us2_expense_list_shown_after_add(self, page_loaded, api_url):
        # Pre-seed via API so the list always has data
        add_expense(api_url, 12.50, "Food", "Bagel", TODAY)
        page_loaded.reload()
        # Wait explicitly for the seeded item – not just the section heading
        page_loaded.get_by_text("Bagel", exact=False).first.wait_for(
            state="visible", timeout=20_000
        )
        assert page_loaded.get_by_text("Bagel").first.is_visible()

    def test_us2_delete_button_present_for_each_expense(self, page_loaded, api_url):
        add_expense(api_url, 20.0, "Bills", "Electric bill", TODAY)
        page_loaded.reload()
        page_loaded.get_by_text("Electric bill").first.wait_for(
            state="visible", timeout=20_000
        )
        # Wait explicitly for at least one delete button to be rendered
        delete_btn = page_loaded.get_by_role("button", name="🗑️ Delete").first
        delete_btn.wait_for(state="visible", timeout=10_000)
        assert page_loaded.get_by_role("button", name="🗑️ Delete").count() >= 1

    # US3 – Monthly total visible in the summary
    def test_us3_monthly_total_displayed(self, page_loaded, api_url):
        add_expense(api_url, 60.0, "Food", "Groceries", TODAY)
        page_loaded.reload()
        page_loaded.get_by_text("Monthly Total", exact=False).first.wait_for(
            state="visible", timeout=15_000
        )
        assert page_loaded.get_by_text("Monthly Total").first.is_visible()

    # US4 – Category chart rendered
    def test_us4_category_chart_rendered(self, page_loaded, api_url):
        add_expense(api_url, 40.0, "Transport", "Train pass", TODAY)
        page_loaded.reload()
        page_loaded.get_by_text("Spending by Category", exact=False).first.wait_for(
            state="visible", timeout=15_000
        )
        assert page_loaded.get_by_text("Spending by Category").first.is_visible()

    def test_us4_daily_bar_chart_rendered(self, page_loaded, api_url):
        add_expense(api_url, 25.0, "Entertainment", "Cinema", TODAY)
        page_loaded.reload()
        page_loaded.get_by_text("Daily Spending This Month", exact=False).first.wait_for(
            state="visible", timeout=15_000
        )
        assert page_loaded.get_by_text("Daily Spending This Month").first.is_visible()

    # US5 – Delete via UI
    def test_us5_delete_expense_via_ui(self, page_loaded, api_url):
        add_expense(api_url, 99.0, "Shopping", "Shoes", TODAY)
        page_loaded.reload()
        page_loaded.get_by_text("Shoes").first.wait_for(
            state="visible", timeout=15_000
        )
        # Click the first Delete button
        page_loaded.get_by_role("button", name="🗑️ Delete").first.click()
        # Wait for the expense to disappear from the list
        page_loaded.get_by_text("Shoes").first.wait_for(
            state="hidden", timeout=15_000
        )
