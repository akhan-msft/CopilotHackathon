from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime, date, timezone
import uuid

app = Flask(__name__)
CORS(app)

# In-memory storage
expenses = []

CATEGORIES = ["Food", "Transport", "Entertainment", "Shopping", "Bills", "Health", "Other"]

def seed_sample_data():
    """Seed some sample expenses for demonstration."""
    sample_expenses = [
        {"category": "Food", "amount": 45.50, "description": "Weekly groceries", "date": "2026-03-01"},
        {"category": "Transport", "amount": 30.00, "description": "Monthly bus pass top-up", "date": "2026-03-02"},
        {"category": "Bills", "amount": 120.00, "description": "Electricity bill", "date": "2026-03-03"},
        {"category": "Entertainment", "amount": 15.99, "description": "Streaming subscription", "date": "2026-03-04"},
        {"category": "Food", "amount": 22.30, "description": "Lunch at cafe", "date": "2026-03-05"},
        {"category": "Shopping", "amount": 65.00, "description": "New shoes", "date": "2026-03-06"},
        {"category": "Health", "amount": 35.00, "description": "Pharmacy", "date": "2026-03-06"},
    ]
    for exp in sample_expenses:
        expenses.append({
            "id": str(uuid.uuid4()),
            "amount": exp["amount"],
            "category": exp["category"],
            "description": exp["description"],
            "date": exp["date"],
            "created_at": datetime.now(timezone.utc).isoformat()
        })

seed_sample_data()


@app.route("/api/categories", methods=["GET"])
def get_categories():
    return jsonify({"categories": CATEGORIES})


@app.route("/api/expenses", methods=["GET"])
def get_expenses():
    month = request.args.get("month")
    year = request.args.get("year")

    filtered = expenses
    if month and year:
        filtered = [
            e for e in expenses
            if e["date"].startswith(f"{year}-{int(month):02d}")
        ]
    elif month:
        current_year = str(date.today().year)
        filtered = [
            e for e in expenses
            if e["date"].startswith(f"{current_year}-{int(month):02d}")
        ]

    sorted_expenses = sorted(filtered, key=lambda x: x["date"], reverse=True)
    return jsonify({"expenses": sorted_expenses, "total": len(sorted_expenses)})


@app.route("/api/expenses", methods=["POST"])
def add_expense():
    data = request.get_json()

    if not data:
        return jsonify({"error": "Request body is required"}), 400

    required_fields = ["amount", "category", "description"]
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Field '{field}' is required"}), 400

    try:
        amount = float(data["amount"])
        if amount <= 0:
            return jsonify({"error": "Amount must be a positive number"}), 400
    except (ValueError, TypeError):
        return jsonify({"error": "Amount must be a valid number"}), 400

    if data["category"] not in CATEGORIES:
        return jsonify({"error": f"Invalid category. Must be one of: {', '.join(CATEGORIES)}"}), 400

    expense_date = data.get("date", date.today().isoformat())
    try:
        datetime.strptime(expense_date, "%Y-%m-%d")
    except ValueError:
        return jsonify({"error": "Date must be in YYYY-MM-DD format"}), 400

    expense = {
        "id": str(uuid.uuid4()),
        "amount": round(amount, 2),
        "category": data["category"],
        "description": data["description"].strip(),
        "date": expense_date,
        "created_at": datetime.now(timezone.utc).isoformat()
    }

    expenses.append(expense)
    return jsonify(expense), 201


@app.route("/api/expenses/<expense_id>", methods=["DELETE"])
def delete_expense(expense_id):
    global expenses
    original_count = len(expenses)
    expenses = [e for e in expenses if e["id"] != expense_id]

    if len(expenses) == original_count:
        return jsonify({"error": "Expense not found"}), 404

    return jsonify({"message": "Expense deleted successfully"}), 200


@app.route("/api/expenses/summary", methods=["GET"])
def get_summary():
    month = request.args.get("month", str(date.today().month))
    year = request.args.get("year", str(date.today().year))

    monthly_expenses = [
        e for e in expenses
        if e["date"].startswith(f"{year}-{int(month):02d}")
    ]

    total = sum(e["amount"] for e in monthly_expenses)

    by_category = {}
    for exp in monthly_expenses:
        cat = exp["category"]
        by_category[cat] = round(by_category.get(cat, 0) + exp["amount"], 2)

    # Daily totals for trend chart
    daily_totals = {}
    for exp in monthly_expenses:
        d = exp["date"]
        daily_totals[d] = round(daily_totals.get(d, 0) + exp["amount"], 2)

    return jsonify({
        "month": int(month),
        "year": int(year),
        "total": round(total, 2),
        "count": len(monthly_expenses),
        "by_category": by_category,
        "daily_totals": daily_totals
    })


@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "timestamp": datetime.now(timezone.utc).isoformat()})


if __name__ == "__main__":
    import os
    debug_mode = os.environ.get("FLASK_DEBUG", "false").lower() == "true"
    app.run(debug=debug_mode, port=5000)
