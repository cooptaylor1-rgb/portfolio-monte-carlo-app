#!/usr/bin/env python3
"""
Quick verification script for report generator
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import numpy as np
from core.report_generator import (
    NarrativeEngine,
    RiskAnalyzer,
    RecommendationEngine,
    FailureAnalyzer,
    WorstCaseAnalyzer
)

print("Testing Report Generator Components...")
print("=" * 60)

# Test 1: NarrativeEngine
print("\n1. Testing NarrativeEngine...")
engine = NarrativeEngine()
summary = engine.generate_executive_summary(
    success_probability=0.85,
    median_ending_value=2000000,
    percentile_10_value=800000,
    percentile_90_value=4000000,
    starting_portfolio=1500000,
    years_to_model=30,
    current_age=65,
    monthly_spending=-7000,
    has_goals=False,
    goals_on_track_count=0,
    total_goals=0
)
print(f"✓ Executive Summary Generated ({len(summary.plan_overview)} chars)")
print(f"  Success Narrative: {summary.success_probability_narrative[:80]}...")
print(f"  Strengths: {len(summary.key_strengths)}")
print(f"  Concerns: {len(summary.key_concerns)}")

# Test 2: RiskAnalyzer
print("\n2. Testing RiskAnalyzer...")
analyzer = RiskAnalyzer()
risks = analyzer.identify_risks(
    success_probability=0.85,
    median_ending=2000000,
    percentile_10=800000,
    failure_scenarios=np.array([]),
    starting_portfolio=1500000,
    annual_spending=84000,
    years_to_model=30,
    current_age=65,
    horizon_age=95,
    equity_pct=0.60,
    monthly_spending=-7000
)
print(f"✓ Identified {len(risks)} risks")
for i, risk in enumerate(risks[:3], 1):
    print(f"  {i}. {risk.risk_type.value}: {risk.severity.value}")

# Test 3: RecommendationEngine
print("\n3. Testing RecommendationEngine...")
rec_engine = RecommendationEngine()
recommendations = rec_engine.generate_recommendations(
    risks=risks,
    success_probability=0.85,
    starting_portfolio=1500000,
    annual_spending=84000,
    equity_pct=0.60,
    years_to_model=30
)
print(f"✓ Generated {len(recommendations)} recommendations")
for i, rec in enumerate(recommendations[:3], 1):
    print(f"  {i}. {rec.title} (Priority: {rec.priority})")

# Test 4: FailureAnalyzer
print("\n4. Testing FailureAnalyzer...")
failure_analyzer = FailureAnalyzer()

# Create synthetic paths with some failures
np.random.seed(42)
all_paths = []
for i in range(100):
    if i < 85:  # Successful
        path = np.linspace(1500000, np.random.uniform(1000000, 3000000), 30)
    else:  # Failed
        failure_year = np.random.randint(15, 25)
        path = np.concatenate([
            np.linspace(1500000, 100000, failure_year),
            np.zeros(30 - failure_year)
        ])
    all_paths.append(path)

all_paths = np.array(all_paths)

failure_analysis = failure_analyzer.analyze_failures(
    all_paths=all_paths,
    success_threshold=0,
    years_to_model=30,
    starting_portfolio=1500000,
    annual_spending=84000
)
print(f"✓ Analyzed failures: {failure_analysis['failure_count']}/{len(all_paths)}")
print(f"  Failure rate: {failure_analysis['failure_rate']:.1%}")
print(f"  Patterns identified: {len(failure_analysis['patterns'])}")

# Test 5: WorstCaseAnalyzer
print("\n5. Testing WorstCaseAnalyzer...")
worst_case_analyzer = WorstCaseAnalyzer()
worst_case = worst_case_analyzer.analyze_worst_case(
    all_paths=all_paths,
    percentile_10_value=800000,
    starting_portfolio=1500000,
    annual_spending=84000,
    years_to_model=30
)
print(f"✓ Worst-case analysis complete")
print(f"  10th percentile value: ${worst_case['percentile_10_value']:,.0f}")
print(f"  Max drawdown: {worst_case['max_drawdown_pct']:.1f}%")
print(f"  What-if scenarios: {len(worst_case['what_if_scenarios'])}")

print("\n" + "=" * 60)
print("✓ ALL TESTS PASSED - Report Generator is operational!")
print("=" * 60)
