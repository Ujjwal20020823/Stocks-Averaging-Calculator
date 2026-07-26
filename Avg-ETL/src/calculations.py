from typing import List, Tuple
from src.models import Transaction, Portfolio

def calculate_weighted_average(transactions: List[Transaction]) -> float:
    """Calculates the true blended cost floor of multiple transactions."""
    if not transactions:
        return 0.0
    
    # Updated 'share_bought' and 'get_total_invested_amount' to match your models.py
    total_invested = sum(t.get_total_invested_amount() for t in transactions)
    total_shares = sum(t.share_bought for t in transactions)
    
    if total_shares == 0:
        return 0.0
    
    return total_invested / total_shares


def calculate_break_even(weighted_avg_cost: float) -> float:
    return weighted_avg_cost


def calculate_current_value(current_price: float, total_shares: int) -> float:
    return current_price * total_shares


def calculate_unrealized_gain_loss(current_value: float, total_invested: float) -> float:
    return current_value - total_invested


def calculate_return_percentage(unrealized_gain_loss: float, total_invested: float) -> float:
    if total_invested == 0:
        return 0.0
    return (unrealized_gain_loss / total_invested) * 100


def calculate_required_shares_for_new_avg(
    current_total_shares: int,
    current_avg_cost: float,
    target_avg_cost: float,
    new_purchase_price: float
) -> Tuple[int, float]:
    """
    Solves the core averaging algebra. Forces proper rounding thresholds.
    """
    if new_purchase_price >= current_avg_cost:
        return 0, 0.0
    
    numerator = current_total_shares * (current_avg_cost - target_avg_cost)
    denominator = target_avg_cost - new_purchase_price
    
    # Catch impossible targets immediately
    if denominator <= 0 or numerator < 0:
        return 0, 0.0
    
    # Use ceiling calculation (add 1) so user buys enough to clear the target line
    shares_to_buy = int(numerator // denominator) + 1
    investment_needed = shares_to_buy * new_purchase_price
    
    return shares_to_buy, investment_needed


def calculate_tvm_adjusted_recovery(
    unrealized_loss: float,
    years_to_recovery: float,
    discount_rate: float
) -> float:
    """
    Calculates the real 'Economic Loss' via inflation/discount factoring.
    """
    if years_to_recovery == 0:
        return abs(unrealized_loss)
    
    rate_decimal = discount_rate / 100
    # Abs ensures loss values remain represented as absolute target values
    return abs(unrealized_loss) / ((1 + rate_decimal) ** years_to_recovery)


def calculate_opportunity_cost(
    additional_investment: float,
    fd_annual_rate: float,
    years: float,
    compounding_frequency: int = 4
) -> float:
    """
    Calcuate compound interest yield. 
    Handles rate wether passed as decimal (0.05) or percentage (5.0)
    """
    r = fd_annual_rate if fd_annual_rate < 1.0 else fd_annual_rate / 100
    n = compounding_frequency
    t = years
    
    future_value = additional_investment * ((1 + (r / n)) ** (n * t))
    return future_value - additional_investment


def calculate_averaging_down_scenario(
    portfolio: Portfolio,
    additional_investment: float,
    new_share_price: float
) -> Tuple[int, float, float]:
    """
    Calculates whole shares purchasable and maps out the post-averaging matrix.
    """
    if new_share_price <= 0:
        return portfolio.get_total_shares_owned(), portfolio.get_average_weighted_cost(), portfolio.get_unrealized_gain_loss_rupees()

    # Calculate exact whole shares affordable
    shares_to_buy = int(additional_investment // new_share_price)
    actual_capital_deployed = shares_to_buy * new_share_price
    
    # Linked directly to your correct models.py method names
    new_total_shares = portfolio.get_total_shares_owned() + shares_to_buy
    new_total_invested = portfolio.get_total_invested_amount() + actual_capital_deployed
    
    new_avg_cost = new_total_invested / new_total_shares if new_total_shares > 0 else 0.0
    
    # Calculate performance delta
    new_current_value = portfolio.current_market_price * new_total_shares
    new_unrealized_loss = new_current_value - new_total_invested
    
    return new_total_shares, new_avg_cost, new_unrealized_loss


def calculate_economic_bep(
    total_fd_benchmark: float,
    total_shares: int
) -> float:
    """
    Calculate Economic Break-Even Price (FD recovery price).
    Economic BEP represents the price needed to recover all lost opportunity costs.
    
    Args:
        total_fd_benchmark: Total compounded FD value across all transactions
        total_shares: Total shares owned across all transactions
    
    Returns:
        Economic BEP price per share (Rs.)
    """
    if total_shares == 0:
        return 0.0
    return total_fd_benchmark / total_shares