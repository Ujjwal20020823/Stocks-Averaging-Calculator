# src/recommender.py
from typing import Dict
from src.models import Portfolio
from src.analyzer import PortfolioAnalyzer


class RecommendationEngine:
    """
    Quantitative decision-making engine providing institutional-grade strategic guidance.
    Compares capital allocation alternatives to optimize recovery strategies.
    """
    
    def __init__(self, portfolio: Portfolio):
        """
        Initializes the engine with a target portfolio position.
        
        Args:
            portfolio (Portfolio): The underlying asset position layer.
        """
        self.portfolio = portfolio
        self.analyzer = PortfolioAnalyzer(portfolio)
    
    def get_position_recommendation(self) -> str:
        """
        Evaluates the current position posture and assigns a strategic directive.
        
        Returns:
            str: Professional advisory message.
        """
        status = self.portfolio.get_portfolio_status()
        gain_loss_pct = abs(self.portfolio.get_floating_return_percentage())
        
        if "profit" in status.lower():
            return (
                f"[STATUS: CAPITAL APPRECIATION] Your position is profitable by Rs.{self.portfolio.get_unrealized_gain_loss_rupees():.2f}. "
                f"Consider partial profit-taking or maintain allocation based on core macro outlook."
            )
        
        elif "break-even" in status.lower():
            return (
                "[STATUS: EQUILIBRIUM] Position is trading at historical cost parity. "
                "Monitor structural support levels closely and formalize defensive risk limits."
            )
        
        else:
            if gain_loss_pct > 50.0:
                return (
                    f"[ADVISORY: SEVERE CAPITAL IMPAIRMENT] Variance is negative {gain_loss_pct:.1f}%. "
                    f"Averaging down is explicitly discouraged. Re-evaluate structural fundamentals to ensure "
                    f"this asset is not experiencing temporary or permanent terminal decline."
                )
            elif gain_loss_pct > 30.0:
                return (
                    f"[ADVISORY: SIGNIFICANT DRAWDOWN] Variance is negative {gain_loss_pct:.1f}%. "
                    f"Capital deployment for averaging down is viable only if recovery probability remains high. "
                    f"Compare capital performance indicators against risk-free yield alternatives (Fixed Deposits)."
                )
            else:
                return (
                    f"[ADVISORY: STANDARD VARIANCE] DRAWDOWN is restricted to negative {gain_loss_pct:.1f}%. "
                    f"This position presents an optimal opportunity for defensive dollar-cost averaging. "
                    f"Verify required capital thresholds and target breakeven metrics prior to execution."
                )
    
    def should_average_down(
        self,
        additional_investment: float,
        fd_rate: float,
        years: float
    ) -> Dict:
        """
        Compares the capital efficiency of an averaging down strategy against a 
        guaranteed capital preservation fixed deposit index.
        
        Args:
            additional_investment (float): Total cash liquidity to deploy (Rs.).
            fd_rate (float): Fixed Deposit annual yield (e.g. 5.0 for 5%)
            years (float): Investment horizon timeline.
        
        Returns:
            Dict: Analytical comparison matrix.
        """
        avg_down_scenario = self.analyzer.analyze_averaging_down(additional_investment)
        fd_comparison = self.analyzer.compare_with_fd(
            fd_annual_rate = fd_rate,
            investment_years = years,
            additional_investment = additional_investment
        )
        
        current_avg_cost = self.portfolio.get_weighted_average_cost()
        current_price = self.portfolio.current_market_price
        
        new_avg_cost = avg_down_scenario['new_avg_cost']
        recovery_gap = new_avg_cost - current_price
        recovery_gap_pct = (recovery_gap / new_avg_cost) * 100 if new_avg_cost > 0 else 0.0
        
        fd_return = fd_comparison['fd_return']
        loss_reduction_from_avg_down = abs(avg_down_scenario['loss_reduction'])
        fd_advantage = fd_return - loss_reduction_from_avg_down
        
        recommendation = self._make_decision(
            recovery_gap_pct,
            fd_advantage,
            fd_return,
            avg_down_scenario,
            current_price
        )
        
        return {
            'recommendation': recommendation,
            'current_avg_cost': current_avg_cost,
            'new_avg_cost_after_averaging': new_avg_cost,
            'recovery_gap_pct': recovery_gap_pct,
            'fd_return': fd_return,
            'fd_advantage': fd_advantage,
            'loss_reduction': loss_reduction_from_avg_down,
            'investment_required': additional_investment,
            'fd_comparison' : fd_comparison,
            'avg_down_scenario' : avg_down_scenario
        }
    
    def _make_decision(
        self,
        recovery_gap_pct: float,
        fd_advantage: float,
        fd_return: float,
        avg_down_scenario: Dict,
        current_price: float
    ) -> str:
        """
        Algorithmic decision tree parsing capital allocations metrics.
        """
        if fd_advantage > abs(avg_down_scenario['loss_reduction']) * 0.5:
            return (
                f"[ALLOCATION DIRECTIVE: ALLOCATE TO GUARANTEED YIELD]\n"
                f"  Fixed Deposit Return: Rs.{fd_return:.2f}\n"
                f"  Averaging Down Net Recovery Value: Rs.{abs(avg_down_scenario['loss_reduction']):.2f}\n"
                f"  Note: Risk-adjusted metrics favor capital allocation to capital-preserved treasury instruments."
            )
        
        if recovery_gap_pct > 15.0:
            return (
                f"[ALLOCATION DIRECTIVE: EXECUTE COST AVERAGING]\n"
                f"  Projected Cost Foundation Basis: Rs.{avg_down_scenario['new_avg_cost']:.2f}\n"
                f"  Required Market Delta to Breakeven: {recovery_gap_pct:.1f}%\n"
                f"  Note: High capital deployment efficiency. The market recovery path is highly achievable."
            )
        
        if 5.0 < recovery_gap_pct <= 15.0:
            return (
                f"[ALLOCATION DIRECTIVE: CONDITIONAL HOLD / CAUTIOUS ACCUMULATION]\n"
                f"  Projected Cost Foundation Basis: Rs.{avg_down_scenario['new_avg_cost']:.2f}\n"
                f"  Required Market Delta to Breakeven: {recovery_gap_pct:.1f}%\n"
                f"  Note: Deploy liquidity in tranches. Ensure institutional thesis remains structurally intact."
            )
        else:
            return (
                f"[ALLOCATION DIRECTIVE: MAINTAIN POSITION / REALLOCATE CAPITAL]\n"
                f"  Projected Cost Foundation Basis: Rs.{avg_down_scenario['new_avg_cost']:.2f}\n"
                f"  Required Market Delta to Breakeven: {recovery_gap_pct:.1f}%\n"
                f"  Note: Marginal accumulation benefit. The position is trading close to underlying value. Hold cash."
            )
    
    def calculate_risk_score(self) -> Dict:
        """
        Generates an exposure risk index based on capital concentration, historical 
        time lock-up periods, and unrealized drawdowns.
        
        Returns:
            Dict: Risk analysis evaluation matrix.
        """
        loss_pct = abs(self.portfolio.get_floating_return_percentage())
        total_invested = self.portfolio.get_total_amount_invested()
        
        # Risk factors (Normalized scale 1-10)
        loss_severity = min(loss_pct / 10.0, 10.0)
        capital_lock = min(total_invested / 100000.0, 5.0)
        
        # Safe fallback check for transaction timeline metrics
        try:
            days = sum(t.get_holding_days() for t in self.portfolio.transactions) / max(len(self.portfolio.transactions), 1)
            holding_period = min(days / 365.0, 5.0)
        except AttributeError:
            holding_period = 2.5 # Neutral fallback value
            
        overall_risk = (loss_severity + capital_lock + holding_period) / 3.0
        
        return {
            'loss_severity_score': loss_severity,
            'capital_lock_score': capital_lock,
            'holding_period_score': holding_period,
            'overall_risk_score': overall_risk,
            'risk_level': self._classify_risk(overall_risk)
        }
    
    def _classify_risk(self, score: float) -> str:
        """Classifies the composite index value into an actionable risk tier."""
        if score < 2.0:
            return "MINIMAL RISK"
        elif score < 5.0:
            return "CONTROLLED DEVIATION RISK"
        elif score < 7.0:
            return "HIGH EXPOSURE RISK"
        else:
            return "CRITICAL PROTOCOL EXPOSURE RISK"
    
    def get_action_plan(self) -> Dict:
        """
        Generates a standardized sequential procedural playbook for risk mitigation.
        """
        return {
            'phase_1': "DIAGNOSTIC ARCHITECTURE: Evaluate structural catalyst shift. Determine if deterioration is systemic.",
            'phase_2': "QUANTITATIVE SIMULATION: Run baseline dollar-cost averaging parameters vs. opportunity cost models.",
            'phase_3': "ASYMMETRY PARITY ASSESSMENT: Verify if projected asset return targets outperform risk-free treasury vectors.",
            'phase_4': "ALLOCATION RESOLUTION: Select action vector based on liquid capital availability and fund compliance constraints.",
            'phase_5': "DELEGATED EXECUTION: Compute transaction inventory thresholds and secure the calculated purchase floor.",
            'phase_6': "POST-EXECUTION COMPLIANCE: Establish trailing structural price stops and define profit target exits."
        }