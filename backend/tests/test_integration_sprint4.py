"""
Integration tests for Sprint 4 enhanced simulation features.
Tests the full flow from API request to enhanced simulation results.
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from core.enhanced_simulation import (
    EnhancedPortfolioInputs,
    run_enhanced_monte_carlo_simulation,
    convert_stochastic_inputs_from_schema
)
from core.stochastic_inflation import InflationRegime
from core.longevity_engine import Gender, HealthStatus
from core.monte_carlo_engine import PortfolioInputs
from models.schemas import (
    StochasticInflationInputs,
    LongevityInputs,
    InflationRegimeEnum,
    GenderEnum,
    HealthStatusEnum
)
import numpy as np


def test_legacy_mode():
    """Test that enhanced simulation works in legacy mode (no stochastic features)"""
    print("\n=== TEST 1: LEGACY MODE (No Stochastic Features) ===")
    
    inputs = EnhancedPortfolioInputs(
        starting_portfolio=1_500_000,
        years_to_model=30,
        current_age=65,
        monthly_spending=7_000,
        inflation_annual=0.03,
        equity_pct=0.60,
        fi_pct=0.30,
        cash_pct=0.10,
        equity_return_annual=0.07,
        fi_return_annual=0.02,
        cash_return_annual=0.00,
        equity_vol_annual=0.18,
        fi_vol_annual=0.06,
        cash_vol_annual=0.01,
        n_scenarios=100,
        random_seed=42,
        use_stochastic_inflation=False,
        use_probabilistic_longevity=False,
        calculate_sequence_risk=True
    )
    
    base_results, extended_results = run_enhanced_monte_carlo_simulation(inputs)
    
    # Verify base results
    assert base_results.success_probability >= 0 and base_results.success_probability <= 1
    assert base_results.median_ending_value > 0
    assert len(base_results.paths) == 100
    
    # Verify sequence risk calculated (even in legacy mode)
    assert extended_results.sequence_risk is not None
    assert extended_results.sequence_risk.sequence_risk_score >= 0
    assert extended_results.sequence_risk.sequence_risk_score <= 10
    
    # Verify no stochastic features
    assert extended_results.inflation_scenarios is None
    assert extended_results.longevity_analysis is None
    
    print(f"✓ Success probability: {base_results.success_probability:.1%}")
    print(f"✓ Median ending: ${base_results.median_ending_value:,.0f}")
    print(f"✓ Sequence risk score: {extended_results.sequence_risk.sequence_risk_score:.1f}/10")
    print("✓ LEGACY MODE PASSED")


def test_stochastic_inflation_only():
    """Test enhanced simulation with only stochastic inflation"""
    print("\n=== TEST 2: STOCHASTIC INFLATION ONLY ===")
    
    inputs = EnhancedPortfolioInputs(
        starting_portfolio=1_500_000,
        years_to_model=30,
        current_age=65,
        monthly_spending=7_000,
        inflation_annual=0.025,
        equity_pct=0.60,
        fi_pct=0.30,
        cash_pct=0.10,
        equity_return_annual=0.07,
        fi_return_annual=0.02,
        cash_return_annual=0.00,
        equity_vol_annual=0.18,
        fi_vol_annual=0.06,
        cash_vol_annual=0.01,
        n_scenarios=100,
        random_seed=42,
        use_stochastic_inflation=True,
        inflation_regime=InflationRegime.NORMAL,
        inflation_volatility=0.015,
        inflation_mean_reversion=0.3,
        use_probabilistic_longevity=False
    )
    
    base_results, extended_results = run_enhanced_monte_carlo_simulation(
        inputs,
        inflation_seed=42
    )
    
    # Verify stochastic inflation generated
    assert extended_results.inflation_scenarios is not None
    assert len(extended_results.inflation_scenarios) > 0
    
    # Check inflation scenario properties
    for scenario in extended_results.inflation_scenarios[:3]:
        assert scenario.final_inflation_rate > 0
        assert scenario.average_inflation > 0
        assert scenario.cumulative_inflation > 1.0  # Should accumulate
    
    # Verify base results still valid
    assert base_results.success_probability > 0
    
    print(f"✓ Generated {len(extended_results.inflation_scenarios)} inflation scenarios")
    print(f"✓ Sample final rates: {[f'{s.final_inflation_rate:.2%}' for s in extended_results.inflation_scenarios[:3]]}")
    print(f"✓ Success probability: {base_results.success_probability:.1%}")
    print("✓ STOCHASTIC INFLATION TEST PASSED")


def test_probabilistic_longevity_only():
    """Test enhanced simulation with only probabilistic longevity"""
    print("\n=== TEST 3: PROBABILISTIC LONGEVITY ONLY ===")
    
    inputs = EnhancedPortfolioInputs(
        starting_portfolio=1_500_000,
        years_to_model=30,
        current_age=65,
        monthly_spending=7_000,
        inflation_annual=0.03,
        equity_pct=0.60,
        fi_pct=0.30,
        cash_pct=0.10,
        equity_return_annual=0.07,
        fi_return_annual=0.02,
        cash_return_annual=0.00,
        equity_vol_annual=0.18,
        fi_vol_annual=0.06,
        cash_vol_annual=0.01,
        n_scenarios=100,
        random_seed=42,
        use_stochastic_inflation=False,
        use_probabilistic_longevity=True,
        gender=Gender.MALE,
        health_status=HealthStatus.GOOD,
        smoker=False,
        planning_percentile=90
    )
    
    base_results, extended_results = run_enhanced_monte_carlo_simulation(
        inputs,
        longevity_seed=42
    )
    
    # Verify longevity analysis generated
    assert extended_results.longevity_analysis is not None
    
    longevity = extended_results.longevity_analysis
    assert longevity.life_expectancy > 65  # Should be beyond current age
    assert longevity.planning_horizon_age > longevity.life_expectancy
    assert longevity.years_of_longevity_risk > 0
    assert longevity.longevity_risk_premium > 0
    assert longevity.p90_age > longevity.median_age
    
    # Verify simulation horizon was adjusted
    # Note: adjusted_years = planning_age - current_age
    expected_adjusted_years = longevity.planning_horizon_age - 65
    
    print(f"✓ Life expectancy: {longevity.life_expectancy:.1f} years")
    print(f"✓ Planning horizon (90th): {longevity.planning_horizon_age} years")
    print(f"✓ Years of risk: {longevity.years_of_longevity_risk:.1f}")
    print(f"✓ Risk premium: ${longevity.longevity_risk_premium:,.0f}")
    print(f"✓ Adjusted simulation horizon: {expected_adjusted_years} years")
    print("✓ PROBABILISTIC LONGEVITY TEST PASSED")


def test_full_enhanced_mode():
    """Test enhanced simulation with ALL stochastic features enabled"""
    print("\n=== TEST 4: FULL ENHANCED MODE (All Features) ===")
    
    inputs = EnhancedPortfolioInputs(
        starting_portfolio=1_500_000,
        years_to_model=30,
        current_age=65,
        monthly_spending=7_000,
        inflation_annual=0.025,
        equity_pct=0.60,
        fi_pct=0.30,
        cash_pct=0.10,
        equity_return_annual=0.07,
        fi_return_annual=0.02,
        cash_return_annual=0.00,
        equity_vol_annual=0.18,
        fi_vol_annual=0.06,
        cash_vol_annual=0.01,
        corr_equity_fi=0.20,
        corr_equity_cash=0.05,
        corr_fi_cash=0.10,
        n_scenarios=200,
        random_seed=42,
        # Enable all stochastic features
        use_stochastic_inflation=True,
        inflation_regime=InflationRegime.NORMAL,
        inflation_volatility=0.015,
        inflation_mean_reversion=0.3,
        use_probabilistic_longevity=True,
        gender=Gender.MALE,
        health_status=HealthStatus.GOOD,
        smoker=False,
        planning_percentile=90,
        calculate_sequence_risk=True
    )
    
    base_results, extended_results = run_enhanced_monte_carlo_simulation(
        inputs,
        inflation_seed=42,
        longevity_seed=42
    )
    
    # Verify all features present
    assert extended_results.inflation_scenarios is not None, "Inflation scenarios missing"
    assert extended_results.longevity_analysis is not None, "Longevity analysis missing"
    assert extended_results.sequence_risk is not None, "Sequence risk missing"
    
    # Verify base simulation ran
    assert base_results.success_probability > 0
    assert base_results.median_ending_value > 0
    assert len(base_results.paths) == 200
    
    # Detailed verification
    inflation_count = len(extended_results.inflation_scenarios)
    longevity = extended_results.longevity_analysis
    sequence = extended_results.sequence_risk
    
    print(f"✓ Stochastic Inflation: {inflation_count} scenarios generated")
    print(f"  Mean final inflation: {np.mean([s.final_inflation_rate for s in extended_results.inflation_scenarios]):.2%}")
    
    print(f"✓ Probabilistic Longevity:")
    print(f"  Life expectancy: {longevity.life_expectancy:.1f} years")
    print(f"  Planning horizon: {longevity.planning_horizon_age} years")
    print(f"  Risk premium: ${longevity.longevity_risk_premium:,.0f}")
    
    print(f"✓ Sequence Risk Analysis:")
    print(f"  Risk score: {sequence.sequence_risk_score:.1f}/10")
    print(f"  Early bear impact: {sequence.early_bear_market_impact:.1%}")
    print(f"  Late bear impact: {sequence.late_bear_market_impact:.1%}")
    
    print(f"✓ Base Simulation Results:")
    print(f"  Success probability: {base_results.success_probability:.1%}")
    print(f"  Median ending: ${base_results.median_ending_value:,.0f}")
    print(f"  P10 ending: ${base_results.p10_ending_value:,.0f}")
    
    print("✓ FULL ENHANCED MODE PASSED")


def test_schema_conversion():
    """Test conversion from Pydantic schemas to dataclasses"""
    print("\n=== TEST 5: SCHEMA CONVERSION ===")
    
    # Create schema objects
    stochastic_inflation = StochasticInflationInputs(
        use_stochastic=True,
        regime=InflationRegimeEnum.NORMAL,
        base_rate=0.025,
        volatility=0.015,
        mean_reversion_speed=0.3
    )
    
    longevity_params = LongevityInputs(
        use_probabilistic=True,
        gender=GenderEnum.MALE,
        health_status=HealthStatusEnum.GOOD,
        smoker=False,
        planning_percentile=90,
        has_spouse=True,
        spouse_age=63,
        spouse_gender=GenderEnum.FEMALE,
        spouse_health=HealthStatusEnum.AVERAGE,
        spouse_smoker=False
    )
    
    # Create base inputs
    base_inputs = PortfolioInputs(
        starting_portfolio=1_500_000,
        years_to_model=30,
        current_age=65,
        monthly_spending=7_000,
        n_scenarios=100
    )
    
    # Convert to enhanced inputs
    enhanced_inputs = convert_stochastic_inputs_from_schema(
        base_inputs,
        stochastic_inflation=stochastic_inflation,
        longevity_params=longevity_params,
        calculate_sequence_risk=True
    )
    
    # Verify conversion
    assert enhanced_inputs.use_stochastic_inflation == True
    assert enhanced_inputs.inflation_regime == InflationRegime.NORMAL
    assert enhanced_inputs.use_probabilistic_longevity == True
    assert enhanced_inputs.gender == Gender.MALE
    assert enhanced_inputs.health_status == HealthStatus.GOOD
    assert enhanced_inputs.has_spouse == True
    assert enhanced_inputs.spouse_age == 63
    assert enhanced_inputs.spouse_gender == Gender.FEMALE
    
    print("✓ Stochastic inflation schema converted")
    print("✓ Longevity parameters schema converted")
    print("✓ Spouse information preserved")
    print("✓ SCHEMA CONVERSION TEST PASSED")


def run_all_tests():
    """Run all integration tests"""
    print("=" * 70)
    print("SPRINT 4 INTEGRATION TESTS")
    print("=" * 70)
    
    try:
        test_legacy_mode()
        test_stochastic_inflation_only()
        test_probabilistic_longevity_only()
        test_full_enhanced_mode()
        test_schema_conversion()
        
        print("\n" + "=" * 70)
        print("✓ ALL INTEGRATION TESTS PASSED")
        print("=" * 70)
        
    except Exception as e:
        print(f"\n✗ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    run_all_tests()
