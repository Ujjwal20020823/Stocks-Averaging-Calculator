from src.models import Transaction, Portfolio

def get_portfolio_from_user() -> Portfolio:
    """Get portfolio details from user interactively."""
    print("\n" + "="*70)
    print("CREATE INVESTOR PROFILE")
    print("="*70 + "\n")
    
    security_name = input("Enter Stock/Ticker Name (e.g., NABIL, NIMB): ").strip().upper()
    current_market_price = float(input("Enter Current Market Price (Rs.): "))
    
    portfolio = Portfolio(security_name, current_market_price)
    
    print("\n" + "-"*70)
    print("ENTER HISTORICAL BUY TRANSACTIONS")
    print("Press [ENTER] on an empty Date box when you are finished entering records.")
    print("-"*70 + "\n")
    
    transaction_id = 1
    while True:
        try:
            date_input = input(f"[TX #{transaction_id}] - Date (YYYY-MM-DD) or press Enter to FINISH: ").strip()
            
            # If the user presses Enter on an empty line, finalize the entry loop
            if date_input == '':
                if transaction_id == 1:
                    print("System requires at least one transaction to compile metrics.\n")
                    continue
                print(f"Entry complete. Compiled {transaction_id - 1} transactions.\n")
                break
            
            # Explicit exit command override just in case
            if date_input.lower() == 'done':
                if transaction_id == 1:
                    print("System requires at least one transaction to compile metrics.\n")
                    continue
                break
            
            price = float(input(f"    - Buy Price per share (Rs.): "))
            shares = int(input(f"    - Number of shares bought: "))
            
            transaction = Transaction(transaction_id, date_input, price, shares)
            portfolio.add_transaction(transaction)
            
            print(f"Position recorded successfully!\n")
            transaction_id += 1
            
        except ValueError as e:
            print(f"Entry Parsing Error: Please enter valid numeric values for price and shares.\n")
        except KeyboardInterrupt:
            print("\n\nProfile building canceled by operator.")
            return None
    
    return portfolio


def display_portfolio_summary(portfolio: Portfolio) -> None:
    """Display complete asset holdings analysis."""
    if portfolio is None:
        return
    
    print("\n" + "═"*70)
    print(f"STRATEGIC POSITION REPORT: {portfolio.security_name}")
    print("═"*70 + "\n")
    
    print("HISTORICAL TRANSACTION LOG:")
    print("-"*70)
    for transaction in portfolio.transactions:
        print(f"  {transaction}")
    
    print("\n" + "CORE POSITION METRICS:")
    print("-"*70)
    print(f"  Total Position Inventory : {portfolio.get_total_shares_owned()} Shares")
    print(f"  Deployed Principal Cash  : Rs.{portfolio.get_total_invested_amount():,.2f}")
    print(f"  Weighted Cost Foundation : Rs.{portfolio.get_average_weighted_cost():,.2f}")
    print(f"  Break-Even Target Floor  : Rs.{portfolio.get_break_even_price():,.2f}")
    
    print("\n" + "VALUATION & EXPOSURE:")
    print("-"*70)
    print(f"  Current Live Market Price: Rs.{portfolio.current_market_price:,.2f}")
    print(f"  Liquid Portfolio Value   : Rs.{portfolio.get_current_portfolio_value():,.2f}")
    
    gain_loss = portfolio.get_unrealized_gain_loss_rupees()
    # Fixed method name connection here
    gain_loss_pct = portfolio.get_unrealized_gain_loss_percentage()
    status = portfolio.get_portfolio_status()
    
    # Creative indicator color schemes
    icon = "🟢" if status == "PROFIT" else ("🔴" if status == "LOSS" else "🟡")
    
    print(f"  Floating Paper Equity    : Rs.{gain_loss:,.2f}")
    print(f"  Total Account Variance   : {gain_loss_pct:.2f}%")
    print(f"  Current Posture Assessment: {icon} {status}")
    print("\n" + "═"*70 + "\n")


def display_menu() -> str:
    """Displays the updated 6-option decision menu required by main.py."""
    print("═"*70)
    print("STRATEGIC DECISION SUPPORT DESK")
    print("═"*70)
    print("Audit Current Position Summary & Advisory Recommendation")
    print("Run Scenario Simulation (What-if I average down now?)")
    print("Calculate Opportunity Cost Risk (Averaging Down vs Fixed Deposit)")
    print("Target Extraction Math (How many shares to reach specific Average cost?)")
    print("Compile Milestone Price Target Scenarios")
    print("6Safely Close Session / Exit Engine")
    print("═"*70)
    
    choice = input("\nSelect Execution Vector (1-6): ").strip()
    return choice