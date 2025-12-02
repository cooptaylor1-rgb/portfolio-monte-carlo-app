"""
AI-Powered Analysis Engine for Portfolio Monte Carlo Platform

This module provides institutional-grade AI capabilities for automated insights,
research assistance, and compliance-friendly commentary generation.

Key Features:
- Conservative, advisor-quality narrative generation
- Natural language research assistant
- Automated stress test translation
- Compliance guardrails and audit trails
- Response caching for performance

Safety Principles:
- Probabilistic framing (avoid certainty)
- Conservative assumptions highlighted
- Risk-aware commentary
- No specific investment recommendations
- Disclosure of AI-generated content
"""

import hashlib
import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
import pandas as pd
import numpy as np

# Note: This implementation uses a placeholder for LLM integration
# In production, integrate with OpenAI, Anthropic, or local LLM
# For now, we'll use rule-based intelligent analysis with AI-ready structure

@dataclass
class AIInsight:
    """Structure for AI-generated insights"""
    insight_type: str  # 'success_driver', 'risk_factor', 'sensitivity', 'recommendation'
    title: str
    summary: str
    detailed_explanation: str
    confidence_level: str  # 'high', 'medium', 'low'
    data_support: Dict[str, Any]
    timestamp: str
    
    def to_dict(self):
        return asdict(self)


@dataclass
class ScenarioAnalysis:
    """Complete AI analysis of a scenario"""
    scenario_id: str
    timestamp: str
    short_summary: str
    long_form_narrative: str
    key_drivers: List[AIInsight]
    risk_factors: List[AIInsight]
    sensitivity_analysis: Dict[str, Any]
    recommendations: List[str]
    audit_metadata: Dict[str, Any]
    
    def to_dict(self):
        return {
            'scenario_id': self.scenario_id,
            'timestamp': self.timestamp,
            'short_summary': self.short_summary,
            'long_form_narrative': self.long_form_narrative,
            'key_drivers': [d.to_dict() for d in self.key_drivers],
            'risk_factors': [r.to_dict() for r in self.risk_factors],
            'sensitivity_analysis': self.sensitivity_analysis,
            'recommendations': self.recommendations,
            'audit_metadata': self.audit_metadata
        }


class AIAnalysisEngine:
    """
    Core AI engine for portfolio analysis.
    
    Provides conservative, compliance-friendly analysis with:
    - Automated insight generation
    - Natural language query processing
    - Stress test interpretation
    - Audit trail maintenance
    """
    
    def __init__(self, cache_enabled: bool = True, audit_trail_path: str = "./audit_logs"):
        self.cache_enabled = cache_enabled
        self.cache = {}
        self.audit_trail_path = audit_trail_path
        self._ensure_audit_directory()
        
        # Compliance guardrails
        self.guardrails = {
            'avoid_certainty': True,
            'require_probability_framing': True,
            'highlight_assumptions': True,
            'conservative_tone': True,
            'no_specific_securities': True
        }
    
    def _ensure_audit_directory(self):
        """Create audit trail directory if it doesn't exist"""
        os.makedirs(self.audit_trail_path, exist_ok=True)
    
    def _generate_cache_key(self, inputs: Dict[str, Any]) -> str:
        """Generate cache key from inputs"""
        key_string = json.dumps(inputs, sort_keys=True)
        return hashlib.md5(key_string.encode()).hexdigest()
    
    def _log_audit_trail(self, analysis: ScenarioAnalysis):
        """Log analysis to audit trail"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"analysis_{analysis.scenario_id}_{timestamp}.json"
        filepath = os.path.join(self.audit_trail_path, filename)
        
        with open(filepath, 'w') as f:
            json.dump(analysis.to_dict(), f, indent=2)
    
    def analyze_scenario(self, 
                        inputs: Dict[str, Any],
                        metrics: Dict[str, Any],
                        stats_df: pd.DataFrame,
                        paths_df: pd.DataFrame) -> ScenarioAnalysis:
        """
        Comprehensive AI analysis of a Monte Carlo scenario.
        
        Args:
            inputs: Simulation input parameters
            metrics: Calculated metrics (success prob, ending values, etc.)
            stats_df: Statistical summary (P10, P50, P90 by month)
            paths_df: All simulation paths
            
        Returns:
            ScenarioAnalysis object with complete insights
        """
        
        # Check cache
        cache_key = self._generate_cache_key({
            'inputs': inputs,
            'metrics': metrics
        })
        
        if self.cache_enabled and cache_key in self.cache:
            return self.cache[cache_key]
        
        # Generate analysis components
        scenario_id = self._generate_scenario_id(inputs)
        timestamp = datetime.now().isoformat()
        
        # Analyze key drivers
        key_drivers = self._identify_key_drivers(inputs, metrics, stats_df)
        
        # Analyze risk factors
        risk_factors = self._analyze_risk_factors(inputs, metrics, stats_df, paths_df)
        
        # Perform sensitivity analysis
        sensitivity = self._perform_sensitivity_analysis(inputs, metrics)
        
        # Generate narratives
        short_summary = self._generate_short_summary(metrics, key_drivers, risk_factors)
        long_form = self._generate_long_form_narrative(inputs, metrics, key_drivers, 
                                                       risk_factors, sensitivity)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(inputs, metrics, risk_factors)
        
        # Build analysis object
        analysis = ScenarioAnalysis(
            scenario_id=scenario_id,
            timestamp=timestamp,
            short_summary=short_summary,
            long_form_narrative=long_form,
            key_drivers=key_drivers,
            risk_factors=risk_factors,
            sensitivity_analysis=sensitivity,
            recommendations=recommendations,
            audit_metadata={
                'cache_key': cache_key,
                'inputs_hash': self._generate_cache_key(inputs),
                'analysis_version': '1.0'
            }
        )
        
        # Cache and log
        if self.cache_enabled:
            self.cache[cache_key] = analysis
        
        self._log_audit_trail(analysis)
        
        return analysis
    
    def _generate_scenario_id(self, inputs: Dict[str, Any]) -> str:
        """Generate unique scenario identifier"""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        input_hash = self._generate_cache_key(inputs)[:8]
        return f"scenario_{timestamp}_{input_hash}"
    
    def _identify_key_drivers(self, 
                             inputs: Dict[str, Any],
                             metrics: Dict[str, Any],
                             stats_df: pd.DataFrame) -> List[AIInsight]:
        """
        Identify key drivers of plan success/failure.
        
        Analyzes:
        - Asset allocation impact
        - Spending rate sustainability
        - Return assumptions
        - Sequence of returns risk
        - Time horizon adequacy
        """
        drivers = []
        
        # Calculate key metrics for analysis
        success_prob = metrics.get('success_probability', 0)
        withdrawal_rate = (abs(inputs.get('monthly_spending', 0)) * 12 / 
                          inputs.get('starting_portfolio', 1)) * 100
        equity_pct = inputs.get('equity_pct', 0) * 100
        years = inputs.get('years_to_model', 0)
        
        # Driver 1: Success Probability Assessment
        if success_prob >= 0.8:
            confidence = "high"
            title = "High Probability of Plan Success"
            summary = f"The plan shows a {success_prob:.0%} probability of success, indicating strong sustainability."
        elif success_prob >= 0.6:
            confidence = "medium"
            title = "Moderate Plan Success Probability"
            summary = f"The plan shows a {success_prob:.0%} probability of success. Consider risk mitigation strategies."
        else:
            confidence = "high"
            title = "Elevated Plan Failure Risk"
            summary = f"The plan shows a {success_prob:.0%} probability of success, below the typical 70-80% threshold."
        
        drivers.append(AIInsight(
            insight_type='success_driver',
            title=title,
            summary=summary,
            detailed_explanation=self._explain_success_probability(success_prob, withdrawal_rate, equity_pct),
            confidence_level=confidence,
            data_support={'success_probability': success_prob},
            timestamp=datetime.now().isoformat()
        ))
        
        # Driver 2: Withdrawal Rate Analysis
        if withdrawal_rate > 5.0:
            drivers.append(AIInsight(
                insight_type='risk_factor',
                title="Elevated Withdrawal Rate",
                summary=f"The initial withdrawal rate of {withdrawal_rate:.2f}% exceeds the traditional 4% guideline.",
                detailed_explanation=self._explain_withdrawal_rate(withdrawal_rate, years),
                confidence_level="high",
                data_support={'withdrawal_rate': withdrawal_rate, 'years': years},
                timestamp=datetime.now().isoformat()
            ))
        
        # Driver 3: Asset Allocation Impact
        drivers.append(AIInsight(
            insight_type='success_driver',
            title=f"Asset Allocation: {equity_pct:.0f}% Equity",
            summary=self._summarize_allocation_impact(equity_pct, years),
            detailed_explanation=self._explain_allocation_impact(equity_pct, years, withdrawal_rate),
            confidence_level="medium",
            data_support={'equity_pct': equity_pct, 'years': years},
            timestamp=datetime.now().isoformat()
        ))
        
        # Driver 4: Sequence of Returns Risk
        early_drawdown_risk = self._assess_sequence_risk(stats_df, inputs)
        if early_drawdown_risk > 0.3:
            drivers.append(AIInsight(
                insight_type='risk_factor',
                title="Elevated Sequence of Returns Risk",
                summary="Early portfolio declines could significantly impact long-term sustainability.",
                detailed_explanation=self._explain_sequence_risk(early_drawdown_risk, withdrawal_rate),
                confidence_level="medium",
                data_support={'sequence_risk_score': early_drawdown_risk},
                timestamp=datetime.now().isoformat()
            ))
        
        return drivers
    
    def _analyze_risk_factors(self,
                             inputs: Dict[str, Any],
                             metrics: Dict[str, Any],
                             stats_df: pd.DataFrame,
                             paths_df: pd.DataFrame) -> List[AIInsight]:
        """
        Analyze risk factors that could impact plan success.
        
        Examines:
        - Portfolio depletion scenarios
        - Volatility impact
        - Tail risk
        - Inflation sensitivity
        - Longevity risk
        """
        risks = []
        
        # Analyze depletion risk
        ending_p10 = metrics.get('ending_p10', 0)
        if ending_p10 <= 0:
            risks.append(AIInsight(
                insight_type='risk_factor',
                title="Portfolio Depletion in Worst Case",
                summary="The 10th percentile outcome shows portfolio depletion, indicating material downside risk.",
                detailed_explanation=self._explain_depletion_risk(ending_p10, metrics),
                confidence_level="high",
                data_support={'ending_p10': ending_p10},
                timestamp=datetime.now().isoformat()
            ))
        
        # Analyze volatility impact
        vol = inputs.get('equity_vol_annual', 0) * 100
        if vol > 20:
            risks.append(AIInsight(
                insight_type='risk_factor',
                title=f"High Portfolio Volatility ({vol:.0f}%)",
                summary="Elevated volatility increases the range of potential outcomes and sequence risk.",
                detailed_explanation=self._explain_volatility_impact(vol, inputs),
                confidence_level="medium",
                data_support={'volatility': vol},
                timestamp=datetime.now().isoformat()
            ))
        
        # Analyze outcome dispersion
        ending_median = metrics.get('ending_median', 0)
        ending_p90 = metrics.get('ending_p90', 0)
        if ending_p10 > 0:
            outcome_ratio = ending_p90 / ending_p10 if ending_p10 > 0 else float('inf')
            if outcome_ratio > 10:
                risks.append(AIInsight(
                    insight_type='risk_factor',
                    title="Wide Range of Potential Outcomes",
                    summary=f"P90/P10 ratio of {outcome_ratio:.1f}x indicates high uncertainty in ending portfolio value.",
                    detailed_explanation=self._explain_outcome_dispersion(ending_p10, ending_median, ending_p90),
                    confidence_level="medium",
                    data_support={'p10': ending_p10, 'p50': ending_median, 'p90': ending_p90},
                    timestamp=datetime.now().isoformat()
                ))
        
        return risks
    
    def _perform_sensitivity_analysis(self,
                                     inputs: Dict[str, Any],
                                     metrics: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform sensitivity analysis on key parameters.
        
        Estimates impact of changes in:
        - Returns (±1%)
        - Spending (±10%)
        - Volatility (±5%)
        - Time horizon (±5 years)
        """
        base_success = metrics.get('success_probability', 0)
        
        # Simplified sensitivity estimates (in production, re-run simulations)
        sensitivity = {
            'returns': {
                'description': 'Impact of ±1% change in expected returns',
                'plus_1_pct': self._estimate_return_sensitivity(inputs, metrics, 0.01),
                'minus_1_pct': self._estimate_return_sensitivity(inputs, metrics, -0.01),
                'importance': 'high'
            },
            'spending': {
                'description': 'Impact of ±10% change in spending',
                'plus_10_pct': self._estimate_spending_sensitivity(inputs, metrics, 0.10),
                'minus_10_pct': self._estimate_spending_sensitivity(inputs, metrics, -0.10),
                'importance': 'high'
            },
            'volatility': {
                'description': 'Impact of ±5% change in volatility',
                'plus_5_pct': self._estimate_volatility_sensitivity(inputs, metrics, 0.05),
                'minus_5_pct': self._estimate_volatility_sensitivity(inputs, metrics, -0.05),
                'importance': 'medium'
            },
            'time_horizon': {
                'description': 'Impact of ±5 years in planning horizon',
                'plus_5_years': 'Consider longevity scenarios',
                'minus_5_years': 'Shorter horizon may improve success',
                'importance': 'high'
            }
        }
        
        return sensitivity
    
    def _generate_short_summary(self,
                               metrics: Dict[str, Any],
                               key_drivers: List[AIInsight],
                               risk_factors: List[AIInsight]) -> str:
        """Generate concise executive summary"""
        success_prob = metrics.get('success_probability', 0)
        ending_median = metrics.get('ending_median', 0)
        ending_p10 = metrics.get('ending_p10', 0)
        
        # Risk assessment
        if success_prob >= 0.8:
            risk_level = "low to moderate"
            outlook = "strong"
        elif success_prob >= 0.6:
            risk_level = "moderate"
            outlook = "reasonable"
        else:
            risk_level = "elevated"
            outlook = "concerning"
        
        summary = f"""
**Executive Summary**

This retirement plan shows a **{success_prob:.0%} probability of success** over the modeled horizon, 
indicating {outlook} sustainability under the stated assumptions.

**Key Findings:**
- Median ending portfolio: ${ending_median:,.0f}
- 10th percentile outcome: ${ending_p10:,.0f}
- Overall risk level: {risk_level.upper()}

**Primary Considerations:**
{self._summarize_drivers(key_drivers[:2])}

**Risk Factors to Monitor:**
{self._summarize_risks(risk_factors[:2])}

*Note: This analysis assumes the stated return, volatility, and spending assumptions. 
Actual results will vary based on market conditions and individual circumstances.*
"""
        return summary.strip()
    
    def _generate_long_form_narrative(self,
                                     inputs: Dict[str, Any],
                                     metrics: Dict[str, Any],
                                     key_drivers: List[AIInsight],
                                     risk_factors: List[AIInsight],
                                     sensitivity: Dict[str, Any]) -> str:
        """Generate detailed client-ready narrative"""
        
        # Build comprehensive narrative
        narrative = f"""
# Portfolio Analysis: Detailed Findings

## Overview

This comprehensive Monte Carlo analysis evaluated {inputs.get('n_scenarios', 10000):,} potential market scenarios 
over a {inputs.get('years_to_model', 0)}-year planning horizon. The analysis incorporates realistic assumptions 
about investment returns, portfolio volatility, inflation, and spending patterns.

## Success Probability Analysis

The plan demonstrates a **{metrics.get('success_probability', 0):.1%} probability of success**, meaning that 
in {metrics.get('success_probability', 0):.1%} of simulated scenarios, the portfolio sustained the planned 
withdrawals throughout the entire time horizon.

{self._explain_success_context(metrics.get('success_probability', 0))}

## Key Drivers of Plan Success

"""
        
        for i, driver in enumerate(key_drivers, 1):
            narrative += f"\n### {i}. {driver.title}\n\n"
            narrative += f"{driver.detailed_explanation}\n"
        
        narrative += "\n## Risk Factors and Considerations\n"
        
        for i, risk in enumerate(risk_factors, 1):
            narrative += f"\n### {i}. {risk.title}\n\n"
            narrative += f"{risk.detailed_explanation}\n"
        
        narrative += "\n## Sensitivity Analysis\n\n"
        narrative += "Understanding how changes in key assumptions impact plan success:\n\n"
        
        for param, analysis in sensitivity.items():
            if isinstance(analysis, dict) and 'description' in analysis:
                narrative += f"**{param.replace('_', ' ').title()}**: {analysis['description']}\n"
        
        narrative += "\n## Important Disclosures\n\n"
        narrative += self._generate_disclosures()
        
        return narrative.strip()
    
    def _generate_recommendations(self,
                                 inputs: Dict[str, Any],
                                 metrics: Dict[str, Any],
                                 risk_factors: List[AIInsight]) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []
        
        success_prob = metrics.get('success_probability', 0)
        withdrawal_rate = (abs(inputs.get('monthly_spending', 0)) * 12 / 
                          inputs.get('starting_portfolio', 1)) * 100
        
        # Success probability based recommendations
        if success_prob < 0.7:
            recommendations.append(
                "Consider reducing planned spending by 10-15% to improve plan sustainability"
            )
            recommendations.append(
                "Explore part-time work or delayed retirement to extend asset accumulation"
            )
        
        # Withdrawal rate recommendations
        if withdrawal_rate > 5.0:
            recommendations.append(
                f"Current {withdrawal_rate:.1f}% withdrawal rate is above sustainable levels; "
                "target 4.0-4.5% for improved longevity"
            )
        
        # Risk-based recommendations
        if len(risk_factors) > 2:
            recommendations.append(
                "Multiple risk factors identified; consider stress testing with conservative assumptions"
            )
        
        # General recommendations
        recommendations.append(
            "Review and update this analysis annually to reflect actual portfolio performance and spending patterns"
        )
        recommendations.append(
            "Consider maintaining 2-3 years of spending in cash/short-term bonds to reduce sequence risk"
        )
        
        return recommendations
    
    # Helper methods for explanations
    
    def _explain_success_probability(self, success_prob: float, withdrawal_rate: float, equity_pct: float) -> str:
        """Detailed explanation of success probability"""
        if success_prob >= 0.8:
            explanation = f"""
The {success_prob:.0%} success probability indicates a robust plan with a high likelihood of sustaining 
planned withdrawals. This elevated success rate reflects:

- **Sustainable withdrawal rate**: At {withdrawal_rate:.2f}%, spending is well-aligned with portfolio capacity
- **Appropriate asset allocation**: {equity_pct:.0f}% equity allocation balances growth and stability
- **Adequate portfolio resources**: Starting capital appears sufficient for the modeled horizon

This success rate provides meaningful margin for unexpected expenses or market volatility.
"""
        elif success_prob >= 0.6:
            explanation = f"""
The {success_prob:.0%} success probability suggests a workable but potentially tight plan. This moderate 
success rate indicates:

- **Borderline withdrawal rate**: At {withdrawal_rate:.2f}%, spending may stress the portfolio in adverse markets
- **Moderate risk exposure**: {equity_pct:.0f}% equity allocation has meaningful volatility impact
- **Limited margin for error**: Unexpected expenses or poor early returns could impact sustainability

Consider building additional margin through reduced spending or extended working years.
"""
        else:
            explanation = f"""
The {success_prob:.0%} success probability indicates elevated risk of portfolio depletion. This concerning 
success rate reflects:

- **Unsustainable withdrawal rate**: At {withdrawal_rate:.2f}%, spending likely exceeds portfolio capacity
- **Insufficient resources**: Starting capital may not support the planned lifestyle and time horizon
- **High failure probability**: {(1-success_prob):.0%} of scenarios result in portfolio depletion

Meaningful adjustments to spending, allocation, or time horizon are recommended.
"""
        return explanation.strip()
    
    def _explain_withdrawal_rate(self, rate: float, years: int) -> str:
        """Explain withdrawal rate implications"""
        return f"""
Research suggests withdrawal rates above 4-4.5% significantly increase portfolio depletion risk, 
particularly for planning horizons of {years} years or longer. The current {rate:.2f}% rate implies 
the portfolio must generate returns exceeding inflation by approximately {rate-1:.1f}% annually after 
accounting for volatility drag.

Historical data shows that {rate:.1f}% withdrawal rates have approximately a 
{self._estimate_historical_failure_rate(rate, years):.0%} failure rate over {years}-year periods, 
even with balanced portfolios. Consider reducing spending or extending the accumulation phase.
"""
    
    def _summarize_allocation_impact(self, equity_pct: float, years: int) -> str:
        """Summarize how allocation impacts outcomes"""
        if equity_pct < 30:
            return f"Conservative {equity_pct:.0f}% equity allocation may limit growth over {years} years"
        elif equity_pct < 60:
            return f"Balanced {equity_pct:.0f}% equity allocation appropriate for {years}-year horizon"
        elif equity_pct < 80:
            return f"Growth-oriented {equity_pct:.0f}% equity allocation increases upside potential and volatility"
        else:
            return f"Aggressive {equity_pct:.0f}% equity allocation maximizes growth but elevates short-term risk"
    
    def _explain_allocation_impact(self, equity_pct: float, years: int, withdrawal_rate: float) -> str:
        """Detailed allocation explanation"""
        if equity_pct >= 70:
            risk_note = "high volatility and potential for significant short-term drawdowns"
        elif equity_pct >= 50:
            risk_note = "moderate volatility balanced against growth potential"
        else:
            risk_note = "lower volatility but potentially limited long-term growth"
        
        return f"""
The {equity_pct:.0f}% equity allocation reflects a balance between growth objectives and risk tolerance 
over the {years}-year planning horizon. This allocation results in {risk_note}.

For withdrawal-based strategies, research suggests equity allocations between 50-70% often optimize 
the trade-off between growth (needed to sustain withdrawals) and stability (to reduce sequence risk). 
The current allocation, combined with the {withdrawal_rate:.2f}% withdrawal rate, implies the portfolio 
must navigate market volatility while generating sufficient returns to sustain spending.
"""
    
    def _assess_sequence_risk(self, stats_df: pd.DataFrame, inputs: Dict[str, Any]) -> float:
        """Assess sequence of returns risk"""
        # Simplified sequence risk score based on early portfolio behavior
        if len(stats_df) < 60:
            return 0.3  # Default moderate risk
        
        # Look at first 5 years volatility
        early_volatility = stats_df.head(60)['P90'].std() / stats_df.head(60)['Median'].mean()
        
        # Normalize to 0-1 scale
        risk_score = min(early_volatility / 0.5, 1.0)
        return risk_score
    
    def _explain_sequence_risk(self, risk_score: float, withdrawal_rate: float) -> str:
        """Explain sequence of returns risk"""
        return f"""
Sequence of returns risk—the danger that poor returns early in retirement coincide with portfolio 
withdrawals—represents a critical threat to plan sustainability. The current {withdrawal_rate:.2f}% 
withdrawal rate amplifies this risk, as early portfolio declines are difficult to recover when 
combined with ongoing withdrawals.

Research shows that portfolios experiencing negative returns in the first 5-10 years of retirement 
have significantly higher failure rates than those experiencing the same returns later. Consider:

- Maintaining 2-3 years of spending in cash/short-term bonds
- Implementing a "guardrails" strategy to reduce spending in down markets
- Delaying Social Security to provide more stable income later
- Building flexibility into spending assumptions
"""
    
    def _explain_depletion_risk(self, ending_p10: float, metrics: Dict[str, Any]) -> str:
        """Explain portfolio depletion risk"""
        success_prob = metrics.get('success_probability', 0)
        return f"""
The 10th percentile outcome shows portfolio depletion, meaning that in approximately 
{(1-success_prob)*100:.0f}% of adverse scenarios, the portfolio fails to sustain planned withdrawals. 
This represents meaningful downside risk that warrants careful consideration.

Portfolio depletion typically results from:
- Poor returns early in the withdrawal phase (sequence risk)
- Spending rates that exceed portfolio growth capacity
- Extended periods of below-average returns
- Unexpected large expenses or reduced income sources

Mitigation strategies include reducing spending, maintaining spending flexibility, delaying retirement, 
or restructuring the portfolio for enhanced stability in early withdrawal years.
"""
    
    def _explain_volatility_impact(self, vol: float, inputs: Dict[str, Any]) -> str:
        """Explain impact of volatility"""
        return f"""
Portfolio volatility of {vol:.0f}% creates significant uncertainty in outcomes and amplifies sequence 
of returns risk during withdrawal phases. While higher volatility often accompanies higher expected 
returns, the combination of volatility and withdrawals can substantially reduce portfolio longevity.

This volatility level implies potential annual portfolio swings of ±{vol*1.5:.0f}% (approximately 
1.5 standard deviations), which can be psychologically challenging and may prompt behavioral errors 
like panic selling. Consider whether current risk tolerance genuinely accommodates these swings.
"""
    
    def _explain_outcome_dispersion(self, p10: float, p50: float, p90: float) -> str:
        """Explain wide outcome range"""
        return f"""
The wide range between worst-case (${p10:,.0f}) and best-case (${p90:,.0f}) outcomes reflects 
substantial uncertainty inherent in long-term projections. This dispersion results from:

- Portfolio volatility compounding over time
- Path-dependent effects of market returns
- Interaction between returns and withdrawals

While the median outcome (${p50:,.0f}) may appear adequate, the wide range suggests meaningful 
probability of outcomes materially above or below this level. Build contingency plans for 
potential downside scenarios.
"""
    
    def _explain_success_context(self, success_prob: float) -> str:
        """Provide context for success probability"""
        if success_prob >= 0.8:
            return "Success rates above 80% are generally considered robust for retirement planning."
        elif success_prob >= 0.7:
            return "Success rates between 70-80% are commonly used as planning thresholds, though higher rates provide more margin."
        elif success_prob >= 0.6:
            return "Success rates between 60-70% indicate elevated risk; most advisors target 70%+ for retirement plans."
        else:
            return "Success rates below 60% indicate substantial risk of portfolio depletion and warrant significant plan adjustments."
    
    def _summarize_drivers(self, drivers: List[AIInsight]) -> str:
        """Summarize key drivers"""
        if not drivers:
            return "- No critical drivers identified"
        
        return "\n".join([f"- {d.summary}" for d in drivers])
    
    def _summarize_risks(self, risks: List[AIInsight]) -> str:
        """Summarize risk factors"""
        if not risks:
            return "- No critical risks identified"
        
        return "\n".join([f"- {r.summary}" for r in risks])
    
    def _estimate_return_sensitivity(self, inputs: Dict[str, Any], metrics: Dict[str, Any], change: float) -> str:
        """Estimate sensitivity to return changes"""
        current_success = metrics.get('success_probability', 0)
        # Simplified estimate: ±1% return ≈ ±8-12% success probability
        impact = change * 10
        new_success = min(max(current_success + impact, 0), 1)
        return f"Estimated success probability: {new_success:.0%} (change of {impact:+.0%})"
    
    def _estimate_spending_sensitivity(self, inputs: Dict[str, Any], metrics: Dict[str, Any], change: float) -> str:
        """Estimate sensitivity to spending changes"""
        current_success = metrics.get('success_probability', 0)
        # Simplified estimate: ±10% spending ≈ ∓5-7% success probability
        impact = -change * 0.6
        new_success = min(max(current_success + impact, 0), 1)
        return f"Estimated success probability: {new_success:.0%} (change of {impact:+.0%})"
    
    def _estimate_volatility_sensitivity(self, inputs: Dict[str, Any], metrics: Dict[str, Any], change: float) -> str:
        """Estimate sensitivity to volatility changes"""
        current_success = metrics.get('success_probability', 0)
        # Simplified estimate: ±5% volatility ≈ ∓3-5% success probability
        impact = -change * 0.8
        new_success = min(max(current_success + impact, 0), 1)
        return f"Estimated success probability: {new_success:.0%} (change of {impact:+.0%})"
    
    def _estimate_historical_failure_rate(self, rate: float, years: int) -> float:
        """Estimate historical failure rate for withdrawal rate"""
        # Simplified historical estimates based on research
        if rate <= 3.5:
            return 0.05
        elif rate <= 4.0:
            return 0.10
        elif rate <= 4.5:
            return 0.18
        elif rate <= 5.0:
            return 0.30
        elif rate <= 5.5:
            return 0.45
        else:
            return 0.60
    
    def _generate_disclosures(self) -> str:
        """Generate compliance-friendly disclosures"""
        return """
**Important Disclosures and Limitations**

*AI-Generated Analysis*: This analysis was generated using automated analytical tools. While designed to 
provide helpful insights, it should not be considered personalized investment advice.

*Assumptions and Limitations*: All projections are based on stated assumptions about returns, volatility, 
inflation, and spending. Actual results will vary, potentially materially, based on market conditions, 
individual circumstances, and behavioral factors.

*No Guarantees*: Past performance does not guarantee future results. Monte Carlo analysis shows potential 
ranges of outcomes but cannot predict actual future returns.

*Not Investment Advice*: This analysis is educational in nature. Consult with qualified financial advisors 
before making investment decisions.

*Probabilities Not Certainties*: Success probabilities represent statistical likelihoods under modeled 
assumptions, not guarantees of outcomes. Plans with high success probabilities can still fail; plans with 
lower probabilities can still succeed.
"""


class AIResearchAssistant:
    """
    Natural language research assistant for advisors.
    
    Provides context-aware answers to questions about:
    - Portfolio characteristics
    - Monte Carlo outputs
    - Historical market regimes
    - Expected returns frameworks
    """
    
    def __init__(self, engine: AIAnalysisEngine):
        self.engine = engine
        self.knowledge_base = self._build_knowledge_base()
    
    def _build_knowledge_base(self) -> Dict[str, Any]:
        """Build knowledge base for research queries"""
        return {
            'withdrawal_rates': {
                'safe_rate': 0.04,
                'aggressive_rate': 0.05,
                'conservative_rate': 0.03,
                'research': 'Based on Bengen (1994) and subsequent research'
            },
            'asset_allocation': {
                'guidelines': {
                    '100_minus_age': 'Traditional conservative approach',
                    '110_minus_age': 'Moderate approach accounting for longevity',
                    '120_minus_age': 'Aggressive approach for longer horizons'
                }
            },
            'historical_returns': {
                'equity_long_term': 0.10,
                'bonds_long_term': 0.05,
                'inflation_long_term': 0.03,
                'source': 'Based on historical US market data 1926-2023'
            },
            'market_regimes': {
                'high_inflation': '1970s, 2021-2023',
                'low_rates': '2009-2021',
                'great_depression': '1929-1939',
                'dotcom_bust': '2000-2002',
                'financial_crisis': '2008-2009'
            }
        }
    
    def answer_query(self, query: str, context: Optional[Dict[str, Any]] = None) -> str:
        """
        Answer natural language query with context-aware response.
        
        Args:
            query: Natural language question from advisor
            context: Optional context from current simulation
            
        Returns:
            Detailed answer grounded in data and research
        """
        query_lower = query.lower()
        
        # Route to appropriate handler
        if any(term in query_lower for term in ['withdrawal rate', 'spending rate', 'draw down', 'swr']):
            return self._answer_withdrawal_query(query, context)
        elif any(term in query_lower for term in ['allocation', 'asset mix', 'equity', 'bonds']):
            return self._answer_allocation_query(query, context)
        elif any(term in query_lower for term in ['historical', 'past', 'history', 'regime']):
            return self._answer_historical_query(query, context)
        elif any(term in query_lower for term in ['returns', 'expected return', 'assumption']):
            return self._answer_returns_query(query, context)
        elif any(term in query_lower for term in ['success', 'probability', 'chance']):
            return self._answer_probability_query(query, context)
        else:
            return self._answer_general_query(query, context)
    
    def _answer_withdrawal_query(self, query: str, context: Optional[Dict[str, Any]]) -> str:
        """Answer withdrawal rate questions"""
        response = """
**Withdrawal Rate Guidance**

Research on sustainable withdrawal rates suggests:

- **4% Rule (Bengen, 1994)**: Historically supported 30-year retirements in most scenarios
- **Dynamic Approaches**: Adjust spending based on portfolio performance
- **Current Environment**: Low starting valuations may warrant caution

**Factors Affecting Sustainability:**
1. Asset allocation (higher equity generally supports higher rates)
2. Planning horizon (longer periods require lower rates)
3. Return expectations (current valuations suggest below-average future returns)
4. Flexibility (ability to reduce spending in downturns improves success)
"""
        
        if context and 'withdrawal_rate' in context:
            current_rate = context['withdrawal_rate']
            response += f"\n**Your Current Rate**: {current_rate:.2f}%\n"
            
            if current_rate <= 4.0:
                response += "Your withdrawal rate aligns with traditional safe withdrawal rate guidance."
            elif current_rate <= 5.0:
                response += "Your withdrawal rate is above traditional guidance; consider stress testing."
            else:
                response += "Your withdrawal rate significantly exceeds traditional guidance; high risk of depletion."
        
        return response
    
    def _answer_allocation_query(self, query: str, context: Optional[Dict[str, Any]]) -> str:
        """Answer asset allocation questions"""
        return """
**Asset Allocation Principles**

Common guidelines for retirement portfolios:

- **100 minus age**: Traditional conservative approach (e.g., age 65 → 35% stocks)
- **110 minus age**: Moderate approach for longer life expectancies (e.g., age 65 → 45% stocks)
- **120 minus age**: Aggressive approach (e.g., age 65 → 55% stocks)

**Key Considerations:**
- Higher equity allocations increase growth potential and volatility
- Bonds provide stability but may underperform inflation
- Sequence risk is highest early in retirement—consider bond tent strategies
- Rebalancing maintains target allocation and can enhance returns

**Research Findings:**
- 50-70% equity often optimal for 30-year retirement horizons
- Higher allocations benefit from lower spending rates
- Individual risk tolerance should override formulaic approaches
"""
    
    def _answer_historical_query(self, query: str, context: Optional[Dict[str, Any]]) -> str:
        """Answer questions about historical markets"""
        return """
**Historical Market Regimes**

**High Inflation Periods:**
- 1970s: Stagflation era (10%+ inflation, equity struggles)
- 2021-2023: Post-pandemic inflation spike

**Low Rate Environments:**
- 2009-2021: Zero/near-zero rates post-financial crisis
- Challenged bond returns, elevated equity valuations

**Major Market Declines:**
- Great Depression (1929-1932): -85% peak to trough
- 2008 Financial Crisis: -57% peak to trough
- 2000-2002 Dot-com: -49% peak to trough
- 2020 COVID: -34% (rapid recovery)

**Key Insights:**
- Markets have recovered from all historical downturns
- Recoveries take 3-5 years on average for major declines
- Sequence risk is real—timing matters for retirees
- Diversification helps but doesn't eliminate downside
"""
    
    def _answer_returns_query(self, query: str, context: Optional[Dict[str, Any]]) -> str:
        """Answer expected returns questions"""
        return """
**Expected Returns Framework**

**Historical Long-Term Returns (1926-2023):**
- US Stocks: ~10% annually
- US Bonds: ~5-6% annually
- Cash: ~3-4% annually
- Inflation: ~3% annually

**Forward-Looking Considerations:**
- Current valuations suggest below-average equity returns ahead
- Low bond yields limit fixed income return potential
- Higher inflation expectations may persist

**Building Assumptions:**
1. Start with current market yields (bonds, dividend yields)
2. Add expected earnings growth (equities)
3. Adjust for valuation levels (high valuations → lower returns)
4. Consider historical ranges and cycles

**Conservative Approach:**
- Use below-average assumptions for planning
- Test sensitivity to assumption changes
- Build margin of safety into projections
"""
    
    def _answer_probability_query(self, query: str, context: Optional[Dict[str, Any]]) -> str:
        """Answer probability interpretation questions"""
        return """
**Interpreting Success Probabilities**

**Common Thresholds:**
- 80-90%: Robust plan with meaningful margin
- 70-80%: Acceptable for many advisors and clients
- 60-70%: Borderline; consider improvements
- <60%: Substantial risk; adjustments recommended

**Important Context:**
- Probabilities depend heavily on assumptions
- Not guarantees—just statistical likelihoods
- Should inform but not dictate decisions
- Consider behavioral/flexibility factors

**Using Probabilities:**
- Compare to spending flexibility
- Test sensitivity to assumption changes
- Consider worst-case outcomes (P10)
- Balance probability with lifestyle goals
"""
    
    def _answer_general_query(self, query: str, context: Optional[Dict[str, Any]]) -> str:
        """Answer general questions"""
        return """
**Research Resources**

For comprehensive retirement planning research:

- **Withdrawal Rates**: Bengen (1994), Trinity Study, Pfau research
- **Asset Allocation**: Markowitz, Sharpe, Bogle principles
- **Sequence Risk**: Kitces, Pfau extensive research
- **Current Market**: Dimensional, Vanguard, BlackRock outlooks

This analysis tool provides institutional-grade Monte Carlo simulation grounded in modern 
portfolio theory and historical market research. Results should be interpreted alongside 
individual circumstances, goals, and risk tolerance.
"""


# Export key classes
__all__ = [
    'AIAnalysisEngine',
    'AIResearchAssistant',
    'ScenarioAnalysis',
    'AIInsight'
]
