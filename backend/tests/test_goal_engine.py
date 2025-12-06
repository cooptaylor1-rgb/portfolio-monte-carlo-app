"""
Test suite for goal-based planning engine.

Tests:
- Single goal simulation
- Multiple goals with different priorities
- Goal conflicts and resolution
- Glide path functionality
- Funding recommendations
- Edge cases (past goals, zero funding)

Author: Salem Investment Counselors
Last Updated: December 2024
"""

import pytest
import numpy as np
import sys
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from core.goal_engine import (
    FinancialGoal,
    GoalEngine,
    GoalPriority,
    GoalStatus,
    GoalResult
)


class TestGoalSimulation:
    """Test Monte Carlo simulation for individual goals"""
    
    def test_single_goal_simulation(self):
        """Test basic goal simulation returns valid result"""
        engine = GoalEngine(current_year=2024, n_scenarios=1000)
        
        goal = FinancialGoal(
            name="Test Goal",
            target_amount=100000,
            target_year=2034,
            current_funding=50000,
            annual_contribution=5000,
            equity_pct=0.60,
        )
        
        result = engine.simulate_goal(goal, seed=42)
        
        # Basic validation
        assert isinstance(result, GoalResult)
        assert 0 <= result.probability_of_success <= 1.0
        assert result.median_value_at_target > 0
        assert result.percentile_10_value <= result.median_value_at_target <= result.percentile_90_value
        assert result.scenarios_succeeded + result.scenarios_failed == 1000
    
    def test_well_funded_goal_has_high_probability(self):
        """Test that overfunded goal shows high probability of success"""
        engine = GoalEngine(current_year=2024, n_scenarios=1000)
        
        goal = FinancialGoal(
            name="Well Funded Goal",
            target_amount=100000,
            target_year=2029,  # 5 years
            current_funding=80000,  # Already 80% funded
            annual_contribution=5000,  # Plus $5k/year
            equity_pct=0.60,
        )
        
        result = engine.simulate_goal(goal, seed=42)
        
        assert result.probability_of_success >= 0.85
        assert result.status == GoalStatus.ON_TRACK
        assert result.additional_funding_needed == 0.0
    
    def test_underfunded_goal_shows_shortfall(self):
        """Test that underfunded goal correctly identifies shortfall"""
        engine = GoalEngine(current_year=2024, n_scenarios=1000)
        
        goal = FinancialGoal(
            name="Underfunded Goal",
            target_amount=500000,
            target_year=2029,  # 5 years
            current_funding=50000,  # Only 10% funded
            annual_contribution=10000,  # Not enough
            equity_pct=0.60,
        )
        
        result = engine.simulate_goal(goal, seed=42)
        
        assert result.probability_of_success < 0.50
        assert result.status in [GoalStatus.UNDERFUNDED, GoalStatus.CRITICAL]
        assert result.additional_funding_needed > 0
        assert result.expected_shortfall > 0
    
    def test_zero_contribution_goal(self):
        """Test goal with no future contributions"""
        engine = GoalEngine(current_year=2024, n_scenarios=1000)
        
        goal = FinancialGoal(
            name="No Contributions",
            target_amount=200000,
            target_year=2044,  # 20 years
            current_funding=100000,
            annual_contribution=0,  # No contributions
            equity_pct=0.60,
        )
        
        result = engine.simulate_goal(goal, seed=42)
        
        # Should still simulate growth
        assert result.median_value_at_target > 100000  # Should grow
        assert isinstance(result.probability_of_success, float)


class TestGlidePath:
    """Test goal-specific glide path functionality"""
    
    def test_glide_path_reduces_equity_near_goal(self):
        """Test that glide path reduces equity allocation as goal approaches"""
        goal = FinancialGoal(
            name="Glide Path Test",
            target_amount=100000,
            target_year=2034,
            equity_pct=0.70,
            use_glide_path=True,
            years_before_goal_to_derisk=5,
            target_equity_at_goal=0.20,
        )
        
        # Far from goal - should use original allocation
        eq_far, fi_far, cash_far = goal.get_allocation_for_year(2024)
        assert eq_far == 0.70
        
        # 5 years before goal - should start reducing
        eq_5yr, fi_5yr, cash_5yr = goal.get_allocation_for_year(2029)
        assert eq_5yr == 0.70  # Just at start of glide path
        
        # 2 years before goal - should be lower
        eq_2yr, fi_2yr, cash_2yr = goal.get_allocation_for_year(2032)
        assert eq_2yr < 0.70
        assert eq_2yr > 0.20
        
        # At goal - should use target allocation
        eq_at, fi_at, cash_at = goal.get_allocation_for_year(2034)
        assert eq_at == 0.20
    
    def test_glide_path_disabled(self):
        """Test that glide path can be disabled"""
        goal = FinancialGoal(
            name="No Glide Path",
            target_amount=100000,
            target_year=2034,
            equity_pct=0.70,
            use_glide_path=False,
        )
        
        # Should always return same allocation
        eq_2024, _, _ = goal.get_allocation_for_year(2024)
        eq_2033, _, _ = goal.get_allocation_for_year(2033)
        eq_2034, _, _ = goal.get_allocation_for_year(2034)
        
        assert eq_2024 == eq_2033 == eq_2034 == 0.70
    
    def test_glide_path_in_simulation(self):
        """Test that glide path affects simulation results"""
        engine = GoalEngine(current_year=2024, n_scenarios=1000)
        
        # Goal with glide path
        goal_with_glide = FinancialGoal(
            name="With Glide Path",
            target_amount=300000,
            target_year=2034,
            current_funding=200000,
            annual_contribution=5000,
            equity_pct=0.70,
            use_glide_path=True,
            years_before_goal_to_derisk=5,
        )
        
        # Goal without glide path
        goal_without_glide = FinancialGoal(
            name="Without Glide Path",
            target_amount=300000,
            target_year=2034,
            current_funding=200000,
            annual_contribution=5000,
            equity_pct=0.70,
            use_glide_path=False,
        )
        
        result_with = engine.simulate_goal(goal_with_glide, seed=42)
        result_without = engine.simulate_goal(goal_without_glide, seed=42)
        
        # With glide path should have lower volatility (smaller range)
        range_with = result_with.percentile_90_value - result_with.percentile_10_value
        range_without = result_without.percentile_90_value - result_without.percentile_10_value
        
        assert range_with < range_without


class TestMultipleGoals:
    """Test handling multiple goals with different priorities"""
    
    def test_multiple_goals_simulation(self):
        """Test simulating multiple goals at once"""
        engine = GoalEngine(current_year=2024, n_scenarios=1000)
        
        goal1 = FinancialGoal(
            name="Retirement",
            target_amount=2000000,
            target_year=2044,
            current_funding=1000000,
            annual_contribution=50000,
            priority=GoalPriority.CRITICAL,
        )
        
        goal2 = FinancialGoal(
            name="College",
            target_amount=200000,
            target_year=2034,
            current_funding=100000,
            annual_contribution=10000,
            priority=GoalPriority.HIGH,
        )
        
        engine.add_goal(goal1)
        engine.add_goal(goal2)
        
        results = engine.simulate_all_goals(seed=42)
        
        assert len(results) == 2
        assert all(isinstance(r, GoalResult) for r in results)
    
    def test_goal_prioritization(self):
        """Test that goal priorities are tracked correctly"""
        engine = GoalEngine(current_year=2024, n_scenarios=100)
        
        critical_goal = FinancialGoal(
            name="Critical",
            target_amount=1000000,
            target_year=2044,
            priority=GoalPriority.CRITICAL,
            current_funding=500000,
            annual_contribution=20000,
        )
        
        medium_goal = FinancialGoal(
            name="Medium",
            target_amount=1000000,
            target_year=2044,
            priority=GoalPriority.MEDIUM,
            current_funding=500000,
            annual_contribution=20000,
        )
        
        engine.add_goal(critical_goal)
        engine.add_goal(medium_goal)
        
        # Both should simulate independently
        results = engine.simulate_all_goals(seed=42)
        
        critical_result = next(r for r in results if r.goal.name == "Critical")
        medium_result = next(r for r in results if r.goal.name == "Medium")
        
        assert critical_result.goal.priority == GoalPriority.CRITICAL
        assert medium_result.goal.priority == GoalPriority.MEDIUM


class TestGoalConflicts:
    """Test goal conflict detection and resolution"""
    
    def test_near_term_conflict_detection(self):
        """Test detection of multiple near-term goals"""
        engine = GoalEngine(current_year=2024, n_scenarios=100)
        
        # Two goals both due in 3 years
        goal1 = FinancialGoal(
            name="Goal 1",
            target_amount=100000,
            target_year=2027,
            current_funding=30000,
            annual_contribution=10000,
        )
        
        goal2 = FinancialGoal(
            name="Goal 2",
            target_amount=100000,
            target_year=2028,
            current_funding=30000,
            annual_contribution=10000,
        )
        
        engine.add_goal(goal1)
        engine.add_goal(goal2)
        
        # Simulate to populate results
        engine.simulate_all_goals(seed=42)
        
        conflicts = engine.check_goal_conflicts()
        
        # Should detect funding competition
        assert len(conflicts) > 0
        assert any(c['type'] == 'funding_competition' for c in conflicts)
    
    def test_critical_goal_at_risk_detection(self):
        """Test detection of critical goal that's underfunded"""
        engine = GoalEngine(current_year=2024, n_scenarios=500)
        
        # Critical goal that's severely underfunded
        critical_goal = FinancialGoal(
            name="Critical Goal",
            target_amount=1000000,
            target_year=2029,  # 5 years
            current_funding=100000,  # Only 10%
            annual_contribution=10000,  # Far too little
            priority=GoalPriority.CRITICAL,
        )
        
        engine.add_goal(critical_goal)
        engine.simulate_all_goals(seed=42)
        
        conflicts = engine.check_goal_conflicts()
        
        # Should flag critical goal at risk
        assert len(conflicts) > 0
        critical_conflict = next(
            (c for c in conflicts if c['type'] == 'critical_goal_at_risk'),
            None
        )
        assert critical_conflict is not None
        assert 'Critical Goal' in critical_conflict['goals_affected']
    
    def test_no_conflicts_when_goals_on_track(self):
        """Test that well-funded goals don't trigger conflicts"""
        engine = GoalEngine(current_year=2024, n_scenarios=500)
        
        # Well-funded goal
        goal = FinancialGoal(
            name="Well Funded",
            target_amount=100000,
            target_year=2034,
            current_funding=80000,
            annual_contribution=5000,
            priority=GoalPriority.CRITICAL,
        )
        
        engine.add_goal(goal)
        engine.simulate_all_goals(seed=42)
        
        conflicts = engine.check_goal_conflicts()
        
        # Should have minimal or no conflicts
        critical_conflicts = [c for c in conflicts if c['type'] == 'critical_goal_at_risk']
        assert len(critical_conflicts) == 0


class TestEdgeCases:
    """Test edge cases and error handling"""
    
    def test_past_goal_achieved(self):
        """Test handling of goal whose date has passed but is fully funded"""
        engine = GoalEngine(current_year=2024, n_scenarios=100)
        
        goal = FinancialGoal(
            name="Past Goal",
            target_amount=100000,
            target_year=2020,  # 4 years ago
            current_funding=150000,  # Overfunded
        )
        
        result = engine.simulate_goal(goal, seed=42)
        
        assert result.status == GoalStatus.ACHIEVED
        assert result.probability_of_success == 1.0
    
    def test_past_goal_not_achieved(self):
        """Test handling of goal whose date has passed and is underfunded"""
        engine = GoalEngine(current_year=2024, n_scenarios=100)
        
        goal = FinancialGoal(
            name="Missed Goal",
            target_amount=100000,
            target_year=2020,  # 4 years ago
            current_funding=50000,  # Underfunded
        )
        
        result = engine.simulate_goal(goal, seed=42)
        
        assert result.status == GoalStatus.CRITICAL
        assert result.probability_of_success == 0.0
        assert result.expected_shortfall == 50000
    
    def test_goal_due_this_year(self):
        """Test goal due in current year"""
        engine = GoalEngine(current_year=2024, n_scenarios=100)
        
        goal = FinancialGoal(
            name="Due Now",
            target_amount=100000,
            target_year=2024,
            current_funding=100000,
        )
        
        result = engine.simulate_goal(goal, seed=42)
        
        # Should handle gracefully
        assert isinstance(result, GoalResult)
    
    def test_very_long_time_horizon(self):
        """Test goal with very long time horizon (40+ years)"""
        engine = GoalEngine(current_year=2024, n_scenarios=1000)
        
        goal = FinancialGoal(
            name="Long Term Goal",
            target_amount=5000000,
            target_year=2064,  # 40 years
            current_funding=100000,
            annual_contribution=10000,
            equity_pct=0.80,
        )
        
        result = engine.simulate_goal(goal, seed=42)
        
        # Should complete without error
        assert isinstance(result, GoalResult)
        assert result.median_value_at_target > 100000  # Should grow significantly
    
    def test_zero_current_funding(self):
        """Test goal starting from zero"""
        engine = GoalEngine(current_year=2024, n_scenarios=500)
        
        goal = FinancialGoal(
            name="Starting From Zero",
            target_amount=100000,
            target_year=2034,
            current_funding=0,
            annual_contribution=8000,
            equity_pct=0.60,
        )
        
        result = engine.simulate_goal(goal, seed=42)
        
        assert isinstance(result, GoalResult)
        assert result.median_value_at_target > 0


class TestRecommendations:
    """Test funding recommendation calculations"""
    
    def test_on_track_goal_needs_no_additional_funding(self):
        """Test that on-track goals don't recommend additional funding"""
        engine = GoalEngine(current_year=2024, n_scenarios=1000)
        
        goal = FinancialGoal(
            name="On Track",
            target_amount=100000,
            target_year=2029,
            current_funding=70000,
            annual_contribution=6000,
        )
        
        result = engine.simulate_goal(goal, seed=42)
        
        if result.status == GoalStatus.ON_TRACK:
            assert result.additional_funding_needed == 0.0
            assert "On track" in result.recommendation
    
    def test_underfunded_goal_recommends_additional_funding(self):
        """Test that underfunded goals recommend additional contributions"""
        engine = GoalEngine(current_year=2024, n_scenarios=1000)
        
        goal = FinancialGoal(
            name="Underfunded",
            target_amount=500000,
            target_year=2029,
            current_funding=50000,
            annual_contribution=10000,
        )
        
        result = engine.simulate_goal(goal, seed=42)
        
        if result.status in [GoalStatus.UNDERFUNDED, GoalStatus.CRITICAL]:
            assert result.additional_funding_needed > 0
            assert "Increase" in result.recommendation or "reduce goal" in result.recommendation.lower()
    
    def test_recommendation_includes_alternatives(self):
        """Test that recommendations include reducing goal amount as alternative"""
        engine = GoalEngine(current_year=2024, n_scenarios=1000)
        
        goal = FinancialGoal(
            name="Test Goal",
            target_amount=500000,
            target_year=2029,
            current_funding=100000,
            annual_contribution=15000,
        )
        
        result = engine.simulate_goal(goal, seed=42)
        
        if result.additional_funding_needed > 0:
            # Should suggest either increase contributions OR reduce goal
            assert "Increase" in result.recommendation or "reduce goal" in result.recommendation.lower()


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "--tb=short"])
