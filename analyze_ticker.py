import pandas as pd
import numpy as np
import talib
from datetime import datetime, timedelta
import alpaca_trade_api as tradeapi

# Alpaca API credentials (replace with your actual keys)
API_KEY = 'PKM0APS6C84ROVD3G60Y'
API_SECRET = 'PKM0APS6C84ROVD3G60Y'
BASE_URL = 'https://api.alpaca.markets'  # Unified base URL for trading and data

api = tradeapi.REST('PKM0APS6C84ROVD3G60Y', 'PKM0APS6C84ROVD3G60Y', 'https://api.alpaca.markets', api_version='v2')

# Function to fetch historical data from Alpaca
def get_historical_data(symbol):
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=90)


    bars = api.get_bars(
    symbol,
    tradeapi.TimeFrame.Day,
    start=start_date.isoformat(),
    end=end_date.isoformat(),
    feed='iex'
).df


    if bars.empty:
        return pd.DataFrame()

    bars = bars[bars['symbol'] == symbol]
    bars = bars.rename(columns={
        'open': 'open',
        'high': 'high',
        'low': 'low',
        'close': 'close',
        'volume': 'volume'
    })
    return bars[['open', 'high', 'low', 'close', 'volume']]

# Function to calculate Fibonacci retracement levels
def calculate_fibonacci_levels(df):
    recent_close = df['close'].iloc[-1]
    max_price = df['high'].max()
    min_price = df['low'].min()
    diff = max_price - min_price
    levels = [
        max_price - 0.236 * diff,
        max_price - 0.382 * diff,
        max_price - 0.5 * diff,
        max_price - 0.618 * diff,
    ]
    return levels

# Indicator checks
def check_indicators(df):
    close_prices = df['close'].values
    volume = df['volume'].values

    rsi = talib.RSI(close_prices, timeperiod=14)
    macd, macdsignal, _ = talib.MACD(close_prices)
    ema50 = talib.EMA(close_prices, timeperiod=50)
    ema200 = talib.EMA(close_prices, timeperiod=200)
    upper_band, middle_band, lower_band = talib.BBANDS(close_prices, timeperiod=20)
    slowk, slowd = talib.STOCHF(df['high'].values, df['low'].values, close_prices)
    adx = talib.ADX(df['high'].values, df['low'].values, close_prices)

    last = df.iloc[-1]
    last_rsi = rsi[-1] if not np.isnan(rsi[-1]) else 50
    macd_bullish = macd[-1] > macdsignal[-1]
    bullish_trend = ema50[-1] > ema200[-1]
    high_volume = volume[-1] > np.mean(volume[-10:])
    rsi_oversold = last_rsi < 40
    price_below_lower_band = last['close'] < lower_band[-1]
    stochastic_oversold = slowk[-1] < 20
    price_near_fib = any(abs(last['close'] - level) < 0.01 * last['close'] for level in calculate_fibonacci_levels(df))
    adx_strong_trend = adx[-1] > 25

    print("\nIndicator Results:")
    print(f"MACD Bullish: {macd_bullish}")
    print(f"Bullish Trend (EMA50 > EMA200): {bullish_trend}")
    print(f"High Volume: {high_volume}")
    print(f"RSI Oversold: {rsi_oversold}")
    print(f"Price Below Lower Bollinger Band: {price_below_lower_band}")
    print(f"Stochastic Oversold: {stochastic_oversold}")
    print(f"Price Near Fibonacci Level: {price_near_fib}")
    print(f"ADX Strong Trend (>25): {adx_strong_trend}")

# Main execution
if __name__ == "__main__":
    ticker = input("Which ticker would you like to analyze? ").upper()
    df = get_historical_data(ticker)

    if df.empty:
        print("Failed to fetch data for the ticker.")
    else:
        check_indicators(df)
