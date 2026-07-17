import unittest

from src.analyzer import PortfolioAnalyzer
from src.calculations import calculate_opportunity_cost
from src.models import Portfolio, Transaction


class TestCalculations(unittest.TestCase):
    def test_calculate_opportunity_cost_uses_decimal_rate(self):
        interest = calculate_opportunity_cost(
            additional_investment=1000.0,
            fd_annual_rate=0.05,
            years=1.0,
            compounding_frequency=4
        )

        self.assertAlmostEqual(interest, 1000.0 * ((1 + (0.05 / 4)) ** 4 - 1), places=8)

    def test_compare_with_fd_normalizes_rate_input(self):
        portfolio = Portfolio("DEMO", current_market_price=90.0)
        portfolio.add_transaction(Transaction(1, "2024-01-01", 100.0, 10))

        analyzer = PortfolioAnalyzer(portfolio)
        result_decimal = analyzer.compare_with_fd(fd_annual_rate=0.05, investment_years=1.0, additional_investment=1000.0)
        result_percentage = analyzer.compare_with_fd(fd_annual_rate=5.0, investment_years=1.0, additional_investment=1000.0)

        self.assertAlmostEqual(result_decimal['fd_return'], result_percentage['fd_return'], places=8)
        self.assertEqual(result_decimal['fd_annual_rate'], result_percentage['fd_annual_rate'])
        self.assertAlmostEqual(result_decimal['fd_return'], 1000.0 * ((1 + (0.05 / 4)) ** 4 - 1), places=8)


if __name__ == '__main__':
    unittest.main()
