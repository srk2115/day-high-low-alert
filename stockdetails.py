import pandas as pd
stock_details = pd.read_csv("StockDetails.csv")
stock_details = stock_details.drop(columns=['Unnamed: 0'])
stock_details.set_index('tv_symbol', inplace=True) 
# Convert the DataFrame to a dictionary 
stock_details_dict = stock_details.to_dict(orient='index')
stock_details.reset_index(inplace=True)


def round_to_nearest(num, base):
    return base * round(num/base)

def generate_dates(start_date, count, holidays):
    from datetime import datetime, timedelta
    dates = []
    current_date = datetime.strptime(start_date, "%y%m%d")

    for _ in range(count):
        is_holiday = False
        while current_date.strftime("%y%m%d") in holidays:
            is_holiday = True
            current_date -= timedelta(days=1)
        dates.append(current_date.strftime("%y%m%d"))
        if is_holiday: #if holiday current_date would have been lessen by a day, here we restore it for next week calculation
            current_date += timedelta(days=1)
        current_date += timedelta(weeks=1)
    
    return dates

def getExpiryDates():
  import requests

  url = "https://www.nseindia.com/api/option-chain-indices?symbol=NIFTY"
  headers = {
      "User-Agent": "Mozilla/5.0",
      "Referer": "https://www.nseindia.com/option-chain"
  }

  session = requests.Session()
  session.get("https://www.nseindia.com", headers=headers)  # Set cookies
  response = session.get(url, headers=headers)
  data = response.json()

  # Example: print available expiry dates
  expiry_dates = data['records']['expiryDates']
  # print(expiry_dates)
  return expiry_dates


def getExpiryDatesA():
    # Example usage
    start_date = "241205"

    count = 57

    holidays = ["240122", "240126", "240308", "240325",
                "240329", "240411", "240417", "240501",
                "240520", "240617", "240717", "240815",
                "241002", "241115", "241120", "241225",
                "250126", "250226", "250314", "250331",
                "250406", "250410", "250414", "250418", 
                "250501", "250607", "250706", "250815", 
                "250827", "251002", "251002", "251105", 
                "251120", "251122", "251225"]


    # start_date = "241129"  # YYMMDD format
    # count = 10
    # holidays = ["241206", "241213", "241220"]  # List of holidays in YYMMDD format

    expiry_dates = generate_dates(start_date, count, holidays)

    # print(expiry_dates[0])
    return expiry_dates

def getLotSize(symbol):
  return stock_details_dict[symbol]["lotsize"]

def getStrikeSpread(symbol):
  return stock_details_dict[symbol]["strike_spread"]

def getRoundOffBase(symbol):
  symbol_roundoff = {"BSE":100,"NIFTY":50,"IGL":10, "CESC": 10, "MCX":100}
  r = symbol_roundoff.get(symbol, 10)
  return r

def getNearExpiryEx():
  from datetime import datetime
  expiry_dates = getExpiryDates()
  converted = [datetime.strptime(d, "%d-%b-%Y").strftime("%Y%m%d") for d in expiry_dates]
  # print(converted)
  near_expiry = converted[0]#str(high_broken_time)[5:7]
  return near_expiry  

def getNearMonthlyExpiryEx():
  from datetime import datetime
  expiry_dates = getExpiryDates()
  converted = [datetime.strptime(d, "%d-%b-%Y").strftime("%Y%m%d") for d in expiry_dates]
  # print(converted)
  near_month_expiry = converted[0]#str(high_broken_time)[5:7]
  for i in converted:
    # print(near_month_expiry, i, near_month_expiry[2:4], i[2:4])
    if(near_month_expiry[4:6] != i[4:6]):
      break
    else:
      near_month_expiry = i
  return near_month_expiry  

def getNearExpiry():
  expiry_dates = getExpiryDatesA()
  near_month_expiry = expiry_dates[0]#str(high_broken_time)[5:7]
  for i in expiry_dates:
    # print(near_month_expiry, i, near_month_expiry[2:4], i[2:4])
    if(near_month_expiry[2:4] != i[2:4]):
      break
    else:
      near_month_expiry = i
  print(near_month_expiry)
  return near_month_expiry  

def generate_strikes(symbol, atm_price, num_strikes, distance):
  atm_strike = round_to_nearest(atm_price, getStrikeSpread(symbol))
  strikes = []
  start_strike = atm_strike - (num_strikes) * distance
  for i in range(num_strikes * 2 + 1):
      strikes.append(start_strike + i * distance)
  return strikes

def extract_scripe_name(input_str):
    import re

    # Use regular expression to match alphabetic part at the beginning of the string
    match = re.match(r'^[A-Z]+', input_str)
    if match:
        return match.group(0)
    return None
  
def fno_expiries():
  return [
    # "27-Feb-2025",
    "06-Mar-2025",
    "13-Mar-2025",
    "20-Mar-2025",
    "27-Mar-2025",
    "03-Apr-2025",
    "24-Apr-2025",
    "26-Jun-2025",
    "25-Sep-2025",
    "24-Dec-2025",
    "25-Jun-2026",
    "31-Dec-2026",
    "24-Jun-2027",
    "30-Dec-2027",
    "29-Jun-2028",
    "28-Dec-2028",
    "28-Jun-2029",
    "27-Dec-2029"
  ]
  
def get_monthly_expiries():
  from datetime import datetime
  from collections import defaultdict
  
  expiries = fno_expiries()
  expiries_by_month = defaultdict(list)

  for expiry in expiries:
      date = datetime.strptime(expiry, "%d-%b-%Y")
      expiries_by_month[(date.year, date.month)].append(date)
  
  monthly_expiries = [max(dates).strftime("%d-%b-%Y") for dates in expiries_by_month.values()]
  
  return monthly_expiries