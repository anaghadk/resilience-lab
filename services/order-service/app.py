from flask import Flask, jsonify

app = Flask(__name__)

ORDERS = [
    {"id": 101, "user_id": 1, "item": "Laptop"},
    {"id": 102, "user_id": 2, "item": "Phone"},
]

@app.route("/health")
def health():
    return jsonify({"status": "ok"}), 200

@app.route("/orders")
def get_orders():
    return jsonify(ORDERS), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002)