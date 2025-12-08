# ---------- IMPORTANT ----------
'''
TURN PAPER TO TRUE OR FALSE
USER MUST ENTER ALPACA API KEY AND SECRET
'''
# ---------- IMPORTANT ----------



# --- Standard Library ---
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import time
import threading
import random
import re

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


import requests
# ----------------------------------------------------------------------------------
# Account Credentials --------------------------------------------------------------
# ----------------------------------------------------------------------------------



# SET TRUE FOR PAPER TRADING, FALSE FOR LIVE
paper = True

# BASE URL (CHANGES IS PAPER OR LIVE)
base_url = 'https://paper-api.alpaca.markets' if paper else 'https://api.alpaca.markets'

# API CREDENTIALS
API_KEY = 'PKMQPNH8AV7ME6AIGPBI'
SECRET_KEY = 'yOOdcAZqdth78fBo9Madoli7tam7UVg9H3FZukM6'

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



print("[UI: 'Begin' button]\n")
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
    print("[here UI picks one of three options: | Bearish | Neutral | Bullish | one will be automatically selected (highlighted) but user can change it]")
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
        

        while True:
            try:
                user_input = input("Enter percentage of cash to allocate to SPY (0-10): [make this a slider in UI] \n")
                spy_allocation_percent = round(float(user_input), 2)

                if spy_allocation_percent > 10:
                    print("Input above 10%. Defaulting to 10.00%.")
                    spy_allocation_percent = 10.0
                elif spy_allocation_percent < 0:
                    print("Input below 0%. Defaulting to 0.00%.")
                    spy_allocation_percent = 0.0
                break
            except ValueError:
                print("Invalid input. Please enter a number (e.g., 5 or 7.25).")

        allocation_fraction = spy_allocation_percent / 100.0

        contract_price = ask_price * 100
        allocated_spy_cash = current_cash * allocation_fraction
        qty = int(allocated_spy_cash // contract_price)


        '''
        contract_price = ask_price * 100
        allocated_spy_cash = current_cash * 0.10 # INVEST 10% OF CASH IN SPY
        qty = int(allocated_spy_cash // contract_price)
        '''
        
        if qty < 1:
            print(f"Not enough allocated cash (allocated cash = 10% of cash: ${allocated_spy_cash:.2f}) to buy even 1 contract at ${contract_price:.2f}.")
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

    user_input = input("Would you like to trade SPY? (Y / N) [make this a toggle in UI] \n").strip().lower()
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



# --- SETUP ---

def setup_driver():
    ua = UserAgent()
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option("useAutomationExtension", False)
    chrome_options.add_argument(f"user-agent={ua.random}")
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--disable-images')
    chrome_options.add_argument('--blink-settings=imagesEnabled=false')
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("window-size=1920,1080")
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)


# --- SCRAPER ---

def get_stock_data_yahoo(url, count):
    if count == 0:
        return []
    if "count=" in url:
        url = re.sub(r'count=[0-9]+', f'count={count}', url)
    driver = setup_driver()
    try:
        driver.get(url)
        WebDriverWait(driver, 3).until(EC.presence_of_element_located((By.TAG_NAME, "table")))
        seen_ids = set()
        last_count = 0
        while True:
            rows = driver.find_elements(By.CSS_SELECTOR, "table tr[data-rowid]")
            for row in rows:
                seen_ids.add(row.get_attribute("data-rowid"))
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(random.uniform(0.1, 0.3))
            if len(seen_ids) == last_count:
                break
            last_count = len(seen_ids)
        final_rows = driver.find_elements(By.CSS_SELECTOR, "table tr")
        stock_data = []
        for row in final_rows[1:count+1]:
            cols = row.find_elements(By.TAG_NAME, "td")
            if len(cols) >= 2:
                stock_data.append((cols[0].text.strip(), cols[1].text.strip()))
        return stock_data
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return []
    finally:
        driver.quit()


# --- URLS ---

yahoo_urls = {
    'trending': "https://finance.yahoo.com/markets/stocks/trending/",
    'losers': "https://finance.yahoo.com/markets/stocks/losers/?start=0&count=50",
    'gainers': "https://finance.yahoo.com/markets/stocks/gainers/?start=0&count=50",
    'most_active': "https://finance.yahoo.com/markets/stocks/most-active/?start=0&count=50",
    '52wk_gainers': "https://finance.yahoo.com/markets/stocks/52-week-gainers/?start=0&count=50",
    '52wk_losers': "https://finance.yahoo.com/markets/stocks/52-week-losers/?start=0&count=50"
}

# --- USER INPUT ---

sections = [
    ('trending', "Trending", 25),
    ('losers', "Top Losers", 100),
    ('gainers', "Top Gainers", 100),
    ('most_active', "Most Active", 100),
    ('52wk_gainers', "52-Week Gainers", 100),
    ('52wk_losers', "52-Week Losers", 100)
]

def get_section_count(section_name, max_limit):
    valid_options = [val for val in [0, 25, 50, 100] if val <= max_limit]
    valid_str = " / ".join(map(str, valid_options))
    while True:
        try:
            val = int(input(f"How many stocks for '{section_name}'? ({valid_str}): ").strip())
            if val in valid_options:
                return val
            else:
                print(f"Please enter one of the allowed values: {valid_str}.")
        except ValueError:
            print("Invalid input. Enter a number.")

section_counts = {}
for key, label, max_limit in sections:
    section_counts[key] = get_section_count(label, max_limit)

# --- MAIN SCRAPING ---

print("Beginning search...")

trending_stocks = get_stock_data_yahoo(yahoo_urls['trending'], section_counts.get('trending', 0))
top_losers = get_stock_data_yahoo(yahoo_urls['losers'], section_counts.get('losers', 0))
top_gainers = get_stock_data_yahoo(yahoo_urls['gainers'], section_counts.get('gainers', 0))
most_active = get_stock_data_yahoo(yahoo_urls['most_active'], section_counts.get('most_active', 0))
wk52_gainers = get_stock_data_yahoo(yahoo_urls['52wk_gainers'], section_counts.get('52wk_gainers', 0))
wk52_losers = get_stock_data_yahoo(yahoo_urls['52wk_losers'], section_counts.get('52wk_losers', 0))

# --- PRINT RESULTS ---

def print_stock_list(title, stock_list):
    if stock_list:
        print(f"\n{title}")
        for i, stock in enumerate(stock_list, 1):
            print(f"{i}. {stock[0]} - {stock[1]}")

print_stock_list("Trending Stocks:", trending_stocks)
print_stock_list("Top Losers:", top_losers)
print_stock_list("Top Gainers:", top_gainers)
print_stock_list("Most Active Stocks:", most_active)
print_stock_list("52-Week Gainers:", wk52_gainers)
print_stock_list("52-Week Losers:", wk52_losers)

# --- TICKER FILTERING ---

all_tickers = [stock[0] for stock in (trending_stocks + top_losers + top_gainers + most_active + wk52_gainers + wk52_losers)]

print("\nList of tickers stored in memory.")

disliked_ticker_input = input("Enter tickers to avoid (comma-separated): [make this a text box in UI] \n").strip()
disliked_tickers = {
    ticker.strip().upper(): True
    for ticker in disliked_ticker_input.split(',') if ticker.strip()
}

print(f"Disliked tickers set: {list(disliked_tickers.keys())}")

def filter_tickers(all_tickers):
    disliked_upper = {t.upper() for t in disliked_tickers}
    filtered = [t for t in all_tickers if t.upper() not in disliked_upper]
    print(f"{len(all_tickers) - len(filtered)} disliked tickers removed")
    print(f"{len(filtered)} tradeable tickers remain")
    return filtered

tradable_tickers = filter_tickers(all_tickers)

print("\nTradeable Tickers:")
for i, ticker in enumerate(tradable_tickers, 1):
    print(f"{i}. {ticker}")



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
required_signals = input("Bullish Signals Required: [UI text box]/{total_ps}\n")
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
    if macd_bullish: positive_signals += 1; total_ps +=1
    if bullish_trend: positive_signals += 1; total_ps +=1
    if high_volume: positive_signals += 1; total_ps +=1
    if rsi_oversold: positive_signals += 1; total_ps +=1
    if price_below_lower_band: positive_signals += 1; total_ps +=1
    if stochastic_oversold: positive_signals += 1; total_ps +=1
    if stochastic_crossover: positive_signals += 1; total_ps +=1
    if high_atr: positive_signals += 1; total_ps +=1
    if price_near_fib: positive_signals += 1; total_ps +=1
    if adx_strong_trend: positive_signals += 1; total_ps +=1

    # Caution signal: price above upper band (may be peaking)
    '''
    if price_above_upper_band:
        positive_signals -= 1
    '''

    # Strong bullish context bonus
    if dip_in_uptrend(df): positive_signals += 1; total_ps +=1

    print(f"Signals => RSI: {last_rsi:.2f}, MACD: {macd_bullish}, EMA Trend: {bullish_trend}, ADX: {adx_strong_trend}, "
          f"Vol: {high_volume}, RSI OS: {rsi_oversold}, BB Low: {price_below_lower_band}, "
          f"Stoch OS: {stochastic_oversold}, Stoch Xover: {stochastic_crossover}, ATR High: {high_atr}, "
          f"Fibo Near: {price_near_fib}, BB High Warning: {price_above_upper_band}")
    print(f"Positive Signals Score: {positive_signals}/11")

    if is_bearish_reversal(df):
        print("Bearish reversal detected. Cancelling bullish signal.")
        return False

    return positive_signals >= required_signals



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


# Stop Loss Input
stop_loss = input("Stop loss: -[text box in UI]% \n").strip().upper()

# Max Position Size Input
while True:
    try:
        user_input = input("Enter MAX position size as a percentage of portfolio (0-15): [make this a slider in UI] \n")
        max_position_percent = round(float(user_input), 2)
        if max_position_percent > 15:
            print("Input above 15%. Defaulting to 15.00%.")
            max_position_percent = 15.0
        elif max_position_percent < 0:
            print("Input below 0%. Defaulting to 0.00%.")
            max_position_percent = 0.0
        break
    except ValueError:
        print("Invalid input. Please enter a number.")

# Min Position Size Input
while True:
    try:
        user_input = input("Enter MIN position size as a percentage of portfolio (0-15): [make this a slider in UI] \n")
        min_position_percent = round(float(user_input), 2)
        if min_position_percent > 15:
            print("Input above 15%. Defaulting to 15.00%.")
            min_position_percent = 15.0
        elif min_position_percent < 0:
            print("Input below 0%. Defaulting to 0.00%.")
            min_position_percent = 0.0
        break
    except ValueError:
        print("Invalid input. Please enter a number.")

# Reserve Cash Input
while True:
    try:
        user_input = input("Enter RESERVE cash as a percentage of portfolio (0-99): [make this a slider in UI] \n")
        reserve_cash_percent = round(float(user_input), 2)
        if reserve_cash_percent > 99:
            print("Input above 99%. Defaulting to 99.00%.")
            reserve_cash_percent = 99.0
        elif reserve_cash_percent < 0:
            print("Input below 0%. Defaulting to 0.00%.")
            reserve_cash_percent = 0.0
        break
    except ValueError:
        print("Invalid input. Please ender a number.")


def position_sizing(symbol, option_ask_price, max_position_percent, min_position_percent, reserve_cash_percent):
    try:
        account = api.get_account()
        cash = float(account.cash)
        portfolio_value = float(account.portfolio_value)

        reserve_cash = portfolio_value * (reserve_cash_percent / 100.0)
        available_cash = max(0, cash - reserve_cash)
        if cash <= reserve_cash or available_cash <= 0:
            print(f"Spending limit reached. Only ${cash:.2f} left.")
            return 0

        max_position_value = portfolio_value * (max_position_percent / 100.0)
        min_position_value = portfolio_value * (min_position_percent / 100.0)

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
            print(f"{symbol} is already at or above the {max_position_percent:.2f}% portfolio cap (${current_position_value:.2f}).")
            return 0

        max_contracts_by_cash = int(available_cash // cost_per_contract)
        max_contracts_by_cap = int(remaining_allocation // cost_per_contract)
        qty = min(max_contracts_by_cash, max_contracts_by_cap)

        if qty < 1:
            print(f"Cannot afford even 1 additional contract of {symbol} within cap.")
            return 0

        total_position_value = qty * cost_per_contract
        if total_position_value < min_position_value:
            print(f"Position value ${total_position_value:.2f} is below minimum threshold (${min_position_value:.2f}). Skipping.")
            return 0

        print(f"Position size for {symbol} at ${option_ask_price:.2f} premium: {qty} contracts (${total_position_value:.2f})")
        return qty

    except Exception as e:
        print(f"Error calculating option position size for {symbol}: {e}")
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


def is_reversal_after_breakout(symbol, timeframe="15Min", lookback=5, volume_multiplier=1.2, min_candle_size_factor=2):
    candles = get_recent_candles(symbol, timeframe=timeframe)
    if candles is None or len(candles) < lookback + 2:
        return False

    # Calculate the gap threshold dynamically based on the timeframe
    recent_candle_range = candles['high'] - candles['low']
    avg_candle_range = recent_candle_range[-lookback:].mean()
    
    # Gap threshold based on timeframe
    if timeframe == "1H":
        gap_threshold = avg_candle_range * 2
    elif timeframe == "30Min":
        gap_threshold = avg_candle_range * 1.5
    else:
        gap_threshold = avg_candle_range

    breakout_candle = candles.iloc[-2]
    last_candle = candles.iloc[-1]

    recent_high = candles['high'].max()
    recent_low = candles['low'].min()
    avg_volume = candles['volume'].mean()

    breakout_up = breakout_candle['close'] > recent_high and breakout_candle['volume'] > avg_volume * volume_multiplier
    breakout_down = breakout_candle['close'] < recent_low and breakout_candle['volume'] > avg_volume * volume_multiplier

    # Detect Fair Value Gap (FVG) on current timeframe
    gap_up = breakout_candle['open'] > breakout_candle['close'] + gap_threshold
    gap_down = breakout_candle['open'] < breakout_candle['close'] - gap_threshold

    avg_candle_size = avg_candle_range

    gap_reversal_up = (
        gap_up and 
        (breakout_candle['open'] - breakout_candle['close']) > min_candle_size_factor * avg_candle_size and
        last_candle['close'] <= breakout_candle['open']
    )

    gap_reversal_down = (
        gap_down and 
        (breakout_candle['close'] - breakout_candle['open']) > min_candle_size_factor * avg_candle_size and
        last_candle['close'] >= breakout_candle['close']
    )

    # Check for standard breakout reversal
    if breakout_up and last_candle['close'] <= recent_high:
        return True

    if breakout_down and last_candle['close'] >= recent_low:
        return True

    # Check for gap reversal (FVG) on current timeframe
    if gap_reversal_up or gap_reversal_down:
        return True

    # Check for FVG reversal in larger timeframes
    for higher_tf in ["30Min", "1H", "1D"]:
        higher_candles = get_recent_candles(symbol, timeframe=higher_tf)
        if higher_candles is None or len(higher_candles) < lookback + 2:
            continue

        breakout = higher_candles.iloc[-2]
        reversal = higher_candles.iloc[-1]
        avg_range = (higher_candles['high'] - higher_candles['low'])[-lookback:].mean()
        avg_vol = higher_candles['volume'][-lookback:].mean()

        tf_gap_up = breakout['open'] > breakout['close'] + avg_range
        tf_gap_down = breakout['open'] < breakout['close'] - avg_range

        tf_large_body_up = (breakout['open'] - breakout['close']) > min_candle_size_factor * avg_range
        tf_large_body_down = (breakout['close'] - breakout['open']) > min_candle_size_factor * avg_range

        tf_strong_volume = breakout['volume'] > avg_vol * volume_multiplier

        tf_gap_reversal_up = tf_gap_up and tf_large_body_up and tf_strong_volume and reversal['close'] <= breakout['open']
        tf_gap_reversal_down = tf_gap_down and tf_large_body_down and tf_strong_volume and reversal['close'] >= breakout['close']

        if tf_gap_reversal_up or tf_gap_reversal_down:
            print(f"Detected FVG reversal in {higher_tf} for {symbol}")
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

def evaluate_open_positions_for_sell(api, symbol, entry_price, option_symbol, direction, strike_price, stop_loss):
    try:
        account = api.get_account()
        equity = float(account.equity)
        day_trade = equity >= 25000

        # Helper to handle both str and datetime for fill times
        def get_fill_date(transaction_time):
            from datetime import datetime
            if isinstance(transaction_time, datetime):
                return transaction_time.date()
            else:
                return datetime.fromisoformat(transaction_time).date()

        # If equity is under $25K, prevent same-day selling
        if not day_trade:
            from datetime import datetime
            fills = api.get_activities(activity_types="FILL")
            recent_option_fills = {
                fill.symbol: get_fill_date(fill.transaction_time)
                for fill in fills
                if hasattr(fill, "transaction_time") and fill.symbol == option_symbol
            }

            fill_date = recent_option_fills.get(option_symbol)
            print(f"Fill timestamp for {option_symbol}: {fill_date}")
            if fill_date == datetime.now().date():
                print(f"Equity (${equity:.2f}) is below $25,000. Skipping day-trade sale for {option_symbol} bought today.")
                return

        req = OptionLatestQuoteRequest(symbol_or_symbols=[option_symbol])
        option_quote = option_data_client.get_option_latest_quote(req)
        quote = option_quote[option_symbol]

        if quote is None:
            print(f"No quote data available for {option_symbol}")
            return

        current_price = quote.ask_price if direction.upper() == "CALL" else quote.bid_price

        if current_price is None:
            print(f"No {'ask' if direction.upper() == 'CALL' else 'bid'} price available for {option_symbol}")
            return

        percent_change = (current_price - entry_price) / entry_price

        if percent_change <= -stop_loss:
            print(f"{option_symbol} hit stop loss. Selling at {current_price:.2f}")
            sell_option(api, option_symbol)
            return

        if percent_change > 0:
            # Only sell if current price exceeds strike
            if direction.upper() == "CALL" and current_price < strike_price:
                print(f"{option_symbol} current price {current_price:.2f} below strike {strike_price}, skipping sell.")
                return
            elif direction.upper() == "PUT" and current_price > strike_price:
                print(f"{option_symbol} current price {current_price:.2f} above strike {strike_price}, skipping sell.")
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
                    time_in_force='day'
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
# Positions and P&L ----------------------------------------------------------------
# ----------------------------------------------------------------------------------



def print_options_and_account_pnl(base_url, API_KEY, SECRET_KEY):
    # --- Helper functions for options ---
    def extract_direction(option_symbol):
        if 'C' in option_symbol:
            return 'CALL'
        elif 'P' in option_symbol:
            return 'PUT'
        else:
            return 'UNKNOWN'

    def extract_strike(option_symbol):
        match = re.match(r"([A-Z]+)(\d{6})([CP])(\d{8})", option_symbol)
        if match:
            strike_int = int(match.group(4))
            return strike_int / 1000
        return None

    def extract_expiration_date(option_symbol):
        match = re.match(r"[A-Z]+(\d{6})[CP]\d{8}", option_symbol)
        if match:
            date_str = match.group(1)
            return datetime.strptime(date_str, "%y%m%d").date()
        return None

    headers = {
        'APCA-API-KEY-ID': API_KEY,
        'APCA-API-SECRET-KEY': SECRET_KEY
    }

    # --- Print open option positions and unrealized P&L ---
    positions_response = requests.get(f'{base_url}/v2/positions', headers=headers)
    if positions_response.status_code != 200:
        print(f"Error fetching positions: {positions_response.status_code} {positions_response.text}")
        return
    positions = positions_response.json()

    total_unrealized_pnl = 0
    print("Open Option Positions:")
    for pos in positions:
        symbol = pos['symbol']
        qty = int(pos['qty'])
        avg_fill_price = float(pos['avg_entry_price'])
        direction = extract_direction(symbol)
        strike_price = extract_strike(symbol)
        expiration_date = extract_expiration_date(symbol)
        filled_date = None  # Not available from this endpoint
        current_price = float(pos.get('current_price', pos.get('market_price', 0)))
        unrealized_pnl = (current_price - avg_fill_price) * qty * 100  # Options = 100 shares per contract

        total_unrealized_pnl += unrealized_pnl

        print(f"Asset: {symbol}")
        print(f"Direction: {direction}")
        print(f"Quantity: {qty}")
        print(f"Average Fill Price: ${avg_fill_price:.2f}")
        print(f"Strike Price: ${strike_price:.2f}")
        print(f"Current Price: ${current_price:.2f}")
        print(f"Filled Date: {filled_date}")
        print(f"Expiration Date: {expiration_date}")
        print(f"Unrealized P&L: ${unrealized_pnl:.2f}")
        print("-----------------------------")

    print(f"Total Unrealized P&L for all open positions: ${total_unrealized_pnl:.2f}")

    # --- Print account-level realized P&L ---
    periods = {
        'day': 1,
        'week': 7,
        'month': 30,
        'year': 365,
        'all-time': None
    }

    print("\nAccount-level Realized P&L (trading only):")
    now = datetime.now()
    for label, days in periods.items():
        realized_pnl = 0
        page_token = None
        while True:
            if days is not None:
                since = (now - timedelta(days=days)).strftime('%Y-%m-%d')
                params = {'activity_types': 'FILL', 'after': since, 'page_size': 100}
            else:
                params = {'activity_types': 'FILL', 'page_size': 100}
            if page_token:
                params['page_token'] = page_token
            resp = requests.get(f'{base_url}/v2/account/activities', headers=headers, params=params)
            if resp.status_code != 200:
                print(f"Error fetching activities for {label}: {resp.status_code} {resp.text}")
                break
            activities = resp.json()
            for act in activities:
                if act.get('side') == 'sell' and act.get('type') == 'fill':
                    profit_loss = act.get('profit_loss')
                    if profit_loss is not None:
                        realized_pnl += float(profit_loss)
            # Pagination: check if there is a next page
            page_token = resp.headers.get('apca-next-page-token')
            if not page_token or len(activities) < 100:
                break
        print(f"Last {label:6}: ${realized_pnl:.2f}")



# ----------------------------------------------------------------------------------
# Extraction Functions, Lists, and Position Data -----------------------------------
# ----------------------------------------------------------------------------------



def extract_underlying(option_symbol):
    match = re.match(r"([A-Z]+)\d+", option_symbol)
    if match:
        return match.group(1)
    return option_symbol  # fallback if pattern doesn't match


def extract_strike(option_symbol):
    match = re.match(r"([A-Z]+)(\d{6})([CP])(\d{8})", option_symbol)
    if match:
        strike_int = int(match.group(4))
        return strike_int / 1000
    return None


last_date = datetime.now().date()
loop_count = 0
open_positions = []
positions = api.list_positions()
print(f"Loading {len(positions)} current open positions from Alpaca into tracking list.")

for pos in positions:
    # Determine direction from option symbol (simple heuristic: 'C' in symbol means CALL, 'P' means PUT)
    if "C" in pos.symbol:
        direction = "CALL"
    elif "P" in pos.symbol:
        direction = "PUT"
    else:
        direction = "UNKNOWN"

    entry_price = float(pos.avg_entry_price)
    underlying_symbol = extract_underlying(pos.symbol)

    open_positions.append({
        "symbol": underlying_symbol,
        "option_symbol": pos.symbol,
        "entry_price": entry_price,
        "direction": direction,
        "strike_price": extract_strike(pos.symbol)
    })

print(f"Tracking {len(open_positions)} open positions after initialization.")

# Initial direction set based on overall_bias
direction = "CALL" if overall_bias.lower() == "bullish" else "PUT"
initial_direction_set = False  # Flag to trigger alternation on subsequent loops



# ----------------------------------------------------------------------------------
# Main Trading Loop ----------------------------------------------------------------
# ----------------------------------------------------------------------------------



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

        next_direction = "PUT" if direction == "CALL" else "CALL"

        # Check Available Cash
        current_cash = float(account.cash)
        min_cash_threshold = starting_cash * 0.10   # KEEP 10% OF CASH FROM LOOP 1 UNALLOCATED

        if current_cash <= min_cash_threshold:
            print(f"Warning: Cash balance is too low (${current_cash:.2f}). No further buy orders will be placed.")

        # Get current positions to enforce 10% equity cap
        positions = api.list_positions()
        symbol_equity_map = {}
        for pos in positions:
            underlying = extract_underlying(pos.symbol)
            symbol_equity_map.setdefault(underlying, 0.0)
            symbol_equity_map[underlying] += float(pos.market_value)
        total_equity = float(account.portfolio_value)

        # Loop Through Tickers
        for symbol in tradable_tickers:
            print(f"\nProcessing {symbol}...")

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
                    try:
                        # Get current price
                        latest_trade = api.get_latest_trade(symbol)
                        current_price = float(latest_trade.price)

                        # Build expiration window
                        now = datetime.now(tz=ZoneInfo("America/New_York"))
                        exp_from = now + timedelta(days=7)
                        exp_to = now + timedelta(days=14)

                        contract_type = ContractType.CALL if direction == "CALL" else ContractType.PUT

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
                            print(f"No {direction} contracts found for {symbol} within 1-2 weeks.")
                            continue

                        expiration_dates = sorted(set(c.expiration_date for c in contracts))
                        preferred_exp = expiration_dates[0]
                        contracts = [c for c in contracts if c.expiration_date == preferred_exp]

                        if direction == "CALL":
                            candidates = sorted(
                                [c for c in contracts if c.strike_price > current_price],
                                key=lambda c: c.strike_price
                            )
                        else:
                            candidates = sorted(
                                [c for c in contracts if c.strike_price < current_price],
                                key=lambda c: c.strike_price,
                                reverse=True
                            )

                        selected_contract = candidates[0] if candidates else None

                        if not selected_contract:
                            print(f"No suitable strike price found for {direction} on {symbol} near ${current_price}")
                            continue

                        try:
                            # Prepare the request for the latest option quote
                            req = OptionLatestQuoteRequest(symbol_or_symbols=[selected_contract.symbol])
                            # Fetch the latest option quote
                            option_quote = option_data_client.get_option_latest_quote(req)
                            # The result is a dictionary keyed by symbol
                            quote_data = option_quote[selected_contract.symbol]
                            if quote_data is None or quote_data.ask_price is None:
                                print(f"No quote or ask price available for {selected_contract.symbol}")
                                continue
                            ask_price = quote_data.ask_price
                        except Exception as e:
                            print(f"Could not get quote for {selected_contract.symbol}: {e}")
                            continue

                        # Enforce equity cap per asset
                        underlying = extract_underlying(selected_contract.symbol)
                        symbol_market_value = symbol_equity_map.get(underlying, 0.0)
                        if symbol_market_value >= max_position_percent: # % CAP PER ASSET
                            print(f"{underlying} already at or above {max_position_percent} of portfolio. Skipping.")
                            continue

                        # Position sizing based on actual ask price
                        qty = position_sizing(symbol, ask_price, max_position_percent, min_position_percent, reserve_cash_percent)

                        if qty > 0:
                            # Place order using existing function
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

                                else:
                                    print("Order was not filled in time.")
                            else:
                                print(f"No suitable option contract for {symbol}.")
                        else:
                            print(f"Insufficient budget or zero quantity for {symbol}.")

                    except Exception as e:
                        print(f"Error placing {direction} for {symbol}: {e}")

            except Exception as e:
                print(f"Error processing {symbol}: {e}")

        # Manage Current Positions
        print("Evaluating open positions...")
        print(f"Currently tracking {len(open_positions)} open positions.")


        for pos in open_positions[:]:
            try:
                strike_price = pos.get("strike_price")
                if strike_price is None:
                    strike_price = extract_strike(pos["option_symbol"])
                evaluate_open_positions_for_sell(
                    api=api,
                    symbol=pos["symbol"],
                    entry_price=pos["entry_price"],
                    option_symbol=pos["option_symbol"],
                    direction=pos["direction"],
                    strike_price=strike_price
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

        print_options_and_account_pnl(base_url, API_KEY, SECRET_KEY)
        print("------------------------------------\n")

        day_trade_count = account.daytrade_count
        print(f"Day Trade Count in the last 5 business days: {day_trade_count}")

        print(f"Today's Bias: {overall_bias}")
        print_cash_details()

        print(f"Previous cycle direction: {direction}")
        print(f"Next cycle direction: {next_direction}")


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
        time.sleep(60) #SLEEP TIME BETWEEN EACH LOOP
        print("[UI: 'Stop' button]")














'''
DISCLAIMER:
This software is provided "as is", without warranty of any kind, express or implied,
including but not limited to warranties of merchantability, fitness for a particular purpose,
noninfringement, or the accuracy or reliability of any results derived from its use.
The user assumes full responsibility for any trading decisions or financial losses.
In no event shall the authors, contributors, or copyright holders be liable for any claim,
loss, or damages, including but not limited to financial losses, trading losses,
or other incidental or consequential damages arising from the use of this software.

© 2025 HalterAPI. All rights reserved.
Unauthorized copying, distribution, reproduction, or modification of this code,
in whole or in part, is strictly prohibited without prior written consent.
'''