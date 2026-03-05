"""
conftest.py – starts Flask backend + Streamlit frontend as subprocesses
before the E2E test session and tears them down after.
"""
import subprocess
import sys
import time
import os
import requests
import pytest

BACKEND_PORT = 5100          # separate port so we don't clash with a manual run
FRONTEND_PORT = 8601
BACKEND_URL = f"http://localhost:{BACKEND_PORT}"
FRONTEND_URL = f"http://localhost:{FRONTEND_PORT}"

ROOT = os.path.join(os.path.dirname(__file__), "..")
BACKEND_DIR = os.path.join(ROOT, "backend")
FRONTEND_DIR = os.path.join(ROOT, "frontend")


def _wait_for(url: str, timeout: int = 30) -> None:
    """Poll url until it responds or timeout expires."""
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            requests.get(url, timeout=2)
            return
        except Exception:
            time.sleep(0.5)
    raise RuntimeError(f"Service at {url} did not start within {timeout}s")


@pytest.fixture(scope="session")
def backend_server():
    """Start the Flask backend on BACKEND_PORT for the test session."""
    env = os.environ.copy()
    proc = subprocess.Popen(
        [
            sys.executable, "-c",
            f"import sys; sys.path.insert(0,''); "
            f"from app import app; "
            f"app.run(host='0.0.0.0', port={BACKEND_PORT}, debug=False, use_reloader=False)",
        ],
        cwd=BACKEND_DIR,
        env=env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    _wait_for(f"{BACKEND_URL}/categories")
    yield BACKEND_URL
    proc.terminate()
    proc.wait(timeout=10)


@pytest.fixture(scope="session")
def frontend_server(backend_server):
    """Start the Streamlit frontend pointing at the test backend."""
    env = os.environ.copy()
    env["BACKEND_URL"] = backend_server          # picked up by conftest patch below
    proc = subprocess.Popen(
        [
            sys.executable, "-m", "streamlit", "run", "app.py",
            "--server.port", str(FRONTEND_PORT),
            "--server.headless", "true",
            "--server.runOnSave", "false",
            "--browser.gatherUsageStats", "false",
        ],
        cwd=FRONTEND_DIR,
        env=env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    _wait_for(FRONTEND_URL, timeout=40)
    yield FRONTEND_URL
    proc.terminate()
    proc.wait(timeout=10)


@pytest.fixture(autouse=True)
def reset_backend(backend_server):
    """Delete all expenses between tests so each test starts clean."""
    expenses = requests.get(f"{backend_server}/expenses").json()
    for exp in expenses:
        requests.delete(f"{backend_server}/expenses/{exp['id']}")
    yield


# Make the backend / frontend URLs available to tests via simple fixtures
@pytest.fixture(scope="session")
def api_url(backend_server):
    return backend_server


@pytest.fixture(scope="session")
def ui_url(frontend_server):
    return frontend_server
