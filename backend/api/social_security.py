"""
Social Security API Endpoints
=============================

FastAPI routes for Social Security claiming optimization.
"""

from fastapi import APIRouter, HTTPException, status
from typing import List
import logging
from datetime import datetime

from models.social_security_schemas import (
    IndividualAnalysisRequest,
    IndividualAnalysisResponse,
    CoupleAnalysisRequest,
    CoupleAnalysisResponse,
    ClaimingScenarioResponse,
    CoupleScenarioResponse,
    BenefitStreamResponse,
    SSSummaryStats,
)
from core.social_security_engine import (
    PersonProfile,
    AnalysisAssumptions,
    get_full_retirement_age,
    get_life_expectancy,
    analyze_individual_scenario,
    analyze_couple_scenario,
    find_optimal_claiming_ages,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/social-security", tags=["Social Security"])


def _format_age_display(years: int, months: int = 0) -> str:
    """Format age for display (e.g., '67' or '66y 10m')"""
    if months == 0:
        return str(years)
    return f"{years}y {months}m"


def _convert_benefit_stream(stream) -> BenefitStreamResponse:
    """Convert engine BenefitStream to API response"""
    return BenefitStreamResponse(
        ages=stream.ages,
        annual_benefits_gross=stream.annual_benefits_gross,
        annual_benefits_net=stream.annual_benefits_net,
        cumulative_gross=stream.cumulative_gross,
        cumulative_net=stream.cumulative_net,
        cumulative_invested=stream.cumulative_invested,
    )


def _convert_claiming_scenario(scenario) -> ClaimingScenarioResponse:
    """Convert engine ClaimingScenario to API response"""
    claiming_years = int(scenario.claiming_age)
    claiming_months = int((scenario.claiming_age - claiming_years) * 12)
    
    return ClaimingScenarioResponse(
        claiming_age=scenario.claiming_age,
        claiming_age_display=_format_age_display(claiming_years, claiming_months),
        monthly_benefit_initial=scenario.monthly_benefit_initial,
        annual_benefit_initial=scenario.annual_benefit_initial,
        benefit_stream=_convert_benefit_stream(scenario.benefit_stream),
        npv_gross=scenario.npv_gross,
        npv_net=scenario.npv_net,
        break_even_age=scenario.break_even_age,
        break_even_age_display=(
            _format_age_display(int(scenario.break_even_age), int((scenario.break_even_age - int(scenario.break_even_age)) * 12))
            if scenario.break_even_age else None
        ),
        cumulative_at_75=scenario.cumulative_at_ages.get(75),
        cumulative_at_80=scenario.cumulative_at_ages.get(80),
        cumulative_at_85=scenario.cumulative_at_ages.get(85),
        cumulative_at_90=scenario.cumulative_at_ages.get(90),
    )


def _convert_couple_scenario(scenario) -> CoupleScenarioResponse:
    """Convert engine CoupleScenario to API response"""
    a_years = int(scenario.spouse_a_claiming_age)
    a_months = int((scenario.spouse_a_claiming_age - a_years) * 12)
    b_years = int(scenario.spouse_b_claiming_age)
    b_months = int((scenario.spouse_b_claiming_age - b_years) * 12)
    
    return CoupleScenarioResponse(
        spouse_a_claiming_age=scenario.spouse_a_claiming_age,
        spouse_a_claiming_age_display=_format_age_display(a_years, a_months),
        spouse_b_claiming_age=scenario.spouse_b_claiming_age,
        spouse_b_claiming_age_display=_format_age_display(b_years, b_months),
        combined_benefit_stream=_convert_benefit_stream(scenario.combined_benefit_stream),
        npv_household_gross=scenario.npv_household_gross,
        npv_household_net=scenario.npv_household_net,
        survivor_benefit_value=scenario.survivor_benefit_value,
        cumulative_at_ages=scenario.cumulative_at_ages,
    )


@router.post("/analyze-individual", response_model=IndividualAnalysisResponse)
async def analyze_individual(request: IndividualAnalysisRequest):
    """
    Analyze Social Security claiming strategies for an individual.
    
    Calculates benefit streams, NPV, break-even ages for one or more claiming ages.
    """
    try:
        logger.info(f"Individual SS analysis: birth {request.person.birth_year}/{request.person.birth_month}, "
                   f"claiming {request.person.claiming_age_years}y {request.person.claiming_age_months}m")
        
        # Convert API models to engine data classes
        profile = PersonProfile(
            birth_year=request.person.birth_year,
            birth_month=request.person.birth_month,
            gender=request.person.gender.value,
            benefit_at_fra=request.person.benefit_at_fra,
            claiming_age_years=request.person.claiming_age_years,
            claiming_age_months=request.person.claiming_age_months,
        )
        
        assumptions = AnalysisAssumptions(
            investment_return_annual=request.assumptions.investment_return_annual,
            cola_annual=request.assumptions.cola_annual,
            discount_rate_real=request.assumptions.discount_rate_real,
            marginal_tax_rate=request.assumptions.marginal_tax_rate,
            ss_taxable_portion=request.assumptions.ss_taxable_portion,
        )
        
        # Get FRA and life expectancy
        fra_years, fra_months = get_full_retirement_age(profile.birth_year, profile.birth_month)
        life_expectancy = (
            request.assumptions.life_expectancy_override
            if request.assumptions.life_expectancy_override
            else get_life_expectancy(profile.claiming_age_years, profile.gender)
        )
        
        # Analyze primary scenario
        primary_scenario = analyze_individual_scenario(profile, assumptions)
        
        # Compare additional ages if requested
        comparison_scenarios = []
        if request.compare_ages:
            for age in request.compare_ages:
                if age != profile.claiming_age_years:
                    compare_profile = PersonProfile(
                        birth_year=profile.birth_year,
                        birth_month=profile.birth_month,
                        gender=profile.gender,
                        benefit_at_fra=profile.benefit_at_fra,
                        claiming_age_years=age,
                        claiming_age_months=0,
                    )
                    scenario = analyze_individual_scenario(compare_profile, assumptions)
                    comparison_scenarios.append(scenario)
        
        # Find optimal
        all_ages = [62, 63, 64, 65, 66, 67, 68, 69, 70]
        optimal_scenarios = find_optimal_claiming_ages(
            PersonProfile(
                birth_year=profile.birth_year,
                birth_month=profile.birth_month,
                gender=profile.gender,
                benefit_at_fra=profile.benefit_at_fra,
                claiming_age_years=67,  # placeholder
                claiming_age_months=0,
            ),
            assumptions,
            age_range=all_ages
        )
        optimal_age = optimal_scenarios[0].claiming_age
        
        # Generate recommendations
        recommendation_notes = []
        
        if life_expectancy < 80:
            recommendation_notes.append(
                f"With life expectancy of {life_expectancy}, earlier claiming (62-65) may be advantageous."
            )
            recommended_range = (62, 65)
        elif life_expectancy > 88:
            recommendation_notes.append(
                f"With life expectancy of {life_expectancy}, delaying to 70 maximizes lifetime benefits."
            )
            recommended_range = (67, 70)
        else:
            recommendation_notes.append(
                "With average life expectancy, claiming at FRA or delaying is typically optimal."
            )
            recommended_range = (fra_years, 70)
        
        if assumptions.investment_return_annual > 0.06:
            recommendation_notes.append(
                f"Higher investment returns ({assumptions.investment_return_annual*100:.1f}%) favor earlier claiming."
            )
        
        if assumptions.marginal_tax_rate > 0.30:
            recommendation_notes.append(
                "High tax rate reduces benefit value; consider tax planning strategies."
            )
        
        return IndividualAnalysisResponse(
            birth_year=profile.birth_year,
            birth_month=profile.birth_month,
            gender=profile.gender,
            fra_years=fra_years,
            fra_months=fra_months,
            fra_display=_format_age_display(fra_years, fra_months),
            life_expectancy=life_expectancy,
            primary_scenario=_convert_claiming_scenario(primary_scenario),
            comparison_scenarios=[_convert_claiming_scenario(s) for s in comparison_scenarios],
            optimal_claiming_age=optimal_age,
            recommended_range_min=recommended_range[0],
            recommended_range_max=recommended_range[1],
            recommendation_notes=recommendation_notes,
        )
    
    except Exception as e:
        logger.error(f"Error in individual SS analysis: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Analysis failed: {str(e)}"
        )


@router.post("/analyze-couple", response_model=CoupleAnalysisResponse)
async def analyze_couple(request: CoupleAnalysisRequest):
    """
    Analyze Social Security claiming strategies for a married couple.
    
    Considers combined household benefits and survivor benefits.
    Optionally analyzes all age combinations (grid search).
    """
    try:
        logger.info(f"Couple SS analysis: A={request.spouse_a.claiming_age_years}, "
                   f"B={request.spouse_b.claiming_age_years}, grid={request.analyze_grid}")
        
        # Convert to engine data classes
        spouse_a_profile = PersonProfile(
            birth_year=request.spouse_a.birth_year,
            birth_month=request.spouse_a.birth_month,
            gender=request.spouse_a.gender.value,
            benefit_at_fra=request.spouse_a.benefit_at_fra,
            claiming_age_years=request.spouse_a.claiming_age_years,
            claiming_age_months=request.spouse_a.claiming_age_months,
        )
        
        spouse_b_profile = PersonProfile(
            birth_year=request.spouse_b.birth_year,
            birth_month=request.spouse_b.birth_month,
            gender=request.spouse_b.gender.value,
            benefit_at_fra=request.spouse_b.benefit_at_fra,
            claiming_age_years=request.spouse_b.claiming_age_years,
            claiming_age_months=request.spouse_b.claiming_age_months,
        )
        
        assumptions = AnalysisAssumptions(
            investment_return_annual=request.assumptions.investment_return_annual,
            cola_annual=request.assumptions.cola_annual,
            discount_rate_real=request.assumptions.discount_rate_real,
            marginal_tax_rate=request.assumptions.marginal_tax_rate,
            ss_taxable_portion=request.assumptions.ss_taxable_portion,
        )
        
        # Get FRA and life expectancy for both
        fra_a_years, fra_a_months = get_full_retirement_age(spouse_a_profile.birth_year, spouse_a_profile.birth_month)
        fra_b_years, fra_b_months = get_full_retirement_age(spouse_b_profile.birth_year, spouse_b_profile.birth_month)
        
        life_exp_a = (
            request.assumptions.life_expectancy_override
            if request.assumptions.life_expectancy_override
            else get_life_expectancy(spouse_a_profile.claiming_age_years, spouse_a_profile.gender)
        )
        life_exp_b = get_life_expectancy(spouse_b_profile.claiming_age_years, spouse_b_profile.gender)
        
        # Analyze primary scenario (specified ages)
        primary_scenario = analyze_couple_scenario(spouse_a_profile, spouse_b_profile, assumptions)
        
        # Grid analysis if requested
        grid_results = None
        optimal_scenario = primary_scenario
        
        if request.analyze_grid:
            grid_results = []
            best_npv = primary_scenario.npv_household_net
            
            for age_a in range(62, 71):
                for age_b in range(62, 71):
                    temp_a = PersonProfile(
                        birth_year=spouse_a_profile.birth_year,
                        birth_month=spouse_a_profile.birth_month,
                        gender=spouse_a_profile.gender,
                        benefit_at_fra=spouse_a_profile.benefit_at_fra,
                        claiming_age_years=age_a,
                        claiming_age_months=0,
                    )
                    temp_b = PersonProfile(
                        birth_year=spouse_b_profile.birth_year,
                        birth_month=spouse_b_profile.birth_month,
                        gender=spouse_b_profile.gender,
                        benefit_at_fra=spouse_b_profile.benefit_at_fra,
                        claiming_age_years=age_b,
                        claiming_age_months=0,
                    )
                    scenario = analyze_couple_scenario(temp_a, temp_b, assumptions)
                    grid_results.append(scenario)
                    
                    if scenario.npv_household_net > best_npv:
                        best_npv = scenario.npv_household_net
                        optimal_scenario = scenario
        
        # Generate recommendations
        recommendation_notes = []
        
        if spouse_a_profile.benefit_at_fra > spouse_b_profile.benefit_at_fra * 1.5:
            recommendation_notes.append(
                "Higher earner should consider delaying to maximize survivor benefits."
            )
        
        if abs(life_exp_a - life_exp_b) > 5:
            recommendation_notes.append(
                "Significant life expectancy difference: longer-lived spouse may benefit from delaying."
            )
        
        recommendation_notes.append(
            "Coordinate claiming to maximize household benefits and survivor protection."
        )
        
        return CoupleAnalysisResponse(
            spouse_a_fra=_format_age_display(fra_a_years, fra_a_months),
            spouse_b_fra=_format_age_display(fra_b_years, fra_b_months),
            spouse_a_life_expectancy=life_exp_a,
            spouse_b_life_expectancy=life_exp_b,
            primary_scenario=_convert_couple_scenario(primary_scenario),
            grid_analysis=[_convert_couple_scenario(s) for s in grid_results] if grid_results else None,
            optimal_scenario=_convert_couple_scenario(optimal_scenario),
            recommendation_notes=recommendation_notes,
        )
    
    except Exception as e:
        logger.error(f"Error in couple SS analysis: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Couple analysis failed: {str(e)}"
        )


@router.post("/compare-scenarios", response_model=IndividualAnalysisResponse)
async def compare_scenarios(request: IndividualAnalysisRequest):
    """
    Compare multiple claiming age scenarios side-by-side.
    
    Convenience endpoint that defaults to comparing ages 62, 65, 67, and 70.
    """
    if not request.compare_ages:
        request.compare_ages = [62, 65, 67, 70]
    
    return await analyze_individual(request)


@router.get("/summary-stats", response_model=SSSummaryStats)
async def get_summary_stats(
    birth_year: int,
    birth_month: int,
    benefit_at_fra: float,
    gender: str = "male",
):
    """
    Quick summary statistics for dashboard display.
    
    Returns optimal age and break-even points without full analysis.
    """
    try:
        profile_base = PersonProfile(
            birth_year=birth_year,
            birth_month=birth_month,
            gender=gender,
            benefit_at_fra=benefit_at_fra,
            claiming_age_years=67,
            claiming_age_months=0,
        )
        
        assumptions = AnalysisAssumptions()
        
        # Analyze key ages
        scenarios = {}
        for age in [62, 67, 70]:
            profile = PersonProfile(
                birth_year=birth_year,
                birth_month=birth_month,
                gender=gender,
                benefit_at_fra=benefit_at_fra,
                claiming_age_years=age,
                claiming_age_months=0,
            )
            scenarios[age] = analyze_individual_scenario(profile, assumptions)
        
        # Find optimal
        optimal_list = find_optimal_claiming_ages(profile_base, assumptions, list(range(62, 71)))
        optimal_age = int(optimal_list[0].claiming_age)
        optimal_npv = optimal_list[0].npv_net
        
        return SSSummaryStats(
            optimal_age_individual=optimal_age,
            optimal_npv_individual=optimal_npv,
            benefit_at_62_monthly=scenarios[62].benefits.annual_benefits_gross[0] / 12,
            benefit_at_67_monthly=scenarios[67].benefits.annual_benefits_gross[0] / 12,
            benefit_at_70_monthly=scenarios[70].benefits.annual_benefits_gross[0] / 12,
            break_even_62_vs_67=scenarios[67].break_even_age,
            break_even_67_vs_70=scenarios[70].break_even_age,
        )
    
    except Exception as e:
        logger.error(f"Error getting SS summary stats: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Summary stats failed: {str(e)}"
        )
