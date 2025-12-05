"""
Social Security Optimization Engine
====================================

Comprehensive calculation engine for Social Security claiming analysis.
Supports individual and couple scenarios with investment modeling.

Key Features:
- Full Retirement Age (FRA) calculations based on birth year
- Early claiming reductions (age 62-FRA)
- Delayed retirement credits (FRA-70)
- COLA adjustments over time
- Investment growth modeling for early benefits
- NPV and break-even analysis
- Couple/household benefit aggregation
- Survivor benefit calculations
- After-tax benefit streams
"""

from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional
from datetime import date
from enum import Enum
import numpy as np
import logging

logger = logging.getLogger(__name__)


class Gender(str, Enum):
    """Gender for life expectancy calculations"""
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"


# =============================================================================
# CONSTANTS AND TABLES
# =============================================================================

# Full Retirement Age (FRA) by birth year
# Source: SSA official tables
FRA_TABLE = {
    # Birth year: (years, months)
    1937: (65, 0),
    1938: (65, 2),
    1939: (65, 4),
    1940: (65, 6),
    1941: (65, 8),
    1942: (65, 10),
    # 1943-1954: FRA = 66
    **{year: (66, 0) for year in range(1943, 1955)},
    1955: (66, 2),
    1956: (66, 4),
    1957: (66, 6),
    1958: (66, 8),
    1959: (66, 10),
    # 1960+: FRA = 67
    **{year: (67, 0) for year in range(1960, 2010)},
}

# Life expectancy tables (SSA Actuarial Life Table 2020)
# Format: {age: {gender: remaining_years}}
LIFE_EXPECTANCY_TABLE = {
    62: {Gender.MALE: 20.5, Gender.FEMALE: 23.2, Gender.OTHER: 21.9},
    65: {Gender.MALE: 18.0, Gender.FEMALE: 20.4, Gender.OTHER: 19.2},
    67: {Gender.MALE: 16.4, Gender.FEMALE: 18.6, Gender.OTHER: 17.5},
    70: {Gender.MALE: 14.0, Gender.FEMALE: 16.1, Gender.OTHER: 15.1},
}

# Early claiming reduction factors
# For each month before FRA, benefit is reduced by:
# - First 36 months: 5/9 of 1% per month (6.67% per year)
# - Additional months: 5/12 of 1% per month (5% per year)
EARLY_REDUCTION_RATE_FIRST_36_MONTHS = 5/9 / 100  # per month
EARLY_REDUCTION_RATE_AFTER_36_MONTHS = 5/12 / 100  # per month

# Delayed retirement credits
# For each month after FRA (up to age 70):
# 2/3 of 1% per month = 8% per year
DELAYED_CREDIT_RATE = 2/3 / 100  # per month


# =============================================================================
# DATA CLASSES
# =============================================================================

@dataclass
class PersonProfile:
    """Individual person profile for SS analysis"""
    birth_year: int
    birth_month: int
    gender: Gender
    benefit_at_fra: float  # Monthly benefit at Full Retirement Age
    claiming_age_years: int
    claiming_age_months: int = 0
    
    def claiming_age_decimal(self) -> float:
        """Get claiming age as decimal years"""
        return self.claiming_age_years + self.claiming_age_months / 12.0
    
    def age_in_months(self, years: int, months: int = 0) -> int:
        """Convert age to total months"""
        return years * 12 + months


@dataclass
class AnalysisAssumptions:
    """Economic and longevity assumptions for analysis"""
    investment_return_annual: float = 0.05  # 5% default
    inflation_annual: float = 0.025  # 2.5% default
    cola_annual: float = 0.025  # 2.5% COLA (often matches inflation)
    discount_rate_real: float = 0.02  # 2% real discount rate for NPV
    marginal_tax_rate: float = 0.22  # 22% marginal tax rate
    ss_taxable_portion: float = 0.85  # 85% of SS is taxable (worst case)
    life_expectancy_override: Optional[int] = None  # Override life expectancy


@dataclass
class BenefitStream:
    """Time series of benefits"""
    ages: List[int]  # Ages (years)
    annual_benefits_gross: List[float]  # Gross annual benefits
    annual_benefits_net: List[float]  # After-tax annual benefits
    cumulative_gross: List[float]  # Cumulative gross benefits
    cumulative_net: List[float]  # Cumulative net benefits
    cumulative_invested: List[float]  # If invested at return rate


@dataclass
class ClaimingScenario:
    """Results for a single claiming age scenario"""
    claiming_age: float
    monthly_benefit_initial: float
    annual_benefit_initial: float
    benefit_stream: BenefitStream
    npv_gross: float
    npv_net: float
    break_even_age: Optional[float]  # vs baseline (typically age 67)
    cumulative_at_ages: Dict[int, float]  # Key ages: 75, 80, 85, 90


@dataclass
class CoupleScenario:
    """Results for couple with two claiming ages"""
    spouse_a_claiming_age: float
    spouse_b_claiming_age: float
    combined_benefit_stream: BenefitStream
    npv_household_gross: float
    npv_household_net: float
    survivor_benefit_value: float  # Expected value of survivor benefits
    household_break_even_age: Optional[float]


# =============================================================================
# CORE CALCULATION FUNCTIONS
# =============================================================================

def get_full_retirement_age(birth_year: int, birth_month: int) -> Tuple[int, int]:
    """
    Get Full Retirement Age (FRA) for given birth date.
    
    Args:
        birth_year: Year of birth
        birth_month: Month of birth (1-12)
        
    Returns:
        Tuple of (years, months) for FRA
        
    Example:
        >>> get_full_retirement_age(1960, 6)
        (67, 0)
    """
    if birth_year < 1937:
        return (65, 0)
    elif birth_year >= 1960:
        return (67, 0)
    else:
        return FRA_TABLE.get(birth_year, (67, 0))


def calculate_benefit_adjustment_factor(
    birth_year: int,
    birth_month: int,
    claiming_age_years: int,
    claiming_age_months: int = 0
) -> float:
    """
    Calculate benefit adjustment factor based on claiming age vs FRA.
    
    Reduction for early claiming:
    - First 36 months before FRA: 5/9 of 1% per month
    - Beyond 36 months: 5/12 of 1% per month
    
    Increase for delayed claiming:
    - After FRA up to age 70: 2/3 of 1% per month (8% per year)
    
    Args:
        birth_year: Year of birth
        birth_month: Month of birth
        claiming_age_years: Claiming age in years
        claiming_age_months: Additional months
        
    Returns:
        Adjustment factor (1.0 = 100% of FRA benefit)
        
    Example:
        >>> # Claim at 62 when FRA is 67 = 60 months early
        >>> calculate_benefit_adjustment_factor(1960, 1, 62, 0)
        0.70  # 30% reduction
    """
    fra_years, fra_months = get_full_retirement_age(birth_year, birth_month)
    
    # Convert to months
    fra_age_months = fra_years * 12 + fra_months
    claiming_age_total_months = claiming_age_years * 12 + claiming_age_months
    
    months_difference = claiming_age_total_months - fra_age_months
    
    if months_difference == 0:
        # Claiming at FRA
        return 1.0
    
    elif months_difference < 0:
        # Early claiming - reduction
        months_early = abs(months_difference)
        
        if months_early <= 36:
            # All months in first tier
            reduction = months_early * EARLY_REDUCTION_RATE_FIRST_36_MONTHS
        else:
            # First 36 months at first tier, rest at second tier
            reduction = (36 * EARLY_REDUCTION_RATE_FIRST_36_MONTHS +
                        (months_early - 36) * EARLY_REDUCTION_RATE_AFTER_36_MONTHS)
        
        return 1.0 - reduction
    
    else:
        # Delayed claiming - credits (up to age 70)
        months_delayed = min(months_difference, (70 - fra_years) * 12 - fra_months)
        credit = months_delayed * DELAYED_CREDIT_RATE
        
        return 1.0 + credit


def calculate_monthly_benefit(
    benefit_at_fra: float,
    birth_year: int,
    birth_month: int,
    claiming_age_years: int,
    claiming_age_months: int = 0
) -> float:
    """
    Calculate monthly benefit for given claiming age.
    
    Args:
        benefit_at_fra: Monthly benefit at Full Retirement Age
        birth_year: Year of birth
        birth_month: Month of birth
        claiming_age_years: Claiming age years
        claiming_age_months: Claiming age months
        
    Returns:
        Monthly benefit amount
    """
    adjustment_factor = calculate_benefit_adjustment_factor(
        birth_year, birth_month, claiming_age_years, claiming_age_months
    )
    
    return benefit_at_fra * adjustment_factor


def get_life_expectancy(
    current_age: int,
    gender: Gender,
    override: Optional[int] = None
) -> int:
    """
    Get life expectancy (age at death) for planning purposes.
    
    Args:
        current_age: Current age in years
        gender: Gender for actuarial tables
        override: Optional override for life expectancy
        
    Returns:
        Expected age at death (years)
    """
    if override:
        return override
    
    # Find closest age in table
    table_ages = sorted(LIFE_EXPECTANCY_TABLE.keys())
    closest_age = min(table_ages, key=lambda x: abs(x - current_age))
    
    remaining_years = LIFE_EXPECTANCY_TABLE[closest_age][gender]
    
    return current_age + int(remaining_years)


def apply_cola(
    initial_benefit: float,
    years_elapsed: int,
    cola_rate: float
) -> float:
    """
    Apply Cost of Living Adjustments (COLA) to benefit.
    
    Args:
        initial_benefit: Initial annual benefit
        years_elapsed: Years since claiming
        cola_rate: Annual COLA rate (e.g., 0.025 for 2.5%)
        
    Returns:
        Benefit after COLA adjustments
    """
    return initial_benefit * ((1 + cola_rate) ** years_elapsed)


def calculate_after_tax_benefit(
    gross_benefit: float,
    marginal_tax_rate: float,
    taxable_portion: float = 0.85
) -> float:
    """
    Calculate after-tax Social Security benefit.
    
    Args:
        gross_benefit: Gross annual benefit
        marginal_tax_rate: Marginal tax rate
        taxable_portion: Portion of SS that's taxable (0.0 to 0.85)
        
    Returns:
        After-tax benefit
    """
    taxable_amount = gross_benefit * taxable_portion
    tax = taxable_amount * marginal_tax_rate
    
    return gross_benefit - tax


def calculate_benefit_stream(
    profile: PersonProfile,
    assumptions: AnalysisAssumptions,
    end_age: Optional[int] = None
) -> BenefitStream:
    """
    Calculate complete benefit stream from claiming age to life expectancy.
    
    Args:
        profile: Person profile with claiming age
        assumptions: Economic assumptions
        end_age: Optional override for ending age
        
    Returns:
        BenefitStream with annual values
    """
    # Calculate initial monthly benefit
    monthly_benefit = calculate_monthly_benefit(
        profile.benefit_at_fra,
        profile.birth_year,
        profile.birth_month,
        profile.claiming_age_years,
        profile.claiming_age_months
    )
    
    annual_benefit_initial = monthly_benefit * 12
    
    # Determine life expectancy
    claiming_age = profile.claiming_age_years
    if end_age is None:
        end_age = get_life_expectancy(
            claiming_age,
            profile.gender,
            assumptions.life_expectancy_override
        )
    
    # Build benefit stream
    ages = list(range(claiming_age, end_age + 1))
    years_elapsed = [age - claiming_age for age in ages]
    
    # Gross benefits with COLA
    annual_benefits_gross = [
        apply_cola(annual_benefit_initial, years, assumptions.cola_annual)
        for years in years_elapsed
    ]
    
    # After-tax benefits
    annual_benefits_net = [
        calculate_after_tax_benefit(
            gross,
            assumptions.marginal_tax_rate,
            assumptions.ss_taxable_portion
        )
        for gross in annual_benefits_gross
    ]
    
    # Cumulative benefits
    cumulative_gross = np.cumsum(annual_benefits_gross).tolist()
    cumulative_net = np.cumsum(annual_benefits_net).tolist()
    
    # Cumulative with investment (for early claiming analysis)
    cumulative_invested = []
    invested_value = 0.0
    for i, net_benefit in enumerate(annual_benefits_net):
        # Add benefit and grow existing balance
        invested_value = invested_value * (1 + assumptions.investment_return_annual) + net_benefit
        cumulative_invested.append(invested_value)
    
    return BenefitStream(
        ages=ages,
        annual_benefits_gross=annual_benefits_gross,
        annual_benefits_net=annual_benefits_net,
        cumulative_gross=cumulative_gross,
        cumulative_net=cumulative_net,
        cumulative_invested=cumulative_invested
    )


def calculate_npv(
    benefit_stream: BenefitStream,
    discount_rate: float,
    use_net: bool = True
) -> float:
    """
    Calculate Net Present Value (NPV) of benefit stream.
    
    Args:
        benefit_stream: Stream of benefits over time
        discount_rate: Real discount rate for NPV
        use_net: Use after-tax benefits (True) or gross (False)
        
    Returns:
        NPV of benefit stream
    """
    benefits = (benefit_stream.annual_benefits_net if use_net 
                else benefit_stream.annual_benefits_gross)
    
    # Discount each year's benefit
    discount_factors = [(1 + discount_rate) ** (-i) 
                        for i in range(len(benefits))]
    
    npv = sum(benefit * factor 
              for benefit, factor in zip(benefits, discount_factors))
    
    return npv


def calculate_break_even_age(
    stream_a: BenefitStream,
    stream_b: BenefitStream
) -> Optional[float]:
    """
    Calculate break-even age where cumulative benefits are equal.
    
    Args:
        stream_a: First benefit stream (e.g., claim at 62)
        stream_b: Second benefit stream (e.g., claim at 67)
        
    Returns:
        Break-even age, or None if streams don't intersect
    """
    # Use net cumulative benefits
    cum_a = stream_a.cumulative_net
    cum_b = stream_b.cumulative_net
    
    # Find intersection
    # Start from when both streams are active
    start_age = max(stream_a.ages[0], stream_b.ages[0])
    
    for i, age in enumerate(stream_a.ages):
        if age < start_age:
            continue
        
        # Find corresponding index in stream_b
        if age not in stream_b.ages:
            continue
        
        j = stream_b.ages.index(age)
        
        # Check if cumulative benefits have crossed
        if i > 0 and j > 0:
            # Previous age
            prev_diff = cum_a[i-1] - cum_b[j-1]
            curr_diff = cum_a[i] - cum_b[j]
            
            # If signs differ, we've crossed
            if prev_diff * curr_diff < 0:
                # Linear interpolation for more precise break-even
                # Assume linear between years
                fraction = abs(prev_diff) / (abs(prev_diff) + abs(curr_diff))
                return stream_a.ages[i-1] + fraction
    
    return None


def analyze_individual_scenario(
    profile: PersonProfile,
    assumptions: AnalysisAssumptions,
    baseline_claiming_age: int = 67
) -> ClaimingScenario:
    """
    Analyze a single claiming age scenario for an individual.
    
    Args:
        profile: Person profile with claiming age
        assumptions: Economic assumptions
        baseline_claiming_age: Baseline age for break-even comparison
        
    Returns:
        Complete scenario analysis
    """
    # Calculate benefit stream
    benefit_stream = calculate_benefit_stream(profile, assumptions)
    
    # Initial benefits
    monthly_benefit = calculate_monthly_benefit(
        profile.benefit_at_fra,
        profile.birth_year,
        profile.birth_month,
        profile.claiming_age_years,
        profile.claiming_age_months
    )
    annual_benefit = monthly_benefit * 12
    
    # NPV calculations
    npv_gross = calculate_npv(benefit_stream, assumptions.discount_rate_real, use_net=False)
    npv_net = calculate_npv(benefit_stream, assumptions.discount_rate_real, use_net=True)
    
    # Break-even vs baseline
    break_even_age = None
    if profile.claiming_age_years != baseline_claiming_age:
        baseline_profile = PersonProfile(
            birth_year=profile.birth_year,
            birth_month=profile.birth_month,
            gender=profile.gender,
            benefit_at_fra=profile.benefit_at_fra,
            claiming_age_years=baseline_claiming_age,
            claiming_age_months=0
        )
        baseline_stream = calculate_benefit_stream(baseline_profile, assumptions)
        break_even_age = calculate_break_even_age(benefit_stream, baseline_stream)
    
    # Cumulative at key ages
    cumulative_at_ages = {}
    for target_age in [75, 80, 85, 90]:
        if target_age in benefit_stream.ages:
            idx = benefit_stream.ages.index(target_age)
            cumulative_at_ages[target_age] = benefit_stream.cumulative_net[idx]
    
    return ClaimingScenario(
        claiming_age=profile.claiming_age_decimal(),
        monthly_benefit_initial=monthly_benefit,
        annual_benefit_initial=annual_benefit,
        benefit_stream=benefit_stream,
        npv_gross=npv_gross,
        npv_net=npv_net,
        break_even_age=break_even_age,
        cumulative_at_ages=cumulative_at_ages
    )


def analyze_couple_scenario(
    spouse_a: PersonProfile,
    spouse_b: PersonProfile,
    assumptions: AnalysisAssumptions
) -> CoupleScenario:
    """
    Analyze couple scenario with two claiming ages.
    
    Includes:
    - Combined household benefits
    - Survivor benefit calculations
    - Household NPV
    
    Args:
        spouse_a: First spouse profile
        spouse_b: Second spouse profile
        assumptions: Economic assumptions
        
    Returns:
        Couple scenario analysis
    """
    # Calculate individual streams
    stream_a = calculate_benefit_stream(spouse_a, assumptions)
    stream_b = calculate_benefit_stream(spouse_b, assumptions)
    
    # Determine overall age range
    start_age = max(stream_a.ages[0], stream_b.ages[0])
    end_age = max(stream_a.ages[-1], stream_b.ages[-1])
    
    # Build combined benefit stream
    ages = list(range(start_age, end_age + 1))
    annual_gross = []
    annual_net = []
    
    for age in ages:
        gross = 0.0
        net = 0.0
        
        # Add spouse A benefit if alive and claiming
        if age >= stream_a.ages[0] and age <= stream_a.ages[-1]:
            idx_a = age - stream_a.ages[0]
            gross += stream_a.annual_benefits_gross[idx_a]
            net += stream_a.annual_benefits_net[idx_a]
        
        # Add spouse B benefit if alive and claiming
        if age >= stream_b.ages[0] and age <= stream_b.ages[-1]:
            idx_b = age - stream_b.ages[0]
            gross += stream_b.annual_benefits_gross[idx_b]
            net += stream_b.annual_benefits_net[idx_b]
        
        annual_gross.append(gross)
        annual_net.append(net)
    
    cumulative_gross = np.cumsum(annual_gross).tolist()
    cumulative_net = np.cumsum(annual_net).tolist()
    
    # Investment growth of combined benefits
    cumulative_invested = []
    invested = 0.0
    for net in annual_net:
        invested = invested * (1 + assumptions.investment_return_annual) + net
        cumulative_invested.append(invested)
    
    combined_stream = BenefitStream(
        ages=ages,
        annual_benefits_gross=annual_gross,
        annual_benefits_net=annual_net,
        cumulative_gross=cumulative_gross,
        cumulative_net=cumulative_net,
        cumulative_invested=cumulative_invested
    )
    
    # NPV of household benefits
    npv_gross = calculate_npv(combined_stream, assumptions.discount_rate_real, use_net=False)
    npv_net = calculate_npv(combined_stream, assumptions.discount_rate_real, use_net=True)
    
    # Estimate survivor benefit value
    # Simplified: higher benefit continues after first spouse dies
    monthly_a = calculate_monthly_benefit(
        spouse_a.benefit_at_fra, spouse_a.birth_year, spouse_a.birth_month,
        spouse_a.claiming_age_years, spouse_a.claiming_age_months
    )
    monthly_b = calculate_monthly_benefit(
        spouse_b.benefit_at_fra, spouse_b.birth_year, spouse_b.birth_month,
        spouse_b.claiming_age_years, spouse_b.claiming_age_months
    )
    
    survivor_benefit = max(monthly_a, monthly_b) * 12
    survivor_years = abs(stream_a.ages[-1] - stream_b.ages[-1])
    survivor_benefit_value = survivor_benefit * survivor_years
    
    return CoupleScenario(
        spouse_a_claiming_age=spouse_a.claiming_age_decimal(),
        spouse_b_claiming_age=spouse_b.claiming_age_decimal(),
        combined_benefit_stream=combined_stream,
        npv_household_gross=npv_gross,
        npv_household_net=npv_net,
        survivor_benefit_value=survivor_benefit_value,
        household_break_even_age=None  # Can be calculated vs baseline
    )


def find_optimal_claiming_ages(
    profile: PersonProfile,
    assumptions: AnalysisAssumptions,
    age_range: List[int] = None
) -> List[ClaimingScenario]:
    """
    Analyze multiple claiming ages and rank by NPV.
    
    Args:
        profile: Person profile (claiming age will be varied)
        assumptions: Economic assumptions
        age_range: List of ages to test (default: 62-70)
        
    Returns:
        List of scenarios sorted by NPV (highest first)
    """
    if age_range is None:
        age_range = list(range(62, 71))  # 62 through 70
    
    scenarios = []
    
    for age in age_range:
        test_profile = PersonProfile(
            birth_year=profile.birth_year,
            birth_month=profile.birth_month,
            gender=profile.gender,
            benefit_at_fra=profile.benefit_at_fra,
            claiming_age_years=age,
            claiming_age_months=0
        )
        
        scenario = analyze_individual_scenario(test_profile, assumptions)
        scenarios.append(scenario)
    
    # Sort by NPV (net, descending)
    scenarios.sort(key=lambda s: s.npv_net, reverse=True)
    
    return scenarios


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def format_currency(amount: float) -> str:
    """Format amount as currency"""
    return f"${amount:,.0f}"


def format_age(age: float) -> str:
    """Format age with months if not whole number"""
    years = int(age)
    months = int((age - years) * 12)
    
    if months == 0:
        return f"{years}"
    else:
        return f"{years} years, {months} months"
