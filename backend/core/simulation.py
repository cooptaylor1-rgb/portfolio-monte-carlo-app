"""
Core Monte Carlo simulation engine.
Pure Python logic with no UI dependencies - all calculations only.
"""
import numpy as np
import pandas as pd
from typing import Tuple, List, Optional
from dataclasses import dataclass


@dataclass
class PortfolioInputs:
    """Core simulation parameters (dataclass for internal use)"""
    starting_portfolio: float
    years_to_model: int
    current_age: int
    monthly_income: float
    monthly_spending: float
    inflation_annual: float
    
    equity_pct: float
    fi_pct: float
    cash_pct: float
    
    equity_return_annual: float
    fi_return_annual: float
    cash_return_annual: float
    
    equity_vol_annual: float
    fi_vol_annual: float
    cash_vol_annual: float
    
    n_scenarios: int
    spending_rule: int = 1
    spending_pct_annual: float = 0.04
    
    # Income sources
    social_security_monthly: float = 0.0
    ss_start_age: int = 67
    pension_monthly: float = 0.0
    pension_start_age: int = 65
    
    # Healthcare
    monthly_healthcare: float = 0.0
    healthcare_start_age: int = 65
    healthcare_inflation: float = 0.05
    
    # Tax accounts
    taxable_pct: float = 0.33
    ira_pct: float = 0.50
    roth_pct: float = 0.17
    tax_rate: float = 0.25
    rmd_age: int = 73
    
    # Advanced features
    use_glide_path: bool = False
    target_equity_at_end: float = 0.40
    use_lifestyle_phases: bool = False
    slow_go_age: int = 75
    no_go_age: int = 85
    slow_go_spending_pct: float = 0.80
    no_go_spending_pct: float = 0.60
    use_guardrails: bool = False
    upper_guardrail: float = 0.20
    lower_guardrail: float = 0.15


def compute_portfolio_return_and_vol(inputs: PortfolioInputs) -> Tuple[float, float]:
    """
    Calculate weighted portfolio expected return and volatility.
    
    Args:
        inputs: Portfolio configuration
        
    Returns:
        Tuple of (expected_annual_return, annual_volatility)
    """
    # Weighted expected return
    exp_return = (
        inputs.equity_pct * inputs.equity_return_annual +
        inputs.fi_pct * inputs.fi_return_annual +
        inputs.cash_pct * inputs.cash_return_annual
    )
    
    # Simplified portfolio volatility (assumes correlations)
    # For more accurate results, would use covariance matrix
    vol = np.sqrt(
        (inputs.equity_pct * inputs.equity_vol_annual) ** 2 +
        (inputs.fi_pct * inputs.fi_vol_annual) ** 2 +
        (inputs.cash_pct * inputs.cash_vol_annual) ** 2
    )
    
    return exp_return, vol


def run_monte_carlo(inputs: PortfolioInputs, seed: Optional[int] = None) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Run Monte Carlo simulation for portfolio projections.
    
    Args:
        inputs: Simulation parameters
        seed: Random seed for reproducibility
        
    Returns:
        Tuple of (paths_df, stats_df) where:
            - paths_df contains all scenario paths
            - stats_df contains monthly statistics (median, percentiles)
    """
    if seed is not None:
        np.random.seed(seed)
    
    exp_annual, vol_annual = compute_portfolio_return_and_vol(inputs)
    
    # Convert to monthly
    months = inputs.years_to_model * 12
    exp_monthly = exp_annual / 12.0
    vol_monthly = vol_annual / np.sqrt(12.0)
    inflation_monthly = inputs.inflation_annual / 12.0
    
    # Initialize arrays
    n_scenarios = inputs.n_scenarios
    paths = np.zeros((n_scenarios, months + 1))
    paths[:, 0] = inputs.starting_portfolio
    
    # Initialize spending
    current_spending = abs(inputs.monthly_spending)
    
    # Calculate income sources by age
    current_month_age = inputs.current_age * 12
    ss_start_month = inputs.ss_start_age * 12
    pension_start_month = inputs.pension_start_age * 12
    healthcare_start_month = inputs.healthcare_start_age * 12
    
    for month in range(1, months + 1):
        # Calculate age for this month
        age_months = current_month_age + month
        current_year = month / 12.0
        
        # Generate random returns for all scenarios
        returns = np.random.normal(exp_monthly, vol_monthly, n_scenarios)
        
        # Apply returns
        paths[:, month] = paths[:, month - 1] * (1 + returns)
        
        # Adjust spending for inflation
        inflated_spending = current_spending * ((1 + inflation_monthly) ** month)
        
        # Add income if applicable
        income = 0.0
        if age_months >= ss_start_month:
            income += inputs.social_security_monthly
        if age_months >= pension_start_month:
            income += inputs.pension_monthly
        
        # Add healthcare costs if applicable
        healthcare_cost = 0.0
        if age_months >= healthcare_start_month:
            months_since_healthcare = month - (healthcare_start_month - current_month_age)
            healthcare_monthly_inflation = inputs.healthcare_inflation / 12.0
            healthcare_cost = inputs.monthly_healthcare * ((1 + healthcare_monthly_inflation) ** months_since_healthcare)
        
        # Net spending
        if inputs.spending_rule == 1:
            # Fixed dollar
            net_spending = inflated_spending + healthcare_cost - income
        else:
            # Percentage of portfolio
            net_spending = paths[:, month - 1] * (inputs.spending_pct_annual / 12.0) + healthcare_cost - income
        
        # Apply glide path if enabled
        if inputs.use_glide_path:
            progress = month / months
            current_equity_pct = inputs.equity_pct + (inputs.target_equity_at_end - inputs.equity_pct) * progress
            # Recalculate returns based on new allocation (simplified)
            exp_annual_adjusted = (
                current_equity_pct * inputs.equity_return_annual +
                (1 - current_equity_pct) * inputs.fi_return_annual
            )
            exp_monthly_adjusted = exp_annual_adjusted / 12.0
            returns = np.random.normal(exp_monthly_adjusted, vol_monthly, n_scenarios)
            paths[:, month] = paths[:, month - 1] * (1 + returns)
        
        # Apply lifestyle phases if enabled
        if inputs.use_lifestyle_phases:
            age_years = age_months / 12.0
            if age_years >= inputs.no_go_age:
                inflated_spending *= inputs.no_go_spending_pct
            elif age_years >= inputs.slow_go_age:
                inflated_spending *= inputs.slow_go_spending_pct
        
        # Subtract net spending
        paths[:, month] = paths[:, month] - net_spending
        
        # Apply guardrails if enabled
        if inputs.use_guardrails and month > 12:
            # Check if portfolio value deviated significantly
            for i in range(n_scenarios):
                if paths[i, month] > paths[i, 0] * (1 + inputs.upper_guardrail):
                    # Increase spending
                    net_spending *= 1.05
                elif paths[i, month] < paths[i, 0] * (1 - inputs.lower_guardrail):
                    # Decrease spending
                    net_spending *= 0.95
        
        # Floor at zero (can't go negative)
        paths[:, month] = np.maximum(paths[:, month], 0)
    
    # Create paths DataFrame
    months_array = np.arange(months + 1)
    paths_df = pd.DataFrame(paths.T, columns=[f"Scenario_{i}" for i in range(n_scenarios)])
    paths_df["Month"] = months_array
    
    # Calculate statistics
    stats_df = pd.DataFrame({
        "Month": months_array,
        "Median": np.median(paths, axis=0),
        "P10": np.percentile(paths, 10, axis=0),
        "P25": np.percentile(paths, 25, axis=0),
        "P75": np.percentile(paths, 75, axis=0),
        "P90": np.percentile(paths, 90, axis=0),
        "Mean": np.mean(paths, axis=0),
        "StdDev": np.std(paths, axis=0)
    })
    
    return paths_df, stats_df


def calculate_metrics(paths_df: pd.DataFrame, stats_df: pd.DataFrame) -> dict:
    """
    Calculate key portfolio metrics from simulation results.
    
    Args:
        paths_df: DataFrame with all scenario paths
        stats_df: DataFrame with monthly statistics
        
    Returns:
        Dictionary of key metrics
    """
    # Get final values
    final_values = paths_df.iloc[-1, :-1].values  # Exclude Month column
    
    # Success probability (ending value > 0)
    success_prob = np.mean(final_values > 0)
    
    # Depletion analysis
    scenario_cols = [col for col in paths_df.columns if col.startswith("Scenario_")]
    depleted_count = 0
    years_to_depletion = []
    
    for col in scenario_cols:
        values = paths_df[col].values
        depletion_months = np.where(values <= 0)[0]
        if len(depletion_months) > 0:
            depleted_count += 1
            years_to_depletion.append(depletion_months[0] / 12.0)
    
    depletion_prob = depleted_count / len(scenario_cols)
    avg_years_depleted = np.mean(years_to_depletion) if years_to_depletion else 0
    
    # Ending values
    ending_median = stats_df["Median"].iloc[-1]
    ending_p10 = stats_df["P10"].iloc[-1]
    ending_p90 = stats_df["P90"].iloc[-1]
    
    # Shortfall risk (scenarios ending below 50% of starting value)
    starting_value = paths_df.iloc[0, 0]
    shortfall_threshold = starting_value * 0.5
    shortfall_risk = np.mean(final_values < shortfall_threshold)
    
    return {
        "success_probability": float(success_prob),
        "ending_median": float(ending_median),
        "ending_p10": float(ending_p10),
        "ending_p90": float(ending_p90),
        "depletion_probability": float(depletion_prob),
        "years_depleted": float(avg_years_depleted),
        "shortfall_risk": float(shortfall_risk)
    }


def calculate_goal_probabilities(
    paths_df: pd.DataFrame,
    goals: List[dict],
    current_age: int
) -> List[dict]:
    """
    Calculate probability of achieving each financial goal.
    
    Args:
        paths_df: DataFrame with all scenario paths
        goals: List of goal dictionaries with name, target_amount, target_age
        current_age: Client's current age
        
    Returns:
        List of dictionaries with goal achievement probabilities
    """
    results = []
    scenario_cols = [col for col in paths_df.columns if col.startswith("Scenario_")]
    
    for goal in goals:
        target_age = goal.get("target_age", 0)
        target_amount = goal.get("target_amount", 0)
        goal_name = goal.get("name", "Goal")
        
        # Calculate month index
        years_from_now = target_age - current_age
        if years_from_now < 0:
            continue
        
        month_index = min(years_from_now * 12, len(paths_df) - 1)
        
        # Get values at that month
        values_at_goal = paths_df.iloc[month_index][scenario_cols].values
        
        # Calculate probability
        prob = np.mean(values_at_goal >= target_amount)
        
        results.append({
            "goal_name": goal_name,
            "target_amount": target_amount,
            "target_age": target_age,
            "probability": float(prob),
            "median_value": float(np.median(values_at_goal))
        })
    
    return results


def sensitivity_analysis(inputs: PortfolioInputs, parameter: str, variations: List[float]) -> pd.DataFrame:
    """
    Run sensitivity analysis on a specific parameter.
    
    Args:
        inputs: Base simulation parameters
        parameter: Parameter name to vary
        variations: List of values to test
        
    Returns:
        DataFrame with sensitivity results
    """
    results = []
    
    for value in variations:
        # Create modified inputs
        modified_inputs = PortfolioInputs(**inputs.__dict__)
        setattr(modified_inputs, parameter, value)
        
        # Run simulation
        paths_df, stats_df = run_monte_carlo(modified_inputs)
        metrics = calculate_metrics(paths_df, stats_df)
        
        results.append({
            "parameter_value": value,
            "success_probability": metrics["success_probability"],
            "ending_median": metrics["ending_median"],
            "depletion_probability": metrics["depletion_probability"]
        })
    
    return pd.DataFrame(results)
