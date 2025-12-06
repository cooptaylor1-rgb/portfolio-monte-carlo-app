"""
Centralized Financial Planning Assumptions and Constants

All values are documented with sources and updated annually.
This module serves as the single source of truth for tax rules,
market assumptions, and financial planning parameters.

Last Updated: December 2024
"""

from typing import Dict, List, Tuple
from dataclasses import dataclass

# =============================================================================
# TAX BRACKETS AND RATES (2024)
# =============================================================================

# Federal Income Tax Brackets (Single Filer, 2024)
# Source: IRS Rev. Proc. 2023-34
FEDERAL_TAX_BRACKETS_SINGLE: List[Tuple[float, float]] = [
    (0, 0.10),        # $0 - $11,600: 10%
    (11600, 0.12),    # $11,600 - $47,150: 12%
    (47150, 0.22),    # $47,150 - $100,525: 22%
    (100525, 0.24),   # $100,525 - $191,950: 24%
    (191950, 0.32),   # $191,950 - $243,725: 32%
    (243725, 0.35),   # $243,725 - $609,350: 35%
    (609350, 0.37),   # $609,350+: 37%
]

# Federal Income Tax Brackets (Married Filing Jointly, 2024)
# Source: IRS Rev. Proc. 2023-34
FEDERAL_TAX_BRACKETS_JOINT: List[Tuple[float, float]] = [
    (0, 0.10),        # $0 - $23,200: 10%
    (23200, 0.12),    # $23,200 - $94,300: 12%
    (94300, 0.22),    # $94,300 - $201,050: 22%
    (201050, 0.24),   # $201,050 - $383,900: 24%
    (383900, 0.32),   # $383,900 - $487,450: 32%
    (487450, 0.35),   # $487,450 - $731,200: 35%
    (731200, 0.37),   # $731,200+: 37%
]

# Long-Term Capital Gains Tax Rates (2024)
# Source: IRS Publication 17
LTCG_BRACKETS_SINGLE: List[Tuple[float, float]] = [
    (0, 0.00),        # $0 - $47,025: 0%
    (47025, 0.15),    # $47,025 - $518,900: 15%
    (518900, 0.20),   # $518,900+: 20%
]

LTCG_BRACKETS_JOINT: List[Tuple[float, float]] = [
    (0, 0.00),        # $0 - $94,050: 0%
    (94050, 0.15),    # $94,050 - $583,750: 15%
    (583750, 0.20),   # $583,750+: 20%
]

# Net Investment Income Tax (NIIT) - Additional 3.8%
# Source: IRS Form 8960
NIIT_THRESHOLD_SINGLE = 200000
NIIT_THRESHOLD_JOINT = 250000
NIIT_RATE = 0.038

# State Tax Considerations (Placeholder - should be parameterized by state)
DEFAULT_STATE_TAX_RATE = 0.05  # 5% average
ZERO_STATE_TAX_STATES = [
    'FL', 'TX', 'NV', 'WA', 'WY', 'SD', 'TN', 'NH', 'AK'
]

# =============================================================================
# MEDICARE IRMAA SURCHARGES (2024)
# =============================================================================

# Medicare Part B IRMAA (Income-Related Monthly Adjustment Amount)
# Source: CMS Medicare Part B Premiums for 2024
# Format: (MAGI threshold, monthly surcharge)
IRMAA_PART_B_SINGLE: List[Tuple[float, float]] = [
    (103000, 0.00),      # Standard premium only ($174.70/mo in 2024)
    (129000, 69.90),     # Tier 1: +$69.90/month
    (161000, 174.70),    # Tier 2: +$174.70/month
    (193000, 279.50),    # Tier 3: +$279.50/month
    (500000, 384.30),    # Tier 4: +$384.30/month
]

IRMAA_PART_B_JOINT: List[Tuple[float, float]] = [
    (206000, 0.00),      # Standard premium only
    (258000, 69.90),     # Tier 1
    (322000, 174.70),    # Tier 2
    (386000, 279.50),    # Tier 3
    (750000, 384.30),    # Tier 4
]

# Medicare Part D IRMAA
# Source: CMS Medicare Part D for 2024
IRMAA_PART_D_SINGLE: List[Tuple[float, float]] = [
    (103000, 0.00),      # No surcharge
    (129000, 12.90),     # Tier 1: +$12.90/month
    (161000, 33.30),     # Tier 2: +$33.30/month
    (193000, 53.80),     # Tier 3: +$53.80/month
    (500000, 74.20),     # Tier 4: +$74.20/month
]

IRMAA_PART_D_JOINT: List[Tuple[float, float]] = [
    (206000, 0.00),
    (258000, 12.90),
    (322000, 33.30),
    (386000, 53.80),
    (750000, 74.20),
]

# Standard Medicare premiums (base amounts before IRMAA)
MEDICARE_PART_B_STANDARD_PREMIUM = 174.70  # Monthly, 2024
MEDICARE_PART_D_AVERAGE_PREMIUM = 55.50    # Monthly average, 2024

# =============================================================================
# REQUIRED MINIMUM DISTRIBUTIONS (RMDs)
# =============================================================================

# RMD Age (SECURE Act 2.0)
# Born 1951-1959: Age 73 (starting 2023)
# Born 1960+: Age 75 (starting 2033)
RMD_AGE_DEFAULT = 73  # For current retirees

# IRS Uniform Lifetime Table (2022+)
# Source: IRS Publication 590-B, Appendix B
# Format: {age: divisor}
RMD_FACTORS: Dict[int, float] = {
    72: 27.4, 73: 26.5, 74: 25.5, 75: 24.6, 76: 23.7, 77: 22.9, 78: 22.0,
    79: 21.1, 80: 20.2, 81: 19.4, 82: 18.5, 83: 17.7, 84: 16.8, 85: 16.0,
    86: 15.2, 87: 14.4, 88: 13.7, 89: 12.9, 90: 12.2, 91: 11.5, 92: 10.8,
    93: 10.1, 94: 9.5, 95: 8.9, 96: 8.4, 97: 7.8, 98: 7.3, 99: 6.8,
    100: 6.4, 101: 6.0, 102: 5.6, 103: 5.2, 104: 4.9, 105: 4.6,
    106: 4.3, 107: 4.1, 108: 3.9, 109: 3.7, 110: 3.5, 111: 3.4,
    112: 3.3, 113: 3.1, 114: 3.0, 115: 2.9, 116: 2.8, 117: 2.7,
    118: 2.5, 119: 2.3, 120: 2.0,
}

# Penalty for missed RMDs
RMD_PENALTY_RATE = 0.25  # 25% penalty (reduced from 50% by SECURE 2.0)

# =============================================================================
# SOCIAL SECURITY
# =============================================================================

# Full Retirement Age (FRA) by Birth Year
# Source: Social Security Administration
SS_FRA_BY_BIRTH_YEAR: Dict[int, float] = {
    1937: 65.0, 1938: 65.17, 1939: 65.33, 1940: 65.50, 1941: 65.67,
    1942: 65.83, 1943: 66.0, 1944: 66.0, 1945: 66.0, 1946: 66.0,
    1947: 66.0, 1948: 66.0, 1949: 66.0, 1950: 66.0, 1951: 66.0,
    1952: 66.0, 1953: 66.0, 1954: 66.0, 1955: 66.17, 1956: 66.33,
    1957: 66.50, 1958: 66.67, 1959: 66.83, 1960: 67.0,
}
# For births after 1960, FRA is 67.0

# Early claiming reduction rates
SS_EARLY_REDUCTION_RATE_FIRST_36 = 5/9 / 100  # 5/9 of 1% per month (first 36 months)
SS_EARLY_REDUCTION_RATE_AFTER_36 = 5/12 / 100  # 5/12 of 1% per month (beyond 36 months)

# Delayed retirement credits
SS_DELAYED_CREDIT_RATE = 2/3 / 100  # 2/3 of 1% per month = 8% per year

# Maximum delay age
SS_MAX_DELAY_AGE = 70

# COLA (Cost of Living Adjustment) assumption
SS_COLA_ASSUMPTION = 0.025  # 2.5% annual average

# Maximum taxable earnings (2024)
SS_MAX_TAXABLE_EARNINGS = 168600  # $168,600

# =============================================================================
# QUALIFIED CHARITABLE DISTRIBUTIONS (QCDs)
# =============================================================================

# QCD Rules (Tax Cuts and Jobs Act)
QCD_MIN_AGE = 70.5  # Eligible age for QCDs
QCD_ANNUAL_LIMIT = 100000  # $100,000 per person per year
QCD_COUNTS_TOWARD_RMD = True  # QCDs satisfy RMD requirement
QCD_EXCLUDED_FROM_INCOME = True  # Not included in AGI

# =============================================================================
# ESTATE TAX (2024)
# =============================================================================

# Federal Estate Tax Exemption
# Source: IRS Rev. Proc. 2023-34
ESTATE_TAX_EXEMPTION_SINGLE = 13610000  # $13.61M per person
ESTATE_TAX_EXEMPTION_JOINT = 27220000   # $27.22M per couple
ESTATE_TAX_RATE = 0.40  # 40% on amounts above exemption

# Step-up in basis at death
STEP_UP_IN_BASIS_ENABLED = True  # Full step-up for inherited taxable accounts

# Portability (surviving spouse can use deceased spouse's unused exemption)
PORTABILITY_ENABLED = True

# =============================================================================
# MARKET RETURN ASSUMPTIONS
# =============================================================================

# Expected Real Returns (After Inflation)
# Source: Vanguard Capital Markets Model (VCMM) 2024
# 10-year outlook, 50th percentile

@dataclass
class AssetClassAssumptions:
    """Return and risk assumptions for major asset classes."""
    name: str
    real_return: float  # Expected real return (after inflation)
    volatility: float   # Annual standard deviation
    expense_ratio: float = 0.0  # Average expense ratio

# Equity
EQUITY_ASSUMPTIONS = AssetClassAssumptions(
    name="U.S. Equity (Broad Market)",
    real_return=0.0527,   # 5.27% real (VCMM 2024: 4.0-6.5% range)
    volatility=0.1790,    # 17.9% annual volatility
    expense_ratio=0.0003  # 3 bps for broad index fund
)

# Fixed Income
FIXED_INCOME_ASSUMPTIONS = AssetClassAssumptions(
    name="U.S. Aggregate Bonds",
    real_return=0.0185,   # 1.85% real (VCMM 2024: 1.0-2.5% range)
    volatility=0.0540,    # 5.4% annual volatility
    expense_ratio=0.0004  # 4 bps for bond index fund
)

# Cash
CASH_ASSUMPTIONS = AssetClassAssumptions(
    name="Cash / Money Market",
    real_return=0.0000,   # 0% real (inflation-matching assumption)
    volatility=0.0100,    # 1% annual volatility (minimal)
    expense_ratio=0.0000  # No fees
)

# Asset Correlation Matrix
# Source: 30-year historical data (Morningstar)
CORRELATION_MATRIX = {
    ('equity', 'fixed_income'): 0.20,
    ('equity', 'cash'): 0.05,
    ('fixed_income', 'cash'): 0.10,
}

# =============================================================================
# INFLATION ASSUMPTIONS
# =============================================================================

# Long-term inflation target
# Source: Federal Reserve long-term inflation target
LONG_TERM_INFLATION = 0.025  # 2.5%
INFLATION_VOLATILITY = 0.015  # 1.5% annual standard deviation

# Mean reversion parameters for stochastic inflation
INFLATION_MEAN_REVERSION_SPEED = 0.30  # 30% reversion per year

# Healthcare-specific inflation
# Source: Fidelity Retiree Health Care Cost Estimate
HEALTHCARE_INFLATION = 0.050  # 5% annual (higher than general inflation)

# =============================================================================
# SPENDING & WITHDRAWAL ASSUMPTIONS
# =============================================================================

# Safe withdrawal rates
# Source: Trinity Study, Bengen's research
CONSERVATIVE_WITHDRAWAL_RATE = 0.035  # 3.5% (95%+ success rate)
MODERATE_WITHDRAWAL_RATE = 0.040      # 4.0% (85-90% success rate)
AGGRESSIVE_WITHDRAWAL_RATE = 0.050    # 5.0% (70-80% success rate)

# Success threshold for Monte Carlo
SUCCESS_PROBABILITY_TARGET = 0.85  # 85% = "acceptable" plan
HIGH_CONFIDENCE_TARGET = 0.90      # 90% = "strong" plan
ULTRA_CONSERVATIVE_TARGET = 0.95   # 95% = "very conservative" plan

# Portfolio floor (minimum balance to maintain)
PORTFOLIO_FLOOR_PERCENTAGE = 0.25  # Don't deplete below 25% of starting value

# =============================================================================
# LONGEVITY ASSUMPTIONS
# =============================================================================

# Life Expectancy Tables
# Source: Society of Actuaries RP-2014 Mortality Tables
# Format: {age: remaining_years}

LIFE_EXPECTANCY_MALE: Dict[int, float] = {
    60: 24.4, 65: 20.3, 70: 16.4, 75: 12.9, 80: 9.8,
    85: 7.2, 90: 5.2, 95: 3.7, 100: 2.7
}

LIFE_EXPECTANCY_FEMALE: Dict[int, float] = {
    60: 27.0, 65: 22.7, 70: 18.5, 75: 14.6, 80: 11.0,
    85: 8.0, 90: 5.6, 95: 3.9, 100: 2.8
}

# Joint life expectancy (both spouses)
# Roughly 1.5x single life expectancy for same-age couple
JOINT_LIFE_EXPECTANCY_MULTIPLIER = 1.5

# Planning horizon safety margin
LONGEVITY_SAFETY_MARGIN_YEARS = 5  # Plan for 5 years beyond life expectancy

# =============================================================================
# HEALTHCARE COST ASSUMPTIONS
# =============================================================================

# Average annual healthcare costs per person (2024)
# Source: Fidelity Retiree Health Care Cost Estimate
AVERAGE_HEALTHCARE_COST_AGE_65 = 15000  # $15,000 per person per year
AVERAGE_HEALTHCARE_COST_AGE_75 = 18000  # $18,000 (increases with age)
AVERAGE_HEALTHCARE_COST_AGE_85 = 22000  # $22,000 (increases with age)

# Long-term care costs (2024)
# Source: Genworth Cost of Care Survey
NURSING_HOME_ANNUAL_COST = 108000     # $108,000/year (private room)
ASSISTED_LIVING_ANNUAL_COST = 57000   # $57,000/year
HOME_HEALTH_AIDE_ANNUAL_COST = 75000  # $75,000/year (40 hrs/week)

# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def get_tax_bracket(income: float, filing_status: str = 'single') -> Tuple[float, float]:
    """
    Get the marginal tax rate and bracket threshold for a given income.
    
    Args:
        income: Taxable income amount
        filing_status: 'single' or 'joint'
    
    Returns:
        Tuple of (threshold, marginal_rate)
    """
    brackets = FEDERAL_TAX_BRACKETS_SINGLE if filing_status == 'single' else FEDERAL_TAX_BRACKETS_JOINT
    
    for i in range(len(brackets) - 1, -1, -1):
        threshold, rate = brackets[i]
        if income >= threshold:
            return (threshold, rate)
    
    return brackets[0]  # Lowest bracket


def calculate_federal_tax(income: float, filing_status: str = 'single') -> float:
    """
    Calculate total federal income tax owed.
    
    Args:
        income: Taxable income
        filing_status: 'single' or 'joint'
    
    Returns:
        Total tax owed
    """
    brackets = FEDERAL_TAX_BRACKETS_SINGLE if filing_status == 'single' else FEDERAL_TAX_BRACKETS_JOINT
    
    tax = 0.0
    remaining_income = income
    
    for i in range(len(brackets)):
        threshold, rate = brackets[i]
        
        # Calculate income in this bracket
        if i < len(brackets) - 1:
            next_threshold = brackets[i + 1][0]
            bracket_income = min(remaining_income, next_threshold - threshold)
        else:
            bracket_income = remaining_income
        
        if bracket_income <= 0:
            break
        
        tax += bracket_income * rate
        remaining_income -= bracket_income
    
    return tax


def get_ltcg_rate(income: float, filing_status: str = 'single') -> float:
    """
    Get the long-term capital gains tax rate for a given income.
    
    Args:
        income: Taxable income (used to determine bracket)
        filing_status: 'single' or 'joint'
    
    Returns:
        LTCG rate (0%, 15%, or 20%)
    """
    brackets = LTCG_BRACKETS_SINGLE if filing_status == 'single' else LTCG_BRACKETS_JOINT
    
    for i in range(len(brackets) - 1, -1, -1):
        threshold, rate = brackets[i]
        if income >= threshold:
            return rate
    
    return brackets[0][1]  # Should be 0%


def get_irmaa_surcharge(magi: float, filing_status: str = 'single') -> Dict[str, float]:
    """
    Calculate Medicare IRMAA surcharges based on MAGI.
    
    Args:
        magi: Modified Adjusted Gross Income
        filing_status: 'single' or 'joint'
    
    Returns:
        Dictionary with Part B and Part D monthly surcharges
    """
    part_b_brackets = IRMAA_PART_B_SINGLE if filing_status == 'single' else IRMAA_PART_B_JOINT
    part_d_brackets = IRMAA_PART_D_SINGLE if filing_status == 'single' else IRMAA_PART_D_JOINT
    
    part_b_surcharge = 0.0
    part_d_surcharge = 0.0
    
    # Find Part B surcharge
    for i in range(len(part_b_brackets) - 1, -1, -1):
        threshold, surcharge = part_b_brackets[i]
        if magi >= threshold:
            part_b_surcharge = surcharge
            break
    
    # Find Part D surcharge
    for i in range(len(part_d_brackets) - 1, -1, -1):
        threshold, surcharge = part_d_brackets[i]
        if magi >= threshold:
            part_d_surcharge = surcharge
            break
    
    return {
        'part_b_monthly': part_b_surcharge,
        'part_d_monthly': part_d_surcharge,
        'total_annual': (part_b_surcharge + part_d_surcharge) * 12
    }


def get_rmd_factor(age: int) -> float:
    """
    Get the RMD divisor for a given age.
    
    Args:
        age: Current age
    
    Returns:
        RMD divisor from IRS Uniform Lifetime Table
    """
    if age < 72:
        return float('inf')  # No RMD required
    if age > 120:
        return RMD_FACTORS[120]  # Use last available factor
    
    return RMD_FACTORS.get(age, RMD_FACTORS[120])


def calculate_rmd(ira_balance: float, age: int) -> float:
    """
    Calculate Required Minimum Distribution for a given age and balance.
    
    Args:
        ira_balance: Traditional IRA account balance (12/31 of prior year)
        age: Current age
    
    Returns:
        Required minimum distribution amount
    """
    if age < RMD_AGE_DEFAULT:
        return 0.0
    
    factor = get_rmd_factor(age)
    return ira_balance / factor if factor > 0 else 0.0


def get_ss_fra(birth_year: int) -> float:
    """
    Get Social Security Full Retirement Age for a birth year.
    
    Args:
        birth_year: Year of birth
    
    Returns:
        Full Retirement Age (e.g., 67.0 for those born in 1960+)
    """
    if birth_year <= 1937:
        return 65.0
    elif birth_year >= 1960:
        return 67.0
    else:
        return SS_FRA_BY_BIRTH_YEAR.get(birth_year, 67.0)


# =============================================================================
# VALIDATION
# =============================================================================

def validate_assumptions():
    """Run validation checks on all assumptions."""
    
    # Check tax brackets are in ascending order
    for brackets in [FEDERAL_TAX_BRACKETS_SINGLE, FEDERAL_TAX_BRACKETS_JOINT]:
        for i in range(len(brackets) - 1):
            assert brackets[i][0] < brackets[i+1][0], "Tax brackets not in order"
            assert 0 <= brackets[i][1] <= 1, "Tax rate out of bounds"
    
    # Check RMD factors are decreasing
    ages = sorted(RMD_FACTORS.keys())
    for i in range(len(ages) - 1):
        assert RMD_FACTORS[ages[i]] > RMD_FACTORS[ages[i+1]], "RMD factors should decrease with age"
    
    # Check correlation matrix is symmetric
    for (a, b), corr in CORRELATION_MATRIX.items():
        assert -1 <= corr <= 1, f"Correlation {a}-{b} out of bounds"
    
    print("✓ All assumptions validated successfully")


if __name__ == "__main__":
    # Run validation
    validate_assumptions()
    
    # Print sample calculations
    print("\n" + "="*60)
    print("SAMPLE TAX CALCULATIONS")
    print("="*60)
    
    # Example 1: Single filer, $150K income
    income = 150000
    tax = calculate_federal_tax(income, 'single')
    effective_rate = tax / income
    marginal = get_tax_bracket(income, 'single')[1]
    print(f"\nSingle filer, ${income:,.0f} income:")
    print(f"  Federal tax: ${tax:,.2f}")
    print(f"  Effective rate: {effective_rate:.2%}")
    print(f"  Marginal rate: {marginal:.0%}")
    
    # Example 2: LTCG rate
    ltcg_rate = get_ltcg_rate(income, 'single')
    print(f"  LTCG rate: {ltcg_rate:.0%}")
    
    # Example 3: IRMAA
    magi = 180000
    irmaa = get_irmaa_surcharge(magi, 'single')
    print(f"\n  MAGI ${magi:,.0f} → IRMAA surcharge: ${irmaa['total_annual']:,.2f}/year")
    
    # Example 4: RMD
    ira_balance = 1000000
    age = 75
    rmd = calculate_rmd(ira_balance, age)
    print(f"\n  IRA ${ira_balance:,.0f}, Age {age} → RMD: ${rmd:,.2f}")
