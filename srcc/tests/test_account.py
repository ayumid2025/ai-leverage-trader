import sys
sys.path.append('src')  # allow importing from src folder
from account import MarginAccount

def test_buy_sell():
    # Initialize account with $10, 100x leverage
    acc = MarginAccount(initial_cash=10.0, leverage=100, maintenance_margin=0.25)
    print("Initial:", acc.get_account_summary({'AAPL': 150}))

    # Buy AAPL at $150 – can we buy?
    # With $10 equity, buying power = $10 * 100 = $1000.
    # $150 share price -> max shares = floor(1000/150) = 6 shares (cost $900)
    acc.buy('AAPL', price=150, shares=6)
    print("After buying 6 AAPL:", acc.get_account_summary({'AAPL': 150}))

    # Now price drops to $140
    print("\nPrice drops to $140")
    print(acc.get_account_summary({'AAPL': 140}))
    if acc.check_margin_call({'AAPL': 140}):
        print("Margin call triggered! Would need to sell or add cash.")

    # Sell half (3 shares) at $140
    acc.sell('AAPL', price=140, shares=3)
    print("After selling 3 at $140:", acc.get_account_summary({'AAPL': 140}))

    # Price recovers to $155
    print("\nPrice recovers to $155")
    print(acc.get_account_summary({'AAPL': 155}))

    # Sell remaining 3 at $155
    acc.sell('AAPL', price=155)  # sell all
    print("After selling remaining at $155:", acc.get_account_summary({'AAPL': 155}))

if __name__ == "__main__":
    test_buy_sell()
