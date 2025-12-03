"""
Pydantic models for API request/response validation.
These models define the data contracts between frontend and backend.
"""
from pydantic import BaseModel, Field, field_validator
from typing import List, Optional
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
    tax_rate: float = Field(default=0.25, ge=0, le=0.50, description="Marginal tax rate")
    rmd_age: int = Field(default=73, ge=70, le=75, description="RMD starting age")
    
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


class SimulationMetrics(BaseModel):
    """Key metrics from simulation results"""
    success_probability: float = Field(description="Probability of success")
    ending_median: float = Field(description="Median ending portfolio value")
    ending_p10: float = Field(description="10th percentile ending value")
    ending_p90: float = Field(description="90th percentile ending value")
    years_depleted: float = Field(description="Average years until depletion")
    depletion_probability: float = Field(description="Probability of depletion")
    shortfall_risk: float = Field(description="Shortfall risk percentage")


class SimulationResponse(BaseModel):
    """Response from Monte Carlo simulation"""
    metrics: SimulationMetrics
    stats: List[dict] = Field(description="Monthly statistics (percentiles)")
    goal_probabilities: Optional[List[dict]] = Field(default=None, description="Goal achievement probabilities")
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
