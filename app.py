import math
from dataclasses import dataclass
from typing import List, Tuple

import numpy as np
import pandas as pd
import streamlit as st
import altair as alt


# -----------------------------
# Core dataclasses
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


@dataclass
class StressTestScenario:
    name: str
    return_delta: float    # additive annual return change (e.g. -0.02 = -2%)
    spending_delta: float  # multiplicative change in spending (e.g. 0.10 = +10%)
    inflation_delta: float # additive annual inflation change (e.g. 0.01 = +1%)


# -----------------------------
# Core simulation helpers
# -----------------------------

def compute_portfolio_return_and_vol(inputs: ModelInputs) -> Tuple[float, float]:
    """Expected annual return and volatility for the blended portfolio.

    Expected annual return = weighted average of asset returns.
    Annual volatility = sqrt(sum((weight * vol)^2)) with zero correlations.
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
    """Monthly Monte Carlo model. Returns (paths_df, stats_df, metrics_dict)."""
    if seed is not None:
        np.random.seed(seed)

    months = inputs.years_to_model * 12

    # Portfolio-level parameters (annual -> monthly)
    exp_ann, vol_ann = compute_portfolio_return_and_vol(inputs)
    mu_month = (1 + exp_ann) ** (1 / 12) - 1        # geometric monthly mean
    sigma_month = vol_ann / math.sqrt(12)           # monthly vol

    monthly_inflation = (1 + inputs.inflation_annual) ** (1 / 12) - 1

    values = np.zeros((months, inputs.n_scenarios), dtype=float)

    for j in range(inputs.n_scenarios):
        val = inputs.starting_portfolio
        spending = inputs.monthly_spending

        for m in range(months):
            month_index = m + 1

            # Spending rule
            if inputs.spending_rule == 1:
                cf = spending
            else:
                cf = -val * (inputs.spending_pct_annual / 12.0)

            # One-time cash flow
            if inputs.one_time_cf_month and month_index == inputs.one_time_cf_month:
                cf += inputs.one_time_cf

            # Apply cash flow then random return
            val = max(val + cf, 0.0)
            rnd = np.random.normal(mu_month, sigma_month)
            val = max(val * (1.0 + rnd), 0.0)

            values[m, j] = val

            # Inflate spending for next month (fixed-$ rule)
            if inputs.spending_rule == 1:
                spending *= (1 + monthly_inflation)

    months_index = np.arange(1, months + 1)
    columns = [f"Scenario_{i+1}" for i in range(inputs.n_scenarios)]
    paths_df = pd.DataFrame(values, index=months_index, columns=columns)
    paths_df.index.name = "Month"

    stats_df = pd.DataFrame({
        "Month": months_index,
        "P10": np.percentile(values, 10, axis=1),
        "P25": np.percentile(values, 25, axis=1),
        "Median": np.percentile(values, 50, axis=1),
        "P75": np.percentile(values, 75, axis=1),
        "P90": np.percentile(values, 90, axis=1),
    })

    ending_values = values[-1, :]
    min_values = values.min(axis=0)

    prob_never_depleted = np.mean(min_values > 0)
    prob_positive_at_end = np.mean(ending_values > 0)

    metrics = {
        "ending_median": float(np.median(ending_values)),
        "ending_p10": float(np.percentile(ending_values, 10)),
        "ending_p90": float(np.percentile(ending_values, 90)),
        "prob_never_depleted": float(prob_never_depleted),
        "prob_positive_at_end": float(prob_positive_at_end),
    }

    return paths_df, stats_df, metrics


def fan_chart(stats_df: pd.DataFrame, title: str = "Portfolio Value – Monte Carlo Fan Chart"):
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
    """Sidebar text input for percents. Shows '3%' for 0.03, returns 0.03."""
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
# Sidebar inputs (with Stress Tests)
# -----------------------------

def sidebar_inputs() -> Tuple[ModelInputs, List[StressTestScenario]]:
    st.sidebar.header("Model Inputs")

    # --- Client & Horizon ---
    st.sidebar.subheader("Client & Horizon")

    current_age = st.sidebar.number_input(
        "Current Age",
        min_value=0,
        max_value=120,
        value=48,
        step=1,
        key="current_age",
    )

    horizon_age = st.sidebar.number_input(
        "Plan Horizon Age",
        min_value=current_age,
        max_value=120,
        value=78,
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

    monthly_spend_abs = _dollar_input(
        "Monthly Spending",
        default_value=20_000.0,
        key="monthly_spending",
        help="Enter the monthly spending amount. It will be treated as a withdrawal.",
    )
    monthly_spending = -abs(monthly_spend_abs)  # withdrawals negative

    inflation_annual = _percent_input(
        "Annual Inflation Rate",
        default_fraction=0.03,
        key="inflation_annual",
    )

    # --- Allocation ---
    st.sidebar.subheader("Allocation")

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

    equity_return_annual = _percent_input(
        "Equity Expected Annual Return",
        default_fraction=0.10,
        key="equity_return",
    )
    fi_return_annual = _percent_input(
        "Fixed Income Expected Annual Return",
        default_fraction=0.03,
        key="fi_return",
    )
    cash_return_annual = _percent_input(
        "Cash Expected Annual Return",
        default_fraction=0.02,
        key="cash_return",
    )

    # --- Volatility Assumptions ---
    st.sidebar.subheader("Volatility (Annual)")

    equity_vol_annual = _percent_input(
        "Equity Annual Volatility",
        default_fraction=0.15,
        key="equity_vol",
    )
    fi_vol_annual = _percent_input(
        "Fixed Income Annual Volatility",
        default_fraction=0.05,
        key="fi_vol",
    )
    cash_vol_annual = _percent_input(
        "Cash Annual Volatility",
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
        step=50,
        key="n_scenarios",
    )

    spending_rule = st.sidebar.radio(
        "Spending Rule",
        options=[1, 2],
        format_func=lambda x: "1 – Fixed $ (inflation-adjusted)" if x == 1 else "2 – % of Portfolio",
        key="spending_rule",
    )

    spending_pct_annual = _percent_input(
        "Percent of Portfolio (Annual, if Rule = 2)",
        default_fraction=0.04,
        key="spending_pct_annual",
    )

    # --- One-Time Cash Flow ---
    st.sidebar.subheader("One-Time Cash Flow")

    one_time_cf = _dollar_input(
        "One-Time Cash Flow",
        default_value=0.0,
        key="one_time_cf",
        help="Positive = inflow, negative = outflow.",
    )

    one_time_cf_month = st.sidebar.number_input(
        "One-Time Cash Flow Month (1 = first month, 0 = never)",
        min_value=0,
        max_value=max(years_to_model * 12, 0),
        value=0,
        step=1,
        key="one_time_cf_month",
    )

    # --- Stress Test Scenarios ---
    st.sidebar.subheader("Stress Test Scenarios (vs Base)")

    default_labels = ["Mild Downturn", "Severe Downturn", "High Inflation"]
    default_return_deltas = [-0.02, -0.04, 0.00]  # -2%, -4%, 0%
    default_spend_deltas = [0.00, 0.05, 0.00]     # 0%, +5%, 0%
    default_infl_deltas = [0.00, 0.00, 0.02]      # 0%, 0%, +2%

    stress_scenarios: List[StressTestScenario] = []

    for i in range(3):
        st.sidebar.markdown(f"**Scenario {i+1}**")
        label = st.sidebar.text_input(
            f"Name {i+1}",
            value=default_labels[i],
            key=f"st_label_{i}",
        )

        return_delta = _percent_input(
            f"Return Change {i+1} (annual)",
            default_fraction=default_return_deltas[i],
            key=f"st_ret_{i}",
            help="Additive change vs base portfolio expected return.",
        )

        spending_delta = _percent_input(
            f"Spending Change {i+1}",
            default_fraction=default_spend_deltas[i],
            key=f"st_spend_{i}",
            help="Change in ongoing spending level vs base.",
        )

        infl_delta = _percent_input(
            f"Inflation Change {i+1}",
            default_fraction=default_infl_deltas[i],
            key=f"st_infl_{i}",
            help="Additive change to annual inflation vs base.",
        )

        if label.strip():
            stress_scenarios.append(
                StressTestScenario(
                    name=label.strip(),
                    return_delta=return_delta,
                    spending_delta=spending_delta,
                    inflation_delta=infl_delta,
                )
            )

        st.sidebar.markdown("---")

    model_inputs = ModelInputs(
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

    return model_inputs, stress_scenarios


# -----------------------------
# Stress-test engine & charts
# -----------------------------

def run_stress_tests(
    inputs: ModelInputs,
    stress_scenarios: List[StressTestScenario],
) -> pd.DataFrame:
    """Deterministic stress-test projections.

    Uses same mechanics as MC engine but without randomness. Each scenario tweaks:
    - expected return (return_delta)
    - spending level (spending_delta)
    - inflation (inflation_delta)
    """
    if not stress_scenarios:
        return pd.DataFrame()

    months = inputs.years_to_model * 12
    month_index = np.arange(1, months + 1)
    data = {"Month": month_index}

    base_exp_ann, _ = compute_portfolio_return_and_vol(inputs)

    for sc in stress_scenarios:
        # Adjusted parameters
        exp_ann = base_exp_ann + sc.return_delta
        exp_ann = max(exp_ann, -0.99)  # sanity floor

        infl_ann = max(inputs.inflation_annual + sc.inflation_delta, 0.0)

        mu_month = (1 + exp_ann) ** (1 / 12) - 1
        monthly_infl = (1 + infl_ann) ** (1 / 12) - 1

        spending = inputs.monthly_spending * (1 + sc.spending_delta)

        vals = np.zeros(months, dtype=float)
        val = inputs.starting_portfolio

        for m in range(months):
            month_no = m + 1

            if inputs.spending_rule == 1:
                cf = spending
            else:
                cf = -val * (inputs.spending_pct_annual / 12.0)

            if inputs.one_time_cf_month and month_no == inputs.one_time_cf_month:
                cf += inputs.one_time_cf

            val = max(val + cf, 0.0)
            val = max(val * (1 + mu_month), 0.0)

            vals[m] = val

            if inputs.spending_rule == 1:
                spending *= (1 + monthly_infl)

        data[sc.name] = vals

    return pd.DataFrame(data)


def stress_test_chart(stats_df: pd.DataFrame, stress_df: pd.DataFrame):
    """Overlay stress-test paths on top of the median Monte Carlo path."""
    if stress_df.empty:
        return None

    med = stats_df[["Month", "Median"]].copy()
    med.rename(columns={"Median": "Value"}, inplace=True)
    med["Scenario"] = "Median (Monte Carlo)"

    stress_long = stress_df.melt(
        id_vars="Month",
        var_name="Scenario",
        value_name="Value",
    )

    combined = pd.concat([med, stress_long], ignore_index=True)

    chart = (
        alt.Chart(combined)
        .mark_line()
        .encode(
            x=alt.X("Month:Q", title="Month"),
            y=alt.Y("Value:Q", title="Portfolio Value"),
            color=alt.Color("Scenario:N", title="Scenario"),
        )
        .properties(
            title="Stress Tests vs Median Monte Carlo Path",
            width="container",
            height=400,
        )
    )
    return chart


# -----------------------------
# Main app
# -----------------------------

def main():
    st.set_page_config(
        page_title="Portfolio Growth – Monte Carlo Scenario Analysis",
        layout="wide",
    )

    st.title("Portfolio Growth – Monte Carlo Scenario Analysis")

    inputs, stress_scenarios = sidebar_inputs()

    exp_ann, vol_ann = compute_portfolio_return_and_vol(inputs)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Starting Portfolio", f"${inputs.starting_portfolio:,.0f}")
        st.metric("Years to Model", f"{inputs.years_to_model} years")
    with col2:
        st.metric("Monthly Spending (initial)", f"${-inputs.monthly_spending:,.0f}")
        st.metric("Annual Inflation", f"{inputs.inflation_annual*100:.1f}%")
    with col3:
        st.metric("Portfolio Expected Annual Return", f"{exp_ann*100:.2f}%")
        st.metric("Portfolio Annual Volatility", f"{vol_ann*100:.2f}%")

    st.markdown("---")

    if st.button("Run Monte Carlo Simulation", type="primary"):
        with st.spinner("Running simulations..."):
            paths_df, stats_df, metrics = run_monte_carlo(inputs)

        st.subheader("Key Monte Carlo Results")

        c1, c2, c3 = st.columns(3)
        with c1:
            st.metric("Median Ending Portfolio", f"${metrics['ending_median']:,.0f}")
        with c2:
            st.metric("10th Percentile Ending Portfolio", f"${metrics['ending_p10']:,.0f}")
        with c3:
            st.metric("90th Percentile Ending Portfolio", f"${metrics['ending_p90']:,.0f}")

        c4, c5 = st.columns(2)
        with c4:
            st.metric(
                "Probability Portfolio Never Depletes",
                f"{metrics['prob_never_depleted']*100:.1f}%",
            )
        with c5:
            st.metric(
                "Probability Portfolio Positive at Horizon End",
                f"{metrics['prob_positive_at_end']*100:.1f}%",
            )

        st.markdown("---")
        st.subheader("Fan Chart of Projected Portfolio Values")

        chart = fan_chart(stats_df)
        st.altair_chart(chart, use_container_width=True)

        # --- Stress Tests section ---
        st.markdown("---")
        st.subheader("Stress Tests (Deterministic Scenarios vs Median)")

        stress_df = run_stress_tests(inputs, stress_scenarios)

        if not stress_df.empty:
            st.caption(
                "Each stress scenario adjusts returns / spending / inflation and projects "
                "a deterministic path, compared against the median Monte Carlo result."
            )

            st_chart = stress_test_chart(stats_df, stress_df)
            if st_chart is not None:
                st.altair_chart(st_chart, use_container_width=True)

            last_month = inputs.years_to_model * 12
            endings = stress_df[stress_df["Month"] == last_month].set_index("Month").T
            endings.columns = ["Ending Value"]
            endings.index.name = "Scenario"

            st.markdown("**Ending Portfolio Values by Scenario**")
            st.dataframe(
                endings.style.format({"Ending Value": "${:,.0f}"}),
                use_container_width=True,
            )
        else:
            st.info("Define at least one stress-test scenario in the sidebar to see results.")

    else:
        st.info("Adjust inputs in the sidebar and click **Run Monte Carlo Simulation** to see results.")


if __name__ == "__main__":
    main()
