"""
Social Security API Schemas
============================

Pydantic models for Social Security optimization API.
"""

from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Dict
from datetime import date
from enum import Enum


class Gender(str, Enum):
    """Gender for life expectancy calculations"""
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"


class PersonInputModel(BaseModel):
    """Input for individual person in SS analysis"""
    birth_year: int = Field(ge=1930, le=2010, description="Year of birth")
    birth_month: int = Field(ge=1, le=12, description="Month of birth (1-12)")
    gender: Gender = Field(description="Gender for life expectancy calculations")
    benefit_at_fra: float = Field(gt=0, le=5000, description="Monthly benefit at Full Retirement Age ($)")
    claiming_age_years: int = Field(ge=62, le=70, description="Claiming age in years")
    claiming_age_months: int = Field(default=0, ge=0, le=11, description="Additional months for claiming age")


class AssumptionsInputModel(BaseModel):
    """Economic and longevity assumptions"""
    investment_return_annual: float = Field(
        default=0.05,
        ge=0.0,
        le=0.15,
        description="Annual investment return rate for invested benefits (e.g., 0.05 = 5%)"
    )
    inflation_annual: float = Field(
        default=0.025,
        ge=0.0,
        le=0.10,
        description="Annual inflation rate (e.g., 0.025 = 2.5%)"
    )
    cola_annual: float = Field(
        default=0.025,
        ge=0.0,
        le=0.10,
        description="Annual Social Security COLA rate (e.g., 0.025 = 2.5%)"
    )
    discount_rate_real: float = Field(
        default=0.02,
        ge=0.0,
        le=0.10,
        description="Real discount rate for NPV calculations (e.g., 0.02 = 2%)"
    )
    marginal_tax_rate: float = Field(
        default=0.22,
        ge=0.0,
        le=0.50,
        description="Marginal tax rate on ordinary income (e.g., 0.22 = 22%)"
    )
    ss_taxable_portion: float = Field(
        default=0.85,
        ge=0.0,
        le=0.85,
        description="Portion of SS benefits that are taxable (0.0 to 0.85)"
    )
    life_expectancy_override: Optional[int] = Field(
        default=None,
        ge=70,
        le=120,
        description="Override life expectancy (age at death). Leave null for actuarial table."
    )


class IndividualAnalysisRequest(BaseModel):
    """Request for individual Social Security analysis"""
    person: PersonInputModel = Field(description="Person profile")
    assumptions: AssumptionsInputModel = Field(
        default_factory=AssumptionsInputModel,
        description="Economic assumptions"
    )
    compare_ages: Optional[List[int]] = Field(
        default=None,
        description="Additional claiming ages to compare (e.g., [62, 65, 67, 70])"
    )


class CoupleAnalysisRequest(BaseModel):
    """Request for couple Social Security analysis"""
    spouse_a: PersonInputModel = Field(description="First spouse profile")
    spouse_b: PersonInputModel = Field(description="Second spouse profile")
    assumptions: AssumptionsInputModel = Field(
        default_factory=AssumptionsInputModel,
        description="Economic assumptions"
    )
    analyze_grid: bool = Field(
        default=False,
        description="If true, analyze all combinations of claiming ages 62-70"
    )


class BenefitStreamResponse(BaseModel):
    """Time series of benefits"""
    ages: List[int] = Field(description="Ages (years)")
    annual_benefits_gross: List[float] = Field(description="Gross annual benefits")
    annual_benefits_net: List[float] = Field(description="After-tax annual benefits")
    cumulative_gross: List[float] = Field(description="Cumulative gross benefits")
    cumulative_net: List[float] = Field(description="Cumulative net benefits")
    cumulative_invested: List[float] = Field(
        description="Cumulative value if benefits invested at assumed return rate"
    )


class ClaimingScenarioResponse(BaseModel):
    """Results for single claiming age scenario"""
    claiming_age: float = Field(description="Claiming age (decimal years)")
    claiming_age_display: str = Field(description="Formatted claiming age (e.g., '62' or '65y 6m')")
    monthly_benefit_initial: float = Field(description="Initial monthly benefit ($)")
    annual_benefit_initial: float = Field(description="Initial annual benefit ($)")
    benefit_stream: BenefitStreamResponse = Field(description="Benefit stream over time")
    npv_gross: float = Field(description="Net Present Value of gross benefits ($)")
    npv_net: float = Field(description="Net Present Value of after-tax benefits ($)")
    break_even_age: Optional[float] = Field(
        default=None,
        description="Break-even age vs baseline (typically age 67)"
    )
    break_even_age_display: Optional[str] = Field(
        default=None,
        description="Formatted break-even age"
    )
    cumulative_at_75: Optional[float] = Field(default=None, description="Cumulative net benefits at age 75")
    cumulative_at_80: Optional[float] = Field(default=None, description="Cumulative net benefits at age 80")
    cumulative_at_85: Optional[float] = Field(default=None, description="Cumulative net benefits at age 85")
    cumulative_at_90: Optional[float] = Field(default=None, description="Cumulative net benefits at age 90")


class IndividualAnalysisResponse(BaseModel):
    """Response for individual Social Security analysis"""
    success: bool = True
    message: str = "Analysis completed successfully"
    
    # Person info
    birth_year: int
    birth_month: int
    gender: str
    fra_years: int = Field(description="Full Retirement Age (years)")
    fra_months: int = Field(description="Full Retirement Age (additional months)")
    fra_display: str = Field(description="Formatted FRA (e.g., '67' or '66y 10m')")
    life_expectancy: int = Field(description="Expected age at death")
    
    # Primary scenario
    primary_scenario: ClaimingScenarioResponse
    
    # Comparison scenarios
    comparison_scenarios: List[ClaimingScenarioResponse] = Field(
        default_factory=list,
        description="Additional scenarios for comparison"
    )
    
    # Recommendations
    optimal_claiming_age: float = Field(
        description="Optimal claiming age based on NPV maximization"
    )
    recommended_range_min: int = Field(
        description="Conservative recommended minimum claiming age"
    )
    recommended_range_max: int = Field(
        description="Conservative recommended maximum claiming age"
    )
    recommendation_notes: List[str] = Field(
        default_factory=list,
        description="Plain-language notes explaining recommendations"
    )


class CoupleScenarioResponse(BaseModel):
    """Results for couple scenario"""
    spouse_a_claiming_age: float
    spouse_a_claiming_age_display: str
    spouse_b_claiming_age: float
    spouse_b_claiming_age_display: str
    
    combined_benefit_stream: BenefitStreamResponse
    npv_household_gross: float = Field(description="Household NPV (gross)")
    npv_household_net: float = Field(description="Household NPV (net)")
    survivor_benefit_value: float = Field(description="Estimated survivor benefit value")
    
    cumulative_at_ages: Dict[int, float] = Field(
        default_factory=dict,
        description="Household cumulative benefits at key ages"
    )


class CoupleAnalysisResponse(BaseModel):
    """Response for couple Social Security analysis"""
    success: bool = True
    message: str = "Couple analysis completed successfully"
    
    # Couple info
    spouse_a_fra: str
    spouse_b_fra: str
    spouse_a_life_expectancy: int
    spouse_b_life_expectancy: int
    
    # Primary scenario (specified claiming ages)
    primary_scenario: CoupleScenarioResponse
    
    # Grid analysis (if requested)
    grid_analysis: Optional[List[CoupleScenarioResponse]] = Field(
        default=None,
        description="All combinations of claiming ages if analyze_grid=True"
    )
    
    # Optimal scenario
    optimal_scenario: CoupleScenarioResponse = Field(
        description="Optimal claiming age combination based on NPV"
    )
    
    # Recommendations
    recommendation_notes: List[str] = Field(
        default_factory=list,
        description="Plain-language notes for couple strategy"
    )


class SSSummaryStats(BaseModel):
    """Quick summary statistics for dashboard"""
    optimal_age_individual: int
    optimal_npv_individual: float
    benefit_at_62_monthly: float
    benefit_at_67_monthly: float
    benefit_at_70_monthly: float
    break_even_62_vs_67: Optional[float]
    break_even_67_vs_70: Optional[float]
