import pandas as pd
import numpy as np
from ta.trend import EMAIndicator, ADXIndicator, MACD, PSARIndicator, IchimokuIndicator
from ta.volatility import AverageTrueRange, BollingerBands, DonchianChannel, KeltnerChannel
from ta.momentum import RSIIndicator, StochasticOscillator, ROCIndicator, WilliamsRIndicator
from ta.volume import OnBalanceVolumeIndicator
from ta.volume import ChaikinMoneyFlowIndicator
from ta.volume import AccDistIndexIndicator





# BULLISH SIGNALS




# Timeframe mapping
TIMEFRAME_MAP = {
    '15min': '15T',
    '30min': '30T',
    '1h': '1H',
    '1d': '1D',
    '1w': '1W'
}

# Resampling
def resample_data_bullish(df, timeframe):
    tf = TIMEFRAME_MAP.get(timeframe.lower())
    if not tf:
        raise ValueError(f"Unsupported timeframe: {timeframe}")
    df = df.copy()
    df.index = pd.to_datetime(df.index)
    return df.resample(tf).agg({
        'open': 'first',
        'high': 'max',
        'low': 'min',
        'close': 'last',
        'volume': 'sum'
    }).dropna()

# ----- Indicator Calculations -----

def calculate_ema_bullish(df):
    ema = EMAIndicator(df['close'], window=20).ema_indicator()
    df['EMA_20'] = ema
    df['EMA_Bullish'] = (df['close'] > ema) & (df['close'].shift(1) <= ema.shift(1))
    return df

def calculate_macd_bullish(df):
    macd = MACD(df['close'])
    df['MACD'] = macd.macd()
    df['MACD_signal'] = macd.macd_signal()
    df['MACD_Bullish'] = (df['MACD'] > df['MACD_signal']) & (df['MACD'].shift(1) <= df['MACD_signal'].shift(1))
    return df

def calculate_adx_bullish(df):
    adx = ADXIndicator(df['high'], df['low'], df['close'], window=14)
    df['ADX'] = adx.adx()
    df['+DI'] = adx.adx_pos()
    df['-DI'] = adx.adx_neg()
    df['ADX_Bullish'] = (df['+DI'] > df['-DI']) & (df['ADX'] > 20)
    return df

def calculate_parabolic_sar_bullish(df):
    psar = PSARIndicator(df['high'], df['low'], df['close'], step=0.02, max_step=0.2)
    df['SAR'] = psar.psar()
    df['SAR_Bullish'] = (df['close'] > df['SAR']) & (df['close'].shift(1) <= df['SAR'].shift(1))
    return df

def calculate_ichimoku_bullish(df):
    ichi = IchimokuIndicator(df['high'], df['low'], window1=9, window2=26, window3=52)
    df['tenkan_sen'] = ichi.ichimoku_conversion_line()
    df['kijun_sen'] = ichi.ichimoku_base_line()
    df['Ichimoku_Bullish'] = (df['tenkan_sen'] > df['kijun_sen']) & (df['tenkan_sen'].shift(1) <= df['kijun_sen'].shift(1))
    return df

def calculate_supertrend_bullish(df, period=10, multiplier=3):
    atr = AverageTrueRange(df['high'], df['low'], df['close'], window=period).average_true_range()
    hl2 = (df['high'] + df['low']) / 2
    upperband = hl2 + multiplier * atr
    lowerband = hl2 - multiplier * atr

    trend = [True]
    supertrend = [np.nan]

    for i in range(1, len(df)):
        if df['close'][i] > upperband[i - 1]:
            trend.append(True)
        elif df['close'][i] < lowerband[i - 1]:
            trend.append(False)
        else:
            trend.append(trend[-1])
            if trend[-1] and lowerband[i] < lowerband[i - 1]:
                lowerband[i] = lowerband[i - 1]
            elif not trend[-1] and upperband[i] > upperband[i - 1]:
                upperband[i] = upperband[i - 1]
        supertrend.append(lowerband[i] if trend[-1] else upperband[i])

    df['SuperTrend'] = supertrend
    df['SuperTrend_Bullish'] = trend
    return df

def calculate_rsi_bullish(df):
    rsi = RSIIndicator(df['close'], window=14).rsi()
    df['RSI'] = rsi
    df['RSI_Bullish'] = (rsi > 30) & (rsi.shift(1) <= 30)
    return df

def calculate_stochastic_bullish(df):
    sto = StochasticOscillator(df['high'], df['low'], df['close'], window=14, smooth_window=3)
    k = sto.stoch()
    d = sto.stoch_signal()
    df['Stoch_K'] = k
    df['Stoch_D'] = d
    df['Stochastic_Bullish'] = (k > d) & (k.shift(1) <= d.shift(1)) & (k < 20)
    return df

def calculate_roc_bullish(df):
    roc = ROCIndicator(df['close'], window=12).roc()
    df['ROC'] = roc
    df['ROC_Bullish'] = (roc > 0) & (roc.shift(1) <= 0)
    return df

def calculate_williams_r_bullish(df):
    willr = WilliamsRIndicator(df['high'], df['low'], df['close'], lbp=14).williams_r()
    df['Williams_%R'] = willr
    df['WilliamsR_Bullish'] = (willr > -80) & (willr.shift(1) <= -80)
    return df

def calculate_cci_bullish(df, window=20, constant=0.015):
    # Typical Price
    tp = (df['high'] + df['low'] + df['close']) / 3
    # Simple Moving Average of Typical Price
    sma_tp = tp.rolling(window=window, min_periods=window).mean()
    # Mean Deviation
    mean_dev = tp.rolling(window=window, min_periods=window).apply(lambda x: (abs(x - x.mean())).mean(), raw=True)
    # CCI Calculation
    cci = (tp - sma_tp) / (constant * mean_dev)
    df['CCI'] = cci
    # Bullish signal: CCI crosses above -100
    df['CCI_Bullish'] = (cci > -100) & (cci.shift(1) <= -100)
    return df

def calculate_bollinger_bands_bullish(df):
    bb = BollingerBands(close=df['close'], window=20, window_dev=2)
    df['BB_lower'] = bb.bollinger_lband()
    df['BB_upper'] = bb.bollinger_hband()
    df['BB_MA'] = bb.bollinger_mavg()
    df['BB_Bullish'] = (df['close'] > df['BB_lower']) & (df['close'].shift(1) <= df['BB_lower'].shift(1))
    return df

def calculate_atr_bullish(df):
    atr = AverageTrueRange(df['high'], df['low'], df['close'], window=14)
    df['ATR'] = atr.average_true_range()
    df['ATR_Bullish'] = df['ATR'] > df['ATR'].shift(1)
    return df

def calculate_donchian_bullish(df):
    dc = DonchianChannel(df['high'], df['low'], window=20)
    df['Donchian_Upper'] = dc.donchian_channel_hband()
    df['Donchian_Lower'] = dc.donchian_channel_lband()
    df['Donchian_Bullish'] = (df['close'] > df['Donchian_Upper']) & (df['close'].shift(1) <= df['Donchian_Upper'].shift(1))
    return df

def calculate_keltner_bullish(df):
    kc = KeltnerChannel(df['high'], df['low'], df['close'], window=20)
    df['Keltner_Upper'] = kc.keltner_channel_hband()
    df['Keltner_Lower'] = kc.keltner_channel_lband()
    df['Keltner_Mid'] = kc.keltner_channel_mband()
    df['Keltner_Bullish'] = (df['close'] > df['Keltner_Mid']) & (df['close'].shift(1) <= df['Keltner_Mid'].shift(1))
    return df

def calculate_obv_bullish(df):
    obv = OnBalanceVolumeIndicator(close=df['close'], volume=df['volume']).on_balance_volume()
    df['OBV'] = obv
    df['OBV_Bullish'] = df['OBV'] > df['OBV'].shift(1)
    return df

def calculate_vwap_bullish(df):
    # Intraday VWAP (resets daily)
    df['cum_vol'] = df['volume'].cumsum()
    df['cum_vol_price'] = (df['close'] * df['volume']).cumsum()
    df['VWAP'] = df['cum_vol_price'] / df['cum_vol']
    df['VWAP_Bullish'] = (df['close'] > df['VWAP']) & (df['close'].shift(1) <= df['VWAP'].shift(1))
    return df

def calculate_cmf_bullish(df):
    cmf = ChaikinMoneyFlowIndicator(high=df['high'], low=df['low'], close=df['close'], volume=df['volume'], window=20)
    df['CMF'] = cmf.chaikin_money_flow()
    df['CMF_Bullish'] = df['CMF'] > 0
    return df

def calculate_ad_line_bullish(df):
    ad = AccDistIndexIndicator(high=df['high'], low=df['low'], close=df['close'], volume=df['volume'])
    df['AD_Line'] = ad.acc_dist_index()
    df['AD_Bullish'] = df['AD_Line'] > df['AD_Line'].shift(1)
    return df

def calculate_high_volume_bullish(df, factor=1.5, window=20):
    avg_vol = df['volume'].rolling(window=window).mean()
    df['HighVolume_Bullish'] = (df['volume'] > factor * avg_vol) & (df['close'] > df['open'])
    return df

def calculate_pivot_points_bullish(df):
    df['Pivot'] = (df['high'].shift(1) + df['low'].shift(1) + df['close'].shift(1)) / 3
    df['R1'] = 2 * df['Pivot'] - df['low'].shift(1)
    df['S1'] = 2 * df['Pivot'] - df['high'].shift(1)

    # Bullish: close crosses above R1 or bounces from S1
    df['Pivot_Bullish'] = (
        (df['close'] > df['R1']) & (df['close'].shift(1) <= df['R1']) |
        (df['close'] > df['S1']) & (df['close'].shift(1) <= df['S1'])
    )
    return df

def calculate_fibonacci_bounce_bullish(df, lookback=20):
    high = df['high'].rolling(window=lookback).max()
    low = df['low'].rolling(window=lookback).min()

    df['Fib_50'] = low + 0.5 * (high - low)
    df['Fib_618'] = low + 0.618 * (high - low)

    # Bullish: close bounces up off 50% or 61.8% retracement
    df['Fibonacci_Bullish'] = (
        (df['close'] > df['Fib_50']) & (df['close'].shift(1) <= df['Fib_50']) |
        (df['close'] > df['Fib_618']) & (df['close'].shift(1) <= df['Fib_618'])
    )
    return df

def calculate_tema_bullish(df, window=20):
    # Calculate EMAs
    ema1 = df['close'].ewm(span=window, adjust=False).mean()
    ema2 = ema1.ewm(span=window, adjust=False).mean()
    ema3 = ema2.ewm(span=window, adjust=False).mean()
    # Calculate TEMA
    tema = 3 * (ema1 - ema2) + ema3
    df['TEMA'] = tema
    # Bullish signal: close crosses above TEMA
    df['TEMA_Bullish'] = (df['close'] > tema) & (df['close'].shift(1) <= tema.shift(1))
    return df

def calculate_hull_moving_average_bullish(df, period=21):
    wma_half = df['close'].rolling(window=period // 2).mean()
    wma_full = df['close'].rolling(window=period).mean()
    raw_hma = 2 * wma_half - wma_full
    hma = raw_hma.rolling(window=int(np.sqrt(period))).mean()
    df['HMA'] = hma
    df['HMA_Bullish'] = hma > hma.shift(1)
    return df

def calculate_elders_force_index_bullish(df):
    df['EFI'] = (df['close'] - df['close'].shift(1)) * df['volume']
    df['EFI_Bullish'] = (df['EFI'] > 0) & (df['EFI'].shift(1) <= 0)
    return df

def calculate_zscore_bullish(df, window=20):
    mean = df['close'].rolling(window).mean()
    std = df['close'].rolling(window).std()
    z = (df['close'] - mean) / std
    df['ZScore'] = z
    df['ZScore_Bullish'] = (z > -1.5) & (z.shift(1) <= -1.5)
    return df

def calculate_selected_indicators(df, selected_indicators, timeframe='1h'):
    df = resample_data(df, timeframe)

    indicator_map = {
        'EMA Bullish': calculate_ema_bullish,
        'MACD Bullish': calculate_macd_bullish,
        'ADX Bullish': calculate_adx_bullish,
        'Parabolic SAR Bullish': calculate_parabolic_sar_bullish,
        'Ichimoku Bullish': calculate_ichimoku_bullish,
        'SuperTrend Bullish': calculate_supertrend_bullish,
        'RSI Bullish': calculate_rsi_bullish,
        'Stochastic Bullish': calculate_stochastic_bullish,
        'ROC Bullish': calculate_roc_bullish,
        'Williams %R Bullish': calculate_williams_r_bullish,
        'CCI Bullish': calculate_cci_bullish,
        'Bollinger Bands Bullish': calculate_bollinger_bands_bullish,
        'ATR Bullish': calculate_atr_bullish,
        'Donchian Channels Bullish': calculate_donchian_bullish,
        'Keltner Channels Bullish': calculate_keltner_bullish,
        'OBV Bullish': calculate_obv_bullish,
        'VWAP Bullish': calculate_vwap_bullish,
        'CMF Bullish': calculate_cmf_bullish,
        'Accumulation/Distribution Bullish': calculate_ad_line_bullish,
        'High Volume Bullish': calculate_high_volume_bullish,
        'Pivot Points Bullish': calculate_pivot_points_bullish,
        'Fibonacci Retracement Bullish': calculate_fibonacci_bounce_bullish,
        'TEMA Bullish': calculate_tema_bullish,
        'Hull MA Bullish': calculate_hull_moving_average_bullish,
        'Elder Force Index Bullish': calculate_elders_force_index_bullish,
        'Z-Score Bullish': calculate_zscore_bullish
    }

    for ind in selected_indicators:
        if ind in indicator_map:
            df = indicator_map[ind](df)

    return df




#------------------- BULLISH SMART MONEY -------------------#




def find_swings_bullish(df, left=2, right=2):
    highs = df['high']
    lows = df['low']
    swing_high = highs[(highs.shift(left) < highs) & (highs.shift(-right) < highs)]
    swing_low = lows[(lows.shift(left) > lows) & (lows.shift(-right) > lows)]
    swings = pd.DataFrame(index=df.index)
    swings['swing_high'] = swing_high
    swings['swing_low'] = swing_low
    return swings

def calculate_bos_bullish(df):
    swings = find_swings(df)
    df['BOS_Bullish'] = False
    last_high = None

    for i in swings['swing_high'].dropna().index:
        last_high = df.loc[i, 'high']
    for j in df.index:
        if last_high and df.loc[j, 'close'] > last_high:
            df.loc[j, 'BOS_Bullish'] = True
            last_high = df.loc[j, 'high']
    return df

def calculate_liquidity_sweep_bullish(df, lookback=5):
    df['Liquidity_Sweep_Bullish'] = False
    for i in range(lookback, len(df)):
        window = df.iloc[i - lookback:i]
        low = window['low'].min()
        if df['low'].iat[i] < low and df['close'].iat[i] > window['close'].iat[-2]:
            df['Liquidity_Sweep_Bullish'].iat[i] = True
    return df

def calculate_order_blocks_bullish(df):
    df['OrderBlock_Bullish'] = False
    df['BreakerBlock_Bullish'] = False
    for i in range(1, len(df)):
        if df['BOS_Bullish'].iat[i]:
            block = df.iloc[i - 1]
            if block['close'] < block['open']:
                df['OrderBlock_Bullish'].iat[i] = True
                if df['close'].iat[i] > block['high']:
                    df['BreakerBlock_Bullish'].iat[i] = True
    return df

def calculate_fvg_bullish(df):
    df['FVG_Bullish'] = False
    df['IFVG_Bullish'] = False
    for i in range(2, len(df)):
        a, b, c = df.iloc[i - 2:i + 1]
        if b['low'] > a['high'] and b['low'] > c['high']:
            df['FVG_Bullish'].iat[i] = True
        if b['high'] < a['low'] and c['close'] > b['high']:
            df['IFVG_Bullish'].iat[i] = True
    return df

def calculate_discount_bullish(df, swing_window=20):
    df['Discount_Bullish'] = False
    rolling_high = df['high'].rolling(swing_window).max()
    rolling_low = df['low'].rolling(swing_window).min()
    equilibrium = (rolling_high + rolling_low) / 2
    df['Discount_Bullish'] = df['close'] < equilibrium
    return df

def calculate_smc_signals_bullish(df):
    df = calculate_bos_bullish(df)
    df = calculate_liquidity_sweep_bullish(df)
    df = calculate_order_blocks_bullish(df)
    df = calculate_fvg_bullish(df)
    df = calculate_discount_bullish(df)
    return df






# BEARISH SIGNALS





# Timeframe mapping
TIMEFRAME_MAP = { 
    '15min':'15T',
    '30min':'30T',
    '1h':'1H',
    '1d':'1D',
    '1w':'1W' }

def resample_data(df, timeframe):
    tf = TIMEFRAME_MAP.get(timeframe.lower())
    if not tf: raise ValueError(f"Unsupported timeframe: {timeframe}")
    df = df.copy()
    df.index = pd.to_datetime(df.index)
    return df.resample(tf).agg({
        'open':'first','high':'max','low':'min','close':'last','volume':'sum'
    }).dropna()

### Technical Indicators – Bearish Signals Only

def calculate_ema_bearish(df):
    ema = EMAIndicator(df['close'], window=20).ema_indicator()
    df['EMA_20'] = ema
    df['EMA_Bearish'] = (df['close'] < ema) & (df['close'].shift(1) >= ema.shift(1))
    return df

def calculate_macd_bearish(df):
    macd = MACD(df['close'])
    df['MACD'] = macd.macd()
    df['MACD_signal'] = macd.macd_signal()
    df['MACD_Bearish'] = (df['MACD'] < df['MACD_signal']) & (df['MACD'].shift(1) >= df['MACD_signal'].shift(1))
    return df

def calculate_adx_bearish(df):
    adx = ADXIndicator(df['high'], df['low'], df['close'], window=14)
    df['ADX'] = adx.adx()
    df['+DI'] = adx.adx_pos()
    df['-DI'] = adx.adx_neg()
    df['ADX_Bearish'] = (df['-DI'] > df['+DI']) & (df['ADX'] > 20)
    return df

def calculate_parabolic_sar_bearish(df):
    psar = PSARIndicator(df['high'], df['low'], df['close'], step=0.02, max_step=0.2)
    df['SAR'] = psar.psar()
    df['SAR_Bearish'] = (df['close'] < df['SAR']) & (df['close'].shift(1) >= df['SAR'].shift(1))
    return df

def calculate_ichimoku_bearish(df):
    ichi = IchimokuIndicator(df['high'], df['low'], window1=9, window2=26, window3=52)
    df['tenkan_sen'] = ichi.ichimoku_conversion_line()
    df['kijun_sen'] = ichi.ichimoku_base_line()
    df['Ichimoku_Bearish'] = (df['tenkan_sen'] < df['kijun_sen']) & (df['tenkan_sen'].shift(1) >= df['kijun_sen'].shift(1))
    return df

def calculate_supertrend_bearish(df, period=10, multiplier=3):
    atr = AverageTrueRange(df['high'], df['low'], df['close'], window=period).average_true_range()
    hl2 = (df['high'] + df['low'])/2
    ub = hl2 + multiplier*atr; lb = hl2 - multiplier*atr
    trend=[True]; st=[np.nan]
    for i in range(1,len(df)):
        if df['close'][i] > ub[i-1]:
            trend.append(True)
        elif df['close'][i] < lb[i-1]:
            trend.append(False)
        else:
            trend.append(trend[-1])
        st.append(lb[i] if trend[-1] else ub[i])
    df['SuperTrend']=st
    df['SuperTrend_Bearish']=[not t for t in trend]
    return df

def calculate_rsi_bearish(df):
    rsi = RSIIndicator(df['close'], window=14).rsi()
    df['RSI']=rsi
    df['RSI_Bearish'] = (rsi < 70) & (rsi.shift(1) >= 70)
    return df

def calculate_stochastic_bearish(df):
    sto = StochasticOscillator(df['high'], df['low'], df['close'], window=14, smooth_window=3)
    k=sto.stoch(); d=sto.stoch_signal()
    df['Stoch_K']=k; df['Stoch_D']=d
    df['Stochastic_Bearish'] = (k < d)&(k.shift(1)>=d.shift(1))&(k>80)
    return df

def calculate_roc_bearish(df):
    roc = ROCIndicator(df['close'], window=12).roc()
    df['ROC']=roc
    df['ROC_Bearish']=(roc<0)&(roc.shift(1)>=0)
    return df

def calculate_williams_r_bearish(df):
    willr = WilliamsRIndicator(df['high'], df['low'], df['close'], lbp=14).williams_r()
    df['Williams_%R']=willr
    df['WilliamsR_Bearish']=(willr<-20)&(willr.shift(1)>=-20)
    return df

def calculate_cci_bearish(df, window=20, constant=0.015):
    tp = (df['high'] + df['low'] + df['close']) / 3
    sma_tp = tp.rolling(window=window, min_periods=window).mean()
    mean_dev = tp.rolling(window=window, min_periods=window).apply(lambda x: (abs(x - x.mean())).mean(), raw=True)
    cci = (tp - sma_tp) / (constant * mean_dev)
    df['CCI'] = cci
    df['CCI_Bearish'] = (cci < 100) & (cci.shift(1) >= 100)
    return df

def calculate_bollinger_bands_bearish(df):
    bb = BollingerBands(df['close'],window=20,window_dev=2)
    df['BB_lower'] = bb.bollinger_lband()
    df['BB_upper'] = bb.bollinger_hband()
    df['BB_MA']= bb.bollinger_mavg()
    df['BB_Bearish'] = (df['close'] < df['BB_upper']) & (df['close'].shift(1) >= df['BB_upper'].shift(1))
    return df

def calculate_atr_bearish(df):
    atr = AverageTrueRange(df['high'],df['low'],df['close'],window=14).average_true_range()
    df['ATR']=atr
    df['ATR_Bearish']=atr<atr.shift(1)
    return df

def calculate_donchian_bearish(df):
    dc = DonchianChannel(df['high'],df['low'],window=20)
    df['Donchian_Upper']=dc.donchian_channel_hband()
    df['Donchian_Lower']=dc.donchian_channel_lband()
    df['Donchian_Bearish']=(df['close']<df['Donchian_Lower'])&(df['close'].shift(1)>=df['Donchian_Lower'].shift(1))
    return df

def calculate_keltner_bearish(df):
    kc = KeltnerChannel(df['high'],df['low'],df['close'],window=20)
    df['Keltner_Mid']=kc.keltner_channel_mband()
    df['Keltner_Bearish']=(df['close']<df['Keltner_Mid'])&(df['close'].shift(1)>=df['Keltner_Mid'].shift(1))
    return df

def calculate_obv_bearish(df):
    obv=OnBalanceVolumeIndicator(df['close'],df['volume']).on_balance_volume()
    df['OBV']=obv
    df['OBV_Bearish']=obv<obv.shift(1)
    return df

def calculate_vwap_bearish(df):
    df['cum_vol']=df['volume'].cumsum()
    df['cum_vol_price']=(df['close']*df['volume']).cumsum()
    df['VWAP']=df['cum_vol_price']/df['cum_vol']
    df['VWAP_Bearish']=(df['close']<df['VWAP'])&(df['close'].shift(1)>=df['VWAP'].shift(1))
    return df

def calculate_cmf_bearish(df):
    cmf = ChaikinMoneyFlowIndicator(df['high'],df['low'],df['close'],df['volume'], window=20).chaikin_money_flow()
    df['CMF']=cmf
    df['CMF_Bearish']=cmf<0
    return df

def calculate_ad_line_bearish(df):
    ad=AccDistIndexIndicator(df['high'],df['low'],df['close'],df['volume']).acc_dist_index()
    df['AD_Line']=ad
    df['AD_Bearish']=ad<ad.shift(1)
    return df

def calculate_high_volume_bearish(df,factor=1.5,window=20):
    avg=df['volume'].rolling(window).mean()
    df['HighVolume_Bearish']=(df['volume']>factor*avg)&(df['close']<df['open'])
    return df

def calculate_pivot_points_bearish(df):
    df['Pivot']=(df['high'].shift(1)+df['low'].shift(1)+df['close'].shift(1))/3
    df['R1']=2*df['Pivot']-df['low'].shift(1)
    df['S1']=2*df['Pivot']-df['high'].shift(1)
    df['Pivot_Bearish'] = (
        (df['close'] < df['S1']) & (df['close'].shift(1) >= df['S1']) |
        (df['close'] < df['R1']) & (df['close'].shift(1) >= df['R1'])
    )
    return df

def calculate_fibonacci_bounce_bearish(df,lookback=20):
    high=df['high'].rolling(lookback).max()
    low=df['low'].rolling(lookback).min()
    df['Fib_50']=low+0.5*(high-low)
    df['Fib_618']=low+0.618*(high-low)
    df['Fibonacci_Bearish']=(
        (df['close']<df['Fib_50'])&(df['close'].shift(1)>=df['Fib_50'])|
        (df['close']<df['Fib_618'])&(df['close'].shift(1)>=df['Fib_618'])
    )
    return df

def calculate_tema_bearish(df,window=20):
    ema1=df['close'].ewm(span=window,adjust=False).mean()
    ema2=ema1.ewm(span=window,adjust=False).mean()
    ema3=ema2.ewm(span=window,adjust=False).mean()
    tema=3*(ema1-ema2)+ema3
    df['TEMA']=tema
    df['TEMA_Bearish']=(df['close']<tema)&(df['close'].shift(1)>=tema.shift(1))
    return df

def calculate_hull_moving_average_bearish(df,period=21):
    wma_half=df['close'].rolling(period//2).mean()
    wma_full=df['close'].rolling(period).mean()
    raw=2*wma_half-wma_full
    hma=raw.rolling(int(np.sqrt(period))).mean()
    df['HMA']=hma
    df['HMA_Bearish']=hma<hma.shift(1)
    return df

def calculate_elders_force_index_bearish(df):
    df['EFI']=(df['close']-df['close'].shift(1))*df['volume']
    df['EFI_Bearish']=(df['EFI']<0)&(df['EFI'].shift(1)>=0)
    return df

def calculate_zscore_bearish(df,window=20):
    mean=df['close'].rolling(window).mean()
    std=df['close'].rolling(window).std()
    z=(df['close']-mean)/std
    df['ZScore']=z
    df['ZScore_Bearish']=(z<1.5)&(z.shift(1)>=1.5)
    return df

def calculate_selected_indicators(df, selected_indicators, timeframe='1h'):
    df = resample_data(df, timeframe)
    for ind in selected_indicators:
        mapping = {
          'EMA Bearish': calculate_ema_bearish,
          'MACD Bearish': calculate_macd_bearish,
          'ADX Bearish': calculate_adx_bearish,
          'Parabolic SAR Bearish': calculate_parabolic_sar_bearish,
          'Ichimoku Bearish': calculate_ichimoku_bearish,
          'SuperTrend Bearish': calculate_supertrend_bearish,
          'RSI Bearish': calculate_rsi_bearish,
          'Stochastic Bearish': calculate_stochastic_bearish,
          'ROC Bearish': calculate_roc_bearish,
          'Williams %R Bearish': calculate_williams_r_bearish,
          'CCI Bearish': calculate_cci_bearish,
          'Bollinger Bands Bearish': calculate_bollinger_bands_bearish,
          'ATR Bearish': calculate_atr_bearish,
          'Donchian Channels Bearish': calculate_donchian_bearish,
          'Keltner Channels Bearish': calculate_keltner_bearish,
          'OBV Bearish': calculate_obv_bearish,
          'VWAP Bearish': calculate_vwap_bearish,
          'CMF Bearish': calculate_cmf_bearish,
          'Accumulation/Distribution Bearish': calculate_ad_line_bearish,
          'High Volume Bearish': calculate_high_volume_bearish,
          'Pivot Points Bearish': calculate_pivot_points_bearish,
          'Fibonacci Retracement Bearish': calculate_fibonacci_bounce_bearish,
          'TEMA Bearish': calculate_tema_bearish,
          'Hull MA Bearish': calculate_hull_moving_average_bearish,
          'Elder Force Index Bearish': calculate_elders_force_index_bearish,
          'Z-Score Bearish': calculate_zscore_bearish
        }
        if ind in mapping: df = mapping[ind](df)
    return df




#------------------- BEARISH SMART MONEY (NOT FOR BETA) -------------------#



def find_swings(df,left=2,right=2):
    highs, lows = df['high'], df['low']
    swing_high = highs[(highs.shift(left)<highs)&(highs.shift(-right)<highs)]
    swing_low = lows[(lows.shift(left)>lows)&(lows.shift(-right)>lows)]
    return swing_high.dropna(), swing_low.dropna()

def calculate_bos_bearish(df):
    highs, _ = find_swings(df)
    df['BOS_Bearish'] = False
    last_low = None
    for i in highs.index: last_low = df.loc[i,'low']
    for j in df.index:
        if last_low and df.loc[j,'close'] < last_low:
            df.loc[j,'BOS_Bearish'] = True
            last_low = df.loc[j,'low']
    return df

def calculate_liquidity_sweep_bearish(df, lookback=5):
    df['Liquidity_Sweep_Bearish'] = False
    for i in range(lookback,len(df)):
        window=df.iloc[i-lookback:i]
        high = window['high'].max()
        if df['high'].iat[i] > high and df['close'].iat[i] < window['close'].iat[-2]:
            df['Liquidity_Sweep_Bearish'].iat[i] = True
    return df

def calculate_order_blocks_bearish(df):
    df['OrderBlock_Bearish'] = False
    df['BreakerBlock_Bearish'] = False
    for i in range(1,len(df)):
        if df['BOS_Bearish'].iat[i]:
            blk = df.iloc[i-1]
            if blk['close'] > blk['open']:
                df['OrderBlock_Bearish'].iat[i]=True
                if df['close'].iat[i] < blk['low']:
                    df['BreakerBlock_Bearish'].iat[i]=True
    return df

def calculate_fvg_bearish(df):
    df['FVG_Bearish']=False
    df['IFVG_Bearish']=False
    for i in range(2,len(df)):
        a,b,c = df.iloc[i-2:i+1]
        if b['high'] < a['low'] and b['high'] < c['low']:
            df['FVG_Bearish'].iat[i]=True
        if b['low'] > a['high'] and c['close'] < b['low']:
            df['IFVG_Bearish'].iat[i]=True
    return df

def calculate_discount_bearish(df,swing_window=20):
    df['Discount_Bearish']=False
    r_high=df['high'].rolling(swing_window).max()
    r_low=df['low'].rolling(swing_window).min()
    eq = (r_high+r_low)/2
    df['Discount_Bearish']=df['close']>eq
    return df

def calculate_smc_signals_bearish(df):
    df = calculate_bos_bearish(df)
    df = calculate_liquidity_sweep_bearish(df)
    df = calculate_order_blocks_bearish(df)
    df = calculate_fvg_bearish(df)
    df = calculate_discount_bearish(df)
    return df