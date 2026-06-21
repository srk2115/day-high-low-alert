from flask import Flask, render_template, session, jsonify, request


import requests
import pandas as pd
import os

app = Flask(__name__)
app.secret_key = "nifty-secret"

# Load data once
df = pd.read_csv("data/nifty.csv")

df['datetime'] = pd.to_datetime(df['datetime'])
df = df.sort_values('datetime').reset_index(drop=True)

def send_pushbullet(access_token, title, message):

    response = requests.post(
        "https://api.pushbullet.com/v2/pushes",
        headers={
            "Access-Token": access_token,
            "Content-Type": "application/json"
        },
        json={
            "type": "note",
            "title": title,
            "body": message
        }
    )

    print(response.status_code)
    print(response.text)

@app.route("/")
def index():

    session['current_index'] = 1

    first_candle = df.iloc[0]

    return render_template(
        "replay_candle.html",
        first_high=first_candle['high'],
        first_low=first_candle['low']
    )


@app.route("/next")
def next_candle():

    idx = session.get('current_index', 1)

    if idx >= len(df):
        return jsonify({
            "finished": True
        })

    first_candle = df.iloc[0]

    first_high = first_candle['high']
    first_low = first_candle['low']

    current = df.iloc[idx]
    previous = df.iloc[idx - 1]

    alert = None
    pushbullet_token = session.get(
        "pushbullet_token"
    )
    
    # Upside cross
    if (
        previous['close'] <= first_high
        and current['close'] > first_high
    ):
        alert = f"🚀 BREAKOUT ABOVE FIRST HIGH ({first_high})"
        alert = (
            f"🚀 BREAKOUT ABOVE FIRST HIGH "
            f"({first_high})"
        )

        send_pushbullet(
            pushbullet_token,
            "NIFTY BREAKOUT",
            alert
        )


    # Downside cross
    elif (
        previous['close'] >= first_low
        and current['close'] < first_low
    ):
        alert = f"🔻 BREAKDOWN BELOW FIRST LOW ({first_low})"
        alert = (
            f"🔻 BREAKDOWN BELOW FIRST LOW "
            f"({first_low})"
        )

        send_pushbullet(
            pushbullet_token,
            "NIFTY BREAKDOWN",
            alert
        )
    session['current_index'] = idx + 1

    return jsonify({
        "datetime": str(current['datetime']),
        "open": float(current['open']),
        "high": float(current['high']),
        "low": float(current['low']),
        "close": float(current['close']),
        "alert": alert,
        "finished": False
    })

@app.route("/save_token", methods=["POST"])
def save_token():

    data = request.get_json()

    session["pushbullet_token"] = data.get("token")

    return {
        "message": "Pushbullet token saved"
    }

@app.route("/test_pushbullet")
def test_pushbullet():

    token = session.get(
        "pushbullet_token"
    )

    send_pushbullet(
        token,
        "NIFTY Replay",
        "Pushbullet is working."
    )

    return {
        "message": "Test notification sent"
    }

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(debug=True, host='127.0.0.1', port=port)