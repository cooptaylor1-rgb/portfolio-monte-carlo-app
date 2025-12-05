# Monte Carlo Engine Quick Start Guide

## Basic Usage

### 1. Import the Engine

```python
from backend.core.monte_carlo_engine import (
    PortfolioInputs,
    run_monte_carlo_simulation,
    SpendingRule
)
```

### 2. Create Input Parameters

```python
# Basic scenario: $1M portfolio, age 65, 30 years
inputs = PortfolioInputs(
    starting_portfolio=1_000_000,
    years_to_model=30,
    current_age=65,
    monthly_spending=4_000,  # $48k/year = 4.8% withdrawal rate
    n_scenarios=1000,
    random_seed=42  # For reproducibility
)
```

### 3. Run Simulation

```python
results = run_monte_carlo_simulation(inputs)

# Access key metrics
print(f"Success Probability: {results.success_probability:.1%}")
print(f"Median Ending Value: ${results.median_ending_value:,.0f}")
print(f"P10 Ending Value: ${results.p10_ending_value:,.0f}")
```

---

## Advanced Configuration

### Portfolio Allocation

```python
inputs = PortfolioInputs(
    starting_portfolio=1_000_000,
    years_to_model=30,
    current_age=65,
    
    # Asset allocation
    equity_pct=0.60,
    fi_pct=0.30,
    cash_pct=0.10,
    
    # Return expectations
    equity_return_annual=0.08,
    fi_return_annual=0.03,
    cash_return_annual=0.01,
    
    # Volatility
    equity_vol_annual=0.18,
    fi_vol_annual=0.06,
    cash_vol_annual=0.01,
    
    # Correlations (for proper portfolio volatility)
    corr_equity_fi=0.20,
    corr_equity_cash=0.05,
    corr_fi_cash=0.10
)
```

### Tax-Advantaged Accounts

```python
inputs = PortfolioInputs(
    starting_portfolio=1_000_000,
    years_to_model=30,
    current_age=65,
    
    # Account types
    taxable_pct=0.33,   # Taxable brokerage
    ira_pct=0.50,       # Traditional IRA/401k
    roth_pct=0.17,      # Roth IRA
    
    # Tax rates
    marginal_tax_rate=0.25,  # Ordinary income
    ltcg_tax_rate=0.15,      # Long-term capital gains
    
    # RMD age and factors
    rmd_age=73,
    rmd_factors={73: 26.5, 74: 25.5, 75: 24.6, ...}  # IRS table
)
```

### Income Sources

```python
inputs = PortfolioInputs(
    starting_portfolio=1_000_000,
    years_to_model=30,
    current_age=65,
    monthly_spending=4_000,
    
    # Social Security
    social_security_annual=30_000,
    ss_start_age=67,
    
    # Pension
    pension_annual=20_000,
    pension_start_age=65,
    pension_cola=0.02,  # 2% annual COLA
    
    # Healthcare costs
    healthcare_annual=12_000,
    healthcare_start_age=65,
    healthcare_inflation_real=0.02  # Real inflation above CPI
)
```

---

## Output Metrics

### Success Probability

```python
# Probability portfolio survives entire horizon
success_rate = results.success_probability
# Example: 0.85 = 85% chance of success
```

### Ending Distribution

```python
# Distribution of portfolio values at end
print(f"P05: ${results.ending_distribution['p05']:,.0f}")
print(f"P10: ${results.ending_distribution['p10']:,.0f}")
print(f"P25: ${results.ending_distribution['p25']:,.0f}")
print(f"P50: ${results.ending_distribution['p50']:,.0f}")  # Median
print(f"P75: ${results.ending_distribution['p75']:,.0f}")
print(f"P90: ${results.ending_distribution['p90']:,.0f}")
print(f"P95: ${results.ending_distribution['p95']:,.0f}")
```

### Ruin Probability

```python
# Annual ruin probability (first-passage)
for year, prob in enumerate(results.annual_ruin_probability, 1):
    if prob > 0.01:  # Print years with >1% risk
        print(f"Year {year}: {prob:.1%} risk of ruin")

# Cumulative ruin probability
print(f"Risk of ruin by year 10: {results.cumulative_ruin_probability[9]:.1%}")
print(f"Risk of ruin by year 20: {results.cumulative_ruin_probability[19]:.1%}")
print(f"Risk of ruin by year 30: {results.cumulative_ruin_probability[29]:.1%}")
```

### Longevity Metrics

```python
# Metrics at milestone ages
for age, metrics in results.longevity_metrics.items():
    print(f"At age {age}:")
    print(f"  Median balance: ${metrics['median_balance']:,.0f}")
    print(f"  Depletion risk: {metrics['depletion_risk']:.1%}")
```

### Time Series Data

```python
import pandas as pd

# Monthly statistics across all scenarios
df = results.monthly_stats

# Plot median path
df.plot(x='month', y='median', title='Median Portfolio Value')

# Confidence bands
df.plot(x='month', y=['p10', 'p50', 'p90'], 
        title='Portfolio Value Percentiles')
```

---

## Common Scenarios

### Conservative Retiree (60/40 Portfolio)

```python
inputs = PortfolioInputs(
    starting_portfolio=1_200_000,
    years_to_model=35,
    current_age=65,
    monthly_spending=4_000,
    
    equity_pct=0.60,
    fi_pct=0.35,
    cash_pct=0.05,
    
    equity_return_annual=0.07,
    equity_vol_annual=0.15,
    
    n_scenarios=5000,
    random_seed=42
)
```

### Aggressive Accumulator (90/10 Portfolio)

```python
inputs = PortfolioInputs(
    starting_portfolio=500_000,
    years_to_model=20,
    current_age=45,
    monthly_spending=0,  # Still accumulating
    
    equity_pct=0.90,
    fi_pct=0.05,
    cash_pct=0.05,
    
    equity_return_annual=0.09,
    equity_vol_annual=0.20,
    
    n_scenarios=1000
)
```

### High Net Worth (Roth Conversion Strategy)

```python
inputs = PortfolioInputs(
    starting_portfolio=5_000_000,
    years_to_model=30,
    current_age=60,
    monthly_spending=15_000,
    
    taxable_pct=0.40,
    ira_pct=0.30,
    roth_pct=0.30,  # Large Roth from conversions
    
    marginal_tax_rate=0.37,  # Top bracket
    ltcg_tax_rate=0.20,
    
    n_scenarios=10000
)
```

---

## Stress Testing

### Market Downturn

```python
from backend.core.monte_carlo_engine import run_stress_test

# Base case
base_results = run_monte_carlo_simulation(inputs)

# Stress: -3% return shock, 50% higher volatility
stress_results = run_stress_test(
    inputs,
    stress_name="Bear Market",
    return_shock=-0.03,
    vol_multiplier=1.5,
    random_seed=42
)

print(f"Base success: {base_results.success_probability:.1%}")
print(f"Stress success: {stress_results.success_probability:.1%}")
print(f"Impact: {(stress_results.success_probability - base_results.success_probability):.1%}")
```

### Inflation Surge

```python
stress_results = run_stress_test(
    inputs,
    stress_name="High Inflation",
    inflation_shock=0.03,  # +3% inflation
    random_seed=42
)
```

---

## Deterministic Validation

### Verify Closed-Form Solution

```python
from backend.core.monte_carlo_engine import deterministic_test

# Should match formula: V(t) = V(0)*(1+r)^t - W*[(1+r)^t - 1]/r
ending, ruin_year = deterministic_test(
    starting_portfolio=1_000_000,
    annual_return=0.05,
    annual_withdrawal=40_000,
    years=30
)

print(f"Ending value: ${ending:,.0f}")
if ruin_year > 0:
    print(f"Depleted in year {ruin_year}")
else:
    print("Portfolio survived")
```

---

## Best Practices

### 1. Use Appropriate Number of Scenarios

```python
# Quick exploration: 500-1000 scenarios (~0.5s)
inputs.n_scenarios = 1000

# Production analysis: 5000-10000 scenarios (~3-5s)
inputs.n_scenarios = 5000

# High precision: 20000+ scenarios (~10s+)
inputs.n_scenarios = 20000
```

### 2. Set Random Seed for Reproducibility

```python
inputs.random_seed = 42  # Any integer
# Same seed = identical results
```

### 3. Validate Inputs

```python
try:
    inputs = PortfolioInputs(
        starting_portfolio=-100_000  # Will raise ValueError
    )
except ValueError as e:
    print(f"Invalid input: {e}")
```

### 4. Conservative Assumptions

```python
inputs = PortfolioInputs(
    equity_return_annual=0.06,  # Conservative vs historical 8-10%
    equity_vol_annual=0.20,     # Higher than historical 15%
    monthly_spending=3_500,     # <4% withdrawal rate
    
    # Include all expenses
    advisory_fee_pct=0.0075,
    fund_expense_pct=0.0025,
    healthcare_annual=12_000
)
```

---

## Performance Tips

### 1. Vectorized Operations (Already Implemented)

The engine uses numpy vectorization for performance:
```python
# All scenarios calculated simultaneously
returns = np.exp(drift + diffusion * Z)  # (n_scenarios × n_months)
```

### 2. Batch Multiple Analyses

```python
# Run multiple scenarios in parallel
from concurrent.futures import ProcessPoolExecutor

scenarios = [
    (1_000_000, 3_000),
    (1_200_000, 3_500),
    (800_000, 2_500)
]

def run_scenario(portfolio, spending):
    inputs = PortfolioInputs(
        starting_portfolio=portfolio,
        monthly_spending=spending,
        years_to_model=30,
        current_age=65
    )
    return run_monte_carlo_simulation(inputs)

with ProcessPoolExecutor() as executor:
    results = list(executor.map(lambda s: run_scenario(*s), scenarios))
```

---

## Troubleshooting

### Issue: Success probability is 0% or 100%

**Cause:** Spending rate too high/low relative to portfolio size

**Fix:**
```python
# Check withdrawal rate
withdrawal_rate = (inputs.monthly_spending * 12) / inputs.starting_portfolio
print(f"Withdrawal rate: {withdrawal_rate:.1%}")

# Adjust spending or portfolio size
if withdrawal_rate > 0.06:  # >6% is risky
    inputs.monthly_spending = inputs.starting_portfolio * 0.04 / 12  # 4% rule
```

### Issue: Results not reproducible

**Cause:** Missing or changing random seed

**Fix:**
```python
# Always set seed for reproducible results
inputs.random_seed = 42
```

### Issue: Simulation too slow

**Cause:** Too many scenarios or too long horizon

**Fix:**
```python
# Reduce scenarios for exploration
inputs.n_scenarios = 1000  # Instead of 10000

# Or reduce horizon
inputs.years_to_model = 25  # Instead of 40
```

---

## API Integration Example

```python
from fastapi import APIRouter
from backend.core.monte_carlo_engine import PortfolioInputs, run_monte_carlo_simulation
from backend.models.schemas import SimulationRequest, SimulationResponse

router = APIRouter()

@router.post("/simulate", response_model=SimulationResponse)
def run_simulation(request: SimulationRequest):
    # Convert API request to engine inputs
    inputs = PortfolioInputs(
        starting_portfolio=request.starting_portfolio,
        years_to_model=request.years_to_model,
        current_age=request.current_age,
        monthly_spending=request.monthly_spending,
        # ... other parameters
    )
    
    # Run simulation
    results = run_monte_carlo_simulation(inputs)
    
    # Convert to API response
    return SimulationResponse(
        success_probability=results.success_probability,
        median_ending_value=results.median_ending_value,
        p10_ending_value=results.p10_ending_value,
        p90_ending_value=results.p90_ending_value,
        annual_ruin_probability=results.annual_ruin_probability,
        cumulative_ruin_probability=results.cumulative_ruin_probability,
        longevity_metrics=results.longevity_metrics,
        monthly_stats=results.monthly_stats.to_dict('records')
    )
```

---

## Further Reading

- **Mathematical Details:** See `BACKEND_REFACTORING_COMPLETE.md`
- **Test Suite:** See `backend/tests/test_monte_carlo_engine.py`
- **Source Code:** See `backend/core/monte_carlo_engine.py`

---

*Last updated: December 2024*
