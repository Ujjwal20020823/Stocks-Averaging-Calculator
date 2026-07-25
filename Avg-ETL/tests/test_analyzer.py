import pytest
from unittest.mock import MagicMock
from src.analyzer import PortfolioAnalyzer

class TestPortfolioAnalyzer:
    """Unit tests for PortfolioAnalyzer engine methods."""

    @pytest.fixture
    def mock_portfolio(self):
        """Creates a mock Portfolio object with standard test values."""
        portfolio = MagicMock()
        portfolio.get_total_shares_owned.return_value = 450
        # Analyzer calls both get_average_weighted_cost() and get_weighted_average_cost()
        portfolio.get_average_weighted_cost.return_value = 938.89
        portfolio.get_weighted_average_cost.return_value = 938.89
        portfolio.current_market_price = 750.0
        portfolio.get_total_invested_amount.return_value = 422500.50
        # Backwards-compat: some tests/calls use get_total_investment
        portfolio.get_total_investment.return_value = 422500.50

        # Unrealized gain/loss should be negative for a paper loss (current - invested)
        portfolio.get_unrealized_gain_loss_rupees.return_value = -85000.00
        # Backwards-compat: older callers may use get_unrealized_loss()
        portfolio.get_unrealized_loss.return_value = -85000.00

        # Provide a mock for get_loss_recovery_amount in case other code calls it directly
        portfolio.get_loss_recovery_amount.return_value = 85000.00
        return portfolio

    def test_compare_with_fd_structure(self, mock_portfolio):
        """Verify compare_with_fd returns complete dictionary with correct FD math."""
        analyzer = PortfolioAnalyzer(mock_portfolio)
        
        result = analyzer.compare_with_fd(
            fd_annual_rate=5.0,
            investment_years=1.0,
            additional_investment=100000.0
        )

        assert 'recovery_needed' in result
        assert 'additional_investment' in result
        assert 'fd_annual_rate' in result
        assert 'investment_years' in result
        assert 'fd_return' in result
        assert 'fd_final_value' in result

        assert result['additional_investment'] == 100000.0
        assert result['fd_annual_rate'] == 5.0
        # Check compound yield is ~5094.53 (tolerance applied)
        assert pytest.approx(result['fd_return'], abs=5.0) == 5094.53
        assert pytest.approx(result['fd_final_value'], abs=5.0) == 105094.53

    def test_compare_with_fd_fallback_capital(self, mock_portfolio):
        """Verify fallback to loss recovery amount when additional_investment is 0."""
        analyzer = PortfolioAnalyzer(mock_portfolio)
        
        result = analyzer.compare_with_fd(
            fd_annual_rate=0.05,
            investment_years=1.0,
            additional_investment=0.0
        )

        # Should fall back to loss recovery amount (Rs. 85,000)
        assert result['additional_investment'] == 85000.00

    def test_calculate_shares_for_target_avg_integration(self, mock_portfolio):
        """Verify calculate_shares_for_target_avg correctly uses get_total_shares_owned()."""
        analyzer = PortfolioAnalyzer(mock_portfolio)

        target_avg = 850.0
        purchase_price = 750.0

        result = analyzer.calculate_shares_for_target_avg(
            target_avg_cost=target_avg,
            new_purchase_price=purchase_price
        )

        # Ensures portfolio.get_total_shares_owned() was called
        mock_portfolio.get_total_shares_owned.assert_called_once()

        assert 'shares_to_buy' in result
        assert 'investment_required' in result
        assert result['shares_to_buy'] >= 0
        assert result['investment_required'] == result['shares_to_buy'] * purchase_price

    def test_analyze_averaging_down(self, mock_portfolio):
        """Verify analyze_averaging_down scenario metrics."""
        analyzer = PortfolioAnalyzer(mock_portfolio)

        result = analyzer.analyze_averaging_down(additional_investment=100000.0)

        # Analyzer returns 'new_shares' (total after buying), 'new_avg_cost' and 'loss_reduction'
        assert 'new_avg_cost' in result
        assert 'new_shares' in result
        assert 'loss_reduction' in result
        # New average cost must be lower than original Rs. 938.89
        assert result['new_avg_cost'] < 938.89
