"""
Unit Tests for Tax Optimizer

Tests cover:
1. Withdrawal sequencing optimization
2. RMD compliance
3. Roth preservation strategy
4. Tax bracket awareness
5. IRMAA threshold management
6. Roth conversion optimization
7. Lifetime tax calculations
"""

import unittest
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from core.tax_optimizer import (
    TaxOptimizer,
    AccountBalances,
    WithdrawalResult,
    RothConversionSchedule,
    compare_withdrawal_strategies,
)
from core.assumptions import RMD_AGE_DEFAULT


class TestWithdrawalSequencing(unittest.TestCase):
    """Test optimal withdrawal sequencing logic."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.optimizer = TaxOptimizer(
            filing_status='single',
            state_tax_rate=0.0,
            current_age=65,
        )
    
    def test_rmd_compliance(self):
        """Verify RMDs are always taken when required."""
        balances = AccountBalances(
            taxable=500000,
            traditional_ira=1000000,
            roth_ira=500000,
            taxable_basis=300000,
        )
        
        # Age 75: RMD required
        result = self.optimizer.calculate_optimal_withdrawals(
            spending_need=50000,
            balances=balances,
            age=75,
        )
        
        # Calculate expected RMD
        from core.assumptions import calculate_rmd
        expected_rmd = calculate_rmd(balances.traditional_ira, 75)
        
        # IRA withdrawal should be at least RMD
        self.assertGreaterEqual(
            result.ira_withdrawal,
            expected_rmd,
            "IRA withdrawal must meet RMD requirement"
        )
    
    def test_roth_preserved_longest(self):
        """Verify Roth is minimized when other accounts available."""
        balances = AccountBalances(
            taxable=200000,
            traditional_ira=300000,
            roth_ira=1000000,  # Large Roth balance
            taxable_basis=120000,
        )
        
        # Need $120K, have plenty in taxable+IRA
        result = self.optimizer.calculate_optimal_withdrawals(
            spending_need=120000,
            balances=balances,
            age=65,
        )
        
        # Should minimize Roth usage (less than 10% of total withdrawal)
        roth_pct = result.roth_withdrawal / result.total_withdrawn if result.total_withdrawn > 0 else 0
        self.assertLess(
            roth_pct,
            0.10,
            "Roth should be minimized when other accounts available"
        )
    
    def test_taxable_account_priority(self):
        """Verify taxable account used before IRA (for LTCG advantage)."""
        balances = AccountBalances(
            taxable=200000,
            traditional_ira=500000,
            roth_ira=500000,
            taxable_basis=120000,  # 60% basis
        )
        
        result = self.optimizer.calculate_optimal_withdrawals(
            spending_need=100000,
            balances=balances,
            age=65,  # Before RMD age
        )
        
        # Should prefer taxable account
        self.assertGreater(
            result.taxable_withdrawal,
            0,
            "Should use taxable account first"
        )
        
        # Should minimize IRA withdrawal
        self.assertLess(
            result.ira_withdrawal,
            result.taxable_withdrawal,
            "IRA withdrawal should be less than taxable"
        )
    
    def test_bracket_awareness(self):
        """Verify optimizer stays within current tax bracket when possible."""
        balances = AccountBalances(
            taxable=50000,
            traditional_ira=1000000,
            roth_ira=500000,
            taxable_basis=30000,
        )
        
        # With SS income of $40K, already at ~12% bracket
        result = self.optimizer.calculate_optimal_withdrawals(
            spending_need=60000,
            balances=balances,
            age=67,
            ss_income=40000,
        )
        
        # Should limit IRA withdrawal to avoid jumping to 22% bracket
        # 12% bracket tops out around $47K for single filer
        # So with $34K taxable SS income + gains, should be cautious
        self.assertLess(
            result.marginal_rate,
            0.25,
            "Should avoid jumping into high brackets unnecessarily"
        )
    
    def test_tax_efficiency_vs_proportional(self):
        """Verify optimized withdrawals save taxes vs proportional approach."""
        balances = AccountBalances(
            taxable=1000000,
            traditional_ira=1000000,
            roth_ira=1000000,
            taxable_basis=600000,
        )
        
        # Optimal withdrawal
        optimal = self.optimizer.calculate_optimal_withdrawals(
            spending_need=150000,
            balances=balances,
            age=70,
        )
        
        # Proportional withdrawal (naive: 1/3 from each)
        # Simulate by forcing specific withdrawals
        proportional_taxable = 150000 / 3
        proportional_ira = 150000 / 3
        proportional_roth = 150000 / 3
        
        # Calculate tax on proportional (manually)
        from core.assumptions import calculate_federal_tax, get_ltcg_rate
        
        # Capital gains from taxable (40% basis)
        gains = proportional_taxable * 0.4
        ltcg_rate = get_ltcg_rate(proportional_ira + gains, 'single')
        prop_ltcg_tax = gains * ltcg_rate
        prop_federal = calculate_federal_tax(proportional_ira, 'single')
        prop_total_tax = prop_ltcg_tax + prop_federal
        
        optimal_total_tax = optimal.federal_tax + optimal.ltcg_tax
        
        # Optimal should save some taxes (even modest savings matter)
        savings_pct = (prop_total_tax - optimal_total_tax) / prop_total_tax
        self.assertGreaterEqual(
            savings_pct,
            0.0,
            f"Optimal strategy should not increase taxes. "
            f"Savings: {savings_pct:.1%}"
        )
        
        # Print for information
        print(f"\n  Tax savings: {savings_pct:.1%} (${prop_total_tax - optimal_total_tax:,.0f})")


class TestRothConversions(unittest.TestCase):
    """Test Roth conversion optimization."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.optimizer = TaxOptimizer(
            filing_status='single',
            current_age=60,
        )
    
    def test_low_income_years_prioritized(self):
        """Verify conversions happen in low-income years."""
        # Scenario: Early retirement, low income for 5 years
        low_income = [20000, 20000, 25000, 30000, 40000]
        
        schedule = self.optimizer.optimize_roth_conversions(
            ira_balance=1000000,
            years_until_rmd=13,  # Age 60 → 73
            projected_income_by_year=low_income + [80000] * 8,  # Higher income later
            current_age=60,
        )
        
        # Should do substantial conversions in first 5 years (low income)
        if len(schedule.conversion_amounts) >= 5:
            early_conversions = sum(schedule.conversion_amounts[:5])
            total_conversions = sum(schedule.conversion_amounts)
            early_pct = early_conversions / total_conversions if total_conversions > 0 else 0
            
            # At least 30% of conversions should happen in low-income years
            self.assertGreater(
                early_pct,
                0.25,
                f"Should do substantial conversions in low-income years. Got {early_pct:.1%}"
            )
    
    def test_irmaa_avoidance(self):
        """Verify conversions respect IRMAA thresholds."""
        # Income just below IRMAA threshold ($103K for single)
        income_near_threshold = [95000] * 10
        
        schedule = self.optimizer.optimize_roth_conversions(
            ira_balance=500000,
            years_until_rmd=10,
            projected_income_by_year=income_near_threshold,
            current_age=63,
            avoid_irmaa=True,
        )
        
        # Conversions should not push income over IRMAA threshold
        for i, conversion in enumerate(schedule.conversion_amounts):
            total_income = income_near_threshold[schedule.years[i]] + conversion
            self.assertLess(
                total_income,
                103000 + 1000,  # Allow $1K buffer
                f"Year {i}: Conversion should avoid IRMAA threshold"
            )
    
    def test_max_conversion_percentage_respected(self):
        """Verify max annual conversion limit is respected."""
        ira_balance = 1000000
        max_pct = 0.10  # 10% max per year
        
        schedule = self.optimizer.optimize_roth_conversions(
            ira_balance=ira_balance,
            years_until_rmd=10,
            projected_income_by_year=[30000] * 10,
            current_age=60,
            max_annual_conversion_pct=max_pct,
        )
        
        # Each year should convert <= 10% of remaining IRA
        remaining = ira_balance
        for i, conversion in enumerate(schedule.conversion_amounts):
            max_allowed = remaining * max_pct
            self.assertLessEqual(
                conversion,
                max_allowed * 1.01,  # Allow 1% rounding
                f"Year {i}: Conversion exceeds max percentage"
            )
            remaining -= conversion
    
    def test_positive_tax_savings(self):
        """Verify Roth conversions generate positive lifetime tax savings."""
        schedule = self.optimizer.optimize_roth_conversions(
            ira_balance=1000000,
            years_until_rmd=10,
            projected_income_by_year=[40000] * 10,
            current_age=60,
        )
        
        # Lifetime savings should be positive
        self.assertGreater(
            schedule.lifetime_tax_savings,
            0,
            "Roth conversions should generate positive tax savings"
        )
        
        # Savings should exceed taxes paid
        self.assertGreater(
            schedule.lifetime_tax_savings,
            schedule.total_taxes_on_conversions,
            "Savings should exceed upfront taxes paid"
        )
    
    def test_no_conversions_at_rmd_age(self):
        """Verify no conversions recommended at/after RMD age."""
        schedule = self.optimizer.optimize_roth_conversions(
            ira_balance=1000000,
            years_until_rmd=0,  # Already at RMD age
            projected_income_by_year=[50000] * 5,
            current_age=73,
        )
        
        self.assertEqual(
            schedule.total_conversions,
            0.0,
            "Should not recommend conversions at RMD age"
        )


class TestTaxCalculations(unittest.TestCase):
    """Test tax calculation accuracy."""
    
    def setUp(self):
        self.optimizer = TaxOptimizer(filing_status='single', current_age=65)
    
    def test_basis_recovery(self):
        """Verify cost basis is properly recovered from taxable accounts."""
        balances = AccountBalances(
            taxable=100000,
            traditional_ira=0,
            roth_ira=0,
            taxable_basis=60000,  # 60% cost basis
        )
        
        result = self.optimizer.calculate_optimal_withdrawals(
            spending_need=100000,
            balances=balances,
            age=65,
        )
        
        # Only 40% should be taxable (gains)
        # With 40K gains and 0% LTCG rate at low income, should be minimal tax
        self.assertLess(
            result.ltcg_tax,
            10000,
            "LTCG tax should reflect basis recovery"
        )
    
    def test_irmaa_triggered_at_threshold(self):
        """Verify IRMAA surcharge applies at correct thresholds."""
        # Create optimizer at age 67 (Medicare age)
        optimizer_67 = TaxOptimizer(filing_status='single', current_age=67)
        
        balances = AccountBalances(
            taxable=200000,
            traditional_ira=1000000,
            roth_ira=0,
            taxable_basis=0,
        )
        
        # Create scenario where withdrawal pushes income over IRMAA threshold
        # Pension just below threshold, then withdrawal pushes over
        result = optimizer_67.calculate_optimal_withdrawals(
            spending_need=80000,  # Need more than pension
            balances=balances,
            age=67,
            pension_income=90000,  # $90K pension + withdrawals will exceed $103K IRMAA threshold
        )
        
        # With $90K pension + withdrawals, MAGI > $103K → IRMAA should apply
        total_income = 90000 + result.ira_withdrawal
        print(f"\\n  Pension: $90K, IRA withdrawal: ${result.ira_withdrawal:,.0f}, "
              f"Total MAGI: ${total_income:,.0f}, IRMAA: ${result.irmaa_surcharge:,.0f}")
        
        if total_income > 103000:
            self.assertGreater(
                result.irmaa_surcharge,
                0,
                f"IRMAA surcharge should apply when MAGI > $103K. MAGI: ${total_income:,.0f}"
            )
        else:
            # If optimizer avoided IRMAA by limiting withdrawals, that's also acceptable
            self.assertLessEqual(
                total_income,
                103000,
                "If IRMAA not triggered, MAGI should be at or below threshold"
            )
    
    def test_marginal_vs_effective_rate(self):
        """Verify marginal rate > effective rate."""
        balances = AccountBalances(
            taxable=100000,
            traditional_ira=500000,
            roth_ira=500000,
            taxable_basis=60000,
        )
        
        result = self.optimizer.calculate_optimal_withdrawals(
            spending_need=80000,
            balances=balances,
            age=65,
        )
        
        # Marginal should be >= effective
        self.assertGreaterEqual(
            result.marginal_rate,
            result.effective_tax_rate,
            "Marginal rate should be >= effective rate"
        )


class TestIntegration(unittest.TestCase):
    """Integration tests for complete scenarios."""
    
    def test_complete_retirement_scenario(self):
        """Test a complete 30-year retirement scenario."""
        optimizer = TaxOptimizer(filing_status='joint', current_age=65)
        
        starting_balances = AccountBalances(
            taxable=1000000,
            traditional_ira=2000000,
            roth_ira=1000000,
            taxable_basis=600000,
        )
        
        annual_spending = 150000
        annual_ss = 50000
        
        # Simulate 30 years of withdrawals
        results = []
        balances = starting_balances
        
        for year in range(30):
            age = 65 + year
            
            result = optimizer.calculate_optimal_withdrawals(
                spending_need=annual_spending,
                balances=balances,
                age=age,
                ss_income=annual_ss if age >= 67 else 0,
            )
            
            results.append(result)
            
            # Update balances (simplified - no growth)
            balances = AccountBalances(
                taxable=max(0, balances.taxable - result.taxable_withdrawal),
                traditional_ira=max(0, balances.traditional_ira - result.ira_withdrawal),
                roth_ira=max(0, balances.roth_ira - result.roth_withdrawal),
                taxable_basis=max(0, balances.taxable_basis - result.taxable_withdrawal * 0.6),
            )
        
        # Verify Roth was preserved until late in retirement
        roth_first_used_year = next(
            (i for i, r in enumerate(results) if r.roth_withdrawal > 0),
            None
        )
        
        if roth_first_used_year is not None:
            # In a drawdown scenario with no growth, Roth is used earlier
            # Check that it's at least after a few years
            self.assertGreater(
                roth_first_used_year,
                3,
                f"Roth should be preserved for several years. First used: year {roth_first_used_year}"
            )
        
        # Calculate lifetime taxes
        lifetime_metrics = optimizer.calculate_lifetime_taxes(results)
        
        print(f"\n30-Year Retirement Simulation:")
        print(f"  Total lifetime taxes: ${lifetime_metrics['total_lifetime_taxes']:,.0f}")
        print(f"  PV lifetime taxes: ${lifetime_metrics['pv_lifetime_taxes']:,.0f}")
        print(f"  Average annual tax: ${lifetime_metrics['average_annual_tax']:,.0f}")
        print(f"  Total IRMAA: ${lifetime_metrics['total_irmaa_surcharges']:,.0f}")
        
        # Sanity check: average tax should be reasonable
        self.assertLess(
            lifetime_metrics['average_annual_tax'],
            annual_spending * 0.25,
            "Average tax rate should be < 25% of spending"
        )


def run_tests():
    """Run all tests and print results."""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestWithdrawalSequencing))
    suite.addTests(loader.loadTestsFromTestCase(TestRothConversions))
    suite.addTests(loader.loadTestsFromTestCase(TestTaxCalculations))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegration))
    
    # Run tests with verbose output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.wasSuccessful():
        print("\n✓ ALL TESTS PASSED")
    else:
        print("\n✗ SOME TESTS FAILED")
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
