import yfinance as yf
import pandas as pd
import os
from datetime import datetime

DATA_DIR = "data"

def ensure_data_dir():
    """Create data directory if it doesn't exist."""
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)

def get_cache_filename(symbol, period):
    """Generate a filename for cached data."""
    # Sanitize symbol (just in case, though yfinance symbols are usually safe)
    safe_symbol = symbol.replace('^', '_')  # handle indexes like ^GSPC
    return os.path.join(DATA_DIR, f"{safe_symbol}_{period}.csv")

def fetch_data(symbol, period="1y", force_download=False):
    """
    Fetch historical data for a symbol.
    If cached data exists and is recent (downloaded today), load it.
    Otherwise, download from Yahoo Finance and cache.
    """
    ensure_data_dir()
    cache_file = get_cache_filename(symbol, period)

    # If we don't want to force download and cache exists, load it
    if not force_download and os.path.exists(cache_file):
        # Optionally, check if file is from today? For simplicity, we'll just load it.
        print(f"Loading cached data for {symbol} from {cache_file}")
        df = pd.read_csv(cache_file, index_col=0, parse_dates=True)
        return df

    # Download fresh data
    print(f"Downloading data for {symbol} (period={period})...")
    ticker = yf.Ticker(symbol)
    df = ticker.history(period=period)

    if df.empty:
        print(f"Warning: No data returned for {symbol}")
        return df

    # Save to cache
    df.to_csv(cache_file)
    print(f"Saved to {cache_file}")
    return df

def fetch_multiple(symbols, period="1y", force_download=False):
    """
    Fetch data for multiple symbols. Returns a dict {symbol: DataFrame}.
    """
    data = {}
    for sym in symbols:
        data[sym] = fetch_data(sym, period, force_download)
    return data

if __name__ == "__main__":
    # Simple test
    test_symbols = ["AAPL", "MSFT", "TSLA"]
    data = fetch_multiple(test_symbols, period="3mo")
    for sym, df in data.items():
        print(f"\n{sym} – {len(df)} rows")
        print(df.head())
