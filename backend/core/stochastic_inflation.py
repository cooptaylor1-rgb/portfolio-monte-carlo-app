"""
Stochastic Inflation Engine with Mean Reversion

Implements Ornstein-Uhlenbeck process for more realistic inflation modeling.
Replaces fixed 3% assumption with scenario-based stochastic paths that:
- Mean revert to long-term average
- Include volatility and shocks
- Model inflation regimes (normal, high, deflation)
- Support stress testing

Author: Salem Investment Counselors
Last Updated: December 2024
"""

from dataclasses import dataclass
from typing import List, Optional, Tuple
from enum import Enum
import numpy as np
import logging

logger = logging.getLogger(__name__)


class InflationRegime(str, Enum):
    """Inflation environment scenarios"""
    NORMAL = "normal"  # 2-3% historical average
    HIGH = "high"  # 1970s stagflation (5-9%)
    DEFLATION = "deflation"  # Japan 1990s (-1 to 1%)
    VOLATILE = "volatile"  # 2020-2022 spike (rapid changes)


@dataclass
class InflationParameters:
    """Parameters for stochastic inflation model"""
    base_rate: float = 0.025  # Long-run mean (2.5%)
    volatility: float = 0.015  # Annual volatility (1.5%)
    mean_reversion_speed: float = 0.3  # Speed of reversion (kappa)
    min_rate: float = -0.02  # Floor (-2% deflation)
    max_rate: float = 0.15  # Ceiling (15% hyperinflation)
    regime: InflationRegime = InflationRegime.NORMAL


@dataclass
class InflationScenario:
    """A single inflation scenario path"""
    monthly_rates: np.ndarray  # Monthly inflation rates
    annual_rates: np.ndarray  # Annualized rates
    cumulative_factor: np.ndarray  # Cumulative inflation multiplier
    regime: InflationRegime


class StochasticInflationEngine:
    """
    Generates realistic inflation paths using Ornstein-Uhlenbeck process.
    
    The OU process models mean reversion:
    dI = κ(μ - I)dt + σdW
    
    where:
    - I = current inflation rate
    - κ = mean reversion speed (how fast it returns to μ)
    - μ = long-run mean inflation rate
    - σ = volatility
    - dW = Wiener process (random shock)
    
    This produces more realistic inflation that:
    1. Reverts to historical average over time
    2. Shows short-term volatility
    3. Avoids unrealistic extremes
    4. Captures regime shifts
    """
    
    def __init__(self, seed: Optional[int] = None):
        """
        Initialize the stochastic inflation engine.
        
        Args:
            seed: Random seed for reproducibility
        """
        self.seed = seed
        if seed is not None:
            np.random.seed(seed)
        
        # Regime-specific parameters
        self.regime_params = {
            InflationRegime.NORMAL: InflationParameters(
                base_rate=0.025,
                volatility=0.015,
                mean_reversion_speed=0.3,
                min_rate=-0.01,
                max_rate=0.06
            ),
            InflationRegime.HIGH: InflationParameters(
                base_rate=0.07,
                volatility=0.025,
                mean_reversion_speed=0.15,  # Slower reversion
                min_rate=0.03,
                max_rate=0.12
            ),
            InflationRegime.DEFLATION: InflationParameters(
                base_rate=0.005,
                volatility=0.010,
                mean_reversion_speed=0.2,
                min_rate=-0.02,
                max_rate=0.03
            ),
            InflationRegime.VOLATILE: InflationParameters(
                base_rate=0.035,
                volatility=0.030,  # High volatility
                mean_reversion_speed=0.25,
                min_rate=-0.01,
                max_rate=0.10
            ),
        }
    
    def generate_scenarios(
        self,
        n_scenarios: int,
        n_months: int,
        regime: InflationRegime = InflationRegime.NORMAL,
        starting_rate: Optional[float] = None
    ) -> List[InflationScenario]:
        """
        Generate multiple stochastic inflation scenarios.
        
        Args:
            n_scenarios: Number of scenarios to generate
            n_months: Length of each scenario in months
            regime: Inflation regime to model
            starting_rate: Initial inflation rate (uses base_rate if None)
        
        Returns:
            List of InflationScenario objects with monthly paths
        """
        params = self.regime_params[regime]
        
        if starting_rate is None:
            starting_rate = params.base_rate
        
        # Generate all scenarios at once (vectorized)
        monthly_paths = self._generate_ou_paths(
            n_scenarios=n_scenarios,
            n_months=n_months,
            starting_rate=starting_rate,
            params=params
        )
        
        scenarios = []
        for i in range(n_scenarios):
            monthly_rates = monthly_paths[i, :]
            annual_rates = self._monthly_to_annual(monthly_rates)
            cumulative_factor = self._calculate_cumulative_inflation(monthly_rates)
            
            scenario = InflationScenario(
                monthly_rates=monthly_rates,
                annual_rates=annual_rates,
                cumulative_factor=cumulative_factor,
                regime=regime
            )
            scenarios.append(scenario)
        
        return scenarios
    
    def _generate_ou_paths(
        self,
        n_scenarios: int,
        n_months: int,
        starting_rate: float,
        params: InflationParameters
    ) -> np.ndarray:
        """
        Generate Ornstein-Uhlenbeck paths for inflation.
        
        Uses the Euler-Maruyama method to discretize the OU SDE:
        I(t+dt) = I(t) + κ(μ - I(t))dt + σ√dt * Z
        
        where Z ~ N(0,1)
        
        Args:
            n_scenarios: Number of paths
            n_months: Number of time steps
            starting_rate: Initial inflation rate
            params: InflationParameters with process parameters
        
        Returns:
            (n_scenarios, n_months) array of inflation rates
        """
        dt = 1.0 / 12.0  # Monthly time step
        sqrt_dt = np.sqrt(dt)
        
        # Initialize paths
        paths = np.zeros((n_scenarios, n_months))
        paths[:, 0] = starting_rate
        
        # Generate paths using OU process
        for t in range(1, n_months):
            # Random shocks
            dW = np.random.randn(n_scenarios) * sqrt_dt
            
            # Mean reversion term: κ(μ - I)dt
            mean_reversion = params.mean_reversion_speed * \
                           (params.base_rate - paths[:, t-1]) * dt
            
            # Volatility term: σdW
            volatility_term = params.volatility * dW
            
            # Update: I(t+dt) = I(t) + drift + diffusion
            paths[:, t] = paths[:, t-1] + mean_reversion + volatility_term
            
            # Apply bounds to prevent unrealistic extremes
            paths[:, t] = np.clip(paths[:, t], params.min_rate, params.max_rate)
        
        return paths
    
    def _monthly_to_annual(self, monthly_rates: np.ndarray) -> np.ndarray:
        """
        Convert monthly inflation rates to annualized rates.
        
        Uses compound formula: (1 + r_monthly)^12 - 1
        
        Args:
            monthly_rates: Array of monthly inflation rates
        
        Returns:
            Array of annualized inflation rates
        """
        # Rolling 12-month annualized rate
        n_months = len(monthly_rates)
        annual_rates = np.zeros(n_months)
        
        for i in range(n_months):
            if i < 11:
                # Not enough history, use simple annualization
                annual_rates[i] = monthly_rates[i] * 12
            else:
                # Compound last 12 months
                last_12_months = monthly_rates[i-11:i+1]
                annual_rates[i] = np.prod(1 + last_12_months) - 1
        
        return annual_rates
    
    def _calculate_cumulative_inflation(self, monthly_rates: np.ndarray) -> np.ndarray:
        """
        Calculate cumulative inflation multiplier.
        
        Example: If cumulative_factor[36] = 1.08, then prices have
        increased 8% over the first 36 months.
        
        Args:
            monthly_rates: Array of monthly inflation rates
        
        Returns:
            Array of cumulative inflation factors
        """
        # Cumulative product of (1 + monthly_rate)
        return np.cumprod(1 + monthly_rates)
    
    def generate_stress_scenarios(
        self,
        n_months: int
    ) -> dict[str, InflationScenario]:
        """
        Generate predefined stress test scenarios.
        
        Args:
            n_months: Length of scenario in months
        
        Returns:
            Dictionary of labeled stress scenarios
        """
        scenarios = {}
        
        # 1970s stagflation
        scenarios['stagflation'] = self.generate_scenarios(
            n_scenarios=1,
            n_months=n_months,
            regime=InflationRegime.HIGH,
            starting_rate=0.04
        )[0]
        
        # 2020-2022 inflation spike
        volatile_scenario = self.generate_scenarios(
            n_scenarios=1,
            n_months=n_months,
            regime=InflationRegime.VOLATILE,
            starting_rate=0.08
        )[0]
        # Force spike then retreat pattern
        spike_months = min(24, n_months // 3)
        volatile_scenario.monthly_rates[:spike_months] *= 1.5
        volatile_scenario.monthly_rates[spike_months:] *= 0.6
        scenarios['2020s_spike'] = volatile_scenario
        
        # Japan deflation
        scenarios['deflation'] = self.generate_scenarios(
            n_scenarios=1,
            n_months=n_months,
            regime=InflationRegime.DEFLATION,
            starting_rate=0.00
        )[0]
        
        # Normal baseline
        scenarios['baseline'] = self.generate_scenarios(
            n_scenarios=1,
            n_months=n_months,
            regime=InflationRegime.NORMAL,
            starting_rate=0.025
        )[0]
        
        return scenarios
    
    def calculate_real_returns(
        self,
        nominal_returns: np.ndarray,
        inflation_scenario: InflationScenario
    ) -> np.ndarray:
        """
        Convert nominal returns to real returns using Fisher equation.
        
        real_return ≈ nominal_return - inflation_rate
        (Exact: (1 + r_nominal) / (1 + r_inflation) - 1)
        
        Args:
            nominal_returns: Array of nominal returns
            inflation_scenario: InflationScenario with inflation path
        
        Returns:
            Array of real (inflation-adjusted) returns
        """
        # Ensure matching lengths
        min_length = min(len(nominal_returns), len(inflation_scenario.monthly_rates))
        
        nominal = nominal_returns[:min_length]
        inflation = inflation_scenario.monthly_rates[:min_length]
        
        # Fisher equation (exact)
        real_returns = (1 + nominal) / (1 + inflation) - 1
        
        return real_returns
    
    def get_percentile_scenarios(
        self,
        scenarios: List[InflationScenario],
        percentiles: List[int] = [10, 50, 90]
    ) -> dict[int, InflationScenario]:
        """
        Extract percentile paths from scenario ensemble.
        
        Args:
            scenarios: List of InflationScenario objects
            percentiles: List of percentiles to extract (0-100)
        
        Returns:
            Dictionary mapping percentile to scenario
        """
        if not scenarios:
            raise ValueError("No scenarios provided")
        
        n_months = len(scenarios[0].monthly_rates)
        n_scenarios = len(scenarios)
        
        # Stack all monthly rates
        all_rates = np.array([s.monthly_rates for s in scenarios])
        
        # Calculate percentiles at each month
        percentile_paths = {}
        for p in percentiles:
            monthly_rates = np.percentile(all_rates, p, axis=0)
            annual_rates = self._monthly_to_annual(monthly_rates)
            cumulative_factor = self._calculate_cumulative_inflation(monthly_rates)
            
            percentile_paths[p] = InflationScenario(
                monthly_rates=monthly_rates,
                annual_rates=annual_rates,
                cumulative_factor=cumulative_factor,
                regime=scenarios[0].regime
            )
        
        return percentile_paths
    
    def calculate_inflation_adjusted_spending(
        self,
        base_spending: float,
        inflation_scenario: InflationScenario,
        n_months: int
    ) -> np.ndarray:
        """
        Calculate inflation-adjusted spending over time.
        
        Args:
            base_spending: Initial monthly spending
            inflation_scenario: InflationScenario to apply
            n_months: Number of months to project
        
        Returns:
            Array of inflation-adjusted spending amounts
        """
        spending = np.zeros(n_months)
        spending[0] = base_spending
        
        for t in range(1, min(n_months, len(inflation_scenario.monthly_rates))):
            # Increase spending by monthly inflation rate
            spending[t] = spending[t-1] * (1 + inflation_scenario.monthly_rates[t])
        
        # If n_months > scenario length, use last rate
        if n_months > len(inflation_scenario.monthly_rates):
            last_rate = inflation_scenario.monthly_rates[-1]
            for t in range(len(inflation_scenario.monthly_rates), n_months):
                spending[t] = spending[t-1] * (1 + last_rate)
        
        return spending


def get_historical_inflation_stats() -> dict:
    """
    Return historical inflation statistics for calibration.
    
    Based on US CPI data 1960-2024.
    
    Returns:
        Dictionary with historical statistics
    """
    return {
        'mean_annual': 0.039,  # 3.9% average
        'median_annual': 0.033,  # 3.3% median
        'std_annual': 0.030,  # 3.0% standard deviation
        'min_annual': -0.004,  # -0.4% (2009)
        'max_annual': 0.135,  # 13.5% (1980)
        'percentile_10': 0.015,  # 1.5%
        'percentile_90': 0.065,  # 6.5%
        'autocorrelation': 0.65,  # Inflation is persistent
        'mean_reversion_halflife': 2.3,  # Years to revert halfway
    }


if __name__ == '__main__':
    # Example usage
    engine = StochasticInflationEngine(seed=42)
    
    # Generate normal scenarios
    scenarios = engine.generate_scenarios(
        n_scenarios=1000,
        n_months=360,  # 30 years
        regime=InflationRegime.NORMAL
    )
    
    print(f"Generated {len(scenarios)} inflation scenarios")
    print(f"Average ending inflation: {np.mean([s.monthly_rates[-1] for s in scenarios]):.2%}")
    
    # Generate stress scenarios
    stress = engine.generate_stress_scenarios(n_months=360)
    print(f"\nStress scenarios: {list(stress.keys())}")
    
    # Get percentiles
    percentiles = engine.get_percentile_scenarios(scenarios, [10, 50, 90])
    print(f"\n50th percentile final inflation: {percentiles[50].monthly_rates[-1]:.2%}")
