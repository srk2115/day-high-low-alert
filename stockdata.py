# import yfinance as yf
import commonfunctions as cf
import pandas as pd
from datetime import datetime, timedelta
from tvDatafeed import TvDatafeed,Interval

def connectTV():
  from tvDatafeed import TvDatafeed,Interval
  # get credentials for tradingview
  username = 'srk2115'
  password = 'Tv@2173@Abc'

  # initialize tradingview
  tv = TvDatafeed(username=username,password=password)
  return tv

def get_stock_data(stock, interval="15m", asondate=cf.getCurrentDate(), data_source = "yahoo", asondateonly=True, fut_contract=None, days=5):
  data = pd.DataFrame()
  enddate = asondate
  enddt = datetime.strptime(asondate, '%Y-%m-%d')
  enddt += timedelta(days=1)
  enddate = enddt.strftime('%Y-%m-%d')
  startdt = enddt - timedelta(days=days)
  startdate = startdt.strftime('%Y-%m-%d')
  asondt = datetime.strptime(asondate, '%Y-%m-%d')
  print(enddt - startdt)
  if (data_source == "yahoo"):
    stock = f"{stock}.NS"
    # try:
    #     print(f"data_source={data_source}, startdate={startdate}, enddate={enddate}")
    #     data = yf.download(stock, start=startdate, end=enddate, interval=interval, progress=False)
    #     if not data.empty:
    #       # but when I checked my data.columns it gave me the result as
    #       # MultiIndex([( 'Close', 'SUNPHARMA.NS'),
    #       # ( 'High', 'SUNPHARMA.NS'), ( 'Low', 'SUNPHARMA.NS'), ( 'Open', 'SUNPHARMA.NS'),
    #       # ('Volume', 'SUNPHARMA.NS')],
    #       #  names=['Price', 'Ticker'])

    #       # DataFrame has a MultiIndex for columns, you can remove the MultiIndex by resetting the columns
    #       # Remove MultiIndex from columns
    #       data.columns = data.columns.get_level_values(0)
    #       data.reset_index(inplace=True)
    #       # print(data.columns, "Date" in data.columns)
    #       if(not ("Date" in data.columns)):
    #         data["Date"] = pd.to_datetime(data['Datetime'])
    #         data["Date"] = data["Date"].dt.date
    #         data["Date"] = pd.to_datetime(data['Date'])
    #       data["open"] = data["Open"]
    #       data["high"] = data["High"]
    #       data["low"] = data["Low"]
    #       data["close"] = data["Close"]

    #       print(asondate, asondt)
    #       if(asondateonly):
    #         data = data[(data["Date"] >= f"{asondt}")]
    #     else:
    #       data = pd.DataFrame()
          
    # except Exception as e:
    #   print(f"In Exception {e}")
  else: #tv
    stock = f"{stock}"
    
    try:
      current_date = cf.getCurrentDate()
      currentdt = datetime.strptime(current_date, '%Y-%m-%d')
      days = (currentdt - startdt).days
      # print(days)
      try:
          tv = connectTV()
      except Exception as e:
        print(f"Exception: {e}")
        
      n_bars = days
      intvl = Interval.in_daily
      if (interval == "1d"):
        intvl = Interval.in_daily
        n_bars = days
      elif (interval == "15m"):
        intvl = Interval.in_15_minute
        n_bars = days*((4*6)+1)
      elif (interval == "5m"):
        intvl = Interval.in_5_minute
        n_bars = days*((12*6)+3)
      elif (interval == "3m"):
        intvl = Interval.in_3_minute
        n_bars = days*((20*6)+5)
      elif (interval == "1m"):
        intvl = Interval.in_1_minute
        n_bars = days*((60*6)+15)
      else:
        intvl = Interval.in_daily
        n_bars = days
      print(f"params: {startdt} - {days} - {stock} - {intvl} - {n_bars} - {fut_contract}")  
      data = tv.get_hist(stock,'NSE',interval=intvl,n_bars=n_bars,fut_contract=fut_contract)
      # print(data.tail())
      # data = tv.get_hist(stock,'NSE',interval=intvl,n_bars=n_bars)
      # print(data)
      if data.shape[0] > 0:
        data.reset_index(inplace=True)
        data["Open"] = data["open"]
        data["High"] = data["high"]
        data["Low"] = data["low"]
        data["Close"] = data["close"]
        data["Volume"] = data["volume"]
        data["Datetime"] = data["datetime"]
        data["Date"] = pd.to_datetime(data['datetime'])
        data["Date"] = data["Date"].dt.date
        data["Date"] = pd.to_datetime(data['Date'])
        asondt = datetime.strptime(asondate, '%Y-%m-%d')
        data = data[(data["Date"] <= f"{asondt}")]
        if(asondateonly):
          data = data[(data["Date"] >= f"{asondt}")]
    except:
      print(f"in exception for {stock}") 
  return data

def get_stock_data_from_to(stock, interval="15m", asondate=cf.getCurrentDate(), data_source = "yahoo", asondateonly=True, fut_contract=None, days=5, fromdate="2024-01-01", todate=cf.getCurrentDate()):
  data = pd.DataFrame()
  enddate = todate
  enddt = datetime.strptime(enddate, '%Y-%m-%d')
  enddt += timedelta(days=1)
  enddate = enddt.strftime('%Y-%m-%d')
  startdt = enddt - timedelta(days=2)
  startdate = startdt.strftime('%Y-%m-%d')
  asondt = datetime.strptime(asondate, '%Y-%m-%d')
  print(enddt - startdt)
  if (data_source == "yahoo"):
    stock = f"{stock}.NS"
  else: #tv
    stock = f"{stock}"
    
    try:
      current_date = cf.getCurrentDate()
      currentdt = datetime.strptime(current_date, '%Y-%m-%d')
      days = (currentdt - startdt).days
      # print(days)
      try:
          tv = connectTV()
      except Exception as e:
        print(f"Exception: {e}")
        
      n_bars = days
      intvl = Interval.in_daily
      if (interval == "1d"):
        intvl = Interval.in_daily
        n_bars = days
      elif (interval == "15m"):
        intvl = Interval.in_15_minute
        n_bars = days*((4*6)+1)
      elif (interval == "5m"):
        intvl = Interval.in_5_minute
        n_bars = days*((12*6)+3)
      elif (interval == "3m"):
        intvl = Interval.in_3_minute
        n_bars = days*((20*6)+5)
      elif (interval == "1m"):
        intvl = Interval.in_1_minute
        n_bars = days*((60*6)+15)
      else:
        intvl = Interval.in_daily
        n_bars = days
      print(f"params: {startdt} - {days} - {stock} - {intvl} - {n_bars} - {fut_contract}")  
      data = tv.get_hist(stock,'NSE',interval=intvl,n_bars=n_bars,fut_contract=fut_contract)
      # print(data.tail())
      # data = tv.get_hist(stock,'NSE',interval=intvl,n_bars=n_bars)
      # print(data)
      if data.shape[0] > 0:
        data.reset_index(inplace=True)
        data["Open"] = data["open"]
        data["High"] = data["high"]
        data["Low"] = data["low"]
        data["Close"] = data["close"]
        data["Volume"] = data["volume"]
        data["Datetime"] = data["datetime"]
        data["Date"] = pd.to_datetime(data['datetime'])
        data["Date"] = data["Date"].dt.date
        data["Date"] = pd.to_datetime(data['Date'])
        asondt = datetime.strptime(asondate, '%Y-%m-%d')
        data = data[(data["Date"] <= f"{asondt}")]
        if(asondateonly):
          data = data[(data["Date"] >= f"{asondt}")]
    except:
      print(f"in exception for {stock}") 
  return data
