import ccxt
import pandas as pd
import time

exchange = ccxt.bybit({
    'enableRateLimit': True,
    'timeout': 30000,
    'options': {
        'defaultType': 'spot'
    }
})

TIMEFRAME = '1h'
LIMIT = 100

def get_ema(series, period):
    return series.ewm(span=period, adjust=False).mean()

def get_all_bybit_spot_usdt_symbols():
    """
    SADECE SPOT + USDT
    Bu fonksiyon SADECE 1 KERE çağrılmalı
    """
    markets = exchange.fetch_markets()
    return [
        m['symbol']
        for m in markets
        if m.get('spot')
        and m.get('quote') == 'USDT'
        and m.get('active')
    ]

def check_ema_crossover(symbol):
    try:
        ohlcv = exchange.fetch_ohlcv(symbol, TIMEFRAME, limit=LIMIT)
        df = pd.DataFrame(
            ohlcv,
            columns=['time', 'open', 'high', 'low', 'close', 'volume']
        )

        df['ema9'] = get_ema(df['close'], 9)
        df['ema21'] = get_ema(df['close'], 21)

        return (
            df['ema9'].iloc[-2] < df['ema21'].iloc[-2] and
            df['ema9'].iloc[-1] > df['ema21'].iloc[-1]
        )

    except Exception:
        return False

def scan_bybit_spot_all():
    symbols = get_all_bybit_spot_usdt_symbols()
    results = []

    for symbol in symbols:
        if check_ema_crossover(symbol):
            results.append(symbol)

        time.sleep(0.35)  # SPOT için güvenli gecikme

    return results

if __name__ == "__main__":
    coins = scan_bybit_spot_all()

    print("Bybit SPOT (Tüm USDT) – EMA 9 / 21 yukarı kesişim:")
    for c in coins:
        print(c)
