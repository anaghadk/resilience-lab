from flask import Flask, jsonify
import requests

app = Flask(__name__)

#Done while testing locally, but when containerised, localhost means the container itself 
# not the neighbouring container. 
# USER_SERVICE_URL = "http://localhost:5001"
# ORDER_SERVICE_URL = "http://localhost:5002"
USER_SERVICE_URL = "http://user-service:5001"
ORDER_SERVICE_URL = "http://order-service:5002"

@app.route("/health")
def health():
    return jsonify({"status": "ok"}), 200

@app.route("/summary")
def summary():
    try:
        users = requests.get(f"{USER_SERVICE_URL}/users", timeout=3).json()
        orders = requests.get(f"{ORDER_SERVICE_URL}/orders", timeout=3).json()
        return jsonify({"users": users, "orders": orders}), 200
    except requests.exceptions.RequestException as e:
        return jsonify({"error": str(e)}), 503

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)