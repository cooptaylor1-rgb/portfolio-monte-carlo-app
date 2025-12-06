"""
Tax-Efficient Withdrawal Sequencing and Roth Conversion Optimization

This module implements sophisticated tax minimization strategies:
1. Optimal withdrawal sequencing across account types
2. Roth conversion optimization
3. Tax projection and lifetime tax calculation
4. IRMAA threshold management

Author: Salem Investment Counselors
Last Updated: December 2024
"""

from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import numpy as np

try:
    # Try absolute import (for API usage)
    from backend.core.assumptions import (
        FEDERAL_TAX_BRACKETS_SINGLE,
        FEDERAL_TAX_BRACKETS_JOINT,
        LTCG_BRACKETS_SINGLE,
        LTCG_BRACKETS_JOINT,
        IRMAA_PART_B_SINGLE,
        IRMAA_PART_B_JOINT,
        calculate_federal_tax,
        get_ltcg_rate,
        get_irmaa_surcharge,
        calculate_rmd,
        RMD_AGE_DEFAULT,
    )
except ImportError:
    # Fall back to relative import (for testing)
    try:
        from assumptions import (
            FEDERAL_TAX_BRACKETS_SINGLE,
            FEDERAL_TAX_BRACKETS_JOINT,
            LTCG_BRACKETS_SINGLE,
            LTCG_BRACKETS_JOINT,
            IRMAA_PART_B_SINGLE,
            IRMAA_PART_B_JOINT,
            calculate_federal_tax,
            get_ltcg_rate,
            get_irmaa_surcharge,
            calculate_rmd,
            RMD_AGE_DEFAULT,
        )
    except ImportError:
        # Try relative import from core
        from core.assumptions import (
            FEDERAL_TAX_BRACKETS_SINGLE,
            FEDERAL_TAX_BRACKETS_JOINT,
            LTCG_BRACKETS_SINGLE,
            LTCG_BRACKETS_JOINT,
            IRMAA_PART_B_SINGLE,
            IRMAA_PART_B_JOINT,
            calculate_federal_tax,
            get_ltcg_rate,
            get_irmaa_surcharge,
            calculate_rmd,
            RMD_AGE_DEFAULT,
        )


@dataclass
class AccountBalances:
    """Current balances across account types."""
    taxable: float
    traditional_ira: float
    roth_ira: float
    taxable_basis: float = 0.0  # Cost basis in taxable account


@dataclass
class WithdrawalResult:
    """Result of withdrawal sequencing optimization."""
    taxable_withdrawal: float
    ira_withdrawal: float
    roth_withdrawal: float
    total_withdrawn: float
    federal_tax: float
    ltcg_tax: float
    irmaa_surcharge: float
    effective_tax_rate: float
    marginal_rate: float


@dataclass
class RothConversionSchedule:
    """Optimal Roth conversion plan over multiple years."""
    years: List[int]  # Year indices
    ages: List[int]  # Client age each year
    conversion_amounts: List[float]  # Amount to convert each year
    projected_taxes: List[float]  # Tax on each conversion
    cumulative_savings: List[float]  # Cumulative tax savings vs no conversion
    total_conversions: float
    total_taxes_on_conversions: float
    lifetime_tax_savings: float  # PV of tax savings


class TaxOptimizer:
    """
    Tax optimization engine for retirement planning.
    
    Key strategies:
    1. Withdrawal sequencing: RMDs → Taxable → IRA → Roth
    2. Roth conversions in low-income years
    3. IRMAA threshold management
    4. Tax bracket awareness
    """
    
    def __init__(
        self,
        filing_status: str = 'single',
        state_tax_rate: float = 0.0,
        current_age: int = 65,
        birth_year: int = 1959,
    ):
        """
        Initialize tax optimizer.
        
        Args:
            filing_status: 'single' or 'joint'
            state_tax_rate: State income tax rate (0.0 for no state tax)
            current_age: Client's current age
            birth_year: Client's birth year (for RMD age determination)
        """
        self.filing_status = filing_status
        self.state_tax_rate = state_tax_rate
        self.current_age = current_age
        self.birth_year = birth_year
        
        # Set appropriate brackets
        if filing_status == 'single':
            self.income_brackets = FEDERAL_TAX_BRACKETS_SINGLE
            self.ltcg_brackets = LTCG_BRACKETS_SINGLE
            self.irmaa_brackets = IRMAA_PART_B_SINGLE
        else:
            self.income_brackets = FEDERAL_TAX_BRACKETS_JOINT
            self.ltcg_brackets = LTCG_BRACKETS_JOINT
            self.irmaa_brackets = IRMAA_PART_B_JOINT
    
    def calculate_optimal_withdrawals(
        self,
        spending_need: float,
        balances: AccountBalances,
        age: int,
        other_income: float = 0.0,
        ss_income: float = 0.0,
        pension_income: float = 0.0,
    ) -> WithdrawalResult:
        """
        Calculate tax-optimal withdrawal sequence.
        
        Strategy:
        1. Take required RMDs from Traditional IRA (if age >= RMD_AGE)
        2. Withdraw from Taxable account (lowest tax rate via LTCG + basis recovery)
        3. Withdraw from Traditional IRA up to top of current bracket
        4. Preserve Roth as long as possible (tax-free growth)
        
        Args:
            spending_need: Total spending amount needed
            balances: Current account balances
            age: Current age
            other_income: Other taxable income (W-2, interest, dividends)
            ss_income: Social Security income (85% taxable)
            pension_income: Pension income (100% taxable)
        
        Returns:
            WithdrawalResult with optimal withdrawal amounts and tax calculations
        """
        
        # Initialize withdrawals
        taxable_withdrawal = 0.0
        ira_withdrawal = 0.0
        roth_withdrawal = 0.0
        remaining_need = spending_need
        
        # Calculate current taxable income before withdrawals
        taxable_ss = ss_income * 0.85  # Assume 85% of SS is taxable (worst case)
        base_income = other_income + taxable_ss + pension_income
        
        # STEP 1: Required Minimum Distributions (must take)
        if age >= RMD_AGE_DEFAULT:
            rmd_required = calculate_rmd(balances.traditional_ira, age)
            rmd_to_take = min(rmd_required, balances.traditional_ira)
            ira_withdrawal += rmd_to_take
            remaining_need -= rmd_to_take
        
        # STEP 2: Taxable account (LTCG rate + basis recovery)
        if remaining_need > 0 and balances.taxable > 0:
            # Calculate available taxable withdrawal
            taxable_available = min(remaining_need, balances.taxable)
            taxable_withdrawal = taxable_available
            remaining_need -= taxable_withdrawal
        
        # STEP 3: Traditional IRA (fill up current tax bracket)
        if remaining_need > 0 and balances.traditional_ira > ira_withdrawal:
            # Calculate current bracket room
            current_income = base_income + ira_withdrawal + self._calculate_taxable_from_taxable_withdrawal(
                taxable_withdrawal, balances.taxable_basis, balances.taxable
            )
            
            # Find next bracket threshold
            next_threshold = self._get_next_bracket_threshold(current_income)
            bracket_room = max(0, next_threshold - current_income)
            
            # Withdraw up to bracket room or remaining need
            ira_available = balances.traditional_ira - ira_withdrawal
            additional_ira = min(remaining_need, ira_available, bracket_room)
            ira_withdrawal += additional_ira
            remaining_need -= additional_ira
        
        # STEP 4: Roth IRA (last resort, tax-free)
        if remaining_need > 0 and balances.roth_ira > 0:
            roth_withdrawal = min(remaining_need, balances.roth_ira)
            remaining_need -= roth_withdrawal
        
        # Calculate total withdrawn
        total_withdrawn = taxable_withdrawal + ira_withdrawal + roth_withdrawal
        
        # Calculate taxes
        taxes = self._calculate_taxes(
            taxable_withdrawal=taxable_withdrawal,
            ira_withdrawal=ira_withdrawal,
            roth_withdrawal=roth_withdrawal,
            taxable_basis=balances.taxable_basis,
            taxable_balance=balances.taxable,
            base_income=base_income,
            age=age,  # Pass age for IRMAA calculation
        )
        
        return WithdrawalResult(
            taxable_withdrawal=taxable_withdrawal,
            ira_withdrawal=ira_withdrawal,
            roth_withdrawal=roth_withdrawal,
            total_withdrawn=total_withdrawn,
            federal_tax=taxes['federal_tax'],
            ltcg_tax=taxes['ltcg_tax'],
            irmaa_surcharge=taxes['irmaa_annual'],
            effective_tax_rate=taxes['effective_rate'],
            marginal_rate=taxes['marginal_rate'],
        )
    
    def optimize_roth_conversions(
        self,
        ira_balance: float,
        years_until_rmd: int,
        projected_income_by_year: List[float],
        current_age: int,
        max_annual_conversion_pct: float = 0.15,
        avoid_irmaa: bool = True,
        discount_rate: float = 0.04,
    ) -> RothConversionSchedule:
        """
        Calculate optimal Roth conversion schedule.
        
        Strategy:
        1. Identify low-income years (early retirement, between jobs, etc.)
        2. Convert up to top of current tax bracket each year
        3. Avoid IRMAA thresholds if specified
        4. Maximize conversions before RMDs begin
        5. Account for tax savings via lower future RMDs
        
        Args:
            ira_balance: Current Traditional IRA balance
            years_until_rmd: Years remaining until RMD age
            projected_income_by_year: Expected income each year (excl. conversions)
            current_age: Client's current age
            max_annual_conversion_pct: Max % of IRA to convert per year (default 15%)
            avoid_irmaa: Whether to stay below IRMAA thresholds
            discount_rate: Discount rate for PV calculations
        
        Returns:
            RothConversionSchedule with year-by-year conversion amounts
        """
        
        n_years = min(years_until_rmd, len(projected_income_by_year))
        if n_years <= 0:
            # Already at RMD age or no projection data
            return RothConversionSchedule(
                years=[], ages=[], conversion_amounts=[], projected_taxes=[],
                cumulative_savings=[], total_conversions=0.0,
                total_taxes_on_conversions=0.0, lifetime_tax_savings=0.0
            )
        
        years = []
        ages = []
        conversion_amounts = []
        projected_taxes = []
        cumulative_savings = []
        
        remaining_ira = ira_balance
        total_taxes = 0.0
        cumulative_pv_savings = 0.0
        
        for year_idx in range(n_years):
            age = current_age + year_idx
            base_income = projected_income_by_year[year_idx]
            
            # Calculate optimal conversion for this year
            conversion, tax_on_conversion = self._calculate_optimal_conversion_for_year(
                remaining_ira=remaining_ira,
                base_income=base_income,
                age=age,
                max_conversion_pct=max_annual_conversion_pct,
                avoid_irmaa=avoid_irmaa,
            )
            
            if conversion > 0:
                years.append(year_idx)
                ages.append(age)
                conversion_amounts.append(conversion)
                projected_taxes.append(tax_on_conversion)
                
                # Calculate tax savings from avoiding future RMDs
                # Simplified: assume conversion saves paying ordinary income tax on RMDs later
                future_rmd_tax_saved = self._estimate_rmd_tax_savings(
                    conversion_amount=conversion,
                    years_until_rmd=years_until_rmd - year_idx,
                )
                
                # Present value of savings
                pv_savings = (future_rmd_tax_saved - tax_on_conversion) / ((1 + discount_rate) ** year_idx)
                cumulative_pv_savings += pv_savings
                cumulative_savings.append(cumulative_pv_savings)
                
                # Update remaining IRA
                remaining_ira -= conversion
                total_taxes += tax_on_conversion
            
        return RothConversionSchedule(
            years=years,
            ages=ages,
            conversion_amounts=conversion_amounts,
            projected_taxes=projected_taxes,
            cumulative_savings=cumulative_savings,
            total_conversions=sum(conversion_amounts),
            total_taxes_on_conversions=total_taxes,
            lifetime_tax_savings=cumulative_pv_savings,
        )
    
    def _calculate_optimal_conversion_for_year(
        self,
        remaining_ira: float,
        base_income: float,
        age: int,
        max_conversion_pct: float,
        avoid_irmaa: bool,
    ) -> Tuple[float, float]:
        """
        Calculate optimal Roth conversion amount for a single year.
        
        Returns:
            Tuple of (conversion_amount, tax_on_conversion)
        """
        
        if remaining_ira <= 0:
            return (0.0, 0.0)
        
        # Maximum conversion based on percentage limit
        max_conversion = remaining_ira * max_conversion_pct
        
        # Find current tax bracket
        current_bracket_threshold, current_rate = self._get_tax_bracket(base_income)
        
        # Find next bracket threshold
        next_threshold = self._get_next_bracket_threshold(base_income)
        
        # Calculate room in current bracket
        bracket_room = next_threshold - base_income
        
        # If avoiding IRMAA, check threshold
        if avoid_irmaa and age >= 63:  # IRMAA looks back 2 years
            irmaa_threshold = self._get_next_irmaa_threshold(base_income)
            if irmaa_threshold < next_threshold:
                # Limit by IRMAA instead
                bracket_room = min(bracket_room, irmaa_threshold - base_income)
        
        # Optimal conversion: fill current bracket without exceeding thresholds
        optimal_conversion = min(max_conversion, bracket_room)
        
        # Ensure positive
        optimal_conversion = max(0.0, optimal_conversion)
        
        # Calculate tax on conversion
        tax = optimal_conversion * current_rate
        
        return (optimal_conversion, tax)
    
    def _estimate_rmd_tax_savings(
        self,
        conversion_amount: float,
        years_until_rmd: int,
    ) -> float:
        """
        Estimate tax savings from reducing future RMDs via Roth conversion.
        
        Simplified model:
        - Converted amount grows tax-free in Roth
        - If left in IRA, would be subject to RMDs and ordinary income tax
        - Assume marginal rate at RMD age
        """
        
        # Assume IRA would grow at 5% real until RMDs start
        growth_rate = 0.05
        future_value = conversion_amount * ((1 + growth_rate) ** years_until_rmd)
        
        # Assume 25% average tax on RMDs (conservative middle bracket)
        estimated_rmd_tax = future_value * 0.25
        
        return estimated_rmd_tax
    
    def _calculate_taxes(
        self,
        taxable_withdrawal: float,
        ira_withdrawal: float,
        roth_withdrawal: float,
        taxable_basis: float,
        taxable_balance: float,
        base_income: float,
        age: int = 65,  # Add age parameter
    ) -> Dict[str, float]:
        """Calculate comprehensive tax liability."""
        
        # Calculate gains in taxable withdrawal
        if taxable_balance > 0:
            basis_pct = min(1.0, taxable_basis / taxable_balance)
            basis_recovered = taxable_withdrawal * basis_pct
            capital_gains = taxable_withdrawal - basis_recovered
        else:
            capital_gains = 0.0
        
        # Calculate taxable income
        # Roth withdrawals are tax-free
        taxable_income = base_income + ira_withdrawal + capital_gains
        
        # Federal income tax (on IRA withdrawals at ordinary rates)
        federal_tax = calculate_federal_tax(base_income + ira_withdrawal, self.filing_status)
        
        # LTCG tax on capital gains
        ltcg_rate = get_ltcg_rate(taxable_income, self.filing_status)
        ltcg_tax = capital_gains * ltcg_rate
        
        # State tax
        state_tax = (ira_withdrawal + capital_gains) * self.state_tax_rate
        
        # IRMAA surcharge (if age 65+)
        # Use MAGI which includes IRA withdrawal but not capital gains benefit
        magi = base_income + ira_withdrawal
        if age >= 65:  # Use age parameter instead of self.current_age
            irmaa = get_irmaa_surcharge(magi, self.filing_status)
            irmaa_annual = irmaa['total_annual']
        else:
            irmaa_annual = 0.0
        
        # Total tax
        total_tax = federal_tax + ltcg_tax + state_tax + irmaa_annual
        
        # Effective rate
        total_withdrawn = taxable_withdrawal + ira_withdrawal + roth_withdrawal
        effective_rate = total_tax / total_withdrawn if total_withdrawn > 0 else 0.0
        
        # Marginal rate
        marginal_rate = self._get_tax_bracket(taxable_income)[1]
        
        return {
            'federal_tax': federal_tax,
            'ltcg_tax': ltcg_tax,
            'state_tax': state_tax,
            'irmaa_annual': irmaa_annual,
            'total_tax': total_tax,
            'effective_rate': effective_rate,
            'marginal_rate': marginal_rate,
        }
    
    def _calculate_taxable_from_taxable_withdrawal(
        self,
        withdrawal: float,
        basis: float,
        balance: float,
    ) -> float:
        """Calculate taxable portion of a taxable account withdrawal."""
        if balance <= 0:
            return 0.0
        
        basis_pct = min(1.0, basis / balance)
        taxable_portion = withdrawal * (1 - basis_pct)
        return taxable_portion
    
    def _get_tax_bracket(self, income: float) -> Tuple[float, float]:
        """Get the tax bracket (threshold, rate) for given income."""
        for i in range(len(self.income_brackets) - 1, -1, -1):
            threshold, rate = self.income_brackets[i]
            if income >= threshold:
                return (threshold, rate)
        return self.income_brackets[0]
    
    def _get_next_bracket_threshold(self, income: float) -> float:
        """Get the threshold of the next higher tax bracket."""
        for i, (threshold, rate) in enumerate(self.income_brackets):
            if income < threshold:
                return threshold
        # Already in highest bracket
        return float('inf')
    
    def _get_next_irmaa_threshold(self, income: float) -> float:
        """Get the threshold of the next higher IRMAA tier."""
        for threshold, surcharge in self.irmaa_brackets:
            if income < threshold:
                return threshold
        return float('inf')
    
    def calculate_lifetime_taxes(
        self,
        withdrawal_schedule: List[WithdrawalResult],
        discount_rate: float = 0.04,
    ) -> Dict[str, float]:
        """
        Calculate present value of lifetime taxes.
        
        Args:
            withdrawal_schedule: List of WithdrawalResult for each year
            discount_rate: Real discount rate for PV calculation
        
        Returns:
            Dictionary with lifetime tax metrics
        """
        
        total_taxes = 0.0
        pv_taxes = 0.0
        total_irmaa = 0.0
        
        for year_idx, result in enumerate(withdrawal_schedule):
            annual_tax = result.federal_tax + result.ltcg_tax
            pv_tax = annual_tax / ((1 + discount_rate) ** year_idx)
            
            total_taxes += annual_tax
            pv_taxes += pv_tax
            total_irmaa += result.irmaa_surcharge
        
        return {
            'total_lifetime_taxes': total_taxes,
            'pv_lifetime_taxes': pv_taxes,
            'total_irmaa_surcharges': total_irmaa,
            'average_annual_tax': total_taxes / len(withdrawal_schedule) if withdrawal_schedule else 0.0,
        }


def compare_withdrawal_strategies(
    naive_results: List[WithdrawalResult],
    optimized_results: List[WithdrawalResult],
    discount_rate: float = 0.04,
) -> Dict[str, any]:
    """
    Compare naive (proportional) vs. optimized withdrawal strategies.
    
    Args:
        naive_results: Results from proportional withdrawals
        optimized_results: Results from tax-optimized withdrawals
        discount_rate: Discount rate for PV calculations
    
    Returns:
        Comparison metrics showing tax savings
    """
    
    optimizer = TaxOptimizer()
    
    naive_lifetime = optimizer.calculate_lifetime_taxes(naive_results, discount_rate)
    optimized_lifetime = optimizer.calculate_lifetime_taxes(optimized_results, discount_rate)
    
    savings = naive_lifetime['pv_lifetime_taxes'] - optimized_lifetime['pv_lifetime_taxes']
    savings_pct = savings / naive_lifetime['pv_lifetime_taxes'] if naive_lifetime['pv_lifetime_taxes'] > 0 else 0.0
    
    return {
        'naive_lifetime_tax': naive_lifetime['pv_lifetime_taxes'],
        'optimized_lifetime_tax': optimized_lifetime['pv_lifetime_taxes'],
        'tax_savings': savings,
        'tax_savings_pct': savings_pct,
        'naive_avg_annual': naive_lifetime['average_annual_tax'],
        'optimized_avg_annual': optimized_lifetime['average_annual_tax'],
        'irmaa_savings': naive_lifetime['total_irmaa_surcharges'] - optimized_lifetime['total_irmaa_surcharges'],
    }


if __name__ == "__main__":
    """Example usage and testing."""
    
    print("="*60)
    print("TAX OPTIMIZER EXAMPLES")
    print("="*60)
    
    # Example 1: Optimal withdrawal sequencing
    print("\nEXAMPLE 1: Optimal Withdrawal Sequencing")
    print("-" * 60)
    
    optimizer = TaxOptimizer(filing_status='single', current_age=68)
    
    balances = AccountBalances(
        taxable=500000,
        traditional_ira=1500000,
        roth_ira=500000,
        taxable_basis=300000,  # 60% cost basis
    )
    
    result = optimizer.calculate_optimal_withdrawals(
        spending_need=120000,
        balances=balances,
        age=68,
        other_income=0,
        ss_income=40000,
        pension_income=0,
    )
    
    print(f"Spending need: ${result.total_withdrawn:,.2f}")
    print(f"  From Taxable: ${result.taxable_withdrawal:,.2f}")
    print(f"  From IRA: ${result.ira_withdrawal:,.2f}")
    print(f"  From Roth: ${result.roth_withdrawal:,.2f}")
    print(f"\nTaxes:")
    print(f"  Federal: ${result.federal_tax:,.2f}")
    print(f"  LTCG: ${result.ltcg_tax:,.2f}")
    print(f"  IRMAA: ${result.irmaa_surcharge:,.2f}")
    print(f"  Effective rate: {result.effective_tax_rate:.2%}")
    print(f"  Marginal rate: {result.marginal_rate:.0%}")
    
    # Example 2: Roth conversion optimization
    print("\n" + "="*60)
    print("EXAMPLE 2: Roth Conversion Optimization")
    print("-" * 60)
    
    projected_income = [30000, 30000, 40000, 50000, 60000]  # Low income in early years
    
    conversion_schedule = optimizer.optimize_roth_conversions(
        ira_balance=1500000,
        years_until_rmd=5,
        projected_income_by_year=projected_income,
        current_age=68,
        max_annual_conversion_pct=0.10,
        avoid_irmaa=True,
    )
    
    print(f"Optimal Roth Conversion Schedule:")
    print(f"{'Year':<6} {'Age':<6} {'Convert':<15} {'Tax':<15} {'Cumul. Savings':<20}")
    print("-" * 65)
    
    for i in range(len(conversion_schedule.years)):
        year = conversion_schedule.years[i]
        age = conversion_schedule.ages[i]
        amount = conversion_schedule.conversion_amounts[i]
        tax = conversion_schedule.projected_taxes[i]
        savings = conversion_schedule.cumulative_savings[i]
        print(f"{year:<6} {age:<6} ${amount:>12,.0f}  ${tax:>12,.0f}  ${savings:>17,.0f}")
    
    print(f"\nSummary:")
    print(f"  Total conversions: ${conversion_schedule.total_conversions:,.0f}")
    print(f"  Total taxes paid: ${conversion_schedule.total_taxes_on_conversions:,.0f}")
    print(f"  Lifetime tax savings (PV): ${conversion_schedule.lifetime_tax_savings:,.0f}")
