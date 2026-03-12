from flask import Flask, jsonify
from flask_socketio import SocketIO, emit
import requests

app = Flask(__name__, static_folder=".", template_folder=".")
app.config["SECRET_KEY"] = "chatwebsockets-secret"
socketio = SocketIO(app, cors_allowed_origins="*")


@app.route("/")
def index():
    return app.send_static_file("index.html")


@app.route("/api/users")
def get_users():
    response = requests.get("https://randomuser.me/api/?results=10", timeout=5)
    response.raise_for_status()
    data = response.json()
    users = [
        {
            "name": f"{u['name']['first']} {u['name']['last']}",
            "avatar": u["picture"]["medium"],
        }
        for u in data["results"]
    ]
    return jsonify(users)


@socketio.on("connect")
def on_connect():
    print("Client connected")


@socketio.on("disconnect")
def on_disconnect():
    print("Client disconnected")


@socketio.on("message")
def on_message(data):
    # data = {user, text, avatar}
    emit("message", data, broadcast=True)


if __name__ == "__main__":
    print("Starting chat server at http://127.0.0.1:5000")
    socketio.run(app, debug=True, host="127.0.0.1", port=5000)
