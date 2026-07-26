from typing import Dict, Tuple
from datetime import datetime
from src.models import Portfolio
from src.calculations import (
    calculate_averaging_down_scenario,
    calculate_opportunity_cost,
    calculate_tvm_adjusted_recovery,
    calculate_required_shares_for_new_avg,
    calculate_economic_bep
)

class PortfolioAnalyzer:
    def __init__(self, portfolio: Portfolio):
        self.portfolio = portfolio

    def get_loss_recovery_amount(self) -> float:
        """
        Calculate the amount needed to recover from the current unrealized loss and reach to break-even.
        """
        loss = self.portfolio.get_unrealized_gain_loss_rupees()
        return abs(loss) if loss < 0 else 0.0

    def analyze_averaging_down(self, additional_investment: float) -> Dict:
        """Analyze what happens if you invest more at current market price, adding a Capital Efficiency Bank."""
        new_shares, new_avg_cost, new_unrealized_loss = calculate_averaging_down_scenario(
            self.portfolio,
            additional_investment,
            self.portfolio.current_market_price
        )

        current_avg = self.portfolio.get_average_weighted_cost()
        shares_added = new_shares - self.portfolio.get_total_shares_owned()
        avg_cost_reduction = current_avg - new_avg_cost
        loss_reduction = self.portfolio.get_unrealized_gain_loss_rupees() - new_unrealized_loss
        cost_drop_percentage = (avg_cost_reduction / current_avg) * 100 if current_avg > 0 else 0.0

        if cost_drop_percentage > 15.0:
            efficiency_rank = "High Efficiency (Substantial break-even reduction)"
        elif cost_drop_percentage >= 5.0:
            efficiency_rank = "Moderate Efficiency (Steady defensive improvement)"
        else:
            efficiency_rank = "Low Efficiency (Marginal drop. Consider holding cash or alternative strategies)"

        return {
            "new_shares": new_shares,
            "shares_added": shares_added,
            "new_avg_cost": new_avg_cost,
            "avg_cost_reduction": avg_cost_reduction,
            "avg_cost_reduction_pct": cost_drop_percentage,
            "efficiency_rank": efficiency_rank,
            "new_unrealized_loss": new_unrealized_loss,
            "loss_reduction": loss_reduction,
            "additional_investment": additional_investment
        }
    def compare_with_fd(self, fd_annual_rate: float, investment_years: float, additional_investment: float=0.0) -> Dict:
        """Compare averaging down vs investing in Fixed Deposit."""
        # If no additional cash is explicitly passes, use the loss recovery amount as fallback.
        if additional_investment > 0:
            capital_to_compare = additional_investment
        else:
            capital_to_compare = self.get_loss_recovery_amount()
        
        decimal_rate = fd_annual_rate if fd_annual_rate < 1.0 else fd_annual_rate / 100.0
        pct_rate = decimal_rate * 100.0
        
        fd_return = calculate_opportunity_cost(
            additional_investment=capital_to_compare,
            fd_annual_rate= fd_annual_rate, 
            years=investment_years
            )
        fd_final_value = capital_to_compare + fd_return
        display_rate= fd_annual_rate * 100.0 if fd_annual_rate < 1.0 else fd_annual_rate
        
        return {
            'recovery_needed' : capital_to_compare,
            'additional_investment': capital_to_compare,
            'fd_annual_rate':display_rate,
            'investment_years': investment_years,
            'fd_return': fd_return,
            'fd_final_value': fd_final_value
        }
    
    def calculate_shares_for_target_avg(self, target_avg_cost: float, new_purchase_price: float) -> Dict:
        """
        Calculate how many shares you need to buy to reach target average cost,
        with an added reality-check guardrail.
        """
        current_avg = self.portfolio.get_weighted_average_cost()
        
        # Creative Guardrail Check
        if target_avg_cost >= current_avg:
            raise ValueError(f"Target average (Rs.{target_avg_cost}) must be lower than your current average (Rs.{current_avg:.2f}).")
        if target_avg_cost <= new_purchase_price:
            raise ValueError(f"Target average cannot be lower than or equal to the market floor price (Rs.{new_purchase_price}).")

        shares_needed, investment_needed = calculate_required_shares_for_new_avg(
            self.portfolio.get_total_shares_owned(),
            current_avg,
            target_avg_cost,
            new_purchase_price
        )
        
        return {
            'target_avg_cost': target_avg_cost,
            'new_purchase_price': new_purchase_price,
            'shares_to_buy': shares_needed,
            'investment_required': investment_needed,
            'current_avg_cost': current_avg
        }
    
    def get_recovery_scenarios(self, annual_fd_rate: float = 5.0) -> Dict:
        """
        Generate multiple psychological recovery scenarios labeled by milestones,
        including the Economic Break-Even Price.
         
        Args:
            annual_fd_rate: Annual FD rate for computing Economic BEP (default 5.0%)
        """
        current_price = self.portfolio.current_market_price
        avg_cost = self.portfolio.get_weighted_average_cost()
        shares = self.portfolio.get_total_shares_owned()
         
        # Get historical opportunity cost data to compute Economic BEP
        hist_opp = self.get_historical_opportunity_cost(annual_fd_rate)
        economic_bep = hist_opp['economic_bep']
         
        # Define milestones including Economic BEP
        milestone_definitions = [
            ("5% Technical Bounce", current_price * 1.05),
            ("15% Market Rally", current_price * 1.15),
            ("90% Recovery Near-Miss", avg_cost * 0.90),
            ("Simple Break-Even (Cost Basis)", avg_cost),
            ("Economic Break-Even (FD Recovery)", economic_bep)
        ]
         
        scenarios = {}
        for label, target_price in milestone_definitions:
            # Calculate what your paper profit/loss looks like if stock hits this price
            projected_gain_loss = (target_price - avg_cost) * shares
             
            scenarios[label] = {
                'target_price': target_price,
                'projected_position_value': target_price * shares,
                'net_result_rupees': projected_gain_loss
            }
         
        return scenarios

    def calculate_historical_fd_benchmark(self, annual_fd_rate: float) -> Dict:
        """
        Calculate historical FD benchmark and break-even analysis based on actual transaction dates.
        
        Focuses strictly on HISTORICAL sunk capital analysis:
        - What capital would be worth if placed in FD from purchase date to today
        - Compares vs current market value
        - Derives Economic BEP (true recovery price)
        
        Args:
            annual_fd_rate: Annual FD interest rate (supports both 5.0% and 0.05 formats)
        
        Returns:
            Dictionary with key metrics:
                - total_cash_invested: Sum of all C_i = P_i × S_i
                - current_portfolio_value: ∑(S_i × CurrentPrice)
                - total_fd_benchmark: ∑[C_i × (1 + r)^T_i]
                - opportunity_cost_gap: Total FD Benchmark - Current Portfolio Value
                - simple_bep: Cost basis breakeven = Total Capital / Total Shares
                - economic_bep: FD recovery price = Total FD Benchmark / Total Shares
                - opportunity_spread: Economic BEP - Simple BEP (per share)
                - gain_from_current_to_economic_bep_pct: % gain needed from current price
        """
        total_shares = self.portfolio.get_total_shares_owned()
        total_capital_invested = self.portfolio.get_total_invested_amount()
        current_portfolio_value = self.portfolio.get_current_portfolio_value()
        current_price = self.portfolio.current_market_price
        simple_bep = self.portfolio.get_weighted_average_cost()
        
        # Convert FD rate from percentage to decimal if needed
        fd_rate_decimal = annual_fd_rate if annual_fd_rate < 1.0 else annual_fd_rate / 100.0
        
        total_fd_benchmark = 0.0
        
        # Compute FD compounding for each transaction tranche
        for transaction in self.portfolio.transactions:
            capital_invested = transaction.get_total_invested_amount()
            holding_years = transaction.get_holding_days() / 365.0
            
            # FD Value = Capital × (1 + rate)^years
            fd_value = capital_invested * ((1 + fd_rate_decimal) ** holding_years)
            total_fd_benchmark += fd_value
        
        # Calculate derived metrics
        economic_bep = calculate_economic_bep(total_fd_benchmark, total_shares)
        opportunity_spread = economic_bep - simple_bep if total_shares > 0 else 0.0
        opportunity_gap = total_fd_benchmark - current_portfolio_value
        
        # Calculate % gain from current price to Economic BEP
        if current_price > 0:
            gain_pct_to_econ_bep = ((economic_bep - current_price) / current_price) * 100
        else:
            gain_pct_to_econ_bep = 0.0
        
        return {
            'total_cash_invested': total_capital_invested,
            'total_shares': total_shares,
            'current_price': current_price,
            'current_portfolio_value': current_portfolio_value,
            'total_fd_benchmark': total_fd_benchmark,
            'opportunity_cost_gap': opportunity_gap,
            'simple_bep': simple_bep,
            'economic_bep': economic_bep,
            'opportunity_spread': opportunity_spread,
            'annual_fd_rate': annual_fd_rate,
            'gain_from_current_to_economic_bep_pct': gain_pct_to_econ_bep
        }

    def get_historical_opportunity_cost(self, annual_fd_rate: float) -> Dict:
        """
        Calculate historical sunk opportunity cost for capital already tied up in past transactions.
        
        This method computes what the invested capital would be worth in a risk-free Fixed Deposit
        from the date of each transaction until today, then compares against current market value.
        
        Args:
            annual_fd_rate: Annual FD interest rate (as percentage, e.g., 5.0 for 5%)
        
        Returns:
            Dictionary with:
                - total_capital_invested: Sum of all purchase prices × shares
                - total_shares: Total shares owned
                - total_fd_benchmark: What the capital would be worth in FD today
                - current_market_value: Current portfolio value at market price
                - historical_opportunity_gap: FD benchmark - current market value
                - simple_bep: Weighted average cost (cost basis)
                - economic_bep: Price needed to recover all FD opportunity cost
                - opportunity_spread: Difference between economic and simple BEP
                - detailed_transactions: List of transaction-level breakdowns
        """
        total_shares = self.portfolio.get_total_shares_owned()
        total_capital_invested = self.portfolio.get_total_invested_amount()
        current_market_value = self.portfolio.get_current_portfolio_value()
        simple_bep = self.portfolio.get_weighted_average_cost()
        
        # Convert FD rate from percentage to decimal if needed
        fd_rate_decimal = annual_fd_rate if annual_fd_rate < 1.0 else annual_fd_rate / 100.0
        
        total_fd_benchmark = 0.0
        detailed_transactions = []
        
        # Compute FD compounding for each transaction
        for transaction in self.portfolio.transactions:
            capital_invested = transaction.get_total_invested_amount()
            holding_years = transaction.get_holding_days() / 365.0
            
            # FD Value = Capital × (1 + rate)^years
            fd_value = capital_invested * ((1 + fd_rate_decimal) ** holding_years)
            opportunity_lost = fd_value - capital_invested
            
            total_fd_benchmark += fd_value
            
            detailed_transactions.append({
                'transaction_id': transaction.transaction_id,
                'date': transaction.date.strftime("%Y-%m-%d"),
                'holding_days': transaction.get_holding_days(),
                'holding_years': round(holding_years, 4),
                'capital_invested': capital_invested,
                'fd_value_today': fd_value,
                'opportunity_cost': opportunity_lost
            })
        
        # Calculate economic BEP and opportunity spread
        economic_bep = calculate_economic_bep(total_fd_benchmark, total_shares)
        opportunity_spread = economic_bep - simple_bep if total_shares > 0 else 0.0
        historical_opportunity_gap = total_fd_benchmark - current_market_value
        
        return {
            'total_capital_invested': total_capital_invested,
            'total_shares': total_shares,
            'total_fd_benchmark': total_fd_benchmark,
            'current_market_value': current_market_value,
            'historical_opportunity_gap': historical_opportunity_gap,
            'simple_bep': simple_bep,
            'economic_bep': economic_bep,
            'opportunity_spread': opportunity_spread,
            'annual_fd_rate': annual_fd_rate,
            'detailed_transactions': detailed_transactions
        }