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
    unique_dates.sort(reverse=True)
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

@app.route("/get_live_data_nifty") #, methods=["POST"])
def get_live_data_nifty():
    # username = request.form.get("username")
    # password = request.form.get("password")
    username = session.get("username","")
    password = session.get("password","")
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

@app.route("/get_live_data", methods=["POST"])
def get_live_data():
    data = request.get_json()
    username = session.get("username","")
    password = session.get("password","")
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
    raw_tickers = data.get("tickers", "")
    tickers = [t.strip() for t in raw_tickers.split(",") if t.strip()] #session.get("tickers", ["NIFTY", "BANKNIFTY", "NIFTY_MID_SELECT", "NIFTYJR"])         # Nifty 50 index , "SENSEX", 
    print(tickers)
    df_dict = {}
    for ticker in tickers:
        print(f"Fetching 5m data for {ticker}")
        df = sd.get_stock_data(ticker, interval="5m", asondate=asondate, data_source="tv", asondateonly=True, username=username, password=password)
        if(not df is None):
            print(f"{ticker}: {df.shape[0]} rows")
            df['datetime'] = pd.to_datetime(df['datetime'])
            df_dict[ticker] = df.reset_index(drop=True)

    error_message = ""
    first_candle = []
    first_high = None
    first_low = None
    alert = None
    message = ""

    pushbullet_token = session.get(
        "pushbullet_token"
    )

    unique_dates = []
    for ticker, df in df_dict.items():
        if df.empty:
            print(f"No data for {ticker}")
            continue
        # each df should be in same shape
        if df.shape[0] != df_dict[tickers[0]].shape[0]:
            print(f"Data shape mismatch for {ticker}: {df.shape} vs {df_dict[tickers[0]].shape}")
            error_message = f"Data shape mismatch for {ticker}: {df.shape} vs {df_dict[tickers[0]].shape}"
            break
            # exit(1)
        else:
            print(f"Data shape match for {ticker}: {df.shape} vs {df_dict[tickers[0]].shape}")
            # unique_dates = df['datetime'].dt.date.unique().tolist()
            unique_dates.extend(df['datetime'].dt.date.unique().tolist())
            unique_dates = sorted(list(set(unique_dates)))
            
    dft_dict = {}
    for ticker in tickers:
        dft_dict[ticker] = df_dict[ticker] #df_dict[ticker][df_dict[ticker]['Date'] == '2026-07-01'].reset_index(drop=True)

    df_details_dict = {}
    trades = []
    first_key = list(dft_dict.keys())[0]
    rows_count = dft_dict[first_key].shape[0]
    print(f"First key: {first_key}, Number of rows: {dft_dict[first_key].shape[0]}")
    high_str = ""
    low_str = ""
    for idx, row in dft_dict[first_key].iterrows():
        highs = 0
        lows = 0
        high_tickers_count = 0
        low_tickers_count = 0
        print(idx, row['datetime'], len(dft_dict[first_key])-1)
        if(idx != len(dft_dict[first_key])-1):
            for ticker in tickers:
                if(ticker not in df_details_dict):
                    df_details_dict[ticker] = {}
                    df_details_dict[ticker]["highs"] = []
                    df_details_dict[ticker]["lows"] = []

                print(f"{ticker}: {df_details_dict[ticker].get('high')}, {df_details_dict[ticker].get('low')}")
                # print(dft_dict[ticker].iloc[idx])
                if "high" in df_details_dict[ticker]:
                    if(dft_dict[ticker].iloc[idx]["high"] > df_details_dict[ticker].get("high")):
                        print(f"New High for {ticker}!")
                        highs += 1
                        df_details_dict[ticker]["high"] = dft_dict[ticker].iloc[idx].get("high")
                        df_details_dict[ticker]["high_Index"] = idx
                        df_details_dict[ticker]["high_at"] = row['datetime']
                else:
                    df_details_dict[ticker]["high"] = dft_dict[ticker].iloc[idx].get("high")
                    df_details_dict[ticker]["high_Index"] = idx
                    df_details_dict[ticker]["high_at"] = row['datetime']

                if "low" in df_details_dict[ticker]:
                    if(dft_dict[ticker].iloc[idx]["low"] < df_details_dict[ticker].get("low")):
                        print(f"New Low for {ticker}!")
                        lows += 1
                        df_details_dict[ticker]["low"] = dft_dict[ticker].iloc[idx].get("low")
                        df_details_dict[ticker]["low_Index"] = idx
                        df_details_dict[ticker]["low_at"] = row['datetime']
                else:
                    df_details_dict[ticker]["low"] = dft_dict[ticker].iloc[idx].get("low")
                    df_details_dict[ticker]["low_Index"] = idx
                    df_details_dict[ticker]["low_at"] = row['datetime']
            else:
                current_datetime = dft_dict[first_key].iloc[idx]['datetime']
                if(dft_dict[ticker].iloc[idx]["high"] > df_details_dict[ticker].get("high")):
                    high_tickers_count += 1
                    df_details_dict[ticker]["high"] = dft_dict[ticker].iloc[idx].get("high")
                    df_details_dict[ticker]["high_Index"] = idx
                    df_details_dict[ticker]["high_at"] = row['datetime']
                if(dft_dict[ticker].iloc[idx]["low"] < df_details_dict[ticker].get("low")):
                    low_tickers_count += 1
                    df_details_dict[ticker]["low"] = dft_dict[ticker].iloc[idx].get("low")
                    df_details_dict[ticker]["low_Index"] = idx
                    df_details_dict[ticker]["low_at"] = row['datetime']

            print("")
        print(f"Highs: {highs}, Lows: {lows}")
        if(highs > 0 or lows > 0):
            error_message = "High or Lows found."
            print(f"High or Lows found")
            if (highs == len(tickers)):
                for ticker in tickers:
                    df_details_dict[ticker]["highs"].append([dft_dict[ticker].iloc[idx]["high"], dft_dict[ticker].iloc[idx]["close"], idx, dft_dict[ticker].iloc[idx]["datetime"]])
                
            if (lows == len(tickers)):
                for ticker in tickers:
                    df_details_dict[ticker]["lows"].append([dft_dict[ticker].iloc[idx]["low"], dft_dict[ticker].iloc[idx]["close"], idx, dft_dict[ticker].iloc[idx]["datetime"]])
        else:
            error_message = "No new highs or lows found yet."
            print(f"All tickers did not have new highs or lows yet")

        for ticker in tickers:
            print(df_details_dict[ticker])
            if(len(df_details_dict[ticker]["highs"]) > 0):
                print(f"{ticker} highs: {df_details_dict[ticker]['highs']}")
                high = df_details_dict[ticker]['highs'][-1]
                error_message = f"All tickers were reached High at {high[3]}"
            if(len(df_details_dict[ticker]["lows"]) > 0):
                print(f"{ticker} lows: {df_details_dict[ticker]['lows']}")
                low = df_details_dict[ticker]['lows'][-1]
                error_message = f"All tickers were reached Low at {low[3]}"

                                
        print(f"High tickers count: {high_tickers_count}, Low tickers count: {low_tickers_count}")
        if(high_tickers_count == len(tickers)):
            print(f"All tickers have new high at index {idx} ({dft_dict[first_key].iloc[idx]['datetime']})")
            message = f"All tickers have new high at index {idx} ({dft_dict[first_key].iloc[idx]['datetime']})"
            high_str = ""
            for ticker in tickers:
                high_str = f"{high_str}\n{dft_dict[ticker].iloc[idx]['high']}"
            alert = (
                f"🚀 All tickers have new high "
                f"({high_str})"
            )

            send_pushbullet(
                pushbullet_token,
                "NIFTY BREAKOUT",
                alert
            )

            for ticker in tickers:
                df_details_dict[ticker]["highs"].append([dft_dict[ticker].iloc[idx]["high"], dft_dict[ticker].iloc[idx]["close"], idx, dft_dict[ticker].iloc[idx]["datetime"]])

        if(low_tickers_count == len(tickers)):
            print(f"All tickers have new low at index {idx} ({dft_dict[first_key].iloc[idx]['datetime']})")
            message = f"All tickers have new low at index {idx} ({dft_dict[first_key].iloc[idx]['datetime']})"
            low_str = ""
            for ticker in tickers:
                low_str = f"{low_str}\n{dft_dict[ticker].iloc[idx]['low']}"
            alert = (
                f"🚀 All tickers have new low "
                f"({low_str})"
            )

            send_pushbullet(
                pushbullet_token,
                "NIFTY BREAKOUT",
                alert
            )

            for ticker in tickers:
                # print(f"{ticker}, Low: {df_details_dict[ticker]['low']} ({df_details_dict[ticker]['low_Index']}), Index: {idx}")
                df_details_dict[ticker]["lows"].append([dft_dict[ticker].iloc[idx]["low"], dft_dict[ticker].iloc[idx]["close"], idx, dft_dict[ticker].iloc[idx]["datetime"]])

    print(f"Rows: {rows_count}")
    if(rows_count != 0):
        for ticker in tickers:
            high_str = f"{high_str}\n{df_details_dict[ticker].get('high')}"
            low_str = f"{low_str}\n{df_details_dict[ticker].get('low')}"
            message = f"{message}\n{ticker.ljust(25, ' ')}: Current High: {dft_dict[ticker].iloc[idx]['high']}, Current Low: {dft_dict[ticker].iloc[idx]['low']}"
            message = f"{message} (Day High - {df_details_dict[ticker].get('high')}, Day Low - {df_details_dict[ticker].get('low')})"
    else:
        error_message = "No data found yet."

    if(rows_count != 0):
        return jsonify({
            "datetime": str(dft_dict[first_key].iloc[-1]['datetime']),
            # "current_high": float(first_high),
            # "first_low": float(first_low),
            # "open": float(current['open']),
            # "high": float(current['high']),
            # "low": float(current['low']),
            # "close": float(current['close']),
            "alert": alert,
            "finished": False,
            "message": message,
            "error_message": error_message
        })
    else:
        return jsonify({
            "datetime": None,
            # "first_high": None,
            # "first_low": None,
            # "open": None,
            # "high": None,
            # "low": None,
            # "close": None,
            "alert": alert,
            "finished": False,
            "error_message": error_message
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
