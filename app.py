
from flask import Flask, render_template, jsonify
import requests

app = Flask(__name__)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/api/mcx-prices")
def mcx_prices():
    try:
        response = requests.get(
            "https://api.oropocket.com/public/prices",
            timeout=10
        )
        response.raise_for_status()

        raw = response.json()
        data = raw["data"]

        gold = float(data["gold"]["buy"])
        silver = float(data["silver"]["buy"])

        if gold <= 0 or silver <= 0:
            raise ValueError("Invalid price")

        return jsonify({
            "source": "OroPocket",
            "currency": "INR",
            "unit": "gram",
            "timestamp": data.get("timestamp"),
            "gold": {"buy": gold},
            "silver": {"buy": silver}
        })

    except (
        requests.RequestException,
        KeyError,
        TypeError,
        ValueError
    ) as error:
        app.logger.warning("Price feed unavailable: %s", error)

        return jsonify({
            "error": "Live prices unavailable. Enter rates manually."
        }), 502


@app.route("/health")
def health():
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    app.run(debug=True, port=5000)
