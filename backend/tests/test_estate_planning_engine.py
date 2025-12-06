"""
Tests for Estate Planning Engine

Validates estate tax calculations, inherited IRA taxation,
basis step-up, and Roth conversion analysis.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.estate_planning_engine import (
    EstatePlanningEngine,
    StateEstateTax
)


def test_estate_tax_basic():
    """Test basic estate tax calculation"""
    print("\n=== TEST: Basic Estate Tax ===")
    
    engine = EstatePlanningEngine()
    
    # Test case: $20M estate, no state tax
    result = engine.calculate_estate_tax(
        gross_estate=20_000_000,
        state=StateEstateTax.NONE
    )
    
    print(f"Gross Estate: ${result.gross_estate:,.0f}")
    print(f"Federal Exemption: ${result.federal_exemption_used:,.0f}")
    print(f"Taxable Estate: ${result.federal_taxable_estate:,.0f}")
    print(f"Federal Tax: ${result.federal_estate_tax:,.0f}")
    print(f"Net to Heirs: ${result.net_to_heirs:,.0f}")
    print(f"Effective Tax Rate: {result.effective_tax_rate*100:.2f}%")
    
    # Validate: $20M - $13.61M = $6.39M taxable @ 40% = $2.556M tax
    expected_taxable = 20_000_000 - 13_610_000
    expected_tax = expected_taxable * 0.40
    
    assert abs(result.federal_taxable_estate - expected_taxable) < 1000, "Taxable estate calculation error"
    assert abs(result.federal_estate_tax - expected_tax) < 1000, "Estate tax calculation error"
    assert result.state_estate_tax == 0, "Should have no state tax"
    
    print("✅ Basic estate tax test passed")


def test_estate_tax_with_state():
    """Test estate tax with state taxes (Massachusetts cliff)"""
    print("\n=== TEST: Estate Tax with MA Cliff ===")
    
    engine = EstatePlanningEngine()
    
    # Massachusetts has $2M exemption with cliff
    # Estate > $2M loses entire exemption
    result = engine.calculate_estate_tax(
        gross_estate=2_500_000,
        state=StateEstateTax.MASSACHUSETTS
    )
    
    print(f"Gross Estate: ${result.gross_estate:,.0f}")
    print(f"State: Massachusetts (cliff at $2M)")
    print(f"State Taxable: ${result.state_taxable_estate:,.0f}")
    print(f"State Tax: ${result.state_estate_tax:,.0f}")
    print(f"Total Estate Tax: ${result.total_estate_tax:,.0f}")
    
    # MA cliff: entire $2.5M is taxable (no exemption)
    assert result.state_taxable_estate == 2_500_000, "MA cliff not applied"
    assert result.state_estate_tax == 2_500_000 * 0.16, "MA tax rate error"
    
    print("✅ MA cliff estate tax test passed")


def test_estate_tax_portability():
    """Test portability of spouse's unused exemption"""
    print("\n=== TEST: Spousal Portability ===")
    
    engine = EstatePlanningEngine()
    
    # Scenario: First spouse died with $5M estate
    # Second spouse gets $8.61M portability ($13.61M - $5M)
    result = engine.calculate_estate_tax(
        gross_estate=20_000_000,
        is_married=False,  # Second spouse (now widowed)
        spousal_exemption_used=8_610_000  # Portability from first spouse
    )
    
    print(f"Gross Estate: ${result.gross_estate:,.0f}")
    print(f"Base Exemption: ${13_610_000:,.0f}")
    print(f"Portability: ${8_610_000:,.0f}")
    print(f"Total Exemption: ${result.federal_exemption_used:,.0f}")
    print(f"Federal Tax: ${result.federal_estate_tax:,.0f}")
    
    # Total exemption: $13.61M + $8.61M = $22.21M
    # $20M estate < $22.21M exemption = no tax
    assert result.federal_estate_tax == 0, "Should have no federal tax with portability"
    assert result.federal_exemption_used == 20_000_000, "Should use only needed exemption"
    
    print("✅ Portability test passed")


def test_inherited_ira_10_year_rule():
    """Test inherited IRA taxation under SECURE Act"""
    print("\n=== TEST: Inherited IRA (10-year rule) ===")
    
    engine = EstatePlanningEngine()
    
    # $1M IRA inherited by 45-year-old in 32% bracket
    result = engine.calculate_inherited_ira_tax(
        ira_balance=1_000_000,
        heir_age=45,
        heir_current_income=150_000,
        distribution_strategy="even_10yr",
        compare_to_stretch=True
    )
    
    print(f"IRA Balance: ${result.ira_balance:,.0f}")
    print(f"Heir Age: {result.heir_age}")
    print(f"Distribution Strategy: {result.distribution_strategy}")
    print(f"Total Distributions: ${result.total_distributions:,.0f}")
    print(f"Total Income Tax: ${result.total_income_tax:,.0f}")
    print(f"Net to Heir: ${result.net_to_heir:,.0f}")
    print(f"Effective Tax Rate: {result.effective_tax_rate*100:.2f}%")
    
    if result.comparison_to_stretch:
        print(f"\nStretch IRA Comparison:")
        print(f"  Stretch Net: ${result.comparison_to_stretch['stretch_net_to_heir']:,.0f}")
        print(f"  SECURE Act Penalty: ${result.comparison_to_stretch['secure_act_penalty']:,.0f}")
    
    # Validate: Should pay significant tax (20-35% range)
    assert result.total_income_tax > 0, "Should have tax liability"
    assert result.effective_tax_rate > 0.15, "Effective rate should be >15%"
    assert len(result.annual_distributions) > 0, "Should have distribution schedule"
    
    print("✅ Inherited IRA test passed")


def test_inherited_ira_strategies():
    """Compare different IRA distribution strategies"""
    print("\n=== TEST: IRA Distribution Strategy Comparison ===")
    
    engine = EstatePlanningEngine()
    
    strategies = ["lump_sum", "even_10yr", "delayed_10yr"]
    results = {}
    
    for strategy in strategies:
        result = engine.calculate_inherited_ira_tax(
            ira_balance=1_000_000,
            heir_age=45,
            heir_current_income=150_000,
            distribution_strategy=strategy,
            growth_rate=0.06,
            compare_to_stretch=False
        )
        results[strategy] = result
        
        print(f"\nStrategy: {strategy}")
        print(f"  Total Income Tax: ${result.total_income_tax:,.0f}")
        print(f"  Net to Heir: ${result.net_to_heir:,.0f}")
        print(f"  Effective Rate: {result.effective_tax_rate*100:.2f}%")
    
    # Validate: Lump sum should have highest tax rate
    assert results["lump_sum"].effective_tax_rate > results["even_10yr"].effective_tax_rate, \
        "Lump sum should have higher tax rate"
    
    print("✅ Strategy comparison test passed")


def test_basis_step_up():
    """Test step-up in basis calculation"""
    print("\n=== TEST: Basis Step-Up ===")
    
    engine = EstatePlanningEngine()
    
    # $5M account with $1M cost basis = $4M unrealized gains
    result = engine.calculate_basis_step_up(
        account_value=5_000_000,
        cost_basis=1_000_000,
        ltcg_rate=0.20,
        state_cap_gains_rate=0.0
    )
    
    print(f"Account Value: ${result.account_value:,.0f}")
    print(f"Original Cost Basis: ${result.original_cost_basis:,.0f}")
    print(f"Unrealized Gains: ${result.unrealized_gains:,.0f}")
    print(f"Capital Gains Eliminated: ${result.capital_gains_eliminated:,.0f}")
    print(f"LTCG Tax Saved: ${result.ltcg_tax_saved:,.0f}")
    print(f"Heir's New Basis: ${result.heir_new_basis:,.0f}")
    
    # Validate: $4M gains @ 23.8% (20% + 3.8% NIIT) = $952k saved
    expected_savings = 4_000_000 * (0.20 + 0.038)
    assert abs(result.ltcg_tax_saved - expected_savings) < 1000, "Tax savings calculation error"
    assert result.heir_new_basis == 5_000_000, "Step-up should equal FMV"
    
    print("✅ Basis step-up test passed")


def test_roth_conversion_analysis():
    """Test Roth conversion analysis for heirs"""
    print("\n=== TEST: Roth Conversion for Heirs ===")
    
    engine = EstatePlanningEngine()
    
    # Convert $500k of $1M IRA
    result = engine.analyze_roth_conversion_for_heirs(
        traditional_ira_balance=1_000_000,
        conversion_amount=500_000,
        owner_age=65,
        owner_tax_rate=0.24,  # Owner in 24% bracket
        heir_age=45,
        heir_tax_bracket=0.32,  # Heir in 32% bracket
        years_until_inheritance=20,
        ira_growth_rate=0.07,
        discount_rate=0.04
    )
    
    print(f"Conversion Amount: ${result.conversion_amount:,.0f}")
    print(f"Upfront Tax (24%): ${result.upfront_conversion_tax:,.0f}")
    print(f"Years Until Inheritance: {result.years_until_inheritance}")
    print(f"Projected Roth Value: ${result.projected_roth_value:,.0f}")
    print(f"Roth Inheritance (tax-free): ${result.roth_inheritance_value:,.0f}")
    print(f"Traditional IRA Tax (32%): ${result.trad_ira_inheritance_tax:,.0f}")
    print(f"Net Benefit to Heir: ${result.net_benefit_to_heir:,.0f}")
    print(f"NPV Advantage: ${result.npv_advantage:,.0f}")
    print(f"Recommendation: {result.recommended_strategy}")
    print(f"Break-even: {result.break_even_years} years")
    
    # Validate: Owner's 24% < heir's 32% = conversion beneficial
    assert result.net_benefit_to_heir > 0, "Should benefit heir (lower owner rate)"
    assert result.upfront_conversion_tax == 500_000 * 0.24, "Conversion tax error"
    
    print("✅ Roth conversion test passed")


def test_comprehensive_estate_plan():
    """Test comprehensive estate planning analysis"""
    print("\n=== TEST: Comprehensive Estate Plan ===")
    
    engine = EstatePlanningEngine()
    
    # High net worth scenario: $25M estate
    result = engine.comprehensive_estate_plan(
        gross_estate=25_000_000,
        traditional_ira=5_000_000,
        roth_ira=2_000_000,
        taxable_account=15_000_000,
        taxable_cost_basis=5_000_000,
        state=StateEstateTax.NEW_YORK,
        heir_age=45,
        heir_income=200_000,
        years_until_inheritance=20
    )
    
    print(f"\n=== Estate Tax ===")
    estate_tax = result["estate_tax"]
    print(f"Gross Estate: ${estate_tax.gross_estate:,.0f}")
    print(f"Federal Tax: ${estate_tax.federal_estate_tax:,.0f}")
    print(f"State Tax: ${estate_tax.state_estate_tax:,.0f}")
    print(f"Total Tax: ${estate_tax.total_estate_tax:,.0f}")
    
    if "inherited_ira" in result:
        print(f"\n=== Inherited IRA ===")
        ira = result["inherited_ira"]
        print(f"IRA Balance: ${ira.ira_balance:,.0f}")
        print(f"Income Tax: ${ira.total_income_tax:,.0f}")
        print(f"Net to Heir: ${ira.net_to_heir:,.0f}")
    
    if "basis_step_up" in result:
        print(f"\n=== Basis Step-Up ===")
        step_up = result["basis_step_up"]
        print(f"Unrealized Gains: ${step_up.unrealized_gains:,.0f}")
        print(f"Tax Saved: ${step_up.ltcg_tax_saved:,.0f}")
    
    if "roth_conversion_scenarios" in result:
        print(f"\n=== Roth Conversion Scenarios ===")
        for scenario in result["roth_conversion_scenarios"]:
            analysis = scenario["analysis"]
            print(f"{scenario['conversion_percentage']*100:.0f}% conversion: NPV ${analysis.npv_advantage:,.0f}")
    
    print(f"\n=== Recommendations ({len(result['recommendations'])} found) ===")
    for rec in result["recommendations"]:
        print(f"[{rec['priority'].upper()}] {rec['category']}: {rec['message']}")
    
    # Validate comprehensive analysis
    assert estate_tax.total_estate_tax > 0, "Should have estate tax"
    assert len(result["recommendations"]) > 0, "Should have recommendations"
    
    print("✅ Comprehensive estate plan test passed")


def run_all_tests():
    """Run all estate planning tests"""
    print("\n" + "="*60)
    print("ESTATE PLANNING ENGINE TEST SUITE")
    print("="*60)
    
    tests = [
        test_estate_tax_basic,
        test_estate_tax_with_state,
        test_estate_tax_portability,
        test_inherited_ira_10_year_rule,
        test_inherited_ira_strategies,
        test_basis_step_up,
        test_roth_conversion_analysis,
        test_comprehensive_estate_plan
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            print(f"❌ {test.__name__} FAILED: {str(e)}")
            failed += 1
    
    print("\n" + "="*60)
    print(f"TEST SUMMARY: {passed} passed, {failed} failed")
    print("="*60)


if __name__ == "__main__":
    run_all_tests()
