'''
This is an options-trading API.
It utilizes both calls and puts.

Daily bias information:
- Daily Bias is determined by averaging the bias of the following ETFs:
    - SPY
    - DIA
    - NDAQ
    - UUP
- UUP bias is flipped as it often trends contrary to the market

Stock filtering information:
- Runs using TipRanks data to find the top 50:
    - Top losers
    - Top Gainers
    - Most Active
- The above three categories constitute the traded tickers for the day.
- Unwanted tickers are filtered upon request in the disliked_tickers list

Cash Reservation:
- 10% of Cash will always remain unallocated.

SPY strategy:
- 10% of Cash is traded daily into the SPY ETF
- Trade based on SPY daily bias calculation
    - If SPY daily bias in neuteral, market bias will be used
    - If SPY bias and market bias are both neuteral, no SPY trade will be taken

Call strategy:    
- Buy call if score is >= 7/11
    - MACD bullish + 1
    - bullish trend + 1
    - high volume + 1
    - RSI oversold + 1
    - price below lower bollinger band + 1
    - stochastic oversold + 1
    - stochastic crossover + 1
    - high ATR + 1
    - price near fibonacci levels + 1
    - ADX strong trend + 1
    - dip in uptrend + 2
    - price above upper bollinger band - 1

Put Strategy:
- Buy put if score is >= 7/11
    - MACD bearish + 1
    - bearish trend + 1
    - high volume + 1
    - RSI overbought + 1
    - price above upper bollinger band + 1
    - stochastic overbought + 1
    - stochastic crossover down + 1
    - high ATR + 1
    - price near fibonacci resistance + 1
    - ADX strong trend + 1
    - pop in downtrend + 2
    - price below lower band - 1


Position Sizing:
- Each position is about 10% of total equity

Stop loss:
- Sell if price drops 10% since entry

Take Profit:
- Sell when price action shows signs of reversal or weakness near key liquidity zones, identified by:
    - A liquidity sweep (price wicks beyond recent highs/lows but closes back inside)
    - A reversal after a breakout (price breaks out on high volume, then closes back inside)

Hold:
- Price pushes beyond liquidity zones with volume confirmation (strong move past recent highs/lows)
    
Contracts expire in 1-2 weeks (with the exclusion of daily SPY trading). 
All orders are executed at market price.
Open positions are evaluated to be sold each loop.
'''
# ---------- IMPORTANT ----------
'''
TURN PAPER TO TRUE OR FALSE: LINE 141
USER MUST ENTER ALPACA API KEY AND SECRET IN LINES 147-148
'''
# ---------- IMPORTANT ----------



# --- Standard Library ---
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import time
import threading
import random

# --- Third-Party Libraries ---
import pandas as pd
import numpy as np
import talib
import alpaca_trade_api as tradeapi
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from fake_useragent import UserAgent

# --- Alpaca Trading API ---
from alpaca.trading.client import TradingClient
from alpaca.trading.enums import (
    AssetStatus,
    ExerciseStyle,
    OrderSide,
    OrderType,
    TimeInForce,
    ContractType,
)
from alpaca.trading.requests import (
    GetOptionContractsRequest,
    MarketOrderRequest,
)

# --- Alpaca Market Data: Historical & Live ---
from alpaca.data.timeframe import TimeFrame
from alpaca.data.historical.stock import (
    StockHistoricalDataClient,
    StockBarsRequest,
)
from alpaca.data.historical.option import OptionHistoricalDataClient
from alpaca.data.requests import OptionLatestQuoteRequest


# ----------------------------------------------------------------------------------
# Account Credentials --------------------------------------------------------------
# ----------------------------------------------------------------------------------



# SET TRUE FOR PAPER TRADING, FALSE FOR LIVE
paper = True

# BASE URL (CHANGES IS PAPER OR LIVE)
base_url = 'https://paper-api.alpaca.markets' if paper else 'https://api.alpaca.markets'

# API CREDENTIALS
API_KEY = 'PKJ98QG1L8JN17WAL25Y'
SECRET_KEY = 'tvvY58ULCrfjWunmGmeWfJJqv22p4xHtsGihx5Xi'

# Standard API (REST) client
api = tradeapi.REST(API_KEY, SECRET_KEY, base_url=base_url)

# Trading Client (Alpaca v2)
trade_client = TradingClient(API_KEY, SECRET_KEY, paper=paper)

# Market Data Client (stocks)
data_client = StockHistoricalDataClient(API_KEY, SECRET_KEY)

# Option Historical Data Client
option_data_client = OptionHistoricalDataClient(API_KEY, SECRET_KEY)



# ----------------------------------------------------------------------------------
# Determine Daily Bias -------------------------------------------------------------
# ----------------------------------------------------------------------------------



def fetch_data(symbol, start_date, end_date, timeframe=TimeFrame.Day):
    try:
        request = StockBarsRequest(
            symbol_or_symbols=[symbol],
            timeframe=timeframe,
            start=start_date,
            end=end_date
        )
        bars = data_client.get_stock_bars(request)
        return bars.df
    except Exception as e:
        print(f"Error fetching data for {symbol}: {e}")
        return pd.DataFrame()


def calculate_rsi(df, period=14):
    delta = df['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))


def calculate_moving_averages(df):
    df['50_MA'] = df['close'].rolling(window=50).mean()
    df['100_MA'] = df['close'].rolling(window=100).mean()


def calculate_bias(df):
    if df is None or df.empty or len(df) < 100:
        return "Insufficient Data"

    calculate_moving_averages(df)
    df['RSI'] = calculate_rsi(df)
    df.dropna(subset=['50_MA', '100_MA', 'RSI'], inplace=True)

    if df.empty:
        return "Insufficient Data"

    latest = df.iloc[-1]
    trend = "Bullish" if latest['50_MA'] > latest['100_MA'] else "Bearish" if latest['50_MA'] < latest['100_MA'] else "Neutral"
    rsi_cond = "Overbought - Bearish" if latest['RSI'] > 70 else "Oversold - Bullish" if latest['RSI'] < 30 else "Neutral RSI"
    price_action = "Bullish" if latest['close'] > latest['open'] else "Bearish" if latest['close'] < latest['open'] else "Neutral Action"

    signals = [trend, rsi_cond, price_action]
    bull_score = signals.count("Bullish") + signals.count("Oversold - Bullish")
    bear_score = signals.count("Bearish") + signals.count("Overbought - Bearish")

    if bull_score >= 2:
        return "Bullish"
    elif bear_score >= 2:
        return "Bearish"
    else:
        return "Neutral"


def calculate_overall_bias(biases):
    bull_count = sum(1 for bias in biases.values() if bias == "Bullish")
    bear_count = sum(1 for bias in biases.values() if bias == "Bearish")

    if bull_count > bear_count:
        return "Bullish"
    elif bear_count > bull_count:
        return "Bearish"
    return "Neutral"


def confirm_overall_bias(overall_bias):
    print(f"\nOverall Market Bias: {overall_bias}")
    response = input("Do you agree with the bias? (Y to confirm / N to flip) \n").strip().upper()

    if response == 'Y':
        print(f'{overall_bias} bias saved')
        return overall_bias
    elif response == 'N':
        overall_bias = "Bearish" if overall_bias == "Bullish" else "Bullish"
        print(f'{overall_bias} bias saved')
        return overall_bias


def daily_bias():
    symbols = ['SPY', 'NDAQ', 'DIA', 'UUP']
    start = datetime.now() - timedelta(days=200)
    end = datetime.now()

    raw_biases = {}
    spy_bias = None

    for symbol in symbols:
        data = fetch_data(symbol, start, end)
        bias = calculate_bias(data)

        if symbol == 'SPY':
            spy_bias = bias

        if symbol == 'UUP':
            if bias == "Bullish":
                market_bias = "Bearish"
            elif bias == "Bearish":
                market_bias = "Bullish"
            else:
                market_bias = "Neutral"
            print(f"{symbol}: {bias} (Market {market_bias})")
            raw_biases[symbol] = market_bias
        else:
            print(f"{symbol}: {bias}")
            raw_biases[symbol] = bias

    overall = calculate_overall_bias(raw_biases)
    overall_bias = confirm_overall_bias(overall)

    return overall_bias, spy_bias


def trade_option_for_spy(trade_client, option_data_client, current_price, direction, current_cash):
    try:
        now = datetime.now(tz=ZoneInfo("America/New_York")) # TIME ZONE
        today = now.date()

        contract_type = ContractType.CALL if direction.upper() == "CALL" else ContractType.PUT

        req = GetOptionContractsRequest(
            underlying_symbols=["SPY"],
            status=AssetStatus.ACTIVE,
            expiration_date = today, # SPY CONTRACT EXPIRATION DATE
            type=contract_type,
            style=ExerciseStyle.AMERICAN,
            limit=100
        )

        res = trade_client.get_option_contracts(req)
        contracts = res.option_contracts

        if not contracts:
            print(f"No {direction.upper()} contracts found for SPY.")
            return None

        expiration_dates = sorted(set(c.expiration_date for c in contracts))
        preferred_exp = expiration_dates[0]
        contracts = [c for c in contracts if c.expiration_date == preferred_exp]

        candidates = (
            sorted([c for c in contracts if c.strike_price > current_price], key=lambda c: c.strike_price)
            if direction.upper() == "CALL"
            else sorted([c for c in contracts if c.strike_price < current_price], key=lambda c: c.strike_price, reverse=True)
        )

        if not candidates:
            print(f"No suitable strike found for {direction.upper()} near ${current_price}")
            return None

        selected_contract = candidates[0]

        quote_req = OptionLatestQuoteRequest(symbol_or_symbols=[selected_contract.symbol])
        quotes = option_data_client.get_option_latest_quote(quote_req)

        if selected_contract.symbol not in quotes:
            print("No quote data for selected contract.")
            return None

        ask_price = float(quotes[selected_contract.symbol].ask_price)
        if ask_price <= 0:
            print("Invalid ask price.")
            return None

        contract_price = ask_price * 100
        allocated_cash = current_cash * 0.10 # INVEST 10% OF CASH IN SPY
        qty = int(allocated_cash // contract_price)

        if qty < 1:
            print(f"Not enough allocated cash (allocated cash = 10% of cash: ${allocated_cash:.2f}) to buy even 1 contract at ${contract_price:.2f}.")
            return None

        print(f"Buying {qty} SPY {direction.upper()} contract(s): {selected_contract.symbol} at ask ${ask_price:.2f} | Strike: {selected_contract.strike_price} | Exp: {selected_contract.expiration_date}")

        order_req = MarketOrderRequest(
            symbol=selected_contract.symbol,
            qty=qty,
            side=OrderSide.BUY,
            type=OrderType.MARKET,
            time_in_force=TimeInForce.DAY
        )

        order = trade_client.submit_order(order_req)
        print(f"Order submitted: {order.id}")
        return order

    except Exception as e:
        print(f"Error placing SPY {direction.upper()} option: {e}")
        return None
    

def trade_spy_option_by_bias(api, trade_client, option_data_client, spy_bias, overall_bias, min_cash_threshold=100):
    symbol = "SPY"
    final_bias = spy_bias if spy_bias in ["Bullish", "Bearish"] else overall_bias

    user_input = input("Would you like to trade SPY? (Y / N): ").strip().lower()
    if user_input != "y":
        print("Skipping SPY trade.")
        return

    if final_bias not in ["Bullish", "Bearish"]:
        print("Both SPY bias and overall bias are Neutral or undefined. No trade will be placed.")
        return

    try:
        account = api.get_account()
        current_cash = float(account.cash)

        if current_cash <= min_cash_threshold:
            print(f"Not enough cash (${current_cash:.2f}) to trade SPY options.")
            return

        latest_trade = api.get_latest_trade(symbol)
        current_price = float(latest_trade.price)
        direction = "CALL" if final_bias == "Bullish" else "PUT"

        order = trade_option_for_spy(
            trade_client=trade_client,
            option_data_client=option_data_client,
            current_price=current_price,
            direction=direction,
            current_cash=current_cash
        )

        if order:
            filled_order = wait_for_order_fill(order.id, timeout=60)
            if filled_order:
                print(f"Order filled: {filled_order}")
            else:
                print("Order was not filled within timeout.")
        else:
            print("Order was not submitted.")

    except Exception as e:
        print(f"Error in SPY option bias trade: {e}")


if __name__ == "__main__":
    overall_bias, spy_bias = daily_bias()

    trade_spy_option_by_bias(api, trade_client, option_data_client, spy_bias, overall_bias)



# ----------------------------------------------------------------------------------
# Open Chrome; find top losers and most active stocks ------------------------------
# ----------------------------------------------------------------------------------


import time
import random
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from fake_useragent import UserAgent
from webdriver_manager.chrome import ChromeDriverManager
import yfinance as yf

print("Beginning Yahoo Finance search...")

ua = UserAgent()
chrome_options = Options()
chrome_options.add_argument("--headless=new")
chrome_options.add_argument("--disable-blink-features=AutomationControlled")
chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
chrome_options.add_experimental_option("useAutomationExtension", False)
chrome_options.add_argument(f"user-agent={ua.random}")
chrome_options.add_argument('--disable-gpu')
chrome_options.add_argument('--blink-settings=imagesEnabled=false')


def setup_driver():
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)


def get_stock_data(url):
    driver = setup_driver()
    try:
        driver.get(url)

        # Scroll down to load all rows (adjust if needed)
        for _ in range(3):
            driver.execute_script("window.scrollBy(0, 500);")
            time.sleep(random.uniform(1, 2))

        # Wait until the main table with stock data is loaded
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "table[data-reactid]"))
        )

        table = driver.find_element(By.CSS_SELECTOR, "table[data-reactid]")
        rows = table.find_elements(By.TAG_NAME, "tr")

        stock_data = []
        for row in rows[1:]:  # Skip header
            cols = row.find_elements(By.TAG_NAME, "td")
            if len(cols) >= 2:
                ticker = cols[0].text.strip()
                name = cols[1].text.strip()
                stock_data.append((ticker, name))

        return stock_data[:50]

    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return []

    finally:
        driver.quit()


def get_top_gainers():
    url = "https://finance.yahoo.com/gainers"
    return get_stock_data(url)


def get_top_losers():
    url = "https://finance.yahoo.com/losers"
    return get_stock_data(url)


def get_most_active():
    url = "https://finance.yahoo.com/most-active"
    return get_stock_data(url)


def filter_tickers(all_tickers):
    disliked_tickers = {
        "AAPL", "NVDA", "GOOGL", "GOOG", "META", "TSLA", "MSFT", "AMZN", "KO", "ORCL",
        "NFLX", "DIS", "LLY", "NVO", "JNJ", "ABBV", "AZN", "MRK", "NVS", "AMGN", "PFE",
        "GILD", "SNY", "BMY", "GSK", "ZTS", "TAK", "HLN", "BIIB", "TEVA", "ITCI", "NBIX",
        "CTLT", "VTRS", "RDY", "GRFS", "LNTH", "ALKS", "ELAN", "PBH", "OGN", "ALVO", "NKE",
        "ALVOW", "PRGO", "HCM", "BHC", "AMRX", "SUPN", "DVAX", "TARO", "EVO", "AMPH",
        "KNSA", "PCRX", "INDV", "ANIP", "HROW", "BGM", "PETQ", "COLL", "PAHC", "EOLS",
        "AVDL", "TLRY", "CRON", "KMDA", "AKBA", "ETON", "SIGA", "ORGO", "EBS", "TKNO",
        "ESPR", "ACB", "IRWD", "ANIK", "AQST", "AMRN", "MNK", "MNKD", "TFFP", "AERI", "SBUX",
        "ACRS", "AUPH", "VSTM", "VYNE", "VTVT", "VBLT", "VCNX", "VTVT", "VSTM", "VYNE", "GME"
    }
    disliked_upper = {t.upper() for t in disliked_tickers}
    filtered = [t for t in all_tickers if t.upper() not in disliked_upper]
    removed = len(all_tickers) - len(filtered)
    print(f"{removed} disliked tickers removed")
    print(f"{len(filtered)} tradeable tickers remain")
    return filtered


def get_yfinance_info(ticker):
    # Optional: Get detailed info using yfinance for each ticker
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        return {
            "ticker": ticker,
            "shortName": info.get("shortName", ""),
            "sector": info.get("sector", ""),
            "price": info.get("regularMarketPrice", None),
        }
    except Exception as e:
        print(f"yfinance error for {ticker}: {e}")
        return None


# === Main flow ===
top_gainers = get_top_gainers()
top_losers = get_top_losers()
most_active = get_most_active()

print("\nTop 50 Gainers:")
for i, (ticker, name) in enumerate(top_gainers, 1):
    print(f"{i}. {ticker} - {name}")

print("\nTop 50 Losers:")
for i, (ticker, name) in enumerate(top_losers, 1):
    print(f"{i}. {ticker} - {name}")

print("\nTop 50 Most Active:")
for i, (ticker, name) in enumerate(most_active, 1):
    print(f"{i}. {ticker} - {name}")

all_tickers = [t for (t, _) in (top_gainers + top_losers + most_active)]
tradable_tickers = filter_tickers(all_tickers)

print("\nDetailed info for first 5 tradeable tickers using yfinance:")
for ticker in tradable_tickers[:5]:
    info = get_yfinance_info(ticker)
    if info:
        print(info)

print("------------------------------------")




'''
print("beginning search...")

ua = UserAgent()
chrome_options = Options()
chrome_options.add_argument("--headless=new")
chrome_options.add_argument("--disable-blink-features=AutomationControlled")
chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
chrome_options.add_experimental_option("useAutomationExtension", False)
chrome_options.add_argument(f"user-agent={ua.random}")
chrome_options.add_argument('--disable-gpu')
chrome_options.add_argument('--disable-images')
chrome_options.add_argument('--blink-settings=imagesEnabled=false')


def setup_driver():
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)


def get_stock_data(url):
    driver = setup_driver()
    try:
        driver.get(url)
        
        # Scroll down in increments to mimic human behavior -- make faster?
        for _ in range(3):  
            driver.execute_script("window.scrollBy(0, 500);")
            time.sleep(random.uniform(2, 4))  

        # Wait for the table to appear -- make faster?
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.TAG_NAME, "table"))
        )

        # Get all tables on the page
        tables = driver.find_elements(By.TAG_NAME, "table")
        stock_data = []

        if tables:
            rows = tables[0].find_elements(By.TAG_NAME, "tr")  # (First table's rows)
            for row in rows[1:]:  # (Skip header row)
                columns = row.find_elements(By.TAG_NAME, "td")
                if len(columns) > 1:
                    number = columns[0].text.strip()
                    ticker = columns[1].text.strip()
                    name = columns[2].text.strip()
                    stock_data.append((number, ticker, name))
        
        return stock_data[:50]  # (Only top 50 results)

    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return []

    finally:
        driver.quit()

def get_top_losers():
    return get_stock_data("https://www.tipranks.com/markets/top-losers")
def get_top_gainers():
    return get_stock_data('https://www.tipranks.com/markets/top-gainers')
def get_most_active_stocks():
    return get_stock_data("https://www.tipranks.com/markets/most-active-stocks")

top_losers = get_top_losers()
top_gainers = get_top_gainers()
most_active = get_most_active_stocks()

print("\nTop 50 Losers:")
for stock in top_losers:
    print(f"{stock[0]}. {stock[1]} - {stock[2]}")

print("\nTop 50 Gainers:")
for stock in top_gainers:
    print(f"{stock[0]}. {stock[1]} - {stock[2]}")

print("\nTop 50 Most Active Stocks:")
for stock in most_active:
    print(f"{stock[0]}. {stock[1]} - {stock[2]}")

all_tickers = [stock[1] for stock in (top_losers + most_active + top_gainers)]
print("\nList of tickers stored in memory.")

# FILTER UNWANTED TICKERS HERE
disliked_tickers = {"AAPL", "NVDA", "GOOGL", "GOOG", "META", "TSLA", "MSFT", "AMZN", "KO", "ORCL", 
                    "NFLX", "DIS", "LLY", "NVO", "JNJ", "ABBV", "AZN", "MRK", "NVS", "AMGN", "PFE", 
                    "GILD", "SNY", "BMY", "GSK", "ZTS", "TAK", "HLN", "BIIB", "TEVA", "ITCI", "NBIX", 
                    "CTLT", "VTRS", "RDY", "GRFS", "LNTH", "ALKS", "ELAN", "PBH", "OGN", "ALVO", "NKE",
                    "ALVOW", "PRGO", "HCM", "BHC", "AMRX", "SUPN", "DVAX", "TARO", "EVO", "AMPH", 
                    "KNSA", "PCRX", "INDV", "ANIP", "HROW", "BGM", "PETQ", "COLL", "PAHC", "EOLS", 
                    "AVDL", "TLRY", "CRON", "KMDA", "AKBA", "ETON", "SIGA", "ORGO", "EBS", "TKNO", 
                    "ESPR", "ACB", "IRWD", "ANIK", "AQST", "AMRN", "MNK", "MNKD", "TFFP", "AERI", "SBUX",
                    "ACRS", "AUPH", "VSTM", "VYNE", "VTVT", "VBLT", "VCNX", "VTVT", "VSTM", "VYNE", "GME"}

def filter_tickers(all_tickers):
    disliked_tickers_upper = {ticker.upper() for ticker in disliked_tickers}
    
    filtered_stocks = [
        stock for stock in all_tickers if stock not in disliked_tickers_upper
    ]
    
    removed_count = len(all_tickers) - len(filtered_stocks)
    print(f"{removed_count} disliked tickers removed")
    print(f"{len(filtered_stocks)} tradeable tickers remain")
    return filtered_stocks

tradable_tickers = filter_tickers(all_tickers)

print("------------------------------------")
'''


# ----------------------------------------------------------------------------------
# Fetch and Print Account Details --------------------------------------------------
# ----------------------------------------------------------------------------------



try:
    account = api.get_account()
    print(f"Account status: {account.status}")
except Exception as e:
    print(f"Error fetching account details: {e}")


try:
    positions = api.list_positions()
    if positions:
        print("Open positions:")
        for position in positions:
            print(f"Symbol: {position.symbol}, Quantity: {position.qty}")
    else:
        print("No open positions.")
except Exception as e:
    print(f"Error fetching positions: {e}")


def get_recent_candles(symbol, timeframe='5Min', limit=50):
    """Fetch recent candlestick data for a given symbol and timeframe."""
    try:
        valid_timeframes = ['1Min', '5Min', '15Min', '1H', '1D']
        if timeframe not in valid_timeframes:
            print(f"Warning: {timeframe} may not be a valid timeframe. Valid options are: {valid_timeframes}")
        
        max_retries = 3
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                bars = api.get_bars(symbol, timeframe, limit=limit)
                break
            except Exception as e:
                retry_count += 1
                if retry_count == max_retries:
                    raise e
                print(f"Retry {retry_count}/{max_retries} for {symbol}: {e}")
                time.sleep(1)
        
        if not bars or len(bars) == 0:
            print(f"No data returned for {symbol}")
            return pd.DataFrame()
            
        df = pd.DataFrame([{
            'time': bar.t,
            'open': bar.o,
            'high': bar.h,
            'low': bar.l,
            'close': bar.c,
            'volume': bar.v
        } for bar in bars])
        
        if not df.empty:
            df = df.sort_values('time')
            
            if not isinstance(df['time'].iloc[0], pd.Timestamp):
                df['time'] = pd.to_datetime(df['time'])
                
            df.set_index('time', inplace=True)
            
            print(f"Successfully fetched {len(df)} candles for {symbol}")
        
        return df
        
    except Exception as e:
        print(f"Error fetching candle data for {symbol}: {e}")
        return pd.DataFrame()



# ----------------------------------------------------------------------------------
# Dtermine if a stock is bearish ---------------------------------------------------
# ----------------------------------------------------------------------------------



def pop_in_downtrend(stock_data: pd.DataFrame) -> bool:
    closes = stock_data['close']

    if len(closes) < 30:
        return False

    ma_20 = closes.rolling(window=20).mean().iloc[-1]
    ma_50 = closes.rolling(window=50).mean().iloc[-1]
    current_price = closes.iloc[-1]

    is_downtrend = ma_20 < ma_50 and current_price < ma_50

    today_rise = closes.iloc[-1] - closes.iloc[-2]
    rise_pct = today_rise / closes.iloc[-2]

    is_pop = rise_pct > 0.03

    still_weak = current_price < ma_20 * 1.03

    return is_downtrend and is_pop and still_weak



# ----------------------------------------------------------------------------------
# Fibonacci Levels -----------------------------------------------------------------
# ----------------------------------------------------------------------------------



def calculate_fibonacci_levels(df):
    recent_high = df['high'].max()
    recent_low = df['low'].min()
    
    difference = recent_high - recent_low
    level_23_6 = recent_high - difference * 0.236
    level_38_2 = recent_high - difference * 0.382
    level_50 = recent_high - difference * 0.5
    level_61_8 = recent_high - difference * 0.618
    
    return level_23_6, level_38_2, level_50, level_61_8



# ----------------------------------------------------------------------------------
# Determine if Stock is Bullish ----------------------------------------------------
# ----------------------------------------------------------------------------------



def dip_in_uptrend(stock_data: pd.DataFrame) -> bool:
    closes = stock_data['close']

    if len(closes) < 30:
        return False

    ma_20 = closes.rolling(window=20).mean().iloc[-1]
    ma_50 = closes.rolling(window=50).mean().iloc[-1]
    current_price = closes.iloc[-1]

    is_uptrend = ma_20 > ma_50 and current_price > ma_50

    today_drop = closes.iloc[-2] - closes.iloc[-1]
    drop_pct = today_drop / closes.iloc[-2]

    is_dip = drop_pct > 0.03

    still_healthy = current_price > ma_20 * 0.97

    return is_uptrend and is_dip and still_healthy


def is_bearish_reversal(df):
    last, prev = df.iloc[-1], df.iloc[-2]

    bearish_engulfing = (
        prev['close'] > prev['open'] and last['close'] < last['open'] and
        last['open'] > prev['close'] and last['close'] < prev['open']
    )

    bearish_confirmation = (
        bearish_engulfing and last['close'] < last['open'] and prev['close'] < prev['open']
    )

    rsi = talib.RSI(df['close'].values, timeperiod=14)
    rsi_overbought = rsi[-1] > 70
    rsi_dropping = rsi[-1] < rsi[-2]

    volume_confirmed = last['volume'] > prev['volume']

    return (bearish_confirmation and volume_confirmed) or (rsi_overbought and rsi_dropping)


# BULLISH STRATEGY
def is_bullish_candlestick(df):
    if len(df) < 50:
        print("Not enough data for pattern detection.")
        return False

    last = df.iloc[-1]
    prev = df.iloc[-2]
    third = df.iloc[-3]

    print(f"Last Candle: {last[['open', 'high', 'low', 'close']]}")
    print(f"Previous Candle: {prev[['open', 'high', 'low', 'close']]}")
    print(f"Third Candle: {third[['open', 'high', 'low', 'close']]}")

    close_prices = df['close'].values
    volume = df['volume'].values
    high = df['high'].values
    low = df['low'].values

    # Indicators
    rsi = talib.RSI(close_prices, timeperiod=14)
    macd, macdsignal, _ = talib.MACD(close_prices, fastperiod=12, slowperiod=26, signalperiod=9)
    ema50 = talib.EMA(close_prices, timeperiod=50)
    ema200 = talib.EMA(close_prices, timeperiod=200)
    upper_band, middle_band, lower_band = talib.BBANDS(close_prices, timeperiod=20, nbdevup=2, nbdevdn=2, matype=0)
    slowk, slowd = talib.STOCHF(high, low, close_prices, fastk_period=14, fastd_period=3, fastd_matype=0)
    atr = talib.ATR(high, low, close_prices, timeperiod=14)
    adx = talib.ADX(high, low, close_prices, timeperiod=14)

    # Conditions
    last_rsi = rsi[-1]
    macd_bullish = macd[-1] > macdsignal[-1]
    bullish_trend = ema50[-1] > ema200[-1]
    adx_strong_trend = adx[-1] > 25
    rsi_oversold = last_rsi < 40
    price_below_lower_band = last['close'] < lower_band[-1]
    price_above_upper_band = last['close'] > upper_band[-1]
    stochastic_oversold = slowk[-1] < 20
    stochastic_crossover = slowk[-2] < slowd[-2] and slowk[-1] > slowd[-1]

    # ATR volatility context
    atr_recent_avg = np.mean(atr[-14:])
    high_atr = atr[-1] > atr_recent_avg

    # Volume check
    if len(volume) < 10:
        print("Not enough volume data.")
        return False

    avg_volume = np.mean(volume[-10:])
    high_volume = volume[-1] > avg_volume

    # Fibonacci levels
    fib_levels = calculate_fibonacci_levels(df)
    price_near_fib = any(abs(last['close'] - level) < 0.01 * last['close'] for level in fib_levels)

    # Scoring
    positive_signals = 0
    if macd_bullish: positive_signals += 1
    if bullish_trend: positive_signals += 1
    if high_volume: positive_signals += 1
    if rsi_oversold: positive_signals += 1
    if price_below_lower_band: positive_signals += 1
    if stochastic_oversold: positive_signals += 1
    if stochastic_crossover: positive_signals += 1
    if high_atr: positive_signals += 1
    if price_near_fib: positive_signals += 1
    if adx_strong_trend: positive_signals += 1

    # Caution signal: price above upper band (may be peaking)
    if price_above_upper_band:
        positive_signals -= 1

    # Strong bullish context bonus
    if dip_in_uptrend(df): positive_signals += 2

    print(f"Signals => RSI: {last_rsi:.2f}, MACD: {macd_bullish}, EMA Trend: {bullish_trend}, ADX: {adx_strong_trend}, "
          f"Vol: {high_volume}, RSI OS: {rsi_oversold}, BB Low: {price_below_lower_band}, "
          f"Stoch OS: {stochastic_oversold}, Stoch Xover: {stochastic_crossover}, ATR High: {high_atr}, "
          f"Fibo Near: {price_near_fib}, BB High Warning: {price_above_upper_band}")
    print(f"Positive Signals Score: {positive_signals}/11")

    if is_bearish_reversal(df):
        print("Bearish reversal detected. Cancelling bullish signal.")
        return False

    return positive_signals >= 7



# ----------------------------------------------------------------------------------
# Determine if Stock is Bearish ----------------------------------------------------
# ----------------------------------------------------------------------------------



def pop_in_downtrend(stock_data: pd.DataFrame) -> bool:
    closes = stock_data['close']

    if len(closes) < 30:
        return False

    ma_20 = closes.rolling(window=20).mean().iloc[-1]
    ma_50 = closes.rolling(window=50).mean().iloc[-1]
    current_price = closes.iloc[-1]

    is_downtrend = ma_20 < ma_50 and current_price < ma_50

    pop_pct = (closes.iloc[-1] - closes.iloc[-2]) / closes.iloc[-2]
    is_pop = pop_pct > 0.03  # price popped over 3%

    still_weak = current_price < ma_20 * 1.03

    return is_downtrend and is_pop and still_weak


# BEARISH STRATEGY
def is_bearish_candlestick(df):
    if len(df) < 50:
        print("Not enough data for pattern detection.")
        return False

    last = df.iloc[-1]
    prev = df.iloc[-2]
    third = df.iloc[-3]

    print(f"Last Candle: {last[['open', 'high', 'low', 'close']]}")
    print(f"Previous Candle: {prev[['open', 'high', 'low', 'close']]}")
    print(f"Third Candle: {third[['open', 'high', 'low', 'close']]}")

    close_prices = df['close'].values
    volume = df['volume'].values
    high = df['high'].values
    low = df['low'].values

    # Indicators
    rsi = talib.RSI(close_prices, timeperiod=14)
    macd, macdsignal, _ = talib.MACD(close_prices, fastperiod=12, slowperiod=26, signalperiod=9)
    ema50 = talib.EMA(close_prices, timeperiod=50)
    ema200 = talib.EMA(close_prices, timeperiod=200)
    upper_band, middle_band, lower_band = talib.BBANDS(close_prices, timeperiod=20, nbdevup=2, nbdevdn=2, matype=0)
    slowk, slowd = talib.STOCHF(high, low, close_prices, fastk_period=14, fastd_period=3, fastd_matype=0)
    atr = talib.ATR(high, low, close_prices, timeperiod=14)
    adx = talib.ADX(high, low, close_prices, timeperiod=14)

    # Conditions
    last_rsi = rsi[-1]
    macd_bearish = macd[-1] < macdsignal[-1]
    bearish_trend = ema50[-1] < ema200[-1]
    adx_strong_trend = adx[-1] > 25
    rsi_overbought = last_rsi > 60
    price_above_upper_band = last['close'] > upper_band[-1]
    price_below_lower_band = last['close'] < lower_band[-1]
    stochastic_overbought = slowk[-1] > 80
    stochastic_crossover_down = slowk[-2] > slowd[-2] and slowk[-1] < slowd[-1]

    atr_recent_avg = np.mean(atr[-14:])
    high_atr = atr[-1] > atr_recent_avg

    if len(volume) < 10:
        print("Not enough volume data.")
        return False

    avg_volume = np.mean(volume[-10:])
    high_volume = volume[-1] > avg_volume

    fib_levels = calculate_fibonacci_levels(df)
    price_near_fib_resistance = any(abs(last['close'] - level) < 0.01 * last['close'] for level in fib_levels)

    # Scoring
    negative_signals = 0
    if macd_bearish: negative_signals += 1
    if bearish_trend: negative_signals += 1
    if high_volume: negative_signals += 1
    if rsi_overbought: negative_signals += 1
    if price_above_upper_band: negative_signals += 1
    if stochastic_overbought: negative_signals += 1
    if stochastic_crossover_down: negative_signals += 1
    if high_atr: negative_signals += 1
    if price_near_fib_resistance: negative_signals += 1
    if adx_strong_trend: negative_signals += 1

    # Caution signal: price below lower band (may be oversold)
    if price_below_lower_band:
        negative_signals -= 1

    # Strong bearish context bonus
    if pop_in_downtrend(df): negative_signals += 2

    print(f"Signals => RSI: {last_rsi:.2f}, MACD: {macd_bearish}, EMA Trend: {bearish_trend}, ADX: {adx_strong_trend}, "
          f"Vol: {high_volume}, RSI OB: {rsi_overbought}, BB High: {price_above_upper_band}, "
          f"Stoch OB: {stochastic_overbought}, Stoch Xover: {stochastic_crossover_down}, ATR High: {high_atr}, "
          f"Fibo Near: {price_near_fib_resistance}, BB Low Warning: {price_below_lower_band}")
    print(f"Negative Signals Score: {negative_signals}/11")

    return negative_signals >= 7



# ----------------------------------------------------------------------------------
# Ordering and Position Sizing -----------------------------------------------------
# ----------------------------------------------------------------------------------
'''

def position_sizing(symbol, option_ask_price):
    try:
        account = api.get_account()
        cash = float(account.cash)
        portfolio_value = float(account.portfolio_value)

        reserve_cash = portfolio_value * 0.10 # KEEP 10% OF PORTFOLIO UNALLOCATED
        available_cash = max(0, cash - reserve_cash)
        if cash <= reserve_cash or available_cash <= 0:
            print(f"Spending limit reached. Only ${cash:.2f} left.")
            return 0

        max_position_value = portfolio_value * 0.10 # MAX POSITION SIZE: 10% OF PORTFOLIO

        cost_per_contract = option_ask_price * 100
        if cost_per_contract <= 0:
            print(f"Invalid option price for {symbol}: {option_ask_price}")
            return 0
        
        try:
            position = api.get_position(symbol)
            current_position_value = float(position.market_value)
        except:
            current_position_value = 0

        remaining_allocation = max_position_value - current_position_value
        if remaining_allocation <= 0:
            print(f"{symbol} is already at or above the 10% portfolio cap (${current_position_value:.2f}).")
            return 0

        max_contracts_by_cash = int(available_cash // cost_per_contract)
        max_contracts_by_cap = int(remaining_allocation // cost_per_contract)
        qty = min(max_contracts_by_cash, max_contracts_by_cap)

        if qty < 1:
            print(f"Cannot afford even 1 additional contract of {symbol} within 10% cap.")
            return 0

        print(f"Position size for {symbol} at ${option_ask_price:.2f} premium: {qty} contracts (${qty * cost_per_contract:.2f})")
        return qty

    except Exception as e:
        print(f"Error calculating option position size for {symbol}: {e}")
        return 0
'''

def position_sizing(symbol, direction):
    try:
        account = api.get_account()
        cash = float(account.cash)
        portfolio_value = float(account.portfolio_value)

        reserve_cash = portfolio_value * 0.10  # KEEP 10% UNALLOCATED
        available_cash = max(0, cash - reserve_cash)
        if available_cash <= 0:
            print(f"Spending limit reached. Only ${cash:.2f} left.")
            return 0

        max_position_value = portfolio_value * 0.10  # 10% MAX POSITION SIZE

        # === Get current price of underlying ===
        latest_trade = api.get_latest_trade(symbol)
        current_price = float(latest_trade.price)

        # === Fetch and filter option contracts ===
        now = datetime.now(tz=ZoneInfo("America/New_York"))
        exp_from = now + timedelta(days=7)
        exp_to = now + timedelta(days=14)

        contract_type = ContractType.CALL if direction.upper() == "CALL" else ContractType.PUT

        req = GetOptionContractsRequest(
            underlying_symbols=[symbol],
            status=AssetStatus.ACTIVE,
            expiration_date_gte=exp_from.date(),
            expiration_date_lte=exp_to.date(),
            type=contract_type,
            style=ExerciseStyle.AMERICAN,
            limit=100
        )

        res = trade_client.get_option_contracts(req)
        contracts = res.option_contracts
        if not contracts:
            print(f"No {direction.upper()} contracts found for {symbol}")
            return 0

        # === Pick soonest expiration date available ===
        expiration_dates = sorted(set(c.expiration_date for c in contracts))
        preferred_exp = expiration_dates[0]
        contracts = [c for c in contracts if c.expiration_date == preferred_exp]

        # === Find nearest OTM contract ===
        if direction.upper() == "CALL":
            otm_contracts = [c for c in contracts if c.strike_price > current_price]
            selected_contract = min(otm_contracts, key=lambda c: c.strike_price, default=None)
        else:
            otm_contracts = [c for c in contracts if c.strike_price < current_price]
            selected_contract = max(otm_contracts, key=lambda c: c.strike_price, default=None)

        if not selected_contract:
            print(f"No suitable {direction.upper()} strike for {symbol} near ${current_price:.2f}")
            return 0

        option_symbol = selected_contract.symbol

        # === Get ask price via simple symbol query ===
        try:
            option_data = trade_client.get_option_market_data_by_symbol(option_symbol)
            option_ask_price = float(option_data.ask_price)
        except Exception as e:
            print(f"Could not get ask price for {option_symbol}: {e}")
            return 0

        cost_per_contract = option_ask_price * 100
        if cost_per_contract <= 0:
            print(f"Invalid ask price for {option_symbol}: {option_ask_price}")
            return 0

        # === Check Existing Option Position ===
        try:
            position = api.get_position(option_symbol)
            current_position_value = float(position.market_value)
        except:
            current_position_value = 0

        remaining_allocation = max_position_value - current_position_value
        if remaining_allocation <= 0:
            print(f"{option_symbol} is at or above the 10% cap.")
            return 0

        # === Quantity Calculation ===
        max_contracts_by_cash = int(available_cash // cost_per_contract)
        max_contracts_by_cap = int(remaining_allocation // cost_per_contract)
        qty = min(max_contracts_by_cash, max_contracts_by_cap)

        if qty < 1:
            print(f"Not enough room to buy at least 1 contract of {option_symbol}.")
            return 0

        print(f"Position size for {option_symbol} at ${option_ask_price:.2f}: {qty} contracts (${qty * cost_per_contract:.2f})")
        return qty

    except Exception as e:
        print(f"Error calculating position size for {symbol} ({direction}): {e}")
        return 0

def wait_for_order_fill(order_id, timeout=60):
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            order = api.get_order(order_id)
            if order.status == 'filled':
                return order
            elif order.status in ['canceled', 'rejected', 'expired']:
                print(f"Order {order_id} {order.status}.")
                return None
            time.sleep(2)
        except Exception as e:
            print(f"Error checking order status: {e}")
            return None
    print(f"Order {order_id} did not fill within {timeout} seconds.")
    return None



# ----------------------------------------------------------------------------------
# Cash Details ---------------------------------------------------------------------
# ----------------------------------------------------------------------------------



def print_cash_details():
    try:
        account = api.get_account()
        available_cash = float(account.cash)
        total_equity = float(account.equity)
        invested_cash = total_equity - available_cash

        print(f"Available Cash: ${available_cash:.2f}")
        print(f"Invested Cash: ${invested_cash:.2f}")
        print(f"Total Equity: ${total_equity:.2f}")

    except Exception as e:
        print(f"Error fetching cash details: {e}")



# ----------------------------------------------------------------------------------
# Stop Perameters ------------------------------------------------------------------
# ----------------------------------------------------------------------------------


stop_flag = False

try:
    starting_cash = float(account.cash)
    if starting_cash is None:
        print("Error: Unable to fetch starting cash balance.")
        stop_flag = True
    else:
        print(f"Starting cash balance: ${starting_cash:.2f}")
except Exception as e:
    print(f"Error fetching account information: {e}")
    stop_flag = True


def listen_for_stop():
    global stop_flag
    while True:
        user_input = input("Type 'stop' to end the loop: ").strip().lower()
        if user_input == "stop":
            stop_flag = True
            break

threading.Thread(target=listen_for_stop, daemon=True).start()



# ----------------------------------------------------------------------------------
# Buying Options -------------------------------------------------------------------
# ----------------------------------------------------------------------------------



def trade_option_for_symbol(trade_client, symbol, current_price, direction="CALL", qty=1):
    try:
        now = datetime.now(tz=ZoneInfo("America/New_York")) # TIME ZONE
        exp_from = now + timedelta(days=7) # EXPIRATION DATE: EARLIEST AVAILABLE CONTRACT IN 1-2 WEEK RANGE
        exp_to = now + timedelta(days=14)

        contract_type = ContractType.CALL if direction.upper() == "CALL" else ContractType.PUT

        req = GetOptionContractsRequest(
            underlying_symbols=[symbol],
            status=AssetStatus.ACTIVE,
            expiration_date_gte=exp_from.date(),
            expiration_date_lte=exp_to.date(),
            type=contract_type,
            style=ExerciseStyle.AMERICAN,
            limit=100
        )

        res = trade_client.get_option_contracts(req)
        contracts = res.option_contracts

        if not contracts:
            print(f"No {direction.upper()} contracts found for {symbol} within 1-2 weeks.")
            return None

        expiration_dates = sorted(set(c.expiration_date for c in contracts))
        preferred_exp = expiration_dates[0]
        contracts = [c for c in contracts if c.expiration_date == preferred_exp]

        if direction.upper() == "CALL":
            candidates = sorted([c for c in contracts if c.strike_price > current_price], key=lambda c: c.strike_price)
            selected_contract = candidates[0] if candidates else None
        else:  # PUT
            candidates = sorted([c for c in contracts if c.strike_price < current_price], key=lambda c: c.strike_price, reverse=True)
            selected_contract = candidates[0] if candidates else None

        if not selected_contract:
            print(f"No suitable strike price found for {direction.upper()} on {symbol} near ${current_price}")
            return None

        print(f"Placing {direction.upper()} option order: {selected_contract.symbol} | Strike: {selected_contract.strike_price} | Exp: {selected_contract.expiration_date}")

        order_req = MarketOrderRequest(
            symbol=selected_contract.symbol,
            qty=qty,
            side=OrderSide.BUY,
            type=OrderType.MARKET,
            time_in_force=TimeInForce.DAY
        )

        order = trade_client.submit_order(order_req)
        print(f"Order submitted: {order.id}")
        return order

    except Exception as e:
        print(f"Error trading {direction.upper()} option for {symbol}: {e}")
        return None



# ----------------------------------------------------------------------------------
# Stop Loss and Take Profit --------------------------------------------------------
# ----------------------------------------------------------------------------------



def is_liquidity_sweep(symbol, timeframe="15Min", lookback=5):
    candles = get_recent_candles(symbol, timeframe=timeframe)
    if candles is None or len(candles) < lookback + 1:
        print(f"Not enough candles for {symbol}")
        return False

    recent = candles[-(lookback+1):-1]
    last_candle = candles.iloc[-1]

    recent_high = recent['high'].max()
    recent_low = recent['low'].min()

    print(f"{symbol} last high: {last_candle['high']}, recent high: {recent_high}")
    print(f"{symbol} last low: {last_candle['low']}, recent low: {recent_low}")

    if last_candle['high'] > recent_high and last_candle['close'] < recent_high:
        print("Bearish liquidity sweep detected.")
        return True

    if last_candle['low'] < recent_low and last_candle['close'] > recent_low:
        print("Bullish liquidity sweep detected.")
        return True

    return False


def is_reversal_after_breakout(symbol, timeframe="15Min", lookback=5, volume_multiplier=1.2):
    candles = get_recent_candles(symbol, timeframe=timeframe)
    if candles is None or len(candles) < lookback + 2:
        return False

    recent = candles[-(lookback+2):-2]
    breakout_candle = candles.iloc[-2]
    last_candle = candles.iloc[-1]

    recent_high = recent['high'].max()
    recent_low = recent['low'].min()
    avg_volume = recent['volume'].mean()

    breakout_up = breakout_candle['close'] > recent_high and breakout_candle['volume'] > avg_volume * volume_multiplier
    breakout_down = breakout_candle['close'] < recent_low and breakout_candle['volume'] > avg_volume * volume_multiplier

    if breakout_up:
        if last_candle['close'] <= recent_high:
            return True

    if breakout_down:
        if last_candle['close'] >= recent_low:
            return True

    return False


def is_breaking_liquidity_zone(symbol, timeframe="15Min", lookback=5, volume_multiplier=1.2):

    candles = get_recent_candles(symbol, timeframe=timeframe)
    if candles is None or len(candles) < lookback + 1:
        return False

    recent = candles[-(lookback+1):-1]
    last_candle = candles.iloc[-1]

    recent_high = recent['high'].max()
    recent_low = recent['low'].min()
    avg_volume = recent['volume'].mean()

    if last_candle['close'] > recent_high and last_candle['volume'] > avg_volume * volume_multiplier:
        return True

    if last_candle['close'] < recent_low and last_candle['volume'] > avg_volume * volume_multiplier:
        return True

    return False


def evaluate_open_positions_for_sell(api, symbol, entry_price, option_symbol, direction):
    try:
        quote = api.get_option_latest_quote(option_symbol)
        current_price = float(quote.ask_price if direction == "CALL" else quote.bid_price)

        percent_change = (current_price - entry_price) / entry_price

        if percent_change <= -0.10: # STOP LOSS AT -10%
            print(f"{option_symbol} hit stop loss. Selling at {current_price:.2f}")
            sell_option(api, option_symbol)
            return

        if is_liquidity_sweep(symbol, timeframe="15Min"):
            print(f"Liquidity sweep detected for {symbol}. Selling {option_symbol}.")
            sell_option(api, option_symbol)
            return

        if is_reversal_after_breakout(symbol, timeframe="15Min"):
            print(f"{symbol} reversed after a breakout. Selling {option_symbol} to lock gains.")
            sell_option(api, option_symbol)
            return

        if is_breaking_liquidity_zone(symbol, timeframe="15Min"):
            print(f"{symbol} is breaking liquidity — watching for continuation or reversal.")

    except Exception as e:
        print(f"Error evaluating position {option_symbol} for sell: {e}")


def sell_option(api, option_symbol, wait_for_fill=True, timeout=30, poll_interval=1):
    try:
        positions = api.list_positions()
        for pos in positions:
            if pos.symbol == option_symbol:
                qty = int(pos.qty)
                order = api.submit_order(
                    symbol=option_symbol,
                    qty=qty,
                    side='sell',
                    type='market',
                    time_in_force='gtc'
                )
                print(f"Sell order placed for {option_symbol}, order ID: {order.id}")

                if wait_for_fill:
                    start_time = time.time()
                    while time.time() - start_time < timeout:
                        current_order = api.get_order(order.id)
                        status = current_order.status.lower()
                        print(f"Order status: {status}")
                        if status == 'filled':
                            print(f"Order {order.id} for {option_symbol} fully filled.")
                            return current_order
                        elif status in ('canceled', 'rejected', 'expired'):
                            print(f"Order {order.id} was {status}.")
                            return current_order
                        time.sleep(poll_interval)
                    print(f"Order {order.id} not filled after {timeout} seconds.")
                    return current_order
                else:
                    return order

        print(f"No open position found for {option_symbol}")
    except Exception as e:
        print(f"Error placing sell order: {e}")



# ----------------------------------------------------------------------------------
# Main Trading Loop ----------------------------------------------------------------
# ----------------------------------------------------------------------------------

'''
last_date = datetime.now().date()
loop_count = 0
open_positions = []

# Initial direction set based on overall_bias
direction = "CALL" if overall_bias.lower() == "bullish" else "PUT"
initial_direction_set = False  # Flag to trigger alternation on subsequent loops


while not stop_flag:
    try:
        now = datetime.now()
        current_time = now.time()

        print("Starting a new trading cycle...")

        # Direction logic
        if not initial_direction_set:
            # First loop uses overall market bias
            direction = "CALL" if overall_bias.lower() == "bullish" else "PUT"
            initial_direction_set = True
            print(f"Initial direction set based on overall bias: {direction}")
        else:
            # Alternate between CALL and PUT every cycle
            direction = "PUT" if direction == "CALL" else "CALL"
            print(f"Alternating direction for this cycle: {direction}")

        # Check Available Cash
        current_cash = float(account.cash)
        min_cash_threshold = starting_cash * 0.10 # KEEP 10% OF CASH FROM LOOP 1 UNALLOCATED

        if current_cash <= min_cash_threshold:
            print(f"Warning: Cash balance is too low (${current_cash:.2f}). No further buy orders will be placed.")

            # Loop Through Tickers
            for symbol in tradable_tickers:
                print(f"\nProcessing {symbol}...")

                # Fetch Candlestick Data
                try:
                    candles = get_recent_candles(symbol)
                    if candles.empty:
                        print(f"No data found for {symbol}.")
                        continue

                    # Validate entry signal based on direction
                    signal_valid = (
                        is_bullish_candlestick(candles) if direction == "CALL"
                        else is_bearish_candlestick(candles)
                    )

        # Allocate Cash Appropriately
        if current_cash > min_cash_threshold and signal_valid:
            qty = position_sizing(symbol)
            if qty > 0:
                try:
                    latest_trade = api.get_latest_trade(symbol)
                    current_price = float(latest_trade.price)

                    # Place Option Order
                    option_order = trade_option_for_symbol(
                        trade_client,
                        symbol,
                        current_price,
                        direction=direction,
                        qty=qty
                    )

                    # Wait for Order to Fill
                    if option_order:
                        filled_order = wait_for_order_fill(option_order.id, timeout=60)
                        if filled_order:
                            print(f"{direction} order placed for {symbol}: {option_order}")

                            # List and Track Positions
                            open_positions.append({
                                "symbol": symbol,
                                "option_symbol": option_order.symbol,
                                "entry_price": float(filled_order.filled_avg_price),
                                "direction": direction
                            })

                        else:
                            print("Order was not filled in time.")
                    else:
                        print(f"No suitable option contract for {symbol}.")

                except Exception as e:
                    print(f"Error placing {direction} for {symbol}: {e}")
            else:
                print(f"Insufficient budget or zero quantity for {symbol}.")

    except Exception as e:
        print(f"Error processing {symbol}: {e}")

# Manage Current Positions
for pos in open_positions[:]:
    try:
        evaluate_open_positions_for_sell(
            api=api,
            symbol=pos["symbol"],
            entry_price=pos["entry_price"],
            option_symbol=pos["option_symbol"],
            direction=pos["direction"]
        )

        positions = api.list_positions()
        still_open = any(p.symbol == pos["option_symbol"] for p in positions)
        if not still_open:
            print(f"Position {pos['option_symbol']} closed, removing from tracking.")
            open_positions.remove(pos)

    except Exception as e:
        print(f"Error evaluating position {pos['option_symbol']} for sell: {e}")
            
        # Account Details
        print("------------------------------------")

        day_trade_count = account.daytrade_count
        print(f"Day Trade Count in the last 5 business days: {day_trade_count}")    

        print(f"Today's Bias: {overall_bias}")    
        print_cash_details()

        current_date = datetime.now().date()
        if current_date != last_date:
            loop_count = 0
            last_date = current_date
            print(f"New day: loop count reset to zero.")
        loop_count += 1
        print(f"Loop {loop_count}. Time: {datetime.now().strftime('%m-%d-%y %H:%M:%S')}")

        print("Cycle complete. Sleeping for 1 minute before next cycle...")
        for _ in range(60):
            if stop_flag:
                print("Stopping the trading loop.")
                break
            time.sleep(1)

    except Exception as e:
        print(f"Error in main trading loop: {e}")
        print("Sleeping for 1 minute before retrying...")
        time.sleep(60) # RESTING TIME BETWEEN LOOPS (1 MINUTE)
'''


last_date = datetime.now().date()
loop_count = 0
open_positions = []

# Initial direction set based on overall_bias
direction = "CALL" if overall_bias.lower() == "bullish" else "PUT"
initial_direction_set = False  # Flag to trigger alternation on subsequent loops

while not stop_flag:
    try:
        now = datetime.now()
        current_time = now.time()

        print("Starting a new trading cycle...")

        # Direction logic
        if not initial_direction_set:
            # First loop uses overall market bias
            direction = "CALL" if overall_bias.lower() == "bullish" else "PUT"
            initial_direction_set = True
            print(f"Initial direction set based on overall bias: {direction}")
        else:
            # Alternate between CALL and PUT every cycle
            direction = "PUT" if direction == "CALL" else "CALL"
            print(f"Alternating direction for this cycle: {direction}")

        # Check Available Cash
        current_cash = float(account.cash)
        min_cash_threshold = starting_cash * 0.10 # KEEP 10% OF CASH FROM LOOP 1 UNALLOCATED

        if current_cash <= min_cash_threshold:
            print(f"Warning: Cash balance is too low (${current_cash:.2f}). No further buy orders will be placed.")

        # Loop Through Tickers
        for symbol in tradable_tickers:
            print(f"\nProcessing {symbol}...")

            # Fetch Candlestick Data
            try:
                candles = get_recent_candles(symbol)
                if candles.empty:
                    print(f"No data found for {symbol}.")
                    continue

                # Validate entry signal based on direction
                signal_valid = (
                    is_bullish_candlestick(candles) if direction == "CALL"
                    else is_bearish_candlestick(candles)
                )

                # Allocate Cash Appropriately
                if current_cash > min_cash_threshold and signal_valid:
                    qty = position_sizing(symbol, direction)
                    if qty > 0:
                        try:
                            latest_trade = api.get_latest_trade(symbol)
                            current_price = float(latest_trade.price)

                            # Place Option Order
                            option_order = trade_option_for_symbol(
                                trade_client,
                                symbol,
                                current_price,
                                direction=direction,
                                qty=qty
                            )

                            # Wait for Order to Fill
                            if option_order:
                                filled_order = wait_for_order_fill(option_order.id, timeout=60)
                                if filled_order:
                                    print(f"{direction} order placed for {symbol}: {option_order}")

                                    # List and Track Positions
                                    open_positions.append({
                                        "symbol": symbol,
                                        "option_symbol": option_order.symbol,
                                        "entry_price": float(filled_order.filled_avg_price),
                                        "direction": direction
                                    })

                                else:
                                    print("Order was not filled in time.")
                            else:
                                print(f"No suitable option contract for {symbol}.")

                        except Exception as e:
                            print(f"Error placing {direction} for {symbol}: {e}")
                    else:
                        print(f"Insufficient budget or zero quantity for {symbol}.")

            except Exception as e:
                print(f"Error processing {symbol}: {e}")

        # Manage Current Positions
        for pos in open_positions[:]:
            try:
                evaluate_open_positions_for_sell(
                    api=api,
                    symbol=pos["symbol"],
                    entry_price=pos["entry_price"],
                    option_symbol=pos["option_symbol"],
                    direction=pos["direction"]
                )

                positions = api.list_positions()
                still_open = any(p.symbol == pos["option_symbol"] for p in positions)
                if not still_open:
                    print(f"Position {pos['option_symbol']} closed, removing from tracking.")
                    open_positions.remove(pos)

            except Exception as e:
                print(f"Error evaluating position {pos['option_symbol']} for sell: {e}")

        # Account Details
        print("------------------------------------")

        day_trade_count = account.daytrade_count
        print(f"Day Trade Count in the last 5 business days: {day_trade_count}")

        print(f"Today's Bias: {overall_bias}")
        print_cash_details()

        current_date = datetime.now().date()
        if current_date != last_date:
            loop_count = 0
            last_date = current_date
            print(f"New day: loop count reset to zero.")
        loop_count += 1
        print(f"Loop {loop_count}. Time: {datetime.now().strftime('%m-%d-%y %H:%M:%S')}")

        print("Cycle complete. Sleeping for 1 minute before next cycle...")
        for _ in range(60):
            if stop_flag:
                print("Stopping the trading loop.")
                break
            time.sleep(1)

    except Exception as e:
        print(f"Error in main trading loop: {e}")
        print("Sleeping for 1 minute before retrying...")
        time.sleep(60) # RESTING TIME BETWEEN LOOPS (1 MINUTE)








# DO NOT TRADE SPY UNTIL MARKET HAS BEEN OPEN FOR 30 MINS?
# FIX SPY
# Error in SPY option bias trade: name 'wait_for_order_fill' is not defined
# Skip line after "Would you like to trade SPY? (Y / N): n"