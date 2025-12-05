"""
Monte Carlo Simulation Engine - Refactored for Mathematical Rigor
==================================================================

This module implements a Monte Carlo simulation engine for retirement portfolio analysis
with a focus on:
1. Correct stochastic modeling (geometric Brownian motion)
2. Conservative risk assessment
3. Proper handling of all cash flows and fees
4. Accurate longevity and ruin probability calculations

MODEL ASSUMPTIONS:
-----------------
- Returns follow geometric Brownian motion (lognormal distribution)
- Operates in REAL (inflation-adjusted) terms by default
- Monthly timesteps for accuracy in cash flow timing
- Fees and taxes applied correctly per period
- Conservative approach: slightly understate success when uncertain

MATHEMATICAL FRAMEWORK:
----------------------
Portfolio value follows: dS/S = μdt + σdW
where:
- μ = drift (expected real return)
- σ = volatility
- dW = Wiener process (Brownian motion)

Discretized for monthly steps:
R(t) = exp((μ - σ²/2)Δt + σ√Δt·Z)
where Z ~ N(0,1)

The (μ - σ²/2) term is the DRIFT ADJUSTMENT for lognormal distributions.
"""

import numpy as np
import pandas as pd
from typing import Tuple, List, Optional, Dict, Any
from dataclasses import dataclass, field
from enum import IntEnum
import logging

logger = logging.getLogger(__name__)


class SpendingRule(IntEnum):
    """Spending withdrawal strategies"""
    FIXED_REAL = 1      # Fixed dollar amount, inflation-adjusted
    PERCENT_OF_PORTFOLIO = 2    # Dynamic % of current portfolio
    HYBRID_FLOOR_CEILING = 3    # % with floor and ceiling


@dataclass
class PortfolioInputs:
    """
    Core simulation parameters with validation and defaults.
    
    All monetary values in dollars.
    All rates as decimals (e.g., 0.05 for 5%).
    All periods in years unless specified.
    """
    # Portfolio basics
    starting_portfolio: float
    years_to_model: int
    current_age: int
    
    # Cash flows (monthly, in REAL dollars at time 0)
    monthly_income: float = 0.0          # Pre-retirement salary (after-tax)
    monthly_spending: float = 0.0        # Living expenses (positive value)
    inflation_annual: float = 0.03       # Expected inflation rate
    
    # Asset allocation (must sum to 1.0)
    equity_pct: float = 0.60
    fi_pct: float = 0.30
    cash_pct: float = 0.10
    
    # Expected REAL returns (after inflation)
    equity_return_annual: float = 0.07    # Real equity return
    fi_return_annual: float = 0.02        # Real fixed income return
    cash_return_annual: float = 0.0       # Real cash return (≈ 0)
    
    # Volatilities (annual standard deviation)
    equity_vol_annual: float = 0.18
    fi_vol_annual: float = 0.06
    cash_vol_annual: float = 0.01
    
    # Correlations (for portfolio volatility calculation)
    corr_equity_fi: float = 0.20
    corr_equity_cash: float = 0.05
    corr_fi_cash: float = 0.10
    
    # Simulation settings
    n_scenarios: int = 1000
    random_seed: Optional[int] = None
    
    # Spending strategy
    spending_rule: SpendingRule = SpendingRule.FIXED_REAL
    spending_pct_annual: float = 0.04     # For % rule
    spending_floor: float = 30000.0       # Minimum annual spending (real)
    spending_ceiling: float = 150000.0    # Maximum annual spending (real)
    
    # Income sources (in REAL dollars)
    social_security_annual: float = 0.0
    ss_start_age: int = 67
    pension_annual: float = 0.0
    pension_start_age: int = 65
    pension_cola: float = 0.0             # Pension inflation adjustment
    
    # Healthcare costs (tends to exceed general inflation)
    healthcare_annual: float = 0.0
    healthcare_start_age: int = 65
    healthcare_inflation_real: float = 0.02  # Excess over general inflation
    
    # Fees and expenses (annual rates)
    advisory_fee_pct: float = 0.0075      # 75 bps
    fund_expense_pct: float = 0.0025      # 25 bps
    
    # Tax structure
    taxable_pct: float = 0.33
    ira_pct: float = 0.50
    roth_pct: float = 0.17
    marginal_tax_rate: float = 0.25
    ltcg_tax_rate: float = 0.15           # Long-term capital gains
    rmd_age: int = 73
    
    # RMD table (simplified - IRS Uniform Lifetime Table)
    rmd_factors: Dict[int, float] = field(default_factory=lambda: {
        73: 26.5, 74: 25.5, 75: 24.6, 76: 23.7, 77: 22.9,
        78: 22.0, 79: 21.1, 80: 20.2, 81: 19.4, 82: 18.5,
        83: 17.7, 84: 16.8, 85: 16.0, 86: 15.2, 87: 14.4,
        88: 13.7, 89: 12.9, 90: 12.2, 91: 11.5, 92: 10.8,
        93: 10.1, 94: 9.5, 95: 8.9, 96: 8.4, 97: 7.8,
        98: 7.3, 99: 6.8, 100: 6.4
    })
    
    # Dynamic allocation (glide path)
    use_glide_path: bool = False
    target_equity_at_end: float = 0.40
    glide_path_type: str = "linear"      # "linear" or "exponential"
    
    # Lifestyle spending phases (go-go, slow-go, no-go)
    use_lifestyle_phases: bool = False
    slow_go_age: int = 75
    no_go_age: int = 85
    slow_go_spending_pct: float = 0.85   # 85% of baseline
    no_go_spending_pct: float = 0.65     # 65% of baseline
    
    # Guardrails (for dynamic spending adjustment)
    use_guardrails: bool = False
    upper_guardrail: float = 0.20        # Increase spending if up 20%
    lower_guardrail: float = 0.15        # Decrease spending if down 15%
    guardrail_adjustment: float = 0.10   # Adjust by 10%
    
    def __post_init__(self):
        """Validate inputs after initialization"""
        self._validate_inputs()
    
    def _validate_inputs(self):
        """Validate all input parameters for correctness"""
        # Portfolio must be positive
        if self.starting_portfolio <= 0:
            raise ValueError(f"Starting portfolio must be positive, got {self.starting_portfolio}")
        
        # Allocation must sum to 1.0
        total_alloc = self.equity_pct + self.fi_pct + self.cash_pct
        if not np.isclose(total_alloc, 1.0, atol=0.001):
            raise ValueError(f"Asset allocation must sum to 1.0, got {total_alloc:.4f}")
        
        # Tax allocation must sum to 1.0
        total_tax_alloc = self.taxable_pct + self.ira_pct + self.roth_pct
        if not np.isclose(total_tax_alloc, 1.0, atol=0.001):
            raise ValueError(f"Tax account allocation must sum to 1.0, got {total_tax_alloc:.4f}")
        
        # Volatilities must be non-negative
        if any(v < 0 for v in [self.equity_vol_annual, self.fi_vol_annual, self.cash_vol_annual]):
            raise ValueError("Volatilities must be non-negative")
        
        # Returns should be reasonable (conservative bounds)
        if self.equity_return_annual < -0.20 or self.equity_return_annual > 0.30:
            logger.warning(f"Equity return {self.equity_return_annual:.2%} is outside typical range")
        
        # Inflation should be reasonable
        if self.inflation_annual < -0.05 or self.inflation_annual > 0.15:
            logger.warning(f"Inflation {self.inflation_annual:.2%} is outside typical range")
        
        # Ages must be sensible
        if not (18 <= self.current_age <= 100):
            raise ValueError(f"Current age {self.current_age} is invalid")
        
        if self.years_to_model < 1 or self.years_to_model > 80:
            raise ValueError(f"Years to model {self.years_to_model} is invalid")
        
        # Spending must be positive if specified
        if self.monthly_spending < 0:
            self.monthly_spending = abs(self.monthly_spending)
        
        logger.info(f"✓ Validated inputs: {self.starting_portfolio:,.0f} portfolio, "
                   f"{self.years_to_model} years, age {self.current_age}")


@dataclass
class SimulationResults:
    """
    Complete simulation results with all metrics and statistics.
    
    This structure provides everything needed for analysis and reporting.
    """
    # Raw simulation data
    paths: np.ndarray                    # Shape: (n_scenarios, n_months+1)
    monthly_stats: pd.DataFrame          # Percentiles and statistics by month
    
    # Key metrics
    success_probability: float           # % of paths that never hit zero
    median_ending_value: float
    p10_ending_value: float
    p90_ending_value: float
    
    # Ruin analysis
    annual_ruin_probability: List[float]     # First-passage probability each year
    cumulative_ruin_probability: List[float] # Running sum of ruin probability
    median_years_to_ruin: Optional[float]    # Median years until ruin (if occurs)
    
    # Longevity analysis (at age milestones)
    longevity_metrics: Dict[int, Dict[str, float]]  # Age -> metrics
    
    # Distribution analysis
    ending_distribution: Dict[str, float]    # Percentiles of ending values
    worst_case_path: np.ndarray             # P5 or worst path
    best_case_path: np.ndarray              # P95 or best path
    median_path: np.ndarray                 # P50 path
    
    # Portfolio statistics
    max_drawdown_median: float              # Largest peak-to-trough decline (median path)
    years_depleted: float                   # Average years to depletion (failed paths only)
    
    # Input parameters (for reference)
    inputs: PortfolioInputs
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert results to dictionary for JSON serialization"""
        return {
            "success_probability": float(self.success_probability),
            "median_ending_value": float(self.median_ending_value),
            "p10_ending_value": float(self.p10_ending_value),
            "p90_ending_value": float(self.p90_ending_value),
            "annual_ruin_probability": [float(p) for p in self.annual_ruin_probability],
            "cumulative_ruin_probability": [float(p) for p in self.cumulative_ruin_probability],
            "median_years_to_ruin": float(self.median_years_to_ruin) if self.median_years_to_ruin else None,
            "longevity_metrics": self.longevity_metrics,
            "ending_distribution": self.ending_distribution,
            "max_drawdown_median": float(self.max_drawdown_median),
            "years_depleted": float(self.years_depleted),
            "monthly_stats": self.monthly_stats.to_dict('records')
        }


def compute_portfolio_statistics(
    inputs: PortfolioInputs
) -> Tuple[float, float]:
    """
    Calculate portfolio expected return and volatility using proper portfolio theory.
    
    Uses the formula:
    σ²_p = Σᵢ Σⱼ wᵢwⱼσᵢσⱼρᵢⱼ
    
    Args:
        inputs: Portfolio configuration
        
    Returns:
        Tuple of (expected_real_return, annual_volatility)
    """
    # Expected return is simply weighted average
    exp_return = (
        inputs.equity_pct * inputs.equity_return_annual +
        inputs.fi_pct * inputs.fi_return_annual +
        inputs.cash_pct * inputs.cash_return_annual
    )
    
    # Portfolio variance using correlation matrix
    w = np.array([inputs.equity_pct, inputs.fi_pct, inputs.cash_pct])
    sigma = np.array([inputs.equity_vol_annual, inputs.fi_vol_annual, inputs.cash_vol_annual])
    
    # Correlation matrix
    corr = np.array([
        [1.0, inputs.corr_equity_fi, inputs.corr_equity_cash],
        [inputs.corr_equity_fi, 1.0, inputs.corr_fi_cash],
        [inputs.corr_equity_cash, inputs.corr_fi_cash, 1.0]
    ])
    
    # Covariance matrix: Σ = diag(σ) @ corr @ diag(σ)
    cov = np.diag(sigma) @ corr @ np.diag(sigma)
    
    # Portfolio variance: w^T Σ w
    portfolio_var = w @ cov @ w
    portfolio_vol = np.sqrt(portfolio_var)
    
    logger.info(f"Portfolio: μ={exp_return:.2%}, σ={portfolio_vol:.2%} (real, annual)")
    
    return exp_return, portfolio_vol


def generate_returns_geometric_brownian_motion(
    mu_annual: float,
    sigma_annual: float,
    n_scenarios: int,
    n_months: int,
    rng: np.random.Generator
) -> np.ndarray:
    """
    Generate returns using geometric Brownian motion (lognormal model).
    
    This is the CORRECT way to model multiplicative returns.
    
    For monthly timestep Δt = 1/12:
    R(t) = exp((μ - σ²/2)Δt + σ√Δt·Z)
    
    The drift adjustment (μ - σ²/2) ensures E[R] = exp(μΔt), which is critical
    for maintaining the correct expected value in lognormal models.
    
    Args:
        mu_annual: Expected annual return (real)
        sigma_annual: Annual volatility
        n_scenarios: Number of paths
        n_months: Number of monthly steps
        rng: NumPy random generator
        
    Returns:
        Array of shape (n_scenarios, n_months) with returns (NOT cumulative)
    """
    dt = 1.0 / 12.0  # Monthly timestep
    
    # Drift adjustment for lognormal distribution
    # This is CRITICAL: without it, the median return will be biased downward
    drift = (mu_annual - 0.5 * sigma_annual**2) * dt
    diffusion = sigma_annual * np.sqrt(dt)
    
    # Generate standard normal random variables
    Z = rng.standard_normal((n_scenarios, n_months))
    
    # Lognormal returns: R = exp(drift + diffusion * Z)
    returns = np.exp(drift + diffusion * Z)
    
    # Returns are multiplicative: V(t+1) = V(t) * R(t)
    # NOT additive: V(t+1) ≠ V(t) + R(t)
    
    logger.debug(f"Generated returns: mean={returns.mean():.6f}, "
                f"median={np.median(returns):.6f}, std={returns.std():.6f}")
    
    return returns


def calculate_required_minimum_distribution(
    ira_balance,  # Can be float or ndarray
    age: int,
    rmd_factors: Dict[int, float]
):
    """
    Calculate Required Minimum Distribution for traditional IRA/401k.

    RMD = IRA Balance / Life Expectancy Factor

    Uses IRS Uniform Lifetime Table.

    Args:
        ira_balance: Traditional IRA/401k balance (scalar or array)
        age: Current age
        rmd_factors: RMD divisor table

    Returns:
        Required minimum distribution amount (same type as ira_balance)
    """
    if age < min(rmd_factors.keys()):
        # Return zero with same shape as input
        if isinstance(ira_balance, np.ndarray):
            return np.zeros_like(ira_balance)
        return 0.0

    # Use the factor for the age, or the last available factor
    if age in rmd_factors:
        factor = rmd_factors[age]
    else:
        # For ages beyond table, use last factor (conservative)
        factor = rmd_factors[max(rmd_factors.keys())]

    rmd = ira_balance / factor
    
    # Ensure non-negative (handle arrays properly)
    if isinstance(rmd, np.ndarray):
        return np.maximum(0.0, rmd)
    return max(0.0, rmd)
def run_monte_carlo_simulation(
    inputs: PortfolioInputs
) -> SimulationResults:
    """
    Execute Monte Carlo simulation with full mathematical rigor.
    
    This is the MAIN SIMULATION ENGINE. It implements:
    1. Geometric Brownian motion for returns
    2. Correct handling of all cash flows
    3. Proper fee and tax application
    4. Conservative risk measurement
    5. Comprehensive metrics calculation
    
    OPERATION MODE: REAL TERMS
    ---------------------------
    All values are in inflation-adjusted (real) dollars. This means:
    - Returns are real returns (after inflation)
    - Cash flows grow only by excess inflation (e.g., healthcare)
    - Results are in "today's dollars" for easier interpretation
    
    ORDER OF OPERATIONS EACH MONTH:
    -------------------------------
    1. Apply investment returns (stochastic)
    2. Subtract fees (advisory + fund expenses)
    3. Add income (Social Security, pension, salary)
    4. Subtract spending (living expenses + healthcare)
    5. Apply RMDs if required
    6. Apply taxes on withdrawals
    7. Check for ruin (balance ≤ 0)
    
    Args:
        inputs: Validated simulation parameters
        
    Returns:
        SimulationResults with all metrics and statistics
    """
    logger.info(f"Starting Monte Carlo simulation: {inputs.n_scenarios} scenarios, "
               f"{inputs.years_to_model} years")
    
    # Initialize RNG with seed for reproducibility
    rng = np.random.default_rng(inputs.random_seed)
    
    # Calculate portfolio statistics
    mu_annual, sigma_annual = compute_portfolio_statistics(inputs)
    
    # Setup time grid
    n_months = inputs.years_to_model * 12
    n_scenarios = inputs.n_scenarios
    
    # Generate all returns upfront (more efficient)
    returns = generate_returns_geometric_brownian_motion(
        mu_annual, sigma_annual, n_scenarios, n_months, rng
    )
    
    # Initialize paths array
    # Shape: (n_scenarios, n_months + 1)
    # paths[:, 0] = starting value
    # paths[:, t] = value at end of month t
    paths = np.zeros((n_scenarios, n_months + 1))
    paths[:, 0] = inputs.starting_portfolio
    
    # Track ruin events (month of first ruin for each scenario)
    ruin_months = np.full(n_scenarios, -1)  # -1 = never ruined
    
    # Convert annual fees to monthly
    monthly_fee_rate = (inputs.advisory_fee_pct + inputs.fund_expense_pct) / 12.0
    
    # Initialize baseline monthly spending (in real dollars)
    baseline_monthly_spending = inputs.monthly_spending if inputs.spending_rule == SpendingRule.FIXED_REAL else 0.0
    
    # Track current spending for guardrails
    current_spending_multiplier = np.ones(n_scenarios)
    
    # ====================
    # MAIN SIMULATION LOOP
    # ====================
    for month in range(1, n_months + 1):
        # Current age (in years, as float)
        age_years = inputs.current_age + (month / 12.0)
        age_int = int(np.floor(age_years))
        
        # ------------------
        # 1. APPLY RETURNS
        # ------------------
        # Multiplicative returns: V(t) = V(t-1) * R(t)
        paths[:, month] = paths[:, month - 1] * returns[:, month - 1]
        
        # ------------------
        # 2. SUBTRACT FEES
        # ------------------
        # Fees are applied monthly as a percentage of AUM
        fees = paths[:, month] * monthly_fee_rate
        paths[:, month] -= fees
        
        # ------------------
        # 3. ADD INCOME
        # ------------------
        monthly_income = 0.0
        
        # Social Security (starts at specified age)
        if age_int >= inputs.ss_start_age:
            monthly_income += inputs.social_security_annual / 12.0
        
        # Pension (with optional COLA)
        if age_int >= inputs.pension_start_age:
            years_since_pension_start = max(0, age_years - inputs.pension_start_age)
            pension_with_cola = inputs.pension_annual * (1 + inputs.pension_cola) ** years_since_pension_start
            monthly_income += pension_with_cola / 12.0
        
        # Salary/wages (pre-retirement income)
        if inputs.monthly_income > 0:
            monthly_income += inputs.monthly_income
        
        paths[:, month] += monthly_income
        
        # ------------------
        # 4. SUBTRACT SPENDING
        # ------------------
        # Calculate spending based on strategy
        if inputs.spending_rule == SpendingRule.FIXED_REAL:
            # Fixed real spending, adjusted for lifestyle phases
            spending = baseline_monthly_spending * current_spending_multiplier
            
        elif inputs.spending_rule == SpendingRule.PERCENT_OF_PORTFOLIO:
            # Dynamic spending as % of portfolio
            spending = paths[:, month] * (inputs.spending_pct_annual / 12.0)
            
        else:  # HYBRID_FLOOR_CEILING
            # % of portfolio with floor and ceiling
            spending = paths[:, month] * (inputs.spending_pct_annual / 12.0)
            spending = np.clip(
                spending,
                inputs.spending_floor / 12.0,
                inputs.spending_ceiling / 12.0
            )
        
        # Lifestyle phase adjustments
        if inputs.use_lifestyle_phases:
            if age_int >= inputs.no_go_age:
                spending *= inputs.no_go_spending_pct
            elif age_int >= inputs.slow_go_age:
                spending *= inputs.slow_go_spending_pct
        
        # Healthcare costs (grows faster than general inflation)
        if age_int >= inputs.healthcare_start_age:
            years_since_healthcare = age_years - inputs.healthcare_start_age
            healthcare_cost = inputs.healthcare_annual * (1 + inputs.healthcare_inflation_real) ** years_since_healthcare
            spending += healthcare_cost / 12.0
        
        paths[:, month] -= spending
        
        # ------------------
        # 5. APPLY RMDs
        # ------------------
        if age_int >= inputs.rmd_age:
            # RMD applies to traditional IRA portion
            ira_balance = paths[:, month] * inputs.ira_pct
            rmd = calculate_required_minimum_distribution(
                ira_balance,
                age_int,
                inputs.rmd_factors
            )
            # RMD is a forced distribution (we model as additional withdrawal)
            # In practice, if spending < RMD, RMD determines withdrawal
            # For simplicity, we add RMD to withdrawals
            # Note: This is conservative (forces more withdrawals)
            rmd_tax = rmd * inputs.marginal_tax_rate
            paths[:, month] -= rmd_tax  # Tax cost of RMD
        
        # ------------------
        # 6. APPLY TAXES
        # ------------------
        # Withdrawals from traditional IRA are taxed at marginal rate
        # Withdrawals from taxable account incur capital gains tax
        # Withdrawals from Roth are tax-free
        # For simplicity, we apply a blended tax rate based on account mix
        blended_tax_rate = (
            inputs.taxable_pct * inputs.ltcg_tax_rate +
            inputs.ira_pct * inputs.marginal_tax_rate +
            inputs.roth_pct * 0.0
        )
        withdrawal_tax = spending * blended_tax_rate
        paths[:, month] -= withdrawal_tax
        
        # ------------------
        # 7. GUARDRAILS
        # ------------------
        if inputs.use_guardrails and month > 12:
            # Check portfolio performance vs. starting value
            portfolio_change = (paths[:, month] - inputs.starting_portfolio) / inputs.starting_portfolio
            
            # Increase spending if portfolio up significantly
            increase_mask = portfolio_change > inputs.upper_guardrail
            current_spending_multiplier[increase_mask] *= (1 + inputs.guardrail_adjustment)
            
            # Decrease spending if portfolio down significantly
            decrease_mask = portfolio_change < -inputs.lower_guardrail
            current_spending_multiplier[decrease_mask] *= (1 - inputs.guardrail_adjustment)
        
        # ------------------
        # 8. CHECK FOR RUIN
        # ------------------
        # Ruin = portfolio value ≤ 0
        # Use small tolerance to avoid floating point issues
        ruined_this_month = (paths[:, month] <= 1.0) & (ruin_months == -1)
        ruin_months[ruined_this_month] = month
        
        # Floor at zero (can't have negative portfolio)
        paths[:, month] = np.maximum(paths[:, month], 0.0)
    
    # =============================
    # POST-SIMULATION: CALCULATE METRICS
    # =============================
    
    logger.info("Simulation complete, calculating metrics...")
    
    # Monthly statistics
    monthly_stats = pd.DataFrame({
        "month": np.arange(n_months + 1),
        "median": np.median(paths, axis=0),
        "p10": np.percentile(paths, 10, axis=0),
        "p25": np.percentile(paths, 25, axis=0),
        "p75": np.percentile(paths, 75, axis=0),
        "p90": np.percentile(paths, 90, axis=0),
        "mean": np.mean(paths, axis=0),
        "std": np.std(paths, axis=0),
        "p05": np.percentile(paths, 5, axis=0),
        "p95": np.percentile(paths, 95, axis=0)
    })
    
    # Success probability (conservative definition)
    # Success = NEVER hitting zero throughout entire horizon
    success_count = np.sum(ruin_months == -1)
    success_probability = success_count / n_scenarios
    
    # Ending values
    ending_values = paths[:, -1]
    median_ending = np.median(ending_values)
    p10_ending = np.percentile(ending_values, 10)
    p90_ending = np.percentile(ending_values, 90)
    
    # Ending distribution
    ending_distribution = {
        "p05": float(np.percentile(ending_values, 5)),
        "p10": float(p10_ending),
        "p25": float(np.percentile(ending_values, 25)),
        "p50": float(median_ending),
        "p75": float(np.percentile(ending_values, 75)),
        "p90": float(p90_ending),
        "p95": float(np.percentile(ending_values, 95))
    }
    
    # Annual ruin probability (first-passage probability)
    # This is the probability of FIRST experiencing ruin in each year
    annual_ruin_prob = []
    for year in range(inputs.years_to_model + 1):
        month_start = year * 12
        month_end = month_start + 12 if year < inputs.years_to_model else n_months
        
        # Count scenarios that ruined in this year
        ruined_this_year = np.sum((ruin_months >= month_start) & (ruin_months < month_end))
        prob = ruined_this_year / n_scenarios
        annual_ruin_prob.append(float(prob))
    
    # Cumulative ruin probability
    # Running sum of first-passage probabilities
    cumulative_ruin_prob = np.cumsum(annual_ruin_prob).tolist()
    
    # Years to ruin (for failed scenarios only)
    failed_scenarios = ruin_months[ruin_months != -1]
    if len(failed_scenarios) > 0:
        years_to_ruin = failed_scenarios / 12.0
        median_years_to_ruin = float(np.median(years_to_ruin))
        avg_years_depleted = float(np.mean(years_to_ruin))
    else:
        median_years_to_ruin = None
        avg_years_depleted = 0.0
    
    # Longevity metrics (at key age milestones)
    longevity_metrics = {}
    for milestone_age in [70, 75, 80, 85, 90, 95, 100]:
        if milestone_age < inputs.current_age:
            continue
        if milestone_age > inputs.current_age + inputs.years_to_model:
            break
        
        years_to_milestone = milestone_age - inputs.current_age
        month_idx = min(years_to_milestone * 12, n_months)
        
        values_at_age = paths[:, month_idx]
        ruined_by_age = np.sum(ruin_months <= month_idx) if month_idx < n_months else np.sum(ruin_months != -1)
        depletion_risk = ruined_by_age / n_scenarios
        
        longevity_metrics[milestone_age] = {
            "median_balance": float(np.median(values_at_age)),
            "p10_balance": float(np.percentile(values_at_age, 10)),
            "p90_balance": float(np.percentile(values_at_age, 90)),
            "depletion_risk": float(depletion_risk),
            "percent_above_1M": float(np.mean(values_at_age > 1_000_000))
        }
    
    # Maximum drawdown (for median path)
    median_path = monthly_stats["median"].values
    running_max = np.maximum.accumulate(median_path)
    drawdown = (median_path - running_max) / running_max
    max_drawdown = float(np.min(drawdown))
    
    # Extract representative paths
    median_scenario_idx = np.argsort(ending_values)[n_scenarios // 2]
    worst_scenario_idx = np.argsort(ending_values)[int(n_scenarios * 0.05)]
    best_scenario_idx = np.argsort(ending_values)[int(n_scenarios * 0.95)]
    
    results = SimulationResults(
        paths=paths,
        monthly_stats=monthly_stats,
        success_probability=success_probability,
        median_ending_value=median_ending,
        p10_ending_value=p10_ending,
        p90_ending_value=p90_ending,
        annual_ruin_probability=annual_ruin_prob,
        cumulative_ruin_probability=cumulative_ruin_prob,
        median_years_to_ruin=median_years_to_ruin,
        longevity_metrics=longevity_metrics,
        ending_distribution=ending_distribution,
        worst_case_path=paths[worst_scenario_idx, :],
        best_case_path=paths[best_scenario_idx, :],
        median_path=median_path,
        max_drawdown_median=max_drawdown,
        years_depleted=avg_years_depleted,
        inputs=inputs
    )
    
    logger.info(f"✓ Success probability: {success_probability:.1%}")
    logger.info(f"✓ Median ending: ${median_ending:,.0f}")
    logger.info(f"✓ P10 ending: ${p10_ending:,.0f}")
    
    return results


# ======================
# STRESS TEST FUNCTIONS
# ======================

def run_stress_test(
    inputs: PortfolioInputs,
    stress_name: str,
    return_shock: float = 0.0,
    vol_multiplier: float = 1.0,
    inflation_shock: float = 0.0,
    random_seed: Optional[int] = None
) -> SimulationResults:
    """
    Run simulation with stressed parameters.
    
    Args:
        inputs: Base parameters
        stress_name: Name of stress scenario
        return_shock: Additive shock to returns (e.g., -0.02 for -2%)
        vol_multiplier: Multiplicative shock to volatility (e.g., 1.5 for +50%)
        inflation_shock: Additive shock to inflation
        random_seed: Optional random seed override for testing
        
    Returns:
        Simulation results under stress
    """
    stressed = PortfolioInputs(**inputs.__dict__)
    stressed.equity_return_annual += return_shock
    stressed.fi_return_annual += return_shock * 0.5
    stressed.equity_vol_annual *= vol_multiplier
    stressed.fi_vol_annual *= vol_multiplier
    stressed.inflation_annual += inflation_shock
    
    if random_seed is not None:
        stressed.random_seed = random_seed
    
    logger.info(f"Running stress test: {stress_name}")
    return run_monte_carlo_simulation(stressed)


def deterministic_test(
    starting_portfolio: float,
    annual_return: float,
    annual_withdrawal: float,
    years: int
) -> Tuple[float, int]:
    """
    Deterministic scenario (zero volatility) for validation.
    
    This should match closed-form solution:
    V(t) = V(0) * (1+r)^t - W * [(1+r)^t - 1] / r
    
    Args:
        starting_portfolio: Initial value
        annual_return: Deterministic return
        annual_withdrawal: Fixed annual withdrawal
        years: Number of years
        
    Returns:
        Tuple of (ending_value, years_to_depletion)
    """
    balance = starting_portfolio
    for year in range(years):
        balance = balance * (1 + annual_return) - annual_withdrawal
        if balance <= 0:
            return 0.0, year + 1
    
    return balance, -1
