from datetime import datetime
from typing import List 

class Transaction:
    def __init__(self, transaction_id: int, date_str: str, price_per_share: float, share_bought: int):
        # 1. Validation
        if price_per_share <= 0:
            raise ValueError("Price per share must be greater than zero.")
        if share_bought <= 0:
            raise ValueError("Number of shares bought must be greater than zero.")
        
        # 2. Smart Parsing
        self.transaction_id = transaction_id
        self.date = datetime.strptime(date_str, "%Y-%m-%d")
        self.price_per_share = price_per_share
        self.share_bought = share_bought

    def get_total_invested_amount(self) -> float:
        return self.price_per_share * self.share_bought
    
    def get_holding_days(self) -> int:
        today = datetime.now()
        delta = today - self.date
        return delta.days
    
    def __repr__(self) -> str:
        formatted_date = self.date.strftime("%b %d, %Y")
        return (
            f"[TX #{self.transaction_id}] | Date: {formatted_date} | "
            f"Cost: Rs.{self.price_per_share:.2f} * {self.share_bought} shares | "
            f"Total Capital Locked: Rs.{self.get_total_invested_amount():.2f} ({self.get_holding_days()} days held)"
        )


class Portfolio:
    def __init__(self, security_name: str = None, current_market_price: float = 0.0, symbol: str = None):
        """Portfolio constructor.

        Backwards-compatible: older tests/code used keyword `symbol=`. Prefer `security_name` going
        forward. If both are provided, `security_name` takes precedence.
        """
        # Support legacy `symbol` keyword without changing external behavior.
        chosen_name = security_name if security_name is not None else symbol
        self.security_name = chosen_name
        self.current_market_price = current_market_price
        self.transactions: List[Transaction] = []

    def add_transaction(self, transaction: Transaction) -> None:
        self.transactions.append(transaction)
    
    def get_total_shares_owned(self) -> int:
        return sum(tx.share_bought for tx in self.transactions)
    
    def get_total_invested_amount(self) -> float:
        return sum(tx.get_total_invested_amount() for tx in self.transactions)
    
    def get_average_weighted_cost(self) -> float:
        total_invested = self.get_total_invested_amount()
        total_shares = self.get_total_shares_owned()
        if total_shares == 0:
            return 0.0
        return total_invested / total_shares
    
    def get_current_portfolio_value(self) -> float:
        return self.get_total_shares_owned() * self.current_market_price
    
    def get_portfolio_status(self) -> str:
        gain_loss = self.get_unrealized_gain_loss_rupees()
        if gain_loss > 0:
            return f"Unrealized profit: Rs.{gain_loss:.2f}"
        elif gain_loss < 0:
            return f"Unrealized loss: Rs.{abs(gain_loss):.2f}"
        else:
            return "BREAK-EVEN: No profit or loss."

    def get_floating_return_percentage(self) -> float:
        return self.get_unrealized_gain_loss_percentage()

    def get_weighted_average_cost(self) -> float:
        return self.get_average_weighted_cost()
    
    def get_weighted_holding_period_years(self) -> float:
        total_days_weighted = 0.0
        total_invested = self.get_total_invested_amount()
        
        if total_invested == 0:
            return 0.0
            
        for tx in self.transactions:
            days_held = tx.get_holding_days()  
            total_days_weighted += tx.get_total_invested_amount() * days_held
            
        # Calculate average days and convert to years
        average_days = total_days_weighted / total_invested
        return average_days / 365.0
    
    def get_unrealized_gain_loss_rupees(self) -> float:
        current_value = self.get_current_portfolio_value()
        total_invested = self.get_total_invested_amount()
        return current_value - total_invested
    
    def get_unrealized_gain_loss_percentage(self) -> float:
        total_invested = self.get_total_invested_amount()
        if total_invested == 0:
            return 0.0
        gain_loss = self.get_unrealized_gain_loss_rupees()
        return (gain_loss / total_invested) * 100
    
    def get_break_even_price(self) -> float:
        return self.get_average_weighted_cost()

    def get_portfolio_status(self) -> str:
        gain_loss = self.get_unrealized_gain_loss_rupees()
        if gain_loss > 0:
            return f"Unrealized profit: Rs.{gain_loss:.2f}"
        elif gain_loss < 0:
            return f"Unrealized loss: Rs.{abs(gain_loss):.2f}"
        else:
            return "BREAK-EVEN: No profit or loss."