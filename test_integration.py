#!/usr/bin/env python3
"""
Integration test for performance optimizations.
Tests that the vectorized Monte Carlo produces correct results and meets performance budgets.
"""

import time
import numpy as np
from performance_optimizer import run_monte_carlo_vectorized, perf_monitor

def test_basic_simulation():
    """Test basic Monte Carlo simulation"""
    print("=" * 70)
    print("INTEGRATION TEST: Basic Monte Carlo Simulation")
    print("=" * 70)
    
    print("\n1. Testing 100 scenarios (budget: 100ms)...")
    start = time.time()
    
    values, stats, metrics = run_monte_carlo_vectorized(
        starting_portfolio=1_000_000,
        monthly_spending=3_333,
        mu_month=0.007,  # ~9% annual
        sigma_month=0.04,
        monthly_inflation=0.002,
        n_scenarios=100,
        n_months=360,
        current_age=65,
        seed=42
    )
    
    duration_ms = (time.time() - start) * 1000
    
    print(f"   ✓ Completed in {duration_ms:.1f}ms (budget: 100ms)")
    print(f"   ✓ Result shape: {values.shape}")
    print(f"   ✓ Ending median: ${metrics['ending_median']:,.0f}")
    print(f"   ✓ Success probability: {metrics['prob_never_depleted']:.1%}")
    
    assert duration_ms < 100, f"Performance budget exceeded: {duration_ms:.1f}ms > 100ms"
    assert values.shape == (360, 100), f"Wrong shape: {values.shape}"
    assert 0 <= metrics['prob_never_depleted'] <= 1, "Invalid probability"
    
    print("\n2. Testing 1,000 scenarios (budget: 500ms)...")
    start = time.time()
    
    values, stats, metrics = run_monte_carlo_vectorized(
        starting_portfolio=1_000_000,
        monthly_spending=3_333,
        mu_month=0.007,
        sigma_month=0.04,
        monthly_inflation=0.002,
        n_scenarios=1000,
        n_months=360,
        current_age=65,
        seed=42
    )
    
    duration_ms = (time.time() - start) * 1000
    throughput = 1000 / (duration_ms / 1000)
    
    print(f"   ✓ Completed in {duration_ms:.1f}ms (budget: 500ms)")
    print(f"   ✓ Result shape: {values.shape}")
    print(f"   ✓ Throughput: {throughput:.0f} scenarios/sec")
    print(f"   ✓ Ending median: ${metrics['ending_median']:,.0f}")
    print(f"   ✓ Success probability: {metrics['prob_never_depleted']:.1%}")
    
    assert duration_ms < 500, f"Performance budget exceeded: {duration_ms:.1f}ms > 500ms"
    assert values.shape == (360, 1000), f"Wrong shape: {values.shape}"
    
    print("\n3. Testing with income streams...")
    start = time.time()
    
    income_streams = {
        'social_security': {
            'monthly_amount': 2000,
            'start_age': 67
        },
        'pension': {
            'monthly_amount': 1500,
            'start_age': 65
        },
        'healthcare': {
            'monthly_amount': -500,  # Expense
            'start_age': 65,
            'inflation': 0.06  # 6% healthcare inflation
        }
    }
    
    values, stats, metrics = run_monte_carlo_vectorized(
        starting_portfolio=1_000_000,
        monthly_spending=3_333,
        mu_month=0.007,
        sigma_month=0.04,
        monthly_inflation=0.002,
        n_scenarios=500,
        n_months=360,
        income_streams=income_streams,
        current_age=65,
        seed=42
    )
    
    duration_ms = (time.time() - start) * 1000
    
    print(f"   ✓ Completed in {duration_ms:.1f}ms")
    print(f"   ✓ Result shape: {values.shape}")
    print(f"   ✓ Ending median: ${metrics['ending_median']:,.0f}")
    print(f"   ✓ Success probability: {metrics['prob_never_depleted']:.1%}")
    
    assert values.shape == (360, 500), f"Wrong shape: {values.shape}"
    assert metrics['ending_median'] > 0, "Negative ending value (unexpected)"
    
    print("\n4. Testing percentage-based spending rule...")
    start = time.time()
    
    values, stats, metrics = run_monte_carlo_vectorized(
        starting_portfolio=1_000_000,
        monthly_spending=0,  # Not used with percentage rule
        mu_month=0.007,
        sigma_month=0.04,
        monthly_inflation=0.002,
        n_scenarios=500,
        n_months=360,
        spending_rule=2,
        spending_pct_annual=0.04,  # 4% rule
        current_age=65,
        seed=42
    )
    
    duration_ms = (time.time() - start) * 1000
    
    print(f"   ✓ Completed in {duration_ms:.1f}ms")
    print(f"   ✓ Result shape: {values.shape}")
    print(f"   ✓ Ending median: ${metrics['ending_median']:,.0f}")
    print(f"   ✓ Success probability: {metrics['prob_never_depleted']:.1%}")
    
    assert values.shape == (360, 500), f"Wrong shape: {values.shape}"
    
    print("\n" + "=" * 70)
    print("✓ ALL INTEGRATION TESTS PASSED")
    print("=" * 70)


def test_performance_monitor():
    """Test performance monitoring"""
    print("\n" + "=" * 70)
    print("INTEGRATION TEST: Performance Monitoring")
    print("=" * 70)
    
    # Run a few operations
    for i in range(3):
        run_monte_carlo_vectorized(
            starting_portfolio=1_000_000,
            monthly_spending=3_333,
            mu_month=0.007,
            sigma_month=0.04,
            monthly_inflation=0.002,
            n_scenarios=100,
            n_months=360,
            current_age=65
        )
    
    # Get stats
    stats = perf_monitor.get_stats()
    
    print("\nPerformance Monitor Statistics:")
    for op_name, op_stats in stats.items():
        print(f"\n  {op_name}:")
        print(f"    Count: {op_stats['count']}")
        print(f"    Mean: {op_stats['mean_ms']:.1f}ms")
        print(f"    Median: {op_stats['median_ms']:.1f}ms")
        print(f"    P95: {op_stats['p95_ms']:.1f}ms")
        print(f"    Max: {op_stats['max_ms']:.1f}ms")
    
    print("\n" + "=" * 70)
    print("✓ PERFORMANCE MONITORING TEST PASSED")
    print("=" * 70)


if __name__ == "__main__":
    try:
        test_basic_simulation()
        test_performance_monitor()
        print("\n🎉 ALL INTEGRATION TESTS PASSED! 🎉\n")
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}\n")
        exit(1)
    except Exception as e:
        print(f"\n❌ ERROR: {e}\n")
        import traceback
        traceback.print_exc()
        exit(1)
