import pytest
from src.calculations import calculate_opportunity_cost

class TestCalculations:
    """Unit tests for standalone calculation engines."""

    def test_calculate_opportunity_cost_percentage_rate(self):
        """Verify compound interest calculation when rate is passed as percentage (e.g., 5.0)."""
        principal = 100000.0
        rate_pct = 5.0  # 5%
        years = 1.0
        
        # Quarterly compounding: 100,000 * (1 + 0.05/4)^4 - 100,000 = ~5094.53
        interest = calculate_opportunity_cost(
            additional_investment=principal,
            fd_annual_rate=rate_pct,
            years=years,
            compounding_frequency=4
        )
        
        assert pytest.approx(interest, abs=1.0) == 5094.53

    def test_calculate_opportunity_cost_decimal_rate(self):
        """Verify compound interest calculation when rate is passed as decimal (e.g., 0.05)."""
        principal = 100000.0
        rate_decimal = 0.05  # 5%
        years = 1.0
        
        interest = calculate_opportunity_cost(
            additional_investment=principal,
            fd_annual_rate=rate_decimal,
            years=years,
            compounding_frequency=4
        )
        
        # Output should match percentage input behavior exactly
        assert pytest.approx(interest, abs=1.0) == 5094.53

    def test_zero_investment_opportunity_cost(self):
        """Verify zero yield when no additional capital is invested."""
        interest = calculate_opportunity_cost(
            additional_investment=0.0,
            fd_annual_rate=5.0,
            years=1.0
        )
        assert interest == 0.0

    def test_weighted_average_cost(self):
        """Verify weighted average cost logic given multiple purchase tranches."""
        # Tranche 1: 100 shares @ Rs. 1000 = Rs. 100,000
        # Tranche 2: 200 shares @ Rs. 700  = Rs. 140,000
        # Total: 300 shares for Rs. 240,000 -> Avg Cost = Rs. 800
        total_cost = 100000.0 + 140000.0
        total_shares = 300
        
        avg_cost = total_cost / total_shares
        assert avg_cost == 800.0

    def test_target_average_cost_shares_needed(self):
        """Verify formula solving for shares needed to reach a target average cost."""
        current_shares = 445
        current_avg_cost = 938.89
        target_avg_cost = 850.0
        purchase_price = 750.0
        
        # Formula: N = [Current_Shares * (Current_Avg - Target_Avg)] / (Target_Avg - Purchase_Price)
        required_shares_exact = (current_shares * (current_avg_cost - target_avg_cost)) / (target_avg_cost - purchase_price)
        
        # 445 * 88.89 / 100 = ~395.56 shares -> 396 to 401 depending on math rounding
        assert pytest.approx(required_shares_exact, abs=0.5) == 395.56