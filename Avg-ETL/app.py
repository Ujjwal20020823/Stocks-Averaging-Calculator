import streamlit as st
from datetime import date, timedelta
from src.models import Portfolio, Transaction
from src.analyzer import PortfolioAnalyzer

# Page Configuration
st.set_page_config(
    page_title="NEPSE Averaging Down vs FD Engine",
    page_icon="📈",
    layout="wide"
)

st.title("📈 Stock Position & Averaging Down vs. Fixed Deposit Analysis")
st.markdown(
    "An interactive financial decision engine for evaluating equity loss recovery against risk-free yield. "
    "Use the sidebar to model your position and compare defensive averaging down strategies with low-risk fixed deposit alternatives."
)

# Sidebar - Portfolio Inputs
st.sidebar.header("Portfolio Inputs")
security_name = st.sidebar.text_input("Security Name", value="NEPSE_STOCK")
current_price = st.sidebar.number_input(
    "Current Market Price (Rs.)", value=750.0, step=10.0, min_value=0.0
)
transaction_count = st.sidebar.slider("Number of Transactions", 1, 10, 2)

portfolio = Portfolio(security_name=security_name, current_market_price=current_price)

st.sidebar.markdown("---")
st.sidebar.subheader("Transaction History")
for idx in range(transaction_count):
    st.sidebar.markdown(f"**Transaction {idx + 1}**")
    transaction_date = st.sidebar.date_input(
        f"Date {idx + 1}",
        value=date(2025, 1, 1) + timedelta(days=idx * 30),
        key=f"date_{idx}"
    )
    purchase_price = st.sidebar.number_input(
        f"Purchase Price (Rs.) {idx + 1}",
        value=1000.0 if idx == 0 else 921.43,
        step=10.0,
        min_value=0.01,
        key=f"price_{idx}"
    )
    shares_bought = st.sidebar.number_input(
        f"Shares Bought {idx + 1}",
        value=100 if idx == 0 else 350,
        step=10,
        min_value=1,
        key=f"shares_{idx}"
    )
    portfolio.add_transaction(
        Transaction(
            idx + 1,
            transaction_date.strftime("%Y-%m-%d"),
            purchase_price,
            shares_bought,
        )
    )

analyzer = PortfolioAnalyzer(portfolio)

# Top Key Metrics Bar
total_shares = portfolio.get_total_shares_owned()
avg_cost = portfolio.get_weighted_average_cost()
portfolio_value = portfolio.get_current_portfolio_value()
unrealized_gain_loss = portfolio.get_unrealized_gain_loss_rupees()
recovery_needed = abs(unrealized_gain_loss) if unrealized_gain_loss < 0 else 0.0

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Shares Owned", f"{total_shares:,}")
col2.metric("Weighted Avg Cost", f"Rs. {avg_cost:,.2f}")
col3.metric("Portfolio Value", f"Rs. {portfolio_value:,.2f}")
col4.metric(
    "Unrealized P/L",
    f"Rs. {unrealized_gain_loss:,.2f}",
    delta=f"Rs. {recovery_needed:,.2f}",
    delta_color="inverse" if unrealized_gain_loss < 0 else "normal",
)

st.markdown(f"**Break-even Price:** Rs. {portfolio.get_break_even_price():,.2f}")
st.divider()

# Tab Navigation for Modules
tab1, tab2, tab3 = st.tabs([
    "💡 FD vs Averaging Down",
    "🎯 Target Average Extractor",
    "📊 Recovery Price Scenarios",
])

# TAB 1: FD vs. Averaging Down Comparison
with tab1:
    st.subheader("Fixed Deposit vs Averaging Down")
    st.write(
        "Compare a defensive averaging-down investment with a low-risk fixed deposit alternative. "
        "This section helps you evaluate whether deploying additional capital to lower your weighted average cost "
        "makes more sense than earning a risk-free return on the same amount."
    )

    col_a, col_b, col_c = st.columns([1, 1, 1])
    with col_a:
        add_cash = st.number_input(
            "Additional Cash to Invest (Rs.)", value=100000.0, step=10000.0, min_value=0.0
        )
    with col_b:
        fd_rate = st.number_input("FD Annual Rate (%)", value=5.0, step=0.25, min_value=0.0)
    with col_c:
        holding_years = st.number_input(
            "Investment Timeline (Years)", value=1.0, step=0.25, min_value=0.0
        )

    fd_comp = analyzer.compare_with_fd(
        fd_annual_rate=fd_rate,
        investment_years=holding_years,
        additional_investment=add_cash,
    )
    avg_scenario = analyzer.analyze_averaging_down(add_cash)

    st.markdown("### Comparative Execution Metrics")
    mc1, mc2, mc3, mc4 = st.columns(4)
    mc1.metric("New Average Cost", f"Rs. {avg_scenario['new_avg_cost']:,.2f}")
    mc2.metric("Avg Cost Reduction", f"Rs. {avg_scenario['avg_cost_reduction']:,.2f}")
    mc3.metric("FD Interest Earned", f"Rs. {fd_comp['fd_return']:,.2f}")
    mc4.metric("FD Final Value", f"Rs. {fd_comp['fd_final_value']:,.2f}")

    st.markdown("#### Additional Analysis")
    st.write(
        f"If you invest Rs. {add_cash:,.0f} at the current market price, your portfolio average cost could drop by "
        f"Rs. {avg_scenario['avg_cost_reduction']:,.2f}, while a fixed deposit at {fd_rate:.2f}% for {holding_years:.2f} years "
        f"would yield about Rs. {fd_comp['fd_return']:,.2f}."
    )

    st.markdown("### Visual Comparison")
    st.bar_chart({
        "FD Final Value": [fd_comp['fd_final_value']],
        "Averaged Portfolio Value": [avg_scenario['new_shares'] * current_price],
    })

# TAB 2: Target Average Extractor
with tab2:
    st.subheader("Target Average Cost Extraction")
    st.write(
        "Determine how many shares you need to buy at a given entry price to reach your desired weighted average cost. "
        "This is useful for planning defensive purchases when managing an under-water position."
    )

    target_avg = st.number_input(
        "Target Average Cost (Rs.)", value=max(avg_cost - 100.0, 1.0), step=10.0, min_value=0.01
    )
    buy_price = st.number_input(
        "Expected Purchase Price (Rs.)", value=current_price, step=10.0, min_value=0.01
    )

    try:
        target_calc = analyzer.calculate_shares_for_target_avg(
            target_avg_cost=target_avg,
            new_purchase_price=buy_price,
        )
        tas1, tas2 = st.columns(2)
        tas1.metric("Required Shares to Buy", f"{target_calc['shares_to_buy']:,} shares")
        tas2.metric("Total Capital Required", f"Rs. {target_calc['investment_required']:,.2f}")
    except ValueError as exc:
        st.error(str(exc))

# TAB 3: Milestone Recovery Scenarios
with tab3:
    st.subheader("Milestone Price Recovery Scenarios")
    st.write(
        "Review projected portfolio outcomes if the stock moves through key recovery milestones. "
        "This table is built around your current weighted average cost and position size."
    )

    recovery_scenarios = analyzer.get_recovery_scenarios()
    scenario_rows = []
    for label, data in recovery_scenarios.items():
        scenario_rows.append(
            {
                "Milestone": label,
                "Target Price": f"Rs. {data['target_price']:,.2f}",
                "Projected Value": f"Rs. {data['projected_position_value']:,.2f}",
                "Net Result (Rs.)": f"Rs. {data['net_result_rupees']:,.2f}",
            }
        )

    st.table(scenario_rows)
