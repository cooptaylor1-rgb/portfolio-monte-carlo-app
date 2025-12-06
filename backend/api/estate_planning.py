"""
Estate Planning API Endpoints

Provides comprehensive estate planning analysis including:
- Federal and state estate taxes
- Inherited IRA taxation (SECURE Act 2.0)
- Basis step-up in taxable accounts
- Roth conversion analysis for heirs
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, List
from models.schemas import (
    EstatePlanningInputs,
    EstatePlanningResponse,
    EstatePlanningResult,
    EstateTaxSummary,
    InheritedIRASummary,
    BasisStepUpSummary,
    RothConversionScenario,
    EstatePlanningRecommendation,
    StateEstateTaxEnum
)
from core.estate_planning_engine import (
    EstatePlanningEngine,
    StateEstateTax
)

router = APIRouter()


def map_state_enum(state: StateEstateTaxEnum) -> StateEstateTax:
    """Map Pydantic enum to engine enum"""
    mapping = {
        StateEstateTaxEnum.NONE: StateEstateTax.NONE,
        StateEstateTaxEnum.CONNECTICUT: StateEstateTax.CONNECTICUT,
        StateEstateTaxEnum.HAWAII: StateEstateTax.HAWAII,
        StateEstateTaxEnum.ILLINOIS: StateEstateTax.ILLINOIS,
        StateEstateTaxEnum.MAINE: StateEstateTax.MAINE,
        StateEstateTaxEnum.MARYLAND: StateEstateTax.MARYLAND,
        StateEstateTaxEnum.MASSACHUSETTS: StateEstateTax.MASSACHUSETTS,
        StateEstateTaxEnum.MINNESOTA: StateEstateTax.MINNESOTA,
        StateEstateTaxEnum.NEW_YORK: StateEstateTax.NEW_YORK,
        StateEstateTaxEnum.OREGON: StateEstateTax.OREGON,
        StateEstateTaxEnum.RHODE_ISLAND: StateEstateTax.RHODE_ISLAND,
        StateEstateTaxEnum.VERMONT: StateEstateTax.VERMONT,
        StateEstateTaxEnum.WASHINGTON: StateEstateTax.WASHINGTON,
        StateEstateTaxEnum.DISTRICT_OF_COLUMBIA: StateEstateTax.DISTRICT_OF_COLUMBIA,
    }
    return mapping[state]


@router.post("/analyze", response_model=EstatePlanningResponse)
async def analyze_estate_plan(inputs: EstatePlanningInputs):
    """
    Comprehensive estate planning analysis
    
    Analyzes estate taxes, inherited IRA taxation, basis step-up benefits,
    and Roth conversion opportunities to minimize taxes for heirs.
    
    **Key Features:**
    - Federal estate tax with 2024/2026 exemption amounts
    - State estate taxes for 13 states + DC
    - Inherited IRA under SECURE Act 2.0 (10-year rule)
    - Step-up in basis for taxable accounts
    - Roth conversion analysis from heir's perspective
    
    **Example Use Cases:**
    - $15M estate: Analyze federal estate tax exposure
    - $2M IRA inheritance: Compare distribution strategies
    - $5M taxable account: Quantify step-up benefits
    - Roth conversion: Determine optimal amount to convert
    """
    try:
        engine = EstatePlanningEngine()
        
        # Map state enum
        state = map_state_enum(inputs.state)
        
        # 1. Estate tax analysis
        estate_tax = engine.calculate_estate_tax(
            gross_estate=inputs.gross_estate,
            state=state,
            is_married=inputs.is_married,
            spousal_exemption_used=inputs.spousal_exemption_used,
            apply_2026_sunset=inputs.apply_2026_sunset
        )
        
        estate_tax_summary = EstateTaxSummary(
            gross_estate=estate_tax.gross_estate,
            federal_exemption_used=estate_tax.federal_exemption_used,
            federal_taxable_estate=estate_tax.federal_taxable_estate,
            federal_estate_tax=estate_tax.federal_estate_tax,
            state_exemption_used=estate_tax.state_exemption_used,
            state_taxable_estate=estate_tax.state_taxable_estate,
            state_estate_tax=estate_tax.state_estate_tax,
            total_estate_tax=estate_tax.total_estate_tax,
            net_to_heirs=estate_tax.net_to_heirs,
            effective_tax_rate=estate_tax.effective_tax_rate,
            portability_available=estate_tax.portability_available
        )
        
        # 2. Inherited IRA analysis (if applicable)
        inherited_ira_summary = None
        if inputs.traditional_ira > 0:
            ira_result = engine.calculate_inherited_ira_tax(
                ira_balance=inputs.traditional_ira,
                heir_age=inputs.heir_age,
                heir_current_income=inputs.heir_current_income,
                heir_filing_status=inputs.heir_filing_status,
                distribution_strategy="even_10yr",
                compare_to_stretch=True
            )
            
            inherited_ira_summary = InheritedIRASummary(
                ira_balance=ira_result.ira_balance,
                heir_age=ira_result.heir_age,
                heir_tax_bracket=ira_result.heir_tax_bracket,
                distribution_strategy=ira_result.distribution_strategy,
                total_distributions=ira_result.total_distributions,
                total_income_tax=ira_result.total_income_tax,
                net_to_heir=ira_result.net_to_heir,
                effective_tax_rate=ira_result.effective_tax_rate,
                comparison_to_stretch=ira_result.comparison_to_stretch
            )
        
        # 3. Basis step-up analysis (if applicable)
        basis_step_up_summary = None
        if inputs.taxable_account > 0:
            step_up = engine.calculate_basis_step_up(
                account_value=inputs.taxable_account,
                cost_basis=inputs.taxable_cost_basis,
                ltcg_rate=0.20,
                state_cap_gains_rate=0.0
            )
            
            basis_step_up_summary = BasisStepUpSummary(
                account_value=step_up.account_value,
                original_cost_basis=step_up.original_cost_basis,
                unrealized_gains=step_up.unrealized_gains,
                capital_gains_eliminated=step_up.capital_gains_eliminated,
                ltcg_tax_saved=step_up.ltcg_tax_saved,
                heir_new_basis=step_up.heir_new_basis,
                strategy_comparison=step_up.strategy_comparison
            )
        
        # 4. Roth conversion scenarios (if applicable)
        roth_scenarios = []
        if inputs.analyze_roth_conversion and inputs.traditional_ira > 0:
            for pct in inputs.roth_conversion_amounts:
                conversion_amt = inputs.traditional_ira * pct
                
                roth_result = engine.analyze_roth_conversion_for_heirs(
                    traditional_ira_balance=inputs.traditional_ira,
                    conversion_amount=conversion_amt,
                    owner_age=65,  # Assumed
                    owner_tax_rate=0.24,  # Assumed 24% bracket
                    heir_age=inputs.heir_age,
                    heir_tax_bracket=0.32,  # Assumed 32% bracket for heir
                    years_until_inheritance=inputs.years_until_inheritance,
                    ira_growth_rate=0.07,
                    discount_rate=0.04
                )
                
                roth_scenarios.append(RothConversionScenario(
                    conversion_percentage=pct,
                    conversion_amount=conversion_amt,
                    upfront_conversion_tax=roth_result.upfront_conversion_tax,
                    projected_roth_value=roth_result.projected_roth_value,
                    roth_inheritance_value=roth_result.roth_inheritance_value,
                    trad_ira_inheritance_tax=roth_result.trad_ira_inheritance_tax,
                    net_benefit_to_heir=roth_result.net_benefit_to_heir,
                    npv_advantage=roth_result.npv_advantage,
                    recommended_strategy=roth_result.recommended_strategy,
                    break_even_years=roth_result.break_even_years
                ))
        
        # 5. Generate recommendations
        recommendations = []
        
        # Estate tax recommendations
        if estate_tax.total_estate_tax > 0:
            recommendations.append(EstatePlanningRecommendation(
                priority="high",
                category="estate_tax",
                message=f"Estate tax liability: ${estate_tax.total_estate_tax:,.0f} ({estate_tax.effective_tax_rate*100:.1f}%)",
                actions=[
                    f"Annual gifting: ${18_000 * 2:,.0f} per couple to each heir (no tax)",
                    "Irrevocable Life Insurance Trust (ILIT) removes insurance from estate",
                    "Charitable Remainder Trust provides income + estate tax deduction",
                    "Qualified Personal Residence Trust (QPRT) for home transfer"
                ]
            ))
        
        # Inherited IRA recommendations
        if inherited_ira_summary and inherited_ira_summary.total_income_tax > inputs.traditional_ira * 0.25:
            tax_hit = inherited_ira_summary.total_income_tax
            recommendations.append(EstatePlanningRecommendation(
                priority="high",
                category="ira_taxation",
                message=f"Heir will pay ${tax_hit:,.0f} in taxes on inherited IRA (effective {inherited_ira_summary.effective_tax_rate*100:.1f}%)",
                actions=[
                    "Consider Roth conversions during low-income years (see scenarios below)",
                    "Qualified Charitable Distributions (QCDs) after age 70.5 reduce RMDs",
                    "Coordinate Social Security timing with IRA distributions",
                    f"SECURE Act penalty vs old stretch IRA: ${abs(inherited_ira_summary.comparison_to_stretch.get('secure_act_penalty', 0)):,.0f}"
                ]
            ))
        
        # Basis step-up recommendations
        if basis_step_up_summary and basis_step_up_summary.ltcg_tax_saved > 50_000:
            recommendations.append(EstatePlanningRecommendation(
                priority="medium",
                category="basis_step_up",
                message=f"Step-up in basis will save ${basis_step_up_summary.ltcg_tax_saved:,.0f} in capital gains tax",
                actions=[
                    "Hold highly appreciated assets until death (don't sell)",
                    "Prioritize spending from IRAs/401(k)s over taxable accounts",
                    "Consider gifting low-basis assets to heirs vs selling and gifting cash",
                    f"Unrealized gains eliminated: ${basis_step_up_summary.unrealized_gains:,.0f}"
                ]
            ))
        
        # Roth conversion recommendations
        if roth_scenarios:
            best_scenario = max(roth_scenarios, key=lambda x: x.npv_advantage)
            if best_scenario.npv_advantage > 0:
                recommendations.append(EstatePlanningRecommendation(
                    priority="high",
                    category="roth_conversion",
                    message=f"Roth conversion could save heir ${best_scenario.net_benefit_to_heir:,.0f} in taxes (NPV: ${best_scenario.npv_advantage:,.0f})",
                    actions=[
                        f"Optimal conversion: {best_scenario.conversion_percentage*100:.0f}% (${best_scenario.conversion_amount:,.0f})",
                        f"Upfront tax cost: ${best_scenario.upfront_conversion_tax:,.0f}",
                        f"Break-even: {best_scenario.break_even_years} years",
                        "Execute conversions in years with lower income (retirement, business loss)",
                        "Spread conversions over multiple years to control tax brackets"
                    ]
                ))
        
        # Calculate summary metrics
        total_tax = estate_tax.total_estate_tax
        if inherited_ira_summary:
            total_tax += inherited_ira_summary.total_income_tax
        
        net_to_heirs = inputs.gross_estate - total_tax
        
        # Estimate tax savings opportunities
        tax_savings = 0
        if basis_step_up_summary:
            tax_savings += basis_step_up_summary.ltcg_tax_saved
        if roth_scenarios and len(roth_scenarios) > 0:
            best_roth = max(roth_scenarios, key=lambda x: x.net_benefit_to_heir)
            if best_roth.net_benefit_to_heir > 0:
                tax_savings += best_roth.net_benefit_to_heir
        
        result = EstatePlanningResult(
            estate_tax=estate_tax_summary,
            inherited_ira=inherited_ira_summary,
            basis_step_up=basis_step_up_summary,
            roth_conversion_scenarios=roth_scenarios if roth_scenarios else None,
            recommendations=recommendations,
            total_tax_liability=total_tax,
            net_to_heirs_after_all_taxes=net_to_heirs,
            tax_saving_opportunities=tax_savings
        )
        
        return EstatePlanningResponse(
            success=True,
            message="Estate planning analysis completed successfully",
            result=result
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Estate planning analysis failed: {str(e)}")


@router.get("/info/estate-tax")
async def estate_tax_info():
    """
    Educational information about estate taxes
    
    Returns overview of federal and state estate tax rules,
    exemptions, rates, and planning strategies.
    """
    return {
        "title": "Estate Tax Overview",
        "federal_rules": {
            "2024_exemption": 13_610_000,
            "2026_sunset_exemption": "~$7M (inflation adjusted)",
            "tax_rate": 0.40,
            "portability": "Surviving spouse can use deceased spouse's unused exemption",
            "annual_gifting": "$18,000 per recipient ($36,000 for couples) excluded from estate"
        },
        "state_rules": {
            "states_with_estate_tax": [
                "Connecticut", "Hawaii", "Illinois", "Maine", "Maryland",
                "Massachusetts", "Minnesota", "New York", "Oregon",
                "Rhode Island", "Vermont", "Washington", "DC"
            ],
            "exemption_range": "$1M (Oregon) to $13.61M (Connecticut)",
            "rate_range": "12% to 20%",
            "cliff_states": ["Massachusetts", "New York"]
        },
        "planning_strategies": [
            "Lifetime gifting: $18k/year per person ($36k for couples)",
            "Irrevocable Life Insurance Trust (ILIT): Remove insurance from estate",
            "Charitable Remainder Trust: Income + estate tax deduction",
            "Qualified Personal Residence Trust (QPRT): Transfer home at discount",
            "Family Limited Partnership: Valuation discounts on business/real estate"
        ]
    }


@router.get("/info/inherited-ira")
async def inherited_ira_info():
    """
    Educational information about inherited IRA taxation
    
    Explains SECURE Act 2.0 rules, 10-year distribution requirement,
    and comparison to old stretch IRA rules.
    """
    return {
        "title": "Inherited IRA Under SECURE Act 2.0",
        "secure_act_changes": {
            "effective_date": "January 1, 2020",
            "key_change": "Eliminated stretch IRA for most beneficiaries",
            "new_rule": "10-year distribution requirement",
            "exception_beneficiaries": [
                "Surviving spouse",
                "Minor children (until age of majority)",
                "Disabled individuals",
                "Chronically ill individuals",
                "Beneficiaries <10 years younger than decedent"
            ]
        },
        "old_rules_vs_new": {
            "pre_2020_stretch": "Could stretch distributions over beneficiary's life expectancy (30-50 years)",
            "post_2020_10_year": "Must distribute entire balance within 10 years",
            "tax_impact": "Compressed distributions = higher tax brackets",
            "example": "$1M IRA stretched over 40 years vs $1M over 10 years"
        },
        "distribution_strategies": {
            "lump_sum": "Take all at once - highest tax impact",
            "even_10yr": "Distribute evenly over 10 years - moderate tax",
            "delayed_10yr": "Wait until year 10 - allows maximum growth, potential tax bomb"
        },
        "planning_opportunities": [
            "Roth conversions before death (heir inherits tax-free)",
            "Name trust as beneficiary for control/protection",
            "Coordinate with heir's income (take in low-income years)",
            "Consider charitable beneficiaries for partial IRA"
        ]
    }


@router.get("/info/step-up")
async def step_up_info():
    """
    Educational information about basis step-up
    
    Explains how taxable accounts get cost basis reset at death,
    eliminating capital gains tax.
    """
    return {
        "title": "Step-Up in Basis at Death",
        "how_it_works": {
            "rule": "Taxable assets get new cost basis = fair market value at death",
            "result": "Unrealized capital gains disappear",
            "example": "$100k investment → $500k at death = $400k gain eliminated"
        },
        "what_qualifies": {
            "yes": [
                "Taxable brokerage accounts",
                "Real estate",
                "Business interests",
                "Other capital assets"
            ],
            "no": [
                "IRAs and 401(k)s (no step-up)",
                "Roth IRAs (already tax-free)",
                "Annuities (taxed as ordinary income)"
            ]
        },
        "planning_strategies": [
            "Hold highly appreciated assets until death (don't sell)",
            "Prioritize spending from retirement accounts over taxable",
            "Gift low-basis assets to heirs vs selling and gifting cash",
            "Avoid selling appreciated assets shortly before death"
        ],
        "survivor_planning": {
            "inherited_property": "Consider holding 1-2 years before selling",
            "tax_benefit": "Sell soon after inheritance = little/no capital gains tax",
            "documentation": "Get professional appraisal to establish stepped-up basis"
        }
    }


@router.get("/info/roth-conversion")
async def roth_conversion_info():
    """
    Educational information about Roth conversions for heirs
    
    Explains how converting Traditional IRA to Roth before death
    can save taxes for heirs.
    """
    return {
        "title": "Roth Conversion Strategy for Heirs",
        "key_concept": {
            "trade_off": "Pay tax now (owner's rate) vs heir pays later (heir's rate)",
            "benefit": "Roth grows tax-free + heir inherits tax-free",
            "best_case": "Owner in low bracket, heir in high bracket"
        },
        "when_it_makes_sense": [
            "Owner has low-income years (early retirement, business loss)",
            "Heir expected to be in higher tax bracket",
            "Long time horizon (10+ years until inheritance)",
            "Owner can pay tax from non-retirement funds"
        ],
        "execution_strategies": {
            "multi_year": "Spread conversions over several years to control brackets",
            "roth_ladder": "Convert progressively from age 60-72 (before RMDs)",
            "fill_brackets": "Convert up to top of 24% bracket, avoid 32%+",
            "market_timing": "Convert during market downturns (lower tax cost)"
        },
        "inherited_roth_rules": {
            "10_year_rule": "Heir must still distribute within 10 years",
            "tax_treatment": "All distributions 100% tax-free to heir",
            "rmd_requirement": "No RMDs during 10-year period",
            "optimal_strategy": "Let Roth grow full 10 years, take in year 10"
        },
        "example_scenario": {
            "setup": "$500k Traditional IRA, owner age 65, heir age 45",
            "owner_converts": "Pay $120k tax now (24% bracket)",
            "20_years_growth": "$500k → $1.93M at 7% growth",
            "heir_receives": "$1.93M tax-free",
            "vs_traditional": "Heir would pay $618k tax (32% on $1.93M)",
            "net_benefit": "$498k tax savings for heir"
        }
    }

