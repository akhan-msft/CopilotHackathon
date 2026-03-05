"""
Backend unit tests for the Expense Tracker Flask API.

Covers all five core user stories:
  US1 – Add a new expense with amount, category, and description
  US2 – View all expenses in a list
  US3 – See total spending for the current month
  US4 – View spending breakdown by category
  US5 – Delete an expense
"""
import sys
import os
import pytest

# Ensure the backend package is on the path regardless of working directory
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import app as flask_app  # noqa: E402


@pytest.fixture()
def client():
    """Return a Flask test client with a clean in-memory expense list."""
    flask_app.app.config["TESTING"] = True
    # Reset shared state before every test
    flask_app.expenses.clear()
    with flask_app.app.test_client() as c:
        yield c


# ── Helpers ──────────────────────────────────────────────────────────────────

def _add(client, amount, category, description="test", date="2026-03-05"):
    return client.post(
        "/expenses",
        json={"amount": amount, "category": category,
              "description": description, "date": date},
    )


# ── US1: Add a new expense ────────────────────────────────────────────────────

class TestAddExpense:
    def test_add_valid_expense_returns_201(self, client):
        resp = _add(client, 25.00, "Food", "Breakfast")
        assert resp.status_code == 201

    def test_add_returns_expense_fields(self, client):
        resp = _add(client, 25.00, "Food", "Breakfast")
        data = resp.get_json()
        assert data["amount"] == 25.00
        assert data["category"] == "Food"
        assert data["description"] == "Breakfast"
        assert data["date"] == "2026-03-05"
        assert "id" in data

    def test_add_all_categories(self, client):
        for cat in ["Food", "Transport", "Entertainment", "Shopping", "Bills", "Other"]:
            resp = _add(client, 10.0, cat)
            assert resp.status_code == 201, f"Expected 201 for category {cat}"

    def test_add_defaults_date_to_today(self, client):
        from datetime import datetime
        resp = client.post("/expenses", json={"amount": 5.0, "category": "Food"})
        assert resp.status_code == 201
        today = datetime.now().strftime("%Y-%m-%d")
        assert resp.get_json()["date"] == today

    def test_add_rejects_negative_amount(self, client):
        resp = _add(client, -1.0, "Food")
        assert resp.status_code == 400
        assert "error" in resp.get_json()

    def test_add_rejects_zero_amount(self, client):
        resp = _add(client, 0, "Food")
        assert resp.status_code == 400

    def test_add_rejects_unknown_category(self, client):
        resp = _add(client, 10.0, "Luxury")
        assert resp.status_code == 400
        assert "error" in resp.get_json()

    def test_add_rejects_missing_body(self, client):
        resp = client.post("/expenses", json={})
        assert resp.status_code == 400

    def test_add_rejects_no_json(self, client):
        resp = client.post("/expenses", data="not json",
                           content_type="text/plain")
        # Flask returns 415 Unsupported Media Type for non-JSON content-type,
        # which is still a valid client-error rejection.
        assert resp.status_code in (400, 415)


# ── US2: View all expenses ────────────────────────────────────────────────────

class TestListExpenses:
    def test_empty_list_returns_200(self, client):
        resp = client.get("/expenses")
        assert resp.status_code == 200
        assert resp.get_json() == []

    def test_list_returns_added_expenses(self, client):
        _add(client, 10.0, "Food", "item1")
        _add(client, 20.0, "Bills", "item2")
        resp = client.get("/expenses")
        assert resp.status_code == 200
        data = resp.get_json()
        assert len(data) == 2

    def test_list_contains_all_fields(self, client):
        _add(client, 15.0, "Transport", "Bus")
        item = client.get("/expenses").get_json()[0]
        for field in ("id", "amount", "category", "description", "date"):
            assert field in item, f"Missing field: {field}"

    def test_list_categories_endpoint(self, client):
        resp = client.get("/categories")
        assert resp.status_code == 200
        cats = resp.get_json()
        assert isinstance(cats, list)
        assert "Food" in cats
        assert len(cats) == 6


# ── US3: Monthly total ────────────────────────────────────────────────────────

class TestMonthlyTotal:
    def test_monthly_total_sums_current_month(self, client):
        from datetime import datetime
        today = datetime.now().strftime("%Y-%m-%d")
        _add(client, 50.0, "Food", date=today)
        _add(client, 30.0, "Bills", date=today)
        summary = client.get("/expenses/summary").get_json()
        assert summary["monthly_total"] == 80.0

    def test_monthly_total_excludes_other_months(self, client):
        from datetime import datetime
        today = datetime.now().strftime("%Y-%m-%d")
        _add(client, 100.0, "Food", date=today)
        _add(client, 999.0, "Shopping", date="2025-01-15")  # previous year
        summary = client.get("/expenses/summary").get_json()
        assert summary["monthly_total"] == 100.0

    def test_monthly_total_zero_when_no_expenses(self, client):
        summary = client.get("/expenses/summary").get_json()
        assert summary["monthly_total"] == 0

    def test_summary_expense_count(self, client):
        from datetime import datetime
        today = datetime.now().strftime("%Y-%m-%d")
        _add(client, 10.0, "Food", date=today)
        _add(client, 20.0, "Food", date=today)
        summary = client.get("/expenses/summary").get_json()
        assert summary["expense_count"] == 2


# ── US4: Category breakdown ───────────────────────────────────────────────────

class TestCategoryBreakdown:
    def test_summary_returns_all_categories(self, client):
        summary = client.get("/expenses/summary").get_json()
        totals = summary["category_totals"]
        for cat in ["Food", "Transport", "Entertainment", "Shopping", "Bills", "Other"]:
            assert cat in totals

    def test_category_totals_correct(self, client):
        from datetime import datetime
        today = datetime.now().strftime("%Y-%m-%d")
        _add(client, 40.0, "Food", date=today)
        _add(client, 10.0, "Food", date=today)
        _add(client, 25.0, "Transport", date=today)
        totals = client.get("/expenses/summary").get_json()["category_totals"]
        assert totals["Food"] == 50.0
        assert totals["Transport"] == 25.0
        assert totals["Bills"] == 0

    def test_category_totals_only_current_month(self, client):
        from datetime import datetime
        today = datetime.now().strftime("%Y-%m-%d")
        _add(client, 100.0, "Entertainment", date=today)
        _add(client, 999.0, "Entertainment", date="2025-06-01")
        totals = client.get("/expenses/summary").get_json()["category_totals"]
        assert totals["Entertainment"] == 100.0


# ── US5: Delete an expense ────────────────────────────────────────────────────

class TestDeleteExpense:
    def test_delete_existing_expense_returns_200(self, client):
        expense_id = _add(client, 20.0, "Food").get_json()["id"]
        resp = client.delete(f"/expenses/{expense_id}")
        assert resp.status_code == 200

    def test_delete_removes_expense_from_list(self, client):
        expense_id = _add(client, 20.0, "Food").get_json()["id"]
        client.delete(f"/expenses/{expense_id}")
        remaining = client.get("/expenses").get_json()
        assert all(e["id"] != expense_id for e in remaining)

    def test_delete_non_existent_returns_404(self, client):
        resp = client.delete("/expenses/does-not-exist")
        assert resp.status_code == 404

    def test_delete_one_of_many(self, client):
        id1 = _add(client, 10.0, "Food", "keep").get_json()["id"]
        id2 = _add(client, 20.0, "Bills", "delete me").get_json()["id"]
        client.delete(f"/expenses/{id2}")
        remaining = [e["id"] for e in client.get("/expenses").get_json()]
        assert id1 in remaining
        assert id2 not in remaining
