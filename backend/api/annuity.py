"""
Annuity API endpoints - SPIA, DIA, and QLAC pricing and analysis.
Provides institutional-grade annuity quotes and comparison tools.
"""
from fastapi import APIRouter, HTTPException
from typing import Dict, Any
import logging

from models.schemas import (
    AnnuityInputs,
    AnnuityQuoteResult,
    QLACRulesResult,
    AnnuityComparisonRequest,
    AnnuityComparisonResult,
    AnnuityResponse,
    AnnuityTypeEnum,
    LifeOptionEnum,
    GenderEnum,
    HealthStatusEnum
)
from core.annuity_engine import (
    AnnuityEngine,
    Gender,
    HealthStatus,
    LifeOption,
    AnnuityType
)

router = APIRouter()
logger = logging.getLogger(__name__)


def map_gender(gender_enum: GenderEnum) -> Gender:
    """Map schema enum to engine enum"""
    return Gender.MALE if gender_enum == GenderEnum.MALE else Gender.FEMALE


def map_health(health_enum: HealthStatusEnum) -> HealthStatus:
    """Map schema enum to engine enum"""
    health_map = {
        HealthStatusEnum.POOR: HealthStatus.POOR,
        HealthStatusEnum.AVERAGE: HealthStatus.AVERAGE,
        HealthStatusEnum.GOOD: HealthStatus.GOOD,
        HealthStatusEnum.EXCELLENT: HealthStatus.EXCELLENT
    }
    return health_map.get(health_enum, HealthStatus.AVERAGE)


def map_life_option(life_enum: LifeOptionEnum) -> LifeOption:
    """Map schema enum to engine enum"""
    life_map = {
        LifeOptionEnum.LIFE_ONLY: LifeOption.LIFE_ONLY,
        LifeOptionEnum.LIFE_WITH_10_CERTAIN: LifeOption.LIFE_WITH_10_CERTAIN,
        LifeOptionEnum.LIFE_WITH_20_CERTAIN: LifeOption.LIFE_WITH_20_CERTAIN,
        LifeOptionEnum.JOINT_LIFE: LifeOption.JOINT_LIFE,
        LifeOptionEnum.JOINT_SURVIVOR_100: LifeOption.JOINT_SURVIVOR_100,
        LifeOptionEnum.JOINT_SURVIVOR_50: LifeOption.JOINT_SURVIVOR_50
    }
    return life_map.get(life_enum, LifeOption.LIFE_ONLY)


@router.post("/quote", response_model=AnnuityResponse)
async def get_annuity_quote(request: AnnuityInputs):
    """
    Get annuity pricing quote for SPIA, DIA, or QLAC.
    
    This endpoint provides institutional-grade annuity pricing using:
    - Mortality tables (SOA 2012 Individual Annuity Mortality)
    - Actuarial present value calculations
    - Market load factors (insurance company markup)
    - Longevity credit quantification
    
    **Annuity Types:**
    - **SPIA** (Single Premium Immediate Annuity): Payments start immediately
    - **DIA** (Deferred Income Annuity): Payments start at future date
    - **QLAC** (Qualified Longevity Annuity Contract): IRA-funded DIA with RMD exclusion
    
    **Example Request (SPIA):**
    ```json
    {
        "annuity_type": "spia",
        "premium": 250000,
        "purchase_age": 65,
        "gender": "male",
        "health_status": "good",
        "life_option": "life_only",
        "cola_pct": 0.0
    }
    ```
    
    **Example Request (QLAC):**
    ```json
    {
        "annuity_type": "qlac",
        "premium": 150000,
        "purchase_age": 70,
        "start_age": 80,
        "ira_balance": 800000,
        "gender": "female",
        "health_status": "average"
    }
    ```
    
    **Returns:**
    - Payout rates and amounts
    - Actuarial metrics (longevity credit, breakeven)
    - Tax treatment (exclusion ratio)
    - QLAC rules validation (if applicable)
    """
    try:
        logger.info(f"Annuity quote request: {request.annuity_type.value}, ${request.premium:,.0f}")
        
        engine = AnnuityEngine(seed=42)
        
        # Map enums
        gender = map_gender(request.gender)
        health = map_health(request.health_status)
        life_option = map_life_option(request.life_option)
        
        # Route to appropriate pricing function
        if request.annuity_type == AnnuityTypeEnum.SPIA:
            quote = engine.quote_spia(
                premium=request.premium,
                age=request.purchase_age,
                gender=gender,
                health_status=health,
                life_option=life_option,
                cola_pct=request.cola_pct,
                smoker=request.smoker
            )
            qlac_rules = None
            
        elif request.annuity_type == AnnuityTypeEnum.DIA:
            if not request.start_age:
                raise HTTPException(status_code=400, detail="start_age required for DIA")
            
            quote = engine.quote_dia(
                premium=request.premium,
                purchase_age=request.purchase_age,
                start_age=request.start_age,
                gender=gender,
                health_status=health,
                life_option=life_option,
                cola_pct=request.cola_pct,
                smoker=request.smoker
            )
            qlac_rules = None
            
        elif request.annuity_type == AnnuityTypeEnum.QLAC:
            if not request.start_age:
                raise HTTPException(status_code=400, detail="start_age required for QLAC")
            if not request.ira_balance:
                raise HTTPException(status_code=400, detail="ira_balance required for QLAC")
            
            quote, qlac_rules_obj = engine.quote_qlac(
                premium=request.premium,
                purchase_age=request.purchase_age,
                start_age=request.start_age,
                ira_balance=request.ira_balance,
                gender=gender,
                health_status=health,
                life_option=life_option,
                smoker=request.smoker
            )
            
            # Convert to schema
            max_25_pct = request.ira_balance * 0.25
            max_allowed = min(max_25_pct, 200_000)
            
            qlac_rules = QLACRulesResult(
                max_premium_pct=0.25,
                max_premium_dollar=200_000.0,
                max_start_age=85,
                rmd_exclusion=True,
                must_be_ira_funded=True,
                premium_within_limits=request.premium <= max_allowed,
                start_age_valid=request.start_age <= 85,
                max_allowed_premium=max_allowed
            )
        
        else:
            raise HTTPException(status_code=400, detail=f"Unknown annuity type: {request.annuity_type}")
        
        # Convert quote to schema
        quote_result = AnnuityQuoteResult(
            annuity_type=request.annuity_type,
            premium=quote.premium,
            annual_payout=quote.annual_payout,
            monthly_payout=quote.monthly_payout,
            payout_rate=quote.payout_rate,
            expected_total_payments=quote.expected_total_payments,
            expected_years_of_payments=quote.expected_years_of_payments,
            longevity_credit=quote.longevity_credit,
            breakeven_years=quote.breakeven_years,
            actuarial_present_value=quote.actuarial_present_value,
            load_factor=quote.load_factor,
            insurance_company_margin=quote.insurance_company_margin,
            purchase_age=quote.purchase_age,
            start_age=quote.start_age,
            deferral_years=quote.deferral_years,
            life_expectancy=quote.life_expectancy,
            life_option=request.life_option,
            cola_pct=quote.cola_pct,
            has_refund=quote.has_refund,
            exclusion_ratio=quote.exclusion_ratio,
            taxable_portion_pct=quote.taxable_portion_pct
        )
        
        logger.info(f"✓ Quote generated: ${quote_result.annual_payout:,.0f}/year ({quote_result.payout_rate:.2%})")
        
        return AnnuityResponse(
            success=True,
            message=f"{request.annuity_type.value.upper()} quote generated successfully",
            quote=quote_result,
            qlac_rules=qlac_rules
        )
        
    except ValueError as e:
        logger.error(f"Validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Annuity pricing error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Annuity pricing failed: {str(e)}")


@router.post("/compare", response_model=AnnuityResponse)
async def compare_annuity_vs_portfolio(request: AnnuityComparisonRequest):
    """
    Compare purchasing annuity vs. keeping money in portfolio.
    
    This analysis helps answer:
    - Should I annuitize some/all of my portfolio?
    - What's the trade-off between guaranteed income and flexibility?
    - How much longevity insurance am I buying?
    
    **Analysis Performed:**
    1. Price SPIA for requested premium
    2. Monte Carlo simulation of portfolio with same withdrawals
    3. Calculate depletion probability and ending values
    4. Compare guaranteed income vs. flexibility trade-off
    5. Generate recommendation based on risk tolerance
    
    **Example Request:**
    ```json
    {
        "premium": 300000,
        "age": 65,
        "annual_spending": 18000,
        "portfolio_return": 0.05,
        "portfolio_vol": 0.10,
        "gender": "male",
        "health_status": "good",
        "n_scenarios": 1000
    }
    ```
    
    **Returns:**
    - Annuity option: guaranteed income, longevity credit
    - Portfolio option: depletion risk, ending values
    - Recommendation: based on risk/return trade-off
    """
    try:
        logger.info(f"Comparison request: ${request.premium:,.0f} annuity vs portfolio")
        
        engine = AnnuityEngine(seed=42)
        
        gender = map_gender(request.gender)
        health = map_health(request.health_status)
        
        comparison_dict = engine.compare_annuity_vs_portfolio(
            premium=request.premium,
            age=request.age,
            annual_spending=request.annual_spending,
            portfolio_return=request.portfolio_return,
            portfolio_vol=request.portfolio_vol,
            gender=gender,
            health_status=health,
            smoker=request.smoker,
            n_scenarios=request.n_scenarios
        )
        
        # Convert to schema
        comparison_result = AnnuityComparisonResult(
            annuity_option=comparison_dict["annuity"],
            portfolio_option=comparison_dict["portfolio"],
            recommendation=comparison_dict["recommendation"]
        )
        
        logger.info(f"✓ Comparison complete")
        logger.info(f"  Annuity: ${comparison_dict['annuity']['annual_income']:,.0f}/year guaranteed")
        logger.info(f"  Portfolio: {comparison_dict['portfolio']['depletion_probability']:.1%} depletion risk")
        
        return AnnuityResponse(
            success=True,
            message="Annuity vs. portfolio comparison completed",
            comparison=comparison_result
        )
        
    except Exception as e:
        logger.error(f"Comparison error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Comparison failed: {str(e)}")


@router.get("/info/{annuity_type}", response_model=Dict[str, Any])
async def get_annuity_info(annuity_type: str):
    """
    Get educational information about annuity product types.
    
    Provides plain-language explanations of:
    - How the product works
    - Key benefits and drawbacks
    - Typical use cases
    - Tax treatment
    - Important considerations
    
    **Supported Types:** spia, dia, qlac
    """
    annuity_info = {
        "spia": {
            "name": "Single Premium Immediate Annuity",
            "description": "Convert lump sum to guaranteed lifetime income starting immediately.",
            "how_it_works": "Pay premium today, start receiving monthly/annual payments within 1 year.",
            "key_benefits": [
                "Guaranteed income for life (eliminates longevity risk)",
                "Simple and predictable",
                "Higher payout than bonds/CDs",
                "Longevity credit from mortality pooling"
            ],
            "key_drawbacks": [
                "Irrevocable (can't get premium back)",
                "No flexibility to adjust payments",
                "No death benefit (life only option)",
                "Lose purchasing power if no COLA"
            ],
            "typical_use_cases": [
                "Retiree age 65-75 seeking income floor",
                "Cover essential expenses",
                "Simplify retirement planning",
                "Peace of mind over portfolio management"
            ],
            "tax_treatment": "Partially taxable (exclusion ratio). Portion of each payment is return of principal (tax-free), rest is taxable income.",
            "payout_rate_example": "Age 65 male: ~5.5-6.0% per year"
        },
        "dia": {
            "name": "Deferred Income Annuity",
            "description": "Longevity insurance - payments start at future date (e.g., age 80).",
            "how_it_works": "Pay premium today, payments start 10-20 years later. Much higher payout rate than SPIA due to time value and survival credit.",
            "key_benefits": [
                "Insures against living too long",
                "Very high payout rates (15-25% per year at age 80)",
                "Reduces need for large portfolio",
                "Frees up assets for early retirement"
            ],
            "key_drawbacks": [
                "No benefit if die before start date",
                "Long deferral period",
                "Irrevocable",
                "Inflation risk if no COLA"
            ],
            "typical_use_cases": [
                "Age 65, plan for income starting age 80+",
                "Hedge against outliving portfolio",
                "Complement Social Security for late-life needs",
                "Cover healthcare costs in advanced age"
            ],
            "tax_treatment": "Same as SPIA - exclusion ratio applies",
            "payout_rate_example": "Age 65 purchase, age 80 start: ~18-22% per year"
        },
        "qlac": {
            "name": "Qualified Longevity Annuity Contract",
            "description": "Special DIA funded from IRA/401(k) with RMD exclusion benefit.",
            "how_it_works": "Transfer up to $200k (or 25% of IRA) to QLAC. Amount excluded from RMD calculations. Payments must start by age 85.",
            "key_benefits": [
                "Reduces Required Minimum Distributions",
                "Lower RMDs = lower taxes and Medicare premiums",
                "All benefits of DIA plus RMD relief",
                "Can save $50k-100k in lifetime taxes"
            ],
            "key_drawbacks": [
                "Strict IRS limits ($200k max)",
                "Must start by age 85",
                "All payments fully taxable (pre-tax money)",
                "Can only use IRA/401(k) funds"
            ],
            "typical_use_cases": [
                "High-income retiree with large IRA",
                "Concerned about RMDs pushing into higher tax bracket",
                "Want to reduce Medicare IRMAA surcharges",
                "Estate planning (reduce IRA for heirs)"
            ],
            "tax_treatment": "100% taxable as ordinary income (funded with pre-tax dollars)",
            "payout_rate_example": "Age 70 purchase, age 80 start: ~16-20% per year",
            "irs_limits": {
                "max_premium": 200000,
                "max_pct_of_ira": 0.25,
                "max_start_age": 85,
                "rmd_exclusion": True
            }
        }
    }
    
    annuity_type = annuity_type.lower()
    if annuity_type not in annuity_info:
        raise HTTPException(
            status_code=404,
            detail=f"Annuity type '{annuity_type}' not found. Valid types: spia, dia, qlac"
        )
    
    return annuity_info[annuity_type]
