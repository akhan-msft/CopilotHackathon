# WebSocket Chat – Test Guide

## Overview

The test suite uses **pytest-bdd** (Gherkin feature files) and **pytest-playwright**
to validate the WebSocket chat application end-to-end in a real browser.

Tests are fully self-contained: `conftest.py` automatically starts `server.py`
before the session and shuts it down afterwards — no manual server step needed
when running via pytest.

---

## Prerequisites

### 1. Python environment

Create and activate a virtual environment inside `challenges/chatwebsockets/`:

```powershell
cd challenges\chatwebsockets
python -m venv .venv
.\.venv\Scripts\Activate.ps1   # Windows PowerShell
# source .venv/bin/activate    # macOS / Linux
```

### 2. Install dependencies

```powershell
pip install -r requirements.txt
```

`requirements.txt` includes:

| Package | Purpose |
|---|---|
| `flask` | Web framework |
| `flask-socketio` | WebSocket (Socket.IO) support |
| `requests` | HTTP client used by server + conftest |
| `pytest` | Test runner |
| `pytest-bdd` | Gherkin/BDD scenario support |
| `pytest-playwright` | Playwright browser automation |

### 3. Install Playwright browsers

```powershell
playwright install chromium
```

---

## Running the Tests

### Headless (default — faster, no browser window)

```powershell
pytest tests/ -v
```

### Headed (watch tests run in a real browser window)

```powershell
pytest tests/ -v --headed
```

### Run a single scenario by name

```powershell
pytest tests/ -v -k "test_send_button"
```

### Run only the broadcast test

```powershell
pytest tests/ -v -k "broadcast"
```

---

## Test Structure

```
tests/
├── conftest.py               # Session fixture: auto-starts/stops server.py
├── features/
│   └── chat.feature          # Gherkin scenarios (source of truth)
└── test_chat.py              # pytest-bdd step implementations + broadcast test
```

---

## Scenarios Covered

| # | Scenario | What is verified |
|---|---|---|
| 1 | Login screen loads with user cards | 10 user cards appear from randomuser.me API |
| 2 | Selecting a user enters the chat | Login screen hides, chat screen shows |
| 3 | Chat header shows the selected user | Header name matches the clicked user |
| 4 | Sending a message via the Send button | Bubble appears, input clears |
| 5 | Sending a message via Enter key | Bubble appears on Enter keypress |
| 6 | Empty message is not sent | Message count unchanged on empty send |
| 7 | HTML in messages is escaped | `<script>` rendered as text, no alert fires |
| 8 | Real-time broadcast (two browser contexts) | Message sent by User A appears in User B's tab, not marked as "own" |

---

## How It Works

1. **`conftest.py`** starts `server.py` as a subprocess on `http://127.0.0.1:5000`
   and polls until it responds before handing control to pytest.
2. Each BDD test navigates to the server URL via a Playwright-managed Chromium
   browser. Steps are defined in `test_chat.py` and matched to lines in
   `chat.feature`.
3. The broadcast test (`test_broadcast_between_two_users`) opens **two separate
   browser contexts** (equivalent to two incognito windows) to simulate two
   different users connected at the same time.
4. After all tests finish, `conftest.py` terminates the server process.

---

## Troubleshooting

| Problem | Solution |
|---|---|
| `playwright install` not found | Run `pip install pytest-playwright` then retry |
| Port 5000 already in use | Stop any existing `server.py` process, or change `BASE_URL` in `conftest.py` and `server.py` |
| Tests time out on login screen | Check internet access — user cards are fetched from `https://randomuser.me` |
| `ScopeMismatch` fixture error | Do not name your own fixture `base_url`; pytest-playwright reserves that name |
