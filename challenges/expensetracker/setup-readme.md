# Expense Tracker – Setup & Usage Guide

Everything you need to install, run, and test the Expense Tracker locally.

---

## Prerequisites

- **Python 3.9+** – [download](https://www.python.org/downloads/)
- Two terminal windows (one for the backend, one for the frontend)

---

## 1 · Backend (Flask REST API)

### Install dependencies

```bash
cd challenges/expensetracker/backend
pip install -r requirements.txt
```

### Start the server

```bash
python app.py
```

The API will be available at **http://localhost:5000**.

To enable the Flask debugger (development only):

```bash
FLASK_DEBUG=true python app.py
```

### API endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/categories` | List all expense categories |
| `GET` | `/expenses` | List all expenses |
| `POST` | `/expenses` | Add a new expense (see body below) |
| `DELETE` | `/expenses/<id>` | Delete an expense by ID |
| `GET` | `/expenses/summary` | Monthly total and per-category breakdown |

**POST `/expenses` – request body**

```json
{
  "amount": 42.50,
  "category": "Food",
  "description": "Lunch",
  "date": "2026-03-05"
}
```

`category` must be one of: `Food`, `Transport`, `Entertainment`, `Shopping`, `Bills`, `Other`.  
`date` defaults to today if omitted.

### Quick smoke-test (curl)

```bash
# Add an expense
curl -s -X POST http://localhost:5000/expenses \
  -H "Content-Type: application/json" \
  -d '{"amount": 12.50, "category": "Food", "description": "Coffee"}' | python3 -m json.tool

# List all expenses
curl -s http://localhost:5000/expenses | python3 -m json.tool

# Monthly summary
curl -s http://localhost:5000/expenses/summary | python3 -m json.tool
```

---

## 2 · Frontend (Streamlit)

### Install dependencies

```bash
cd challenges/expensetracker/frontend
pip install -r requirements.txt
```

### Start the app

```bash
streamlit run app.py
```

Streamlit will open **http://localhost:8501** in your browser automatically.

### Point the frontend at a different backend

By default the frontend connects to `http://localhost:5000`. Override this with the
`BACKEND_URL` environment variable:

```bash
BACKEND_URL=http://my-server:5000 streamlit run app.py
```

---

## 3 · Running the Tests

All tests live under `challenges/expensetracker/` and are discovered via `pytest.ini`.

### Backend unit tests only (no browser, fastest)

```bash
cd challenges/expensetracker
python -m pytest backend/tests/ -v
```

### Full test suite (unit + end-to-end API + Playwright browser tests)

The E2E tests spin up the Flask and Streamlit servers automatically, so **no manual
server startup is required**.

**One-time Playwright browser install** (only needed the first time):

```bash
python -m playwright install chromium
```

**Run all 50 tests:**

```bash
cd challenges/expensetracker
python -m pytest -v --browser chromium
```

Expected output:

```
50 passed in ~20s
```

### Test structure

| Path | Type | Count |
|------|------|-------|
| `backend/tests/test_api.py` | Flask test-client unit tests | 24 |
| `tests/test_e2e.py` – `TestE2EApi` | Live HTTP round-trip tests | 18 |
| `tests/test_e2e.py` – `TestE2EUI` | Playwright browser tests | 8 |

The `tests/conftest.py` fixture starts isolated Flask (`:5100`) and Streamlit (`:8601`)
processes for the E2E session and resets all data between every test automatically.

---

## 4 · Running Everything Together (Quick Start)

Open **three** terminals from the repo root:

```bash
# Terminal 1 – backend
cd challenges/expensetracker/backend && pip install -r requirements.txt && python app.py

# Terminal 2 – frontend
cd challenges/expensetracker/frontend && pip install -r requirements.txt && streamlit run app.py

# Terminal 3 – tests (after servers are up, or let the test suite manage its own processes)
cd challenges/expensetracker && python -m pytest -v --browser chromium
```

---

## 5 · Project Structure

```
challenges/expensetracker/
├── setup-readme.md          ← you are here
├── pytest.ini               ← pytest configuration
├── README.md                ← challenge description
├── backend/
│   ├── app.py               ← Flask REST API
│   ├── requirements.txt
│   └── tests/
│       └── test_api.py      ← backend unit tests
├── frontend/
│   ├── app.py               ← Streamlit UI
│   └── requirements.txt
└── tests/
    ├── conftest.py          ← server lifecycle fixtures
    └── test_e2e.py          ← end-to-end tests
```
