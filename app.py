import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.optimize import newton
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Import functions from financial_simulation module
from financial_simulation_lib import (
    calculate_monthly_return,
    get_15_year_sequences,
    run_investment_simulation,
    extract_simulation_data,
    calculate_all_irrs,
    calculate_milestone_statistics,
    calculate_fund_returns,
    market_returns
)

def get_contribution_for_month(month, contribution_periods):
    """
    Get the contribution amount for a given month based on contribution periods.
    
    Parameters:
    -----------
    month : int
        The month number (0-indexed)
    contribution_periods : list
        List of dicts with 'contribution' and 'start_month'
    
    Returns:
    --------
    float : The contribution amount for that month
    """
    # Find the appropriate period (last period whose start_month <= month)
    applicable_contribution = contribution_periods[0]['contribution']
    for period in contribution_periods:
        if month >= period['start_month']:
            applicable_contribution = period['contribution']
        else:
            break
    return applicable_contribution

# Page configuration
st.set_page_config(
    page_title="Financial Simulation Comparator",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        font-size: 4.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .section-header {
        font-size: 2rem;
        font-weight: bold;
        color: #2c3e50;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.5rem;
        font-weight: bold;
        color: #2c3e50;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    </style>
""", unsafe_allow_html=True)

# Title
st.markdown('<p class="main-header">Investment Portfolio Simulator</p>', unsafe_allow_html=True)
st.markdown("**Compare up to 4 different investment strategies over 15 years using historical market data**")

# Sidebar for global parameters
st.sidebar.header("📊 Simulation Parameters")

# Initial amounts
st.sidebar.subheader("Initial Amounts")
investment_start = st.sidebar.number_input(
    "Initial Investment ($)",
    min_value=0,
    max_value=1000000,
    value=50000,
    step=1000,
    help="Starting investment amount to allocate across funds"
)

emergency_fund_start = st.sidebar.number_input(
    "Emergency Fund ($)",
    min_value=0,
    max_value=1000000,
    value=25000,
    step=1000,
    help="Emergency fund kept in HYSA (grows but receives no contributions)"
)

# Contribution schedule
st.sidebar.subheader("Monthly Contributions")

# Number of contribution periods
num_periods = st.sidebar.selectbox(
    "Number of Contribution Periods",
    options=[1, 2, 3, 4],
    index=2,
    help="Define different contribution amounts over time"
)

# Initialize contribution periods
contribution_periods = []

for i in range(num_periods):
    with st.sidebar.expander(f"Period {i+1}", expanded=(i==0)):
        if i == 0:
            contribution = st.number_input(
                f"Monthly Contribution ($)",
                min_value=0,
                max_value=50000,
                value=3200,
                step=100,
                key=f"contrib_{i}",
                help="Monthly contribution for this period"
            )
            duration = None  # First period starts immediately
        else:
            contribution = st.number_input(
                f"Monthly Contribution ($)",
                min_value=0,
                max_value=50000,
                value=[4000, 1000, 500][i-1] if i <= 3 else 1000,
                step=100,
                key=f"contrib_{i}",
                help="Monthly contribution for this period"
            )
            duration = st.slider(
                f"Starts at Month",
                min_value=1,
                max_value=180,
                value=[7, 20, 36][i-1] if i <= 3 else 12*i,
                key=f"duration_{i}",
                help="Month when this contribution period begins"
            )
        
        contribution_periods.append({
            'contribution': contribution,
            'start_month': duration if duration is not None else 0
        })

# Sort periods by start month
contribution_periods = sorted(contribution_periods, key=lambda x: x['start_month'])

# Market parameters
st.sidebar.subheader("Market Volatility")
hysa_apy = st.sidebar.slider(
    "HYSA APY (%)",
    min_value=0.0,
    max_value=10.0,
    value=3.5,
    step=0.1,
    help="Annual percentage yield for High Yield Savings Account"
) / 100

SP500_std = st.sidebar.slider(
    "S&P 500 Std Dev",
    min_value=0.0,
    max_value=0.2,
    value=0.045,
    step=0.005,
    help="Monthly return standard deviation for S&P 500"
)

NASDAQ_std = st.sidebar.slider(
    "NASDAQ Std Dev",
    min_value=0.0,
    max_value=0.2,
    value=0.07,
    step=0.005,
    help="Monthly return standard deviation for NASDAQ 100"
)

T_Bills_std = st.sidebar.slider(
    "T-Bills Std Dev",
    min_value=0.0,
    max_value=0.05,
    value=0.002,
    step=0.001,
    help="Monthly return standard deviation for 3-Month T-Bills"
)

# Simulation parameters
st.sidebar.subheader("Simulation Settings")
total_iterations = st.sidebar.selectbox(
    "Iterations per Sequence",
    options=[100, 500, 1000, 2500, 5000],
    index=2,
    help="Number of Monte Carlo iterations to run for each historical sequence"
)

# Initialize session state for portfolios
if 'portfolios' not in st.session_state:
    st.session_state.portfolios = {
        1: {'name': 'Moderately Aggressive', 'SP500': 45, 'NASDAQ': 35, 'TBill': 5, 'HYSA': 15, 'enabled': True, 'rebalance': False, 'rebalance_threshold': 5},
        2: {'name': 'Moderately Conservative', 'SP500': 30, 'NASDAQ': 20, 'TBill': 5, 'HYSA': 45, 'enabled': True, 'rebalance': False, 'rebalance_threshold': 5},
        3: {'name': 'Balanced', 'SP500': 40, 'NASDAQ': 25, 'TBill': 10, 'HYSA': 25, 'enabled': False, 'rebalance': False, 'rebalance_threshold': 5},
        4: {'name': 'Conservative', 'SP500': 20, 'NASDAQ': 10, 'TBill': 20, 'HYSA': 50, 'enabled': False, 'rebalance': False, 'rebalance_threshold': 5}
    }

# Portfolio configuration section
st.markdown('<p class="section-header">🎯 Portfolio Configurations</p>', unsafe_allow_html=True)
st.markdown("Configure up to 4 different investment portfolios to compare. Toggle the checkbox to include each portfolio in the comparison.")

portfolio_cols = st.columns(4)

for i in range(1, 5):
    with portfolio_cols[i-1]:
        st.markdown(f"**Portfolio {i}**")
        
        enabled = st.checkbox(
            f"Enable Portfolio {i}",
            value=st.session_state.portfolios[i]['enabled'],
            key=f"enable_{i}"
        )
        st.session_state.portfolios[i]['enabled'] = enabled
        
        if enabled:
            name = st.text_input(
                "Name",
                value=st.session_state.portfolios[i]['name'],
                key=f"name_{i}"
            )
            st.session_state.portfolios[i]['name'] = name
            
            sp500 = st.number_input(
                "S&P 500 (%)",
                min_value=0,
                max_value=100,
                value=st.session_state.portfolios[i]['SP500'],
                step=5,
                key=f"sp500_{i}"
            )
            
            nasdaq = st.number_input(
                "NASDAQ (%)",
                min_value=0,
                max_value=100,
                value=st.session_state.portfolios[i]['NASDAQ'],
                step=5,
                key=f"nasdaq_{i}"
            )
            
            tbill = st.number_input(
                "T-Bills (%)",
                min_value=0,
                max_value=100,
                value=st.session_state.portfolios[i]['TBill'],
                step=5,
                key=f"tbill_{i}"
            )
            
            hysa = st.number_input(
                "HYSA (%)",
                min_value=0,
                max_value=100,
                value=st.session_state.portfolios[i]['HYSA'],
                step=5,
                key=f"hysa_{i}"
            )
            
            # Update portfolio
            st.session_state.portfolios[i].update({
                'SP500': sp500,
                'NASDAQ': nasdaq,
                'TBill': tbill,
                'HYSA': hysa
            })
            
            # Rebalancing option
            rebalance = st.checkbox(
                "Enable Quarterly Rebalancing",
                value=st.session_state.portfolios[i].get('rebalance', False),
                key=f"rebalance_{i}",
                help="Automatically adjust contributions each quarter to maintain target allocation"
            )
            st.session_state.portfolios[i]['rebalance'] = rebalance
            
            # If rebalancing enabled, show threshold slider
            if rebalance:
                rebalance_threshold = st.slider(
                    "Rebalancing Threshold (%)",
                    min_value=1,
                    max_value=10,
                    value=st.session_state.portfolios[i].get('rebalance_threshold', 5),
                    step=1,
                    key=f"rebalance_threshold_{i}",
                    help="Trigger rebalancing when any asset deviates by this percentage from target"
                )
                st.session_state.portfolios[i]['rebalance_threshold'] = rebalance_threshold
            else:
                st.session_state.portfolios[i]['rebalance_threshold'] = 5  # Default
            
            # Validate allocation
            total = sp500 + nasdaq + tbill + hysa
            if total == 100:
                st.success(f"✓ Total: {total}%")
            else:
                st.error(f"⚠ Total: {total}% (must equal 100%)")

# Run simulation button
st.markdown("---")
run_simulation = st.button("🚀 Run Simulation", type="primary", use_container_width=True)

if run_simulation:
    # Validate all enabled portfolios
    enabled_portfolios = [i for i in range(1, 5) if st.session_state.portfolios[i]['enabled']]
    
    if not enabled_portfolios:
        st.error("Please enable at least one portfolio to run the simulation.")
    else:
        all_valid = True
        for i in enabled_portfolios:
            port = st.session_state.portfolios[i]
            total = port['SP500'] + port['NASDAQ'] + port['TBill'] + port['HYSA']
            if total != 100:
                st.error(f"Portfolio {i} ({port['name']}) allocation must total 100% (currently {total}%)")
                all_valid = False
        
        if all_valid:
            # Get historical sequences
            with st.spinner("Loading historical market data..."):
                sequences = get_15_year_sequences(market_returns)
                complete_sequences = [seq for seq in sequences
                                    if seq['SP500'] is not None
                                    and seq['NASDAQ100'] is not None
                                    and seq['TBILL_3M'] is not None]
                
                st.info(f"Found {len(complete_sequences)} complete 15-year historical sequences")
            
            # Create contribution function
            def contribution_func(month):
                return get_contribution_for_month(month, contribution_periods)
            
            # Store results
            simulation_results = {}
            
            # Run simulations for each enabled portfolio
            for i in enabled_portfolios:
                port = st.session_state.portfolios[i]
                
                with st.spinner(f"Running simulation for {port['name']}..."):
                    investment_mix = {
                        'SP500': port['SP500'] / 100,
                        'NASDAQ': port['NASDAQ'] / 100,
                        'TBill': port['TBill'] / 100,
                        'HYSA': port['HYSA'] / 100
                    }
                    
                    results = run_investment_simulation(
                        investment_mix=investment_mix,
                        investment_start=investment_start,
                        emergency_fund_start=emergency_fund_start,
                        complete_sequences=complete_sequences,
                        total_iterations=total_iterations,
                        hysa_apy=hysa_apy,
                        SP500_std=SP500_std,
                        NASDAQ_std=NASDAQ_std,
                        T_Bills_std=T_Bills_std,
                        contribution_function=contribution_func,
                        enable_rebalancing=port['rebalance'],
                        rebalancing_threshold=port.get('rebalance_threshold', 5) / 100,  # Convert to decimal
                        simulation_name=port['name']
                    )
                    
                    simulation_results[i] = {
                        'name': port['name'],
                        'results': results,
                        'data': extract_simulation_data(results),
                        'investment_mix': investment_mix
                    }
            
            # Store in session state
            st.session_state.simulation_results = simulation_results
            st.session_state.complete_sequences = complete_sequences
            st.session_state.contribution_func = contribution_func
            st.success("✓ Simulation complete!")

# Display results if available
if 'simulation_results' in st.session_state:
    results = st.session_state.simulation_results
    complete_sequences = st.session_state.complete_sequences
    contribution_func = st.session_state.contribution_func
    
    st.markdown("---")
    st.markdown('<p class="section-header">📈 Simulation Results</p>', unsafe_allow_html=True)
    
    # Summary metrics
    st.markdown("### Final Portfolio Values (15 Years)")
    
    # Add baseline column first, then portfolio columns
    baseline_mean = np.mean(list(results.values())[0]['data']['baselines'])
    
    num_cols = len(results) + 1  # +1 for baseline
    metric_cols = st.columns(num_cols)
    
    # Baseline in first column
    with metric_cols[0]:
        st.metric(
            label="Baseline (HYSA)",
            value=f"${baseline_mean:,.0f}",
            delta=None
        )
    
    # Portfolios in remaining columns
    for idx, (port_id, result_data) in enumerate(results.items(), 1):
        with metric_cols[idx]:
            data = result_data['data']
            final_values = data['final_values']
            baselines = data['baselines']
            
            median_value = np.median(final_values)
            beat_baseline_pct = np.sum(final_values > baselines) / len(final_values) * 100
            
            st.metric(
                label=result_data['name'],
                value=f"${median_value:,.0f}",
                delta=f"{beat_baseline_pct:.1f}% beat baseline"
            )
    
    # Create comparison table
    st.markdown("### Detailed Comparison")
    
    comparison_data = []
    for port_id, result_data in results.items():
        data = result_data['data']
        final_values = data['final_values']
        baselines = data['baselines']
        
        comparison_data.append({
            'Portfolio': result_data['name'],
            'Mean': f"${np.mean(final_values):,.0f}",
            'Median': f"${np.median(final_values):,.0f}",
            '25th %ile': f"${np.percentile(final_values, 25):,.0f}",
            '75th %ile': f"${np.percentile(final_values, 75):,.0f}",
            'Std Dev': f"${np.std(final_values):,.0f}",
            'Beat Baseline': f"{np.sum(final_values > baselines) / len(final_values) * 100:.1f}%"
        })
    
    df_comparison = pd.DataFrame(comparison_data)
    st.dataframe(df_comparison, use_container_width=True)
    
    # Milestone comparison with percentiles
    st.markdown("### Portfolio Growth Over Time")
    
    # Controls for filtering the chart
    st.markdown("**Chart Filters:**")
    filter_col1, filter_col2 = st.columns(2)
    
    with filter_col1:
        st.markdown("**Select Portfolios:**")
        portfolio_filters = {}
        for port_id, result_data in results.items():
            portfolio_filters[port_id] = st.checkbox(
                result_data['name'],
                value=True,
                key=f"filter_port_{port_id}"
            )
    
    with filter_col2:
        st.markdown("**Select Percentiles:**")
        show_p10 = st.checkbox("10th Percentile", value=False, key="show_p10")
        show_p25 = st.checkbox("25th Percentile", value=False, key="show_p25")
        show_median = st.checkbox("Median (50th)", value=True, key="show_median")
        show_p75 = st.checkbox("75th Percentile", value=False, key="show_p75")
        show_p90 = st.checkbox("90th Percentile", value=False, key="show_p90")
        show_baseline = st.checkbox("Baseline", value=True, key="show_baseline")
    
    # Build milestone data
    milestones = [3, 5, 7, 10, 15]
    
    # Create interactive plot with Plotly
    fig = go.Figure()
    
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728']
    
    # Add traces for each selected portfolio and percentile
    for idx, (port_id, result_data) in enumerate(results.items()):
        if not portfolio_filters.get(port_id, False):
            continue
            
        color = colors[idx % len(colors)]
        name = result_data['name']
        
        # Calculate percentiles at each milestone
        percentile_data = {
            'p10': [],
            'p25': [],
            'p50': [],
            'p75': [],
            'p90': []
        }
        
        for year in milestones:
            stats = calculate_milestone_statistics(result_data['results'], year)
            month_index = year * 12
            
            # Calculate all percentiles
            milestone_values = []
            for result_dict in result_data['results']['result_dict']:
                if len(result_dict['Month_Index']) > month_index:
                    total = (result_dict['SP500'][month_index] +
                            result_dict['NASDAQ100'][month_index] +
                            result_dict['TBILL_3M'][month_index] +
                            result_dict['HYSA'][month_index] +
                            result_dict['Emergency_fund'][month_index])
                    milestone_values.append(total)
            
            milestone_values = np.array(milestone_values)
            percentile_data['p10'].append(np.percentile(milestone_values, 10))
            percentile_data['p25'].append(np.percentile(milestone_values, 25))
            percentile_data['p50'].append(np.percentile(milestone_values, 50))
            percentile_data['p75'].append(np.percentile(milestone_values, 75))
            percentile_data['p90'].append(np.percentile(milestone_values, 90))
        
        # Add selected percentile traces
        if show_p10:
            fig.add_trace(go.Scatter(
                x=milestones,
                y=percentile_data['p10'],
                mode='lines+markers',
                name=f"{name} (10th %ile)",
                line=dict(color=color, width=2, dash='dot'),
                marker=dict(size=6),
                legendgroup=name
            ))
        
        if show_p25:
            fig.add_trace(go.Scatter(
                x=milestones,
                y=percentile_data['p25'],
                mode='lines+markers',
                name=f"{name} (25th %ile)",
                line=dict(color=color, width=2, dash='dash'),
                marker=dict(size=6),
                legendgroup=name
            ))
        
        if show_median:
            fig.add_trace(go.Scatter(
                x=milestones,
                y=percentile_data['p50'],
                mode='lines+markers',
                name=f"{name} (Median)",
                line=dict(color=color, width=3),
                marker=dict(size=8),
                legendgroup=name
            ))
        
        if show_p75:
            fig.add_trace(go.Scatter(
                x=milestones,
                y=percentile_data['p75'],
                mode='lines+markers',
                name=f"{name} (75th %ile)",
                line=dict(color=color, width=2, dash='dash'),
                marker=dict(size=6),
                legendgroup=name
            ))
        
        if show_p90:
            fig.add_trace(go.Scatter(
                x=milestones,
                y=percentile_data['p90'],
                mode='lines+markers',
                name=f"{name} (90th %ile)",
                line=dict(color=color, width=2, dash='dot'),
                marker=dict(size=6),
                legendgroup=name
            ))
    
    # Add baseline if selected
    if show_baseline:
        baseline_values = []
        for year in milestones:
            stats = calculate_milestone_statistics(list(results.values())[0]['results'], year)
            baseline_values.append(stats['avg_baseline'])
        
        fig.add_trace(go.Scatter(
            x=milestones,
            y=baseline_values,
            mode='lines+markers',
            name='Baseline (HYSA only)',
            line=dict(color='black', width=3, dash='dash'),
            marker=dict(size=8)
        ))
    
    fig.update_layout(
        title='Portfolio Value at Key Milestones (Customizable View)',
        xaxis_title='Years',
        yaxis_title='Portfolio Value ($)',
        hovermode='x unified',
        height=600,
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01
        )
    )
    
    fig.update_yaxes(tickformat='$,.0f')
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Percentile Table at Milestones
    st.markdown("### Percentile Values at Key Milestones")
    
    milestones = [3, 5, 7, 10, 15]
    
    # Build hierarchical column structure
    columns = [('Year', '')]
    columns.append(('Baseline', ''))
    
    for port_id, result_data in results.items():
        for percentile_name in ['10th', '25th', '50th', '75th', '90th']:
            columns.append((result_data['name'], f"{percentile_name}%"))
    
    # Create multi-index columns
    multi_columns = pd.MultiIndex.from_tuples(columns)
    
    # Build data rows
    table_data = []
    for year in milestones:
        row_data = [year]
        
        # Add baseline
        stats = calculate_milestone_statistics(list(results.values())[0]['results'], year)
        row_data.append(f"${stats['avg_baseline']:,.0f}")
        
        # Add each portfolio's percentiles
        for port_id, result_data in results.items():
            month_index = year * 12
            milestone_values = []
            
            for result_dict in result_data['results']['result_dict']:
                if len(result_dict['Month_Index']) > month_index:
                    total = (result_dict['SP500'][month_index] +
                            result_dict['NASDAQ100'][month_index] +
                            result_dict['TBILL_3M'][month_index] +
                            result_dict['HYSA'][month_index] +
                            result_dict['Emergency_fund'][month_index])
                    milestone_values.append(total)
            
            if milestone_values:
                for percentile_value in [10, 25, 50, 75, 90]:
                    row_data.append(f"${np.percentile(milestone_values, percentile_value):,.0f}")
            else:
                for _ in range(5):
                    row_data.append("N/A")
        
        table_data.append(row_data)
    
    # Create DataFrame with hierarchical columns
    df_milestones = pd.DataFrame(table_data, columns=multi_columns)
    st.dataframe(df_milestones, use_container_width=True, hide_index=True)
    
    # Distribution comparison (tabs instead of overlay)
    st.markdown("### Final Value Distributions")
    
    # First, calculate the max frequency across all portfolios for consistent y-axis
    all_final_values = []
    for port_id, result_data in results.items():
        all_final_values.extend(result_data['data']['final_values'])
    
    # Calculate histogram to get max frequency
    hist_counts, _ = np.histogram(all_final_values, bins=35)
    max_frequency = int(np.max(hist_counts) * 1.1)  # Add 10% padding
    
    # Create tabs for each portfolio
    dist_tabs = st.tabs([result_data['name'] for result_data in results.values()])
    
    for tab, (port_id, result_data) in zip(dist_tabs, results.items()):
        with tab:
            data = result_data['data']
            final_values = data['final_values']
            baselines = data['baselines']
            
            fig = go.Figure()
            
            # Add portfolio distribution
            fig.add_trace(go.Histogram(
                x=final_values,
                name=result_data['name'],
                marker_color=colors[(port_id-1) % len(colors)],
                opacity=0.7,
                nbinsx=35
            ))
            
            # Add median line only (removed baseline)
            median_val = np.median(final_values)
            fig.add_vline(
                x=median_val,
                line_dash="dot",
                line_color="darkblue",
                annotation_text=f"Median: ${median_val:,.0f}",
                annotation_position="top"
            )
            
            fig.update_layout(
                title=f'{result_data["name"]} - Distribution of Final Values (15 Years)',
                xaxis_title='Final Portfolio Value ($)',
                yaxis_title='Frequency',
                height=500,
                showlegend=False,
                yaxis=dict(range=[0, max_frequency])
            )
            
            fig.update_xaxes(tickformat='$,.0f')
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Show summary statistics with baseline first, then all percentiles including median
            baseline_mean = np.mean(baselines)
            col0, col1, col2, col3, col4, col5 = st.columns(6)
            with col0:
                st.metric("Baseline", f"${baseline_mean:,.0f}")
            with col1:
                st.metric("10th %ile", f"${np.percentile(final_values, 10):,.0f}")
            with col2:
                st.metric("25th %ile", f"${np.percentile(final_values, 25):,.0f}")
            with col3:
                st.metric("50th %ile (Median)", f"${np.percentile(final_values, 50):,.0f}")
            with col4:
                st.metric("75th %ile", f"${np.percentile(final_values, 75):,.0f}")
            with col5:
                st.metric("90th %ile", f"${np.percentile(final_values, 90):,.0f}")
    
    # Asset Allocation Over Time
    st.markdown("### Asset Allocation Over Time")
    st.markdown("**Track how portfolio allocation changes over the 15-year period**")
    
    # Create tabs for each portfolio
    alloc_tabs = st.tabs([result_data['name'] for result_data in results.values()])
    
    for tab, (port_id, result_data) in zip(alloc_tabs, results.items()):
        with tab:
            # Calculate median allocations at each month
            months = list(range(0, 181, 1))  # 0 to 180 months (15 years)
            
            # Initialize allocation tracking
            sp500_allocs = []
            nasdaq_allocs = []
            tbill_allocs = []
            hysa_allocs = []
            
            for month_idx in months:
                month_sp500 = []
                month_nasdaq = []
                month_tbill = []
                month_hysa = []
                
                # Get allocation at this month for all iterations
                for result_dict in result_data['results']['result_dict']:
                    if month_idx < len(result_dict['Month_Index']):
                        total = (result_dict['SP500'][month_idx] +
                                result_dict['NASDAQ100'][month_idx] +
                                result_dict['TBILL_3M'][month_idx] +
                                result_dict['HYSA'][month_idx])
                        
                        if total > 0:
                            month_sp500.append(result_dict['SP500'][month_idx] / total * 100)
                            month_nasdaq.append(result_dict['NASDAQ100'][month_idx] / total * 100)
                            month_tbill.append(result_dict['TBILL_3M'][month_idx] / total * 100)
                            month_hysa.append(result_dict['HYSA'][month_idx] / total * 100)
                
                # Calculate median allocation for this month
                if month_sp500:
                    sp500_allocs.append(np.median(month_sp500))
                    nasdaq_allocs.append(np.median(month_nasdaq))
                    tbill_allocs.append(np.median(month_tbill))
                    hysa_allocs.append(np.median(month_hysa))
                else:
                    sp500_allocs.append(None)
                    nasdaq_allocs.append(None)
                    tbill_allocs.append(None)
                    hysa_allocs.append(None)
            
            # Convert months to years for x-axis
            years_axis = [m / 12 for m in months]
            
            # Create the allocation chart
            fig = go.Figure()
            
            fig.add_trace(go.Scatter(
                x=years_axis,
                y=sp500_allocs,
                mode='lines',
                name='S&P 500',
                line=dict(color='#1f77b4', width=2),
                stackgroup='one'
            ))
            
            fig.add_trace(go.Scatter(
                x=years_axis,
                y=nasdaq_allocs,
                mode='lines',
                name='NASDAQ 100',
                line=dict(color='#ff7f0e', width=2),
                stackgroup='one'
            ))
            
            fig.add_trace(go.Scatter(
                x=years_axis,
                y=tbill_allocs,
                mode='lines',
                name='3-Month T-Bills',
                line=dict(color='#2ca02c', width=2),
                stackgroup='one'
            ))
            
            fig.add_trace(go.Scatter(
                x=years_axis,
                y=hysa_allocs,
                mode='lines',
                name='HYSA',
                line=dict(color='#d62728', width=2),
                stackgroup='one'
            ))
            
            # Add target allocation lines (dashed)
            target_mix = result_data['investment_mix']
            fig.add_trace(go.Scatter(
                x=[0, 15],
                y=[target_mix['SP500']*100, target_mix['SP500']*100],
                mode='lines',
                name='Target S&P 500',
                line=dict(color='#1f77b4', width=1, dash='dash'),
                showlegend=False
            ))
            
            fig.update_layout(
                title=f'{result_data["name"]} - Median Asset Allocation Over Time',
                xaxis_title='Years',
                yaxis_title='Allocation (%)',
                hovermode='x unified',
                height=500,
                yaxis=dict(range=[0, 100])
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Show initial vs final allocation
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**Target Allocation:**")
                st.write(f"S&P 500: {target_mix['SP500']*100:.1f}%")
                st.write(f"NASDAQ 100: {target_mix['NASDAQ']*100:.1f}%")
                st.write(f"T-Bills: {target_mix['TBill']*100:.1f}%")
                st.write(f"HYSA: {target_mix['HYSA']*100:.1f}%")
            
            with col2:
                st.markdown("**Median Final Allocation (Year 15):**")
                st.write(f"S&P 500: {sp500_allocs[-1]:.1f}%")
                st.write(f"NASDAQ 100: {nasdaq_allocs[-1]:.1f}%")
                st.write(f"T-Bills: {tbill_allocs[-1]:.1f}%")
                st.write(f"HYSA: {hysa_allocs[-1]:.1f}%")
    
    # Sequence Analysis - Best and Worst Performing Sequences
    st.markdown("### Historical Sequence Analysis")
    st.markdown("**Which 15-year historical periods performed best and worst?**")
    
    # Analyze sequences for each portfolio
    for port_id, result_data in results.items():
        with st.expander(f"{result_data['name']} - Best & Worst Sequences"):
            data = result_data['data']
            final_values = data['final_values']
            sequence_indices = data['sequence_indices']
            baselines = data['baselines']
            
            # Calculate average final value for each sequence
            sequence_performance = {}
            for seq_idx in range(len(complete_sequences)):
                seq_mask = sequence_indices == seq_idx
                seq_finals = final_values[seq_mask]
                seq_baselines = baselines[seq_mask]
                
                if len(seq_finals) > 0:
                    sequence_performance[seq_idx] = {
                        'start_year': complete_sequences[seq_idx]['start_year'],
                        'end_year': complete_sequences[seq_idx]['end_year'],
                        'avg_final': np.mean(seq_finals),
                        'median_final': np.median(seq_finals),
                        'p10': np.percentile(seq_finals, 10),
                        'p25': np.percentile(seq_finals, 25),
                        'p75': np.percentile(seq_finals, 75),
                        'p90': np.percentile(seq_finals, 90),
                        'avg_baseline': np.mean(seq_baselines),
                        'beat_baseline_pct': np.sum(seq_finals > seq_baselines) / len(seq_finals) * 100
                    }
            
            # Sort by median final value (not average)
            sorted_sequences = sorted(sequence_performance.items(), key=lambda x: x[1]['median_final'], reverse=True)
            
            # Top 3 performing sequences
            st.markdown("**Top 3 Best Performing Sequences:**")
            top3_data = []
            for seq_idx, perf in sorted_sequences[:3]:
                top3_data.append({
                    'Period': f"{perf['start_year']}-{perf['end_year']}",
                    'Baseline': f"${perf['avg_baseline']:,.0f}",
                    'Median Final': f"${perf['median_final']:,.0f}",
                    '10th %ile': f"${perf['p10']:,.0f}",
                    '90th %ile': f"${perf['p90']:,.0f}",
                    'vs Baseline': f"+${perf['median_final'] - perf['avg_baseline']:,.0f}",
                    'Beat %': f"{perf['beat_baseline_pct']:.1f}%"
                })
            st.dataframe(pd.DataFrame(top3_data), use_container_width=True)
            
            # Bottom 3 performing sequences
            st.markdown("**Top 3 Worst Performing Sequences:**")
            bottom3_data = []
            for seq_idx, perf in sorted_sequences[-3:]:
                bottom3_data.append({
                    'Period': f"{perf['start_year']}-{perf['end_year']}",
                    'Baseline': f"${perf['avg_baseline']:,.0f}",
                    'Median Final': f"${perf['median_final']:,.0f}",
                    '10th %ile': f"${perf['p10']:,.0f}",
                    '90th %ile': f"${perf['p90']:,.0f}",
                    'vs Baseline': f"+${perf['median_final'] - perf['avg_baseline']:,.0f}",
                    'Beat %': f"{perf['beat_baseline_pct']:.1f}%"
                })
            st.dataframe(pd.DataFrame(bottom3_data), use_container_width=True)
    
    # Detailed statistics for each portfolio
    st.markdown("### Detailed Portfolio Statistics")
    
    tabs = st.tabs([result_data['name'] for result_data in results.values()])
    
    HYSA_monthly_returns = calculate_monthly_return(hysa_apy, 0)[0]
    
    for tab, (port_id, result_data) in zip(tabs, results.items()):
        with tab:
            data = result_data['data']
            final_values = data['final_values']
            baselines = data['baselines']
            
            # Calculate IRR
            with st.spinner("Calculating IRR..."):
                irr_data = calculate_all_irrs(
                    result_data['results'],
                    contribution_func,
                    HYSA_monthly_returns
                )
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Portfolio Statistics**")
                st.write(f"Mean IRR: {np.mean(irr_data['irr_returns']):.2f}%")
                st.write(f"Median IRR: {np.median(irr_data['irr_returns']):.2f}%")
                st.write(f"Std Dev IRR: {np.std(irr_data['irr_returns']):.2f}%")
                st.write(f"Min IRR: {np.min(irr_data['irr_returns']):.2f}%")
                st.write(f"Max IRR: {np.max(irr_data['irr_returns']):.2f}%")
            
            with col2:
                st.markdown("**Baseline Comparison**")
                st.write(f"Baseline IRR: {np.mean(irr_data['baseline_irr_returns']):.2f}%")
                st.write(f"IRR Advantage: {np.mean(irr_data['irr_returns']) - np.mean(irr_data['baseline_irr_returns']):.2f}%")
                beat_pct = np.sum(final_values > baselines) / len(final_values) * 100
                st.write(f"Beat Baseline: {beat_pct:.2f}%")
                st.write(f"Median Gain: ${np.median(final_values - baselines):,.0f}")
            

# Footer
st.markdown("---")
st.markdown("""
    <div style='text-align: center; color: #7f8c8d;'>
        <p>💡 This simulator uses historical market data (1926-2024) to model investment outcomes over 15 years.</p>
        <p>Monte Carlo simulation with adjustable volatility provides a range of possible futures.</p>
        <p><strong>Disclaimer:</strong> Past performance does not guarantee future results. This is for educational purposes only.</p>
    </div>
""", unsafe_allow_html=True)
