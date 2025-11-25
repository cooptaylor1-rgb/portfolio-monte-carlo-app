import math
from dataclasses import dataclass

import numpy as np
import pandas as pd
import streamlit as st
import altair as alt


# -----------------------------
# Data structures & simulation
# -----------------------------

@dataclass
class ModelInputs:
    starting_portfolio: float = 4_500_000.0
    years_to_model: int = 30
    current_age: int = 48
    horizon_age: int = 78

    monthly_spending: float = -20_000.0  # negative = withdrawal
    inflation_annual: float = 0.03

    equity_pct: float = 0.70
    fi_pct: float = 0.25
    cash_pct: float = 0.05

    equity_return_annual: float = 0.10
    fi_return_annual: float = 0.03
    cash_return_annual: float = 0.02

    equity_vol_annual: float = 0.15
    fi_vol_annual: float = 0.05
    cash_vol_annual: float = 0.01

    n_scenarios: int = 200

    spending_rule: int = 1       # 1=fixed $, 2=% of portfolio
    spending_pct_annual: float = 0.04  # if rule=2

    one_time_cf: float = 0.0
    one_time_cf_month: int = 0   # 0 = ignore


def compute_portfolio_return_and_vol(inputs: ModelInputs) -> tuple[float, float]:
    """
    Match the logic in the 'Inputs' sheet:
    - Expected annual return = weighted average of asset returns
    - Annual volatility = sqrt(sum((weight * vol)^2)) with zero correlations
    """
    w_eq, w_fi, w_c = inputs.equity_pct, inputs.fi_pct, inputs.cash_pct

    expected_return = (
        w_eq * inputs.equity_return_annual +
        w_fi * inputs.fi_return_annual +
        w_c * inputs.cash_return_annual
    )

    variance = (
        (w_eq * inputs.equity_vol_annual) ** 2 +
        (w_fi * inputs.fi_vol_annual) ** 2 +
        (w_c * inputs.cash_vol_annual) ** 2
    )
    vol = math.sqrt(variance)
    return expected_return, vol


def run_monte_carlo(inputs: ModelInputs, seed: int | None = None):
    """
    Monthly Monte Carlo model similar in spirit to your Excel workbook.
    - Returns a tuple: (paths_df, stats_df, metrics_dict)
    """

    if seed is not None:
        np.random.seed(seed)

    months = inputs.years_to_model * 12

    # Portfolio-level parameters (annual -> monthly)
    exp_ann, vol_ann = compute_portfolio_return_and_vol(inputs)
    mu_month = (1 + exp_ann) ** (1 / 12) - 1        # geometric monthly mean
    sigma_month = vol_ann / math.sqrt(12)           # monthly vol from annual

    # Option: keep spending in nominal terms to match your Projection sheet.
    monthly_inflation = (1 + inputs.inflation_annual) ** (1 / 12) - 1

    # Simulated paths: rows = months, cols = scenarios
    values = np.zeros((months, inputs.n_scenarios), dtype=float)

    for j in range(inputs.n_scenarios):
        val = inputs.starting_portfolio
        spending = inputs.monthly_spending

        for m in range(months):
            month_index = m + 1

            # Spending rule: either fixed nominal $ or % of portfolio
            if inputs.spending_rule == 1:
                cf = spending
            else:
                # Percent of portfolio (annual) -> monthly withdrawal
                cf = -val * (inputs.spending_pct_annual / 12.0)

            # One-time cash flow (positive=inflow, negative=outflow)
            if inputs.one_time_cf_month and month_index == inputs.one_time_cf_month:
                cf += inputs.one_time_cf

            # Apply cash flow then portfolio return
            val = max(val + cf, 0.0)  # don’t let it go below 0 before returns
            rnd = np.random.normal(mu_month, sigma_month)
            val = max(val * (1.0 + rnd), 0.0)

            # Save result
            values[m, j] = val

            # Inflate spending for next month (to stay roughly in line w/ Excel logic text)
            if inputs.spending_rule == 1:
                spending *= (1 + monthly_inflation)

    # Build DataFrame with paths
    months_index = np.arange(1, months + 1)
    columns = [f"Scenario_{i+1}" for i in range(inputs.n_scenarios)]
    paths_df = pd.DataFrame(values, index=months_index, columns=columns)
    paths_df.index.name = "Month"

    # Percentiles per month (like MC_Stats: P10, P25, Median, P75, P90)
    stats_df = pd.DataFrame({
        "Month": months_index,
        "P10": np.percentile(values, 10, axis=1),
        "P25": np.percentile(values, 25, axis=1),
        "Median": np.percentile(values, 50, axis=1),
        "P75": np.percentile(values, 75, axis=1),
        "P90": np.percentile(values, 90, axis=1),
    })

    # Key metrics: ending wealth distribution and success probabilities
    ending_values = values[-1, :]
    min_values = values.min(axis=0)

    prob_never_depleted = np.mean(min_values > 0)   # stayed above 0 the whole time
    prob_positive_at_end = np.mean(ending_values > 0)

    metrics = {
        "ending_median": float(np.median(ending_values)),
        "ending_p10": float(np.percentile(ending_values, 10)),
        "ending_p90": float(np.percentile(ending_values, 90)),
        "prob_never_depleted": float(prob_never_depleted),
        "prob_positive_at_end": float(prob_positive_at_end),
    }

    return paths_df, stats_df, metrics


# -----------------------------
# Charts
# -----------------------------

def fan_chart(stats_df: pd.DataFrame, title: str = "Portfolio Value – Monte Carlo Fan Chart"):
    """
    Shaded fan chart: P10–P90 band, P25–P75 band, median line.
    """
    base = alt.Chart(stats_df).encode(
        x=alt.X("Month:Q", title="Month"),
    )

    band_10_90 = base.mark_area(opacity=0.2).encode(
        y=alt.Y("P10:Q", title="Portfolio Value"),
        y2="P90:Q"
    )

    band_25_75 = base.mark_area(opacity=0.4).encode(
        y="P25:Q",
        y2="P75:Q"
    )

    median_line = base.mark_line(size=2).encode(
        y="Median:Q",
        color=alt.value("black")
    )

    chart = (band_10_90 + band_25_75 + median_line).properties(
        title=title,
        width="container",
        height=400
    )

    return chart


# -----------------------------
# Streamlit UI
# Helper input formatters
# -----------------------------

def _dollar_input(label: str, default_value: float, key: str, help: str | None = None) -> float:
    """Sidebar text input that shows/accepts a dollar amount like $20,000."""
    default_str = f"${default_value:,.0f}"
    s = st.sidebar.text_input(label, value=default_str, key=key, help=help)

    try:
        clean = (
            s.replace("$", "")
             .replace(",", "")
             .replace(" ", "")
             .replace("(", "-")
             .replace(")", "")
        )
        if clean == "":
            return default_value
        return float(clean)
    except ValueError:
        st.sidebar.warning(f"Could not parse '{s}' as a dollar amount. Using {default_str}.")
        return default_value


def _percent_input(label: str, default_fraction: float, key: str, help: str | None = None) -> float:
    """
    Sidebar text input for percents.
    Shows '3%' for 0.03 and returns the fraction (0.03).
    """
    default_str = f"{default_fraction * 100:.1f}%"
    s = st.sidebar.text_input(label, value=default_str, key=key, help=help)

    try:
        clean = s.replace("%", "").strip()
        if clean == "":
            return default_fraction
        return float(clean) / 100.0
    except ValueError:
        st.sidebar.warning(f"Could not parse '{s}' as a percent. Using {default_str}.")
        return default_fraction


# -----------------------------
# Formatted sidebar inputs
# -----------------------------

def sidebar_inputs() -> ModelInputs:
    st.sidebar.header("Model Inputs")

    # --- Client & Horizon ---
    st.sidebar.subheader("Client & Horizon")
    starting_portfolio = st.sidebar.number_input(
        "Starting Portfolio Value ($)",
        min_value=0.0,
        value=4_500_000.0,
        step=50_000.0,
        format="%.0f"
    )
    years_to_model = st.sidebar.slider(
        "Years to Model",
        min_value=5,
        max_value=60,
        value=30,
        step=1
    )

    current_age = st.sidebar.number_input(
        "Current Age",
        min_value=0,
        max_value=120,
        value=48,
        step=1
        step=1,
        key="current_age",
    )

    horizon_age = st.sidebar.number_input(
        "Plan Horizon Age",
        min_value=current_age,
        max_value=120,
        value=78,
        step=1
        step=1,
        key="horizon_age",
    )

    years_to_model = horizon_age - current_age

    starting_portfolio = _dollar_input(
        "Starting Portfolio Value",
        default_value=4_500_000.0,
        key="starting_portfolio",
    )

    # --- Spending & Inflation ---
    st.sidebar.subheader("Spending & Inflation")
    monthly_spending = st.sidebar.number_input(
        "Monthly Spending (negative = withdrawal)",
        value=-20_000.0,
        step=1_000.0,
        format="%.0f"

    monthly_spend_abs = _dollar_input(
        "Monthly Spending",
        default_value=20_000.0,
        key="monthly_spending",
        help="Enter the monthly spending amount. It will be treated as a withdrawal.",
    )
    inflation_annual = st.sidebar.number_input(
    # Internal convention: withdrawals are negative
    monthly_spending = -abs(monthly_spend_abs)

    inflation_annual = _percent_input(
        "Annual Inflation Rate",
        min_value=0.0,
        max_value=0.10,
        value=0.03,
        step=0.005,
        format="%.3f"
        default_fraction=0.03,
        key="inflation_annual",
    )

    # --- Allocation ---
    st.sidebar.subheader("Allocation")
    equity_pct = st.sidebar.slider("Equity %", 0.0, 1.0, 0.70, 0.05)
    fi_pct = st.sidebar.slider("Fixed Income %", 0.0, 1.0, 0.25, 0.05)
    cash_pct = st.sidebar.slider("Cash %", 0.0, 1.0, 0.05, 0.01)

    equity_pct_slider = st.sidebar.slider(
        "Equity %",
        min_value=0,
        max_value=100,
        value=70,
        step=1,
        key="equity_pct",
    )
    fi_pct_slider = st.sidebar.slider(
        "Fixed Income %",
        min_value=0,
        max_value=100,
        value=25,
        step=1,
        key="fi_pct",
    )
    cash_pct_slider = st.sidebar.slider(
        "Cash %",
        min_value=0,
        max_value=100,
        value=5,
        step=1,
        key="cash_pct",
    )

    equity_pct = equity_pct_slider / 100.0
    fi_pct = fi_pct_slider / 100.0
    cash_pct = cash_pct_slider / 100.0

    alloc_sum = equity_pct + fi_pct + cash_pct
    if abs(alloc_sum - 1.0) > 1e-6:
        st.sidebar.warning(
            f"Allocation totals {alloc_sum*100:.1f}% (should be 100%). "
            "Consider adjusting Equity / Fixed Income / Cash."
        )

    # --- Return Assumptions ---
    st.sidebar.subheader("Return Assumptions (Annual, Nominal)")
    equity_return_annual = st.sidebar.number_input(

    equity_return_annual = _percent_input(
        "Equity Expected Annual Return",
        min_value=-0.20,
        max_value=0.25,
        value=0.10,
        step=0.01,
        format="%.3f"
        default_fraction=0.10,
        key="equity_return",
    )
    fi_return_annual = st.sidebar.number_input(
    fi_return_annual = _percent_input(
        "Fixed Income Expected Annual Return",
        min_value=-0.10,
        max_value=0.15,
        value=0.03,
        step=0.005,
        format="%.3f"
        default_fraction=0.03,
        key="fi_return",
    )
    cash_return_annual = st.sidebar.number_input(
    cash_return_annual = _percent_input(
        "Cash Expected Annual Return",
        min_value=-0.05,
        max_value=0.10,
        value=0.02,
        step=0.005,
        format="%.3f"
        default_fraction=0.02,
        key="cash_return",
    )

    # --- Volatility Assumptions ---
    st.sidebar.subheader("Volatility (Annual)")
    equity_vol_annual = st.sidebar.number_input(

    equity_vol_annual = _percent_input(
        "Equity Annual Volatility",
        min_value=0.0,
        max_value=0.60,
        value=0.15,
        step=0.01,
        format="%.3f"
        default_fraction=0.15,
        key="equity_vol",
    )
    fi_vol_annual = st.sidebar.number_input(
    fi_vol_annual = _percent_input(
        "Fixed Income Annual Volatility",
        min_value=0.0,
        max_value=0.40,
        value=0.05,
        step=0.005,
        format="%.3f"
        default_fraction=0.05,
        key="fi_vol",
    )
    cash_vol_annual = st.sidebar.number_input(
    cash_vol_annual = _percent_input(
        "Cash Annual Volatility",
        min_value=0.0,
        max_value=0.20,
        value=0.01,
        step=0.005,
        format="%.3f"
        default_fraction=0.01,
        key="cash_vol",
    )

    # --- Monte Carlo Settings ---
    st.sidebar.subheader("Monte Carlo Settings")

    n_scenarios = st.sidebar.slider(
        "Number of Scenarios",
        min_value=50,
        max_value=2000,
        value=200,
        step=50
        step=50,
        key="n_scenarios",
    )

    spending_rule = st.sidebar.radio(
        "Spending Rule",
        options=[1, 2],
        format_func=lambda x: "1 – Fixed $ (inflation-adjusted)" if x == 1 else "2 – % of Portfolio"
        format_func=lambda x: "1 – Fixed $ (inflation-adjusted)" if x == 1 else "2 – % of Portfolio",
        key="spending_rule",
    )
    spending_pct_annual = st.sidebar.number_input(
        "Percent of Portfolio (Annual, if Rule=2)",
        min_value=0.0,
        max_value=0.15,
        value=0.04,
        step=0.005,
        format="%.3f"

    spending_pct_annual = _percent_input(
        "Percent of Portfolio (Annual, if Rule = 2)",
        default_fraction=0.04,
        key="spending_pct_annual",
    )

    # --- One-Time Cash Flow ---
    st.sidebar.subheader("One-Time Cash Flow")
    one_time_cf = st.sidebar.number_input(
        "One-Time Cash Flow (positive=inflow, negative=outflow)",
        value=0.0,
        step=10_000.0,
        format="%.0f"

    one_time_cf = _dollar_input(
        "One-Time Cash Flow",
        default_value=0.0,
        key="one_time_cf",
        help="Positive = inflow, negative = outflow.",
    )

    one_time_cf_month = st.sidebar.number_input(
        "One-Time Cash Flow Month (1 = first month, 0 = never)",
        min_value=0,
        max_value=years_to_model * 12,
        max_value=max(years_to_model * 12, 0),
        value=0,
        step=1
        step=1,
        key="one_time_cf_month",
    )

    return ModelInputs(
        starting_portfolio=starting_portfolio,
        years_to_model=years_to_model,
        current_age=current_age,
        horizon_age=horizon_age,
        monthly_spending=monthly_spending,
        inflation_annual=inflation_annual,
        equity_pct=equity_pct,
        fi_pct=fi_pct,
        cash_pct=cash_pct,
        equity_return_annual=equity_return_annual,
        fi_return_annual=fi_return_annual,
        cash_return_annual=cash_return_annual,
        equity_vol_annual=equity_vol_annual,
        fi_vol_annual=fi_vol_annual,
        cash_vol_annual=cash_vol_annual,
        n_scenarios=n_scenarios,
        spending_rule=spending_rule,
        spending_pct_annual=spending_pct_annual,
        one_time_cf=one_time_cf,
        one_time_cf_month=one_time_cf_month,
    )


def main():
    st.set_page_config(
        page_title="Portfolio Growth Monte Carlo Scenario Analysis",
        layout="wide",
    )

    st.title("Portfolio Growth – Monte Carlo Scenario Analysis")
    st.markdown(
        """
        This application is built from your Monte Carlo scenario analysis workbook.

        Use the controls in the sidebar to adjust assumptions and instantly see
        how they affect the **distribution of outcomes** and the **probability of plan success**.
        """
    )

    inputs = sidebar_inputs()

    # Quick allocation check
    alloc_sum = inputs.equity_pct + inputs.fi_pct + inputs.cash_pct
    if abs(alloc_sum - 1.0) > 1e-6:
        st.warning(
            f"Your allocation weights sum to {alloc_sum:.3f}, not 1.0. "
            "Consider adjusting Equity/Fixed Income/Cash so they add up to 100%."
        )

    # Summary of key assumptions
    col1, col2, col3 = st.columns(3)
    exp_ann, vol_ann = compute_portfolio_return_and_vol(inputs)
    with col1:
        st.metric(
            "Starting Portfolio",
            f"${inputs.starting_portfolio:,.0f}"
        )
        st.metric(
            "Years to Model",
            f"{inputs.years_to_model} years"
        )
    with col2:
        st.metric(
            "Monthly Spending (initial)",
            f"${inputs.monthly_spending:,.0f}"
        )
        st.metric(
            "Annual Inflation",
            f"{inputs.inflation_annual*100:.1f}%"
        )
    with col3:
        st.metric(
            "Portfolio Expected Annual Return",
            f"{exp_ann*100:.2f}%"
        )
        st.metric(
            "Portfolio Annual Volatility",
            f"{vol_ann*100:.2f}%"
        )

    st.markdown("---")

    if st.button("Run Monte Carlo Simulation", type="primary"):
        with st.spinner("Running simulations..."):
            paths_df, stats_df, metrics = run_monte_carlo(inputs)

        st.subheader("Key Monte Carlo Results")

        c1, c2, c3 = st.columns(3)
        with c1:
            st.metric(
                "Median Ending Portfolio",
                f"${metrics['ending_median']:,.0f}"
            )
        with c2:
            st.metric(
                "10th Percentile Ending Portfolio",
                f"${metrics['ending_p10']:,.0f}"
            )
        with c3:
            st.metric(
                "90th Percentile Ending Portfolio",
                f"${metrics['ending_p90']:,.0f}"
            )

        c4, c5 = st.columns(2)
        with c4:
            st.metric(
                "Probability Portfolio Never Depletes",
                f"{metrics['prob_never_depleted']*100:.1f}%"
            )
        with c5:
            st.metric(
                "Probability Portfolio Positive at Horizon End",
                f"{metrics['prob_positive_at_end']*100:.1f}%"
            )

        st.markdown("---")
        st.subheader("Fan Chart of Projected Portfolio Values")

        chart = fan_chart(stats_df)
        st.altair_chart(chart, use_container_width=True)

        with st.expander("Show Percentile Table (like MC_Stats)", expanded=False):
            st.dataframe(stats_df, use_container_width=True)

        with st.expander("Show Raw Scenario Paths (like MC_Simulations)", expanded=False):
            st.dataframe(paths_df.head(100), use_container_width=True)
            st.caption("Showing first 100 months; export below for full dataset.")

        # Download links
        st.subheader("Download Simulation Results")
        stats_csv = stats_df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="Download Percentiles (MC_Stats) as CSV",
            data=stats_csv,
            file_name="mc_stats_percentiles.csv",
            mime="text/csv",
        )

        paths_csv = paths_df.to_csv().encode("utf-8")
        st.download_button(
            label="Download Scenario Paths (MC_Simulations) as CSV",
            data=paths_csv,
            file_name="mc_simulations_paths.csv",
            mime="text/csv",
        )

    else:
        st.info("Adjust inputs in the sidebar and click **Run Monte Carlo Simulation** to see results.")


if __name__ == "__main__":
    main()
~
