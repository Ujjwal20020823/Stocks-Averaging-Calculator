import pytest
from unittest.mock import MagicMock, Mock
from src.analyzer import PortfolioAnalyzer
from src.models import Portfolio, Transaction
from datetime import datetime, timedelta

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

    # New tests for historical opportunity cost functionality
    @pytest.fixture
    def real_portfolio(self):
        """Creates a real Portfolio with actual Transaction objects for comprehensive testing."""
        portfolio = Portfolio(security_name="TEST_STOCK", current_market_price=750.0)
        
        # Transaction 1: 100 days ago, Rs. 1000/share, 100 shares
        date1 = datetime.now() - timedelta(days=100)
        tx1 = Transaction(1, date1.strftime("%Y-%m-%d"), 1000.0, 100)
        portfolio.add_transaction(tx1)
        
        # Transaction 2: 50 days ago, Rs. 900/share, 350 shares
        date2 = datetime.now() - timedelta(days=50)
        tx2 = Transaction(2, date2.strftime("%Y-%m-%d"), 900.0, 350)
        portfolio.add_transaction(tx2)
        
        return portfolio

    def test_historical_opportunity_cost_structure(self, real_portfolio):
        """Verify get_historical_opportunity_cost returns complete dictionary with all required keys."""
        analyzer = PortfolioAnalyzer(real_portfolio)
        
        result = analyzer.get_historical_opportunity_cost(annual_fd_rate=5.0)

        assert 'total_capital_invested' in result
        assert 'total_shares' in result
        assert 'total_fd_benchmark' in result
        assert 'current_market_value' in result
        assert 'historical_opportunity_gap' in result
        assert 'simple_bep' in result
        assert 'economic_bep' in result
        assert 'opportunity_spread' in result
        assert 'annual_fd_rate' in result
        assert 'detailed_transactions' in result

    def test_historical_opportunity_cost_values(self, real_portfolio):
        """Verify historical opportunity cost calculations are mathematically correct."""
        analyzer = PortfolioAnalyzer(real_portfolio)
        
        result = analyzer.get_historical_opportunity_cost(annual_fd_rate=5.0)

        # Total shares should be 100 + 350 = 450
        assert result['total_shares'] == 450
        
        # Total capital invested should be (1000*100) + (900*350) = 100000 + 315000 = 415000
        assert result['total_capital_invested'] == 415000.0
        
        # Simple BEP should be 415000 / 450 ≈ 922.22
        assert pytest.approx(result['simple_bep'], abs=0.1) == 922.22
        
        # FD benchmark should be greater than capital invested (compounding effect)
        assert result['total_fd_benchmark'] > result['total_capital_invested']
        
        # Economic BEP should be greater than Simple BEP
        assert result['economic_bep'] > result['simple_bep']
        
        # Current market value should be 450 * 750 = 337500
        assert result['current_market_value'] == 337500.0
        
        # Historical opportunity gap should be FD benchmark - current value (should be positive if market is down)
        assert result['historical_opportunity_gap'] == (result['total_fd_benchmark'] - result['current_market_value'])

    def test_historical_opportunity_cost_detail_transactions(self, real_portfolio):
        """Verify detailed transaction breakdowns are accurate."""
        analyzer = PortfolioAnalyzer(real_portfolio)
        
        result = analyzer.get_historical_opportunity_cost(annual_fd_rate=5.0)
        
        detailed = result['detailed_transactions']
        
        # Should have 2 transactions
        assert len(detailed) == 2
        
        # Each transaction should have required keys
        for tx in detailed:
            assert 'transaction_id' in tx
            assert 'date' in tx
            assert 'holding_days' in tx
            assert 'holding_years' in tx
            assert 'capital_invested' in tx
            assert 'fd_value_today' in tx
            assert 'opportunity_cost' in tx
        
        # FD value should be greater than capital invested (compounding)
        for tx in detailed:
            assert tx['fd_value_today'] > tx['capital_invested']
            assert tx['opportunity_cost'] > 0

    def test_historical_opportunity_cost_with_different_rates(self, real_portfolio):
        """Verify that higher FD rates produce higher opportunity costs."""
        analyzer = PortfolioAnalyzer(real_portfolio)
        
        result_3pct = analyzer.get_historical_opportunity_cost(annual_fd_rate=3.0)
        result_5pct = analyzer.get_historical_opportunity_cost(annual_fd_rate=5.0)
        result_8pct = analyzer.get_historical_opportunity_cost(annual_fd_rate=8.0)
        
        # FD benchmarks should increase with rate
        assert result_3pct['total_fd_benchmark'] < result_5pct['total_fd_benchmark']
        assert result_5pct['total_fd_benchmark'] < result_8pct['total_fd_benchmark']
        
        # Economic BEP should also increase
        assert result_3pct['economic_bep'] < result_5pct['economic_bep']
        assert result_5pct['economic_bep'] < result_8pct['economic_bep']

    def test_historical_opportunity_cost_percentage_rate(self, real_portfolio):
        """Verify FD rate can be passed as decimal (0.05) or percentage (5.0)."""
        analyzer = PortfolioAnalyzer(real_portfolio)
        
        result_decimal = analyzer.get_historical_opportunity_cost(annual_fd_rate=0.05)
        result_percentage = analyzer.get_historical_opportunity_cost(annual_fd_rate=5.0)
        
        # Both should produce identical results
        assert pytest.approx(result_decimal['economic_bep'], abs=0.01) == result_percentage['economic_bep']
        assert pytest.approx(result_decimal['total_fd_benchmark'], abs=0.01) == result_percentage['total_fd_benchmark']

    def test_economic_bep_with_zero_shares(self):
        """Test edge case: portfolio with zero shares."""
        portfolio = Portfolio(security_name="EMPTY", current_market_price=750.0)
        portfolio.transactions = []
        
        analyzer = PortfolioAnalyzer(portfolio)
        result = analyzer.get_historical_opportunity_cost(annual_fd_rate=5.0)
        
        assert result['total_shares'] == 0
        assert result['economic_bep'] == 0.0
        assert result['opportunity_spread'] == 0.0

    def test_recovery_scenarios_includes_economic_bep(self, real_portfolio):
        """Verify recovery scenarios include Economic BEP milestone."""
        analyzer = PortfolioAnalyzer(real_portfolio)
        
        scenarios = analyzer.get_recovery_scenarios(annual_fd_rate=5.0)
        
        # Should have 5 milestones including Economic BEP
        assert len(scenarios) == 5
        
        # Check for Economic BEP milestone
        economic_bep_found = False
        for label in scenarios.keys():
            if 'Economic Break-Even' in label or 'FD Recovery' in label:
                economic_bep_found = True
                break
        
        assert economic_bep_found, "Economic Break-Even milestone not found in recovery scenarios"
        
        # Verify each scenario has required keys
        for label, data in scenarios.items():
            assert 'target_price' in data
            assert 'projected_position_value' in data
            assert 'net_result_rupees' in data

    # Tests for calculate_historical_fd_benchmark() - New Refactored Method
    def test_calculate_historical_fd_benchmark_structure(self, real_portfolio):
        """Verify calculate_historical_fd_benchmark returns all required keys."""
        analyzer = PortfolioAnalyzer(real_portfolio)
        
        result = analyzer.calculate_historical_fd_benchmark(annual_fd_rate=5.0)

        required_keys = [
            'total_cash_invested',
            'total_shares',
            'current_price',
            'current_portfolio_value',
            'total_fd_benchmark',
            'opportunity_cost_gap',
            'simple_bep',
            'economic_bep',
            'opportunity_spread',
            'annual_fd_rate',
            'gain_from_current_to_economic_bep_pct'
        ]
        
        for key in required_keys:
            assert key in result, f"Missing key: {key}"

    def test_calculate_historical_fd_benchmark_values(self, real_portfolio):
        """Verify historical FD benchmark calculations are correct."""
        analyzer = PortfolioAnalyzer(real_portfolio)
        
        result = analyzer.calculate_historical_fd_benchmark(annual_fd_rate=5.0)

        # Verify basic constraints
        assert result['total_shares'] == 450
        assert result['total_cash_invested'] == 415000.0
        assert result['current_portfolio_value'] == 337500.0  # 450 shares * 750
        
        # FD benchmark should be greater than capital invested
        assert result['total_fd_benchmark'] > result['total_cash_invested']
        
        # Opportunity gap should be positive (FD Benchmark - Current Value)
        assert result['opportunity_cost_gap'] > 0
        
        # Economic BEP should be greater than Simple BEP
        assert result['economic_bep'] > result['simple_bep']
        
        # Simple BEP should match weighted average cost
        assert pytest.approx(result['simple_bep'], abs=0.01) == 922.22

    def test_calculate_historical_fd_benchmark_gain_percentage(self, real_portfolio):
        """Verify gain percentage calculation is correct."""
        analyzer = PortfolioAnalyzer(real_portfolio)
        
        result = analyzer.calculate_historical_fd_benchmark(annual_fd_rate=5.0)
        
        # Manual calculation: (economic_bep - current_price) / current_price * 100
        expected_gain_pct = ((result['economic_bep'] - result['current_price']) / result['current_price']) * 100
        
        assert pytest.approx(result['gain_from_current_to_economic_bep_pct'], abs=0.01) == expected_gain_pct

    def test_calculate_historical_fd_benchmark_with_zero_portfolio(self):
        """Test edge case: empty portfolio."""
        portfolio = Portfolio(security_name="EMPTY", current_market_price=750.0)
        portfolio.transactions = []
        
        analyzer = PortfolioAnalyzer(portfolio)
        result = analyzer.calculate_historical_fd_benchmark(annual_fd_rate=5.0)
        
        assert result['total_shares'] == 0
        assert result['total_cash_invested'] == 0.0
        assert result['current_portfolio_value'] == 0.0
        assert result['total_fd_benchmark'] == 0.0
        assert result['economic_bep'] == 0.0
        assert result['simple_bep'] == 0.0
        assert result['opportunity_spread'] == 0.0
        assert result['opportunity_cost_gap'] == 0.0

    def test_calculate_historical_fd_benchmark_comparison_with_old_method(self, real_portfolio):
        """Verify new method produces consistent results with old method."""
        analyzer = PortfolioAnalyzer(real_portfolio)
        
        new_result = analyzer.calculate_historical_fd_benchmark(annual_fd_rate=5.0)
        old_result = analyzer.get_historical_opportunity_cost(annual_fd_rate=5.0)
        
        # Key metrics should match
        assert new_result['total_cash_invested'] == old_result['total_capital_invested']
        assert new_result['total_shares'] == old_result['total_shares']
        assert pytest.approx(new_result['total_fd_benchmark'], abs=0.1) == old_result['total_fd_benchmark']
        assert pytest.approx(new_result['current_portfolio_value'], abs=0.1) == old_result['current_market_value']
        assert pytest.approx(new_result['simple_bep'], abs=0.01) == old_result['simple_bep']
        assert pytest.approx(new_result['economic_bep'], abs=0.01) == old_result['economic_bep']
        assert pytest.approx(new_result['opportunity_spread'], abs=0.01) == old_result['opportunity_spread']
