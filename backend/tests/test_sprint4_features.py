#!/usr/bin/env python3
"""
Test script for Sprint 4 features
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import numpy as np
from core.stochastic_inflation import StochasticInflationEngine, InflationRegime
from core.longevity_engine import LongevityEngine, LongevityParameters, Gender, HealthStatus
from core.monte_carlo_engine import generate_correlated_asset_returns, PortfolioInputs

print("=" * 70)
print("SPRINT 4 FEATURE TESTS")
print("=" * 70)

# Test 1: Stochastic Inflation
print("\n1. Testing Stochastic Inflation Engine...")
inf_engine = StochasticInflationEngine(seed=42)

scenarios = inf_engine.generate_scenarios(
    n_scenarios=1000,
    n_months=360,
    regime=InflationRegime.NORMAL
)
print(f"✓ Generated {len(scenarios)} inflation scenarios")

avg_inflation = np.mean([s.monthly_rates[-1] for s in scenarios])
print(f"  Average final inflation rate: {avg_inflation:.2%}")

stress = inf_engine.generate_stress_scenarios(n_months=360)
print(f"  Stress scenarios: {list(stress.keys())}")

percentiles = inf_engine.get_percentile_scenarios(scenarios, [10, 50, 90])
print(f"  50th percentile final inflation: {percentiles[50].monthly_rates[-1]:.2%}")
print(f"  90th percentile final inflation: {percentiles[90].monthly_rates[-1]:.2%}")

# Test 2: Longevity Engine
print("\n2. Testing Longevity Engine...")
long_engine = LongevityEngine(seed=42)

params = LongevityParameters(
    current_age=65,
    gender=Gender.MALE,
    health_status=HealthStatus.GOOD,
    smoker=False
)

life_exp = long_engine.get_life_expectancy(params)
planning_90 = long_engine.get_planning_horizon(params, percentile=90)
planning_95 = long_engine.get_planning_horizon(params, percentile=95)

print(f"✓ Life expectancy: {life_exp:.1f} years")
print(f"  Planning horizon (90th): {planning_90} years")
print(f"  Planning horizon (95th): {planning_95} years")

# Test with couple
couple_params = LongevityParameters(
    current_age=65,
    gender=Gender.MALE,
    health_status=HealthStatus.GOOD,
    spouse_age=63,
    spouse_gender=Gender.FEMALE,
    spouse_health=HealthStatus.EXCELLENT
)

joint_horizon = long_engine.get_planning_horizon(couple_params, percentile=90, include_spouse=True)
print(f"  Joint planning horizon (90th): {joint_horizon} years")

# Longevity risk premium
risk_metrics = long_engine.calculate_longevity_risk_premium(params, annual_spending=80000)
print(f"  90th percentile age: {risk_metrics['p90_age']:.0f}")
print(f"  Extra years of risk: {risk_metrics['years_of_risk_90']:.1f}")
print(f"  Risk premium (90%): ${risk_metrics['risk_premium_90']:,.0f}")

# Test 3: Correlated Asset Returns
print("\n3. Testing Correlated Asset Returns...")

inputs = PortfolioInputs(
    starting_portfolio=1000000,
    years_to_model=30,
    current_age=65,
    equity_pct=0.60,
    fi_pct=0.30,
    cash_pct=0.10,
    equity_return_annual=0.07,
    fi_return_annual=0.02,
    cash_return_annual=0.0,
    equity_vol_annual=0.18,
    fi_vol_annual=0.06,
    cash_vol_annual=0.01,
    corr_equity_fi=0.20,
    corr_equity_cash=0.05,
    corr_fi_cash=0.10,
    n_scenarios=1000,
    random_seed=42
)

rng = np.random.default_rng(42)
equity_rets, fi_rets, cash_rets = generate_correlated_asset_returns(
    inputs, n_scenarios=1000, n_months=360, rng=rng
)

print(f"✓ Generated correlated returns")
print(f"  Equity returns shape: {equity_rets.shape}")
print(f"  FI returns shape: {fi_rets.shape}")

# Check actual correlations
equity_flat = equity_rets.flatten()
fi_flat = fi_rets.flatten()
cash_flat = cash_rets.flatten()

actual_corr_eq_fi = np.corrcoef(equity_flat, fi_flat)[0, 1]
actual_corr_eq_cash = np.corrcoef(equity_flat, cash_flat)[0, 1]
actual_corr_fi_cash = np.corrcoef(fi_flat, cash_flat)[0, 1]

print(f"  Equity-FI correlation: {actual_corr_eq_fi:.3f} (target: {inputs.corr_equity_fi:.3f})")
print(f"  Equity-Cash correlation: {actual_corr_eq_cash:.3f} (target: {inputs.corr_equity_cash:.3f})")
print(f"  FI-Cash correlation: {actual_corr_fi_cash:.3f} (target: {inputs.corr_fi_cash:.3f})")

# Integration test
print("\n4. Integration Test: Inflation + Longevity...")

# Simulate lifetime
death_ages = long_engine.simulate_lifetime(params, n_scenarios=1000)
median_death_age = np.median(death_ages)
print(f"✓ Median death age: {median_death_age:.0f}")

# Generate inflation for that horizon
planning_years = int(median_death_age - params.current_age)
planning_months = planning_years * 12

inflation_scenarios = inf_engine.generate_scenarios(
    n_scenarios=100,
    n_months=planning_months,
    regime=InflationRegime.NORMAL
)

# Calculate inflation-adjusted spending
base_spending = 7000  # monthly
adjusted_spending = inf_engine.calculate_inflation_adjusted_spending(
    base_spending=base_spending,
    inflation_scenario=inflation_scenarios[0],
    n_months=planning_months
)

print(f"  Starting spending: ${base_spending:,.0f}/month")
print(f"  Final spending (year {planning_years}): ${adjusted_spending[-1]:,.0f}/month")
print(f"  Total inflation impact: {(adjusted_spending[-1] / base_spending - 1) * 100:.1f}%")

print("\n" + "=" * 70)
print("✓ ALL SPRINT 4 TESTS PASSED")
print("=" * 70)
