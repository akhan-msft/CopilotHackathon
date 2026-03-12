"""
Simple static file server for the Expense Tracker frontend.
Serves index.html on port 8501.
"""

import http.server
import os
import functools

PORT = int(os.environ.get("FRONTEND_PORT", 8501))
DIRECTORY = os.path.dirname(os.path.abspath(__file__))


def main():
    handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=DIRECTORY)
    with http.server.HTTPServer(("0.0.0.0", PORT), handler) as server:
        print(f"Frontend serving on http://localhost:{PORT}")
        server.serve_forever()


if __name__ == "__main__":
    main()
