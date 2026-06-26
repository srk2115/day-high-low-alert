from flask import Flask, render_template, session, jsonify, request


import requests
import pandas as pd
import os

import yfinance as yf
import numpy as np

app = Flask(__name__)
app.secret_key = "nifty-secret"

# Load data once
df = pd.read_csv("data/NIFTY.csv")

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

@app.route("/backtest_asondate", methods=["POST"])
def backtest_asondate():
    data = request.get_json()
    print(data)
    session["asondate"] = data.get("asondate")
    asondate = session["asondate"]
    print(f"Ason date: {session['asondate']}")

    print(asondate)
    print(df.head())
    dft = df[df["Date"] == asondate]#.reset_index(drop=True)
    print(dft.head())
    session['current_index'] = 1

    # # session['df'] = dft
    # session['df'] = dft.to_dict(orient="records")

    print(dft.iloc[0])
    first_candle = dft.iloc[0]
    first_high = float(first_candle['high']);
    first_low =  float(first_candle['low']);

    print(first_high, first_low)

    return jsonify({
        "status": "success",
        "message": f"Data loaded successfully for {session['asondate']}",
        "first_high": first_high, # Float conversion prevents JSON errors
        "first_low": first_low
    })    

@app.route("/backtest")
def backtest():
    unique_dates = df['datetime'].dt.date.unique().tolist()
    print(unique_dates)
    # session['current_index'] = 1

    # first_candle = df.iloc[0]

    return render_template(
        "replay_candle.html",
        trade_dates = unique_dates
        # first_high=first_candle['high'],
        # first_low=first_candle['low']
    )

@app.route("/testtv")
def testtv():
    return "";


@app.route("/next_ason", methods=["POST"])
def next_ason():
    data = request.get_json()

    session["username"] = data.get("username")
    session["password"] = data.get("password")

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


@app.route("/next_candle_asondate", methods=["POST"])
def next_candle_asondate():

    idx = session.get('current_index', 0)
    # # dft = session['df']
    # stored_data = session.get('df', [])
    # dft = pd.DataFrame(stored_data)

    data = request.get_json()
    print(data)
    session["asondate"] = data.get("asondate")
    asondate = session["asondate"]
    print(f"Ason date: {session['asondate']}")

    print(asondate)
    print(df.shape)
    dft = df[df["Date"] == asondate].reset_index(drop=True)
    print(dft.shape)

    idx = idx + 1
    session['current_index'] = idx
    if idx >= len(dft):
        return jsonify({
            "finished": True
        })

    asondate = session["asondate"]
    # print(asondate)
    # dft = df[df["datetime"] == asondate]

    first_candle = dft.iloc[0]
    print(f"first candle: {first_candle}")
    first_high = first_candle['high']
    first_low = first_candle['low']
    print(f"first candle HL: {first_high}, {first_low}")

    current = dft.iloc[idx]
    previous = dft.iloc[idx - 1]
    print(f"previous candle: {previous}")
    print(f"curernt candle: {current}")

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
    

    return jsonify({
        "datetime": str(current['datetime']),
        "open": float(current['open']),
        "high": float(current['high']),
        "low": float(current['low']),
        "close": float(current['close']),
        "alert": alert,
        "finished": False
    })

@app.route("/next")
def next_candle():

    idx = session.get('current_index', 1)
    # dft = session['df']
    stored_data = session.get('df', [])
    dft = pd.DataFrame(stored_data)

    if idx >= len(dft):
        return jsonify({
            "finished": True
        })

    asondate = session["asondate"]
    # print(asondate)
    # dft = df[df["datetime"] == asondate]

    first_candle = dft.iloc[0]
    print(f"first candle: {first_candle}")
    first_high = first_candle['high']
    first_low = first_candle['low']
    print(f"first candle HL: {first_high}, {first_low}")

    current = dft.iloc[idx]
    previous = dft.iloc[idx - 1]
    print(f"previous candle: {previous}")
    print(f"curernt candle: {current}")

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

@app.route("/save_tv", methods=["POST"])
def save_tv():

    data = request.get_json()

    session["username"] = data.get("username")
    session["password"] = data.get("password")
    print(session["username"], session["password"]);

    return {
        "message": "Trading View details saved."
    }

@app.route("/save_token", methods=["POST"])
def save_token():

    data = request.get_json()

    session["pushbullet_token"] = data.get("token")

    return {
        "message": "Pushbullet token saved."
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

@app.route("/")
def index():
    error_message = "No data yet."
    first_high = 0
    first_low = 0
    return render_template(
        "live.html",
        first_high=first_high,
        first_low=first_low,
        error_message=error_message
    )

@app.route("/get_live_data", methods=["POST"])
def get_live_data():
    username = request.form.get("username")
    password = request.form.get("password")
    print(f"Username: {username}, Password: {password}")

    from datetime import datetime
    # import warnings

    import commonfunctions as cf
    import stockdata as sd
    import stockdetails as stkdtls

    import pandas as pd
    # warnings.filterwarnings("ignore")
    import matplotlib.pyplot as plt
    import mplfinance as mpf
    import io

    asondate = cf.getCurrentDate()
    symbol = "NIFTY"
    data_source = "tv"
    data1 = sd.get_stock_data(symbol, interval="5m", asondate=asondate, data_source=data_source, asondateonly=True, username=username, password=password)
    print(data1.shape)
    print(data1)

    error_message = ""
    first_candle = []
    first_high = None
    first_low = None
    alert = None

    if data1.shape[0] > 0:
        first_candle = data1.iloc[0]
        first_high=first_candle['high']
        first_low=first_candle['low']

        print(first_candle, first_high, first_low)

        if(data1.shape[0]>1):
            current_candle = data1.iloc[-1]
            current_candle_high = current_candle['high']
            current_candle_low = current_candle['low']
            print(current_candle, current_candle_high, current_candle_low)

        if(data1.shape[0]>2):
            prev_candle = data1.iloc[-2]
            prev_candle_high = prev_candle['high']
            prev_candle_low = prev_candle['low']
            print(prev_candle, prev_candle_high, prev_candle_low)

            pushbullet_token = session.get(
                "pushbullet_token"
            )

            previous = prev_candle
            current = current_candle
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
        return jsonify({
            "datetime": str(current['datetime']),
            "first_high": float(first_high),
            "first_low": float(first_low),
            "open": float(current['open']),
            "high": float(current['high']),
            "low": float(current['low']),
            "close": float(current['close']),
            "alert": alert,
            "finished": False,
            "error_message": error_message
        })
    else:
        error_message = "No data found yet." 

        return jsonify({
            "datetime": None,
            "first_high": None,
            "first_low": None,
            "open": None,
            "high": None,
            "low": None,
            "close": None,
            "alert": alert,
            "finished": False,
            "error_message": ""
        })

@app.route("/live_yf")
def get_live_data_yf():
    symbol = "NIFTY"

    # auto_adjust = True
    # print(f"Fetching latest daily data for {symbol} with auto_adjust={auto_adjust}...")
    # df1 = yf.download(
    #         tickers=f"{symbol}.NS",
    #         period="1d",
    #         interval="1d",
    #         auto_adjust=auto_adjust, 
    #         threads=False,     
    #         timeout=15,
    #         progress=False
    #     )
    # if isinstance(df1.columns, pd.MultiIndex):
    #     # If a batch multi-index leaks through, extract ONLY the current symbol's data slice
    #     ticker_str = f"{symbol}.NS"
    #     if ticker_str in df1.columns.get_level_values(1):
    #         df1 = df1.xs(ticker_str, axis=1, level=1)
    #     else:
    #         # Fallback to level 0 if layout varies
    #         df1.columns = df1.columns.get_level_values(0)
    # else:
    #     # If it's already flat, just normalize index layout
    #     df1.columns = [str(col).strip() for col in df1.columns]

    # first_candle = df1.iloc[0]
    # last_candle = df1.iloc[-1]

    # return render_template(
    #     "replay_candle.html",
    #     first_high=first_candle['high'],
    #     first_low=first_candle['low']
    # )

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    if os.environ.get("RENDER"):
        # Render Environment Settings
        app.run(debug=True, host='0.0.0.0', port=port)
    else:
        # Your Local Workspace Settings
        app.run(debug=True, host='127.0.0.1', port=port)
