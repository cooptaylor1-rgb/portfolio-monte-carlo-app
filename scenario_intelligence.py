"""
Scenario Intelligence System
Reusable templates, validation, and analysis for retirement scenarios
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
import pandas as pd
import numpy as np


@dataclass
class ScenarioTemplate:
    """Template for pre-configured retirement scenarios."""
    name: str
    description: str
    equity_return: float
    fi_return: float
    cash_return: float
    equity_vol: float
    fi_vol: float
    cash_vol: float
    inflation: float
    spending_adjustment: float = 1.0  # Multiplier
    color: str = "#1B3B5F"
    icon: str = "📊"
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for easy access."""
        return {
            'name': self.name,
            'description': self.description,
            'equity_return': self.equity_return,
            'fi_return': self.fi_return,
            'cash_return': self.cash_return,
            'equity_vol': self.equity_vol,
            'fi_vol': self.fi_vol,
            'cash_vol': self.cash_vol,
            'inflation': self.inflation,
            'spending_adjustment': self.spending_adjustment,
            'color': self.color,
            'icon': self.icon
        }


# Pre-defined institutional scenario templates
INSTITUTIONAL_SCENARIOS = {
    'base': ScenarioTemplate(
        name="Base Case",
        description="Moderate assumptions based on long-term historical averages",
        equity_return=0.07,
        fi_return=0.03,
        cash_return=0.015,
        equity_vol=0.18,
        fi_vol=0.06,
        cash_vol=0.01,
        inflation=0.025,
        color="#1B3B5F",
        icon="📊"
    ),
    'conservative': ScenarioTemplate(
        name="Conservative",
        description="Lower returns, reduced volatility, defensive positioning",
        equity_return=0.05,
        fi_return=0.025,
        cash_return=0.01,
        equity_vol=0.15,
        fi_vol=0.05,
        cash_vol=0.005,
        inflation=0.02,
        color="#10B981",
        icon="🛡️"
    ),
    'stress': ScenarioTemplate(
        name="Market Stress",
        description="Severe market downturn with elevated volatility",
        equity_return=0.00,
        fi_return=0.015,
        cash_return=0.005,
        equity_vol=0.35,
        fi_vol=0.10,
        cash_vol=0.02,
        inflation=0.03,
        color="#EF4444",
        icon="⚠️"
    ),
    'longevity': ScenarioTemplate(
        name="Longevity Risk",
        description="Extended planning horizon with increased spending",
        equity_return=0.065,
        fi_return=0.028,
        cash_return=0.012,
        equity_vol=0.18,
        fi_vol=0.06,
        cash_vol=0.01,
        inflation=0.025,
        spending_adjustment=1.15,
        color="#8B5CF6",
        icon="⏳"
    ),
    'inflation_shock': ScenarioTemplate(
        name="Inflation Shock",
        description="Persistent high inflation eroding purchasing power",
        equity_return=0.06,
        fi_return=0.02,
        cash_return=0.01,
        equity_vol=0.20,
        fi_vol=0.08,
        cash_vol=0.015,
        inflation=0.06,
        color="#F59E0B",
        icon="🔥"
    ),
    'recession': ScenarioTemplate(
        name="Recession Path",
        description="Multi-year economic contraction with low returns",
        equity_return=0.02,
        fi_return=0.018,
        cash_return=0.008,
        equity_vol=0.25,
        fi_vol=0.07,
        cash_vol=0.012,
        inflation=0.015,
        color="#DC2626",
        icon="📉"
    ),
    'optimistic': ScenarioTemplate(
        name="Favorable Markets",
        description="Strong economic growth with robust returns",
        equity_return=0.10,
        fi_return=0.04,
        cash_return=0.02,
        equity_vol=0.16,
        fi_vol=0.055,
        cash_vol=0.008,
        inflation=0.022,
        color="#059669",
        icon="📈"
    )
}


class AssumptionValidator:
    """Validates retirement assumptions and surfaces warnings."""
    
    @staticmethod
    def validate_returns(equity_return: float, fi_return: float, 
                        cash_return: float, inflation: float) -> List[str]:
        """Validate return assumptions and generate warnings."""
        warnings = []
        
        # Real return checks
        equity_real = equity_return - inflation
        fi_real = fi_return - inflation
        cash_real = cash_return - inflation
        
        if equity_return < 0.03 or equity_return > 0.15:
            warnings.append(f"⚠️ Equity return of {equity_return:.1%} is outside typical range (3-15%)")
        
        if fi_return < 0.01 or fi_return > 0.08:
            warnings.append(f"⚠️ Fixed income return of {fi_return:.1%} is outside typical range (1-8%)")
        
        if cash_return < 0 or cash_return > 0.05:
            warnings.append(f"⚠️ Cash return of {cash_return:.1%} is outside typical range (0-5%)")
        
        if inflation < 0.01 or inflation > 0.08:
            warnings.append(f"⚠️ Inflation of {inflation:.1%} is outside typical range (1-8%)")
        
        # Real return warnings
        if equity_real < 0.02:
            warnings.append(f"⚠️ Real equity return ({equity_real:.1%}) is very low - may not meet growth needs")
        
        if fi_real < -0.01:
            warnings.append(f"⚠️ Real fixed income return ({fi_real:.1%}) is negative - consider inflation protection")
        
        if cash_real < -0.015:
            warnings.append(f"⚠️ Real cash return ({cash_real:.1%}) is significantly negative - cash drag risk")
        
        # Ordering checks
        if not (equity_return > fi_return > cash_return):
            warnings.append("⚠️ Expected return hierarchy violated (Equity > FI > Cash)")
        
        return warnings
    
    @staticmethod
    def validate_volatility(equity_vol: float, fi_vol: float, 
                           cash_vol: float) -> List[str]:
        """Validate volatility assumptions."""
        warnings = []
        
        if equity_vol < 0.08 or equity_vol > 0.40:
            warnings.append(f"⚠️ Equity volatility of {equity_vol:.1%} is outside typical range (8-40%)")
        
        if fi_vol < 0.02 or fi_vol > 0.15:
            warnings.append(f"⚠️ Fixed income volatility of {fi_vol:.1%} is outside typical range (2-15%)")
        
        if cash_vol > 0.03:
            warnings.append(f"⚠️ Cash volatility of {cash_vol:.1%} seems high for cash equivalents")
        
        if not (equity_vol > fi_vol > cash_vol):
            warnings.append("⚠️ Volatility hierarchy violated (Equity > FI > Cash)")
        
        return warnings
    
    @staticmethod
    def validate_allocation(equity_pct: float, fi_pct: float, 
                           cash_pct: float) -> List[str]:
        """Validate portfolio allocation."""
        warnings = []
        
        total = equity_pct + fi_pct + cash_pct
        if abs(total - 1.0) > 0.001:
            warnings.append(f"❌ Allocation must sum to 100% (currently {total:.1%})")
        
        if equity_pct > 0.90:
            warnings.append(f"⚠️ Equity allocation of {equity_pct:.1%} is very aggressive for retirement")
        
        if equity_pct < 0.20 and fi_pct + cash_pct > 0.80:
            warnings.append(f"⚠️ Very conservative allocation may not provide adequate growth")
        
        if cash_pct > 0.30:
            warnings.append(f"⚠️ Cash allocation of {cash_pct:.1%} is high - consider opportunity cost")
        
        return warnings
    
    @staticmethod
    def validate_spending(monthly_spending: float, starting_portfolio: float,
                         years_to_model: int) -> List[str]:
        """Validate spending assumptions."""
        warnings = []
        
        annual_spending = abs(monthly_spending) * 12
        withdrawal_rate = annual_spending / starting_portfolio if starting_portfolio > 0 else 0
        
        if withdrawal_rate > 0.05:
            warnings.append(f"⚠️ Initial withdrawal rate of {withdrawal_rate:.1%} exceeds 5% threshold")
        
        if withdrawal_rate > 0.06:
            warnings.append(f"🚨 Withdrawal rate of {withdrawal_rate:.1%} is very high - significant depletion risk")
        
        if withdrawal_rate < 0.02:
            warnings.append(f"ℹ️ Withdrawal rate of {withdrawal_rate:.1%} is conservative - may leave significant legacy")
        
        # Longevity check
        if years_to_model < 20:
            warnings.append(f"ℹ️ Planning horizon of {years_to_model} years may be short - consider longevity risk")
        
        if years_to_model > 40:
            warnings.append(f"ℹ️ Planning horizon of {years_to_model} years is extended - ensure inflation adjustments")
        
        return warnings
    
    @staticmethod
    def validate_all(equity_return: float, fi_return: float, cash_return: float,
                    equity_vol: float, fi_vol: float, cash_vol: float,
                    inflation: float, equity_pct: float, fi_pct: float,
                    cash_pct: float, monthly_spending: float,
                    starting_portfolio: float, years_to_model: int) -> Dict[str, List[str]]:
        """Run all validations and return categorized warnings."""
        
        return {
            'returns': AssumptionValidator.validate_returns(
                equity_return, fi_return, cash_return, inflation
            ),
            'volatility': AssumptionValidator.validate_volatility(
                equity_vol, fi_vol, cash_vol
            ),
            'allocation': AssumptionValidator.validate_allocation(
                equity_pct, fi_pct, cash_pct
            ),
            'spending': AssumptionValidator.validate_spending(
                monthly_spending, starting_portfolio, years_to_model
            )
        }


class ScenarioDifferential:
    """Analyze differences between scenarios to identify key drivers."""
    
    @staticmethod
    def calculate_scenario_diff(base_metrics: Dict, comparison_metrics: Dict) -> Dict:
        """Calculate key differences between two scenarios."""
        
        diffs = {
            'success_probability_diff': comparison_metrics.get('prob_never_depleted', 0) - base_metrics.get('prob_never_depleted', 0),
            'median_ending_diff': comparison_metrics.get('ending_median', 0) - base_metrics.get('ending_median', 0),
            'median_ending_pct': ((comparison_metrics.get('ending_median', 1) / base_metrics.get('ending_median', 1)) - 1) if base_metrics.get('ending_median', 0) > 0 else 0,
            'p10_diff': comparison_metrics.get('ending_p10', 0) - base_metrics.get('ending_p10', 0),
            'p90_diff': comparison_metrics.get('ending_p90', 0) - base_metrics.get('ending_p90', 0)
        }
        
        # Determine primary driver
        if abs(diffs['success_probability_diff']) > 0.10:
            diffs['primary_driver'] = 'Success Probability'
            diffs['driver_impact'] = diffs['success_probability_diff']
        elif abs(diffs['median_ending_pct']) > 0.25:
            diffs['primary_driver'] = 'Terminal Wealth'
            diffs['driver_impact'] = diffs['median_ending_pct']
        elif abs(diffs['p10_diff']) > base_metrics.get('starting_portfolio', 1) * 0.3:
            diffs['primary_driver'] = 'Downside Risk'
            diffs['driver_impact'] = diffs['p10_diff']
        else:
            diffs['primary_driver'] = 'Multiple Factors'
            diffs['driver_impact'] = diffs['median_ending_pct']
        
        return diffs
    
    @staticmethod
    def generate_diff_summary(diffs: Dict) -> str:
        """Generate human-readable summary of scenario differences."""
        
        success_diff = diffs['success_probability_diff'] * 100
        median_pct = diffs['median_ending_pct'] * 100
        
        if success_diff > 0:
            success_text = f"improves by {success_diff:.1f} percentage points"
        else:
            success_text = f"declines by {abs(success_diff):.1f} percentage points"
        
        if median_pct > 0:
            wealth_text = f"increases {median_pct:.1f}%"
        else:
            wealth_text = f"decreases {abs(median_pct):.1f}%"
        
        summary = f"""
**Key Differences:**
- Success probability {success_text}
- Median ending wealth {wealth_text}
- Primary driver: {diffs['primary_driver']}
        """.strip()
        
        return summary


def calculate_required_capital(annual_spending: float, 
                               withdrawal_rate: float = 0.04,
                               safety_margin: float = 1.25) -> Dict[str, float]:
    """
    Calculate required retirement capital based on spending needs.
    
    Returns multiple estimates based on different methodologies.
    """
    
    # Simple withdrawal rate method
    simple_capital = annual_spending / withdrawal_rate
    
    # With safety margin
    conservative_capital = simple_capital * safety_margin
    
    # Dynamic withdrawal (4-5% range)
    dynamic_low = annual_spending / 0.05
    dynamic_high = annual_spending / 0.04
    
    return {
        'simple_estimate': simple_capital,
        'conservative_estimate': conservative_capital,
        'dynamic_range_low': dynamic_low,
        'dynamic_range_high': dynamic_high,
        'recommended': conservative_capital
    }


def assess_glidepath(equity_pct: float, age: int, 
                     horizon_years: int) -> Dict[str, any]:
    """
    Assess if allocation follows recommended glidepath for retirement.
    
    Common rules:
    - 110 - age = equity allocation
    - 120 - age = aggressive
    - 100 - age = conservative
    """
    
    # Calculate suggested allocations
    conservative_equity = max(0.20, (100 - age) / 100)
    moderate_equity = max(0.30, (110 - age) / 100)
    aggressive_equity = max(0.40, (120 - age) / 100)
    
    # Determine current positioning
    if equity_pct < conservative_equity:
        position = "Very Conservative"
        color = "#10B981"
    elif equity_pct < moderate_equity:
        position = "Conservative"
        color = "#059669"
    elif equity_pct < aggressive_equity:
        position = "Moderate"
        color = "#1B3B5F"
    elif equity_pct < aggressive_equity * 1.15:
        position = "Aggressive"
        color = "#F59E0B"
    else:
        position = "Very Aggressive"
        color = "#EF4444"
    
    return {
        'current_equity': equity_pct,
        'conservative_target': conservative_equity,
        'moderate_target': moderate_equity,
        'aggressive_target': aggressive_equity,
        '100_minus_age': conservative_equity,
        '110_minus_age': moderate_equity,
        '120_minus_age': aggressive_equity,
        'position': position,
        'color': color,
        'deviation': equity_pct - moderate_equity
    }
