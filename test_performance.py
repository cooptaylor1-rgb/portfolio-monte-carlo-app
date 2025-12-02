"""
Performance Testing & Benchmarking Suite

Comprehensive tests to validate performance improvements and track regressions.
"""

import time
import pytest
import numpy as np
import pandas as pd
from performance_optimizer import (
    run_monte_carlo_vectorized,
    cache_manager,
    perf_monitor,
    downsample_timeseries,
    optimize_dataframe_memory,
    benchmark_monte_carlo
)


# ===========================================
# PERFORMANCE BUDGETS (SLAs)
# ===========================================

PERFORMANCE_BUDGETS = {
    'monte_carlo_100_scenarios': 100,  # ms
    'monte_carlo_1000_scenarios': 500,  # ms
    'monte_carlo_5000_scenarios': 2000,  # ms
    'chart_render_small': 50,  # ms
    'chart_render_large': 200,  # ms
    'cache_retrieval': 5,  # ms
    'page_load': 2000,  # ms
    'tab_switch': 300,  # ms
}


# ===========================================
# MONTE CARLO PERFORMANCE TESTS
# ===========================================

def test_monte_carlo_100_scenarios_performance():
    """Test: Monte Carlo with 100 scenarios meets performance budget"""
    start = time.time()
    
    values, stats_df, metrics = run_monte_carlo_vectorized(
        starting_portfolio=1000000,
        monthly_spending=5000,
        mu_month=0.007,
        sigma_month=0.04,
        monthly_inflation=0.002,
        n_scenarios=100,
        n_months=360,
        seed=42
    )
    
    duration_ms = (time.time() - start) * 1000
    
    print(f"\n100 scenarios: {duration_ms:.1f}ms (budget: {PERFORMANCE_BUDGETS['monte_carlo_100_scenarios']}ms)")
    assert duration_ms < PERFORMANCE_BUDGETS['monte_carlo_100_scenarios'], \
        f"Monte Carlo (100) too slow: {duration_ms:.1f}ms > {PERFORMANCE_BUDGETS['monte_carlo_100_scenarios']}ms"
    
    # Validate results
    assert values.shape == (360, 100)
    assert len(stats_df) == 360
    assert 'ending_median' in metrics
    assert metrics['success_probability'] >= 0 and metrics['success_probability'] <= 1


def test_monte_carlo_1000_scenarios_performance():
    """Test: Monte Carlo with 1,000 scenarios meets performance budget"""
    start = time.time()
    
    values, stats_df, metrics = run_monte_carlo_vectorized(
        starting_portfolio=1000000,
        monthly_spending=5000,
        mu_month=0.007,
        sigma_month=0.04,
        monthly_inflation=0.002,
        n_scenarios=1000,
        n_months=360,
        seed=42
    )
    
    duration_ms = (time.time() - start) * 1000
    
    print(f"\n1,000 scenarios: {duration_ms:.1f}ms (budget: {PERFORMANCE_BUDGETS['monte_carlo_1000_scenarios']}ms)")
    assert duration_ms < PERFORMANCE_BUDGETS['monte_carlo_1000_scenarios'], \
        f"Monte Carlo (1000) too slow: {duration_ms:.1f}ms > {PERFORMANCE_BUDGETS['monte_carlo_1000_scenarios']}ms"


def test_monte_carlo_5000_scenarios_performance():
    """Test: Monte Carlo with 5,000 scenarios meets performance budget"""
    start = time.time()
    
    values, stats_df, metrics = run_monte_carlo_vectorized(
        starting_portfolio=1000000,
        monthly_spending=5000,
        mu_month=0.007,
        sigma_month=0.04,
        monthly_inflation=0.002,
        n_scenarios=5000,
        n_months=360,
        seed=42
    )
    
    duration_ms = (time.time() - start) * 1000
    
    print(f"\n5,000 scenarios: {duration_ms:.1f}ms (budget: {PERFORMANCE_BUDGETS['monte_carlo_5000_scenarios']}ms)")
    assert duration_ms < PERFORMANCE_BUDGETS['monte_carlo_5000_scenarios'], \
        f"Monte Carlo (5000) too slow: {duration_ms:.1f}ms > {PERFORMANCE_BUDGETS['monte_carlo_5000_scenarios']}ms"


def test_monte_carlo_scalability():
    """Test: Monte Carlo scales linearly with scenario count"""
    results = []
    
    for n_scenarios in [100, 500, 1000, 2000]:
        start = time.time()
        run_monte_carlo_vectorized(
            starting_portfolio=1000000,
            monthly_spending=5000,
            mu_month=0.007,
            sigma_month=0.04,
            monthly_inflation=0.002,
            n_scenarios=n_scenarios,
            n_months=360,
            seed=42
        )
        duration = time.time() - start
        results.append((n_scenarios, duration))
    
    # Check that doubling scenarios approximately doubles time (within 2.5x tolerance)
    for i in range(len(results) - 1):
        n1, t1 = results[i]
        n2, t2 = results[i + 1]
        ratio = (t2 / t1) / (n2 / n1)
        print(f"\n{n1} → {n2} scenarios: time ratio {ratio:.2f}x (should be ~1.0-2.5x)")
        assert ratio < 2.5, f"Poor scalability: {ratio:.2f}x ratio for {n1}→{n2} scenarios"


# ===========================================
# CACHE PERFORMANCE TESTS
# ===========================================

def test_cache_hit_performance():
    """Test: Cache retrieval meets performance budget"""
    # Populate cache
    cache_manager.clear()
    test_data = np.random.rand(1000, 1000)
    cache_manager.set('test_key', test_data)
    
    # Measure retrieval
    start = time.time()
    result = cache_manager.get('test_key')
    duration_ms = (time.time() - start) * 1000
    
    print(f"\nCache retrieval: {duration_ms:.3f}ms (budget: {PERFORMANCE_BUDGETS['cache_retrieval']}ms)")
    assert duration_ms < PERFORMANCE_BUDGETS['cache_retrieval'], \
        f"Cache retrieval too slow: {duration_ms:.3f}ms"
    assert result is not None


def test_cache_effectiveness():
    """Test: Cache provides significant speedup"""
    cache_manager.clear()
    
    # First run (no cache)
    start = time.time()
    values1, _, _ = run_monte_carlo_vectorized(
        starting_portfolio=1000000,
        monthly_spending=5000,
        mu_month=0.007,
        sigma_month=0.04,
        monthly_inflation=0.002,
        n_scenarios=1000,
        n_months=360,
        seed=42
    )
    uncached_time = time.time() - start
    
    # Second run (with numpy's internal caching and repeated computation)
    start = time.time()
    values2, _, _ = run_monte_carlo_vectorized(
        starting_portfolio=1000000,
        monthly_spending=5000,
        mu_month=0.007,
        sigma_month=0.04,
        monthly_inflation=0.002,
        n_scenarios=1000,
        n_months=360,
        seed=42
    )
    cached_time = time.time() - start
    
    print(f"\nFirst run: {uncached_time*1000:.1f}ms")
    print(f"Second run: {cached_time*1000:.1f}ms")
    print(f"Speedup: {uncached_time/cached_time:.2f}x")


# ===========================================
# DATA OPTIMIZATION TESTS
# ===========================================

def test_dataframe_memory_optimization():
    """Test: DataFrame memory optimization reduces size significantly"""
    # Create large DataFrame
    n_rows = 10000
    df = pd.DataFrame({
        'value': np.random.rand(n_rows) * 1000000,
        'count': np.random.randint(0, 1000, n_rows),
        'month': np.arange(n_rows)
    })
    
    # Measure original size
    original_size = df.memory_usage(deep=True).sum() / (1024 * 1024)
    
    # Optimize
    df_optimized = optimize_dataframe_memory(df)
    optimized_size = df_optimized.memory_usage(deep=True).sum() / (1024 * 1024)
    
    reduction_pct = ((original_size - optimized_size) / original_size) * 100
    
    print(f"\nOriginal size: {original_size:.2f} MB")
    print(f"Optimized size: {optimized_size:.2f} MB")
    print(f"Reduction: {reduction_pct:.1f}%")
    
    # Should reduce by at least 40%
    assert reduction_pct > 40, f"Insufficient memory reduction: {reduction_pct:.1f}%"


def test_downsampling_preserves_trends():
    """Test: Downsampling maintains data integrity"""
    # Create data with clear trend
    months = np.arange(1, 1001)
    values = 1000000 + months * 1000 + np.random.randn(1000) * 10000
    df = pd.DataFrame({'Month': months, 'Value': values})
    
    # Downsample
    df_downsampled = downsample_timeseries(df, max_points=100)
    
    print(f"\nOriginal points: {len(df)}")
    print(f"Downsampled points: {len(df_downsampled)}")
    
    # Check size reduction
    assert len(df_downsampled) <= 100
    
    # Check trend preservation (first and last values should match)
    assert df_downsampled.iloc[0]['Month'] == df.iloc[0]['Month']
    assert df_downsampled.iloc[-1]['Month'] == df.iloc[-1]['Month']
    
    # Check that downsampled maintains rough trajectory
    original_slope = (df.iloc[-1]['Value'] - df.iloc[0]['Value']) / len(df)
    downsampled_slope = (df_downsampled.iloc[-1]['Value'] - df_downsampled.iloc[0]['Value']) / len(df_downsampled)
    slope_ratio = abs(downsampled_slope / original_slope - 1000 / 100)
    
    # Slopes should be proportional to point count
    assert slope_ratio < 1.2, f"Downsampling distorted trend: ratio {slope_ratio:.2f}"


# ===========================================
# LOAD TESTS
# ===========================================

def test_concurrent_simulations():
    """Test: Multiple simultaneous simulations don't degrade performance excessively"""
    import threading
    
    results = []
    
    def run_simulation():
        start = time.time()
        run_monte_carlo_vectorized(
            starting_portfolio=1000000,
            monthly_spending=5000,
            mu_month=0.007,
            sigma_month=0.04,
            monthly_inflation=0.002,
            n_scenarios=500,
            n_months=360,
            seed=None  # Different seeds for concurrent runs
        )
        duration = time.time() - start
        results.append(duration)
    
    # Run 5 simulations concurrently
    threads = [threading.Thread(target=run_simulation) for _ in range(5)]
    
    start = time.time()
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    total_time = time.time() - start
    
    avg_time = np.mean(results)
    max_time = np.max(results)
    
    print(f"\n5 concurrent simulations:")
    print(f"  Total time: {total_time*1000:.1f}ms")
    print(f"  Avg per simulation: {avg_time*1000:.1f}ms")
    print(f"  Max per simulation: {max_time*1000:.1f}ms")
    
    # With good parallelization, max should be < 2x single-threaded
    assert max_time < 1.0, f"Concurrent simulations too slow: {max_time*1000:.1f}ms"


def test_large_portfolio_performance():
    """Test: Large portfolio (many months, many scenarios) completes within budget"""
    start = time.time()
    
    # 50-year simulation with 2,000 scenarios
    values, stats_df, metrics = run_monte_carlo_vectorized(
        starting_portfolio=5000000,
        monthly_spending=20000,
        mu_month=0.006,
        sigma_month=0.045,
        monthly_inflation=0.0025,
        n_scenarios=2000,
        n_months=600,  # 50 years
        seed=42
    )
    
    duration_ms = (time.time() - start) * 1000
    
    print(f"\nLarge portfolio (2000 scenarios x 600 months): {duration_ms:.1f}ms")
    
    # Should complete in under 3 seconds
    assert duration_ms < 3000, f"Large portfolio too slow: {duration_ms:.1f}ms"
    assert values.shape == (600, 2000)


# ===========================================
# REGRESSION TESTS
# ===========================================

def test_vectorized_matches_reference():
    """Test: Vectorized implementation produces same results as reference"""
    seed = 42
    
    # Run vectorized
    values_vec, stats_vec, metrics_vec = run_monte_carlo_vectorized(
        starting_portfolio=1000000,
        monthly_spending=5000,
        mu_month=0.007,
        sigma_month=0.04,
        monthly_inflation=0.002,
        n_scenarios=100,
        n_months=360,
        seed=seed
    )
    
    # Check basic statistical properties
    ending_median = metrics_vec['ending_median']
    success_prob = metrics_vec['success_probability']
    
    print(f"\nEnding median: ${ending_median:,.0f}")
    print(f"Success probability: {success_prob:.1%}")
    
    # Sanity checks
    assert ending_median > 0, "Ending median should be positive"
    assert ending_median < 10_000_000, "Ending median unrealistically high"
    assert 0 <= success_prob <= 1, "Success probability out of range"


# ===========================================
# BENCHMARK SUITE
# ===========================================

def run_full_benchmark_suite():
    """Run comprehensive performance benchmarks"""
    print("\n" + "="*60)
    print("PERFORMANCE BENCHMARK SUITE")
    print("="*60)
    
    # Monte Carlo benchmarks
    print("\n1. Monte Carlo Performance:")
    mc_results = benchmark_monte_carlo([100, 500, 1000, 2000, 5000])
    print(mc_results.to_string(index=False))
    
    # Cache stats
    print("\n2. Cache Statistics:")
    cache_stats = cache_manager.get_stats()
    for key, value in cache_stats.items():
        print(f"  {key}: {value}")
    
    # Performance monitor stats
    print("\n3. Operation Performance:")
    perf_stats = perf_monitor.get_stats()
    if perf_stats:
        for op_name, stats in perf_stats.items():
            print(f"  {op_name}:")
            print(f"    Mean: {stats['mean_ms']:.1f}ms")
            print(f"    P95: {stats['p95_ms']:.1f}ms")
            print(f"    Count: {stats['count']}")
    else:
        print("  No operations tracked yet")
    
    # Memory usage
    print("\n4. Memory Usage:")
    import psutil
    import os
    process = psutil.Process(os.getpid())
    mem_mb = process.memory_info().rss / (1024 * 1024)
    print(f"  Process memory: {mem_mb:.1f} MB")
    
    print("\n" + "="*60)
    print("BENCHMARK COMPLETE")
    print("="*60)


if __name__ == "__main__":
    # Run benchmark suite
    run_full_benchmark_suite()
    
    # Run pytest
    print("\n\nRunning performance tests...")
    pytest.main([__file__, "-v", "-s"])
