from secrets_client import client
import requests
import json
import os
from uuid import uuid4
from urllib.parse import urlencode
from flask import Flask, redirect, request, session, Response

client_id = client.get("CLIENT_ID")
client_secret = client.get("CLIENT_SECRET")
# if not client_id or not client_secret:
#     raise SystemExit("Missing CLIENT_ID or CLIENT_SECRET in secrets.client")

OAUTH_AUTHORIZE = "https://oauth.battle.net/authorize"
OAUTH_TOKEN = "https://oauth.battle.net/token"
# Must match the redirect URI configured in your Blizzard OAuth client
REDIRECT_URI = "http://localhost:5000/callback"
SCOPE = "wow.profile"

app = Flask(__name__)
# For dev only: set a secret key so session can store state
app.secret_key = os.environ.get("FLASK_SECRET") or os.urandom(24)

@app.route("/authorize")
def authorize():
    state = uuid4().hex
    session["oauth_state"] = state
    params = {
        "client_id": client_id,
        "scope": SCOPE,
        "response_type": "code",
        "redirect_uri": REDIRECT_URI,
        "state": state,
    }
    return redirect(f"{OAUTH_AUTHORIZE}?{urlencode(params)}")

@app.route("/callback")
def callback():
    error = request.args.get("error")
    if error:
        return Response(json.dumps({"error": error, "details": request.args.get("error_description")}), mimetype="application/json", status=400)

    state = request.args.get("state")
    if not state or state != session.get("oauth_state"):
        return Response(json.dumps({"error": "invalid_state"}), mimetype="application/json", status=400)

    code = request.args.get("code")
    if not code:
        return Response(json.dumps({"error": "missing_code"}), mimetype="application/json", status=400)

    # Exchange authorization code for tokens (server-side, using client secret)
    data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": REDIRECT_URI,
    }
    token_resp = requests.post(OAUTH_TOKEN, auth=(client_id, client_secret), data=data)
    try:
        token_json = token_resp.json()
    except ValueError:
        return Response(json.dumps({"error": "invalid_token_response", "text": token_resp.text}), mimetype="application/json", status=500)

    if token_resp.status_code != 200:
        return Response(json.dumps({"error": "token_request_failed", "response": token_json}), mimetype="application/json", status=token_resp.status_code)

    access_token = token_json.get("access_token")
    token_type = token_json.get("token_type")
    if not access_token or not token_type:
        return Response(json.dumps({"error": "missing_token_fields", "response": token_json}), mimetype="application/json", status=500)

    # Example API call using the access token
    personal_achiev = "https://eu.api.blizzard.com/profile/wow/character/sylvanas/ruana/achievements?namespace=profile-eu&locale=en_GB"
    headers = {"Authorization": f"{token_type} {access_token}"}
    api_resp = requests.get(personal_achiev, headers=headers)

    result = {
        "token_response": token_json,
        "api_status": api_resp.status_code,
        "api_response": api_resp.json() if api_resp.ok else {"text": api_resp.text}
    }
    return Response(json.dumps(result, indent=2), mimetype="application/json")

if __name__ == "__main__":
    # Run on 0.0.0.0 so it's reachable from the host in the devcontainer
    # Use a single-threaded dev server for simplicity
    app.run(host="0.0.0.0", port=5000, debug=True)