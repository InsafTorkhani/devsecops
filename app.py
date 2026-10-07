import os

import yaml
from flask import Flask, jsonify, request

app = Flask(__name__)

API_TOKEN = os.environ.get("API_TOKEN")


@app.after_request
def add_security_headers(response):
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Content-Security-Policy"] = "default-src 'self'"
    response.headers["Permissions-Policy"] = "geolocation=(), camera=(), microphone=()"
    return response


@app.route("/")
def hello_world():
    return "Hello from vulnerable DevSecOps app!"


@app.route("/search")
def search_user():
    user = request.args.get("q", "")
    query = "SELECT * FROM users WHERE username = ?"
    return jsonify({"query": query, "params": [user], "status": "ok"})


@app.route("/load")
def unsafe_load():
    user_input = request.args.get("data", "{}")
    parsed = yaml.safe_load(user_input)
    return jsonify({"parsed": parsed})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    # Container must bind all interfaces; access is limited by Docker port mapping.
    app.run(host="0.0.0.0", port=port)  # nosec B104