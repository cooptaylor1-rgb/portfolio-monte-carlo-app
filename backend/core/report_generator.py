"""
Enhanced Report Generation with Natural Language Narratives

Generates client-ready reports with:
- Executive summaries in plain English
- Risk identification and prioritization
- Actionable recommendations
- Failure analysis and recovery strategies
- Worst-case scenario planning

Author: Salem Investment Counselors
Last Updated: December 2024
"""

from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple, Any
from enum import Enum
import numpy as np
import logging

logger = logging.getLogger(__name__)


class RiskLevel(str, Enum):
    """Risk severity levels"""
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    CRITICAL = "critical"


class RiskType(str, Enum):
    """Types of financial risks"""
    SEQUENCE_OF_RETURNS = "sequence_of_returns"
    LONGEVITY = "longevity"
    INFLATION = "inflation"
    HEALTHCARE_COSTS = "healthcare_costs"
    PORTFOLIO_DEPLETION = "portfolio_depletion"
    TAX_INEFFICIENCY = "tax_inefficiency"
    SPENDING_UNSUSTAINABLE = "spending_unsustainable"
    CONCENTRATION = "concentration"
    MARKET_VOLATILITY = "market_volatility"


@dataclass
class IdentifiedRisk:
    """A specific risk identified in the analysis"""
    risk_type: RiskType
    severity: RiskLevel
    probability: float  # 0-1
    potential_impact: float  # Dollar amount or percentage
    description: str
    mitigation_strategy: str
    priority_rank: int = 0


@dataclass
class Recommendation:
    """An actionable recommendation"""
    title: str
    description: str
    expected_benefit: str
    implementation_steps: List[str]
    priority: int  # 1 = highest
    category: str  # "spending", "allocation", "tax", "insurance"


@dataclass
class FailurePattern:
    """Pattern observed in failed scenarios"""
    pattern_name: str
    frequency: float  # % of failures showing this pattern
    typical_failure_year: int
    description: str
    prevention_strategy: str


@dataclass
class ExecutiveSummary:
    """Natural language executive summary"""
    plan_overview: str
    success_probability_narrative: str
    key_strengths: List[str]
    key_concerns: List[str]
    bottom_line: str


class NarrativeEngine:
    """
    Generates natural language narratives from simulation results.
    
    Analyzes Monte Carlo output and creates human-readable summaries
    that advisors can present to clients.
    """
    
    def __init__(self):
        self.risk_thresholds = {
            'success_prob_critical': 0.70,
            'success_prob_moderate': 0.85,
            'depletion_year_critical': 10,
            'depletion_year_moderate': 20,
            'inflation_sensitivity_high': 0.15,
        }
    
    def generate_executive_summary(
        self,
        success_probability: float,
        median_ending_value: float,
        percentile_10_value: float,
        percentile_90_value: float,
        starting_portfolio: float,
        years_to_model: int,
        current_age: int,
        monthly_spending: float,
        has_goals: bool = False,
        goals_on_track_count: int = 0,
        total_goals: int = 0,
    ) -> ExecutiveSummary:
        """
        Generate executive summary in natural language.
        
        Args:
            success_probability: Monte Carlo success rate
            median_ending_value: Median portfolio value at horizon
            percentile_10_value: 10th percentile (worst case)
            percentile_90_value: 90th percentile (best case)
            starting_portfolio: Initial portfolio value
            years_to_model: Planning horizon
            current_age: Client's current age
            monthly_spending: Monthly spending amount
            has_goals: Whether goal-based planning is enabled
            goals_on_track_count: Number of goals on track
            total_goals: Total number of goals
        
        Returns:
            ExecutiveSummary with natural language descriptions
        """
        horizon_age = current_age + years_to_model
        annual_spending = abs(monthly_spending) * 12
        
        # Plan overview
        plan_overview = self._generate_plan_overview(
            starting_portfolio, annual_spending, current_age, horizon_age, has_goals
        )
        
        # Success probability narrative
        success_narrative = self._generate_success_narrative(
            success_probability, years_to_model
        )
        
        # Key strengths
        strengths = self._identify_strengths(
            success_probability,
            median_ending_value,
            starting_portfolio,
            annual_spending,
            has_goals,
            goals_on_track_count,
            total_goals
        )
        
        # Key concerns
        concerns = self._identify_concerns(
            success_probability,
            percentile_10_value,
            starting_portfolio,
            annual_spending,
            years_to_model
        )
        
        # Bottom line
        bottom_line = self._generate_bottom_line(
            success_probability, concerns, strengths
        )
        
        return ExecutiveSummary(
            plan_overview=plan_overview,
            success_probability_narrative=success_narrative,
            key_strengths=strengths,
            key_concerns=concerns,
            bottom_line=bottom_line
        )
    
    def _generate_plan_overview(
        self,
        starting_portfolio: float,
        annual_spending: float,
        current_age: int,
        horizon_age: int,
        has_goals: bool
    ) -> str:
        """Generate natural language plan overview"""
        spending_rate = (annual_spending / starting_portfolio) * 100
        
        overview = (
            f"This financial plan analyzes a ${starting_portfolio:,.0f} portfolio "
            f"supporting ${annual_spending:,.0f} in annual spending (adjusted for inflation) "
            f"from age {current_age} to {horizon_age}. "
        )
        
        if spending_rate < 3:
            overview += "The spending rate is conservative, which enhances sustainability. "
        elif spending_rate < 4:
            overview += "The spending rate is moderate and generally sustainable. "
        elif spending_rate < 5:
            overview += "The spending rate is elevated, requiring careful monitoring. "
        else:
            overview += "The spending rate is aggressive and may require adjustment. "
        
        if has_goals:
            overview += "The plan incorporates specific financial goals with dedicated tracking."
        
        return overview
    
    def _generate_success_narrative(
        self,
        success_probability: float,
        years: int
    ) -> str:
        """Generate success probability narrative"""
        if success_probability >= 0.90:
            return (
                f"The plan has a {success_probability:.0%} probability of success over {years} years. "
                f"This excellent success rate suggests the current strategy is well-positioned "
                f"to meet your financial objectives with a comfortable margin of safety."
            )
        elif success_probability >= 0.85:
            return (
                f"The plan shows a {success_probability:.0%} probability of success. "
                f"This solid success rate indicates the strategy is sustainable, "
                f"though periodic monitoring is recommended to maintain this trajectory."
            )
        elif success_probability >= 0.75:
            return (
                f"With a {success_probability:.0%} success probability, the plan is viable "
                f"but has less margin for error. Consider modest adjustments to improve "
                f"resilience against market volatility or unexpected expenses."
            )
        elif success_probability >= 0.70:
            return (
                f"The {success_probability:.0%} success rate indicates moderate risk. "
                f"The plan may work under favorable conditions, but adjustments to spending "
                f"or asset allocation should be considered to increase probability of success."
            )
        else:
            return (
                f"The {success_probability:.0%} success probability is concerning. "
                f"Without meaningful adjustments to spending, portfolio allocation, or income sources, "
                f"the plan faces significant risk of portfolio depletion. Immediate review recommended."
            )
    
    def _identify_strengths(
        self,
        success_prob: float,
        median_ending: float,
        starting: float,
        annual_spending: float,
        has_goals: bool,
        goals_on_track: int,
        total_goals: int
    ) -> List[str]:
        """Identify key plan strengths"""
        strengths = []
        
        if success_prob >= 0.85:
            strengths.append(f"High probability of success ({success_prob:.0%}) provides strong financial security")
        
        if median_ending > starting:
            growth = ((median_ending - starting) / starting) * 100
            strengths.append(f"Portfolio expected to grow {growth:.0f}% in real terms (median scenario)")
        
        spending_rate = (annual_spending / starting) * 100
        if spending_rate <= 4:
            strengths.append(f"Sustainable spending rate ({spending_rate:.1f}%) supports long-term plan")
        
        if has_goals and total_goals > 0:
            pct_on_track = (goals_on_track / total_goals) * 100
            if pct_on_track >= 75:
                strengths.append(f"Majority of financial goals ({goals_on_track}/{total_goals}) are on track")
        
        if median_ending > starting * 1.5:
            strengths.append("Significant wealth accumulation potential for legacy or increased spending flexibility")
        
        if not strengths:
            strengths.append("Plan is established with clear objectives and timeline")
        
        return strengths
    
    def _identify_concerns(
        self,
        success_prob: float,
        percentile_10: float,
        starting: float,
        annual_spending: float,
        years: int
    ) -> List[str]:
        """Identify key plan concerns"""
        concerns = []
        
        if success_prob < 0.85:
            concerns.append(
                f"Success probability ({success_prob:.0%}) is below ideal threshold of 85%"
            )
        
        if percentile_10 <= 0:
            concerns.append(
                "Worst-case scenarios result in portfolio depletion - downside protection recommended"
            )
        elif percentile_10 < starting * 0.3:
            concerns.append(
                f"10th percentile outcome (${percentile_10:,.0f}) represents significant portfolio decline"
            )
        
        spending_rate = (annual_spending / starting) * 100
        if spending_rate > 4.5:
            concerns.append(
                f"Spending rate ({spending_rate:.1f}%) exceeds sustainable guidelines (4% rule)"
            )
        
        if years >= 30:
            concerns.append(
                "Long planning horizon (30+ years) increases exposure to sequence-of-returns risk"
            )
        
        if not concerns:
            concerns.append("No major concerns identified - plan appears well-structured")
        
        return concerns
    
    def _generate_bottom_line(
        self,
        success_prob: float,
        concerns: List[str],
        strengths: List[str]
    ) -> str:
        """Generate bottom line recommendation"""
        if success_prob >= 0.90 and len(concerns) <= 1:
            return (
                "**Bottom Line:** Your financial plan is in excellent shape. "
                "Continue current strategy with annual reviews to ensure you stay on track."
            )
        elif success_prob >= 0.85:
            return (
                "**Bottom Line:** Your plan is solid with good probability of success. "
                "Minor adjustments may further enhance resilience. Recommend semi-annual monitoring."
            )
        elif success_prob >= 0.75:
            return (
                "**Bottom Line:** Your plan is viable but would benefit from adjustments. "
                "Consider the recommendations below to improve probability of success. "
                "Quarterly reviews recommended."
            )
        elif success_prob >= 0.70:
            return (
                "**Bottom Line:** Your plan needs attention. Implementing recommended changes "
                "is important to reduce risk of portfolio depletion. Schedule planning meeting to discuss options."
            )
        else:
            return (
                "**Bottom Line:** Immediate action required. Current plan has high risk of failure. "
                "Priority recommendations should be implemented promptly. Schedule comprehensive plan review."
            )


class RiskAnalyzer:
    """
    Identifies and prioritizes financial planning risks.
    
    Analyzes simulation results to detect specific risk factors
    and ranks them by severity and probability.
    """
    
    def identify_risks(
        self,
        success_probability: float,
        median_ending: float,
        percentile_10: float,
        failure_scenarios: np.ndarray,
        starting_portfolio: float,
        annual_spending: float,
        years_to_model: int,
        current_age: int,
        horizon_age: int,
        equity_pct: float,
        monthly_spending: float,
    ) -> List[IdentifiedRisk]:
        """
        Identify and rank all relevant risks.
        
        Returns: List of IdentifiedRisk objects, sorted by priority
        """
        risks = []
        
        # 1. Portfolio depletion risk
        if success_probability < 0.85:
            risks.append(self._analyze_depletion_risk(
                success_probability, starting_portfolio, annual_spending
            ))
        
        # 2. Sequence of returns risk
        if years_to_model >= 20 and current_age >= 60:
            risks.append(self._analyze_sequence_risk(
                current_age, years_to_model, success_probability
            ))
        
        # 3. Longevity risk
        if horizon_age >= 90 or years_to_model >= 30:
            risks.append(self._analyze_longevity_risk(
                horizon_age, median_ending, starting_portfolio
            ))
        
        # 4. Inflation risk
        if annual_spending > starting_portfolio * 0.04:
            risks.append(self._analyze_inflation_risk(
                annual_spending, starting_portfolio
            ))
        
        # 5. Market volatility risk
        if percentile_10 < starting_portfolio * 0.3:
            risks.append(self._analyze_volatility_risk(
                percentile_10, median_ending, starting_portfolio
            ))
        
        # 6. Spending sustainability risk
        spending_rate = (annual_spending / starting_portfolio) * 100
        if spending_rate > 4.5:
            risks.append(self._analyze_spending_risk(
                spending_rate, starting_portfolio, annual_spending
            ))
        
        # 7. Asset allocation risk
        if equity_pct > 0.80 or equity_pct < 0.30:
            risks.append(self._analyze_allocation_risk(
                equity_pct, current_age
            ))
        
        # Sort by severity and probability
        risks.sort(key=lambda r: (
            ['low', 'moderate', 'high', 'critical'].index(r.severity.value),
            -r.probability
        ), reverse=True)
        
        # Assign priority ranks
        for i, risk in enumerate(risks, 1):
            risk.priority_rank = i
        
        return risks[:5]  # Return top 5 risks
    
    def _analyze_depletion_risk(
        self,
        success_prob: float,
        starting: float,
        annual_spending: float
    ) -> IdentifiedRisk:
        """Analyze risk of portfolio depletion"""
        failure_prob = 1 - success_prob
        
        if failure_prob > 0.30:
            severity = RiskLevel.CRITICAL
        elif failure_prob > 0.15:
            severity = RiskLevel.HIGH
        elif failure_prob > 0.10:
            severity = RiskLevel.MODERATE
        else:
            severity = RiskLevel.LOW
        
        description = (
            f"Portfolio has {failure_prob:.0%} probability of depletion before plan horizon. "
            f"Primary driver is spending rate relative to portfolio size."
        )
        
        # Calculate spending reduction needed
        reduction_needed = starting * 0.04 - annual_spending
        
        mitigation = (
            f"Reduce annual spending by ${abs(reduction_needed):,.0f} (targeting 4% withdrawal rate), "
            f"or increase portfolio contributions, or adjust allocation for higher growth."
        )
        
        return IdentifiedRisk(
            risk_type=RiskType.PORTFOLIO_DEPLETION,
            severity=severity,
            probability=failure_prob,
            potential_impact=starting,
            description=description,
            mitigation_strategy=mitigation
        )
    
    def _analyze_sequence_risk(
        self,
        current_age: int,
        years: int,
        success_prob: float
    ) -> IdentifiedRisk:
        """Analyze sequence-of-returns risk"""
        if current_age >= 65 and years >= 30:
            severity = RiskLevel.HIGH
            probability = 0.25
        elif current_age >= 60 and years >= 25:
            severity = RiskLevel.MODERATE
            probability = 0.20
        else:
            severity = RiskLevel.MODERATE
            probability = 0.15
        
        description = (
            f"Retiring at age {current_age} with {years}-year horizon creates exposure "
            f"to early retirement market volatility. Poor returns in first 5-10 years "
            f"can significantly impair long-term sustainability."
        )
        
        mitigation = (
            "Build 2-3 year cash reserve to avoid selling stocks during market downturns. "
            "Consider bond tent strategy (temporarily higher fixed income allocation). "
            "Implement flexible spending rules to reduce withdrawals during bear markets."
        )
        
        return IdentifiedRisk(
            risk_type=RiskType.SEQUENCE_OF_RETURNS,
            severity=severity,
            probability=probability,
            potential_impact=0.30,  # Can reduce success by ~30%
            description=description,
            mitigation_strategy=mitigation
        )
    
    def _analyze_longevity_risk(
        self,
        horizon_age: int,
        median_ending: float,
        starting: float
    ) -> IdentifiedRisk:
        """Analyze risk of outliving plan"""
        if horizon_age >= 95:
            severity = RiskLevel.HIGH
            probability = 0.50  # 50% chance one spouse lives to 95+
        elif horizon_age >= 90:
            severity = RiskLevel.MODERATE
            probability = 0.35
        else:
            severity = RiskLevel.LOW
            probability = 0.20
        
        description = (
            f"Planning to age {horizon_age}. There is {probability:.0%} probability "
            f"of living beyond this age, requiring portfolio to last longer than modeled."
        )
        
        if median_ending > starting * 0.5:
            mitigation = (
                f"Median ending value (${median_ending:,.0f}) provides cushion. "
                f"Consider: (1) extend planning horizon to age {horizon_age + 5}, "
                f"(2) purchase longevity annuity at age 75-80, or "
                f"(3) implement hybrid spending strategy that adjusts to portfolio performance."
            )
        else:
            mitigation = (
                "Low ending values increase longevity risk. Strongly consider: "
                "(1) longevity annuity to cover essential expenses, "
                "(2) delay Social Security to age 70 for maximum benefits, "
                "(3) reduce spending now to preserve capital."
            )
        
        return IdentifiedRisk(
            risk_type=RiskType.LONGEVITY,
            severity=severity,
            probability=probability,
            potential_impact=0.20,
            description=description,
            mitigation_strategy=mitigation
        )
    
    def _analyze_inflation_risk(
        self,
        annual_spending: float,
        starting: float,
        stochastic_scenarios: Optional[List] = None
    ) -> IdentifiedRisk:
        """
        Analyze inflation risk with optional stochastic scenarios.
        
        If stochastic_scenarios provided, analyzes distribution of inflation outcomes.
        Otherwise uses simple heuristics based on spending rate.
        
        Args:
            annual_spending: Annual spending amount
            starting: Starting portfolio value
            stochastic_scenarios: Optional list of InflationScenario objects
        
        Returns:
            IdentifiedRisk with inflation assessment
        """
        spending_rate = (annual_spending / starting) * 100
        
        # Enhanced analysis if stochastic scenarios provided
        if stochastic_scenarios and len(stochastic_scenarios) > 0:
            # Analyze distribution of inflation outcomes
            final_rates = [s.monthly_rates[-1] * 12 for s in stochastic_scenarios]  # Annualized
            avg_inflation = np.mean(final_rates)
            p90_inflation = np.percentile(final_rates, 90)
            p10_inflation = np.percentile(final_rates, 10)
            
            # Calculate cumulative inflation impact
            cumulative_factors = [s.cumulative_factor[-1] for s in stochastic_scenarios]
            avg_cumulative = np.mean(cumulative_factors)
            p90_cumulative = np.percentile(cumulative_factors, 90)
            
            # Assess severity based on tail risk
            if p90_inflation > 0.06:  # 90th percentile above 6%
                severity = RiskLevel.HIGH
                probability = 0.40
            elif p90_inflation > 0.045:  # 90th percentile above 4.5%
                severity = RiskLevel.MODERATE
                probability = 0.30
            elif avg_inflation > 0.035:  # Average above 3.5%
                severity = RiskLevel.MODERATE
                probability = 0.25
            else:
                severity = RiskLevel.LOW
                probability = 0.15
            
            # Impact: erosion of purchasing power
            years = len(stochastic_scenarios[0].monthly_rates) / 12
            potential_impact = annual_spending * (p90_cumulative - 1.0) * years * 0.5
            
            description = (
                f"Stochastic inflation analysis shows mean inflation of {avg_inflation:.1%} "
                f"with 90th percentile at {p90_inflation:.1%}. Over {int(years)} years, "
                f"this creates {(p90_cumulative - 1.0) * 100:.0f}% cumulative inflation in worst case. "
                f"Current spending rate ({spending_rate:.1f}%) amplifies inflation sensitivity."
            )
            
            if p90_inflation > 0.05:
                mitigation = (
                    f"HIGH INFLATION RISK: 90th percentile inflation ({p90_inflation:.1%}) significantly "
                    f"exceeds historical average. URGENT recommendations: "
                    f"(1) Increase TIPS/I-Bonds to 20-25% of portfolio, "
                    f"(2) Maintain 60%+ equity for long-term inflation hedge, "
                    f"(3) Build 30% flexible spending capacity to cut during inflation spikes, "
                    f"(4) Consider inflation-protected annuity (COLA rider) for essential expenses. "
                    f"Monitor CPI quarterly and adjust spending immediately if inflation exceeds 4%."
                )
            else:
                mitigation = (
                    f"Moderate inflation risk ({avg_inflation:.1%} average, {p90_inflation:.1%} 90th percentile). "
                    f"Recommendations: (1) Allocate 10-15% to TIPS/I-Bonds for baseline inflation protection, "
                    f"(2) Maintain diversified equity exposure (50-70%) as long-term inflation hedge, "
                    f"(3) Review spending annually for inflation adjustments, "
                    f"(4) Consider flexible spending rules (10-20% discretionary buffer) for high inflation periods."
                )
        
        else:
            # Fallback to simple analysis if no stochastic data
            if spending_rate > 5:
                severity = RiskLevel.HIGH
                probability = 0.35
            elif spending_rate > 4.5:
                severity = RiskLevel.MODERATE
                probability = 0.25
            else:
                severity = RiskLevel.LOW
                probability = 0.15
            
            potential_impact = starting * 0.15
            
            description = (
                f"High spending rate ({spending_rate:.1f}%) amplifies inflation risk. "
                f"If inflation exceeds 3% for extended period, real portfolio value "
                f"may decline faster than expected."
            )
            
            mitigation = (
                "Increase TIPS or I-Bond allocation to 10-15% of portfolio for inflation protection. "
                "Consider equity allocation (stocks historically outpace inflation). "
                "Build flexible spending budget to cut discretionary expenses during high inflation."
            )
        
        return IdentifiedRisk(
            risk_type=RiskType.INFLATION,
            severity=severity,
            probability=probability,
            potential_impact=potential_impact,
            description=description,
            mitigation_strategy=mitigation
        )
    
    def _analyze_volatility_risk(
        self,
        percentile_10: float,
        median: float,
        starting: float
    ) -> IdentifiedRisk:
        """Analyze market volatility risk"""
        downside_deviation = (starting - percentile_10) / starting
        
        if downside_deviation > 0.70:
            severity = RiskLevel.HIGH
        elif downside_deviation > 0.50:
            severity = RiskLevel.MODERATE
        else:
            severity = RiskLevel.LOW
        
        description = (
            f"Wide outcome range: worst-case scenario (${percentile_10:,.0f}) "
            f"is {downside_deviation:.0%} below starting value. High volatility "
            f"creates emotional stress and may lead to poor decisions during downturns."
        )
        
        mitigation = (
            "Consider reducing equity allocation by 10-15% to dampen volatility. "
            "Establish written investment policy to prevent emotional decisions. "
            "Focus on total return (growth + income) rather than daily market movements."
        )
        
        return IdentifiedRisk(
            risk_type=RiskType.MARKET_VOLATILITY,
            severity=severity,
            probability=0.30,
            potential_impact=starting * downside_deviation,
            description=description,
            mitigation_strategy=mitigation
        )
    
    def _analyze_spending_risk(
        self,
        spending_rate: float,
        starting: float,
        annual_spending: float
    ) -> IdentifiedRisk:
        """Analyze spending sustainability risk"""
        if spending_rate > 6:
            severity = RiskLevel.CRITICAL
        elif spending_rate > 5:
            severity = RiskLevel.HIGH
        elif spending_rate > 4.5:
            severity = RiskLevel.MODERATE
        else:
            severity = RiskLevel.LOW
        
        description = (
            f"Current spending rate ({spending_rate:.1f}%) significantly exceeds "
            f"sustainable guidelines (4% rule). This aggressive withdrawal rate "
            f"is primary driver of plan risk."
        )
        
        target_spending = starting * 0.04
        reduction = annual_spending - target_spending
        
        mitigation = (
            f"PRIORITY: Reduce spending by ${reduction:,.0f}/year to reach 4% target. "
            f"Alternative: Increase portfolio by ${reduction * 25:,.0f} through contributions. "
            f"Or: Implement flexible spending with 20% discretionary buffer for market downturns."
        )
        
        return IdentifiedRisk(
            risk_type=RiskType.SPENDING_UNSUSTAINABLE,
            severity=severity,
            probability=0.80 if spending_rate > 5 else 0.60,
            potential_impact=reduction * 20,  # 20 years of excess spending
            description=description,
            mitigation_strategy=mitigation
        )
    
    def _analyze_allocation_risk(
        self,
        equity_pct: float,
        current_age: int
    ) -> IdentifiedRisk:
        """Analyze asset allocation appropriateness"""
        rule_of_thumb = (110 - current_age) / 100  # Simple age-based guideline
        deviation = abs(equity_pct - rule_of_thumb)
        
        if deviation > 0.25:
            severity = RiskLevel.MODERATE
        elif deviation > 0.15:
            severity = RiskLevel.LOW
        else:
            return None  # Allocation is reasonable
        
        if equity_pct > rule_of_thumb:
            concern = "higher equity allocation than typical for your age"
            adjustment = "reduce equity to {:.0%}".format(rule_of_thumb)
        else:
            concern = "lower equity allocation than typical for your age"
            adjustment = "increase equity to {:.0%} for better growth".format(rule_of_thumb)
        
        description = (
            f"Current allocation ({equity_pct:.0%} equity) represents {concern}. "
            f"Rule of thumb suggests {rule_of_thumb:.0%} equity at age {current_age}."
        )
        
        mitigation = (
            f"Consider adjusting to {adjustment}. However, final allocation should reflect "
            f"your risk tolerance, spending needs, and time horizon. Extreme allocations "
            f"(<30% or >80% equity) warrant careful review."
        )
        
        return IdentifiedRisk(
            risk_type=RiskType.CONCENTRATION,
            severity=severity,
            probability=0.40,
            potential_impact=0.10,
            description=description,
            mitigation_strategy=mitigation
        )


class RecommendationEngine:
    """
    Generates prioritized, actionable recommendations.
    
    Based on identified risks and plan analysis, creates specific
    recommendations that advisors can discuss with clients.
    """
    
    def generate_recommendations(
        self,
        risks: List[IdentifiedRisk],
        success_probability: float,
        starting_portfolio: float,
        annual_spending: float,
        equity_pct: float,
        years_to_model: int,
    ) -> List[Recommendation]:
        """
        Generate top recommendations based on identified risks.
        
        Returns: List of 3-5 prioritized recommendations
        """
        recommendations = []
        
        # Address top risks first
        for risk in risks[:3]:
            rec = self._risk_to_recommendation(risk, starting_portfolio, annual_spending)
            if rec:
                recommendations.append(rec)
        
        # Add general recommendations based on overall plan
        if success_probability < 0.85:
            recommendations.append(self._recommend_success_improvement(
                success_probability, starting_portfolio, annual_spending
            ))
        
        if equity_pct > 0.70 and years_to_model >= 25:
            recommendations.append(self._recommend_glide_path())
        
        # Limit to top 5
        return recommendations[:5]
    
    def _risk_to_recommendation(
        self,
        risk: IdentifiedRisk,
        starting: float,
        annual_spending: float
    ) -> Optional[Recommendation]:
        """Convert identified risk to actionable recommendation"""
        if risk.risk_type == RiskType.SPENDING_UNSUSTAINABLE:
            return Recommendation(
                title="Reduce Annual Spending",
                description=risk.description,
                expected_benefit=f"Increase success probability by 10-15 percentage points",
                implementation_steps=[
                    f"Target spending reduction: ${(annual_spending - starting * 0.04):,.0f}/year",
                    "Identify discretionary expenses to cut (travel, dining, gifts)",
                    "Implement spending tracking system",
                    "Review spending quarterly and adjust as needed"
                ],
                priority=1,
                category="spending"
            )
        
        elif risk.risk_type == RiskType.SEQUENCE_OF_RETURNS:
            return Recommendation(
                title="Build Cash Reserve Buffer",
                description="Protect against early retirement market volatility",
                expected_benefit="Avoid forced stock sales during market downturns, improving long-term returns by 1-2%/year",
                implementation_steps=[
                    "Allocate 2-3 years of spending to cash/short-term bonds",
                    f"Target reserve: ${annual_spending * 2.5:,.0f}",
                    "Replenish reserve during strong market years",
                    "Use reserve instead of selling stocks when market down >10%"
                ],
                priority=2,
                category="allocation"
            )
        
        elif risk.risk_type == RiskType.PORTFOLIO_DEPLETION:
            return Recommendation(
                title="Implement Flexible Spending Strategy",
                description="Adjust spending based on portfolio performance",
                expected_benefit="Reduce failure probability by 5-10 percentage points while maintaining lifestyle",
                implementation_steps=[
                    "Separate spending into essential vs. discretionary buckets",
                    "Cut discretionary spending by 10-20% when portfolio declines >15%",
                    "Increase spending modestly (5%) when portfolio outperforms",
                    "Review spending adjustments annually"
                ],
                priority=1,
                category="spending"
            )
        
        elif risk.risk_type == RiskType.LONGEVITY:
            return Recommendation(
                title="Consider Longevity Insurance",
                description=risk.description,
                expected_benefit="Guarantee lifetime income, reducing anxiety about outliving assets",
                implementation_steps=[
                    "Research longevity annuities (QLAC or deferred income annuity)",
                    "Target purchase at age 70-75 for income starting at 80-85",
                    "Allocate 10-15% of portfolio to purchase",
                    "Compare quotes from multiple highly-rated insurers (A+ rating minimum)"
                ],
                priority=3,
                category="insurance"
            )
        
        return None
    
    def _recommend_success_improvement(
        self,
        success_prob: float,
        starting: float,
        annual_spending: float
    ) -> Recommendation:
        """Recommend ways to improve success probability"""
        gap = 0.85 - success_prob
        spending_reduction = starting * (gap * 0.05)  # Rough estimate
        
        return Recommendation(
            title="Enhance Plan Success Probability",
            description=f"Current {success_prob:.0%} success rate below recommended 85% threshold",
            expected_benefit=f"Achieve 85%+ success probability, providing greater financial security",
            implementation_steps=[
                f"Option 1: Reduce spending by ${spending_reduction:,.0f}/year",
                f"Option 2: Increase portfolio through additional contributions or delayed retirement",
                "Option 3: Delay Social Security to age 70 for 24% higher benefit",
                "Option 4: Implement combination of moderate adjustments across all areas"
            ],
            priority=1,
            category="comprehensive"
        )
    
    def _recommend_glide_path(self) -> Recommendation:
        """Recommend equity glide path"""
        return Recommendation(
            title="Implement Equity Glide Path",
            description="Gradually reduce equity exposure as you age to protect accumulated wealth",
            expected_benefit="Reduce downside risk in later retirement while maintaining growth in early years",
            implementation_steps=[
                "Start with current 70% equity allocation",
                "Reduce by 1-2 percentage points per year over next 10-15 years",
                "Target 40-50% equity allocation by age 75-80",
                "Rebalance annually during plan review"
            ],
            priority=3,
            category="allocation"
        )


class FailureAnalyzer:
    """
    Analyzes failure scenarios to understand what causes portfolio depletion.
    
    Examines the characteristics of scenarios that fail to identify
    common patterns and develop prevention strategies.
    """
    
    def analyze_failures(
        self,
        all_paths: np.ndarray,
        success_threshold: float,
        years_to_model: int,
        starting_portfolio: float,
        annual_spending: float,
    ) -> Dict[str, any]:
        """
        Analyze failed scenarios to identify patterns.
        
        Args:
            all_paths: All Monte Carlo paths (n_scenarios x n_months)
            success_threshold: Minimum ending value for success
            years_to_model: Planning horizon
            starting_portfolio: Initial portfolio value
            annual_spending: Annual spending amount
        
        Returns:
            Dictionary with failure analysis insights
        """
        # Identify failed scenarios (ending value < threshold)
        ending_values = all_paths[:, -1]
        failed_mask = ending_values < success_threshold
        failed_paths = all_paths[failed_mask]
        
        if len(failed_paths) == 0:
            return {
                'failure_count': 0,
                'failure_rate': 0.0,
                'patterns': [],
                'avg_failure_year': None,
                'summary': "No failure scenarios detected. Plan is highly robust."
            }
        
        failure_count = len(failed_paths)
        failure_rate = failure_count / len(all_paths)
        
        # Find when failures typically occur
        failure_years = self._identify_failure_years(failed_paths, starting_portfolio)
        avg_failure_year = np.mean(failure_years)
        
        # Identify common patterns
        patterns = self._identify_failure_patterns(
            failed_paths, failure_years, starting_portfolio, annual_spending
        )
        
        # Generate summary
        summary = self._generate_failure_summary(
            failure_rate, avg_failure_year, patterns
        )
        
        return {
            'failure_count': failure_count,
            'failure_rate': failure_rate,
            'patterns': patterns,
            'avg_failure_year': int(avg_failure_year) if not np.isnan(avg_failure_year) else None,
            'median_failure_year': int(np.median(failure_years)),
            'earliest_failure_year': int(np.min(failure_years)),
            'summary': summary,
            'prevention_strategies': [p.prevention_strategy for p in patterns]
        }
    
    def _identify_failure_years(
        self,
        failed_paths: np.ndarray,
        starting_portfolio: float
    ) -> np.ndarray:
        """Identify year when each scenario depletes"""
        failure_years = []
        
        for path in failed_paths:
            # Find first month when portfolio hits zero or goes negative
            depletion_month = np.where(path <= 0)[0]
            if len(depletion_month) > 0:
                failure_years.append(depletion_month[0] / 12.0)
            else:
                # Didn't hit zero but ended below threshold
                # Approximate when it would hit zero
                decline_rate = (starting_portfolio - path[-1]) / len(path)
                if decline_rate > 0:
                    months_to_zero = path[-1] / (decline_rate * 12)
                    failure_years.append(len(path) / 12.0 + months_to_zero)
                else:
                    failure_years.append(len(path) / 12.0)
        
        return np.array(failure_years)
    
    def _identify_failure_patterns(
        self,
        failed_paths: np.ndarray,
        failure_years: np.ndarray,
        starting: float,
        annual_spending: float
    ) -> List[FailurePattern]:
        """Identify common characteristics of failed scenarios"""
        patterns = []
        
        # Pattern 1: Early market decline (first 5 years)
        early_decline_count = 0
        for path in failed_paths:
            year_5_value = path[min(60, len(path)-1)]  # Month 60 = year 5
            if year_5_value < starting * 0.75:  # Lost 25%+ in first 5 years
                early_decline_count += 1
        
        if early_decline_count > len(failed_paths) * 0.3:
            patterns.append(FailurePattern(
                pattern_name="Early Market Decline",
                frequency=early_decline_count / len(failed_paths),
                typical_failure_year=int(np.median(failure_years[failure_years < 15])) if any(failure_years < 15) else 20,
                description=(
                    f"{early_decline_count / len(failed_paths):.0%} of failures experienced "
                    f"significant portfolio losses (25%+) in the first 5 years of retirement. "
                    f"This sequence-of-returns risk is the primary driver of early depletion."
                ),
                prevention_strategy=(
                    "Build 2-3 year cash reserve. Implement bond tent strategy. "
                    "Use flexible spending rules to cut withdrawals by 10-20% when portfolio declines >15%."
                )
            ))
        
        # Pattern 2: Gradual depletion (steady decline)
        gradual_count = sum(1 for fy in failure_years if fy > 15)
        if gradual_count > len(failed_paths) * 0.3:
            patterns.append(FailurePattern(
                pattern_name="Gradual Depletion",
                frequency=gradual_count / len(failed_paths),
                typical_failure_year=int(np.median(failure_years[failure_years > 15])) if any(failure_years > 15) else 20,
                description=(
                    f"{gradual_count / len(failed_paths):.0%} of failures result from steady "
                    f"portfolio decline over 15+ years. Spending rate consistently exceeds "
                    f"portfolio returns, causing slow but inevitable depletion."
                ),
                prevention_strategy=(
                    "Reduce annual spending by 10-15% to align with sustainable withdrawal rate. "
                    "Or: increase equity allocation for higher long-term growth (with higher volatility trade-off)."
                )
            ))
        
        # Pattern 3: Late-life depletion (longevity risk)
        late_count = sum(1 for fy in failure_years if fy > 25)
        if late_count > len(failed_paths) * 0.2:
            patterns.append(FailurePattern(
                pattern_name="Late-Life Depletion",
                frequency=late_count / len(failed_paths),
                typical_failure_year=int(np.median(failure_years[failure_years > 25])) if any(failure_years > 25) else 28,
                description=(
                    f"{late_count / len(failed_paths):.0%} of failures occur after year 25, "
                    f"indicating longevity risk. Portfolio successfully navigates most of retirement "
                    f"but depletes in final years due to cumulative inflation and healthcare costs."
                ),
                prevention_strategy=(
                    "Consider longevity annuity (QLAC) to guarantee income after age 80-85. "
                    "Delay Social Security to age 70 for maximum lifetime benefits. "
                    "Reduce spending in early retirement to preserve capital for later years."
                )
            ))
        
        # Pattern 4: Volatile early years
        volatile_count = 0
        for path in failed_paths:
            first_10_years = path[:120]  # First 10 years (120 months)
            volatility = np.std(first_10_years) / np.mean(first_10_years)
            if volatility > 0.20:  # High early volatility
                volatile_count += 1
        
        if volatile_count > len(failed_paths) * 0.25:
            patterns.append(FailurePattern(
                pattern_name="High Early Volatility",
                frequency=volatile_count / len(failed_paths),
                typical_failure_year=int(np.median(failure_years)),
                description=(
                    f"{volatile_count / len(failed_paths):.0%} of failures feature high portfolio "
                    f"volatility in first 10 years, creating emotional stress and potential for "
                    f"poor decisions. Wild swings undermine confidence in long-term plan."
                ),
                prevention_strategy=(
                    "Reduce equity allocation by 10-15% to dampen volatility. "
                    "Establish written investment policy to prevent panic selling. "
                    "Consider target-date fund or managed volatility strategies."
                )
            ))
        
        return patterns
    
    def _generate_failure_summary(
        self,
        failure_rate: float,
        avg_failure_year: float,
        patterns: List[FailurePattern]
    ) -> str:
        """Generate human-readable failure analysis summary"""
        if failure_rate == 0:
            return "No failure scenarios detected. Plan is highly robust."
        
        summary = (
            f"{failure_rate:.0%} of scenarios result in portfolio depletion. "
        )
        
        if avg_failure_year < 10:
            summary += (
                f"Failures occur early (average year {avg_failure_year:.0f}), "
                f"indicating high sensitivity to early market conditions (sequence risk). "
            )
        elif avg_failure_year < 20:
            summary += (
                f"Failures typically occur mid-plan (average year {avg_failure_year:.0f}), "
                f"suggesting spending rate is marginally unsustainable. "
            )
        else:
            summary += (
                f"Failures occur late (average year {avg_failure_year:.0f}), "
                f"indicating longevity risk and cumulative inflation impact. "
            )
        
        if patterns:
            dominant_pattern = max(patterns, key=lambda p: p.frequency)
            summary += (
                f"Dominant failure pattern: {dominant_pattern.pattern_name} "
                f"({dominant_pattern.frequency:.0%} of failures)."
            )
        
        return summary


class WorstCaseAnalyzer:
    """
    Deep-dive analysis of worst-case (10th percentile) scenarios.
    
    Helps clients understand downside risks and develop
    contingency plans for unfavorable outcomes.
    """
    
    def analyze_worst_case(
        self,
        all_paths: np.ndarray,
        percentile_10_value: float,
        starting_portfolio: float,
        annual_spending: float,
        years_to_model: int,
    ) -> Dict[str, any]:
        """
        Analyze 10th percentile scenarios to understand worst-case outcomes.
        
        Returns: Dictionary with worst-case insights and recovery strategies
        """
        # Find paths at or below 10th percentile
        ending_values = all_paths[:, -1]
        percentile_10_threshold = np.percentile(ending_values, 10)
        worst_case_paths = all_paths[ending_values <= percentile_10_threshold]
        
        if len(worst_case_paths) == 0:
            return {'error': 'No worst-case paths found'}
        
        # Average worst-case path
        avg_worst_case_path = np.mean(worst_case_paths, axis=0)
        
        # Identify when things go wrong
        turning_point = self._find_turning_point(avg_worst_case_path, starting_portfolio)
        
        # Calculate worst-case statistics
        max_drawdown = self._calculate_max_drawdown(avg_worst_case_path, starting_portfolio)
        recovery_time = self._estimate_recovery_time(avg_worst_case_path, starting_portfolio)
        
        # Generate recovery strategies
        recovery_strategies = self._generate_recovery_strategies(
            percentile_10_value,
            starting_portfolio,
            annual_spending,
            max_drawdown
        )
        
        # What-if scenarios
        what_if_scenarios = self._generate_what_if_scenarios(
            starting_portfolio,
            annual_spending,
            percentile_10_value
        )
        
        description = self._generate_worst_case_description(
            percentile_10_value,
            starting_portfolio,
            max_drawdown,
            turning_point,
            years_to_model
        )
        
        return {
            'percentile_10_value': percentile_10_value,
            'max_drawdown_pct': max_drawdown,
            'turning_point_year': turning_point,
            'recovery_time_years': recovery_time,
            'description': description,
            'recovery_strategies': recovery_strategies,
            'what_if_scenarios': what_if_scenarios,
            'avg_worst_case_path': avg_worst_case_path.tolist() if len(avg_worst_case_path) < 500 else []
        }
    
    def _find_turning_point(
        self,
        path: np.ndarray,
        starting: float
    ) -> int:
        """Find year when portfolio decline becomes problematic"""
        for month in range(len(path)):
            if path[month] < starting * 0.75:  # Lost 25%
                return month // 12
        return 0
    
    def _calculate_max_drawdown(
        self,
        path: np.ndarray,
        starting: float
    ) -> float:
        """Calculate maximum drawdown percentage"""
        running_max = np.maximum.accumulate(path)
        drawdown = (running_max - path) / running_max
        max_drawdown = np.max(drawdown)
        return max_drawdown
    
    def _estimate_recovery_time(
        self,
        path: np.ndarray,
        starting: float
    ) -> Optional[int]:
        """Estimate years to recover from worst decline"""
        # Find lowest point
        lowest_idx = np.argmin(path)
        lowest_value = path[lowest_idx]
        
        # See if portfolio recovers
        recovery_idx = np.where(path[lowest_idx:] >= starting)[0]
        if len(recovery_idx) > 0:
            return (recovery_idx[0] + lowest_idx) // 12
        
        return None  # Never recovers
    
    def _generate_worst_case_description(
        self,
        percentile_10: float,
        starting: float,
        max_drawdown: float,
        turning_point: int,
        years: int
    ) -> str:
        """Generate worst-case scenario description"""
        decline_pct = ((starting - percentile_10) / starting) * 100
        
        description = (
            f"In worst-case scenarios (bottom 10%), portfolio ends at ${percentile_10:,.0f}, "
            f"representing a {decline_pct:.0f}% decline from starting value. "
        )
        
        if turning_point <= 5:
            description += (
                f"Trouble begins early (year {turning_point}), typically due to poor market "
                f"returns in first 5 years combined with ongoing withdrawals. "
            )
        elif turning_point <= 15:
            description += (
                f"Portfolio decline accelerates around year {turning_point}, often due to "
                f"prolonged period of below-average returns or elevated spending. "
            )
        else:
            description += (
                f"Portfolio remains relatively stable until year {turning_point}, when "
                f"cumulative effects of inflation and withdrawals overwhelm growth. "
            )
        
        description += (
            f"Maximum drawdown reaches {max_drawdown:.0%}, which would be emotionally "
            f"challenging and may prompt poor decisions if not anticipated."
        )
        
        return description
    
    def _generate_recovery_strategies(
        self,
        percentile_10: float,
        starting: float,
        annual_spending: float,
        max_drawdown: float
    ) -> List[str]:
        """Generate specific recovery strategies for worst-case"""
        strategies = []
        
        # Strategy 1: Spending cuts
        if annual_spending > starting * 0.03:
            reduction_needed = annual_spending - (starting * 0.03)
            strategies.append(
                f"Cut spending by ${reduction_needed:,.0f}/year (to 3% withdrawal rate) "
                f"until portfolio recovers to starting value"
            )
        
        # Strategy 2: Work longer or return to work
        if annual_spending > 60000:
            part_time_income = annual_spending * 0.3
            strategies.append(
                f"Generate ${part_time_income:,.0f}/year through part-time work or consulting "
                f"to reduce portfolio withdrawals by 30%"
            )
        
        # Strategy 3: Delay Social Security
        strategies.append(
            "Delay Social Security to age 70 for 24-32% higher lifetime benefits "
            "(8% annual increase from 67-70)"
        )
        
        # Strategy 4: Downsize or tap home equity
        home_equity_estimate = starting * 0.3  # Rough estimate
        strategies.append(
            f"Consider downsizing home or HECM reverse mortgage to access ~${home_equity_estimate:,.0f} "
            f"in home equity without selling portfolio at depressed prices"
        )
        
        # Strategy 5: Tax optimization
        strategies.append(
            "Optimize withdrawal sources: harvest tax losses, use Roth funds strategically, "
            "minimize unnecessary tax drag on portfolio returns"
        )
        
        return strategies
    
    def _generate_what_if_scenarios(
        self,
        starting: float,
        annual_spending: float,
        percentile_10: float
    ) -> List[Dict[str, str]]:
        """Generate what-if alternative scenarios"""
        scenarios = []
        
        # What if: Reduce spending 15%
        reduced_spending = annual_spending * 0.85
        spending_rate_reduced = (reduced_spending / starting) * 100
        scenarios.append({
            'scenario': 'Reduce Spending 15%',
            'change': f'Spending: ${reduced_spending:,.0f}/year ({spending_rate_reduced:.2f}%)',
            'impact': 'Likely improves worst-case by 20-30%, potentially avoiding depletion',
            'trade_off': 'Modest lifestyle adjustment, cut discretionary expenses'
        })
        
        # What if: Increase equity allocation
        scenarios.append({
            'scenario': 'Increase Equity 10%',
            'change': 'Boost stock allocation for higher long-term returns',
            'impact': 'May improve median outcomes but increases volatility and risk of worse downside',
            'trade_off': 'Higher potential upside with greater emotional/volatility risk'
        })
        
        # What if: Purchase annuity
        annuity_amount = starting * 0.25
        annual_income = annuity_amount * 0.05  # Rough 5% payout
        scenarios.append({
            'scenario': 'Purchase Immediate Annuity',
            'change': f'Convert ${annuity_amount:,.0f} to guaranteed ${annual_income:,.0f}/year income',
            'impact': 'Eliminates longevity risk, provides income floor, reduces worst-case impact',
            'trade_off': 'Irreversible decision, reduced flexibility, estate value reduced'
        })
        
        # What if: Work 2 more years
        additional_savings = annual_spending * 2 * 0.5  # Save 50% of spending for 2 years
        scenarios.append({
            'scenario': 'Delay Retirement 2 Years',
            'change': f'Add ${additional_savings:,.0f} to portfolio, defer withdrawals 2 years',
            'impact': 'Significantly improves all outcomes, worst-case likely positive',
            'trade_off': 'Less retirement time, continued work stress'
        })
        
        return scenarios


# Example usage
if __name__ == "__main__":
    print("="*70)
    print("NARRATIVE REPORT GENERATION DEMO")
    print("="*70)
    
    # Sample simulation results
    success_prob = 0.78
    median_ending = 3_200_000
    percentile_10 = 500_000
    percentile_90 = 8_500_000
    starting = 4_500_000
    years = 30
    current_age = 65
    monthly_spending = 15_000
    
    # Generate executive summary
    narrative_engine = NarrativeEngine()
    summary = narrative_engine.generate_executive_summary(
        success_probability=success_prob,
        median_ending_value=median_ending,
        percentile_10_value=percentile_10,
        percentile_90_value=percentile_90,
        starting_portfolio=starting,
        years_to_model=years,
        current_age=current_age,
        monthly_spending=monthly_spending,
        has_goals=False
    )
    
    print("\n" + "="*70)
    print("EXECUTIVE SUMMARY")
    print("="*70)
    print(f"\n{summary.plan_overview}\n")
    print(f"{summary.success_probability_narrative}\n")
    
    print("\nKEY STRENGTHS:")
    for strength in summary.key_strengths:
        print(f"  ✓ {strength}")
    
    print("\nKEY CONCERNS:")
    for concern in summary.key_concerns:
        print(f"  ⚠ {concern}")
    
    print(f"\n{summary.bottom_line}\n")
    
    # Identify risks
    risk_analyzer = RiskAnalyzer()
    risks = risk_analyzer.identify_risks(
        success_probability=success_prob,
        median_ending=median_ending,
        percentile_10=percentile_10,
        failure_scenarios=np.array([]),  # Simplified for demo
        starting_portfolio=starting,
        annual_spending=monthly_spending * 12,
        years_to_model=years,
        current_age=current_age,
        horizon_age=current_age + years,
        equity_pct=0.70,
        monthly_spending=monthly_spending
    )
    
    print("="*70)
    print("TOP IDENTIFIED RISKS")
    print("="*70)
    for risk in risks[:3]:
        print(f"\n{risk.priority_rank}. {risk.risk_type.value.upper().replace('_', ' ')}")
        print(f"   Severity: {risk.severity.value.upper()} | Probability: {risk.probability:.0%}")
        print(f"   {risk.description}")
        print(f"   Mitigation: {risk.mitigation_strategy}")
    
    # Generate recommendations
    rec_engine = RecommendationEngine()
    recommendations = rec_engine.generate_recommendations(
        risks=risks,
        success_probability=success_prob,
        starting_portfolio=starting,
        annual_spending=monthly_spending * 12,
        equity_pct=0.70,
        years_to_model=years
    )
    
    print("\n" + "="*70)
    print("TOP RECOMMENDATIONS")
    print("="*70)
    for rec in recommendations[:3]:
        print(f"\n{rec.priority}. {rec.title}")
        print(f"   Category: {rec.category.upper()}")
        print(f"   {rec.description}")
        print(f"   Expected Benefit: {rec.expected_benefit}")
        print(f"   Implementation Steps:")
        for step in rec.implementation_steps:
            print(f"      • {step}")
    
    print("\n" + "="*70)
    print("DEMO COMPLETE ✓")


# ============================================================================
# SEQUENCE OF RETURNS RISK ANALYSIS
# ============================================================================

def analyze_sequence_risk(
    all_paths: np.ndarray,
    years_to_model: int,
    starting_portfolio: float
) -> Dict[str, Any]:
    """
    Analyze sequence of returns risk by comparing early vs late bear market impact.
    
    Sequence risk is the risk that poor returns early in retirement have a much
    larger impact on success than poor returns later. This is because early losses
    compound with withdrawals, creating a "hole" the portfolio never escapes.
    
    Args:
        all_paths: Array of shape (n_scenarios, n_months) with portfolio values
        years_to_model: Number of years in simulation
        starting_portfolio: Initial portfolio value
    
    Returns:
        Dictionary with sequence risk metrics
    """
    n_scenarios, n_months = all_paths.shape
    
    # Define periods
    early_months = min(60, n_months)  # First 5 years
    mid_start = early_months
    mid_months = min(120, n_months - early_months)  # Years 6-15
    late_start = min(early_months + mid_months, n_months)
    
    # Calculate returns for each period
    early_returns = []
    mid_returns = []
    late_returns = []
    
    for path in all_paths:
        if early_months > 0:
            early_ret = (path[early_months - 1] / starting_portfolio) - 1
            early_returns.append(early_ret)
        
        if mid_months > 0 and mid_start < n_months:
            mid_ret = (path[min(mid_start + mid_months - 1, n_months - 1)] / 
                      path[mid_start]) - 1
            mid_returns.append(mid_ret)
        
        if late_start < n_months:
            late_ret = (path[-1] / path[late_start]) - 1
            late_returns.append(late_ret)
    
    avg_early = np.mean(early_returns) if early_returns else 0
    avg_mid = np.mean(mid_returns) if mid_returns else 0
    avg_late = np.mean(late_returns) if late_returns else 0
    
    # Identify scenarios with early bear markets (bottom 10%)
    early_bear_threshold = np.percentile(early_returns, 10)
    early_bear_scenarios = [i for i, ret in enumerate(early_returns) 
                           if ret <= early_bear_threshold]
    
    # Identify scenarios with late bear markets
    late_bear_threshold = np.percentile(late_returns, 10) if late_returns else 0
    late_bear_scenarios = [i for i, ret in enumerate(late_returns) 
                          if ret <= late_bear_threshold]
    
    # Calculate final portfolio values for each group
    early_bear_final = np.mean([all_paths[i, -1] for i in early_bear_scenarios])
    late_bear_final = np.mean([all_paths[i, -1] for i in late_bear_scenarios]) if late_bear_scenarios else 0
    overall_median = np.median(all_paths[:, -1])
    
    # Sequence risk score (0-10)
    early_impact_pct = (overall_median - early_bear_final) / starting_portfolio
    late_impact_pct = (overall_median - late_bear_final) / starting_portfolio if late_bear_final > 0 else 0
    
    # Higher score = early losses hurt much more than late losses
    if late_impact_pct > 0:
        impact_ratio = early_impact_pct / late_impact_pct
    else:
        impact_ratio = 5.0  # Default if no late impact
    
    sequence_score = min(10.0, impact_ratio * 2)  # Scale to 0-10
    
    # Description
    if sequence_score > 7:
        risk_level = "CRITICAL"
        description = (
            f"CRITICAL sequence risk: Early bear markets reduce final portfolio by "
            f"{early_impact_pct * 100:.0f}% vs only {late_impact_pct * 100:.0f}% for late bear markets "
            f"(impact ratio {impact_ratio:.1f}x). This plan is extremely vulnerable to early poor returns. "
            f"URGENT: Build 3-5 year cash reserve to avoid forced stock sales during early downturns."
        )
    elif sequence_score > 4:
        risk_level = "MODERATE"
        description = (
            f"Moderate sequence risk: Early bear markets reduce final portfolio by "
            f"{early_impact_pct * 100:.0f}% vs {late_impact_pct * 100:.0f}% for late bear markets "
            f"(impact ratio {impact_ratio:.1f}x). Consider building 2-3 year cash buffer "
            f"to weather early market volatility without forced sales."
        )
    else:
        risk_level = "LOW"
        description = (
            f"Low sequence risk: Impact of early vs late bear markets is similar "
            f"({early_impact_pct * 100:.0f}% vs {late_impact_pct * 100:.0f}%, ratio {impact_ratio:.1f}x). "
            f"Plan is reasonably resilient to market timing. Maintain diversified allocation "
            f"and 1-2 year cash reserve for normal volatility management."
        )
    
    return {
        'early_period_return': avg_early,
        'mid_period_return': avg_mid,
        'late_period_return': avg_late,
        'sequence_risk_score': sequence_score,
        'risk_level': risk_level,
        'description': description,
        'early_bear_market_impact': early_impact_pct,
        'late_bear_market_impact': late_impact_pct,
        'impact_ratio': impact_ratio,
        'early_bear_final_value': early_bear_final,
        'late_bear_final_value': late_bear_final,
        'overall_median_final': overall_median,
    }
    print("="*70)
    
    # Additional demo: Failure Analysis
    print("\n\n" + "="*70)
    print("FAILURE ANALYSIS DEMO")
    print("="*70)
    
    # Generate sample Monte Carlo paths
    np.random.seed(42)
    n_scenarios = 1000
    n_months = years * 12
    
    # Simulate simple paths (starting at $4.5M, declining with spending + returns)
    paths = np.zeros((n_scenarios, n_months + 1))
    paths[:, 0] = starting
    
    for month in range(1, n_months + 1):
        # Random returns (7% annual = 0.58% monthly with 18% vol)
        returns = np.random.normal(0.0058, 0.052, n_scenarios)
        paths[:, month] = paths[:, month-1] * (1 + returns) - (monthly_spending + 500)  # Spending + healthcare
    
    # Analyze failures
    failure_analyzer = FailureAnalyzer()
    failure_analysis = failure_analyzer.analyze_failures(
        all_paths=paths,
        success_threshold=0,
        years_to_model=years,
        starting_portfolio=starting,
        annual_spending=monthly_spending * 12
    )
    
    print(f"\nFailure Rate: {failure_analysis['failure_rate']:.1%}")
    print(f"Average Failure Year: {failure_analysis['avg_failure_year']}")
    print(f"\n{failure_analysis['summary']}\n")
    
    if failure_analysis['patterns']:
        print("FAILURE PATTERNS:")
        for pattern in failure_analysis['patterns']:
            print(f"\n  {pattern.pattern_name} ({pattern.frequency:.0%})")
            print(f"  Typical Failure: Year {pattern.typical_failure_year}")
            print(f"  {pattern.description}")
            print(f"  Prevention: {pattern.prevention_strategy}")
    
    # Worst-case analysis
    print("\n\n" + "="*70)
    print("WORST-CASE SCENARIO ANALYSIS")
    print("="*70)
    
    worst_case_analyzer = WorstCaseAnalyzer()
    worst_case = worst_case_analyzer.analyze_worst_case(
        all_paths=paths,
        percentile_10_value=percentile_10,
        starting_portfolio=starting,
        annual_spending=monthly_spending * 12,
        years_to_model=years
    )
    
    print(f"\n{worst_case['description']}\n")
    print("RECOVERY STRATEGIES:")
    for i, strategy in enumerate(worst_case['recovery_strategies'], 1):
        print(f"  {i}. {strategy}")
    
    print("\n" + "-"*70)
    print("WHAT-IF SCENARIOS")
    print("-"*70)
    for scenario in worst_case['what_if_scenarios']:
        print(f"\n{scenario['scenario']}:")
        print(f"  Change: {scenario['change']}")
        print(f"  Impact: {scenario['impact']}")
        print(f"  Trade-off: {scenario['trade_off']}")
    
    print("\n" + "="*70)
    print("ALL DEMOS COMPLETE ✓")
    print("="*70)
