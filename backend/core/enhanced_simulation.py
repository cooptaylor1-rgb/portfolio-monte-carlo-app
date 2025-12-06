"""
Enhanced Monte Carlo Simulation with Stochastic Modeling
=========================================================

This module extends the base Monte Carlo engine with:
1. Stochastic inflation (Ornstein-Uhlenbeck process)
2. Probabilistic longevity (Gompertz-Makeham)
3. Correlated asset returns (Cholesky decomposition)
4. Sequence-of-returns risk analysis

Integrates Sprint 4 features into the main simulation workflow.
"""

import numpy as np
import logging
from typing import Optional, Tuple, Dict, Any, List
from dataclasses import dataclass, field

from core.monte_carlo_engine import (
    PortfolioInputs,
    SimulationResults,
    run_monte_carlo_simulation,
    generate_correlated_asset_returns,
    calculate_required_minimum_distribution
)
from core.stochastic_inflation import (
    StochasticInflationEngine,
    InflationRegime,
    InflationScenario
)
from core.longevity_engine import (
    LongevityEngine,
    LongevityParameters,
    Gender,
    HealthStatus
)
from core.report_generator import analyze_sequence_risk
from models.schemas import (
    StochasticInflationInputs,
    LongevityInputs,
    SequenceRiskAnalysis,
    InflationScenarioResult,
    LongevityResult,
    ExtendedSimulationResult,
    InflationRegimeEnum,
    GenderEnum,
    HealthStatusEnum
)

logger = logging.getLogger(__name__)


@dataclass
class EnhancedPortfolioInputs(PortfolioInputs):
    """
    Extended inputs that include stochastic modeling parameters.
    Inherits all base parameters from PortfolioInputs.
    """
    # Stochastic inflation parameters
    use_stochastic_inflation: bool = False
    inflation_regime: Optional[InflationRegime] = None
    inflation_volatility: float = 0.015
    inflation_mean_reversion: float = 0.3
    
    # Longevity parameters
    use_probabilistic_longevity: bool = False
    gender: Optional[Gender] = None
    health_status: HealthStatus = HealthStatus.AVERAGE
    smoker: bool = False
    planning_percentile: int = 90
    
    # Spouse information (for joint life)
    has_spouse: bool = False
    spouse_age: Optional[int] = None
    spouse_gender: Optional[Gender] = None
    spouse_health: HealthStatus = HealthStatus.AVERAGE
    spouse_smoker: bool = False
    
    # Analysis flags
    calculate_sequence_risk: bool = True


def run_enhanced_monte_carlo_simulation(
    inputs: EnhancedPortfolioInputs,
    inflation_seed: Optional[int] = None,
    longevity_seed: Optional[int] = None
) -> Tuple[SimulationResults, ExtendedSimulationResult]:
    """
    Run Monte Carlo simulation with optional stochastic enhancements.
    
    This function integrates:
    1. Stochastic inflation scenarios (if enabled)
    2. Probabilistic longevity analysis (if enabled)
    3. Sequence-of-returns risk analysis (always)
    4. Correlated asset returns (always)
    
    The simulation can operate in two modes:
    - LEGACY MODE: use_stochastic_inflation=False, use_probabilistic_longevity=False
      Behaves exactly like original run_monte_carlo_simulation()
    - ENHANCED MODE: One or both stochastic features enabled
      Uses realistic probabilistic modeling
    
    Args:
        inputs: Enhanced simulation parameters
        inflation_seed: Random seed for inflation generation
        longevity_seed: Random seed for longevity simulation
        
    Returns:
        Tuple of (base_results, extended_results)
        - base_results: Standard SimulationResults
        - extended_results: ExtendedSimulationResult with stochastic analysis
    """
    logger.info(f"=== ENHANCED MONTE CARLO SIMULATION ===")
    logger.info(f"Stochastic inflation: {inputs.use_stochastic_inflation}")
    logger.info(f"Probabilistic longevity: {inputs.use_probabilistic_longevity}")
    logger.info(f"Scenarios: {inputs.n_scenarios}, Years: {inputs.years_to_model}")
    
    # Initialize extended results container
    extended_results = ExtendedSimulationResult()
    
    # ============================================
    # PART 1: STOCHASTIC INFLATION ANALYSIS
    # ============================================
    inflation_scenarios: Optional[List[InflationScenario]] = None
    
    if inputs.use_stochastic_inflation:
        logger.info("Generating stochastic inflation scenarios...")
        
        inflation_engine = StochasticInflationEngine(seed=inflation_seed)
        regime = inputs.inflation_regime or InflationRegime.NORMAL
        
        # Generate inflation scenarios matching simulation scope
        inflation_scenarios = inflation_engine.generate_scenarios(
            n_scenarios=inputs.n_scenarios,
            n_months=inputs.years_to_model * 12,
            regime=regime,
            base_rate=inputs.inflation_annual,
            volatility=inputs.inflation_volatility,
            mean_reversion_speed=inputs.inflation_mean_reversion
        )
        
        # Convert to schema format for API response
        extended_results.inflation_scenarios = [
            InflationScenarioResult(
                scenario_id=i,
                final_inflation_rate=float(scenario.monthly_rates[-1] * 12),
                average_inflation=float(np.mean(scenario.monthly_rates) * 12),
                cumulative_inflation=float(scenario.cumulative_factor[-1]),
                percentile=None
            )
            for i, scenario in enumerate(inflation_scenarios[:10])  # Sample 10
        ]
        
        # Add percentile scenarios
        percentile_scenarios = inflation_engine.get_percentile_scenarios(
            inflation_scenarios, [10, 50, 90]
        )
        
        for percentile, scenario in percentile_scenarios.items():
            extended_results.inflation_scenarios.append(
                InflationScenarioResult(
                    scenario_id=999,
                    final_inflation_rate=float(scenario.monthly_rates[-1] * 12),
                    average_inflation=float(np.mean(scenario.monthly_rates) * 12),
                    cumulative_inflation=float(scenario.cumulative_factor[-1]),
                    percentile=percentile
                )
            )
        
        logger.info(f"✓ Generated {len(inflation_scenarios)} inflation scenarios")
        logger.info(f"  Mean inflation: {np.mean([s.monthly_rates[-1] * 12 for s in inflation_scenarios]):.2%}")
        logger.info(f"  90th percentile: {np.percentile([s.monthly_rates[-1] * 12 for s in inflation_scenarios], 90):.2%}")
    
    # ============================================
    # PART 2: PROBABILISTIC LONGEVITY ANALYSIS
    # ============================================
    longevity_result: Optional[LongevityResult] = None
    adjusted_years_to_model = inputs.years_to_model
    
    if inputs.use_probabilistic_longevity:
        logger.info("Running probabilistic longevity analysis...")
        
        longevity_engine = LongevityEngine(seed=longevity_seed)
        
        # Build primary parameters
        primary_params = LongevityParameters(
            current_age=inputs.current_age,
            gender=inputs.gender or Gender.MALE,
            health_status=inputs.health_status,
            smoker=inputs.smoker
        )
        
        # Simulate lifetimes
        death_ages = longevity_engine.simulate_lifetime(
            primary_params, 
            n_scenarios=10000
        )
        
        life_expectancy = np.mean(death_ages)
        median_age = np.median(death_ages)
        p75_age = np.percentile(death_ages, 75)
        p90_age = np.percentile(death_ages, 90)
        p95_age = np.percentile(death_ages, 95)
        
        # Get conservative planning horizon
        planning_age = longevity_engine.get_planning_horizon(
            primary_params,
            percentile=inputs.planning_percentile
        )
        
        years_of_risk = planning_age - life_expectancy
        
        # Calculate longevity risk premium
        annual_spending = abs(inputs.monthly_spending) * 12
        risk_metrics = longevity_engine.calculate_longevity_risk_premium(
            primary_params,
            annual_spending=annual_spending,
            percentile=inputs.planning_percentile
        )
        
        # Joint life analysis (if spouse)
        joint_life_exp = None
        joint_planning_horizon = None
        
        if inputs.has_spouse and inputs.spouse_age:
            spouse_params = LongevityParameters(
                current_age=inputs.spouse_age,
                gender=inputs.spouse_gender or Gender.FEMALE,
                health_status=inputs.spouse_health,
                smoker=inputs.spouse_smoker
            )
            
            first_death, second_death, survivor = longevity_engine.simulate_joint_lifetime(
                primary_params,
                spouse_params,
                n_scenarios=10000
            )
            
            joint_life_exp = np.mean(second_death)
            joint_planning_horizon = int(np.percentile(second_death, inputs.planning_percentile))
            
            logger.info(f"  Joint life expectancy: {joint_life_exp:.1f} years")
            logger.info(f"  Joint planning horizon: {joint_planning_horizon} years")
        
        # Build longevity result
        longevity_result = LongevityResult(
            life_expectancy=float(life_expectancy),
            median_age=float(median_age),
            p75_age=float(p75_age),
            p90_age=float(p90_age),
            p95_age=float(p95_age),
            planning_horizon_age=int(planning_age),
            years_of_longevity_risk=float(years_of_risk),
            longevity_risk_premium=float(risk_metrics['risk_premium_90']),
            joint_life_expectancy=float(joint_life_exp) if joint_life_exp else None,
            joint_planning_horizon=int(joint_planning_horizon) if joint_planning_horizon else None
        )
        
        extended_results.longevity_analysis = longevity_result
        
        # Adjust simulation horizon to planning horizon
        adjusted_years_to_model = planning_age - inputs.current_age
        inputs.years_to_model = adjusted_years_to_model
        
        logger.info(f"✓ Longevity analysis complete")
        logger.info(f"  Life expectancy: {life_expectancy:.1f} years")
        logger.info(f"  Planning horizon: {planning_age} years ({inputs.planning_percentile}th percentile)")
        logger.info(f"  Longevity risk premium: ${risk_metrics['risk_premium_90']:,.0f}")
        logger.info(f"  Adjusted simulation horizon: {adjusted_years_to_model} years")
    
    # ============================================
    # PART 3: RUN BASE MONTE CARLO SIMULATION
    # ============================================
    logger.info("Running base Monte Carlo simulation...")
    
    # Convert enhanced inputs back to base PortfolioInputs for simulation
    base_inputs = PortfolioInputs(
        starting_portfolio=inputs.starting_portfolio,
        years_to_model=adjusted_years_to_model,
        current_age=inputs.current_age,
        monthly_income=inputs.monthly_income,
        monthly_spending=inputs.monthly_spending,
        inflation_annual=inputs.inflation_annual,
        equity_pct=inputs.equity_pct,
        fi_pct=inputs.fi_pct,
        cash_pct=inputs.cash_pct,
        equity_return_annual=inputs.equity_return_annual,
        fi_return_annual=inputs.fi_return_annual,
        cash_return_annual=inputs.cash_return_annual,
        equity_vol_annual=inputs.equity_vol_annual,
        fi_vol_annual=inputs.fi_vol_annual,
        cash_vol_annual=inputs.cash_vol_annual,
        corr_equity_fi=inputs.corr_equity_fi,
        corr_equity_cash=inputs.corr_equity_cash,
        corr_fi_cash=inputs.corr_fi_cash,
        n_scenarios=inputs.n_scenarios,
        random_seed=inputs.random_seed,
        spending_rule=inputs.spending_rule,
        spending_pct_annual=inputs.spending_pct_annual,
        spending_floor=inputs.spending_floor,
        spending_ceiling=inputs.spending_ceiling,
        social_security_annual=inputs.social_security_annual,
        ss_start_age=inputs.ss_start_age,
        pension_annual=inputs.pension_annual,
        pension_start_age=inputs.pension_start_age,
        pension_cola=inputs.pension_cola,
        healthcare_annual=inputs.healthcare_annual,
        healthcare_start_age=inputs.healthcare_start_age,
        healthcare_inflation_real=inputs.healthcare_inflation_real,
        advisory_fee_pct=inputs.advisory_fee_pct,
        fund_expense_pct=inputs.fund_expense_pct,
        taxable_pct=inputs.taxable_pct,
        ira_pct=inputs.ira_pct,
        roth_pct=inputs.roth_pct,
        marginal_tax_rate=inputs.marginal_tax_rate,
        ltcg_tax_rate=inputs.ltcg_tax_rate,
        rmd_age=inputs.rmd_age,
        use_glide_path=inputs.use_glide_path,
        target_equity_at_end=inputs.target_equity_at_end,
        glide_path_type=inputs.glide_path_type,
        use_lifestyle_phases=inputs.use_lifestyle_phases,
        slow_go_age=inputs.slow_go_age,
        no_go_age=inputs.no_go_age,
        slow_go_spending_pct=inputs.slow_go_spending_pct,
        no_go_spending_pct=inputs.no_go_spending_pct,
        use_guardrails=inputs.use_guardrails,
        upper_guardrail=inputs.upper_guardrail,
        lower_guardrail=inputs.lower_guardrail,
        guardrail_adjustment=inputs.guardrail_adjustment
    )
    
    # Run the core simulation
    base_results = run_monte_carlo_simulation(base_inputs)
    
    logger.info(f"✓ Base simulation complete")
    logger.info(f"  Success probability: {base_results.success_probability:.1%}")
    logger.info(f"  Median ending: ${base_results.median_ending_value:,.0f}")
    
    # ============================================
    # PART 4: SEQUENCE-OF-RETURNS RISK ANALYSIS
    # ============================================
    if inputs.calculate_sequence_risk:
        logger.info("Analyzing sequence-of-returns risk...")
        
        sequence_analysis_dict = analyze_sequence_risk(
            all_paths=base_results.paths,
            years_to_model=adjusted_years_to_model,
            starting_portfolio=inputs.starting_portfolio
        )
        
        # Convert to schema
        extended_results.sequence_risk = SequenceRiskAnalysis(
            early_period_return=sequence_analysis_dict['early_period_return'],
            mid_period_return=sequence_analysis_dict['mid_period_return'],
            late_period_return=sequence_analysis_dict['late_period_return'],
            sequence_risk_score=sequence_analysis_dict['sequence_risk_score'],
            description=sequence_analysis_dict['description'],
            early_bear_market_impact=sequence_analysis_dict['early_bear_market_impact'],
            late_bear_market_impact=sequence_analysis_dict['late_bear_market_impact']
        )
        
        logger.info(f"✓ Sequence risk analysis complete")
        logger.info(f"  Risk score: {sequence_analysis_dict['sequence_risk_score']:.1f}/10")
        logger.info(f"  Risk level: {sequence_analysis_dict.get('risk_level', 'N/A')}")
    
    # ============================================
    # PART 5: RETURN COMPREHENSIVE RESULTS
    # ============================================
    logger.info("=== ENHANCED SIMULATION COMPLETE ===")
    
    return base_results, extended_results


def convert_stochastic_inputs_from_schema(
    base_inputs: PortfolioInputs,
    stochastic_inflation: Optional[StochasticInflationInputs] = None,
    longevity_params: Optional[LongevityInputs] = None,
    calculate_sequence_risk: bool = True
) -> EnhancedPortfolioInputs:
    """
    Convert base inputs + optional stochastic schemas to EnhancedPortfolioInputs.
    
    This is the bridge function for API integration.
    """
    # Map enums
    inflation_regime_map = {
        InflationRegimeEnum.NORMAL: InflationRegime.NORMAL,
        InflationRegimeEnum.HIGH: InflationRegime.HIGH,
        InflationRegimeEnum.DEFLATION: InflationRegime.DEFLATION,
        InflationRegimeEnum.VOLATILE: InflationRegime.VOLATILE
    }
    
    gender_map = {
        GenderEnum.MALE: Gender.MALE,
        GenderEnum.FEMALE: Gender.FEMALE
    }
    
    health_map = {
        HealthStatusEnum.POOR: HealthStatus.POOR,
        HealthStatusEnum.AVERAGE: HealthStatus.AVERAGE,
        HealthStatusEnum.GOOD: HealthStatus.GOOD,
        HealthStatusEnum.EXCELLENT: HealthStatus.EXCELLENT
    }
    
    # Build enhanced inputs
    enhanced = EnhancedPortfolioInputs(
        **base_inputs.__dict__,
        calculate_sequence_risk=calculate_sequence_risk
    )
    
    # Add stochastic inflation parameters
    if stochastic_inflation and stochastic_inflation.use_stochastic:
        enhanced.use_stochastic_inflation = True
        enhanced.inflation_regime = inflation_regime_map.get(stochastic_inflation.regime, InflationRegime.NORMAL)
        enhanced.inflation_volatility = stochastic_inflation.volatility
        enhanced.inflation_mean_reversion = stochastic_inflation.mean_reversion_speed
    
    # Add longevity parameters
    if longevity_params and longevity_params.use_probabilistic:
        enhanced.use_probabilistic_longevity = True
        enhanced.gender = gender_map.get(longevity_params.gender, Gender.MALE)
        enhanced.health_status = health_map.get(longevity_params.health_status, HealthStatus.AVERAGE)
        enhanced.smoker = longevity_params.smoker
        enhanced.planning_percentile = longevity_params.planning_percentile
        
        # Spouse
        if longevity_params.has_spouse:
            enhanced.has_spouse = True
            enhanced.spouse_age = longevity_params.spouse_age
            enhanced.spouse_gender = gender_map.get(longevity_params.spouse_gender, Gender.FEMALE) if longevity_params.spouse_gender else None
            enhanced.spouse_health = health_map.get(longevity_params.spouse_health, HealthStatus.AVERAGE)
            enhanced.spouse_smoker = longevity_params.spouse_smoker
    
    return enhanced
