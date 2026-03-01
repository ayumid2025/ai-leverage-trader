class MarginAccount:
    def __init__(self, initial_cash, leverage, maintenance_margin=0.25):
        """
        Simulates a margin trading account.
        :param initial_cash: starting cash (e.g., $10)
        :param leverage: maximum leverage allowed (e.g., 100)
        :param maintenance_margin: minimum equity/asset ratio before margin call (usually 0.25 for 25%)
        """
        self.cash = initial_cash
        self.leverage = leverage
        self.maintenance_margin = maintenance_margin
        self.positions = {}  # symbol -> {shares: int, entry_price: float}
        self.loan = 0.0      # total borrowed money

    def buy(self, symbol, price, shares):
        """
        Buy shares of a stock using available cash and borrowing if needed.
        Returns True if successful, False if insufficient buying power.
        """
        cost = shares * price
        # Total buying power = cash * leverage
        buying_power = self.cash * self.leverage
        # We also need to consider existing loan? For simplicity, buying power is based on equity.
        # More accurate: equity = cash + position_value - loan. Buying power = equity * leverage.
        # Let's compute equity first.
        equity = self._calculate_equity({symbol: price})  # pass current prices (only this symbol for now)
        buying_power = equity * self.leverage
        self.trade_log.append({
    'date': None,  # we'll fill later in backtester
    'symbol': symbol,
    'action': 'BUY',
    'shares': shares,
    'price': price,
    'cost': cost
})

        if cost > buying_power:
            print(f"Cannot buy {shares} shares of {symbol} for ${cost:.2f}. Buying power: ${buying_power:.2f}")
            return False

        # Use cash first, borrow the rest
        if cost <= self.cash:
            self.cash -= cost
        else:
            # Use all cash, borrow remainder
            needed_loan = cost - self.cash
            self.cash = 0
            self.loan += needed_loan

        # Add to positions
        if symbol in self.positions:
            # Average down (simplified: just add shares and new average price)
            old_shares = self.positions[symbol]['shares']
            old_price = self.positions[symbol]['entry_price']
            total_shares = old_shares + shares
            avg_price = (old_shares * old_price + shares * price) / total_shares
            self.positions[symbol] = {'shares': total_shares, 'entry_price': avg_price}
        else:
            self.positions[symbol] = {'shares': shares, 'entry_price': price}

        print(f"Bought {shares} shares of {symbol} at ${price:.2f}. Cost: ${cost:.2f}")
        return True

    def sell(self, symbol, price, shares=None):
        """
        Sell shares. If shares is None, sell all.
        Returns True if successful, False if symbol not held or insufficient shares.
        """
        if symbol not in self.positions:
            print(f"No position in {symbol}")
            return False
            self.trade_log.append({
    'date': None,  # we'll fill later in backtester
    'symbol': symbol,
    'action': 'BUY',
    'shares': shares,
    'price': price,
    'cost': cost
})

        pos = self.positions[symbol]
        if shares is None:
            shares = pos['shares']
        elif shares > pos['shares']:
            print(f"Not enough shares. You have {pos['shares']}, trying to sell {shares}")
            return False

        revenue = shares * price
        # Pay back loan first? Actually, when we sell, we get cash, which can reduce loan.
        # We'll treat loan as separate; cash increases, loan stays until we explicitly reduce it.
        # For simplicity, we'll just add revenue to cash.
        self.cash += revenue

        # Reduce or remove position
        if shares == pos['shares']:
            del self.positions[symbol]
        else:
            self.positions[symbol]['shares'] -= shares

        print(f"Sold {shares} shares of {symbol} at ${price:.2f}. Revenue: ${revenue:.2f}")
        return True

    def _calculate_equity(self, current_prices):
        """
        Calculate current equity (cash + position value - loan).
        current_prices: dict {symbol: current_price}
        """
        position_value = 0.0
        for sym, pos in self.positions.items():
            price = current_prices.get(sym, pos['entry_price'])  # fallback to entry price if not provided
            position_value += pos['shares'] * price
        equity = self.cash + position_value - self.loan
        return equity

    def check_margin_call(self, current_prices):
        """
        Check if equity falls below maintenance margin requirement.
        Returns True if margin call triggered, else False.
        """
        equity = self._calculate_equity(current_prices)
        position_value = sum(pos['shares'] * current_prices.get(sym, pos['entry_price']) 
                             for sym, pos in self.positions.items())
        if position_value == 0:
            return False
        margin_ratio = equity / position_value
        if margin_ratio < self.maintenance_margin:
            print(f"MARGIN CALL! Equity/Assets = {margin_ratio:.2%} < {self.maintenance_margin:.2%}")
            return True
        return False

    def get_account_summary(self, current_prices):
        """Return a string summary of the account."""
        equity = self._calculate_equity(current_prices)
        position_value = sum(pos['shares'] * current_prices.get(sym, pos['entry_price']) 
                             for sym, pos in self.positions.items())
        return (f"Cash: ${self.cash:.2f}, Loan: ${self.loan:.2f}, "
                f"Position Value: ${position_value:.2f}, Equity: ${equity:.2f}, "
                f"Leverage Used: {position_value/equity:.2f}x")

    def total_equity(self, current_prices):
        """Return current equity."""
        return self._calculate_equity(current_prices)
