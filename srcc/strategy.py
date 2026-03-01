import pandas as pd

def moving_average_crossover(data, short_window=20, long_window=50):
    """
    Simple moving average crossover strategy.
    Returns a signal: 1 = buy, -1 = sell, 0 = no action.
    """
    if len(data) < long_window:
        return 0  # not enough data

    # Calculate moving averages
    short_ma = data['Close'].rolling(window=short_window).mean()
    long_ma = data['Close'].rolling(window=long_window).mean()

    # Current values
    current_short = short_ma.iloc[-1]
    current_long = long_ma.iloc[-1]
    # Previous values to detect crossover
    prev_short = short_ma.iloc[-2] if len(short_ma) > 1 else current_short
    prev_long = long_ma.iloc[-2] if len(long_ma) > 1 else current_long

    # Detect crossover
    if prev_short <= prev_long and current_short > current_long:
        return 1   # buy signal
    elif prev_short >= prev_long and current_short < current_long:
        return -1  # sell signal
    else:
        return 0
