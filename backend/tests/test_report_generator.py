"""
Unit Tests for Enhanced Report Generator

Tests cover:
1. NarrativeEngine: Executive summary generation
2. RiskAnalyzer: Risk identification with severity scoring
3. RecommendationEngine: Actionable recommendation generation
4. FailureAnalyzer: Failure pattern detection
5. WorstCaseAnalyzer: 10th percentile deep-dive analysis
6. API integration: /reports/narrative endpoint
"""

import unittest
import sys
import os
import numpy as np
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from core.report_generator import (
    NarrativeEngine,
    RiskAnalyzer,
    RecommendationEngine,
    FailureAnalyzer,
    WorstCaseAnalyzer,
    RiskLevel,
    RiskType,
)


class TestNarrativeEngine(unittest.TestCase):
    """Test executive summary generation."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.engine = NarrativeEngine()
    
    def test_executive_summary_high_success(self):
        """Test summary generation for high success probability."""
        summary = self.engine.generate_executive_summary(
            success_probability=0.92,
            median_ending_value=3500000,
            percentile_10_value=2000000,
            percentile_90_value=6000000,
            starting_portfolio=2000000,
            years_to_model=30,
            current_age=65,
            monthly_spending=-8000,
            has_goals=False,
            goals_on_track_count=0,
            total_goals=0
        )
        
        # Validate structure
        self.assertIsNotNone(summary.plan_overview)
        self.assertIsNotNone(summary.success_probability_narrative)
        self.assertIsInstance(summary.key_strengths, list)
        self.assertIsInstance(summary.key_concerns, list)
        self.assertIsNotNone(summary.bottom_line)
        
        # Validate content quality
        self.assertGreater(len(summary.plan_overview), 100)
        self.assertIn("92%", summary.success_probability_narrative)
        self.assertGreater(len(summary.key_strengths), 0)
        self.assertIn("comfortable", summary.bottom_line.lower())
    
    def test_executive_summary_moderate_success(self):
        """Test summary for moderate success probability."""
        summary = self.engine.generate_executive_summary(
            success_probability=0.75,
            median_ending_value=1200000,
            percentile_10_value=100000,
            percentile_90_value=3000000,
            starting_portfolio=1500000,
            years_to_model=30,
            current_age=60,
            monthly_spending=-6000,
            has_goals=True,
            goals_on_track_count=2,
            total_goals=3
        )
        
        # Should have both strengths and concerns
        self.assertGreater(len(summary.key_strengths), 0)
        self.assertGreater(len(summary.key_concerns), 0)
        self.assertIn("75%", summary.success_probability_narrative)
    
    def test_executive_summary_low_success(self):
        """Test summary for low success probability."""
        summary = self.engine.generate_executive_summary(
            success_probability=0.45,
            median_ending_value=0,
            percentile_10_value=0,
            percentile_90_value=800000,
            starting_portfolio=800000,
            years_to_model=35,
            current_age=65,
            monthly_spending=-5000,
            has_goals=False,
            goals_on_track_count=0,
            total_goals=0
        )
        
        # Should have concerns
        self.assertGreater(len(summary.key_concerns), 0)
        self.assertIn("45%", summary.success_probability_narrative)
        self.assertIn("adjustment", summary.bottom_line.lower())
    
    def test_executive_summary_with_goals(self):
        """Test summary with goal tracking."""
        summary = self.engine.generate_executive_summary(
            success_probability=0.85,
            median_ending_value=2000000,
            percentile_10_value=800000,
            percentile_90_value=4000000,
            starting_portfolio=1500000,
            years_to_model=25,
            current_age=62,
            monthly_spending=-7000,
            has_goals=True,
            goals_on_track_count=4,
            total_goals=5
        )
        
        # Should mention goals
        overview_lower = summary.plan_overview.lower()
        self.assertTrue("goal" in overview_lower or "4 of 5" in overview_lower)


class TestRiskAnalyzer(unittest.TestCase):
    """Test risk identification and severity scoring."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.analyzer = RiskAnalyzer()
    
    def test_identify_risks_high_success(self):
        """Test risk identification for high success plan."""
        risks = self.analyzer.identify_risks(
            success_probability=0.90,
            median_ending=3000000,
            percentile_10=1500000,
            failure_scenarios=np.array([]),
            starting_portfolio=2000000,
            annual_spending=96000,
            years_to_model=30,
            current_age=65,
            horizon_age=95,
            equity_pct=0.60,
            monthly_spending=-8000
        )
        
        # Should identify some risks even for strong plan
        self.assertGreater(len(risks), 0)
        self.assertLessEqual(len(risks), 5)  # Top 5 risks
        
        # Validate risk structure
        for risk in risks:
            self.assertIn(risk.risk_type, [r for r in RiskType])
            self.assertIn(risk.severity, [r for r in RiskLevel])
            self.assertGreater(risk.probability, 0.0)
            self.assertLessEqual(risk.probability, 1.0)
            self.assertIsNotNone(risk.description)
            self.assertIsNotNone(risk.mitigation_strategy)
            self.assertGreater(risk.priority_rank, 0)
        
        # Most severe risk should be first
        if len(risks) > 1:
            self.assertLessEqual(risks[0].priority_rank, risks[-1].priority_rank)
    
    def test_identify_risks_low_success(self):
        """Test risk identification for struggling plan."""
        risks = self.analyzer.identify_risks(
            success_probability=0.50,
            median_ending=0,
            percentile_10=0,
            failure_scenarios=np.array([]),
            starting_portfolio=800000,
            annual_spending=60000,
            years_to_model=35,
            current_age=65,
            horizon_age=100,
            equity_pct=0.40,
            monthly_spending=-5000
        )
        
        # Should identify multiple high-severity risks
        self.assertGreater(len(risks), 2)
        
        # Should have at least one HIGH or CRITICAL risk
        severities = [risk.severity for risk in risks]
        self.assertTrue(
            RiskLevel.HIGH in severities or RiskLevel.CRITICAL in severities
        )
        
        # Should identify portfolio depletion risk
        risk_types = [risk.risk_type for risk in risks]
        self.assertIn(RiskType.PORTFOLIO_DEPLETION, risk_types)
    
    def test_sequence_of_returns_risk(self):
        """Test sequence of returns risk detection."""
        risks = self.analyzer.identify_risks(
            success_probability=0.72,
            median_ending=1200000,
            percentile_10=200000,
            failure_scenarios=np.array([]),
            starting_portfolio=1500000,
            annual_spending=84000,
            years_to_model=30,
            current_age=62,
            horizon_age=92,
            equity_pct=0.70,
            monthly_spending=-7000
        )
        
        # High equity early in retirement should trigger sequence risk
        risk_types = [risk.risk_type for risk in risks]
        self.assertIn(RiskType.SEQUENCE_OF_RETURNS, risk_types)
    
    def test_longevity_risk(self):
        """Test longevity risk detection."""
        risks = self.analyzer.identify_risks(
            success_probability=0.80,
            median_ending=500000,
            percentile_10=50000,
            failure_scenarios=np.array([]),
            starting_portfolio=1000000,
            annual_spending=60000,
            years_to_model=40,
            current_age=60,
            horizon_age=100,
            equity_pct=0.50,
            monthly_spending=-5000
        )
        
        # Long horizon (40 years) should trigger longevity risk
        risk_types = [risk.risk_type for risk in risks]
        self.assertIn(RiskType.LONGEVITY, risk_types)
    
    def test_spending_unsustainable_risk(self):
        """Test spending sustainability risk detection."""
        risks = self.analyzer.identify_risks(
            success_probability=0.55,
            median_ending=200000,
            percentile_10=0,
            failure_scenarios=np.array([]),
            starting_portfolio=1000000,
            annual_spending=80000,
            years_to_model=30,
            current_age=65,
            horizon_age=95,
            equity_pct=0.50,
            monthly_spending=-6667
        )
        
        # 8% withdrawal rate should trigger spending risk
        risk_types = [risk.risk_type for risk in risks]
        self.assertIn(RiskType.SPENDING_UNSUSTAINABLE, risk_types)


class TestRecommendationEngine(unittest.TestCase):
    """Test recommendation generation."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.engine = RecommendationEngine()
        self.analyzer = RiskAnalyzer()
    
    def test_generate_recommendations_from_risks(self):
        """Test recommendation generation from identified risks."""
        # First identify risks
        risks = self.analyzer.identify_risks(
            success_probability=0.65,
            median_ending=800000,
            percentile_10=100000,
            failure_scenarios=np.array([]),
            starting_portfolio=1200000,
            annual_spending=72000,
            years_to_model=30,
            current_age=65,
            horizon_age=95,
            equity_pct=0.65,
            monthly_spending=-6000
        )
        
        # Generate recommendations
        recommendations = self.engine.generate_recommendations(
            risks=risks,
            success_probability=0.65,
            starting_portfolio=1200000,
            annual_spending=72000,
            equity_pct=0.65,
            years_to_model=30
        )
        
        # Validate structure
        self.assertGreater(len(recommendations), 0)
        self.assertLessEqual(len(recommendations), 8)
        
        for rec in recommendations:
            self.assertIsNotNone(rec.title)
            self.assertIsNotNone(rec.description)
            self.assertIsNotNone(rec.expected_benefit)
            self.assertIsInstance(rec.implementation_steps, list)
            self.assertGreater(len(rec.implementation_steps), 0)
            self.assertIsNotNone(rec.priority)
            self.assertIsNotNone(rec.category)
        
        # Should be prioritized
        if len(recommendations) > 1:
            priorities = [rec.priority for rec in recommendations]
            # At least first should be high priority
            self.assertIn("High", priorities[0])
    
    def test_recommendations_actionable(self):
        """Test that recommendations have concrete implementation steps."""
        risks = self.analyzer.identify_risks(
            success_probability=0.70,
            median_ending=1000000,
            percentile_10=200000,
            failure_scenarios=np.array([]),
            starting_portfolio=1500000,
            annual_spending=84000,
            years_to_model=30,
            current_age=62,
            horizon_age=92,
            equity_pct=0.70,
            monthly_spending=-7000
        )
        
        recommendations = self.engine.generate_recommendations(
            risks=risks,
            success_probability=0.70,
            starting_portfolio=1500000,
            annual_spending=84000,
            equity_pct=0.70,
            years_to_model=30
        )
        
        # Each recommendation should have multiple steps
        for rec in recommendations:
            self.assertGreaterEqual(len(rec.implementation_steps), 2)
            # Steps should be specific (contain numbers or concrete actions)
            steps_text = " ".join(rec.implementation_steps).lower()
            self.assertTrue(
                any(keyword in steps_text for keyword in [
                    "reduce", "increase", "consider", "implement",
                    "review", "adjust", "target", "%", "$"
                ])
            )


class TestFailureAnalyzer(unittest.TestCase):
    """Test failure pattern detection."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.analyzer = FailureAnalyzer()
    
    def test_analyze_failures_with_failures(self):
        """Test failure analysis with failed scenarios."""
        # Create synthetic paths with some failures
        np.random.seed(42)
        all_paths = []
        
        # 70 successful paths
        for _ in range(70):
            path = np.linspace(1000000, np.random.uniform(800000, 2000000), 30)
            all_paths.append(path)
        
        # 30 failed paths (early, mid, late failures)
        # Early failures (years 5-10)
        for _ in range(10):
            failure_year = np.random.randint(5, 11)
            path = np.concatenate([
                np.linspace(1000000, 200000, failure_year),
                np.zeros(30 - failure_year)
            ])
            all_paths.append(path)
        
        # Mid failures (years 15-20)
        for _ in range(10):
            failure_year = np.random.randint(15, 21)
            path = np.concatenate([
                np.linspace(1000000, 200000, failure_year),
                np.zeros(30 - failure_year)
            ])
            all_paths.append(path)
        
        # Late failures (years 25-30)
        for _ in range(10):
            failure_year = np.random.randint(25, 30)
            path = np.concatenate([
                np.linspace(1000000, 200000, failure_year),
                np.zeros(30 - failure_year)
            ])
            all_paths.append(path)
        
        all_paths = np.array(all_paths)
        
        # Run analysis
        analysis = self.analyzer.analyze_failures(
            all_paths=all_paths,
            success_threshold=0,
            years_to_model=30,
            starting_portfolio=1000000,
            annual_spending=60000
        )
        
        # Validate structure
        self.assertIn('failure_count', analysis)
        self.assertIn('failure_rate', analysis)
        self.assertIn('patterns', analysis)
        self.assertIn('summary', analysis)
        self.assertIn('prevention_strategies', analysis)
        
        # Validate values
        self.assertEqual(analysis['failure_count'], 30)
        self.assertAlmostEqual(analysis['failure_rate'], 0.30, places=2)
        self.assertGreater(len(analysis['patterns']), 0)
        self.assertGreater(len(analysis['prevention_strategies']), 0)
        
        # Should identify patterns
        pattern_names = [p.pattern_name for p in analysis['patterns']]
        self.assertTrue(any("Early" in name or "Mid" in name or "Late" in name 
                          for name in pattern_names))
    
    def test_analyze_failures_no_failures(self):
        """Test failure analysis with no failures."""
        # All successful paths
        np.random.seed(42)
        all_paths = []
        for _ in range(100):
            path = np.linspace(1000000, np.random.uniform(1500000, 3000000), 30)
            all_paths.append(path)
        
        all_paths = np.array(all_paths)
        
        analysis = self.analyzer.analyze_failures(
            all_paths=all_paths,
            success_threshold=0,
            years_to_model=30,
            starting_portfolio=1000000,
            annual_spending=60000
        )
        
        # Should handle gracefully
        self.assertEqual(analysis['failure_count'], 0)
        self.assertEqual(analysis['failure_rate'], 0.0)
        self.assertEqual(len(analysis['patterns']), 0)
        self.assertIn("no failures", analysis['summary'].lower())


class TestWorstCaseAnalyzer(unittest.TestCase):
    """Test worst-case (10th percentile) analysis."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.analyzer = WorstCaseAnalyzer()
    
    def test_analyze_worst_case_with_recovery(self):
        """Test worst-case analysis with recovery."""
        np.random.seed(42)
        
        # Create synthetic 10th percentile path with drawdown and recovery
        worst_path = np.concatenate([
            np.linspace(1000000, 400000, 8),  # Drawdown years 0-7
            np.linspace(400000, 600000, 12),  # Recovery years 8-19
            np.linspace(600000, 800000, 10)   # Stabilization years 20-29
        ])
        
        all_paths = np.array([worst_path] * 100)  # Simplified
        
        analysis = self.analyzer.analyze_worst_case(
            all_paths=all_paths,
            percentile_10_value=800000,
            starting_portfolio=1000000,
            annual_spending=60000,
            years_to_model=30
        )
        
        # Validate structure
        self.assertIn('percentile_10_value', analysis)
        self.assertIn('max_drawdown_pct', analysis)
        self.assertIn('turning_point_year', analysis)
        self.assertIn('recovery_time_years', analysis)
        self.assertIn('description', analysis)
        self.assertIn('recovery_strategies', analysis)
        self.assertIn('what_if_scenarios', analysis)
        
        # Validate values
        self.assertEqual(analysis['percentile_10_value'], 800000)
        self.assertGreater(analysis['max_drawdown_pct'], 0)
        self.assertGreater(analysis['turning_point_year'], 0)
        self.assertGreater(len(analysis['recovery_strategies']), 0)
        self.assertGreater(len(analysis['what_if_scenarios']), 0)
        
        # What-if scenarios should have structure
        for scenario in analysis['what_if_scenarios']:
            self.assertIn('scenario', scenario)
            self.assertIn('change', scenario)
            self.assertIn('impact', scenario)
            self.assertIn('trade_off', scenario)
    
    def test_analyze_worst_case_no_recovery(self):
        """Test worst-case analysis with depletion."""
        # Create path that depletes
        worst_path = np.linspace(800000, 0, 30)
        all_paths = np.array([worst_path] * 100)
        
        analysis = self.analyzer.analyze_worst_case(
            all_paths=all_paths,
            percentile_10_value=0,
            starting_portfolio=800000,
            annual_spending=50000,
            years_to_model=30
        )
        
        # Should identify depletion
        self.assertEqual(analysis['percentile_10_value'], 0)
        self.assertIn("depletion", analysis['description'].lower())
        self.assertGreater(len(analysis['recovery_strategies']), 0)


class TestIntegration(unittest.TestCase):
    """Test end-to-end integration of all components."""
    
    def test_full_report_generation_pipeline(self):
        """Test complete report generation workflow."""
        # Initialize all engines
        narrative_engine = NarrativeEngine()
        risk_analyzer = RiskAnalyzer()
        recommendation_engine = RecommendationEngine()
        failure_analyzer = FailureAnalyzer()
        worst_case_analyzer = WorstCaseAnalyzer()
        
        # Synthetic simulation results
        success_probability = 0.75
        starting_portfolio = 1500000
        median_ending = 1200000
        percentile_10 = 300000
        percentile_90 = 3000000
        annual_spending = 84000
        equity_pct = 0.60
        years_to_model = 30
        current_age = 65
        
        # Create synthetic paths
        np.random.seed(42)
        all_paths = []
        for i in range(100):
            if i < 75:  # Successful scenarios
                path = np.linspace(starting_portfolio, 
                                 np.random.uniform(800000, 3000000), 
                                 years_to_model)
            else:  # Failed scenarios
                failure_year = np.random.randint(15, 25)
                path = np.concatenate([
                    np.linspace(starting_portfolio, 100000, failure_year),
                    np.zeros(years_to_model - failure_year)
                ])
            all_paths.append(path)
        
        all_paths = np.array(all_paths)
        
        # 1. Generate executive summary
        executive_summary = narrative_engine.generate_executive_summary(
            success_probability=success_probability,
            median_ending_value=median_ending,
            percentile_10_value=percentile_10,
            percentile_90_value=percentile_90,
            starting_portfolio=starting_portfolio,
            years_to_model=years_to_model,
            current_age=current_age,
            monthly_spending=-7000,
            has_goals=False,
            goals_on_track_count=0,
            total_goals=0
        )
        
        self.assertIsNotNone(executive_summary)
        
        # 2. Identify risks
        risks = risk_analyzer.identify_risks(
            success_probability=success_probability,
            median_ending=median_ending,
            percentile_10=percentile_10,
            failure_scenarios=np.array([]),
            starting_portfolio=starting_portfolio,
            annual_spending=annual_spending,
            years_to_model=years_to_model,
            current_age=current_age,
            horizon_age=current_age + years_to_model,
            equity_pct=equity_pct,
            monthly_spending=-7000
        )
        
        self.assertGreater(len(risks), 0)
        
        # 3. Generate recommendations
        recommendations = recommendation_engine.generate_recommendations(
            risks=risks,
            success_probability=success_probability,
            starting_portfolio=starting_portfolio,
            annual_spending=annual_spending,
            equity_pct=equity_pct,
            years_to_model=years_to_model
        )
        
        self.assertGreater(len(recommendations), 0)
        
        # 4. Analyze failures
        failure_analysis = failure_analyzer.analyze_failures(
            all_paths=all_paths,
            success_threshold=0,
            years_to_model=years_to_model,
            starting_portfolio=starting_portfolio,
            annual_spending=annual_spending
        )
        
        self.assertIn('failure_count', failure_analysis)
        self.assertEqual(failure_analysis['failure_count'], 25)
        
        # 5. Analyze worst case
        worst_case = worst_case_analyzer.analyze_worst_case(
            all_paths=all_paths,
            percentile_10_value=percentile_10,
            starting_portfolio=starting_portfolio,
            annual_spending=annual_spending,
            years_to_model=years_to_model
        )
        
        self.assertIn('percentile_10_value', worst_case)
        
        # All components should integrate successfully
        self.assertTrue(True)


if __name__ == '__main__':
    unittest.main()
