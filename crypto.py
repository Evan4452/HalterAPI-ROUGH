import time
import threading
import random
import talib
import time
import yfinance as yf
import pandas as pd
import numpy as np
import alpaca_trade_api as tradeapi
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from fake_useragent import UserAgent


# ----------------------------------------------------------------------------------
# Determine Daily Bias -------------------------------------------------------------
# ----------------------------------------------------------------------------------
'''

def fetch_data(symbol, period='1mo', interval='1d'):
    try:
        data = yf.download(symbol, period=period, interval=interval)
        return data
    except Exception as e:
        print(f"Error fetching data for {symbol}: {e}")
        return None

def calculate_rsi(df, period=14):
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def calculate_bias(df):
    if df is None or len(df) < 2:
        return "Insufficient Data"

    df['50_MA'] = df['Close'].rolling(window=50).mean()
    df['200_MA'] = df['Close'].rolling(window=200).mean()
    df['50_EMA'] = df['Close'].ewm(span=50, adjust=False).mean()
    df['200_EMA'] = df['Close'].ewm(span=200, adjust=False).mean()
    df['RSI'] = calculate_rsi(df)

    if df['50_EMA'].iloc[-1] > df['200_EMA'].iloc[-1]:
        trend = "Bullish"
    elif df['50_EMA'].iloc[-1] < df['200_EMA'].iloc[-1]:
        trend = "Bearish"
    else:
        print(f"No bearish signal detected for {symbol}.")
        print(f"No bearish signal detected for {symbol}.")
        trend = "Neutral"

    if df['RSI'].iloc[-1] > 70:
        rsi_condition = "Overbought - Bearish"
    elif df['RSI'].iloc[-1] < 30:
        rsi_condition = "Oversold - Bullish"
    else:
        rsi_condition = "Neutral RSI"

    latest_close = df['Close'].iloc[-1].item() if not isinstance(df['Close'].iloc[-1], float) else df['Close'].iloc[-1]
    latest_open = df['Open'].iloc[-1].item() if not isinstance(df['Open'].iloc[-1], float) else df['Open'].iloc[-1]

    if latest_close > latest_open:
        price_action = "Bullish"
    elif latest_close < latest_open:
        price_action = "Bearish"
    else:
        price_action = "Neutral Action"

    if trend == "Bullish" and (rsi_condition == "Oversold - Bullish" or price_action == "Bullish"):
        return "Bullish"
    elif trend == "Bearish" and (rsi_condition == "Overbought - Bearish" or price_action == "Bearish"):
        return "Bearish"
    else:
        return "Neutral"

def calculate_overall_bias(biases):
    bullish_count = sum(1 for bias in biases.values() if bias == "Bullish")
    bearish_count = sum(1 for bias in biases.values() if bias == "Bearish")

    if bullish_count > bearish_count:
        overall_bias = "Bullish"
    elif bearish_count > bullish_count:
        overall_bias = "Bearish"
    else:
        overall_bias = "Neutral"

    return overall_bias

def confirm_overall_bias(overall_bias):

    
    print(f"\nOverall Market Bias: {overall_bias}")

    if overall_bias == "Neutral":
        print("The bias is Neutral. Would you like to choose a direction? (B for Bullish / S for Bearish):")
        user_input = input().strip().upper()
        if user_input == 'B':
            overall_bias = "Bullish"
            print("Bullish Bias Saved")
        elif user_input == 'S':
            overall_bias = "Bearish"
            print("Bearish Bias Saved")
        else:
            print("Invalid input. Keeping bias as Neutral.")
    else:
        print("Do you agree with the overall market bias? (Y/N):")
        user_input = input().strip().upper()

        if user_input == 'Y':
            print("Overall bias confirmed and saved.")
            with open('overall_market_bias.txt', 'w') as f:
                f.write(f"Overall Market Bias: {overall_bias}\n")
        elif user_input == 'N':
            corrected = "Bearish" if overall_bias == "Bullish" else "Bullish"
            print(f"Switching the overall bias to: {corrected}")
            with open('overall_market_bias_corrected.txt', 'w') as f:
                f.write(f"Corrected Overall Market Bias: {corrected}\n")
        else:
            print("Invalid input. Exiting without saving.")
    return overall_bias  

def daily_bias():
    # Fetch data using index symbols
    spx_data = fetch_data('^GSPC')  # S&P 500 Index
    qqq_data = fetch_data('^NDX')   # Nasdaq-100 Index
    dia_data = fetch_data('^DJI')   # Dow Jones Index
    uup_data = fetch_data('DX-Y.NYB')   # US Dollar Index

    biases = {
        'S&P 500': calculate_bias(spx_data),
        'Nasdaq': calculate_bias(qqq_data),
        'Dow Jones': calculate_bias(dia_data),
        'US Dollar': calculate_bias(uup_data)
    }

    for name, bias in biases.items():
        print(f"{name}: {bias}")

    overall_bias = calculate_overall_bias(biases)
    final_bias = confirm_overall_bias(overall_bias)
    return final_bias

overall_bias = daily_bias()

'''
# ----------------------------------------------------------------------------------
# Open Chrome; find top losers and most active stocks ------------------------------
# ----------------------------------------------------------------------------------


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

# Fetch top losers and most active stocks
def get_top_losers():
    return get_stock_data("https://finance.yahoo.com/markets/crypto/losers/")
def get_most_active_stocks():
    return get_stock_data("https://finance.yahoo.com/markets/crypto/most-active/")

top_losers = get_top_losers()
most_active = get_most_active_stocks()

print("\nTop 50 Losers:")
for stock in top_losers:
    print(f"{stock[0]}. {stock[1]} - {stock[2]}")

print("\nTop 50 Most Active Stocks:")
for stock in most_active:
    print(f"{stock[0]}. {stock[1]} - {stock[2]}")

all_tickers = [stock[1] for stock in (top_losers + most_active)]
print("\nList of tickers stored in memory.")

tradable_tickers = all_tickers

'''
# Remove Big Tech/Pharma stocks from list
disliked_tickers = {"AAPL", "NVDA", "GOOGL", "GOOG", "META", "TSLA", "MSFT", "AMZN", "KO", "ORCL", 
                    "NFLX", "DIS", "LLY", "NVO", "JNJ", "ABBV", "AZN", "MRK", "NVS", "AMGN", "PFE", 
                    "GILD", "SNY", "BMY", "GSK", "ZTS", "TAK", "HLN", "BIIB", "TEVA", "ITCI", "NBIX", 
                    "CTLT", "VTRS", "RDY", "GRFS", "LNTH", "ALKS", "ELAN", "PBH", "OGN", "ALVO", "NKE",
                    "ALVOW", "PRGO", "HCM", "BHC", "AMRX", "SUPN", "DVAX", "TARO", "EVO", "AMPH", 
                    "KNSA", "PCRX", "INDV", "ANIP", "HROW", "BGM", "PETQ", "COLL", "PAHC", "EOLS", 
                    "AVDL", "TLRY", "CRON", "KMDA", "AKBA", "ETON", "SIGA", "ORGO", "EBS", "TKNO", 
                    "ESPR", "ACB", "IRWD", "ANIK", "AQST", "AMRN", "MNK", "MNKD", "TFFP", "AERI", "SBUX",
                    "ACRS", "AUPH", "VSTM", "VYNE", "VTVT", "VBLT", "VCNX", "VTVT", "VSTM", "VYNE"}

def filter_tickers(all_tickers):
    disliked_tickers_upper = {ticker.upper() for ticker in disliked_tickers}
    
    filtered_stocks = [
        stock for stock in all_tickers if stock not in disliked_tickers_upper
    ]
    
    removed_count = len(all_tickers) - len(filtered_stocks)
    print(f"{removed_count} disliked tickers removed")
    print(f"{len(filtered_stocks)} tradeable tickers remain")
    return filtered_stocks

# List of all tickers for the day's trading
tradable_tickers = filter_tickers(all_tickers)
'''

print("------------------------------------")


# ----------------------------------------------------------------------------------
# Fetch and print account details---------------------------------------------------
# ----------------------------------------------------------------------------------


# API credentials
api = tradeapi.REST('PKVVPFG2F1MCX4XH05P1', 
                    'Jcf1XSnLvgPvZmRBDcJb84dWrdrNoPibqn3gxseb', 
                    base_url='https://paper-api.alpaca.markets'
                    )

# Determine account status
try:
    account = api.get_account()
    print(f"Account status: {account.status}")
except Exception as e:
    print(f"Error fetching account details: {e}")


# List open positions
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

# recieve candles for each stock in tradable_tickers
def get_recent_candles(symbol, timeframe='5Min', limit=50):
    """Fetch recent candlestick data for a given symbol and timeframe."""
    try:
        # Add timeframe validation
        valid_timeframes = ['1Min', '5Min', '15Min', '1H', '1D']
        if timeframe not in valid_timeframes:
            print(f"Warning: {timeframe} may not be a valid timeframe. Valid options are: {valid_timeframes}")
        
        # Add retry logic for API calls
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
                time.sleep(1)  # Wait before retrying
        
        # Check for data
        if not bars or len(bars) == 0:
            print(f"No data returned for {symbol}")
            return pd.DataFrame()
            
        # Convert list of bar objects to a DataFrame
        df = pd.DataFrame([{
            'time': bar.t,
            'open': bar.o,
            'high': bar.h,
            'low': bar.l,
            'close': bar.c,
            'volume': bar.v
        } for bar in bars])
        
        # Ensure the DataFrame is sorted by time
        if not df.empty:
            df = df.sort_values('time')
            
            # Convert timestamp to datetime if needed
            if not isinstance(df['time'].iloc[0], pd.Timestamp):
                df['time'] = pd.to_datetime(df['time'])
                
            # Set time as index for easier analysis
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
        return False  # need more data to assess trend

    # Step 1: Confirm general downtrend using moving averages
    ma_20 = closes.rolling(window=20).mean().iloc[-1]
    ma_50 = closes.rolling(window=50).mean().iloc[-1]
    current_price = closes.iloc[-1]

    is_downtrend = ma_20 < ma_50 and current_price < ma_50

    # Step 2: Detect recent pop
    today_rise = closes.iloc[-1] - closes.iloc[-2]
    rise_pct = today_rise / closes.iloc[-2]

    is_pop = rise_pct > 0.03  # price popped more than 3%

    # Step 3: Make sure price is still below 20 MA (trend not broken)
    still_weak = current_price < ma_20 * 1.03  # hasn't broken above MA

    return is_downtrend and is_pop and still_weak



def is_bearish_candlestick(df):
    score = 0
    if len(df) < 20:
        print("Not enough data for pattern detection.")
        return False
    
    # Get recent candles
    last = df.iloc[-1]
    prev = df.iloc[-2]
    third = df.iloc[-3]

    print(f"Last Candle: {last[['open', 'high', 'low', 'close']]}")
    print(f"Previous Candle: {prev[['open', 'high', 'low', 'close']]}")
    print(f"Third Candle: {third[['open', 'high', 'low', 'close']]}")

    close_prices = df['close'].values
    volume = df['volume'].values

    # Indicators
    rsi = talib.RSI(close_prices, timeperiod=14)
    macd, macdsignal, _ = talib.MACD(close_prices, fastperiod=12, slowperiod=26, signalperiod=9)
    ema50 = talib.EMA(close_prices, timeperiod=50)
    ema200 = talib.EMA(close_prices, timeperiod=200)
    upper_band, middle_band, lower_band = talib.BBANDS(close_prices, timeperiod=20, nbdevup=2, nbdevdn=2, matype=0)
    slowk, slowd = talib.STOCHF(df['high'].values, df['low'].values, close_prices, fastk_period=14, fastd_period=3, fastd_matype=0)
    atr = talib.ATR(df['high'].values, df['low'].values, close_prices, timeperiod=14)
    adx = talib.ADX(df['high'].values, df['low'].values, close_prices, timeperiod=14)

    # Bearish indicators
    last_rsi = rsi[-1] if not np.isnan(rsi[-1]) else 50
    macd_bearish = macd[-1] < macdsignal[-1]
    bearish_trend = ema50[-1] < ema200[-1]
    
    if len(volume) < 10:
        print("Not enough volume data for average calculation.")
        return False
    avg_volume = np.mean(volume[-10:])
    high_volume = volume[-1] > avg_volume
    rsi_overbought = last_rsi > 60
    price_above_upper_band = last['close'] > upper_band[-1]
    stochastic_overbought = slowk[-1] > 80

    fib_levels = calculate_fibonacci_levels(df)
    price_near_fib = any(abs(last['close'] - level) < 0.01 * last['close'] for level in fib_levels)
    adx_strong_trend = adx[-1] > 25

    # Score bearish signals
    if macd_bearish: score += 1
    if bearish_trend: score += 1
    if high_volume: score += 1
    if rsi_overbought: score += 1
    if price_above_upper_band: score += 1
    if stochastic_overbought: score += 1
    if price_near_fib: score += 1
    if adx_strong_trend: score += 1
    if pop_in_downtrend(df): score += 2

    print(f"RSI: {last_rsi}, MACD Bearish: {macd_bearish}, Bearish Trend: {bearish_trend}, High Volume: {high_volume}, "
          f"RSI Overbought: {rsi_overbought}, Price Above Upper Band: {price_above_upper_band}, Stochastic Overbought: {stochastic_overbought}, "
          f"Price Near Fibonacci Levels: {price_near_fib}, ADX Strong Trend: {adx_strong_trend}")

    print(f"Total bearish signals: {score}/10")

    return score >= 5


# ----------------------------------------------------------------------------------
# Fibonacci Levels -----------------------------------------------------------------
# ----------------------------------------------------------------------------------


# Calculate Fibonacci levels
def calculate_fibonacci_levels(df):
    """Calculate Fibonacci retracement levels based on the high and low of the last 20 periods."""
    recent_high = df['high'].max()
    recent_low = df['low'].min()
    
    difference = recent_high - recent_low
    level_23_6 = recent_high - difference * 0.236
    level_38_2 = recent_high - difference * 0.382
    level_50 = recent_high - difference * 0.5
    level_61_8 = recent_high - difference * 0.618
    
    return level_23_6, level_38_2, level_50, level_61_8


# ----------------------------------------------------------------------------------
# Determine if a stock is bullish ---------------------------------------------------
# ----------------------------------------------------------------------------------


# Determine if stock is in uptrend and buy the dip
def dip_in_uptrend(stock_data: pd.DataFrame) -> bool:
    closes = stock_data['close']

    if len(closes) < 30:
        return False  # need more data to assess trend

    # Step 1: Confirm general uptrend using moving averages
    ma_20 = closes.rolling(window=20).mean().iloc[-1]
    ma_50 = closes.rolling(window=50).mean().iloc[-1]
    current_price = closes.iloc[-1]

    is_uptrend = ma_20 > ma_50 and current_price > ma_50

    # Step 2: Detect recent dip (e.g., today's close vs yesterday's)
    today_drop = closes.iloc[-2] - closes.iloc[-1]
    drop_pct = today_drop / closes.iloc[-2]

    is_dip = drop_pct > 0.03  # dropped more than 3%

    # Step 3: Make sure price is still above 20 MA (trend not broken)
    still_healthy = current_price > ma_20 * 0.97  # hasn't crashed far below MA

    return is_uptrend and is_dip and still_healthy



# Calculate for bearish reversal
def is_bearish_reversal(df):
    last, prev = df.iloc[-1], df.iloc[-2]

    # Bearish Engulfing Confirmation
    bearish_engulfing = (
        prev['close'] > prev['open'] and last['close'] < last['open'] and
        last['open'] > prev['close'] and last['close'] < prev['open']
    )

    # Extra confirmation: Two consecutive bearish candles
    bearish_confirmation = (
        bearish_engulfing and last['close'] < last['open'] and prev['close'] < prev['open']
    )

    # RSI with a downward trend
    rsi = talib.RSI(df['close'].values, timeperiod=14)
    rsi_overbought = rsi[-1] > 70
    rsi_dropping = rsi[-1] < rsi[-2]  # RSI must be decreasing

    # Volume Confirmation
    volume_confirmed = last['volume'] > prev['volume']

    # Final Decision: Require at least two bearish conditions to trigger a sell
    return (bearish_confirmation and volume_confirmed) or (rsi_overbought and rsi_dropping)


# Calculate if stock is bullish
def is_bullish_candlestick(df):
    score = 0
    if len(df) < 20:
        print("Not enough data for pattern detection.")
        return False
    
    
    # Review the three most recent candles
    last = df.iloc[-1]
    prev = df.iloc[-2]
    third = df.iloc[-3]
    

    # Debugging output
    print(f"Last Candle: {last[['open', 'high', 'low', 'close']]}")
    print(f"Previous Candle: {prev[['open', 'high', 'low', 'close']]}")
    print(f"Third Candle: {third[['open', 'high', 'low', 'close']]}")
    
    close_prices = df['close'].values
    volume = df['volume'].values
    
    # Calculate indicators
    rsi = talib.RSI(close_prices, timeperiod=14)
    macd, macdsignal, _ = talib.MACD(close_prices, fastperiod=12, slowperiod=26, signalperiod=9)
    ema50 = talib.EMA(close_prices, timeperiod=50)
    ema200 = talib.EMA(close_prices, timeperiod=200)
    
    # Bollinger Bands
    upper_band, middle_band, lower_band = talib.BBANDS(close_prices, timeperiod=20, nbdevup=2, nbdevdn=2, matype=0)
    
    # Stochastic Oscillator
    slowk, slowd = talib.STOCHF(df['high'].values, df['low'].values, close_prices, fastk_period=14, fastd_period=3, fastd_matype=0)
    
    # Average True Range (ATR)
    atr = talib.ATR(df['high'].values, df['low'].values, close_prices, timeperiod=14)
    
    # Average Directional Index (ADX)
    adx = talib.ADX(df['high'].values, df['low'].values, close_prices, timeperiod=14)
    adx_strong_trend = adx[-1] > 25  # ADX above 25 confirms strong trend
    

    last_rsi = rsi[-1] if not np.isnan(rsi[-1]) else 50
    macd_bullish = macd[-1] > macdsignal[-1]
    bullish_trend = ema50[-1] > ema200[-1]
    
    # Ensure there are enough volume data points
    if len(volume) < 10:
        print("Not enough volume data for average calculation.")
        return False
    
    avg_volume = np.mean(volume[-10:])
    high_volume = volume[-1] > avg_volume
    rsi_oversold = last_rsi < 40
    
    # Bollinger Bands conditions
    price_below_lower_band = last['close'] < lower_band[-1]
    
    # Stochastic conditions
    stochastic_oversold = slowk[-1] < 20
    
    # Calculate Fibonacci levels
    fib_levels = calculate_fibonacci_levels(df)
    # Check if close is near any Fibonacci level
    price_near_fib = any(abs(last['close'] - level) < 0.01 * last['close'] for level in fib_levels)
    
# Count positive signals
    positive_signals = 0
    if macd_bullish: positive_signals += 1
    if bullish_trend: positive_signals += 1
    if high_volume: positive_signals += 1
    if rsi_oversold: positive_signals += 1
    if price_below_lower_band: positive_signals += 1
    if stochastic_oversold: positive_signals += 1
    if price_near_fib: positive_signals += 1
    if adx_strong_trend: positive_signals += 1
    if dip_in_uptrend(df): positive_signals += 2
    
    print(f"RSI: {last_rsi}, MACD Bullish: {macd_bullish}, Bullish Trend: {bullish_trend}, High Volume: {high_volume}, "
          f"RSI Oversold: {rsi_oversold}, Price Below Lower Band: {price_below_lower_band}, Stochastic Oversold: {stochastic_oversold}, "
          f"Price Near Fibonacci Levels: {price_near_fib}, ADX Strong Trend: {adx_strong_trend}")

    print(f"Total positive signals: {positive_signals}/10")


    if is_bearish_reversal(df):
        print("Bearish reversal detected—canceling bullish signal.")
        return False

    return positive_signals >= 5   


# ----------------------------------------------------------------------------------
# Calculate the stop loss ----------------------------------------------------------
# ----------------------------------------------------------------------------------


# Define the trailing percentage as a constant
TRAILING_PERCENTAGE = 0.03  # 3% trailing stop loss

''' # Uncomment for automated stop loss
# Calculate the stop loss price
def calculate_stop_loss(entry_price):
    # Calculate the stop loss price based on the entry price and the trailing percentage
    stop_loss_price = entry_price * (1 - TRAILING_PERCENTAGE)  # Example for a trailing stop loss
    return stop_loss_price
'''

# ----------------------------------------------------------------------------------
# Ordering and position sizing -----------------------------------------------------
# ----------------------------------------------------------------------------------


# Position sizing
def position_sizing(symbol):
    try:
        # Get account information
        account = api.get_account()
        cash = float(account.cash)
        portfolio_value = float(account.portfolio_value)
        
        # Ensure 10% of total money stays uninvested
        reserve_cash = portfolio_value * 0.10  # 10% of total money
        available_cash = max(0, cash - reserve_cash)
        
        if available_cash <= 0:
            print(f"Insufficient cash for trading after reserving 10% of total money. Available: ${available_cash:.2f}")
            return 0
        
    
        # Get current price of the symbol
        candles = get_recent_candles(symbol)
        if candles.empty:
            print(f"Cannot calculate position size for {symbol}: No price data available")
            return 0
            
        current_price = candles['close'].iloc[-1]
        
        '''
        # Risk parameters
        risk_percentage = 0.02  # Risk 2% of available cash per trade
        max_position_percentage = 0.30  # No position should be more than 30% of portfolio
        
        # Calculate position size based on risk
        risk_amount = available_cash * risk_percentage
        max_position_amount = available_cash * max_position_percentage
        
        # Calculate shares based on risk      
        price_risk_per_share = current_price * TRAILING_PERCENTAGE
        shares_based_on_risk = int(risk_amount / price_risk_per_share)
        
        # Calculate shares based on max position size
        shares_based_on_max = int(max_position_amount / current_price)
        
        # Take the smaller of the two
        position_size = min(shares_based_on_risk, shares_based_on_max)
        '''

        # Max position cap
        max_position_percentage = 0.20  # 20% of portfolio max
        max_position_value = portfolio_value * max_position_percentage

        # Get current holding in this symbol
        try:
            position = api.get_position(symbol)
            current_position_value = float(position.market_value)
        except:
            current_position_value = 0  # No existing position

        # Remaining room for this stock
        remaining_allocation = max_position_value - current_position_value
        if remaining_allocation <= 0:
            print(f"{symbol} is already at or above the 20% cap (${current_position_value:.2f})")
            return 0

        # Risk controls
        risk_percentage = 0.02
        risk_amount = available_cash * risk_percentage
        price_risk_per_share = current_price * TRAILING_PERCENTAGE
        shares_based_on_risk = int(risk_amount / price_risk_per_share)

        # Limit based on remaining allocation
        shares_based_on_remaining_allocation = int(remaining_allocation / current_price)

        position_size = min(shares_based_on_risk, shares_based_on_remaining_allocation)

        if position_size < 1:
            print(f"Calculated position size for {symbol} is too small: {position_size}")
            return 0
            
        print(f"Position size for {symbol} at ${current_price:.2f}: {position_size} shares (${position_size * current_price:.2f})")
        return position_size
        
    except Exception as e:
        print(f"Error calculating position size for {symbol}: {e}")
        return 0


#Wait for order to be filled
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
            time.sleep(2)  # Wait 2 seconds before checking again
        except Exception as e:
            print(f"Error checking order status: {e}")
            return None
    print(f"Order {order_id} did not fill within {timeout} seconds.")
    return None

# Retrieve the current position quantity for the given stock symbol.
def get_current_position_qty(symbol):
    try:
        # Fetch the account's positions
        positions = api.list_positions()  # Replace with your API's method to get positions

        # Loop through the positions to find the specified symbol
        for position in positions:
            if position.symbol == symbol:
                return int(position.qty)  # Return the quantity as an integer

        # If the symbol is not found, return 0
        return 0
    except Exception as e:
        print(f"Error retrieving position for {symbol}: {e}")
        return 0  # Return 0 in case of an error

# Print cash details
def print_cash_details():
    try:
        # Get account details
        account = api.get_account()

        # Available cash
        available_cash = float(account.cash)
        # Total equity (includes cash, positions, and P&L)
        total_equity = float(account.equity)
        # Calculate invested cash
        invested_cash = total_equity - available_cash

        # Print cash details
        print(f"Available Cash: ${available_cash:.2f}")
        print(f"Invested Cash: ${invested_cash:.2f}")
        print(f"Total Equity: ${total_equity:.2f}")


    except Exception as e:
        print(f"Error fetching cash details: {e}")



# ----------------------------------------------------------------------------------
# sell bearish positions -----------------------------------------------------------
# ----------------------------------------------------------------------------------


# Sell bearish positions
def sell_bearish_positions():
    try:
        positions = api.list_positions()

        if not positions:
            print("No open positions to check.")
            return

        for position in positions:
            symbol = position.symbol
            qty = float(position.qty)

            if qty <= 0:
                continue  

            print(f"Checking {symbol} for bearish signals...")

            # Check for bearish signals
            try:
                candles = get_recent_candles(symbol)
                if candles.empty:
                    print(f"No data found for {symbol}. Skipping.")
                    continue

                if is_bearish_candlestick(candles):
                    print(f"Bearish signal detected for {symbol}. Selling {qty} shares.")

                    sell_order = api.submit_order(
                        symbol=symbol,
                        qty=qty,
                        side='sell',
                        type='market',
                        time_in_force='gtc'
                    )

                    print(f"Sell order placed for {symbol}.")

                    filled_order = wait_for_order_fill(sell_order.id, timeout=60)
                    if not filled_order:
                        print(f"Sell order for {symbol} did not fill within the timeout period.")
                else:
                    print(f"{symbol} is not bearish. Holding position.")

            except Exception as e:
                print(f"Error processing {symbol}: {e}")

    except Exception as e:
        print(f"Error retrieving account positions: {e}")


# ----------------------------------------------------------------------------------
# Stop Perameters ------------------------------------------------------------------
# ----------------------------------------------------------------------------------


# Allow for loop to stop
stop_flag = False
starting_cash = float(account.cash)  # Implement this function
if starting_cash is None:
    print("Error: Unable to fetch starting cash balance.")
    stop_flag = True  # Stop trading (no account info)

# Listen for user input to stop the loop
def listen_for_stop():
    global stop_flag
    while True:
        user_input = input("Type 'stop' to end the loop: ").strip().lower()
        if user_input == "stop":
            stop_flag = True
            break

# Start user input listener thread
threading.Thread(target=listen_for_stop, daemon=True).start()


# ----------------------------------------------------------------------------------
# Main Trading Loop ----------------------------------------------------------------
# ----------------------------------------------------------------------------------



last_date = datetime.now().date()
loop_count = 0

while not stop_flag:
    try:
        # Get current time
        now = datetime.now()
        current_time = now.time()

        print("Starting a new trading cycle...")

        current_cash = float(account.cash)  # Fetch current cash balance
        min_cash_threshold = starting_cash * 0.10  # 10% of the initial balance
        

        if current_cash <= min_cash_threshold:
            print(f"Warning: Cash balance is too low (${current_cash:.2f}). No further buy orders will be placed.")

        for symbol in tradable_tickers:
            print(f"\nProcessing {symbol}...")

            try:
                candles = get_recent_candles(symbol)
                if candles.empty:
                    print(f"No data found for {symbol}.")
                    continue  

                # Check for bullish conditions before buying
                if current_cash > min_cash_threshold and is_bullish_candlestick(candles):  
                    qty = position_sizing(symbol)
                    if qty > 0:
                        try:
                            buy_order = api.submit_order(
                                symbol=symbol,
                                qty=qty,
                                side='buy',
                                type='market',
                                time_in_force='gtc'
                            )
                            print(f"Buy order successfully placed for {symbol}.")
                            
                            filled_order = wait_for_order_fill(buy_order.id, timeout=60)
                            if not filled_order:
                                print(f"Order for {symbol} did not fill within timeout period.")
                                continue

                            entry_price = float(filled_order.filled_avg_price)

                        except Exception as e:
                            print(f"Error in order process for {symbol}: {e}")
                    else:
                        print(f"Not enough cash to buy {symbol} or position sizing returned 0.")

                current_position_qty = get_current_position_qty(symbol)
                # if current_position_qty > 0 and is_bearish_candlestick(candles):  # Sell only if an owner
                   
                    # stop loss code
                    
                # else:
                #   print(f"No bullish signal detected for {symbol}.")

            except Exception as e:
                print(f"Error processing {symbol}: {e}")


        
        print("------------------------------------")
        
        day_trade_count = account.daytrade_count
        print(f"Day Trade Count in the last 5 business days: {day_trade_count}")    

        # print(f"Today's Bias: {overall_bias}")    
        
        print_cash_details()


         # Count Amount of Loops Fulfilled (According to Day)
        current_date = datetime.now().date()
        if current_date != last_date:
            loop_count = 0
            last_date = current_date
            print(f"New day: loop count reset to zero.")
        loop_count += 1  # Increment counter
        print(f"Loop {loop_count}.")

        # Print current time
        print("Time Stopped:", datetime.now().strftime("%m-%d-%y %H:%M:%S"))


        print("Cycle complete. Sleeping for 1 minute before next cycle...")
        for _ in range(60):
            if stop_flag:
                print("Stopping the trading loop.")
                break
            time.sleep(1)

    except Exception as e:
        print(f"Error in main trading loop: {e}")
        print("Sleeping for 1 minute before retrying...")
        time.sleep(60) 

        '''


last_date = datetime.now().date()
loop_count = 0

# In-memory stop loss store
stop_loss_dict = {}

def set_stop_loss(symbol, price):
    stop_loss_dict[symbol] = price

def get_stop_loss(symbol):
    return stop_loss_dict.get(symbol, None)

while not stop_flag:
    try:
        now = datetime.now()
        current_time = now.time()

        print("Starting a new trading cycle...")

        current_cash = float(account.cash)
        min_cash_threshold = starting_cash * 0.10

        if current_cash <= min_cash_threshold:
            print(f"Warning: Cash balance is too low (${current_cash:.2f}). No further buy/short orders will be placed.")

        for symbol in tradable_tickers:
            print(f"\nProcessing {symbol}...")

            try:
                candles = get_recent_candles(symbol)
                if candles.empty:
                    print(f"No data found for {symbol}.")
                    continue  

                current_position_qty = get_current_position_qty(symbol)  # fetched at start

                # ============= LONG TRADES (bearish market bias) ============
                if overall_bias == 'bearish':
                    if current_cash > min_cash_threshold and is_bullish_candlestick(candles):
                        qty = position_sizing(symbol)
                        if qty > 0:
                            try:
                                buy_order = api.submit_order(
                                    symbol=symbol,
                                    qty=qty,
                                    side='buy',
                                    type='market',
                                    time_in_force='gtc'
                                )
                                print(f"Buy order successfully placed for {symbol}.")
                                filled_order = wait_for_order_fill(buy_order.id, timeout=60)
                                if not filled_order:
                                    print(f"Order for {symbol} did not fill within timeout period.")
                                    continue
                            except Exception as e:
                                print(f"Error in buy order process for {symbol}: {e}")
                        else:
                            print(f"Not enough cash to buy {symbol} or position sizing returned 0.")

                # ============= SHORT TRADES (bullish market bias) ============
                elif overall_bias == 'bullish':
                    if current_cash > min_cash_threshold and is_bearish_candlestick(candles):
                        qty = position_sizing(symbol)
                        if qty > 0:
                            try:
                                short_order = api.submit_order(
                                    symbol=symbol,
                                    qty=qty,
                                    side='sell',  # short
                                    type='market',
                                    time_in_force='gtc'
                                )
                                print(f"Short order placed for {symbol}")

                                filled_order = wait_for_order_fill(short_order.id, timeout=60)
                                if not filled_order:
                                    print(f"Short order for {symbol} did not fill within timeout period.")
                                    continue

                                entry_price = float(filled_order.filled_avg_price)

                                # Identify swing high for stop-loss placement
                                swing_high = candles['high'].rolling(window=5).max().iloc[-2]  # avoid current bar
                                buffer = 0.5
                                stop_price = round(swing_high + buffer, 2)

                                set_stop_loss(symbol, stop_price)
                                print(f"Stop loss for {symbol} set at {stop_price}")

                                # RE-FETCH current position after successful short
                                current_position_qty = get_current_position_qty(symbol)

                            except Exception as e:
                                print(f"Error in short order process for {symbol}: {e}")
                        else:
                            print(f"Not enough margin to short {symbol} or position sizing returned 0.")

                # ============= STOP-LOSS CHECK ============
                if current_position_qty < 0:  # now correct (check if we are short)
                    stop_price = get_stop_loss(symbol)
                    if stop_price:
                        last_candle_close = candles.iloc[-1]['close']
                        if last_candle_close > stop_price:
                            try:
                                api.submit_order(
                                    symbol=symbol,
                                    qty=abs(current_position_qty),
                                    side='buy',  # cover short
                                    type='market',
                                    time_in_force='gtc'
                                )
                                print(f"Stop loss triggered. Covered short on {symbol} at {last_candle_close}")
                                set_stop_loss(symbol, None)
                            except Exception as e:
                                print(f"Failed to close short on stop loss for {symbol}: {e}")
                    else:
                        print(f"No stop loss set for short position in {symbol}.")

                else:
                    print(f"No active short position to manage for {symbol}.")

            except Exception as e:
                print(f"Error processing {symbol}: {e}")

        print("------------------------------------")
        print(f"Day Trade Count in the last 5 business days: {account.daytrade_count}")    
        print(f"Today's Bias: {overall_bias}")    
        print_cash_details()

        # Reset daily loop counter if new day
        current_date = datetime.now().date()
        if current_date != last_date:
            loop_count = 0
            last_date = current_date
            print(f"New day: loop count reset to zero.")
        loop_count += 1
        print(f"Loop {loop_count}.")
        print("Time Stopped:", datetime.now().strftime("%m-%d-%y %H:%M:%S"))

        print("Cycle complete. Sleeping for 1 minute before next cycle...")
        for _ in range(60):
            if stop_flag:
                print("Stopping the trading loop.")
                break
            time.sleep(1)

    except Exception as e:
        print(f"Error in main trading loop: {e}")
        print("Sleeping for 1 minute before retrying...")
        time.sleep(60)
'''