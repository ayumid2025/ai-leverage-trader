import pandas as pd
import matplotlib.pyplot as plt
import yaml
import os
import sys
sys.path.append('src')  # ensure we can import our modules

from data_fetcher import fetch_multiple
from account import MarginAccount
from strategy import moving_average_crossover

def run_backtest(config_file='config/config.yaml'):
    # Load configuration
    with open(config_file, 'r') as f:
        config = yaml.safe_load(f)

    symbols = config['symbols']
    initial_cash = config['initial_cash']
    leverage = config['leverage']
    maintenance_margin = config.get('maintenance_margin', 0.25)
    period = config.get('period', '1y')  # we can add this to config

    # Fetch data for all symbols
    print(f"Fetching data for {symbols} (period={period})...")
    data_dict = fetch_multiple(symbols, period=period)

    # We'll align all data to the same dates (trading days). Find common dates.
    # For simplicity, we'll just use the dates of the first symbol, assuming all have same days.
    first_symbol = symbols[0]
    all_dates = data_dict[first_symbol].index
    min_days = len(all_dates)

    # Initialize account
    account = MarginAccount(initial_cash, leverage, maintenance_margin)

    # We'll keep a list of portfolio values over time
    portfolio_values = []
    dates_list = []

    # We need at least long_window days to compute signals (e.g., 50 days)
    min_required_days = 50  # from strategy's long_window
    start_day = min_required_days

    for day in range(start_day, min_days):
        current_date = all_dates[day]
        dates_list.append(current_date)

        # Build a dictionary of current prices for all symbols
        current_prices = {}
        for sym in symbols:
            df = data_dict[sym]
            if day < len(df):
                current_prices[sym] = df['Close'].iloc[day]

        # For each symbol, decide action based on data up to today
        for sym in symbols:
            df = data_dict[sym]
            if day >= len(df):
                continue  # not enough data for this symbol
            # Get data up to current day
            hist_data = df.iloc[:day+1]
            signal = moving_average_crossover(hist_data)

            current_price = current_prices[sym]

            if signal == 1:  # buy signal
                # We want to buy as many shares as we can given our risk rules
                # We'll use a simple approach: invest all cash (but limit by buying power)
                # In real strategy, you'd use position sizing. We'll keep it simple for now.
                # Let's calculate how many shares we can buy with all cash (but not exceeding buying power)
                # Actually, we should use risk-based sizing from earlier. For simplicity, we'll buy with 10% of equity.
                # But let's not overcomplicate. We'll use a fixed fraction for now.
                equity = account.total_equity(current_prices)
                # Use, say, 20% of equity for this trade
                invest_amount = equity * 0.2
                shares_to_buy = int(invest_amount // current_price)
                if shares_to_buy > 0:
                    account.buy(sym, current_price, shares_to_buy)

            elif signal == -1:  # sell signal
                # Sell all shares of this symbol if we own any
                if sym in account.positions:
                    account.sell(sym, current_price)  # sells all

        # After processing all stocks, check for margin call
        if account.check_margin_call(current_prices):
            # Margin call: liquidate all positions (sell everything)
            print(f"Margin call on {current_date.date()} – liquidating all positions.")
            for sym in list(account.positions.keys()):  # iterate over a copy
                account.sell(sym, current_prices[sym])

        # Record total portfolio value
        total_value = account.total_equity(current_prices)
        portfolio_values.append(total_value)

    # Backtest completed – print summary
    final_value = portfolio_values[-1] if portfolio_values else initial_cash
    print("\n" + "="*50)
    print("BACKTEST COMPLETE")
    print("="*50)
    print(f"Period: {all_dates[start_day].date()} to {all_dates[-1].date()}")
    print(f"Initial cash: ${initial_cash:.2f}")
    print(f"Final equity: ${final_value:.2f}")
    print(f"Total return: {((final_value - initial_cash)/initial_cash)*100:.2f}%")
    print(f"Number of trades: {len(account.trade_log) if hasattr(account, 'trade_log') else 'N/A'}")

    # Plot the portfolio value over time
    plt.figure(figsize=(12,6))
    plt.plot(dates_list, portfolio_values, label='AI Trader (10$, 100x)', color='blue')
    plt.title('AI Leverage Trader Backtest')
    plt.xlabel('Date')
    plt.ylabel('Portfolio Value ($)')
    plt.grid(True)

    # Compare to buy-and-hold of S&P 500
    try:
        spy_data = fetch_multiple(['SPY'], period=period)['SPY']
        # Align dates
        spy_dates = spy_data.index
        spy_values = spy_data['Close']
        # Normalize to start at initial cash
        start_idx = spy_dates.get_indexer([dates_list[0]], method='nearest')[0]
        spy_start = spy_values.iloc[start_idx]
        spy_plot = spy_values / spy_start * initial_cash
        # Slice to same date range
        spy_plot = spy_plot.loc[dates_list[0]:dates_list[-1]]
        plt.plot(spy_plot.index, spy_plot.values, label='S&P 500 (SPY) Buy & Hold', color='orange', alpha=0.7)
    except Exception as e:
        print("Could not plot SPY comparison:", e)

    plt.legend()
    plt.show()

if __name__ == "__main__":
    run_backtest()
