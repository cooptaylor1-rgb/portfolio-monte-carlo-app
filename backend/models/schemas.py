"""
Pydantic models for API request/response validation.
These models define the data contracts between frontend and backend.
"""
from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Dict
from datetime import date
from enum import Enum


class SpendingRule(int, Enum):
    """Spending withdrawal strategy"""
    FIXED_DOLLAR = 1
    PERCENT_OF_PORTFOLIO = 2


class ClientInfoModel(BaseModel):
    """Client demographic and identification information"""
    client_name: str = Field(default="", description="Client full name")
    report_date: date = Field(default_factory=date.today, description="Report generation date")
    advisor_name: str = Field(default="", description="Assigned advisor name")
    client_id: str = Field(default="", description="Unique client identifier")
    client_notes: str = Field(default="", description="Additional notes")


class ModelInputsModel(BaseModel):
    """Core Monte Carlo simulation parameters"""
    # Portfolio configuration
    starting_portfolio: float = Field(default=4_500_000.0, gt=0, description="Initial portfolio value")
    years_to_model: int = Field(default=30, ge=1, le=50, description="Planning horizon in years")
    current_age: int = Field(default=48, ge=18, le=100, description="Current age")
    horizon_age: int = Field(default=78, ge=19, le=120, description="End age for planning")
    
    # Spending parameters
    monthly_income: float = Field(default=0.0, description="Monthly income (positive)")
    monthly_spending: float = Field(default=-20_000.0, description="Monthly withdrawal (negative)")
    inflation_annual: float = Field(default=0.03, ge=-0.05, le=0.15, description="Annual inflation rate")
    spending_rule: SpendingRule = Field(default=SpendingRule.FIXED_DOLLAR, description="Withdrawal strategy")
    spending_pct_annual: float = Field(default=0.04, ge=0, le=0.20, description="Annual spending as % of portfolio")
    
    # Asset allocation
    equity_pct: float = Field(default=0.70, ge=0, le=1, description="Equity allocation")
    fi_pct: float = Field(default=0.25, ge=0, le=1, description="Fixed income allocation")
    cash_pct: float = Field(default=0.05, ge=0, le=1, description="Cash allocation")
    
    # Return assumptions
    equity_return_annual: float = Field(default=0.10, ge=-0.20, le=0.30, description="Expected equity return")
    fi_return_annual: float = Field(default=0.03, ge=-0.10, le=0.15, description="Expected FI return")
    cash_return_annual: float = Field(default=0.02, ge=-0.05, le=0.10, description="Expected cash return")
    
    # Volatility assumptions
    equity_vol_annual: float = Field(default=0.15, ge=0, le=0.50, description="Equity volatility")
    fi_vol_annual: float = Field(default=0.05, ge=0, le=0.30, description="FI volatility")
    cash_vol_annual: float = Field(default=0.01, ge=0, le=0.10, description="Cash volatility")
    
    # Monte Carlo settings
    n_scenarios: int = Field(default=200, ge=50, le=10000, description="Number of simulation scenarios")
    
    # One-time cash flows
    one_time_cf: float = Field(default=0.0, description="One-time cash flow amount")
    one_time_cf_month: int = Field(default=0, ge=0, description="Month for one-time cash flow (0=ignore)")
    
    # Tax-advantaged accounts
    taxable_pct: float = Field(default=0.33, ge=0, le=1, description="% in taxable accounts")
    ira_pct: float = Field(default=0.50, ge=0, le=1, description="% in traditional IRA/401k")
    roth_pct: float = Field(default=0.17, ge=0, le=1, description="% in Roth IRA")
    taxable_basis_pct: float = Field(default=0.60, ge=0, le=1, description="Cost basis % of taxable accounts")
    tax_rate: float = Field(default=0.25, ge=0, le=0.50, description="Marginal tax rate")
    filing_status: str = Field(default="single", description="Tax filing status: single or joint")
    state_tax_rate: float = Field(default=0.0, ge=0, le=0.15, description="State income tax rate")
    rmd_age: int = Field(default=73, ge=70, le=75, description="RMD starting age")
    
    # Tax optimization
    use_tax_optimization: bool = Field(default=True, description="Enable optimal withdrawal sequencing")
    optimize_roth_conversions: bool = Field(default=False, description="Calculate optimal Roth conversions")
    roth_conversion_start_age: int = Field(default=60, ge=50, le=72, description="Start age for conversions")
    roth_conversion_end_age: int = Field(default=72, ge=60, le=73, description="End age for conversions")
    avoid_irmaa: bool = Field(default=True, description="Avoid Medicare IRMAA thresholds in conversions")
    
    # Income sources
    social_security_monthly: float = Field(default=0.0, ge=0, description="Monthly Social Security benefit")
    ss_start_age: int = Field(default=67, ge=62, le=70, description="SS claiming age")
    pension_monthly: float = Field(default=0.0, ge=0, description="Monthly pension payment")
    pension_start_age: int = Field(default=65, ge=55, le=75, description="Pension start age")
    
    # Healthcare costs
    monthly_healthcare: float = Field(default=0.0, ge=0, description="Monthly healthcare expenses")
    healthcare_start_age: int = Field(default=65, ge=40, le=100, description="Healthcare expense start age")
    healthcare_inflation: float = Field(default=0.05, ge=0, le=0.15, description="Healthcare inflation rate")
    
    # Advanced features
    roth_conversion_annual: float = Field(default=0.0, ge=0, description="Annual Roth conversion amount")
    estate_tax_exemption: float = Field(default=13_610_000.0, ge=0, description="Estate tax exemption")
    legacy_goal: float = Field(default=0.0, ge=0, description="Target legacy/estate goal")
    
    # Longevity planning
    use_actuarial_tables: bool = Field(default=False, description="Use actuarial life expectancy")
    health_adjustment: int = Field(default=0, ge=-10, le=10, description="Health adjustment years")
    
    # Dynamic allocation
    use_glide_path: bool = Field(default=False, description="Enable dynamic asset allocation")
    target_equity_at_end: float = Field(default=0.40, ge=0, le=1, description="Target equity % at horizon")
    
    # Lifestyle spending phases
    use_lifestyle_phases: bool = Field(default=False, description="Enable go-go, slow-go, no-go phases")
    slow_go_age: int = Field(default=75, ge=60, le=90, description="Slow-go phase start")
    no_go_age: int = Field(default=85, ge=70, le=100, description="No-go phase start")
    slow_go_spending_pct: float = Field(default=0.80, ge=0.5, le=1, description="Spending % in slow-go")
    no_go_spending_pct: float = Field(default=0.60, ge=0.3, le=1, description="Spending % in no-go")
    
    # Guardrails
    use_guardrails: bool = Field(default=False, description="Enable dynamic spending guardrails")
    upper_guardrail: float = Field(default=0.20, ge=0, le=0.50, description="Upper guardrail threshold")
    lower_guardrail: float = Field(default=0.15, ge=0, le=0.50, description="Lower guardrail threshold")
    
    @field_validator('equity_pct', 'fi_pct', 'cash_pct')
    @classmethod
    def validate_allocation(cls, v, info):
        """Ensure allocations sum to ~1.0"""
        return v
    
    @field_validator('horizon_age')
    @classmethod
    def validate_horizon(cls, v, info):
        """Ensure horizon_age > current_age"""
        if 'current_age' in info.data and v <= info.data['current_age']:
            raise ValueError('horizon_age must be greater than current_age')
        return v


class FinancialGoalModel(BaseModel):
    """Specific financial goal to track"""
    name: str = Field(description="Goal name")
    target_amount: float = Field(gt=0, description="Target dollar amount")
    target_age: int = Field(ge=0, le=120, description="Age when goal is needed")
    priority: str = Field(default="medium", description="Priority level")


class StressTestScenarioModel(BaseModel):
    """Stress test scenario definition"""
    name: str = Field(description="Scenario name")
    description: str = Field(default="", description="Scenario description")
    equity_return_adj: float = Field(default=0.0, description="Equity return adjustment")
    fi_return_adj: float = Field(default=0.0, description="FI return adjustment")
    inflation_adj: float = Field(default=0.0, description="Inflation adjustment")
    spending_adj: float = Field(default=0.0, description="Spending adjustment")
    volatility_multiplier: float = Field(default=1.0, gt=0, description="Volatility multiplier")


class SimulationRequest(BaseModel):
    """Request to run Monte Carlo simulation"""
    client_info: ClientInfoModel
    inputs: ModelInputsModel
    financial_goals: Optional[List[FinancialGoalModel]] = Field(default_factory=list)
    stress_scenarios: Optional[List[StressTestScenarioModel]] = Field(default_factory=list)
    seed: Optional[int] = Field(default=None, description="Random seed for reproducibility")


class RothConversionYearModel(BaseModel):
    """Single year of Roth conversion plan"""
    year: int = Field(description="Year index (0 = start)")
    age: int = Field(description="Client age this year")
    conversion_amount: float = Field(description="Amount to convert from IRA to Roth")
    tax_on_conversion: float = Field(description="Tax owed on conversion")
    cumulative_savings: float = Field(description="Cumulative PV tax savings")


class RothConversionPlanModel(BaseModel):
    """Complete Roth conversion optimization plan"""
    enabled: bool = Field(default=False, description="Whether optimization was run")
    years: List[RothConversionYearModel] = Field(default_factory=list, description="Year-by-year schedule")
    total_conversions: float = Field(default=0.0, description="Total amount converted")
    total_taxes_paid: float = Field(default=0.0, description="Total taxes on conversions")
    lifetime_tax_savings: float = Field(default=0.0, description="PV of lifetime tax savings")
    recommendation: str = Field(default="", description="Summary recommendation")


class TaxOptimizationMetrics(BaseModel):
    """Tax optimization results and metrics"""
    enabled: bool = Field(default=False, description="Whether tax optimization was used")
    total_lifetime_taxes: float = Field(default=0.0, description="Total taxes paid over lifetime")
    pv_lifetime_taxes: float = Field(default=0.0, description="Present value of lifetime taxes")
    average_annual_tax: float = Field(default=0.0, description="Average annual tax payment")
    average_effective_rate: float = Field(default=0.0, description="Average effective tax rate")
    total_irmaa_surcharges: float = Field(default=0.0, description="Total Medicare IRMAA surcharges")
    roth_conversion_plan: Optional[RothConversionPlanModel] = Field(default=None, description="Optimal Roth conversion schedule")
    tax_savings_vs_naive: float = Field(default=0.0, description="Tax savings vs proportional withdrawals")
    withdrawal_strategy: str = Field(default="", description="Description of withdrawal strategy used")


class SimulationMetrics(BaseModel):
    """Key metrics from simulation results"""
    success_probability: float = Field(description="Probability of success")
    ending_median: float = Field(description="Median ending portfolio value")
    ending_p10: float = Field(description="10th percentile ending value")
    ending_p90: float = Field(description="90th percentile ending value")
    years_depleted: float = Field(description="Average years until depletion")
    depletion_probability: float = Field(description="Probability of depletion")
    shortfall_risk: float = Field(description="Shortfall risk percentage")
    
    # NEW METRICS from refactored engine
    annual_ruin_probability: Optional[List[float]] = Field(
        default=None, 
        description="Annual first-passage ruin probability by year"
    )
    cumulative_ruin_probability: Optional[List[float]] = Field(
        default=None,
        description="Cumulative ruin probability by year"
    )
    longevity_metrics: Optional[Dict[int, Dict[str, float]]] = Field(
        default=None,
        description="Metrics at longevity milestone ages (70, 75, 80, 85, 90, 95, 100)"
    )
    
    # Tax optimization metrics
    tax_optimization: Optional[TaxOptimizationMetrics] = Field(
        default=None,
        description="Tax optimization results and analysis"
    )


class SimulationResponse(BaseModel):
    """Response from Monte Carlo simulation"""
    metrics: SimulationMetrics
    stats: List[dict] = Field(description="Monthly statistics (percentiles)")
    goal_probabilities: Optional[List[dict]] = Field(default=None, description="Goal achievement probabilities")
    inputs: Optional[ModelInputsModel] = Field(default=None, description="Echo of input parameters for reference")
    success: bool = True
    message: str = "Simulation completed successfully"


class AssumptionPresetModel(BaseModel):
    """Predefined assumption preset"""
    name: str
    equity_return: float
    fi_return: float
    cash_return: float
    equity_vol: float
    fi_vol: float
    cash_vol: float


class HealthCheckResponse(BaseModel):
    """API health check response"""
    status: str
    version: str
    timestamp: str


class SensitivityRequest(BaseModel):
    """Request for sensitivity analysis"""
    inputs: ModelInputsModel = Field(description="Base simulation inputs")
    parameter: str = Field(description="Parameter name to vary")
    variations: List[float] = Field(description="List of parameter values to test")


class SensitivityResult(BaseModel):
    """Single sensitivity analysis result"""
    parameter_value: float = Field(description="Value of the varied parameter")
    success_probability: float = Field(description="Success probability at this parameter value")
    ending_median: float = Field(description="Median ending portfolio value")
    depletion_probability: float = Field(description="Depletion probability")


class SensitivityResponse(BaseModel):
    """Response from sensitivity analysis"""
    success: bool = True
    parameter: str = Field(description="Parameter that was varied")
    results: List[SensitivityResult] = Field(description="Results for each parameter variation")


# ============================================================================
# Salem-Branded Report Models
# ============================================================================

class KeyMetric(BaseModel):
    """Single key metric for display"""
    label: str = Field(description="Metric label for display")
    value: str = Field(description="Formatted value (e.g., '$4.5M', '85%')")
    tooltip: Optional[str] = Field(default=None, description="Optional explanatory tooltip")
    variant: Optional[str] = Field(default="neutral", description="Visual variant: success|warning|error|neutral")


class ReportSummary(BaseModel):
    """High-level report summary and metadata"""
    client_name: str = Field(description="Client full name")
    scenario_name: str = Field(default="Base Case Analysis", description="Scenario identifier")
    as_of_date: str = Field(description="Report generation date (YYYY-MM-DD)")
    advisor_name: str = Field(description="Advising professional name")
    firm_name: str = Field(default="Salem Investment Counselors", description="Advisory firm name")
    key_metrics: List[KeyMetric] = Field(description="Key metrics cards for summary")


class NarrativeBlock(BaseModel):
    """Narrative content block with findings, risks, recommendations"""
    key_findings: List[str] = Field(default_factory=list, description="Key findings (bullet points)")
    key_risks: List[str] = Field(default_factory=list, description="Key risks (bullet points)")
    recommendations: List[str] = Field(default_factory=list, description="Recommendations (bullet points)")


class PercentilePathPoint(BaseModel):
    """Single point in percentile path"""
    year: int = Field(description="Year number (0 = start)")
    p5: Optional[float] = Field(default=None, description="5th percentile portfolio value")
    p10: float = Field(description="10th percentile portfolio value")
    p25: Optional[float] = Field(default=None, description="25th percentile portfolio value")
    p50: float = Field(description="50th percentile (median) portfolio value")
    p75: Optional[float] = Field(default=None, description="75th percentile portfolio value")
    p90: float = Field(description="90th percentile portfolio value")
    p95: Optional[float] = Field(default=None, description="95th percentile portfolio value")


class SuccessProbabilityPoint(BaseModel):
    """Success probability at a given year"""
    year: int = Field(description="Year number")
    success_probability: float = Field(ge=0, le=1, description="Success probability at this year")


class TerminalWealthBucket(BaseModel):
    """Histogram bucket for terminal wealth distribution"""
    bucket_label: str = Field(description="Bucket label (e.g., '$0-$250K')")
    count: int = Field(ge=0, description="Number of scenarios in this bucket")
    min_value: float = Field(description="Minimum value in bucket")
    max_value: float = Field(description="Maximum value in bucket")
    percentage: float = Field(ge=0, le=1, description="Percentage of total scenarios")


class CashFlowProjection(BaseModel):
    """Annual cash flow projection"""
    year: int = Field(description="Year number")
    age: Optional[int] = Field(default=None, description="Client age")
    beginning_balance: float = Field(description="Portfolio value at start of year")
    withdrawals: float = Field(description="Total withdrawals (negative)")
    income_sources_total: float = Field(description="Total income (SS, pension, etc.)")
    taxes: float = Field(description="Taxes paid (negative)")
    investment_return: float = Field(description="Investment return for year")
    ending_balance: float = Field(description="Portfolio value at end of year")


class IncomeSourcesTimeline(BaseModel):
    """Income sources breakdown by year"""
    year: int = Field(description="Year number")
    social_security: float = Field(default=0, description="Social Security income")
    pension: float = Field(default=0, description="Pension income")
    annuity: float = Field(default=0, description="Annuity income")
    portfolio_withdrawals: float = Field(description="Portfolio withdrawals")
    other_income: float = Field(default=0, description="Other income sources")


class MonteCarloBlock(BaseModel):
    """Monte Carlo simulation results"""
    percentile_path: List[PercentilePathPoint] = Field(description="Yearly percentile paths")
    success_probability: float = Field(ge=0, le=1, description="Success probability (0-1)")
    num_runs: int = Field(description="Number of Monte Carlo scenarios")
    horizon_years: int = Field(description="Planning horizon in years")
    first_failure_year: Optional[int] = Field(default=None, description="Year of first failure (if any)")
    success_probability_over_time: Optional[List[SuccessProbabilityPoint]] = Field(
        default=None, 
        description="Success probability evolution over time"
    )
    terminal_wealth_distribution: Optional[List[TerminalWealthBucket]] = Field(
        default=None,
        description="Histogram of terminal wealth outcomes"
    )


class StressMetric(BaseModel):
    """Key metric under stress scenario"""
    label: str = Field(description="Metric label")
    base_value: str = Field(description="Formatted base case value")
    stressed_value: str = Field(description="Formatted stressed value")
    change: str = Field(description="Formatted change (e.g., '-15%', '$-500K')")


class StressScenarioResult(BaseModel):
    """Stress test scenario result"""
    id: str = Field(description="Scenario identifier")
    name: str = Field(description="Scenario display name")
    description: str = Field(description="Scenario description")
    base_success_probability: float = Field(ge=0, le=1, description="Base case success probability")
    stressed_success_probability: float = Field(ge=0, le=1, description="Stressed success probability")
    base_key_metrics: List[KeyMetric] = Field(description="Base case metrics")
    stressed_key_metrics: List[KeyMetric] = Field(description="Stressed metrics")
    impact_severity: str = Field(default="medium", description="Impact severity: low|medium|high")


class AssumptionsBlock(BaseModel):
    """Planning assumptions"""
    planning_horizon_years: int = Field(description="Total planning years")
    real_return_mean: float = Field(description="Mean real return assumption")
    real_return_std: float = Field(description="Standard deviation of real returns")
    inflation_rate: float = Field(description="Annual inflation assumption")
    spending_rule_description: str = Field(description="Description of spending strategy")
    other_assumptions: Optional[dict] = Field(default_factory=dict, description="Additional assumptions")


class AppendixItem(BaseModel):
    """Appendix content item"""
    title: str = Field(description="Section title")
    content: List[str] = Field(description="Content items (paragraphs or bullets)")


class ReportData(BaseModel):
    """Complete Salem-branded report data structure"""
    report_id: str = Field(description="Unique report identifier")
    summary: ReportSummary = Field(description="Report summary and metadata")
    narrative: NarrativeBlock = Field(description="Key findings, risks, recommendations")
    monte_carlo: MonteCarloBlock = Field(description="Monte Carlo simulation results")
    stress_tests: List[StressScenarioResult] = Field(default_factory=list, description="Stress test scenarios")
    assumptions: AssumptionsBlock = Field(description="Planning assumptions")
    appendix: List[AppendixItem] = Field(default_factory=list, description="Appendix sections")
    cash_flow_projection: Optional[List[CashFlowProjection]] = Field(
        default=None,
        description="Year-by-year cash flow projections"
    )
    income_timeline: Optional[List[IncomeSourcesTimeline]] = Field(
        default=None,
        description="Income sources breakdown over time"
    )


# ============================================================================
# GOAL-BASED PLANNING MODELS
# ============================================================================

class GoalPriorityEnum(str, Enum):
    """Goal priority levels"""
    CRITICAL = "critical"  # Must-have (retirement, healthcare)
    HIGH = "high"          # Very important (education, home)
    MEDIUM = "medium"      # Nice-to-have (vacation home)
    LOW = "low"            # Aspirational (legacy)


class GoalStatusEnum(str, Enum):
    """Goal achievement status"""
    ON_TRACK = "on_track"          # >85% probability
    AT_RISK = "at_risk"            # 70-85% probability
    UNDERFUNDED = "underfunded"    # 50-70% probability
    CRITICAL = "critical"          # <50% probability
    ACHIEVED = "achieved"          # Already funded
    ABANDONED = "abandoned"        # Deprioritized


class GoalInputModel(BaseModel):
    """Input model for financial goal"""
    name: str = Field(description="Goal name/description")
    target_amount: float = Field(gt=0, description="Target amount in today's dollars")
    target_year: int = Field(ge=2024, le=2100, description="Year when goal is needed")
    priority: GoalPriorityEnum = Field(default=GoalPriorityEnum.MEDIUM, description="Goal priority")
    
    # Funding
    current_funding: float = Field(default=0.0, ge=0, description="Current amount allocated")
    annual_contribution: float = Field(default=0.0, ge=0, description="Annual contribution")
    contribution_start_year: int = Field(default=2024, description="First year of contributions")
    contribution_end_year: Optional[int] = Field(default=None, description="Last year of contributions")
    
    # Asset allocation
    equity_pct: float = Field(default=0.60, ge=0, le=1, description="Equity allocation for this goal")
    fi_pct: float = Field(default=0.35, ge=0, le=1, description="Fixed income allocation")
    cash_pct: float = Field(default=0.05, ge=0, le=1, description="Cash allocation")
    
    # Glide path
    use_glide_path: bool = Field(default=True, description="Reduce equity as goal approaches")
    years_before_goal_to_derisk: int = Field(default=5, ge=0, le=20, description="Years to start derisking")
    target_equity_at_goal: float = Field(default=0.20, ge=0, le=1, description="Target equity at goal date")
    
    # Success criteria
    success_threshold: float = Field(default=0.85, ge=0.5, le=0.99, description="Required probability")
    acceptable_shortfall_pct: float = Field(default=0.10, ge=0, le=0.50, description="Acceptable shortfall %")
    
    # Optional
    id: Optional[str] = Field(default=None, description="Goal identifier")
    notes: str = Field(default="", description="Additional notes")
    
    @field_validator('equity_pct', 'fi_pct', 'cash_pct')
    @classmethod
    def validate_allocation(cls, v, info):
        if v < 0 or v > 1:
            raise ValueError(f"{info.field_name} must be between 0 and 1")
        return v


class GoalResultModel(BaseModel):
    """Result of goal-based simulation"""
    goal_name: str = Field(description="Goal name")
    goal_id: Optional[str] = Field(description="Goal identifier")
    priority: GoalPriorityEnum = Field(description="Goal priority")
    status: GoalStatusEnum = Field(description="Goal status")
    
    # Target and timing
    target_amount: float = Field(description="Target amount needed")
    target_year: int = Field(description="Year when goal is needed")
    years_remaining: int = Field(description="Years until goal")
    
    # Simulation results
    probability_of_success: float = Field(ge=0, le=1, description="Probability of meeting goal")
    median_value_at_target: float = Field(description="Median portfolio value at goal date")
    percentile_10: float = Field(description="10th percentile value")
    percentile_90: float = Field(description="90th percentile value")
    
    # Funding analysis
    current_funding_pct: float = Field(ge=0, description="Current funding as % of target")
    expected_shortfall: float = Field(ge=0, description="Expected $ shortfall in failure scenarios")
    shortfall_probability: float = Field(ge=0, le=1, description="Probability of shortfall")
    
    # Recommendations
    additional_funding_needed: float = Field(ge=0, description="Additional annual funding to reach target")
    recommendation: str = Field(description="Action recommendation")
    
    # Statistics
    scenarios_succeeded: int = Field(description="Number of scenarios that met goal")
    scenarios_failed: int = Field(description="Number of scenarios that failed")


class GoalConflictModel(BaseModel):
    """Detected conflict between goals"""
    conflict_type: str = Field(description="Type of conflict (funding_competition, priority_mismatch)")
    description: str = Field(description="Human-readable conflict description")
    goals_affected: List[str] = Field(description="Names of goals in conflict")
    total_funding_gap: Optional[float] = Field(default=None, description="Total $ gap across goals")
    recommendation: str = Field(description="Recommendation to resolve conflict")


class GoalAnalysisRequest(BaseModel):
    """Request for goal-based planning analysis"""
    current_year: int = Field(default=2024, description="Current calendar year")
    goals: List[GoalInputModel] = Field(description="Goals to analyze")
    
    # Market assumptions (optional - will use defaults if not provided)
    equity_return_annual: Optional[float] = Field(default=0.07, description="Expected equity return")
    fi_return_annual: Optional[float] = Field(default=0.02, description="Expected FI return")
    cash_return_annual: Optional[float] = Field(default=0.00, description="Expected cash return")
    equity_volatility: Optional[float] = Field(default=0.18, description="Equity volatility")
    fi_volatility: Optional[float] = Field(default=0.06, description="FI volatility")
    cash_volatility: Optional[float] = Field(default=0.01, description="Cash volatility")
    
    n_scenarios: int = Field(default=1000, ge=100, le=10000, description="Number of Monte Carlo scenarios")


class GoalAnalysisResponse(BaseModel):
    """Response containing goal analysis results"""
    goals: List[GoalResultModel] = Field(description="Results for each goal")
    conflicts: List[GoalConflictModel] = Field(default_factory=list, description="Detected conflicts")
    overall_summary: str = Field(description="Overall portfolio goal analysis summary")
    total_annual_funding_needed: float = Field(description="Total additional funding across all goals")
    critical_goals_count: int = Field(description="Number of critical priority goals")
    on_track_count: int = Field(description="Number of goals on track")
    at_risk_count: int = Field(description="Number of goals at risk")


# ============================================================================
# ENHANCED NARRATIVE REPORT MODELS
# ============================================================================

class RiskLevelEnum(str, Enum):
    """Risk severity levels"""
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    CRITICAL = "critical"


class RiskTypeEnum(str, Enum):
    """Types of financial risks"""
    SEQUENCE_OF_RETURNS = "sequence_of_returns"
    LONGEVITY = "longevity"
    INFLATION = "inflation"
    HEALTHCARE_COSTS = "healthcare_costs"
    PORTFOLIO_DEPLETION = "portfolio_depletion"
    TAX_INEFFICIENCY = "tax_inefficiency"
    SPENDING_UNSUSTAINABLE = "spending_unsustainable"
    CONCENTRATION = "concentration"
    MARKET_VOLATILITY = "market_volatility"


class IdentifiedRiskModel(BaseModel):
    """A specific identified risk"""
    risk_type: RiskTypeEnum = Field(description="Type of risk")
    severity: RiskLevelEnum = Field(description="Risk severity level")
    probability: float = Field(ge=0, le=1, description="Probability of risk materializing")
    potential_impact: float = Field(description="Dollar amount or percentage impact")
    description: str = Field(description="Risk description in plain language")
    mitigation_strategy: str = Field(description="Specific mitigation steps")
    priority_rank: int = Field(description="Priority rank (1 = highest)")


class RecommendationModel(BaseModel):
    """An actionable recommendation"""
    title: str = Field(description="Recommendation title")
    description: str = Field(description="Detailed description")
    expected_benefit: str = Field(description="Expected outcome/benefit")
    implementation_steps: List[str] = Field(description="Concrete implementation steps")
    priority: int = Field(description="Priority (1 = highest)")
    category: str = Field(description="Category (spending, allocation, tax, insurance)")


class ExecutiveSummaryModel(BaseModel):
    """Natural language executive summary"""
    plan_overview: str = Field(description="Plan overview in plain English")
    success_probability_narrative: str = Field(description="Success probability explanation")
    key_strengths: List[str] = Field(description="Key plan strengths")
    key_concerns: List[str] = Field(description="Key concerns to address")
    bottom_line: str = Field(description="Bottom-line recommendation")


class FailurePatternModel(BaseModel):
    """Pattern observed in failed scenarios"""
    pattern_name: str = Field(description="Pattern name")
    frequency: float = Field(ge=0, le=1, description="Percentage of failures showing this pattern")
    typical_failure_year: int = Field(description="Typical year when failure occurs")
    description: str = Field(description="Pattern description")
    prevention_strategy: str = Field(description="Strategy to prevent this failure pattern")


class FailureAnalysisModel(BaseModel):
    """Failure scenario analysis"""
    failure_count: int = Field(description="Number of scenarios that failed")
    failure_rate: float = Field(ge=0, le=1, description="Failure rate")
    avg_failure_year: Optional[int] = Field(description="Average year of failure")
    median_failure_year: Optional[int] = Field(description="Median year of failure")
    earliest_failure_year: Optional[int] = Field(description="Earliest failure year observed")
    patterns: List[FailurePatternModel] = Field(description="Identified failure patterns")
    summary: str = Field(description="Failure analysis summary")
    prevention_strategies: List[str] = Field(description="Overall prevention strategies")


class WhatIfScenarioModel(BaseModel):
    """Alternative what-if scenario"""
    scenario: str = Field(description="Scenario name")
    change: str = Field(description="What changes in this scenario")
    impact: str = Field(description="Expected impact")
    trade_off: str = Field(description="Trade-offs to consider")


class WorstCaseAnalysisModel(BaseModel):
    """Worst-case (10th percentile) analysis"""
    percentile_10_value: float = Field(description="10th percentile ending value")
    max_drawdown_pct: float = Field(ge=0, le=1, description="Maximum drawdown percentage")
    turning_point_year: int = Field(description="Year when problems begin")
    recovery_time_years: Optional[int] = Field(description="Years to recover (if at all)")
    description: str = Field(description="Worst-case scenario description")
    recovery_strategies: List[str] = Field(description="Specific recovery strategies")
    what_if_scenarios: List[WhatIfScenarioModel] = Field(description="Alternative scenarios to consider")


class EnhancedNarrativeReportModel(BaseModel):
    """Complete enhanced narrative report"""
    executive_summary: ExecutiveSummaryModel = Field(description="Executive summary")
    identified_risks: List[IdentifiedRiskModel] = Field(description="Top identified risks")
    recommendations: List[RecommendationModel] = Field(description="Prioritized recommendations")
    failure_analysis: Optional[FailureAnalysisModel] = Field(default=None, description="Failure scenario analysis")
    worst_case_analysis: Optional[WorstCaseAnalysisModel] = Field(default=None, description="Worst-case analysis")
    report_generated_at: str = Field(description="Report generation timestamp")


class NarrativeReportRequest(BaseModel):
    """Request for enhanced narrative report"""
    # Monte Carlo simulation results
    success_probability: float = Field(ge=0, le=1, description="Success probability")
    median_ending_value: float = Field(description="Median ending portfolio value")
    percentile_10_value: float = Field(description="10th percentile value")
    percentile_90_value: float = Field(description="90th percentile value")
    
    # Plan parameters
    starting_portfolio: float = Field(gt=0, description="Starting portfolio value")
    years_to_model: int = Field(ge=1, le=50, description="Planning horizon")
    current_age: int = Field(ge=18, le=100, description="Current age")
    monthly_spending: float = Field(description="Monthly spending (negative)")
    
    # Asset allocation
    equity_pct: float = Field(ge=0, le=1, description="Equity allocation")
    
    # Optional: Monte Carlo paths for detailed analysis
    all_paths: Optional[List[List[float]]] = Field(
        default=None,
        description="All Monte Carlo paths for failure/worst-case analysis"
    )
    
    # Optional: Goal-based planning
    has_goals: bool = Field(default=False, description="Whether goal-based planning is used")
    goals_on_track_count: int = Field(default=0, description="Number of goals on track")
    total_goals: int = Field(default=0, description="Total number of goals")
    
    # Options
    include_failure_analysis: bool = Field(default=True, description="Include failure analysis")
    include_worst_case_analysis: bool = Field(default=True, description="Include worst-case analysis")


class NarrativeReportResponse(BaseModel):
    """Response containing enhanced narrative report"""
    report: EnhancedNarrativeReportModel = Field(description="Complete narrative report")
    success: bool = Field(default=True, description="Request success status")
    message: Optional[str] = Field(default=None, description="Optional message")
