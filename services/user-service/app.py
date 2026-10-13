from flask import Flask, jsonify

app = Flask(__name__)

USERS = [
    {"id": 1, "name": "Anagha"},
    {"id": 2, "name": "Ravi"},
]

@app.route("/health")
def health():
    return jsonify({"status": "ok"}), 200

@app.route("/users")
def get_users():
    return jsonify(USERS), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)