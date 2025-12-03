"""
Salem-Branded Reports API
Professional advisor/client-ready portfolio analysis reports
"""
from fastapi import APIRouter, HTTPException
from models.schemas import (
    ReportData,
    ReportSummary,
    NarrativeBlock,
    MonteCarloBlock,
    StressScenarioResult,
    AssumptionsBlock,
    AppendixItem,
    KeyMetric,
    PercentilePathPoint,
    StressMetric,
    SuccessProbabilityPoint,
    TerminalWealthBucket,
    CashFlowProjection,
    IncomeSourcesTimeline,
)
from datetime import date
import logging
from typing import List

router = APIRouter()
logger = logging.getLogger(__name__)


def format_currency(value: float, decimals: int = 0) -> str:
    """Format value as currency"""
    if abs(value) >= 1_000_000:
        return f"${value/1_000_000:.{decimals}f}M"
    elif abs(value) >= 1_000:
        return f"${value/1_000:.{decimals}f}K"
    return f"${value:,.{decimals}f}"


def format_percent(value: float, decimals: int = 1) -> str:
    """Format value as percentage"""
    return f"{value * 100:.{decimals}f}%"


def generate_key_findings(
    success_prob: float,
    median_ending: float,
    starting: float,
    depletion_prob: float
) -> List[str]:
    """Generate contextual key findings"""
    findings = []
    
    # Success probability finding
    if success_prob >= 0.85:
        findings.append(
            f"Plan demonstrates strong {format_percent(success_prob)} probability of success, "
            f"indicating robust likelihood of meeting all financial objectives throughout the planning period."
        )
    elif success_prob >= 0.70:
        findings.append(
            f"Plan shows moderate {format_percent(success_prob)} probability of success. "
            f"While reasonable, consider stress testing and maintaining spending flexibility."
        )
    else:
        findings.append(
            f"Plan exhibits {format_percent(success_prob)} success probability, below recommended thresholds. "
            f"Adjustments to spending, allocation, or timeline recommended."
        )
    
    # Portfolio trajectory finding
    growth = (median_ending - starting) / starting
    if growth > 0.50:
        findings.append(
            f"Median scenario projects substantial portfolio growth to {format_currency(median_ending)}, "
            f"representing {format_percent(growth)} increase from starting value."
        )
    elif growth > 0:
        findings.append(
            f"Median scenario projects modest portfolio growth to {format_currency(median_ending)}."
        )
    else:
        findings.append(
            f"Median scenario projects controlled spend-down to {format_currency(median_ending)}, "
            f"aligned with decumulation objectives."
        )
    
    # Depletion risk finding
    if depletion_prob > 0.15:
        findings.append(
            f"Elevated depletion risk of {format_percent(depletion_prob)} warrants contingency planning "
            f"and potential adjustments to mitigate downside scenarios."
        )
    
    return findings


def generate_key_risks(
    success_prob: float,
    depletion_prob: float,
    equity_pct: float
) -> List[str]:
    """Generate key risk assessments"""
    risks = []
    
    if success_prob < 0.70:
        risks.append(
            "Current plan success probability falls below recommended thresholds, "
            "indicating material risk of not achieving stated financial objectives."
        )
    
    if depletion_prob > 0.20:
        risks.append(
            f"Portfolio depletion probability of {format_percent(depletion_prob)} represents "
            f"significant longevity risk requiring mitigation strategies."
        )
    
    if equity_pct > 0.80:
        risks.append(
            f"Aggressive {format_percent(equity_pct)} equity allocation increases exposure "
            f"to market volatility and sequence-of-returns risk, particularly critical during early retirement years."
        )
    elif equity_pct < 0.30:
        risks.append(
            f"Conservative {format_percent(equity_pct)} equity allocation may limit growth potential, "
            f"increasing exposure to inflation and longevity risk over extended time horizons."
        )
    
    risks.append(
        "Market conditions, inflation rates, and healthcare costs may differ materially from assumptions, "
        "affecting actual outcomes. Regular plan reviews recommended."
    )
    
    return risks


def generate_recommendations(
    success_prob: float,
    median_ending: float,
    starting: float
) -> List[str]:
    """Generate actionable recommendations"""
    recommendations = []
    
    if success_prob < 0.70:
        recommendations.extend([
            "Consider reducing discretionary spending by 10-15% to improve plan sustainability and increase success probability.",
            "Explore opportunities to defer retirement or incorporate part-time income to strengthen financial position.",
            "Review asset allocation with advisor to ensure appropriate risk/return profile for circumstances and objectives.",
            "Develop flexible spending contingencies to adapt to adverse market conditions if they occur."
        ])
    elif success_prob < 0.85:
        recommendations.extend([
            "Maintain current strategy with annual monitoring and periodic stress testing against various scenarios.",
            "Consider establishing spending flexibility thresholds to dynamically adjust to market performance.",
            "Review and update plan annually or following significant life events, market changes, or goal modifications.",
            "Evaluate tax optimization strategies including Roth conversions, strategic withdrawals, and loss harvesting."
        ])
    else:
        surplus = median_ending - starting
        if surplus > starting * 0.50:
            recommendations.append(
                "Plan demonstrates significant margin of success. Consider enhancing lifestyle spending, "
                "legacy goals, or charitable giving aligned with values and tax objectives."
            )
        recommendations.extend([
            "Explore tax-efficient wealth transfer strategies including lifetime gifting within annual exclusions.",
            "Review estate planning documents to ensure alignment with current intentions and tax law changes.",
            "Consider charitable giving opportunities through donor-advised funds or direct contributions.",
            "Maintain disciplined rebalancing and tax-loss harvesting within investment policy guidelines."
        ])
    
    return recommendations


@router.get("/reports/{plan_id}", response_model=ReportData)
async def get_report(plan_id: str):
    """
    Retrieve comprehensive Salem-branded portfolio analysis report.
    
    This endpoint generates a complete, advisor/client-ready report with:
    - Executive summary with key metrics
    - Narrative insights (findings, risks, recommendations)
    - Monte Carlo simulation results with percentile paths
    - Stress test scenario analysis
    - Planning assumptions and disclosures
    
    **Parameters:**
    - plan_id: Unique plan identifier (simulation run ID)
    
    **Returns:**
    - Complete ReportData structure ready for rendering
    """
    try:
        logger.info(f"Generating report for plan_id: {plan_id}")
        
        # TODO: In production, fetch from database/storage using plan_id
        # For now, generate sample report data demonstrating structure
        
        # Sample data representing a typical simulation result
        starting_portfolio = 4_500_000
        median_ending = 5_200_000
        p10_ending = 2_100_000
        p90_ending = 9_800_000
        success_prob = 0.82
        depletion_prob = 0.12
        equity_pct = 0.70
        years = 30
        num_runs = 1000
        
        # Generate key metrics for summary cards
        key_metrics = [
            KeyMetric(
                label="Success Probability",
                value=format_percent(success_prob),
                tooltip="Probability of meeting all spending needs throughout planning horizon",
                variant="success" if success_prob >= 0.85 else "warning" if success_prob >= 0.70 else "error"
            ),
            KeyMetric(
                label="Median Ending Portfolio",
                value=format_currency(median_ending),
                tooltip="50th percentile outcome - most likely portfolio value at end of planning period",
                variant="success"
            ),
            KeyMetric(
                label="10th Percentile (Downside)",
                value=format_currency(p10_ending),
                tooltip="Portfolio value in adverse scenarios - 90% of outcomes exceed this level",
                variant="neutral"
            ),
            KeyMetric(
                label="Depletion Risk",
                value=format_percent(depletion_prob),
                tooltip="Probability of portfolio depleting before end of planning horizon",
                variant="error" if depletion_prob > 0.15 else "warning"
            ),
        ]
        
        # Build report summary
        summary = ReportSummary(
            client_name="John & Mary Smith",  # TODO: Fetch from plan data
            scenario_name="Base Case Monte Carlo Analysis",
            as_of_date=date.today().isoformat(),
            advisor_name="Michael Chen, CFP®",  # TODO: Fetch from plan data
            firm_name="Salem Investment Counselors",
            key_metrics=key_metrics
        )
        
        # Generate narrative content
        narrative = NarrativeBlock(
            key_findings=generate_key_findings(success_prob, median_ending, starting_portfolio, depletion_prob),
            key_risks=generate_key_risks(success_prob, depletion_prob, equity_pct),
            recommendations=generate_recommendations(success_prob, median_ending, starting_portfolio)
        )
        
        # Build percentile path (yearly data points with 5 percentiles)
        percentile_path = []
        for year in range(years + 1):
            # Generate representative percentile values
            # In production, these would come from actual simulation results
            growth_factor_p50 = 1.06 ** year
            growth_factor_p5 = 0.92 ** year
            growth_factor_p10 = 0.98 ** year
            growth_factor_p25 = 1.02 ** year
            growth_factor_p75 = 1.10 ** year
            growth_factor_p90 = 1.12 ** year
            growth_factor_p95 = 1.14 ** year
            
            percentile_path.append(
                PercentilePathPoint(
                    year=year,
                    p5=starting_portfolio * growth_factor_p5,
                    p10=starting_portfolio * growth_factor_p10,
                    p25=starting_portfolio * growth_factor_p25,
                    p50=starting_portfolio * growth_factor_p50,
                    p75=starting_portfolio * growth_factor_p75,
                    p90=starting_portfolio * growth_factor_p90,
                    p95=starting_portfolio * growth_factor_p95
                )
            )
        
        # Generate success probability over time
        success_prob_over_time = []
        for year in range(1, years + 1):
            # Success probability tends to decrease over time as scenarios diverge
            year_success = success_prob * (0.98 ** (year / 10))  # Slight decay
            success_prob_over_time.append(
                SuccessProbabilityPoint(
                    year=year,
                    success_probability=min(1.0, year_success)
                )
            )
        
        # Generate terminal wealth distribution (histogram)
        terminal_wealth_dist = []
        bucket_ranges = [
            (0, 500_000, "$0-$500K"),
            (500_000, 1_000_000, "$500K-$1M"),
            (1_000_000, 2_000_000, "$1M-$2M"),
            (2_000_000, 3_000_000, "$2M-$3M"),
            (3_000_000, 5_000_000, "$3M-$5M"),
            (5_000_000, 7_500_000, "$5M-$7.5M"),
            (7_500_000, 10_000_000, "$7.5M-$10M"),
            (10_000_000, float('inf'), "$10M+"),
        ]
        
        # Simulate distribution (in production, use actual simulation results)
        import random
        random.seed(42)  # For reproducibility
        terminal_values = [
            median_ending * random.lognormvariate(0, 0.5) for _ in range(num_runs)
        ]
        
        for min_val, max_val, label in bucket_ranges:
            count = sum(1 for v in terminal_values if min_val <= v < max_val)
            if count > 0:
                terminal_wealth_dist.append(
                    TerminalWealthBucket(
                        bucket_label=label,
                        count=count,
                        min_value=min_val,
                        max_value=max_val if max_val != float('inf') else max(terminal_values),
                        percentage=count / num_runs
                    )
                )
        
        # Build Monte Carlo block
        monte_carlo = MonteCarloBlock(
            percentile_path=percentile_path,
            success_probability=success_prob,
            num_runs=num_runs,
            horizon_years=years,
            first_failure_year=None if success_prob > 0.50 else 22,
            success_probability_over_time=success_prob_over_time,
            terminal_wealth_distribution=terminal_wealth_dist
        )
        
        # Generate cash flow projections
        current_age = 48  # TODO: Get from plan data
        annual_spending = 240_000
        ss_income = 48_000
        ss_start_age = 67
        
        cash_flow_projections = []
        balance = starting_portfolio
        
        for year in range(1, years + 1):
            age = current_age + year
            
            # Income sources
            ss_this_year = ss_income if age >= ss_start_age else 0
            pension_this_year = 0  # TODO: Add pension logic
            total_income = ss_this_year + pension_this_year
            
            # Withdrawals (negative)
            withdrawals = -annual_spending * (1.03 ** year)  # Inflation adjusted
            
            # Taxes (simplified)
            taxable_income = max(0, -withdrawals + total_income)
            taxes = -taxable_income * 0.25
            
            # Investment return (simplified - use median growth)
            inv_return = balance * 0.06
            
            # Ending balance
            ending = balance + withdrawals + total_income + taxes + inv_return
            
            cash_flow_projections.append(
                CashFlowProjection(
                    year=year,
                    age=age,
                    beginning_balance=balance,
                    withdrawals=withdrawals,
                    income_sources_total=total_income,
                    taxes=taxes,
                    investment_return=inv_return,
                    ending_balance=ending
                )
            )
            
            balance = ending
        
        # Generate income timeline
        income_timeline = []
        for year in range(1, years + 1):
            age = current_age + year
            ss_this_year = ss_income if age >= ss_start_age else 0
            withdrawals_this_year = annual_spending * (1.03 ** year)
            
            income_timeline.append(
                IncomeSourcesTimeline(
                    year=year,
                    social_security=ss_this_year,
                    pension=0,  # TODO: Add pension
                    annuity=0,  # TODO: Add annuity
                    portfolio_withdrawals=withdrawals_this_year,
                    other_income=0
                )
            )
        
        # Generate stress test scenarios
        stress_tests = [
            StressScenarioResult(
                id="early_bear",
                name="Early Bear Market",
                description="Severe market downturn (-30% equity, -10% bonds) in first 3 years of plan",
                base_success_probability=success_prob,
                stressed_success_probability=max(0, success_prob - 0.15),
                base_key_metrics=[
                    KeyMetric(label="Success Rate", value=format_percent(success_prob), variant="success"),
                    KeyMetric(label="Median Ending", value=format_currency(median_ending), variant="neutral"),
                ],
                stressed_key_metrics=[
                    KeyMetric(label="Success Rate", value=format_percent(max(0, success_prob - 0.15)), variant="warning"),
                    KeyMetric(label="Median Ending", value=format_currency(median_ending * 0.75), variant="warning"),
                ],
                impact_severity="high"
            ),
            StressScenarioResult(
                id="high_inflation",
                name="Elevated Inflation",
                description="Persistent 5% annual inflation versus 3% base assumption throughout planning period",
                base_success_probability=success_prob,
                stressed_success_probability=max(0, success_prob - 0.10),
                base_key_metrics=[
                    KeyMetric(label="Success Rate", value=format_percent(success_prob), variant="success"),
                    KeyMetric(label="Median Ending", value=format_currency(median_ending), variant="neutral"),
                ],
                stressed_key_metrics=[
                    KeyMetric(label="Success Rate", value=format_percent(max(0, success_prob - 0.10)), variant="warning"),
                    KeyMetric(label="Median Ending", value=format_currency(median_ending * 0.82), variant="neutral"),
                ],
                impact_severity="medium"
            ),
            StressScenarioResult(
                id="lower_returns",
                name="Lower Market Returns",
                description="Market returns 2 percentage points below long-term historical averages across all asset classes",
                base_success_probability=success_prob,
                stressed_success_probability=max(0, success_prob - 0.18),
                base_key_metrics=[
                    KeyMetric(label="Success Rate", value=format_percent(success_prob), variant="success"),
                    KeyMetric(label="Median Ending", value=format_currency(median_ending), variant="neutral"),
                ],
                stressed_key_metrics=[
                    KeyMetric(label="Success Rate", value=format_percent(max(0, success_prob - 0.18)), variant="error"),
                    KeyMetric(label="Median Ending", value=format_currency(median_ending * 0.68), variant="warning"),
                ],
                impact_severity="high"
            ),
        ]
        
        # Build assumptions block
        assumptions = AssumptionsBlock(
            planning_horizon_years=years,
            real_return_mean=0.065,  # 6.5% nominal minus 3% inflation
            real_return_std=0.12,
            inflation_rate=0.03,
            spending_rule_description="Fixed dollar spending adjusted annually for inflation (3% rate)",
            other_assumptions={
                "equity_allocation": format_percent(equity_pct),
                "fixed_income_allocation": format_percent(0.25),
                "cash_allocation": format_percent(0.05),
                "starting_portfolio": format_currency(starting_portfolio),
                "annual_spending": format_currency(240_000),  # Example: $20K/month
                "social_security": "$48,000/year starting age 67",
                "healthcare_costs": "$15,000/year starting age 65, inflating at 5%",
                "tax_rate": "25% marginal rate",
                "estate_goal": format_currency(2_000_000)
            }
        )
        
        # Build appendix sections
        appendix = [
            AppendixItem(
                title="Methodology",
                content=[
                    "Monte Carlo simulation utilizing geometric Brownian motion to model portfolio returns and volatility.",
                    "Asset class returns modeled with log-normal distribution incorporating historical mean returns and standard deviations.",
                    f"{num_runs:,} independent simulation paths generated to capture range of potential outcomes.",
                    "Spending rules, income sources, taxes, and healthcare costs incorporated into each scenario.",
                    "Success defined as maintaining positive portfolio balance throughout entire planning horizon."
                ]
            ),
            AppendixItem(
                title="Important Limitations",
                content=[
                    "Simulations based on historical return and volatility assumptions which may not reflect future market conditions.",
                    "Extreme market events ('black swans') may not be adequately captured in historical data.",
                    "Actual tax treatment depends on individual circumstances and may differ from assumptions.",
                    "Inflation assumptions may not reflect actual cost increases, particularly for healthcare.",
                    "Does not constitute investment advice or guarantee of future results. Consult with qualified professionals."
                ]
            ),
            AppendixItem(
                title="Regular Review Recommended",
                content=[
                    "Financial plans should be reviewed annually or following significant life events.",
                    "Market conditions, tax laws, and personal circumstances change over time.",
                    "Adjust assumptions and strategies as needed to maintain plan relevance and accuracy.",
                    "Contact your Salem Investment Counselors advisor to discuss updates or questions."
                ]
            ),
        ]
        
        # Assemble complete report
        report = ReportData(
            report_id=plan_id,
            summary=summary,
            narrative=narrative,
            monte_carlo=monte_carlo,
            stress_tests=stress_tests,
            assumptions=assumptions,
            appendix=appendix,
            cash_flow_projection=cash_flow_projections,
            income_timeline=income_timeline
        )
        
        logger.info(f"Report generated successfully for plan_id: {plan_id}")
        return report
        
    except Exception as e:
        logger.error(f"Failed to generate report for plan_id {plan_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Report generation failed: {str(e)}")
