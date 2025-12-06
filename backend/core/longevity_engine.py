"""
Monte Carlo Longevity Engine

Implements probabilistic lifetime modeling based on actuarial tables and health factors.
Replaces fixed planning horizons (e.g., "age 95") with realistic mortality distributions.

Features:
- Gender-specific mortality rates (SOA tables)
- Health adjustment factors
- Joint life expectancy (couples)
- Conditional survival probabilities
- Conservative planning (use longer percentiles)

Author: Salem Investment Counselors
Last Updated: December 2024
"""

from dataclasses import dataclass
from typing import Optional, Tuple, List
from enum import Enum
import numpy as np
import logging

logger = logging.getLogger(__name__)


class Gender(str, Enum):
    """Gender for mortality tables"""
    MALE = "male"
    FEMALE = "female"


class HealthStatus(str, Enum):
    """Health status adjustment factors"""
    POOR = "poor"  # Chronic conditions, reduced mobility
    AVERAGE = "average"  # Typical for age
    GOOD = "good"  # Active, no major conditions
    EXCELLENT = "excellent"  # Very active, great health


@dataclass
class LongevityParameters:
    """Parameters for longevity modeling"""
    current_age: int
    gender: Gender
    health_status: HealthStatus = HealthStatus.AVERAGE
    smoker: bool = False
    
    # For couples (joint life modeling)
    spouse_age: Optional[int] = None
    spouse_gender: Optional[Gender] = None
    spouse_health: HealthStatus = HealthStatus.AVERAGE
    spouse_smoker: bool = False


class LongevityEngine:
    """
    Generates probabilistic lifetimes using actuarial tables with adjustments.
    
    Uses Society of Actuaries (SOA) 2012 Individual Annuity Mortality tables
    as baseline, then applies health/lifestyle adjustments.
    """
    
    def __init__(self, seed: Optional[int] = None):
        """
        Initialize longevity engine.
        
        Args:
            seed: Random seed for reproducibility
        """
        self.seed = seed
        if seed is not None:
            np.random.seed(seed)
        
        # Simplified mortality tables (deaths per 1000)
        # Based on SOA 2012 IAM tables
        self._mortality_tables = self._load_mortality_tables()
        
        # Health adjustment factors (multiplier on base mortality)
        self._health_adjustments = {
            HealthStatus.POOR: 1.5,  # 50% higher mortality
            HealthStatus.AVERAGE: 1.0,
            HealthStatus.GOOD: 0.85,  # 15% lower mortality
            HealthStatus.EXCELLENT: 0.70,  # 30% lower mortality
        }
        
        # Smoker adds ~10 years of mortality risk
        self._smoker_adjustment = 1.8
    
    def _load_mortality_tables(self) -> dict:
        """
        Load simplified mortality tables.
        
        Returns annual death probability (qx) by age and gender.
        For production, use actual SOA tables.
        """
        # Simplified Gompertz-Makeham model
        # qx ≈ α + β * exp(γ * age)
        
        ages = np.arange(0, 121)
        
        # Male parameters (calibrated to US life tables)
        alpha_m, beta_m, gamma_m = 0.0005, 0.0001, 0.08
        male_qx = alpha_m + beta_m * np.exp(gamma_m * ages)
        male_qx = np.clip(male_qx, 0, 1)
        
        # Female parameters (lower mortality at all ages)
        alpha_f, beta_f, gamma_f = 0.0003, 0.00008, 0.08
        female_qx = alpha_f + beta_f * np.exp(gamma_f * ages)
        female_qx = np.clip(female_qx, 0, 1)
        
        return {
            Gender.MALE: {age: male_qx[age] for age in ages},
            Gender.FEMALE: {age: female_qx[age] for age in ages}
        }
    
    def get_annual_death_probability(
        self,
        age: int,
        gender: Gender,
        health: HealthStatus = HealthStatus.AVERAGE,
        smoker: bool = False
    ) -> float:
        """
        Get annual death probability for given characteristics.
        
        Args:
            age: Current age
            gender: Gender
            health: Health status
            smoker: Smoking status
        
        Returns:
            Annual death probability (0-1)
        """
        if age < 0 or age > 120:
            return 1.0  # Certain death beyond 120
        
        # Base mortality from tables
        base_qx = self._mortality_tables[gender].get(age, 1.0)
        
        # Apply health adjustment
        health_factor = self._health_adjustments[health]
        
        # Apply smoker adjustment
        smoker_factor = self._smoker_adjustment if smoker else 1.0
        
        # Combined adjustment
        adjusted_qx = base_qx * health_factor * smoker_factor
        
        # Ensure probability stays in [0, 1]
        return min(adjusted_qx, 1.0)
    
    def simulate_lifetime(
        self,
        params: LongevityParameters,
        n_scenarios: int = 1000
    ) -> np.ndarray:
        """
        Simulate age at death for an individual.
        
        Args:
            params: LongevityParameters
            n_scenarios: Number of scenarios
        
        Returns:
            Array of ages at death (length n_scenarios)
        """
        current_age = params.current_age
        max_age = 120
        
        # Pre-allocate death ages
        death_ages = np.zeros(n_scenarios)
        
        for scenario in range(n_scenarios):
            age = current_age
            
            while age <= max_age:
                # Get death probability for this age
                qx = self.get_annual_death_probability(
                    age=age,
                    gender=params.gender,
                    health=params.health_status,
                    smoker=params.smoker
                )
                
                # Random draw: does person die this year?
                if np.random.random() < qx:
                    death_ages[scenario] = age
                    break
                
                age += 1
            
            # If survived to max_age, death at max_age
            if age > max_age:
                death_ages[scenario] = max_age
        
        return death_ages
    
    def simulate_joint_lifetime(
        self,
        params: LongevityParameters,
        n_scenarios: int = 1000
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Simulate lifetimes for a couple (first death, last death).
        
        Important for planning: portfolio must last until last spouse dies.
        
        Args:
            params: LongevityParameters with spouse information
            n_scenarios: Number of scenarios
        
        Returns:
            Tuple of (first_death_ages, second_death_ages, last_survivor_sex)
        """
        if params.spouse_age is None:
            raise ValueError("Spouse age required for joint life simulation")
        
        # Simulate primary person
        primary_deaths = self.simulate_lifetime(params, n_scenarios)
        
        # Simulate spouse
        spouse_params = LongevityParameters(
            current_age=params.spouse_age,
            gender=params.spouse_gender,
            health_status=params.spouse_health,
            smoker=params.spouse_smoker
        )
        spouse_deaths = self.simulate_lifetime(spouse_params, n_scenarios)
        
        # Calculate first and second deaths
        first_death = np.minimum(primary_deaths, spouse_deaths)
        second_death = np.maximum(primary_deaths, spouse_deaths)
        
        # Track which spouse survives longer (0 = primary, 1 = spouse)
        last_survivor = (spouse_deaths > primary_deaths).astype(int)
        
        return first_death, second_death, last_survivor
    
    def calculate_survival_probabilities(
        self,
        params: LongevityParameters,
        target_ages: np.ndarray
    ) -> np.ndarray:
        """
        Calculate probability of surviving to each target age.
        
        Args:
            params: LongevityParameters
            target_ages: Array of ages to calculate survival for
        
        Returns:
            Array of survival probabilities
        """
        current_age = params.current_age
        
        survival_probs = np.zeros(len(target_ages))
        
        for i, target_age in enumerate(target_ages):
            if target_age < current_age:
                survival_probs[i] = 1.0  # Already survived
                continue
            
            # Calculate cumulative survival probability
            cum_survival = 1.0
            
            for age in range(int(current_age), int(target_age)):
                qx = self.get_annual_death_probability(
                    age=age,
                    gender=params.gender,
                    health=params.health_status,
                    smoker=params.smoker
                )
                
                # Survival probability for this year
                px = 1.0 - qx
                
                # Cumulative survival
                cum_survival *= px
            
            survival_probs[i] = cum_survival
        
        return survival_probs
    
    def get_life_expectancy(
        self,
        params: LongevityParameters,
        use_median: bool = False
    ) -> float:
        """
        Calculate life expectancy (mean or median remaining years).
        
        Args:
            params: LongevityParameters
            use_median: If True, return median; if False, return mean
        
        Returns:
            Expected age at death
        """
        # Simulate many lifetimes
        death_ages = self.simulate_lifetime(params, n_scenarios=10000)
        
        if use_median:
            return np.median(death_ages)
        else:
            return np.mean(death_ages)
    
    def get_planning_horizon(
        self,
        params: LongevityParameters,
        percentile: int = 90,
        include_spouse: bool = False
    ) -> int:
        """
        Get conservative planning horizon (e.g., 90th percentile age).
        
        For retirement planning, we want to plan for longer-than-expected life.
        Using 90th percentile means 90% of people will die before this age.
        
        Args:
            params: LongevityParameters
            percentile: Percentile to use (75, 90, 95 common)
            include_spouse: If True, use joint life (last to die)
        
        Returns:
            Planning horizon age (integer)
        """
        if include_spouse and params.spouse_age is not None:
            # Joint life: plan for last survivor
            _, second_deaths, _ = self.simulate_joint_lifetime(params, n_scenarios=10000)
            planning_age = np.percentile(second_deaths, percentile)
        else:
            # Individual life
            death_ages = self.simulate_lifetime(params, n_scenarios=10000)
            planning_age = np.percentile(death_ages, percentile)
        
        return int(np.ceil(planning_age))
    
    def calculate_longevity_risk_premium(
        self,
        params: LongevityParameters,
        annual_spending: float,
        discount_rate: float = 0.03
    ) -> dict:
        """
        Calculate the economic value of longevity risk.
        
        Compares expected lifetime costs vs. worst-case (95th percentile).
        
        Args:
            params: LongevityParameters
            annual_spending: Annual spending in today's dollars
            discount_rate: Real discount rate
        
        Returns:
            Dictionary with longevity risk metrics
        """
        death_ages = self.simulate_lifetime(params, n_scenarios=10000)
        
        life_expectancy = np.mean(death_ages)
        p50_age = np.percentile(death_ages, 50)
        p75_age = np.percentile(death_ages, 75)
        p90_age = np.percentile(death_ages, 90)
        p95_age = np.percentile(death_ages, 95)
        
        current_age = params.current_age
        
        # Calculate present value of lifetime spending for each percentile
        def pv_spending(target_age):
            years = target_age - current_age
            if years <= 0:
                return 0
            # PV = spending * (1 - (1+r)^-n) / r
            return annual_spending * (1 - (1 + discount_rate)**(-years)) / discount_rate
        
        pv_expected = pv_spending(life_expectancy)
        pv_p90 = pv_spending(p90_age)
        pv_p95 = pv_spending(p95_age)
        
        # Longevity risk premium: extra capital needed for tail risk
        risk_premium_90 = pv_p90 - pv_expected
        risk_premium_95 = pv_p95 - pv_expected
        
        return {
            'life_expectancy': life_expectancy,
            'median_age': p50_age,
            'p75_age': p75_age,
            'p90_age': p90_age,
            'p95_age': p95_age,
            'pv_expected_spending': pv_expected,
            'pv_p90_spending': pv_p90,
            'pv_p95_spending': pv_p95,
            'risk_premium_90': risk_premium_90,
            'risk_premium_95': risk_premium_95,
            'years_of_risk_90': p90_age - life_expectancy,
            'years_of_risk_95': p95_age - life_expectancy,
        }


if __name__ == '__main__':
    # Example usage
    engine = LongevityEngine(seed=42)
    
    # Individual example
    params = LongevityParameters(
        current_age=65,
        gender=Gender.MALE,
        health_status=HealthStatus.GOOD,
        smoker=False
    )
    
    life_exp = engine.get_life_expectancy(params)
    planning_horizon = engine.get_planning_horizon(params, percentile=90)
    
    print(f"Life expectancy: {life_exp:.1f}")
    print(f"Planning horizon (90th percentile): {planning_horizon}")
    
    # Couple example
    couple_params = LongevityParameters(
        current_age=65,
        gender=Gender.MALE,
        health_status=HealthStatus.GOOD,
        spouse_age=63,
        spouse_gender=Gender.FEMALE,
        spouse_health=HealthStatus.EXCELLENT
    )
    
    joint_horizon = engine.get_planning_horizon(couple_params, percentile=90, include_spouse=True)
    print(f"\nJoint planning horizon (90th percentile): {joint_horizon}")
    
    # Longevity risk premium
    risk_metrics = engine.calculate_longevity_risk_premium(params, annual_spending=80000)
    print(f"\nLongevity Risk Metrics:")
    print(f"  90th percentile age: {risk_metrics['p90_age']:.0f}")
    print(f"  Extra years of risk: {risk_metrics['years_of_risk_90']:.1f}")
    print(f"  Risk premium (90%): ${risk_metrics['risk_premium_90']:,.0f}")
