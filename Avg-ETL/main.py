# main.py
from src.models import Transaction, Portfolio
from src.ui import (
    get_portfolio_from_user,
    display_portfolio_summary,
    display_menu
)
from src.analyzer import PortfolioAnalyzer
from src.recommender import RecommendationEngine

def main():
    """
    Main entry point for Smart Recovery Investment Engine.
    Orchestrates the entire application workflow.
    """
    print("\n" + "="*80)
    print("SMART RECOVERY INVESTMENT ENGINE")
    print("Professional Financial Decision Support System")
    print("="*80 + "\n")
    
    # Get portfolio from user
    portfolio = get_portfolio_from_user()
    
    if portfolio is None:
        print("No portfolio created. Exiting.")
        return
    
    # Main application loop
    while True:
        choice = display_menu()
        
        if choice == '1':
            # Analyze current portfolio
            display_portfolio_summary(portfolio)
            
            # Get recommendation for current position
            engine = RecommendationEngine(portfolio)
            recommendation = engine.get_position_recommendation()
            
            print("\n" + "-"*80)
            print("POSITION RECOMMENDATION:")
            print("-"*80)
            print(recommendation)
            print("-"*80 + "\n")
        
        elif choice == '2':
            # Scenario analysis - averaging down
            try:
                additional_investment = float(input("\nHow much additional investment (Rs.)? "))
                
                if additional_investment <= 0:
                    print("Investment must be greater than zero.")
                    continue
                
                analyzer = PortfolioAnalyzer(portfolio)
                scenario = analyzer.analyze_averaging_down(additional_investment)
                
                print("\n" + "="*80)
                print("AVERAGING DOWN SCENARIO ANALYSIS")
                print("="*80 + "\n")
                
                print(f"Current State:")
                print(f"  Total Shares: {portfolio.get_total_shares_owned()}") # Fixed name
                print(f"  Average Cost: Rs.{portfolio.get_average_weighted_cost():.2f}") # Fixed name
                print(f"  Unrealized Loss: Rs.{abs(portfolio.get_unrealized_gain_loss_rupees()):.2f}")
                
                print(f"\nAfter Averaging Down (Investment: Rs.{additional_investment:.2f}):")
                print(f"  New Total Shares: {scenario['new_shares']}")
                print(f"  New Average Cost: Rs.{scenario['new_avg_cost']:.2f}")
                print(f"  New Unrealized Loss: Rs.{abs(scenario['new_unrealized_loss']):.2f}")
                
                print(f"\nImprovement:")
                print(f"  Shares Added: {scenario['shares_added']}")
                print(f"  Average Cost Reduced By: Rs.{scenario['avg_cost_reduction']:.2f} ({scenario['avg_cost_reduction_pct']:.2f}%)")
                print(f"  Loss Reduction: Rs.{scenario['loss_reduction']:.2f}")
                print(f"  Efficiency Rating: {scenario['efficiency_rank']}")
                
                print("\n" + "="*80 + "\n")
                
            except ValueError:
                print("Invalid input. Please enter a valid amount.\n")
        
        elif choice == '3':
            # Fixed Deposit comparison
            try:
                raw_rate = float(input("\nFixed Deposit annual interest rate (e.g., 7 for 7%): "))
                fd_rate = raw_rate / 100.0
                add_cash = float(input("Additional cash to invest (Rs.): "))
                
                years = portfolio.get_weighted_holding_period_years()
                print(f"Automatically calculated holding period: {years:.2f} years")
                
                if fd_rate < 0 or years <= 0 or add_cash < 0:
                    print("Invalid input. Rate must be non-negative and years must be positive.")
                    continue
                
                analyzer = PortfolioAnalyzer(portfolio)
                fd_comparison = analyzer.compare_with_fd(
                    fd_annual_rate=fd_rate,
                    investment_years=years,
                    additional_investment=add_cash
                )
                
                print("\n" + "="*80)
                print("FIXED DEPOSIT vs AVERAGING DOWN ANALYSIS")
                print("="*80 + "\n")
                
                print(f"If you invest to average down:")
                recovery_needed = analyzer.get_loss_recovery_amount()
                print(f"  Amount needed to recover: Rs.{recovery_needed:.2f}")
                
                print(f"\nIf you invest in Fixed Deposit instead:")
                print(f"  Principal: Rs.{fd_comparison['recovery_needed']:.2f}")
                print(f"  Annual Rate: {fd_comparison['fd_annual_rate']:.2f}%")
                print(f"  Period: {fd_comparison['investment_years']:.2f} years")
                print(f"  Interest Earned: Rs.{fd_comparison['fd_return']:.2f}")
                print(f"  Final Value: Rs.{fd_comparison['fd_final_value']:.2f}")
                
                print("\n" + "="*80 + "\n")
                
                # Get recommendation
                engine = RecommendationEngine(portfolio)
                rec = engine.should_average_down(add_cash, fd_rate, years)
                
                print("RECOMMENDATION:", rec['recommendation'])
                print(f" Fixed Deposit Return: Rs.{rec['fd_return']:.2f}")
                print("="*80 + "\n")
                
            except ValueError:
                print("Invalid input. Please enter valid numbers.\n")
        
        elif choice == '4':
            # Calculate shares needed for target average cost
            try:
                target_avg_cost = float(input("\nTarget average cost (Rs.): "))
                new_purchase_price = float(input("Expected purchase price at market (Rs.): "))
                
                if target_avg_cost <= 0 or new_purchase_price <= 0:
                    print("Prices must be greater than zero.")
                    continue
                
                analyzer = PortfolioAnalyzer(portfolio)
                calc = analyzer.calculate_shares_for_target_avg(target_avg_cost, new_purchase_price)
                
                print("\n" + "="*80)
                print("SHARES CALCULATION FOR TARGET AVERAGE COST")
                print("="*80 + "\n")
                
                print(f"Current Average Cost: Rs.{calc['current_avg_cost']:.2f}")
                print(f"Target Average Cost: Rs.{calc['target_avg_cost']:.2f}")
                print(f"Expected Purchase Price: Rs.{calc['new_purchase_price']:.2f}")
                
                print(f"\nTo achieve target average cost:")
                print(f"  Shares to buy: {calc['shares_to_buy']}")
                print(f"  Investment required: Rs.{calc['investment_required']:.2f}")
                
                print("\n" + "="*80 + "\n")
                
            except ValueError as e:
                print(f"Analysis Input Blocked: {e}\n")
        
        elif choice == '5':
            # Recovery scenarios
            analyzer = PortfolioAnalyzer(portfolio)
            scenarios = analyzer.get_recovery_scenarios()
            
            print("\n" + "="*80)
            print("RECOVERY PRICE SCENARIOS")
            print("="*80 + "\n")
            
            print(f"Current Market Price: Rs.{portfolio.current_market_price:.2f}")
            print(f"Current Unrealized Loss: Rs.{abs(portfolio.get_unrealized_gain_loss_rupees()):.2f}\n")
            
            print(f"{'Milestone Scenario':<32} {'Target Price':<15} {'Net Return':<15} {'Status':<15}")
            print("-"*80)
            
            # Adjusted parser loop to safely unwrap our creative dictionary layout
            for milestone_label, data in scenarios.items():
                net_rupees = data['net_result_rupees']
                status = "PROFIT" if net_rupees > 0 else ("BREAK-EVEN" if net_rupees == 0 else "LOSS")
                print(f"{milestone_label:<32} Rs.{data['target_price']:<12.2f} Rs.{net_rupees:<13.2f} {status:<15}")
            
            print("\n" + "="*80 + "\n")
        
        elif choice == '6':
            print("\nThank you for using Smart Recovery Investment Engine!")
            print("="*80)
            break
        
        else:
            print("Invalid choice. Please select 1-6.\n")

if __name__ == "__main__":
    main()