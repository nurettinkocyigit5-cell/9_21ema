import ccxt
import pandas as pd
import time

# Bybit Futures bağlantısı
exchange = ccxt.bybit({
    'enableRateLimit': True,
    'timeout': 30000,
    'options': {
        'defaultType': 'linear'  # USDT Perpetual
    }
})

TIMEFRAME = '1h'
LIMIT = 100

def get_ema(series, period):
    return series.ewm(span=period, adjust=False).mean()

def get_bybit_usdt_futures_symbols():
    """
    SADECE USDT perpetual futures
    """
    markets = exchange.fetch_markets()
    return [
        m['symbol'] for m in markets
        if m.get('linear') and m.get('quote') == 'USDT'
    ]

def check_ema_crossover(symbol):
    try:
        ohlcv = exchange.fetch_ohlcv(symbol, timeframe=TIMEFRAME, limit=LIMIT)
        df = pd.DataFrame(
            ohlcv,
            columns=['time', 'open', 'high', 'low', 'close', 'volume']
        )

        df['ema9'] = get_ema(df['close'], 9)
        df['ema21'] = get_ema(df['close'], 21)

        prev = df.iloc[-2]
        last = df.iloc[-1]

        return prev['ema9'] < prev['ema21'] and last['ema9'] > last['ema21']

    except Exception:
        return False

def scan_bybit_futures():
    symbols = get_bybit_usdt_futures_symbols()
    crossed = []

    for symbol in symbols:
        if check_ema_crossover(symbol):
            crossed.append(symbol)

        time.sleep(0.15)  # Cloud rate-limit koruması

    return crossed

if __name__ == "__main__":
    results = scan_bybit_futures()

    print("Bybit EMA 9 / EMA 21 yukarı kesişim:")
    for coin in results:
        print(coin)
