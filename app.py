
import os
from datetime import datetime, timezone

import requests
from flask import Flask, jsonify

app = Flask(__name__)

API_TOKEN = os.environ.get("FOOTBALL_DATA_TOKEN")
API_BASE = "https://api.football-data.org/v4"


@app.route("/")
def home():
    return jsonify({
        "application": "FootPredict Africa",
        "status": "online",
        "message": "Le serveur fonctionne."
    })


@app.route("/api/matches")
def matches():
    if not API_TOKEN:
        return jsonify({
            "error": "Le serveur API n'est pas encore configuré."
        }), 503

    today = datetime.now(timezone.utc).date().isoformat()

    headers = {"X-Auth-Token": API_TOKEN}
    params = {"dateFrom": today, "dateTo": today}

    competitions = ["PD", "PL", "FL1", "BL1", "SA"]

    results = []

    for competition in competitions:
        try:
            response = requests.get(
                f"{API_BASE}/competitions/{competition}/matches",
                headers=headers,
                params=params,
                timeout=15
            )

            if response.status_code == 200:
                data = response.json()

                for match in data.get("matches", []):
                    results.append({
                        "competition": match.get("competition", {}).get("name"),
                        "date": match.get("utcDate"),
                        "status": match.get("status"),
                        "homeTeam": match.get("homeTeam", {}).get("name"),
                        "awayTeam": match.get("awayTeam", {}).get("name"),
                        "homeScore": match.get("score", {}).get("fullTime", {}).get("home"),
                        "awayScore": match.get("score", {}).get("fullTime", {}).get("away")
                    })

            elif response.status_code == 429:
                return jsonify({
                    "error": "Limite de requêtes API atteinte. Réessaie plus tard."
                }), 429

        except requests.RequestException:
            continue

    return jsonify({
        "date": today,
        "count": len(results),
        "matches": results
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
