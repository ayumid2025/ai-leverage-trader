import yfinance as yf

def fetch_data(symbol, period="1y"):
    ticker = yf.Ticker(symbol)
    data = ticker.history(period=period)
    return data
