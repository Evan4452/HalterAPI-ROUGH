import yfinance as yf
import talib
import numpy as np
import pandas as pd

def get_recent_candles(symbol, interval='1d', period='60d'):
    df = yf.download(symbol, interval=interval, period=period)
    df.dropna(inplace=True)
    return df

def macd_bullish(df):
    macd, signal, _ = talib.MACD(df['Close'], fastperiod=12, slowperiod=26, signalperiod=9)
    return macd.iloc[-1] > signal.iloc[-1]

def bullish_trend(df):
    ema50 = talib.EMA(df['Close'], timeperiod=50)
    ema200 = talib.EMA(df['Close'], timeperiod=200)
    return ema50.iloc[-1] > ema200.iloc[-1]

def high_volume(df):
    volume = df['Volume']
    avg_volume = volume.rolling(window=10).mean()
    return volume.iloc[-1] > avg_volume.iloc[-1]

def rsi_oversold(df):
    rsi = talib.RSI(df['Close'], timeperiod=14)
    return rsi.iloc[-1] < 40

def price_below_lower_band(df):
    upper, middle, lower = talib.BBANDS(df['Close'], timeperiod=20)
    return df['Close'].iloc[-1] < lower.iloc[-1]

def stochastic_oversold(df):
    slowk, slowd = talib.STOCHF(df['High'], df['Low'], df['Close'], fastk_period=14, fastd_period=3)
    return slowk.iloc[-1] < 20

def adx_strong_trend(df):
    adx = talib.ADX(df['High'], df['Low'], df['Close'], timeperiod=14)
    return adx.iloc[-1] > 25

# Main execution
if __name__ == '__main__':
    import sys
    if len(sys.argv) < 2:
        print("Usage: python check_indicators.py <TICKER>")
        sys.exit(1)

    ticker = sys.argv[1]
    df = get_recent_candles(ticker)

    print(f"MACD Bullish: {macd_bullish(df)}")
    print(f"Bullish Trend (EMA50 > EMA200): {bullish_trend(df)}")
    print(f"High Volume: {high_volume(df)}")
    print(f"RSI Oversold (<40): {rsi_oversold(df)}")
    print(f"Price Below Lower Bollinger Band: {price_below_lower_band(df)}")
    print(f"Stochastic Oversold (<20): {stochastic_oversold(df)}")
    print(f"ADX Strong Trend (>25): {adx_strong_trend(df)}")
