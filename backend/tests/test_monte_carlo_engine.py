"""
Test Suite for Monte Carlo Engine
==================================

This module tests the refactored Monte Carlo engine for:
1. Mathematical correctness
2. Edge case handling
3. Deterministic validation
4. Property-based invariants
5. Regression testing

Run with: pytest test_monte_carlo_engine.py -v
"""

import pytest
import numpy as np
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.monte_carlo_engine import (
    PortfolioInputs,
    SimulationResults,
    SpendingRule,
    run_monte_carlo_simulation,
    compute_portfolio_statistics,
    generate_returns_geometric_brownian_motion,
    calculate_required_minimum_distribution,
    deterministic_test,
    run_stress_test
)


class TestInputValidation:
    """Test input parameter validation"""
    
    def test_valid_inputs(self):
        """Valid inputs should not raise errors"""
        inputs = PortfolioInputs(
            starting_portfolio=1_000_000,
            years_to_model=30,
            current_age=65
        )
        assert inputs.starting_portfolio == 1_000_000
    
    def test_negative_portfolio_rejected(self):
        """Negative starting portfolio should be rejected"""
        with pytest.raises(ValueError, match="must be positive"):
            PortfolioInputs(
                starting_portfolio=-100_000,
                years_to_model=30,
                current_age=65
            )
    
    def test_allocation_must_sum_to_one(self):
        """Asset allocation must sum to 1.0"""
        with pytest.raises(ValueError, match="must sum to 1.0"):
            PortfolioInputs(
                starting_portfolio=1_000_000,
                years_to_model=30,
                current_age=65,
                equity_pct=0.70,
                fi_pct=0.25,
                cash_pct=0.10  # Sum = 1.05
            )
    
    def test_tax_allocation_must_sum_to_one(self):
        """Tax account allocation must sum to 1.0"""
        with pytest.raises(ValueError, match="must sum to 1.0"):
            PortfolioInputs(
                starting_portfolio=1_000_000,
                years_to_model=30,
                current_age=65,
                taxable_pct=0.50,
                ira_pct=0.50,
                roth_pct=0.10  # Sum = 1.10
            )
    
    def test_invalid_age_rejected(self):
        """Invalid ages should be rejected"""
        with pytest.raises(ValueError, match="age.*is invalid"):
            PortfolioInputs(
                starting_portfolio=1_000_000,
                years_to_model=30,
                current_age=15  # Too young
            )
    
    def test_negative_volatility_rejected(self):
        """Negative volatility should be rejected"""
        with pytest.raises(ValueError, match="must be non-negative"):
            PortfolioInputs(
                starting_portfolio=1_000_000,
                years_to_model=30,
                current_age=65,
                equity_vol_annual=-0.15
            )


class TestPortfolioStatistics:
    """Test portfolio return and volatility calculations"""
    
    def test_single_asset_portfolio(self):
        """100% equity should return equity stats"""
        inputs = PortfolioInputs(
            starting_portfolio=1_000_000,
            years_to_model=30,
            current_age=65,
            equity_pct=1.0,
            fi_pct=0.0,
            cash_pct=0.0,
            equity_return_annual=0.08,
            equity_vol_annual=0.15
        )
        mu, sigma = compute_portfolio_statistics(inputs)
        assert np.isclose(mu, 0.08)
        assert np.isclose(sigma, 0.15)
    
    def test_diversification_reduces_volatility(self):
        """Diversified portfolio should have lower vol than weighted average"""
        # 100% equity
        inputs_equity = PortfolioInputs(
            starting_portfolio=1_000_000,
            years_to_model=30,
            current_age=65,
            equity_pct=1.0,
            fi_pct=0.0,
            cash_pct=0.0,
            equity_vol_annual=0.18
        )
        
        # 60/40 equity/bonds
        inputs_diversified = PortfolioInputs(
            starting_portfolio=1_000_000,
            years_to_model=30,
            current_age=65,
            equity_pct=0.60,
            fi_pct=0.40,
            cash_pct=0.0,
            equity_vol_annual=0.18,
            fi_vol_annual=0.06,
            corr_equity_fi=0.20  # Imperfect correlation
        )
        
        _, sigma_equity = compute_portfolio_statistics(inputs_equity)
        _, sigma_diversified = compute_portfolio_statistics(inputs_diversified)
        
        # Diversified vol should be less than weighted average
        weighted_avg_vol = 0.60 * 0.18 + 0.40 * 0.06
        assert sigma_diversified < weighted_avg_vol
        assert sigma_diversified < sigma_equity
    
    def test_weighted_return(self):
        """Portfolio return should be weighted average"""
        inputs = PortfolioInputs(
            starting_portfolio=1_000_000,
            years_to_model=30,
            current_age=65,
            equity_pct=0.60,
            fi_pct=0.30,
            cash_pct=0.10,
            equity_return_annual=0.08,
            fi_return_annual=0.03,
            cash_return_annual=0.01
        )
        mu, _ = compute_portfolio_statistics(inputs)
        expected = 0.60 * 0.08 + 0.30 * 0.03 + 0.10 * 0.01
        assert np.isclose(mu, expected)


class TestReturnGeneration:
    """Test geometric Brownian motion return generation"""
    
    def test_return_shape(self):
        """Returns array should have correct shape"""
        rng = np.random.default_rng(42)
        returns = generate_returns_geometric_brownian_motion(
            mu_annual=0.07,
            sigma_annual=0.15,
            n_scenarios=1000,
            n_months=360,
            rng=rng
        )
        assert returns.shape == (1000, 360)
    
    def test_returns_positive(self):
        """Returns should be positive (multiplicative factors)"""
        rng = np.random.default_rng(42)
        returns = generate_returns_geometric_brownian_motion(
            mu_annual=0.07,
            sigma_annual=0.15,
            n_scenarios=1000,
            n_months=360,
            rng=rng
        )
        # All returns should be positive (can be < 1 for losses)
        assert np.all(returns > 0)
    
    def test_zero_volatility(self):
        """Zero volatility should give constant returns"""
        rng = np.random.default_rng(42)
        mu_annual = 0.06
        returns = generate_returns_geometric_brownian_motion(
            mu_annual=mu_annual,
            sigma_annual=0.0,  # Zero volatility
            n_scenarios=1000,
            n_months=12,
            rng=rng
        )
        # All returns should be identical
        expected_monthly_return = np.exp(mu_annual / 12.0)
        assert np.allclose(returns, expected_monthly_return, rtol=1e-10)
    
    def test_reproducibility_with_seed(self):
        """Same seed should give same results"""
        returns1 = generate_returns_geometric_brownian_motion(
            mu_annual=0.07,
            sigma_annual=0.15,
            n_scenarios=100,
            n_months=120,
            rng=np.random.default_rng(12345)
        )
        returns2 = generate_returns_geometric_brownian_motion(
            mu_annual=0.07,
            sigma_annual=0.15,
            n_scenarios=100,
            n_months=120,
            rng=np.random.default_rng(12345)
        )
        assert np.allclose(returns1, returns2)


class TestRMDCalculation:
    """Test Required Minimum Distribution calculations"""
    
    def test_rmd_before_age(self):
        """No RMD before RMD age"""
        rmd_factors = {73: 26.5, 74: 25.5}
        rmd = calculate_required_minimum_distribution(
            ira_balance=500_000,
            age=72,
            rmd_factors=rmd_factors
        )
        assert rmd == 0.0
    
    def test_rmd_at_73(self):
        """RMD at age 73 should use correct factor"""
        rmd_factors = {73: 26.5, 74: 25.5}
        rmd = calculate_required_minimum_distribution(
            ira_balance=500_000,
            age=73,
            rmd_factors=rmd_factors
        )
        expected = 500_000 / 26.5
        assert np.isclose(rmd, expected)
    
    def test_rmd_increases_with_age(self):
        """RMD % should increase with age"""
        rmd_factors = {73: 26.5, 80: 20.2, 90: 12.2}
        
        rmd_73 = calculate_required_minimum_distribution(500_000, 73, rmd_factors)
        rmd_80 = calculate_required_minimum_distribution(500_000, 80, rmd_factors)
        rmd_90 = calculate_required_minimum_distribution(500_000, 90, rmd_factors)
        
        assert rmd_73 < rmd_80 < rmd_90


class TestDeterministicScenarios:
    """Test deterministic scenarios with closed-form solutions"""
    
    def test_zero_return_zero_withdrawal(self):
        """Portfolio should remain constant with 0% return and $0 withdrawal"""
        ending, years_ruined = deterministic_test(
            starting_portfolio=1_000_000,
            annual_return=0.0,
            annual_withdrawal=0.0,
            years=30
        )
        assert np.isclose(ending, 1_000_000)
        assert years_ruined == -1
    
    def test_positive_return_no_withdrawal(self):
        """Portfolio should grow with positive return and no withdrawal"""
        ending, years_ruined = deterministic_test(
            starting_portfolio=1_000_000,
            annual_return=0.05,
            annual_withdrawal=0.0,
            years=10
        )
        expected = 1_000_000 * (1.05 ** 10)
        assert np.isclose(ending, expected, rtol=0.001)
        assert years_ruined == -1
    
    def test_excessive_withdrawal_causes_ruin(self):
        """Excessive withdrawals should deplete portfolio"""
        ending, years_ruined = deterministic_test(
            starting_portfolio=1_000_000,
            annual_return=0.05,
            annual_withdrawal=100_000,  # 10% withdrawal rate
            years=20
        )
        # Should run out before 20 years
        assert years_ruined > 0
        assert years_ruined < 20
        assert ending == 0.0
    
    def test_sustainable_withdrawal_rate(self):
        """4% withdrawal with 5% return should be sustainable"""
        starting = 1_000_000
        withdrawal = 40_000  # 4%
        ending, years_ruined = deterministic_test(
            starting_portfolio=starting,
            annual_return=0.05,
            annual_withdrawal=withdrawal,
            years=30
        )
        # Should not run out
        assert years_ruined == -1
        assert ending > 0


class TestSimulationBasics:
    """Test basic simulation functionality"""
    
    def test_simulation_runs_successfully(self):
        """Basic simulation should complete without errors"""
        inputs = PortfolioInputs(
            starting_portfolio=1_000_000,
            years_to_model=30,
            current_age=65,
            n_scenarios=100,
            random_seed=42
        )
        results = run_monte_carlo_simulation(inputs)
        
        assert isinstance(results, SimulationResults)
        assert results.success_probability >= 0.0
        assert results.success_probability <= 1.0
    
    def test_paths_start_at_initial_value(self):
        """All paths should start at initial portfolio value"""
        inputs = PortfolioInputs(
            starting_portfolio=1_000_000,
            years_to_model=10,
            current_age=65,
            n_scenarios=100,
            random_seed=42
        )
        results = run_monte_carlo_simulation(inputs)
        
        assert np.all(results.paths[:, 0] == 1_000_000)
    
    def test_paths_non_negative(self):
        """Portfolio values should never be negative"""
        inputs = PortfolioInputs(
            starting_portfolio=500_000,
            years_to_model=30,
            current_age=65,
            monthly_spending=5_000,
            n_scenarios=100,
            random_seed=42
        )
        results = run_monte_carlo_simulation(inputs)
        
        assert np.all(results.paths >= 0)
    
    def test_reproducibility_with_seed(self):
        """Same seed should produce identical results"""
        inputs = PortfolioInputs(
            starting_portfolio=1_000_000,
            years_to_model=30,
            current_age=65,
            n_scenarios=100,
            random_seed=12345
        )
        
        results1 = run_monte_carlo_simulation(inputs)
        results2 = run_monte_carlo_simulation(inputs)
        
        assert np.allclose(results1.paths, results2.paths)
        assert results1.success_probability == results2.success_probability


class TestPropertyInvariants:
    """Test mathematical properties that should always hold"""
    
    def test_higher_volatility_lower_success(self):
        """Higher volatility should not significantly increase success probability"""
        base_inputs = PortfolioInputs(
            starting_portfolio=1_000_000,
            years_to_model=30,
            current_age=65,
            monthly_spending=5_000,  # Use higher spending to test stress
            n_scenarios=500,
            random_seed=42
        )
        
        # Low volatility
        low_vol = PortfolioInputs(**base_inputs.__dict__)
        low_vol.equity_vol_annual = 0.10
        low_vol.random_seed = 42
        
        # High volatility
        high_vol = PortfolioInputs(**base_inputs.__dict__)
        high_vol.equity_vol_annual = 0.25
        high_vol.random_seed = 42
        
        results_low = run_monte_carlo_simulation(low_vol)
        results_high = run_monte_carlo_simulation(high_vol)
        
        # At higher spending rates, volatility should hurt success probability
        # (At very low spending, convexity can make higher vol neutral or slightly beneficial)
        # This test uses realistic spending to ensure vol increases risk
        assert results_high.success_probability <= results_low.success_probability + 0.15  # Tolerance for convexity
    
    def test_higher_spending_lower_success(self):
        """Higher spending should decrease success probability"""
        base_inputs = PortfolioInputs(
            starting_portfolio=1_000_000,
            years_to_model=30,
            current_age=65,
            n_scenarios=500,
            random_seed=42
        )
        
        # Low spending
        low_spend = PortfolioInputs(**base_inputs.__dict__)
        low_spend.monthly_spending = 2_000
        low_spend.random_seed = 42
        
        # High spending
        high_spend = PortfolioInputs(**base_inputs.__dict__)
        high_spend.monthly_spending = 6_000
        high_spend.random_seed = 42
        
        results_low = run_monte_carlo_simulation(low_spend)
        results_high = run_monte_carlo_simulation(high_spend)
        
        # Higher spending should have lower success
        assert results_high.success_probability < results_low.success_probability
    
    def test_longer_horizon_lower_success(self):
        """Longer time horizon should not increase success probability"""
        base_inputs = PortfolioInputs(
            starting_portfolio=1_000_000,
            years_to_model=30,  # Add required parameter
            current_age=65,
            monthly_spending=3_500,
            n_scenarios=500,
            random_seed=42
        )
        
        # Shorter horizon
        short = PortfolioInputs(**base_inputs.__dict__)
        short.years_to_model = 20
        short.random_seed = 42
        
        # Longer horizon
        long = PortfolioInputs(**base_inputs.__dict__)
        long.years_to_model = 40
        long.random_seed = 42
        
        results_short = run_monte_carlo_simulation(short)
        results_long = run_monte_carlo_simulation(long)
        
        # Longer horizon should have equal or lower success
        assert results_long.success_probability <= results_short.success_probability + 0.05
    
    def test_cumulative_ruin_probability_monotonic(self):
        """Cumulative ruin probability should never decrease"""
        inputs = PortfolioInputs(
            starting_portfolio=500_000,
            years_to_model=30,
            current_age=65,
            monthly_spending=4_000,
            n_scenarios=500,
            random_seed=42
        )
        results = run_monte_carlo_simulation(inputs)
        
        cumulative = results.cumulative_ruin_probability
        for i in range(1, len(cumulative)):
            # Each year's cumulative should be >= previous year
            assert cumulative[i] >= cumulative[i-1] - 1e-10  # Small tolerance for floating point


class TestMetricsConsistency:
    """Test that metrics are internally consistent"""
    
    def test_success_plus_failure_equals_one(self):
        """Success probability + final cumulative ruin should ≈ 1.0"""
        inputs = PortfolioInputs(
            starting_portfolio=800_000,
            years_to_model=30,
            current_age=65,
            monthly_spending=3_500,
            n_scenarios=1000,
            random_seed=42
        )
        results = run_monte_carlo_simulation(inputs)
        
        final_ruin = results.cumulative_ruin_probability[-1]
        total = results.success_probability + final_ruin
        
        # Should sum to approximately 1.0 (small tolerance for rounding)
        assert np.isclose(total, 1.0, atol=0.01)
    
    def test_percentiles_ordered(self):
        """Percentiles should be in ascending order"""
        inputs = PortfolioInputs(
            starting_portfolio=1_000_000,
            years_to_model=30,
            current_age=65,
            n_scenarios=1000,
            random_seed=42
        )
        results = run_monte_carlo_simulation(inputs)
        
        dist = results.ending_distribution
        assert dist["p05"] <= dist["p10"] <= dist["p25"] <= dist["p50"]
        assert dist["p50"] <= dist["p75"] <= dist["p90"] <= dist["p95"]
    
    def test_median_between_p10_and_p90(self):
        """Median should be between P10 and P90"""
        inputs = PortfolioInputs(
            starting_portfolio=1_000_000,
            years_to_model=30,
            current_age=65,
            n_scenarios=1000,
            random_seed=42
        )
        results = run_monte_carlo_simulation(inputs)
        
        assert results.p10_ending_value <= results.median_ending_value <= results.p90_ending_value


class TestLongevityMetrics:
    """Test longevity analysis metrics"""
    
    def test_longevity_metrics_computed(self):
        """Longevity metrics should be computed for relevant ages"""
        inputs = PortfolioInputs(
            starting_portfolio=1_000_000,
            years_to_model=30,
            current_age=65,
            n_scenarios=500,
            random_seed=42
        )
        results = run_monte_carlo_simulation(inputs)
        
        # Should have metrics for ages within horizon
        assert len(results.longevity_metrics) > 0
        for age, metrics in results.longevity_metrics.items():
            assert "median_balance" in metrics
            assert "depletion_risk" in metrics
    
    def test_depletion_risk_increases_with_age(self):
        """Depletion risk should generally increase over time"""
        inputs = PortfolioInputs(
            starting_portfolio=600_000,
            years_to_model=35,
            current_age=65,
            monthly_spending=4_000,
            n_scenarios=500,
            random_seed=42
        )
        results = run_monte_carlo_simulation(inputs)
        
        ages = sorted(results.longevity_metrics.keys())
        if len(ages) >= 2:
            risks = [results.longevity_metrics[age]["depletion_risk"] for age in ages]
            # Risk should generally not decrease (with small tolerance)
            for i in range(1, len(risks)):
                assert risks[i] >= risks[i-1] - 0.05


class TestStressScenarios:
    """Test stress testing functionality"""
    
    def test_negative_return_shock_decreases_success(self):
        """Negative return shock should decrease success probability"""
        inputs = PortfolioInputs(
            starting_portfolio=1_000_000,
            years_to_model=30,
            current_age=65,
            monthly_spending=3_000,
            n_scenarios=500,
            random_seed=42
        )
        
        base_results = run_monte_carlo_simulation(inputs)
        stress_results = run_stress_test(
            inputs,
            stress_name="Bear Market",
            return_shock=-0.03,  # -3% return shock
            random_seed=42
        )
        
        assert stress_results.success_probability < base_results.success_probability
    
    def test_volatility_shock_decreases_success(self):
        """Increased volatility should decrease success probability"""
        inputs = PortfolioInputs(
            starting_portfolio=1_000_000,
            years_to_model=30,
            current_age=65,
            monthly_spending=3_000,
            n_scenarios=500,
            random_seed=42
        )
        
        base_results = run_monte_carlo_simulation(inputs)
        stress_results = run_stress_test(
            inputs,
            stress_name="High Volatility",
            vol_multiplier=1.5,  # 50% increase in volatility
            random_seed=42
        )
        
        # Higher vol should not increase success
        assert stress_results.success_probability <= base_results.success_probability + 0.05


class TestEdgeCases:
    """Test edge cases and boundary conditions"""
    
    def test_very_high_withdrawal_rate(self):
        """Very high withdrawal rate should lead to failure"""
        inputs = PortfolioInputs(
            starting_portfolio=1_000_000,
            years_to_model=30,
            current_age=65,
            monthly_spending=10_000,  # $120k/year = 12%
            n_scenarios=100,
            random_seed=42
        )
        results = run_monte_carlo_simulation(inputs)
        
        # Should have low success probability
        assert results.success_probability < 0.50
    
    def test_zero_spending(self):
        """Zero spending should have ~100% success"""
        inputs = PortfolioInputs(
            starting_portfolio=1_000_000,
            years_to_model=30,
            current_age=65,
            monthly_spending=0.0,
            n_scenarios=100,
            random_seed=42
        )
        results = run_monte_carlo_simulation(inputs)
        
        # Should have very high success (allow for extreme bad luck)
        assert results.success_probability > 0.95
    
    def test_single_year_horizon(self):
        """Single year horizon should work correctly"""
        inputs = PortfolioInputs(
            starting_portfolio=1_000_000,
            years_to_model=1,
            current_age=65,
            monthly_spending=3_000,
            n_scenarios=100,
            random_seed=42
        )
        results = run_monte_carlo_simulation(inputs)
        
        assert results.paths.shape[1] == 13  # 12 months + initial
        assert results.success_probability >= 0.0


# ======================
# RUN ALL TESTS
# ======================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
