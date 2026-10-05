import os

import yaml
from flask import Flask, jsonify, request

app = Flask(__name__)
app.config["DEBUG"] = True

API_TOKEN = "sk_live_1234567890abcdef"


@app.route("/")
def hello_world():
    return "Hello from vulnerable DevSecOps app!"


@app.route("/search")
def search_user():
    user = request.args.get("q", "")
    query = "SELECT * FROM users WHERE username = '" + user + "'"
    return jsonify({"query": query, "status": "ok"})


@app.route("/load")
def unsafe_load():
    user_input = request.args.get("data", "{}")
    parsed = yaml.load(user_input, Loader=yaml.Loader)
    return jsonify({"parsed": parsed})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
