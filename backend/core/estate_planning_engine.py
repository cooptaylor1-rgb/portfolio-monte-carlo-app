"""
Estate Planning Engine - Sprint 6

Comprehensive estate and inheritance planning calculator including:
- Federal and state estate tax calculations (2024 rules)
- Inherited IRA taxation under SECURE Act 2.0
- Basis step-up modeling for taxable accounts
- Roth conversion analysis for heirs

Key Regulations:
- Federal estate tax: $13.61M exemption (2024), 40% rate above
- SECURE Act 2.0: 10-year rule for inherited IRAs (no more stretch)
- Step-up in basis: Taxable accounts reset cost basis at death
- Portability: Surviving spouse can use deceased spouse's exemption
"""

from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional, Tuple
import numpy as np


class StateEstateTax(Enum):
    """States with estate or inheritance taxes (2024)"""
    NONE = "none"
    # Estate taxes
    CONNECTICUT = "ct"  # $13.61M exemption, 12% rate
    HAWAII = "hi"  # $5.49M exemption, 20% rate
    ILLINOIS = "il"  # $4M exemption, 16% rate
    MAINE = "me"  # $6.41M exemption, 12% rate
    MARYLAND = "md"  # $5M exemption, 16% rate (also inheritance tax)
    MASSACHUSETTS = "ma"  # $2M exemption, 16% rate
    MINNESOTA = "mn"  # $3M exemption, 16% rate
    NEW_YORK = "ny"  # $6.94M exemption, 16% rate
    OREGON = "or"  # $1M exemption, 16% rate
    RHODE_ISLAND = "ri"  # $1.8M exemption, 16% rate
    VERMONT = "vt"  # $5M exemption, 16% rate
    WASHINGTON = "wa"  # $2.2M exemption, 20% rate
    DISTRICT_OF_COLUMBIA = "dc"  # $4.53M exemption, 16% rate


@dataclass
class StateEstateTaxRules:
    """State-specific estate tax rules"""
    exemption: float  # State exemption amount
    top_rate: float  # Top marginal rate
    has_cliff: bool  # Some states have cliff (lose entire exemption if over)
    cliff_threshold: Optional[float]  # Threshold where exemption phases out


STATE_TAX_RULES = {
    StateEstateTax.CONNECTICUT: StateEstateTaxRules(13_610_000, 0.12, False, None),
    StateEstateTax.HAWAII: StateEstateTaxRules(5_490_000, 0.20, False, None),
    StateEstateTax.ILLINOIS: StateEstateTaxRules(4_000_000, 0.16, False, None),
    StateEstateTax.MAINE: StateEstateTaxRules(6_410_000, 0.12, False, None),
    StateEstateTax.MARYLAND: StateEstateTaxRules(5_000_000, 0.16, False, None),
    StateEstateTax.MASSACHUSETTS: StateEstateTaxRules(2_000_000, 0.16, True, 2_000_000),  # Cliff
    StateEstateTax.MINNESOTA: StateEstateTaxRules(3_000_000, 0.16, False, None),
    StateEstateTax.NEW_YORK: StateEstateTaxRules(6_940_000, 0.16, True, 6_940_000),  # Cliff
    StateEstateTax.OREGON: StateEstateTaxRules(1_000_000, 0.16, False, None),
    StateEstateTax.RHODE_ISLAND: StateEstateTaxRules(1_788_000, 0.16, False, None),
    StateEstateTax.VERMONT: StateEstateTaxRules(5_000_000, 0.16, False, None),
    StateEstateTax.WASHINGTON: StateEstateTaxRules(2_193_000, 0.20, False, None),
    StateEstateTax.DISTRICT_OF_COLUMBIA: StateEstateTaxRules(4_528_800, 0.16, False, None),
}


@dataclass
class EstateTaxResult:
    """Estate tax calculation results"""
    gross_estate: float
    federal_exemption_used: float
    federal_taxable_estate: float
    federal_estate_tax: float
    state_exemption_used: float
    state_taxable_estate: float
    state_estate_tax: float
    total_estate_tax: float
    net_to_heirs: float
    effective_tax_rate: float
    portability_available: float  # Unused exemption for surviving spouse


@dataclass
class InheritedIRAResult:
    """Inherited IRA taxation analysis"""
    ira_balance: float
    heir_age: int
    heir_tax_bracket: float
    distribution_strategy: str  # "lump_sum", "even_10yr", "delayed_10yr"
    total_distributions: float
    total_income_tax: float
    net_to_heir: float
    effective_tax_rate: float
    annual_distributions: List[Tuple[int, float, float]]  # (year, distribution, tax)
    comparison_to_stretch: Optional[Dict[str, float]]  # Compare to old stretch IRA


@dataclass
class BasisStepUpResult:
    """Step-up in basis analysis"""
    account_value: float
    original_cost_basis: float
    unrealized_gains: float
    capital_gains_eliminated: float  # Gain that disappears at death
    ltcg_tax_saved: float  # Tax saved vs selling before death
    heir_new_basis: float  # Stepped-up basis
    strategy_comparison: Dict[str, float]  # Different timing strategies


@dataclass
class RothConversionForHeirsResult:
    """Roth conversion analysis from heir's perspective"""
    traditional_ira_balance: float
    conversion_amount: float
    owner_age: int
    owner_tax_rate: float
    heir_age: int
    heir_tax_bracket: float
    years_until_inheritance: int
    
    # Costs and benefits
    upfront_conversion_tax: float
    growth_years: int
    projected_roth_value: float
    projected_trad_ira_value: float
    
    # Heir outcomes
    roth_inheritance_value: float  # Tax-free to heir
    trad_ira_inheritance_tax: float  # Tax heir pays on Traditional IRA
    net_benefit_to_heir: float
    
    # NPV analysis
    npv_roth_strategy: float
    npv_trad_ira_strategy: float
    npv_advantage: float
    
    # Recommendation
    recommended_strategy: str
    break_even_years: int


class EstatePlanningEngine:
    """
    Comprehensive estate planning calculator
    
    This engine models estate taxes, inheritance taxation, basis step-up,
    and Roth conversion strategies to optimize wealth transfer to heirs.
    """
    
    # Federal estate tax parameters (2024)
    FEDERAL_EXEMPTION_2024 = 13_610_000
    FEDERAL_EXEMPTION_2026_SUNSET = 7_000_000  # Approximate after sunset
    FEDERAL_ESTATE_TAX_RATE = 0.40
    
    # Capital gains rates
    LTCG_RATE_0_PERCENT = 0.00  # Income < $44,625 (single) / $89,250 (joint)
    LTCG_RATE_15_PERCENT = 0.15  # Income < $492,300 (single) / $553,850 (joint)
    LTCG_RATE_20_PERCENT = 0.20  # Income above thresholds
    NIIT_RATE = 0.038  # Net Investment Income Tax (3.8%)
    
    def __init__(self):
        self.federal_exemption = self.FEDERAL_EXEMPTION_2024
        
    def calculate_estate_tax(
        self,
        gross_estate: float,
        state: StateEstateTax = StateEstateTax.NONE,
        is_married: bool = False,
        spousal_exemption_used: float = 0,
        apply_2026_sunset: bool = False
    ) -> EstateTaxResult:
        """
        Calculate federal and state estate taxes
        
        Args:
            gross_estate: Total estate value
            state: State for estate tax calculation
            is_married: Whether married (affects portability)
            spousal_exemption_used: Spouse's unused exemption (portability)
            apply_2026_sunset: Use post-2026 lower exemption
            
        Returns:
            EstateTaxResult with tax calculations
        """
        # Federal exemption
        base_exemption = (
            self.FEDERAL_EXEMPTION_2026_SUNSET if apply_2026_sunset 
            else self.FEDERAL_EXEMPTION_2024
        )
        
        # Add portability if applicable
        federal_exemption = base_exemption + spousal_exemption_used
        
        # Calculate federal tax
        federal_taxable = max(0, gross_estate - federal_exemption)
        federal_tax = federal_taxable * self.FEDERAL_ESTATE_TAX_RATE
        
        # Calculate state tax
        state_tax = 0
        state_exemption = 0
        state_taxable = 0
        
        if state != StateEstateTax.NONE and state in STATE_TAX_RULES:
            rules = STATE_TAX_RULES[state]
            state_exemption = rules.exemption
            
            # Check for cliff provision
            if rules.has_cliff and gross_estate > rules.cliff_threshold:
                # Lose exemption entirely (MA, NY)
                state_taxable = gross_estate
            else:
                state_taxable = max(0, gross_estate - state_exemption)
            
            state_tax = state_taxable * rules.top_rate
        
        # Calculate totals
        total_tax = federal_tax + state_tax
        net_to_heirs = gross_estate - total_tax
        effective_rate = total_tax / gross_estate if gross_estate > 0 else 0
        
        # Calculate unused exemption for portability
        portability_available = max(0, federal_exemption - gross_estate) if is_married else 0
        
        return EstateTaxResult(
            gross_estate=gross_estate,
            federal_exemption_used=min(federal_exemption, gross_estate),
            federal_taxable_estate=federal_taxable,
            federal_estate_tax=federal_tax,
            state_exemption_used=min(state_exemption, gross_estate),
            state_taxable_estate=state_taxable,
            state_estate_tax=state_tax,
            total_estate_tax=total_tax,
            net_to_heirs=net_to_heirs,
            effective_tax_rate=effective_rate,
            portability_available=portability_available
        )
    
    def calculate_inherited_ira_tax(
        self,
        ira_balance: float,
        heir_age: int,
        heir_current_income: float,
        heir_filing_status: str = "single",
        distribution_strategy: str = "even_10yr",
        growth_rate: float = 0.06,
        compare_to_stretch: bool = True
    ) -> InheritedIRAResult:
        """
        Calculate taxation of inherited IRA under SECURE Act 2.0
        
        SECURE Act (2020) eliminated stretch IRA for most beneficiaries.
        Must distribute entire balance within 10 years.
        
        Args:
            ira_balance: IRA balance at inheritance
            heir_age: Beneficiary's age
            heir_current_income: Heir's current taxable income
            heir_filing_status: "single" or "married"
            distribution_strategy: "lump_sum", "even_10yr", "delayed_10yr"
            growth_rate: IRA growth rate during 10-year period
            compare_to_stretch: Compare to old stretch IRA rules
            
        Returns:
            InheritedIRAResult with tax analysis
        """
        from .tax_engine import TaxEngine
        tax_engine = TaxEngine()
        
        annual_distributions = []
        total_tax = 0
        remaining_balance = ira_balance
        
        if distribution_strategy == "lump_sum":
            # Take entire IRA in year 1
            taxable_income = heir_current_income + ira_balance
            tax_bracket = tax_engine.calculate_marginal_rate(taxable_income, heir_filing_status)
            tax_on_distribution = ira_balance * tax_bracket
            total_tax = tax_on_distribution
            annual_distributions.append((1, ira_balance, tax_on_distribution))
            
        elif distribution_strategy == "even_10yr":
            # Distribute evenly over 10 years
            annual_distribution = ira_balance / 10
            
            for year in range(1, 11):
                # Account grows at growth_rate
                distribution = min(annual_distribution, remaining_balance)
                taxable_income = heir_current_income + distribution
                tax_bracket = tax_engine.calculate_marginal_rate(taxable_income, heir_filing_status)
                tax = distribution * tax_bracket
                total_tax += tax
                annual_distributions.append((year, distribution, tax))
                
                remaining_balance -= distribution
                remaining_balance *= (1 + growth_rate)
                
        elif distribution_strategy == "delayed_10yr":
            # Delay until year 10, let IRA grow
            for year in range(1, 10):
                remaining_balance *= (1 + growth_rate)
            
            # Take entire amount in year 10
            taxable_income = heir_current_income + remaining_balance
            tax_bracket = tax_engine.calculate_marginal_rate(taxable_income, heir_filing_status)
            tax = remaining_balance * tax_bracket
            total_tax = tax
            annual_distributions.append((10, remaining_balance, tax))
        
        total_distributions = sum(dist for _, dist, _ in annual_distributions)
        net_to_heir = total_distributions - total_tax
        effective_rate = total_tax / total_distributions if total_distributions > 0 else 0
        
        # Compare to old stretch IRA rules (if requested)
        stretch_comparison = None
        if compare_to_stretch:
            # Old rule: Could stretch over heir's life expectancy
            life_expectancy = 85 - heir_age  # Simplified
            annual_rmd = ira_balance / life_expectancy
            
            # Estimate tax over life expectancy (simplified)
            stretch_total = 0
            stretch_tax = 0
            balance = ira_balance
            
            for year in range(min(life_expectancy, 40)):  # Cap at 40 years
                rmd = balance / (life_expectancy - year)
                taxable = heir_current_income + rmd
                bracket = tax_engine.calculate_marginal_rate(taxable, heir_filing_status)
                tax = rmd * bracket
                
                stretch_total += rmd
                stretch_tax += tax
                balance -= rmd
                balance *= (1 + growth_rate)
            
            stretch_net = stretch_total - stretch_tax
            
            stretch_comparison = {
                "stretch_total_distributions": stretch_total,
                "stretch_total_tax": stretch_tax,
                "stretch_net_to_heir": stretch_net,
                "secure_act_penalty": net_to_heir - stretch_net,  # How much heir loses
                "tax_acceleration": stretch_tax - total_tax  # How much more/less tax
            }
        
        return InheritedIRAResult(
            ira_balance=ira_balance,
            heir_age=heir_age,
            heir_tax_bracket=tax_engine.calculate_marginal_rate(
                heir_current_income, heir_filing_status
            ),
            distribution_strategy=distribution_strategy,
            total_distributions=total_distributions,
            total_income_tax=total_tax,
            net_to_heir=net_to_heir,
            effective_tax_rate=effective_rate,
            annual_distributions=annual_distributions,
            comparison_to_stretch=stretch_comparison
        )
    
    def calculate_basis_step_up(
        self,
        account_value: float,
        cost_basis: float,
        ltcg_rate: float = 0.20,
        state_cap_gains_rate: float = 0.0,
        hold_vs_sell_years: int = 5
    ) -> BasisStepUpResult:
        """
        Calculate tax savings from step-up in basis at death
        
        Taxable accounts get basis reset to FMV at death, eliminating capital gains.
        
        Args:
            account_value: Current market value
            cost_basis: Original cost basis
            ltcg_rate: Federal long-term capital gains rate
            state_cap_gains_rate: State capital gains rate
            hold_vs_sell_years: Years to compare holding vs selling
            
        Returns:
            BasisStepUpResult with tax savings analysis
        """
        unrealized_gains = account_value - cost_basis
        
        # Tax if sold before death
        total_cg_rate = ltcg_rate + state_cap_gains_rate + self.NIIT_RATE
        tax_if_sold_now = unrealized_gains * total_cg_rate
        
        # After death: heir gets stepped-up basis
        heir_new_basis = account_value
        capital_gains_eliminated = unrealized_gains
        ltcg_tax_saved = capital_gains_eliminated * total_cg_rate
        
        # Strategy comparison
        strategies = {
            "sell_before_death": account_value - tax_if_sold_now,
            "inherit_with_step_up": account_value,  # Full value, no tax
            "tax_savings": ltcg_tax_saved,
            "effective_benefit_rate": ltcg_tax_saved / account_value
        }
        
        return BasisStepUpResult(
            account_value=account_value,
            original_cost_basis=cost_basis,
            unrealized_gains=unrealized_gains,
            capital_gains_eliminated=capital_gains_eliminated,
            ltcg_tax_saved=ltcg_tax_saved,
            heir_new_basis=heir_new_basis,
            strategy_comparison=strategies
        )
    
    def analyze_roth_conversion_for_heirs(
        self,
        traditional_ira_balance: float,
        conversion_amount: float,
        owner_age: int,
        owner_tax_rate: float,
        heir_age: int,
        heir_tax_bracket: float,
        years_until_inheritance: int,
        ira_growth_rate: float = 0.07,
        discount_rate: float = 0.04
    ) -> RothConversionForHeirsResult:
        """
        Analyze Roth conversion from heir's perspective
        
        Trade-off: Pay tax now (owner's rate) vs heir pays later (heir's rate)
        Roth grows tax-free and heir inherits tax-free.
        
        Args:
            traditional_ira_balance: Current IRA balance
            conversion_amount: Amount to convert to Roth
            owner_age: Current owner's age
            owner_tax_rate: Owner's marginal tax rate
            heir_age: Heir's current age
            heir_tax_bracket: Heir's expected tax bracket
            years_until_inheritance: Years until expected inheritance
            ira_growth_rate: IRA growth rate
            discount_rate: Discount rate for NPV
            
        Returns:
            RothConversionForHeirsResult with analysis
        """
        # Cost: Upfront conversion tax
        upfront_tax = conversion_amount * owner_tax_rate
        
        # Scenario 1: Convert to Roth
        roth_value_at_death = conversion_amount * ((1 + ira_growth_rate) ** years_until_inheritance)
        roth_inheritance_value = roth_value_at_death  # Tax-free to heir
        
        # Scenario 2: Keep as Traditional IRA
        trad_ira_value_at_death = conversion_amount * ((1 + ira_growth_rate) ** years_until_inheritance)
        
        # Heir must pay tax on Traditional IRA distributions (10-year rule)
        # Assume heir takes even distributions over 10 years
        heir_inheritance_tax = trad_ira_value_at_death * heir_tax_bracket
        trad_ira_net_to_heir = trad_ira_value_at_death - heir_inheritance_tax
        
        # Net benefit to heir
        net_benefit = roth_inheritance_value - trad_ira_net_to_heir
        
        # NPV analysis
        # Roth: Pay upfront_tax now, get roth_value at death
        roth_npv = -upfront_tax + (roth_inheritance_value / ((1 + discount_rate) ** years_until_inheritance))
        
        # Traditional: No cost now, get trad_ira_net at death
        trad_npv = trad_ira_net_to_heir / ((1 + discount_rate) ** years_until_inheritance)
        
        npv_advantage = roth_npv - trad_npv
        
        # Recommendation
        if npv_advantage > 0:
            recommended = "Convert to Roth - saves heir taxes"
        elif owner_tax_rate < heir_tax_bracket:
            recommended = "Convert to Roth - owner's lower tax rate"
        else:
            recommended = "Keep Traditional IRA - conversion cost too high"
        
        # Break-even calculation
        # Years where Roth strategy equals Traditional IRA strategy
        # Simplified: when does tax savings offset upfront cost?
        tax_rate_differential = heir_tax_bracket - owner_tax_rate
        if tax_rate_differential > 0 and ira_growth_rate > 0:
            # Rough approximation
            break_even = int(np.log(1 + (upfront_tax / (conversion_amount * tax_rate_differential))) / 
                           np.log(1 + ira_growth_rate))
        else:
            break_even = 999  # Never breaks even
        
        return RothConversionForHeirsResult(
            traditional_ira_balance=traditional_ira_balance,
            conversion_amount=conversion_amount,
            owner_age=owner_age,
            owner_tax_rate=owner_tax_rate,
            heir_age=heir_age,
            heir_tax_bracket=heir_tax_bracket,
            years_until_inheritance=years_until_inheritance,
            upfront_conversion_tax=upfront_tax,
            growth_years=years_until_inheritance,
            projected_roth_value=roth_value_at_death,
            projected_trad_ira_value=trad_ira_value_at_death,
            roth_inheritance_value=roth_inheritance_value,
            trad_ira_inheritance_tax=heir_inheritance_tax,
            net_benefit_to_heir=net_benefit,
            npv_roth_strategy=roth_npv,
            npv_trad_ira_strategy=trad_npv,
            npv_advantage=npv_advantage,
            recommended_strategy=recommended,
            break_even_years=break_even
        )
    
    def comprehensive_estate_plan(
        self,
        gross_estate: float,
        traditional_ira: float,
        roth_ira: float,
        taxable_account: float,
        taxable_cost_basis: float,
        state: StateEstateTax = StateEstateTax.NONE,
        heir_age: int = 45,
        heir_income: float = 150_000,
        years_until_inheritance: int = 20
    ) -> Dict[str, any]:
        """
        Comprehensive estate planning analysis combining all components
        
        Returns recommendations for estate tax minimization, Roth conversions,
        and optimal asset allocation.
        """
        results = {}
        
        # 1. Estate tax analysis
        estate_tax = self.calculate_estate_tax(gross_estate, state)
        results["estate_tax"] = estate_tax
        
        # 2. Inherited IRA analysis
        if traditional_ira > 0:
            ira_analysis = self.calculate_inherited_ira_tax(
                traditional_ira, heir_age, heir_income,
                distribution_strategy="even_10yr"
            )
            results["inherited_ira"] = ira_analysis
        
        # 3. Basis step-up analysis
        if taxable_account > 0:
            step_up = self.calculate_basis_step_up(
                taxable_account, taxable_cost_basis
            )
            results["basis_step_up"] = step_up
        
        # 4. Roth conversion opportunities
        if traditional_ira > 0:
            # Analyze converting 25%, 50%, 75% of Traditional IRA
            conversion_scenarios = []
            for pct in [0.25, 0.50, 0.75]:
                conversion = self.analyze_roth_conversion_for_heirs(
                    traditional_ira,
                    traditional_ira * pct,
                    owner_age=65,  # Assumed
                    owner_tax_rate=0.24,
                    heir_age=heir_age,
                    heir_tax_bracket=0.32,
                    years_until_inheritance=years_until_inheritance
                )
                conversion_scenarios.append({
                    "conversion_percentage": pct,
                    "analysis": conversion
                })
            results["roth_conversion_scenarios"] = conversion_scenarios
        
        # 5. Recommendations
        recommendations = []
        
        if estate_tax.total_estate_tax > 0:
            recommendations.append({
                "priority": "high",
                "category": "estate_tax",
                "message": f"Estate tax liability: ${estate_tax.total_estate_tax:,.0f}",
                "actions": [
                    "Consider gifting during lifetime ($18k/year per recipient)",
                    "Irrevocable life insurance trust (ILIT) to remove insurance from estate",
                    "Charitable remainder trust for tax deduction"
                ]
            })
        
        if "inherited_ira" in results:
            ira = results["inherited_ira"]
            if ira.total_income_tax > traditional_ira * 0.25:
                recommendations.append({
                    "priority": "high",
                    "category": "ira_taxation",
                    "message": f"Heir will pay ${ira.total_income_tax:,.0f} in taxes on inherited IRA",
                    "actions": [
                        "Consider Roth conversions during low-income years",
                        "Qualified charitable distributions (QCDs) after age 70.5",
                        "Strategic timing of RMDs"
                    ]
                })
        
        if "basis_step_up" in results:
            step_up = results["basis_step_up"]
            if step_up.ltcg_tax_saved > 50_000:
                recommendations.append({
                    "priority": "medium",
                    "category": "basis_step_up",
                    "message": f"Step-up in basis will save ${step_up.ltcg_tax_saved:,.0f} in capital gains",
                    "actions": [
                        "Hold highly appreciated assets until death (don't sell)",
                        "Prioritize spending from IRAs over taxable accounts",
                        "Consider gifting low-basis assets vs cash"
                    ]
                })
        
        results["recommendations"] = recommendations
        
        return results
