# -*- coding: utf-8 -*-
"""
Financial Simulation Library
Contains all core functions for running investment simulations
"""

import numpy as np
from scipy.optimize import newton

# Historical market returns data
market_returns = {
    'SP500': {
        1926: 11.62, 1927: 37.49, 1928: 43.61, 1929: -8.42, 1930: -24.90,
        1931: -43.34, 1932: -8.19, 1933: 53.99, 1934: -1.44, 1935: 47.67,
        1936: 33.92, 1937: -35.03, 1938: 31.12, 1939: -0.41, 1940: -9.78,
        1941: -11.59, 1942: 20.34, 1943: 25.90, 1944: 19.75, 1945: 36.44,
        1946: -8.07, 1947: 5.71, 1948: 5.50, 1949: 18.79, 1950: 31.71,
        1951: 24.02, 1952: 18.37, 1953: -0.99, 1954: 52.62, 1955: 31.56,
        1956: 6.56, 1957: -10.78, 1958: 43.36, 1959: 11.96, 1960: 0.47,
        1961: 26.89, 1962: -8.73, 1963: 22.80, 1964: 16.48, 1965: 12.45,
        1966: -10.06, 1967: 23.98, 1968: 11.06, 1969: -8.50, 1970: 4.01,
        1971: 14.31, 1972: 18.98, 1973: -14.66, 1974: -26.47, 1975: 37.20,
        1976: 23.84, 1977: -7.18, 1978: 6.56, 1979: 18.44, 1980: 32.42,
        1981: -4.91, 1982: 21.55, 1983: 22.56, 1984: 6.27, 1985: 31.73,
        1986: 18.67, 1987: 5.25, 1988: 16.61, 1989: 31.69, 1990: -3.10,
        1991: 30.47, 1992: 7.62, 1993: 10.08, 1994: 1.32, 1995: 37.58,
        1996: 22.96, 1997: 33.36, 1998: 28.58, 1999: 21.04, 2000: -9.10,
        2001: -11.89, 2002: -22.10, 2003: 28.68, 2004: 10.88, 2005: 4.91,
        2006: 15.79, 2007: 5.49, 2008: -37.00, 2009: 26.46, 2010: 15.06,
        2011: 2.11, 2012: 16.00, 2013: 32.39, 2014: 13.69, 2015: 1.38,
        2016: 11.96, 2017: 21.83, 2018: -4.38, 2019: 31.49, 2020: 18.40,
        2021: 28.71, 2022: -18.11, 2023: 26.29, 2024: 25.02
    },
    'NASDAQ100': {
        1986: 6.89, 1987: 10.50, 1988: 13.54, 1989: 26.17, 1990: -10.41,
        1991: 64.99, 1992: 8.87, 1993: 10.58, 1994: 1.50, 1995: 42.54,
        1996: 42.54, 1997: 20.63, 1998: 85.31, 1999: 101.95, 2000: -36.84,
        2001: -32.65, 2002: -37.58, 2003: 49.12, 2004: 10.44, 2005: 1.49,
        2006: 6.79, 2007: 18.67, 2008: -41.89, 2009: 53.54, 2010: 19.22,
        2011: 2.70, 2012: 16.82, 2013: 34.99, 2014: 17.94, 2015: 8.43,
        2016: 5.89, 2017: 31.52, 2018: -1.04, 2019: 37.96, 2020: 47.58,
        2021: 26.63, 2022: -32.97, 2023: 53.81, 2024: 24.88
    },
    'TBILL_3M': {
        1928: 3.08, 1929: 3.16, 1930: 4.55, 1931: 2.31, 1932: 1.07,
        1933: 0.96, 1934: 0.28, 1935: 0.17, 1936: 0.17, 1937: 0.28,
        1938: 0.07, 1939: 0.05, 1940: 0.04, 1941: 0.13, 1942: 0.34,
        1943: 0.38, 1944: 0.38, 1945: 0.38, 1946: 0.38, 1947: 0.60,
        1948: 1.05, 1949: 1.12, 1950: 1.20, 1951: 1.52, 1952: 1.72,
        1953: 1.89, 1954: 0.94, 1955: 1.72, 1956: 2.62, 1957: 3.22,
        1958: 1.77, 1959: 3.39, 1960: 2.87, 1961: 2.35, 1962: 2.77,
        1963: 3.16, 1964: 3.55, 1965: 3.95, 1966: 4.86, 1967: 4.29,
        1968: 5.34, 1969: 6.67, 1970: 6.39, 1971: 4.33, 1972: 4.06,
        1973: 7.04, 1974: 7.85, 1975: 5.79, 1976: 4.98, 1977: 5.26,
        1978: 7.18, 1979: 10.05, 1980: 11.39, 1981: 14.04, 1982: 10.60,
        1983: 8.62, 1984: 9.54, 1985: 7.47, 1986: 5.97, 1987: 5.78,
        1988: 6.67, 1989: 8.11, 1990: 7.50, 1991: 5.38, 1992: 3.43,
        1993: 3.00, 1994: 4.25, 1995: 5.49, 1996: 5.01, 1997: 5.06,
        1998: 4.78, 1999: 4.64, 2000: 5.82, 2001: 3.40, 2002: 1.61,
        2003: 1.01, 2004: 1.37, 2005: 3.15, 2006: 4.73, 2007: 4.36,
        2008: 1.37, 2009: 0.15, 2010: 0.14, 2011: 0.05, 2012: 0.09,
        2013: 0.06, 2014: 0.03, 2015: 0.05, 2016: 0.32, 2017: 0.93,
        2018: 1.94, 2019: 2.06, 2020: 0.35, 2021: 0.05, 2022: 2.02,
        2023: 5.07, 2024: 4.97
    }
}


def calculate_irr(cash_flows, times):
    """
    Calculate Internal Rate of Return (IRR) given cash flows and their timing.
    """
    def npv(rate):
        return sum(cf / (1 + rate) ** t for cf, t in zip(cash_flows, times))

    def npv_derivative(rate):
        return sum(-t * cf / (1 + rate) ** (t + 1) for cf, t in zip(cash_flows, times))

    try:
        irr = newton(npv, 0.05, fprime=npv_derivative, maxiter=100)
        return irr
    except:
        return np.nan


def extract_simulation_data(simulation_results):
    """
    Extract key data arrays from simulation results.
    """
    final_values = []
    all_timeseries = []
    baselines = []
    sequence_indices = []

    for i, result_dict in enumerate(simulation_results['result_dict']):
        final_total = (result_dict['SP500'][-1] +
                       result_dict['NASDAQ100'][-1] +
                       result_dict['TBILL_3M'][-1] +
                       result_dict['HYSA'][-1] +
                       result_dict['Emergency_fund'][-1])
        final_values.append(final_total)
        baselines.append(result_dict['Baseline'][-1])
        sequence_indices.append(simulation_results['sequence_index'][i])

        timeseries = []
        for j in range(len(result_dict['Month_Index'])):
            total = (result_dict['SP500'][j] +
                     result_dict['NASDAQ100'][j] +
                     result_dict['TBILL_3M'][j] +
                     result_dict['HYSA'][j] +
                     result_dict['Emergency_fund'][j])
            timeseries.append(total)
        all_timeseries.append(timeseries)

    return {
        'final_values': np.array(final_values),
        'baselines': np.array(baselines),
        'all_timeseries': all_timeseries,
        'sequence_indices': np.array(sequence_indices)
    }


def calculate_all_irrs(simulation_results, contribution_function, HYSA_monthly_returns):
    """
    Calculate IRR for all simulations (both portfolio and baseline).
    
    Parameters:
    -----------
    contribution_function : callable
        Function that takes month number and returns contribution amount
    """
    irr_returns = []
    baseline_irr_returns = []

    for idx, result_dict in enumerate(simulation_results['result_dict']):
        # Build cash flow list for portfolio
        cash_flows = []
        times = []

        initial = (result_dict['SP500'][0] +
                  result_dict['NASDAQ100'][0] +
                  result_dict['TBILL_3M'][0] +
                  result_dict['HYSA'][0] +
                  result_dict['Emergency_fund'][0])
        cash_flows.append(-initial)
        times.append(0)

        total_months = len(result_dict['Month_Index']) - 1
        for month_idx in range(1, total_months + 1):
            month = month_idx - 1
            contribution = contribution_function(month)
            cash_flows.append(-contribution)
            times.append(month_idx / 12)

        final = (result_dict['SP500'][-1] +
                result_dict['NASDAQ100'][-1] +
                result_dict['TBILL_3M'][-1] +
                result_dict['HYSA'][-1] +
                result_dict['Emergency_fund'][-1])
        cash_flows.append(final)
        times.append(15)

        irr = calculate_irr(cash_flows, times)
        if not np.isnan(irr):
            irr_returns.append(irr * 100)

        # Build cash flow list for baseline
        baseline_cash_flows = []
        baseline_times = []

        baseline_initial = result_dict['Baseline'][0]
        baseline_cash_flows.append(-baseline_initial)
        baseline_times.append(0)

        for month_idx in range(1, total_months + 1):
            prev_baseline = result_dict['Baseline'][month_idx - 1]
            curr_baseline = result_dict['Baseline'][month_idx]
            baseline_contribution = (curr_baseline / (1 + HYSA_monthly_returns)) - prev_baseline
            baseline_cash_flows.append(-baseline_contribution)
            baseline_times.append(month_idx / 12)

        baseline_final = result_dict['Baseline'][-1]
        baseline_cash_flows.append(baseline_final)
        baseline_times.append(15)

        baseline_irr = calculate_irr(baseline_cash_flows, baseline_times)
        if not np.isnan(baseline_irr):
            baseline_irr_returns.append(baseline_irr * 100)

    return {
        'irr_returns': np.array(irr_returns),
        'baseline_irr_returns': np.array(baseline_irr_returns)
    }


def calculate_milestone_statistics(simulation_results, year):
    """
    Calculate statistics at a specific year milestone.
    """
    month_index = year * 12

    milestone_values = []
    milestone_baselines = []

    for result_dict in simulation_results['result_dict']:
        if len(result_dict['Month_Index']) > month_index:
            total = (result_dict['SP500'][month_index] +
                    result_dict['NASDAQ100'][month_index] +
                    result_dict['TBILL_3M'][month_index] +
                    result_dict['HYSA'][month_index] +
                    result_dict['Emergency_fund'][month_index])
            milestone_values.append(total)
            milestone_baselines.append(result_dict['Baseline'][month_index])

    milestone_values = np.array(milestone_values)
    milestone_baselines = np.array(milestone_baselines)

    return {
        'p25': np.percentile(milestone_values, 25),
        'p50': np.percentile(milestone_values, 50),
        'p75': np.percentile(milestone_values, 75),
        'avg_baseline': np.mean(milestone_baselines),
        'beat_baseline_pct': np.sum(milestone_values > milestone_baselines) / len(milestone_values) * 100,
        'median_gain': np.percentile(milestone_values, 50) - np.mean(milestone_baselines)
    }


def calculate_fund_returns(simulation_results, contribution_function, investment_mix):
    """
    Calculate annualized returns for each individual fund.
    
    Parameters:
    -----------
    contribution_function : callable
        Function that takes month number and returns contribution amount
    """
    sp500_returns = []
    nasdaq_returns = []
    tbill_returns = []
    hysa_returns = []
    emergency_returns = []

    for idx, result_dict in enumerate(simulation_results['result_dict']):
        total_months = len(result_dict['Month_Index']) - 1
        total_contribution = 0
        for month in range(total_months):
            total_contribution += contribution_function(month)

        # S&P 500
        sp500_initial = result_dict['SP500'][0]
        sp500_final = result_dict['SP500'][-1]
        sp500_contributions = total_contribution * investment_mix['SP500']
        sp500_total_invested = sp500_initial + sp500_contributions
        if sp500_total_invested > 0:
            sp500_return = ((sp500_final / sp500_total_invested) ** (1/15) - 1) * 100
            sp500_returns.append(sp500_return)

        # NASDAQ 100
        nasdaq_initial = result_dict['NASDAQ100'][0]
        nasdaq_final = result_dict['NASDAQ100'][-1]
        nasdaq_contributions = total_contribution * investment_mix['NASDAQ']
        nasdaq_total_invested = nasdaq_initial + nasdaq_contributions
        if nasdaq_total_invested > 0:
            nasdaq_return = ((nasdaq_final / nasdaq_total_invested) ** (1/15) - 1) * 100
            nasdaq_returns.append(nasdaq_return)

        # T-Bills
        tbill_initial = result_dict['TBILL_3M'][0]
        tbill_final = result_dict['TBILL_3M'][-1]
        tbill_contributions = total_contribution * investment_mix['TBill']
        tbill_total_invested = tbill_initial + tbill_contributions
        if tbill_total_invested > 0:
            tbill_return = ((tbill_final / tbill_total_invested) ** (1/15) - 1) * 100
            tbill_returns.append(tbill_return)

        # HYSA
        hysa_initial = result_dict['HYSA'][0]
        hysa_final = result_dict['HYSA'][-1]
        hysa_contributions = total_contribution * investment_mix['HYSA']
        hysa_total_invested = hysa_initial + hysa_contributions
        if hysa_total_invested > 0:
            hysa_return = ((hysa_final / hysa_total_invested) ** (1/15) - 1) * 100
            hysa_returns.append(hysa_return)

        # Emergency Fund
        emergency_initial = result_dict['Emergency_fund'][0]
        emergency_final = result_dict['Emergency_fund'][-1]
        if emergency_initial > 0:
            emergency_return = ((emergency_final / emergency_initial) ** (1/15) - 1) * 100
            emergency_returns.append(emergency_return)

    return {
        'SP500': np.array(sp500_returns),
        'NASDAQ100': np.array(nasdaq_returns),
        'TBILL_3M': np.array(tbill_returns),
        'HYSA': np.array(hysa_returns),
        'Emergency_fund': np.array(emergency_returns)
    }


def calculate_monthly_return(yearly_return, std):
    """
    Get the monthly return from the annual return with noise for realism.
    """
    avg_monthly_return = (1 + yearly_return)**(1/12) - 1
    actual_monthly_return = []
    for i in range(0, 12):
        actual_return = avg_monthly_return + np.random.normal(0, std)
        actual_monthly_return.append(actual_return)
    return actual_monthly_return


def get_15_year_sequences(market_returns):
    """
    Get all unique 15-year sequences from the market returns data.
    """
    sequences = []

    sp500_years = sorted(market_returns['SP500'].keys())
    nasdaq_years = sorted(market_returns['NASDAQ100'].keys())
    tbill_years = sorted(market_returns['TBILL_3M'].keys())

    earliest_year = min(sp500_years[0], nasdaq_years[0], tbill_years[0])
    latest_year = max(sp500_years[-1], nasdaq_years[-1], tbill_years[-1])

    for start_year in range(earliest_year, latest_year - 14):
        end_year = start_year + 14

        sequence = {
            'start_year': start_year,
            'end_year': end_year,
            'SP500': [],
            'NASDAQ100': [],
            'TBILL_3M': []
        }

        has_sp500 = all(year in sp500_years for year in range(start_year, end_year + 1))
        has_nasdaq = all(year in nasdaq_years for year in range(start_year, end_year + 1))
        has_tbill = all(year in tbill_years for year in range(start_year, end_year + 1))

        if has_sp500:
            sequence['SP500'] = [market_returns['SP500'][year] for year in range(start_year, end_year + 1)]
        else:
            sequence['SP500'] = None

        if has_nasdaq:
            sequence['NASDAQ100'] = [market_returns['NASDAQ100'][year] for year in range(start_year, end_year + 1)]
        else:
            sequence['NASDAQ100'] = None

        if has_tbill:
            sequence['TBILL_3M'] = [market_returns['TBILL_3M'][year] for year in range(start_year, end_year + 1)]
        else:
            sequence['TBILL_3M'] = None

        sequences.append(sequence)

    return sequences


def run_investment_simulation(investment_mix, investment_start, emergency_fund_start,
                               complete_sequences, total_iterations,
                               hysa_apy, SP500_std, NASDAQ_std, T_Bills_std,
                               contribution_function,
                               enable_rebalancing=False,
                               rebalancing_threshold=0.05,
                               simulation_name="Investment Simulation"):
    """
    Run a complete investment simulation with a given investment mix.
    
    Parameters:
    -----------
    contribution_function : callable
        Function that takes month number and returns contribution amount
    enable_rebalancing : bool
        If True, rebalance contribution allocations quarterly to maintain target mix
    rebalancing_threshold : float
        Decimal threshold for triggering rebalancing (e.g., 0.05 for 5%)
    """
    simulation_results = {
        'iteration': [],
        'sequence_index': [],
        'sequence_start_year': [],
        'sequence_end_year': [],
        'result_dict': [],
        'simulation_name': simulation_name,
        'investment_mix': investment_mix
    }

    HYSA_monthly_returns = calculate_monthly_return(hysa_apy, 0)[0]
    
    # Store target allocation
    target_mix = {
        'SP500': investment_mix['SP500'],
        'NASDAQ': investment_mix['NASDAQ'],
        'TBill': investment_mix['TBill'],
        'HYSA': investment_mix['HYSA']
    }

    for seq_idx, seq in enumerate(complete_sequences):
        for iteration in range(0, total_iterations):
            investment_breakdown = {
                'Month_Index': [0],
                'SP500': [investment_start * investment_mix['SP500']],
                'NASDAQ100': [investment_start * investment_mix['NASDAQ']],
                'TBILL_3M': [investment_start * investment_mix['TBill']],
                'HYSA': [investment_start * investment_mix['HYSA']],
                'Emergency_fund': [emergency_fund_start],
                'Baseline': [investment_start + emergency_fund_start]
            }
            
            # Current contribution allocation (starts at target)
            current_mix = target_mix.copy()

            for year_idx in range(15):
                sp500_monthly_returns = calculate_monthly_return(seq['SP500'][year_idx]/100, SP500_std)
                nasdaq_monthly_returns = calculate_monthly_return(seq['NASDAQ100'][year_idx]/100, NASDAQ_std)
                TBILL_3M_monthly_returns = calculate_monthly_return(seq['TBILL_3M'][year_idx]/100, T_Bills_std)

                for month_idx in range(12):
                    current_month = investment_breakdown['Month_Index'][-1]
                    
                    # Check for quarterly rebalancing (months 3, 6, 9, 12, 15, etc.)
                    if enable_rebalancing and current_month > 0 and current_month % 3 == 0:
                        # Calculate current allocation percentages
                        total_value = (investment_breakdown['SP500'][-1] +
                                      investment_breakdown['NASDAQ100'][-1] +
                                      investment_breakdown['TBILL_3M'][-1] +
                                      investment_breakdown['HYSA'][-1])
                        
                        if total_value > 0:
                            current_allocation = {
                                'SP500': investment_breakdown['SP500'][-1] / total_value,
                                'NASDAQ': investment_breakdown['NASDAQ100'][-1] / total_value,
                                'TBill': investment_breakdown['TBILL_3M'][-1] / total_value,
                                'HYSA': investment_breakdown['HYSA'][-1] / total_value
                            }
                            
                            # Check if any asset is >threshold off target
                            needs_rebalancing = False
                            for asset in ['SP500', 'NASDAQ', 'TBill', 'HYSA']:
                                diff = abs(current_allocation[asset] - target_mix[asset])
                                if diff > rebalancing_threshold:
                                    needs_rebalancing = True
                                    break
                            
                            if needs_rebalancing:
                                # Calculate adjustment: allocate more to under-weighted assets
                                # and less to over-weighted assets
                                adjustments = {}
                                for asset in ['SP500', 'NASDAQ', 'TBill', 'HYSA']:
                                    # Difference from target (positive = over-allocated)
                                    diff = current_allocation[asset] - target_mix[asset]
                                    # Invert: negative diff means we should allocate MORE
                                    adjustments[asset] = -diff
                                
                                # Normalize adjustments to sum to 1.0
                                total_adjustment = sum(max(0, adj) for adj in adjustments.values())
                                if total_adjustment > 0:
                                    current_mix = {}
                                    for asset in ['SP500', 'NASDAQ', 'TBill', 'HYSA']:
                                        # Assets that are under-allocated get more contribution
                                        if adjustments[asset] > 0:
                                            current_mix[asset] = target_mix[asset] + (adjustments[asset] / total_adjustment) * 0.5
                                        else:
                                            current_mix[asset] = target_mix[asset] + (adjustments[asset] / total_adjustment) * 0.5
                                    
                                    # Ensure sum to 1.0
                                    total_mix = sum(current_mix.values())
                                    if total_mix > 0:
                                        for asset in current_mix:
                                            current_mix[asset] = current_mix[asset] / total_mix
                    
                    contribution = contribution_function(current_month)

                    sp500_contribution = contribution * current_mix['SP500']
                    nasdaq_contribution = contribution * current_mix['NASDAQ']
                    tbill_contribution = contribution * current_mix['TBill']
                    hysa_contribution = contribution * current_mix['HYSA']

                    investment_breakdown['Month_Index'].append(current_month + 1)

                    new_sp500 = (investment_breakdown['SP500'][-1] + sp500_contribution) * (1 + sp500_monthly_returns[month_idx])
                    new_nasdaq = (investment_breakdown['NASDAQ100'][-1] + nasdaq_contribution) * (1 + nasdaq_monthly_returns[month_idx])
                    new_tbill = (investment_breakdown['TBILL_3M'][-1] + tbill_contribution) * (1 + TBILL_3M_monthly_returns[month_idx])
                    new_hysa = (investment_breakdown['HYSA'][-1] + hysa_contribution) * (1 + HYSA_monthly_returns)
                    new_baseline = (investment_breakdown['Baseline'][-1] + contribution) * (1 + HYSA_monthly_returns)

                    investment_breakdown['SP500'].append(new_sp500)
                    investment_breakdown['NASDAQ100'].append(new_nasdaq)
                    investment_breakdown['TBILL_3M'].append(new_tbill)
                    investment_breakdown['HYSA'].append(new_hysa)
                    investment_breakdown['Emergency_fund'].append(investment_breakdown['Emergency_fund'][-1] * (1 + HYSA_monthly_returns))
                    investment_breakdown['Baseline'].append(new_baseline)

            simulation_results['iteration'].append(iteration)
            simulation_results['sequence_index'].append(seq_idx)
            simulation_results['sequence_start_year'].append(seq['start_year'])
            simulation_results['sequence_end_year'].append(seq['end_year'])
            simulation_results['result_dict'].append(investment_breakdown)

    return simulation_results
