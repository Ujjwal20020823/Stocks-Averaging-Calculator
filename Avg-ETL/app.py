import streamlit as st
from datetime import date, timedelta
import plotly.graph_objects as go
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
fd_rate = st.sidebar.number_input("FD Annual Rate (%)", value=5.0, step=0.25, min_value=0.0)
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

# Get historical FD benchmark metrics using the refactored method
hist_metrics = analyzer.calculate_historical_fd_benchmark(fd_rate)
simple_bep = hist_metrics['simple_bep']
economic_bep = hist_metrics['economic_bep']
opportunity_spread = hist_metrics['opportunity_spread']

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

st.markdown("---")
st.markdown("### Break-Even Price Comparison")
bep_col1, bep_col2, bep_col3 = st.columns(3)
bep_col1.metric("Simple BEP (Cost Basis)", f"Rs. {simple_bep:,.2f}")
bep_col2.metric("Economic BEP (FD Recovery)", f"Rs. {economic_bep:,.2f}")
bep_col3.metric("Lost Opportunity Spread", f"Rs. {opportunity_spread:,.2f} per share")
st.divider()

# Tab Navigation for Modules
tab1, tab2, tab3 = st.tabs([
    "💡 FD vs Averaging Down",
    "🎯 Target Average Extractor",
    "📊 Recovery Price Scenarios",
])

# TAB 1: Historical Sunk Opportunity Cost Analysis
with tab1:
    st.subheader("💡 Historical Sunk Opportunity Cost Analysis")
    st.write(
        "Analyze what your capital invested in past transactions would be worth today in a risk-free Fixed Deposit. "
        "Understand the true economic cost of holding equity vs the risk-free alternative, and your true break-even price."
    )
    
    # Calculate historical FD benchmark using the refactored method
    hist_metrics = analyzer.calculate_historical_fd_benchmark(fd_rate)
    
    st.markdown("---")
    st.markdown("## 📊 Key Historical Metrics")
    
    # Four KPI Cards
    kpi_col1, kpi_col2, kpi_col3, kpi_col4 = st.columns(4)
    with kpi_col1:
        st.metric(
            "Total Invested",
            f"Rs. {hist_metrics['total_cash_invested']:,.0f}",
            help="Total capital invested across all transactions"
        )
    with kpi_col2:
        st.metric(
            "Current Equity Value",
            f"Rs. {hist_metrics['current_portfolio_value']:,.0f}",
            help="Current market value of portfolio"
        )
    with kpi_col3:
        st.metric(
            "Historical FD Benchmark",
            f"Rs. {hist_metrics['total_fd_benchmark']:,.0f}",
            help=f"Value if invested in FD from transaction dates @ {fd_rate:.2f}%"
        )
    with kpi_col4:
        gap = hist_metrics['opportunity_cost_gap']
        gap_color = "inverse" if gap > 0 else "normal"
        st.metric(
            "Opportunity Cost Gap",
            f"Rs. {gap:,.0f}",
            delta_color=gap_color,
            help="Lost yield vs FD (FD Benchmark - Current Value)"
        )
    
    st.markdown("---")
    st.markdown("## 🎯 Break-Even Price Analysis")
    
    # Prominent BEP Banner
    simple_bep = hist_metrics['simple_bep']
    economic_bep = hist_metrics['economic_bep']
    spread = hist_metrics['opportunity_spread']
    current_price = hist_metrics['current_price']
    gain_pct = hist_metrics['gain_from_current_to_economic_bep_pct']
    
    col_bep1, col_bep2, col_bep3 = st.columns(3)
    with col_bep1:
        st.markdown(f"""
        <div style="background-color: #e3f2fd; padding: 15px; border-radius: 8px; text-align: center;">
            <h4 style="color: #1565c0; margin: 0;">Simple BEP</h4>
            <h3 style="color: #0d47a1; margin: 5px 0;">Rs. {simple_bep:,.2f}</h3>
            <p style="color: #666; font-size: 12px; margin: 0;">Cost Basis Breakeven</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col_bep2:
        st.markdown(f"""
        <div style="background-color: #f3e5f5; padding: 15px; border-radius: 8px; text-align: center;">
            <h4 style="color: #6a1b9a; margin: 0;">Economic BEP</h4>
            <h3 style="color: #4a148c; margin: 5px 0;">Rs. {economic_bep:,.2f}</h3>
            <p style="color: #666; font-size: 12px; margin: 0;">True Recovery Price (FD-Adjusted)</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col_bep3:
        st.markdown(f"""
        <div style="background-color: #fff3e0; padding: 15px; border-radius: 8px; text-align: center;">
            <h4 style="color: #e65100; margin: 0;">Spread Required</h4>
            <h3 style="color: #bf360c; margin: 5px 0;">Rs. {spread:,.2f}</h3>
            <p style="color: #666; font-size: 12px; margin: 0;">Per Share Opportunity Cost</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Gain percentage to Economic BEP
    st.markdown("---")
    col_gain_left, col_gain_right = st.columns([2, 1])
    with col_gain_left:
        st.info(f"""
        **Current Price: Rs. {current_price:,.2f}**
        
        To hit Economic BEP (Rs. {economic_bep:,.2f}), you need a **{gain_pct:+.2f}%** move from current price.
        """)
    with col_gain_right:
        if gain_pct > 0:
            st.success(f"↑ {gain_pct:.2f}% to goal")
        elif gain_pct < 0:
            st.error(f"↓ {abs(gain_pct):.2f}% (Already above)")
        else:
            st.warning("At Economic BEP")
    
    st.markdown("---")
    st.markdown("## 📈 Historical Capital Comparison")
    
    # Three-bar comparison chart
    fig_comparison = go.Figure()
    
    categories = ['Total Invested', 'Current Equity Value', 'FD Benchmark Value']
    values = [
        hist_metrics['total_cash_invested'],
        hist_metrics['current_portfolio_value'],
        hist_metrics['total_fd_benchmark']
    ]
    colors = ['#3498db', '#e74c3c', '#2ecc71']
    
    fig_comparison.add_trace(go.Bar(
        x=categories,
        y=values,
        marker_color=colors,
        text=[f"Rs. {v:,.0f}" for v in values],
        textposition='auto',
        hovertemplate="<b>%{x}</b><br>Rs. %{y:,.0f}<extra></extra>"
    ))
    
    fig_comparison.update_layout(
        title='Historical Capital: What You Invested vs. What You Have vs. What FD Would Be Worth',
        yaxis_title='Value (Rs.)',
        xaxis_title='',
        height=450,
        showlegend=False,
        hovermode='x unified'
    )
    
    st.plotly_chart(fig_comparison, use_container_width=True)
    
    st.markdown("---")
    st.markdown("## 📋 Transaction-Level Breakdown")
    
    # Get detailed transaction breakdown
    hist_opp_data = analyzer.get_historical_opportunity_cost(fd_rate)
    
    with st.expander("Show transaction-level compounding details"):
        st.write(f"Detailed analysis of each transaction's FD opportunity cost @ {fd_rate:.2f}% annually:")
        trans_data = []
        for tx in hist_opp_data['detailed_transactions']:
            trans_data.append({
                'TX ID': tx['transaction_id'],
                'Date': tx['date'],
                'Days Held': tx['holding_days'],
                'Years Held': f"{tx['holding_years']:.3f}",
                'Capital': f"Rs. {tx['capital_invested']:,.0f}",
                'FD Value': f"Rs. {tx['fd_value_today']:,.0f}",
                'Opp. Cost': f"Rs. {tx['opportunity_cost']:,.0f}"
            })
        st.dataframe(trans_data, use_container_width=True)
    
    st.markdown("---")
    st.markdown("## 💡 What This Means")
    st.write(f"""
    Your capital of **Rs. {hist_metrics['total_cash_invested']:,.0f}** has been earning equity market returns instead of 
    the guaranteed **{fd_rate:.2f}%** FD rate. 
    
    - If placed in FD from purchase dates, it would be worth **Rs. {hist_metrics['total_fd_benchmark']:,.0f}** today
    - Your equity position is worth **Rs. {hist_metrics['current_portfolio_value']:,.0f}** currently
    - **Hidden opportunity cost: Rs. {hist_metrics['opportunity_cost_gap']:,.0f}**
    
    Your **Simple Break-Even** (cost basis) is **Rs. {simple_bep:,.2f}** per share.
    
    But your **Economic Break-Even** (accounting for lost FD yields) is **Rs. {economic_bep:,.2f}** per share.
    
    The **Rs. {spread:,.2f} per share spread** represents the true economic cost of your equity decision.
    """)

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
    st.subheader("📊 Milestone Price Recovery Scenarios")
    st.write(
        "Review projected portfolio outcomes if the stock moves through key recovery milestones. "
        "This includes both Simple Break-Even (cost basis) and Economic Break-Even (FD recovery price), "
        "which accounts for lost risk-free yields."
    )

    recovery_scenarios = analyzer.get_recovery_scenarios(annual_fd_rate=fd_rate)
    scenario_rows = []
    milestones = []
    net_results = []
    
    for label, data in recovery_scenarios.items():
        scenario_rows.append(
            {
                "Milestone": label,
                "Target Price": f"Rs. {data['target_price']:,.2f}",
                "Projected Value": f"Rs. {data['projected_position_value']:,.2f}",
                "Net Result (Rs.)": f"Rs. {data['net_result_rupees']:,.2f}",
            }
        )
        milestones.append(label)
        net_results.append(data['net_result_rupees'])

    st.table(scenario_rows)

    st.markdown("### Recovery Gain/Loss Visualization")
    
    # Horizontal Bar Chart for Net Results
    colors = ['#e74c3c' if r < 0 else '#2ecc71' for r in net_results]

    fig_recovery = go.Figure(go.Bar(
        x=net_results,
        y=milestones,
        orientation='h',
        marker_color=colors,
        text=[f"Rs. {r:,.0f}" for r in net_results],
        textposition='auto'
    ))

    fig_recovery.update_layout(
        title="Net Portfolio Value Gain/Loss Across Recovery Milestones",
        xaxis_title="Unrealized Gain / Loss (Rs.)",
        yaxis=dict(autorange="reversed"),
        height=380,
        margin=dict(l=20, r=20, t=40, b=20)
    )

    st.plotly_chart(fig_recovery, use_container_width=True)