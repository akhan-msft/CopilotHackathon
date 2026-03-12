"""
conftest.py – starts the Flask-SocketIO chat server as a subprocess
before the test session and tears it down afterwards.
"""
import os
import subprocess
import sys
import time

import pytest
import requests

BASE_URL = "http://127.0.0.1:5000"
SERVER_DIR = os.path.join(os.path.dirname(__file__), "..")


def _wait_for_server(url: str, timeout: int = 30) -> None:
    """Poll url until it responds or timeout expires."""
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            requests.get(url, timeout=2)
            return
        except Exception:
            time.sleep(0.5)
    raise RuntimeError(f"Chat server did not start within {timeout}s")


@pytest.fixture(scope="session")
def chat_server():
    """Start server.py once for the whole test session."""
    proc = subprocess.Popen(
        [sys.executable, "server.py"],
        cwd=SERVER_DIR,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    _wait_for_server(BASE_URL)
    yield BASE_URL
    proc.terminate()
    proc.wait(timeout=10)


@pytest.fixture
def server_url(chat_server):
    return chat_server


@pytest.fixture
def ctx():
    """Mutable dict for sharing state between BDD steps within a scenario."""
    return {}
