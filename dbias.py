import yfinance as yf
import pandas as pd
import numpy as np
import talib
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report
import matplotlib.pyplot as plt

def download_data():
    symbols = {
        'S&P 500': '^GSPC',
        'NASDAQ': '^IXIC',
        'Dow Jones': '^DJI',
        'US Dollar Index': 'DX-Y.NYB'
    }

    data = {}

    for name, symbol in symbols.items():
        df = yf.download(symbol, period='3mo', interval='1d', progress=False)
        if df.empty:
            print(f"⚠️  Warning: Data for {name} is empty.")
        else:
            data[name] = df

    return data

def add_indicators(df):
    close = df['Close'].values.flatten()

    df['RSI'] = talib.RSI(close, timeperiod=14)
    df['MA20'] = df['Close'].rolling(window=20).mean()
    df['MA50'] = df['Close'].rolling(window=50).mean()
    df['MACD'], df['MACD_signal'], _ = talib.MACD(close, fastperiod=12, slowperiod=26, signalperiod=9)

    df.dropna(inplace=True)
    return df

def prepare_data(data):
    all_data = []
    for index_name, df in data.items():
        if df.empty:
            continue

        df = add_indicators(df)
        if df.empty:
            print(f"{index_name} data empty after indicators.")
            continue

        df['Bias'] = np.where(df['Close'] > df['Close'].shift(1), 1, 0)
        df['Bias'] = np.where(df['Close'] < df['Close'].shift(1), -1, df['Bias'])

        features = ['RSI', 'MA20', 'MA50', 'MACD', 'MACD_signal']
        df = df[features + ['Bias']].dropna()
        df['Index'] = index_name
        all_data.append(df)

    if not all_data:
        print("All indices returned empty after preprocessing.")
        return None, None

    combined_data = pd.concat(all_data)
    combined_data.dropna(inplace=True)

    if combined_data.empty:
        print("Combined data is empty after final cleaning.")
        return None, None

    '''
    X = combined_data[features + ['Index']]
    y = combined_data['Bias']
    return pd.get_dummies(X), y
    '''

    X = combined_data[features + ['Index']]
    y = combined_data['Bias']

    X = pd.get_dummies(X)
    X.columns = X.columns.astype(str)  # ✅ Convert all column names to strings

    return X, y


def train_and_predict(X, y):
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, shuffle=False)
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    print("Model Evaluation:\n")
    print(classification_report(y_test, y_pred))
    return model, y_pred, y_test

def visualize_predictions(y_pred, y_test):
    plt.figure(figsize=(10,6))
    plt.plot(y_test.index, y_test, label='Actual Bias', color='blue')
    plt.plot(y_test.index, y_pred, label='Predicted Bias', color='red', alpha=0.7)
    plt.title('Actual vs Predicted Bias')
    plt.legend()
    plt.show()

def print_daily_bias_prediction(model, data):
    print("\n📈 Today's Bias Predictions:")
    for index_name, df in data.items():
        if df.empty:
            continue
        df = add_indicators(df)
        latest = df.iloc[-1:]
        if latest.empty:
            print(f"{index_name}: Not enough data")
            continue
        features = latest[['RSI', 'MA20', 'MA50', 'MACD', 'MACD_signal']]
        features['Index'] = index_name
        X_live = pd.get_dummies(features)
        X_live.columns = X_live.columns.astype(str)  # Match training format
        X_live = X_live.reindex(columns=model.feature_names_in_, fill_value=0)

        prediction = model.predict(X_live)[0]
        label = "📊 Bullish" if prediction == 1 else "📉 Bearish" if prediction == -1 else "⏸ Neutral"
        print(f"{index_name}: {label}")

def main():
    data = download_data()
    X, y = prepare_data(data)

    if X is None or y is None:
        print("⚠️ Data preparation failed. Exiting the program.")
        return

    model, y_pred, y_test = train_and_predict(X, y)
    visualize_predictions(y_pred, y_test)
    print_daily_bias_prediction(model, data)

if __name__ == "__main__":
    main()
