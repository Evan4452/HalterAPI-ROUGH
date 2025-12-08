# ETF PUTS

def buy_puts_on_bearish_bias(overall_bias, api, max_cost_per_contract=200):
    if overall_bias.lower() != "bearish":
        print("Market bias is not bearish — skipping put purchases.")
        return

    index_etfs = ["SPY", "QQQ", "DIA", "IWM"]
    expiration = get_nearest_expiration_date()  # You’ll define this helper function
    contracts_bought = []

    for symbol in index_etfs:
        try:
            options_chain = api.get_option_chain(symbol, expiration=expiration, option_type="put")
            if not options_chain:
                print(f"No options found for {symbol}.")
                continue

            # Filter ATM puts with good liquidity
            underlying_price = get_last_trade_price(symbol)
            best_contract = None
            min_diff = float("inf")

            for contract in options_chain:
                strike = float(contract.strike_price)
                diff = abs(strike - underlying_price)
                if diff < min_diff and contract.ask_price <= max_cost_per_contract and contract.volume >= 100:
                    best_contract = contract
                    min_diff = diff

            if best_contract:
                qty = 1  # or use a smarter position sizing strategy
                order = api.submit_option_order(
                    symbol=best_contract.symbol,
                    qty=qty,
                    side="buy",
                    type="market",
                    time_in_force="gtc"
                )
                contracts_bought.append(best_contract.symbol)
                print(f"Bought 1 PUT contract for {symbol} → {best_contract.symbol}")
            else:
                print(f"No suitable ATM put found for {symbol}.")

        except Exception as e:
            print(f"Error processing {symbol}: {e}")

    return contracts_bought


def get_last_trade_price(symbol):
    quote = api.get_last_trade(symbol)
    return float(quote.price)

def get_nearest_expiration_date():
    today = datetime.today().date()
    weekday = today.weekday()
    days_until_friday = (4 - weekday) % 7
    expiration = today + timedelta(days=days_until_friday)
    return expiration.strftime("%Y-%m-%d")
