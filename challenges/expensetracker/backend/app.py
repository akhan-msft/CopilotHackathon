from flask import Flask, jsonify, request
from flask_cors import CORS
from datetime import datetime
import uuid

app = Flask(__name__)
CORS(app)

# In-memory storage for expenses
expenses = []

CATEGORIES = ["Food", "Transport", "Entertainment", "Shopping", "Bills", "Other"]


@app.route("/categories", methods=["GET"])
def get_categories():
    return jsonify(CATEGORIES)


@app.route("/expenses", methods=["GET"])
def get_expenses():
    return jsonify(expenses)


@app.route("/expenses", methods=["POST"])
def add_expense():
    data = request.get_json()

    if not data:
        return jsonify({"error": "No data provided"}), 400

    amount = data.get("amount")
    category = data.get("category")
    description = data.get("description", "")
    date = data.get("date", datetime.now().strftime("%Y-%m-%d"))

    if amount is None or amount <= 0:
        return jsonify({"error": "Amount must be a positive number"}), 400
    if not category or category not in CATEGORIES:
        return jsonify({"error": f"Category must be one of {CATEGORIES}"}), 400

    expense = {
        "id": str(uuid.uuid4()),
        "amount": float(amount),
        "category": category,
        "description": description,
        "date": date,
    }
    expenses.append(expense)
    return jsonify(expense), 201


@app.route("/expenses/<expense_id>", methods=["DELETE"])
def delete_expense(expense_id):
    global expenses
    original_count = len(expenses)
    expenses = [e for e in expenses if e["id"] != expense_id]
    if len(expenses) == original_count:
        return jsonify({"error": "Expense not found"}), 404
    return jsonify({"message": "Expense deleted"}), 200


@app.route("/expenses/summary", methods=["GET"])
def get_summary():
    now = datetime.now()
    current_month = now.strftime("%Y-%m")

    monthly_expenses = [e for e in expenses if e["date"].startswith(current_month)]
    monthly_total = sum(e["amount"] for e in monthly_expenses)

    category_totals = {}
    for category in CATEGORIES:
        category_totals[category] = sum(
            e["amount"] for e in monthly_expenses if e["category"] == category
        )

    return jsonify(
        {
            "monthly_total": monthly_total,
            "category_totals": category_totals,
            "month": current_month,
            "expense_count": len(monthly_expenses),
        }
    )


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
