"""
Goal-Based Planning Engine

Enables tracking of multiple financial goals with individual probabilities,
priority management, and goal-specific asset allocations.

Key Features:
- Separate Monte Carlo simulation per goal
- Goal-specific asset allocation and glide paths
- Priority-based resource allocation
- Conflict detection and resolution
- Funding recommendations

Author: Salem Investment Counselors
Last Updated: December 2024
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
from enum import Enum
import numpy as np
import logging

logger = logging.getLogger(__name__)


class GoalPriority(int, Enum):
    """Goal priority levels"""
    CRITICAL = 1  # Must-have (retirement income, healthcare)
    HIGH = 2      # Very important (education, home)
    MEDIUM = 3    # Nice-to-have (vacation home, travel)
    LOW = 4       # Aspirational (legacy, luxury items)


class GoalStatus(str, Enum):
    """Goal achievement status"""
    ON_TRACK = "on_track"          # >85% probability
    AT_RISK = "at_risk"            # 70-85% probability
    UNDERFUNDED = "underfunded"    # 50-70% probability
    CRITICAL = "critical"          # <50% probability
    ACHIEVED = "achieved"          # Already funded
    ABANDONED = "abandoned"        # Deprioritized


@dataclass
class FinancialGoal:
    """
    Individual financial goal with tracking parameters.
    
    Each goal can have its own asset allocation, funding schedule,
    and success criteria.
    """
    name: str
    target_amount: float
    target_year: int  # Absolute year (e.g., 2035)
    priority: GoalPriority = GoalPriority.MEDIUM
    
    # Funding
    current_funding: float = 0.0
    annual_contribution: float = 0.0
    contribution_start_year: int = field(default_factory=lambda: 2024)
    contribution_end_year: Optional[int] = None
    
    # Asset allocation for this goal (defaults to moderate)
    equity_pct: float = 0.60
    fi_pct: float = 0.35
    cash_pct: float = 0.05
    
    # Glide path: reduce equity as goal approaches
    use_glide_path: bool = True
    years_before_goal_to_derisk: int = 5  # Start reducing equity 5 years out
    target_equity_at_goal: float = 0.20   # 20% equity at goal date
    
    # Success criteria
    success_threshold: float = 0.85  # 85% probability = success
    acceptable_shortfall_pct: float = 0.10  # 10% shortfall acceptable
    
    # Tracking
    id: Optional[str] = None
    notes: str = ""
    
    def years_until_goal(self, current_year: int) -> int:
        """Calculate years remaining until goal."""
        return max(0, self.target_year - current_year)
    
    def is_near_term(self, current_year: int, threshold_years: int = 5) -> bool:
        """Check if goal is near-term (within threshold years)."""
        return self.years_until_goal(current_year) <= threshold_years
    
    def get_allocation_for_year(self, current_year: int) -> Tuple[float, float, float]:
        """
        Get asset allocation for current year, applying glide path if enabled.
        
        Returns: (equity_pct, fi_pct, cash_pct)
        """
        if not self.use_glide_path:
            return (self.equity_pct, self.fi_pct, self.cash_pct)
        
        years_remaining = self.years_until_goal(current_year)
        
        if years_remaining > self.years_before_goal_to_derisk:
            # Far from goal, use original allocation
            return (self.equity_pct, self.fi_pct, self.cash_pct)
        
        if years_remaining <= 0:
            # At or past goal, use target allocation
            return (self.target_equity_at_goal, 1.0 - self.target_equity_at_goal - 0.05, 0.05)
        
        # Linear glide path
        progress = 1.0 - (years_remaining / self.years_before_goal_to_derisk)
        equity = self.equity_pct - progress * (self.equity_pct - self.target_equity_at_goal)
        fi = 1.0 - equity - self.cash_pct
        
        return (equity, fi, self.cash_pct)


@dataclass
class GoalResult:
    """Result of goal-based simulation"""
    goal: FinancialGoal
    probability_of_success: float
    median_value_at_target: float
    percentile_10_value: float
    percentile_90_value: float
    expected_shortfall: float  # Expected $ shortfall in failure scenarios
    shortfall_probability: float
    
    # Status and recommendations
    status: GoalStatus
    current_funding_pct: float  # % of target currently funded
    additional_funding_needed: float  # Annual addition to reach 85% prob
    recommendation: str
    
    # Simulation details
    scenarios_succeeded: int
    scenarios_failed: int
    value_distribution: Optional[np.ndarray] = None


class GoalEngine:
    """
    Goal-based financial planning engine.
    
    Manages multiple goals, runs Monte Carlo simulations per goal,
    handles priority conflicts, and generates funding recommendations.
    """
    
    def __init__(
        self,
        current_year: int = 2024,
        default_equity_return: float = 0.07,
        default_fi_return: float = 0.02,
        default_cash_return: float = 0.0,
        default_equity_vol: float = 0.18,
        default_fi_vol: float = 0.06,
        default_cash_vol: float = 0.01,
        n_scenarios: int = 1000,
    ):
        """
        Initialize goal engine with market assumptions.
        
        Args:
            current_year: Current calendar year
            default_*_return: Default real returns by asset class
            default_*_vol: Default volatilities by asset class
            n_scenarios: Number of Monte Carlo scenarios to run
        """
        self.current_year = current_year
        self.equity_return = default_equity_return
        self.fi_return = default_fi_return
        self.cash_return = default_cash_return
        self.equity_vol = default_equity_vol
        self.fi_vol = default_fi_vol
        self.cash_vol = default_cash_vol
        self.n_scenarios = n_scenarios
        
        self.goals: List[FinancialGoal] = []
        self.results: Dict[str, GoalResult] = {}
    
    def add_goal(self, goal: FinancialGoal) -> None:
        """Add a goal to track."""
        if goal.id is None:
            goal.id = f"goal_{len(self.goals) + 1}"
        self.goals.append(goal)
        logger.info(f"Added goal: {goal.name} (${goal.target_amount:,.0f} by {goal.target_year})")
    
    def simulate_goal(
        self,
        goal: FinancialGoal,
        seed: Optional[int] = None,
    ) -> GoalResult:
        """
        Run Monte Carlo simulation for a single goal.
        
        Simulates goal-specific sub-portfolio growth with:
        - Annual contributions
        - Goal-specific asset allocation
        - Glide path (if enabled)
        - Stochastic returns
        
        Returns:
            GoalResult with probability and recommendations
        """
        if seed is not None:
            np.random.seed(seed)
        
        years = goal.years_until_goal(self.current_year)
        if years <= 0:
            # Goal date has passed or is now
            return self._handle_past_goal(goal)
        
        # Initialize scenarios
        values = np.full(self.n_scenarios, goal.current_funding, dtype=float)
        
        # Simulate year by year
        for year_idx in range(years):
            current_year = self.current_year + year_idx
            
            # Get allocation for this year (with glide path)
            eq_pct, fi_pct, cash_pct = goal.get_allocation_for_year(current_year)
            
            # Calculate annual portfolio return for each scenario
            # Generate correlated annual returns
            annual_return = (
                eq_pct * self.equity_return +
                fi_pct * self.fi_return +
                cash_pct * self.cash_return
            )
            annual_vol = np.sqrt(
                (eq_pct * self.equity_vol) ** 2 +
                (fi_pct * self.fi_vol) ** 2 +
                (cash_pct * self.cash_vol) ** 2
            )
            
            portfolio_returns = np.random.normal(
                annual_return,
                annual_vol,
                self.n_scenarios
            )
            
            # Apply annual returns
            values *= (1 + portfolio_returns)
            
            # Add annual contribution (if within funding period)
            if (goal.contribution_end_year is None or 
                current_year <= goal.contribution_end_year):
                if current_year >= goal.contribution_start_year:
                    values += goal.annual_contribution
        
        # Analyze results
        final_values = values
        succeeded = np.sum(final_values >= goal.target_amount)
        failed = self.n_scenarios - succeeded
        prob_success = succeeded / self.n_scenarios
        
        # Calculate shortfall in failure scenarios
        shortfall_scenarios = final_values[final_values < goal.target_amount]
        if len(shortfall_scenarios) > 0:
            expected_shortfall = np.mean(goal.target_amount - shortfall_scenarios)
            shortfall_prob = len(shortfall_scenarios) / self.n_scenarios
        else:
            expected_shortfall = 0.0
            shortfall_prob = 0.0
        
        # Determine status
        if prob_success >= goal.success_threshold:
            status = GoalStatus.ON_TRACK
        elif prob_success >= 0.70:
            status = GoalStatus.AT_RISK
        elif prob_success >= 0.50:
            status = GoalStatus.UNDERFUNDED
        else:
            status = GoalStatus.CRITICAL
        
        # Calculate funding percentage
        current_pv = self._calculate_pv_of_contributions(goal)
        current_funding_pct = (goal.current_funding + current_pv) / goal.target_amount
        
        # Calculate additional funding needed
        additional_needed = self._calculate_additional_funding_needed(
            goal, prob_success, np.median(final_values)
        )
        
        # Generate recommendation
        recommendation = self._generate_recommendation(
            goal, prob_success, additional_needed, status
        )
        
        result = GoalResult(
            goal=goal,
            probability_of_success=prob_success,
            median_value_at_target=np.median(final_values),
            percentile_10_value=np.percentile(final_values, 10),
            percentile_90_value=np.percentile(final_values, 90),
            expected_shortfall=expected_shortfall,
            shortfall_probability=shortfall_prob,
            status=status,
            current_funding_pct=current_funding_pct,
            additional_funding_needed=additional_needed,
            recommendation=recommendation,
            scenarios_succeeded=succeeded,
            scenarios_failed=failed,
            value_distribution=final_values,
        )
        
        self.results[goal.id] = result
        return result
    
    def simulate_all_goals(self, seed: Optional[int] = None) -> List[GoalResult]:
        """
        Simulate all goals.
        
        Returns: List of GoalResult objects
        """
        results = []
        for i, goal in enumerate(self.goals):
            goal_seed = seed + i if seed is not None else None
            result = self.simulate_goal(goal, seed=goal_seed)
            results.append(result)
        
        return results
    
    def check_goal_conflicts(self) -> List[Dict[str, any]]:
        """
        Identify conflicts between goals (overlapping timelines, funding competition).
        
        Returns: List of conflicts with recommendations
        """
        conflicts = []
        
        # Group goals by time period
        near_term = [g for g in self.goals if g.is_near_term(self.current_year, 5)]
        
        if len(near_term) > 1:
            # Check if total funding needed exceeds reasonable contribution capacity
            total_needed = sum(
                self.results[g.id].additional_funding_needed 
                for g in near_term if g.id in self.results
            )
            
            if total_needed > 0:
                conflicts.append({
                    'type': 'funding_competition',
                    'description': f'{len(near_term)} goals competing for funding in next 5 years',
                    'goals_affected': [g.name for g in near_term],
                    'total_funding_gap': total_needed,
                    'recommendation': self._resolve_funding_conflict(near_term)
                })
        
        # Check priority conflicts
        critical_at_risk = [
            g for g in self.goals 
            if g.priority == GoalPriority.CRITICAL 
            and g.id in self.results
            and self.results[g.id].status in [GoalStatus.AT_RISK, GoalStatus.CRITICAL]
        ]
        
        if critical_at_risk:
            conflicts.append({
                'type': 'critical_goal_at_risk',
                'description': f'{len(critical_at_risk)} critical goals not on track',
                'goals_affected': [g.name for g in critical_at_risk],
                'recommendation': 'Increase funding for critical goals or reduce spending on lower-priority goals'
            })
        
        return conflicts
    
    def _calculate_pv_of_contributions(self, goal: FinancialGoal) -> float:
        """Calculate present value of future contributions."""
        years = goal.years_until_goal(self.current_year)
        if goal.annual_contribution == 0 or years <= 0:
            return 0.0
        
        # Simple PV calculation assuming mid-year returns
        discount_rate = (
            goal.equity_pct * self.equity_return +
            goal.fi_pct * self.fi_return +
            goal.cash_pct * self.cash_return
        )
        
        # PV of annuity
        if discount_rate > 0:
            pv = goal.annual_contribution * (
                (1 - (1 + discount_rate) ** -years) / discount_rate
            ) * (1 + discount_rate)  # Adjust for beginning of year payments
        else:
            pv = goal.annual_contribution * years
        
        return pv
    
    def _calculate_additional_funding_needed(
        self,
        goal: FinancialGoal,
        current_prob: float,
        median_value: float,
    ) -> float:
        """
        Estimate additional annual funding needed to reach success threshold.
        
        Simplified calculation - more sophisticated version would re-run simulation.
        """
        if current_prob >= goal.success_threshold:
            return 0.0
        
        # Estimate gap
        gap = goal.target_amount - median_value
        years = goal.years_until_goal(self.current_year)
        
        if years <= 0:
            return 0.0
        
        # Additional annual contribution needed (simplified)
        additional = gap / years * 1.2  # 20% buffer
        
        return max(0.0, additional)
    
    def _generate_recommendation(
        self,
        goal: FinancialGoal,
        prob_success: float,
        additional_needed: float,
        status: GoalStatus,
    ) -> str:
        """Generate human-readable recommendation for goal."""
        if status == GoalStatus.ON_TRACK:
            return f"On track! {prob_success:.0%} probability of success. Continue current funding strategy."
        
        if additional_needed > 0:
            years = goal.years_until_goal(self.current_year)
            return (
                f"Increase annual contributions by ${additional_needed:,.0f} "
                f"({prob_success:.0%} → {goal.success_threshold:.0%} target). "
                f"Or reduce goal by ${additional_needed * years:,.0f}."
            )
        
        return f"Review goal parameters. Current probability: {prob_success:.0%}"
    
    def _resolve_funding_conflict(self, conflicting_goals: List[FinancialGoal]) -> str:
        """Generate recommendation for resolving funding conflicts."""
        # Sort by priority
        sorted_goals = sorted(conflicting_goals, key=lambda g: g.priority.value)
        
        critical = [g for g in sorted_goals if g.priority == GoalPriority.CRITICAL]
        
        if critical:
            return (
                f"Prioritize critical goals: {', '.join(g.name for g in critical)}. "
                f"Consider delaying or reducing lower-priority goals."
            )
        
        return "Consider extending timelines for lower-priority goals or increasing overall contributions."
    
    def _handle_past_goal(self, goal: FinancialGoal) -> GoalResult:
        """Handle goal whose target date has passed."""
        if goal.current_funding >= goal.target_amount:
            status = GoalStatus.ACHIEVED
            recommendation = "Goal achieved!"
            prob_success = 1.0
        else:
            status = GoalStatus.CRITICAL
            shortfall = goal.target_amount - goal.current_funding
            recommendation = f"Goal date passed. Shortfall: ${shortfall:,.0f}"
            prob_success = 0.0
        
        return GoalResult(
            goal=goal,
            probability_of_success=prob_success,
            median_value_at_target=goal.current_funding,
            percentile_10_value=goal.current_funding,
            percentile_90_value=goal.current_funding,
            expected_shortfall=max(0, goal.target_amount - goal.current_funding),
            shortfall_probability=1.0 if prob_success == 0 else 0.0,
            status=status,
            current_funding_pct=goal.current_funding / goal.target_amount,
            additional_funding_needed=0.0,
            recommendation=recommendation,
            scenarios_succeeded=self.n_scenarios if prob_success == 1.0 else 0,
            scenarios_failed=0 if prob_success == 1.0 else self.n_scenarios,
        )


# Example usage
if __name__ == "__main__":
    print("="*60)
    print("GOAL-BASED PLANNING ENGINE DEMO")
    print("="*60)
    
    # Initialize engine
    engine = GoalEngine(current_year=2024, n_scenarios=1000)
    
    # Define goals
    retirement = FinancialGoal(
        name="Retirement Income Portfolio",
        target_amount=3000000,
        target_year=2045,
        priority=GoalPriority.CRITICAL,
        current_funding=1500000,
        annual_contribution=50000,
        equity_pct=0.70,
        use_glide_path=True,
    )
    
    college = FinancialGoal(
        name="College Fund - Child 1",
        target_amount=300000,
        target_year=2030,
        priority=GoalPriority.HIGH,
        current_funding=120000,
        annual_contribution=20000,
        equity_pct=0.60,
        use_glide_path=True,
        years_before_goal_to_derisk=3,
    )
    
    vacation_home = FinancialGoal(
        name="Vacation Home Purchase",
        target_amount=500000,
        target_year=2035,
        priority=GoalPriority.MEDIUM,
        current_funding=50000,
        annual_contribution=15000,
        equity_pct=0.50,
        use_glide_path=False,
    )
    
    # Add goals
    engine.add_goal(retirement)
    engine.add_goal(college)
    engine.add_goal(vacation_home)
    
    # Simulate all goals
    print("\nRunning simulations...")
    results = engine.simulate_all_goals(seed=42)
    
    # Print results
    print("\n" + "="*60)
    print("GOAL ANALYSIS RESULTS")
    print("="*60)
    
    for result in results:
        print(f"\n{result.goal.name}:")
        print(f"  Target: ${result.goal.target_amount:,.0f} by {result.goal.target_year}")
        print(f"  Priority: {result.goal.priority.name}")
        print(f"  Status: {result.status.value.upper()}")
        print(f"  Probability of Success: {result.probability_of_success:.1%}")
        print(f"  Current Funding: {result.current_funding_pct:.1%}")
        print(f"  Median Outcome: ${result.median_value_at_target:,.0f}")
        print(f"  10th Percentile: ${result.percentile_10_value:,.0f}")
        print(f"  90th Percentile: ${result.percentile_90_value:,.0f}")
        if result.additional_funding_needed > 0:
            print(f"  Additional Funding Needed: ${result.additional_funding_needed:,.0f}/year")
        print(f"  Recommendation: {result.recommendation}")
    
    # Check for conflicts
    conflicts = engine.check_goal_conflicts()
    if conflicts:
        print("\n" + "="*60)
        print("GOAL CONFLICTS DETECTED")
        print("="*60)
        for conflict in conflicts:
            print(f"\n{conflict['type'].upper()}:")
            print(f"  {conflict['description']}")
            print(f"  Affected goals: {', '.join(conflict['goals_affected'])}")
            print(f"  Recommendation: {conflict['recommendation']}")
