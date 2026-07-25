import pytest
from src.models import Portfolio, Transaction

class TestPortfolioModel:
    """Unit tests for Portfolio domain model (adapted to current model API)."""

    def test_portfolio_shares_and_cost_basis(self):
        """Verify total shares owned and weighted average cost calculations."""
        # Portfolio constructor expects (security_name, current_market_price)
        portfolio = Portfolio(security_name="NEPSE_STOCK", current_market_price=750.0)

        # Add two purchase transactions using the Transaction(transaction_id, date_str, price_per_share, share_bought) signature
        portfolio.add_transaction(Transaction(1, "2025-01-01", 1000.0, 100))
        portfolio.add_transaction(Transaction(2, "2025-02-01", 921.43, 350))

        # Verify get_total_shares_owned()
        assert portfolio.get_total_shares_owned() == 450

        # Total invested amount
        assert pytest.approx(portfolio.get_total_invested_amount(), abs=0.1) == 422500.5

        # Weighted average cost = 422,500.5 / 450 = ~938.89
        assert pytest.approx(portfolio.get_average_weighted_cost(), abs=0.01) == 938.89

    def test_unrealized_loss_calculation(self):
        """Verify unrealized loss and recovery amount calculation."""
        portfolio = Portfolio(security_name="NEPSE_STOCK", current_market_price=750.0)
        portfolio.add_transaction(Transaction(1, "2025-01-01", 938.89, 450))

        # current_value - total_invested should be negative for a loss
        unrealized = portfolio.get_unrealized_gain_loss_rupees()
        assert unrealized < 0
        # The absolute recovery amount should match the magnitude of the loss
        recovery_needed = abs(unrealized)
        assert pytest.approx(recovery_needed, abs=1.0) == 85000.5

    def test_empty_portfolio_graceful_handling(self):
        """Verify zero values for empty portfolio without throwing division by zero."""
        portfolio = Portfolio(security_name="NEPSE_STOCK", current_market_price=500.0)

        assert portfolio.get_total_shares_owned() == 0
        assert portfolio.get_average_weighted_cost() == 0.0
        # No transactions -> unrealized gain/loss should be 0.0
        assert portfolio.get_unrealized_gain_loss_rupees() == 0.0
