from typing import Dict, Tuple
from src.models import Portfolio
from src.calculations import (
    calculate_averaging_down_scenario,
    calculate_opportunity_cost,
    calculate_tvm_adjusted_recovery,
    calculate_required_shares_for_new_avg
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
    
    def get_recovery_scenarios(self) -> Dict:
        """
        Generate multiple psychological recovery scenarios labeled by milestones.
        """
        current_price = self.portfolio.current_market_price
        avg_cost = self.portfolio.get_weighted_average_cost()
        shares = self.portfolio.get_total_shares_owned()
        
        # Define milestones creatively instead of plain numbers
        milestone_definitions = [
            ("5% Technical Bounce", current_price * 1.05),
            ("15% Market Rally", current_price * 1.15),
            ("90% Recovery Near-Miss", avg_cost * 0.90),
            ("TRUE BREAK-EVEN MILESTONE", avg_cost)
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