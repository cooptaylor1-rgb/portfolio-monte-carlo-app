"""
Adapter layer for new Monte Carlo engine.
Provides backward-compatible interface for existing API endpoints.
"""
from typing import Tuple, Optional, List, Dict
import pandas as pd
import numpy as np
from core.monte_carlo_engine import (
    PortfolioInputs as NewPortfolioInputs,
    SimulationResults,
    run_monte_carlo_simulation,
    SpendingRule as NewSpendingRule
)
import logging

logger = logging.getLogger(__name__)


def convert_old_inputs_to_new(old_inputs) -> NewPortfolioInputs:
    """
    Convert old PortfolioInputs dataclass to new engine format.
    
    Maps fields from legacy simulation.py to new monte_carlo_engine.py
    """
    # Map spending rule (old uses int, new uses enum)
    spending_rule_map = {
        1: NewSpendingRule.FIXED_REAL,
        2: NewSpendingRule.PERCENT_OF_PORTFOLIO
    }
    
    # Convert monthly values to match new engine's annual expectations
    return NewPortfolioInputs(
        starting_portfolio=old_inputs.starting_portfolio,
        years_to_model=old_inputs.years_to_model,
        current_age=old_inputs.current_age,
        
        # Convert monthly to annual for spending
        monthly_spending=abs(old_inputs.monthly_spending),  # New engine expects positive
        
        # Asset allocation (same)
        equity_pct=old_inputs.equity_pct,
        fi_pct=old_inputs.fi_pct,
        cash_pct=old_inputs.cash_pct,
        
        # Returns (same)
        equity_return_annual=old_inputs.equity_return_annual,
        fi_return_annual=old_inputs.fi_return_annual,
        cash_return_annual=old_inputs.cash_return_annual,
        
        # Volatility (same)
        equity_vol_annual=old_inputs.equity_vol_annual,
        fi_vol_annual=old_inputs.fi_vol_annual,
        cash_vol_annual=old_inputs.cash_vol_annual,
        
        # Inflation
        inflation_annual=old_inputs.inflation_annual,
        
        # Monte Carlo settings
        n_scenarios=old_inputs.n_scenarios,
        random_seed=None,  # Will be set separately
        
        # Spending rule
        spending_rule=spending_rule_map.get(old_inputs.spending_rule, NewSpendingRule.FIXED_REAL),
        spending_pct_annual=old_inputs.spending_pct_annual,
        
        # Income sources (convert monthly to annual)
        social_security_annual=old_inputs.social_security_monthly * 12,
        ss_start_age=old_inputs.ss_start_age,
        pension_annual=old_inputs.pension_monthly * 12,
        pension_start_age=old_inputs.pension_start_age,
        
        # Healthcare (convert monthly to annual)
        healthcare_annual=old_inputs.monthly_healthcare * 12,
        healthcare_start_age=old_inputs.healthcare_start_age,
        healthcare_inflation_real=old_inputs.healthcare_inflation - old_inputs.inflation_annual,
        
        # Tax accounts
        taxable_pct=old_inputs.taxable_pct,
        ira_pct=old_inputs.ira_pct,
        roth_pct=old_inputs.roth_pct,
        marginal_tax_rate=old_inputs.tax_rate,
        rmd_age=old_inputs.rmd_age,
        
        # Advanced features
        use_glide_path=old_inputs.use_glide_path,
        target_equity_at_end=old_inputs.target_equity_at_end,
        use_lifestyle_phases=old_inputs.use_lifestyle_phases,
        slow_go_age=old_inputs.slow_go_age,
        no_go_age=old_inputs.no_go_age,
        slow_go_spending_pct=old_inputs.slow_go_spending_pct,
        no_go_spending_pct=old_inputs.no_go_spending_pct,
        use_guardrails=old_inputs.use_guardrails,
        upper_guardrail=old_inputs.upper_guardrail,
        lower_guardrail=old_inputs.lower_guardrail
    )


def convert_results_to_legacy_format(
    results: SimulationResults,
    inputs: NewPortfolioInputs
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Convert new engine results to legacy format for backward compatibility.
    
    Returns:
        Tuple of (paths_df, stats_df) matching old engine format
    """
    # Convert paths array to DataFrame
    n_scenarios, n_months = results.paths.shape
    paths_df = pd.DataFrame(
        results.paths.T,  # Transpose to have months as rows
        columns=[f"scenario_{i}" for i in range(n_scenarios)]
    )
    paths_df.insert(0, 'month', range(n_months))
    
    # Use existing monthly_stats DataFrame from results
    stats_df = results.monthly_stats.copy()
    
    return paths_df, stats_df


def calculate_metrics(paths_df: pd.DataFrame, stats_df: pd.DataFrame) -> Dict:
    """
    Calculate metrics from simulation results.
    Maintains compatibility with old API while adding new metrics.
    """
    # Get ending values from last row
    ending_values = paths_df.iloc[-1, 1:].values  # Exclude 'month' column
    
    # Calculate traditional metrics
    success_count = np.sum(ending_values > 0)
    total_scenarios = len(ending_values)
    success_probability = success_count / total_scenarios
    
    # Depletion tracking
    depletion_count = total_scenarios - success_count
    depletion_probability = depletion_count / total_scenarios
    
    # Calculate years to depletion for failed scenarios
    years_depleted_list = []
    for col in paths_df.columns[1:]:  # Skip 'month' column
        scenario_values = paths_df[col].values
        if scenario_values[-1] == 0:  # Scenario failed
            # Find first month where value hit zero
            depletion_month = np.argmax(scenario_values == 0)
            if depletion_month > 0:
                years_depleted_list.append(depletion_month / 12)
    
    avg_years_depleted = np.mean(years_depleted_list) if years_depleted_list else 0.0
    
    # Percentiles from stats_df last row
    last_stats = stats_df.iloc[-1]
    
    return {
        "success_probability": success_probability,
        "ending_median": last_stats['median'],
        "ending_p10": last_stats['p10'],
        "ending_p90": last_stats['p90'],
        "years_depleted": avg_years_depleted,
        "depletion_probability": depletion_probability,
        "shortfall_risk": depletion_probability  # Alias
    }


def run_monte_carlo_adapted(
    inputs,
    seed: Optional[int] = None
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Adapter function that wraps new engine with old interface.
    
    This maintains backward compatibility with existing API code.
    """
    logger.info("Using NEW Monte Carlo engine (with adapter)")
    
    # Convert inputs
    new_inputs = convert_old_inputs_to_new(inputs)
    if seed is not None:
        new_inputs.random_seed = seed
    
    # Run new simulation
    results = run_monte_carlo_simulation(new_inputs)
    
    # Convert results to legacy format
    paths_df, stats_df = convert_results_to_legacy_format(results, new_inputs)
    
    # Store new metrics for later retrieval
    paths_df.attrs['new_engine_results'] = results
    
    return paths_df, stats_df


def calculate_goal_probabilities(
    paths_df: pd.DataFrame,
    goals: List[Dict],
    current_age: int
) -> List[Dict]:
    """
    Calculate probability of achieving financial goals.
    
    Maintains compatibility with old API.
    """
    goal_probs = []
    
    for goal in goals:
        target_amount = goal['target_amount']
        target_age = goal['target_age']
        
        # Calculate months to target age
        years_to_target = target_age - current_age
        months_to_target = years_to_target * 12
        
        # Get values at target month (if within simulation horizon)
        if 0 <= months_to_target < len(paths_df):
            values_at_target = paths_df.iloc[months_to_target, 1:].values
            achieved = np.sum(values_at_target >= target_amount)
            probability = achieved / len(values_at_target)
        else:
            probability = 0.0
        
        goal_probs.append({
            "name": goal['name'],
            "target_amount": target_amount,
            "target_age": target_age,
            "probability": probability
        })
    
    return goal_probs


def sensitivity_analysis(
    inputs,
    parameter: str,
    variations: List[float]
) -> pd.DataFrame:
    """
    Run sensitivity analysis by varying a parameter.
    
    Maintains compatibility with old API.
    """
    results = []
    
    for value in variations:
        # Create copy of inputs and modify parameter
        test_inputs = type(inputs)(**inputs.__dict__)
        setattr(test_inputs, parameter, value)
        
        # Run simulation
        paths_df, stats_df = run_monte_carlo_adapted(test_inputs)
        metrics = calculate_metrics(paths_df, stats_df)
        
        results.append({
            'parameter_value': value,
            'success_probability': metrics['success_probability'],
            'ending_median': metrics['ending_median'],
            'depletion_probability': metrics['depletion_probability']
        })
    
    return pd.DataFrame(results)


def get_new_engine_metrics(paths_df: pd.DataFrame) -> Optional[SimulationResults]:
    """
    Retrieve new engine metrics if available.
    
    This allows API endpoints to access new metrics like:
    - annual_ruin_probability
    - cumulative_ruin_probability  
    - longevity_metrics
    """
    return paths_df.attrs.get('new_engine_results')
