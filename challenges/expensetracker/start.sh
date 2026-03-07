#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────────────
# start.sh – Launch the Expense Tracker backend + frontend in isolated venvs
# Usage:  chmod +x start.sh && ./start.sh
# ─────────────────────────────────────────────────────────────────────────────
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$SCRIPT_DIR/backend"
FRONTEND_DIR="$SCRIPT_DIR/frontend"

echo ""
echo "======================================================"
echo "  💰  Expense Tracker – Startup Script"
echo "======================================================"
echo ""

# ── Backend ──────────────────────────────────────────────────────────────────
echo "📦 Setting up backend virtual environment..."
cd "$BACKEND_DIR"
if [ ! -d ".venv" ]; then
  python3 -m venv .venv
fi
source .venv/bin/activate
pip install -q -r requirements.txt
deactivate

echo "🚀 Starting Flask backend on http://localhost:5000 ..."
cd "$BACKEND_DIR"
source .venv/bin/activate
python app.py &
BACKEND_PID=$!
deactivate
echo "   Backend PID: $BACKEND_PID"

# Give Flask a moment to start
sleep 2

# ── Frontend ─────────────────────────────────────────────────────────────────
echo ""
echo "📦 Setting up frontend virtual environment..."
cd "$FRONTEND_DIR"
if [ ! -d ".venv" ]; then
  python3 -m venv .venv
fi
source .venv/bin/activate
pip install -q -r requirements.txt
deactivate

echo "🚀 Starting Streamlit frontend on http://localhost:8501 ..."
cd "$FRONTEND_DIR"
source .venv/bin/activate
streamlit run app.py --server.port 8501 --server.headless true &
FRONTEND_PID=$!
deactivate
echo "   Frontend PID: $FRONTEND_PID"

echo ""
echo "======================================================"
echo "  ✅  Both services are running!"
echo "  🔗  Frontend:  http://localhost:8501"
echo "  🔗  Backend:   http://localhost:5000"
echo ""
echo "  Press Ctrl+C to stop both services."
echo "======================================================"
echo ""

# Trap Ctrl+C and kill both processes
trap "echo ''; echo '🛑 Stopping services...'; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit 0" INT TERM

# Wait for both
wait $BACKEND_PID $FRONTEND_PID
