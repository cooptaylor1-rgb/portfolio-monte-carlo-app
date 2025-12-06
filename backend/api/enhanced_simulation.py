"""
Enhanced simulation endpoints with stochastic modeling.
Provides API access to Sprint 4 advanced features.
"""
from fastapi import APIRouter, HTTPException
from typing import Optional
import numpy as np
import logging

from models.schemas import (
    SimulationRequest,
    SimulationResponse,
    SimulationMetrics,
    ExtendedModelInputs,
    ExtendedSimulationResult,
    StochasticInflationInputs,
    LongevityInputs
)
from core.monte_carlo_engine import PortfolioInputs
from core.enhanced_simulation import (
    run_enhanced_monte_carlo_simulation,
    convert_stochastic_inputs_from_schema
)
from core.simulation_adapter import (
    calculate_metrics,
    calculate_goal_probabilities
)

router = APIRouter()
logger = logging.getLogger(__name__)


def convert_extended_model_to_dataclass(model: ExtendedModelInputs) -> PortfolioInputs:
    """Convert ExtendedModelInputs to base PortfolioInputs dataclass"""
    # Convert monthly to annual for social security and pension
    ss_annual = model.social_security_monthly * 12 if hasattr(model, 'social_security_monthly') else 0.0
    pension_annual = model.pension_monthly * 12 if hasattr(model, 'pension_monthly') else 0.0
    healthcare_annual = model.monthly_healthcare * 12 if hasattr(model, 'monthly_healthcare') else 0.0
    
    return PortfolioInputs(
        starting_portfolio=model.starting_portfolio,
        years_to_model=model.years_to_model,
        current_age=model.current_age,
        monthly_income=model.monthly_income,
        monthly_spending=model.monthly_spending,
        inflation_annual=model.inflation_annual,
        equity_pct=model.equity_pct,
        fi_pct=model.fi_pct,
        cash_pct=model.cash_pct,
        equity_return_annual=model.equity_return_annual,
        fi_return_annual=model.fi_return_annual,
        cash_return_annual=model.cash_return_annual,
        equity_vol_annual=model.equity_vol_annual,
        fi_vol_annual=model.fi_vol_annual,
        cash_vol_annual=model.cash_vol_annual,
        corr_equity_fi=model.corr_equity_fi,
        corr_equity_cash=model.corr_equity_cash,
        corr_fi_cash=model.corr_fi_cash,
        n_scenarios=model.n_scenarios,
        spending_rule=int(model.spending_rule),
        spending_pct_annual=model.spending_pct_annual,
        # Income sources - convert monthly to annual
        social_security_annual=ss_annual,
        ss_start_age=getattr(model, 'ss_start_age', 67),
        pension_annual=pension_annual,
        pension_start_age=getattr(model, 'pension_start_age', 65),
        pension_cola=0.0,
        # Healthcare - convert monthly to annual
        healthcare_annual=healthcare_annual,
        healthcare_start_age=getattr(model, 'healthcare_start_age', 65),
        healthcare_inflation_real=getattr(model, 'healthcare_inflation', 0.05) - model.inflation_annual,
        # Fees
        advisory_fee_pct=0.0075,
        fund_expense_pct=0.0025,
        # Tax
        taxable_pct=model.taxable_pct,
        ira_pct=model.ira_pct,
        roth_pct=model.roth_pct,
        marginal_tax_rate=getattr(model, 'tax_rate', 0.25),
        ltcg_tax_rate=0.15,
        rmd_age=getattr(model, 'rmd_age', 73),
        # Advanced features
        use_glide_path=model.use_glide_path,
        target_equity_at_end=model.target_equity_at_end,
        use_lifestyle_phases=model.use_lifestyle_phases,
        slow_go_age=model.slow_go_age,
        no_go_age=model.no_go_age,
        slow_go_spending_pct=model.slow_go_spending_pct,
        no_go_spending_pct=model.no_go_spending_pct,
        use_guardrails=model.use_guardrails,
        upper_guardrail=model.upper_guardrail,
        lower_guardrail=model.lower_guardrail
    )


@router.post("/run-enhanced", response_model=SimulationResponse)
async def run_enhanced_simulation(request: SimulationRequest):
    """
    Run enhanced Monte Carlo simulation with stochastic modeling.
    
    This endpoint provides access to Sprint 4 advanced features:
    - **Stochastic Inflation**: Ornstein-Uhlenbeck mean-reverting process
    - **Probabilistic Longevity**: Gompertz-Makeham mortality model
    - **Correlated Returns**: Cholesky decomposition for realistic diversification
    - **Sequence Risk**: Early vs late bear market impact analysis
    
    **Enhanced Parameters:**
    - inputs: Can be ExtendedModelInputs with stochastic_inflation and longevity_params
    - stochastic_inflation: Optional inflation regime settings
    - longevity_params: Optional gender/health/smoking inputs
    
    **Enhanced Returns:**
    - All standard SimulationResponse fields
    - Plus: sequence_risk, inflation_scenarios, longevity_analysis
    
    **Example Request:**
    ```json
    {
        "client_info": {...},
        "inputs": {
            ...base parameters...,
            "stochastic_inflation": {
                "use_stochastic": true,
                "regime": "normal",
                "volatility": 0.015
            },
            "longevity_params": {
                "use_probabilistic": true,
                "gender": "male",
                "health_status": "good",
                "smoker": false,
                "planning_percentile": 90
            }
        }
    }
    ```
    """
    try:
        logger.info(f"=== ENHANCED SIMULATION REQUEST ===")
        logger.info(f"Client: {request.client_info.client_name}")
        
        # Check if inputs include stochastic parameters
        inputs = request.inputs
        stochastic_inflation = None
        longevity_params = None
        
        if isinstance(inputs, ExtendedModelInputs):
            stochastic_inflation = inputs.stochastic_inflation
            longevity_params = inputs.longevity_params
            logger.info(f"Stochastic inflation: {stochastic_inflation.use_stochastic if stochastic_inflation else False}")
            logger.info(f"Probabilistic longevity: {longevity_params.use_probabilistic if longevity_params else False}")
        
        # Convert to base PortfolioInputs
        if isinstance(inputs, ExtendedModelInputs):
            base_inputs = convert_extended_model_to_dataclass(inputs)
        else:
            # Fallback for standard ModelInputsModel
            from api.simulation import convert_model_to_dataclass
            base_inputs = convert_model_to_dataclass(inputs)
        
        # Convert to EnhancedPortfolioInputs if stochastic features requested
        if stochastic_inflation or longevity_params:
            enhanced_inputs = convert_stochastic_inputs_from_schema(
                base_inputs,
                stochastic_inflation=stochastic_inflation,
                longevity_params=longevity_params,
                calculate_sequence_risk=True
            )
            
            # Run enhanced simulation
            base_results, extended_results = run_enhanced_monte_carlo_simulation(
                enhanced_inputs,
                inflation_seed=request.seed,
                longevity_seed=request.seed
            )
        else:
            # Fall back to standard simulation
            logger.info("No stochastic features requested, running standard simulation")
            from core.simulation_adapter import run_monte_carlo_adapted
            base_results = run_monte_carlo_adapted(base_inputs, seed=request.seed)
            
            # Create empty extended results
            extended_results = ExtendedSimulationResult()
        
        # Calculate metrics
        metrics = calculate_metrics(base_results, base_inputs)
        
        # Calculate goal probabilities if goals provided
        goal_probs = {}
        if request.financial_goals:
            goal_probs = calculate_goal_probabilities(
                base_results,
                request.financial_goals,
                base_inputs.starting_portfolio,
                base_inputs.current_age
            )
        
        # Prepare monthly stats for response
        monthly_stats = base_results.monthly_stats.to_dict(orient='records')
        
        # Build response
        response = SimulationResponse(
            success=True,
            message="Enhanced simulation completed successfully",
            metrics=metrics,
            stats=monthly_stats,
            goal_probabilities=goal_probs,
            ending_distribution=base_results.ending_distribution,
            worst_case_path=base_results.worst_case_path.tolist(),
            best_case_path=base_results.best_case_path.tolist(),
            median_path=base_results.median_path.tolist(),
            # Extended results
            sequence_risk=extended_results.sequence_risk,
            inflation_scenarios=extended_results.inflation_scenarios,
            longevity_analysis=extended_results.longevity_analysis
        )
        
        logger.info(f"✓ Enhanced simulation complete")
        logger.info(f"  Success probability: {metrics.success_probability:.1%}")
        logger.info(f"  Median ending: ${metrics.median_ending:,.0f}")
        
        if extended_results.sequence_risk:
            logger.info(f"  Sequence risk score: {extended_results.sequence_risk.sequence_risk_score:.1f}/10")
        if extended_results.longevity_analysis:
            logger.info(f"  Planning horizon: {extended_results.longevity_analysis.planning_horizon_age} years")
        
        return response
        
    except ValueError as e:
        logger.error(f"Validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Simulation error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Simulation failed: {str(e)}")


@router.post("/analyze-inflation", response_model=dict)
async def analyze_inflation_scenarios(
    regime: str = "normal",
    n_scenarios: int = 1000,
    n_years: int = 30,
    base_rate: float = 0.025,
    volatility: float = 0.015,
    seed: Optional[int] = None
):
    """
    Generate and analyze stochastic inflation scenarios.
    
    Standalone endpoint for inflation analysis without full simulation.
    Useful for exploring different inflation regimes and their distributions.
    
    **Parameters:**
    - regime: "normal", "high", "deflation", or "volatile"
    - n_scenarios: Number of paths to generate
    - n_years: Time horizon in years
    - base_rate: Starting inflation rate
    - volatility: Inflation volatility parameter
    - seed: Random seed for reproducibility
    
    **Returns:**
    - Distribution statistics (mean, percentiles)
    - Sample scenarios
    - Stress test results
    """
    try:
        from core.stochastic_inflation import StochasticInflationEngine, InflationRegime
        
        logger.info(f"Analyzing inflation scenarios: {regime}, {n_scenarios} paths, {n_years} years")
        
        # Map regime string to enum
        regime_map = {
            "normal": InflationRegime.NORMAL,
            "high": InflationRegime.HIGH,
            "deflation": InflationRegime.DEFLATION,
            "volatile": InflationRegime.VOLATILE
        }
        
        inflation_regime = regime_map.get(regime.lower(), InflationRegime.NORMAL)
        
        # Generate scenarios
        engine = StochasticInflationEngine(seed=seed)
        scenarios = engine.generate_scenarios(
            n_scenarios=n_scenarios,
            n_months=n_years * 12,
            regime=inflation_regime,
            base_rate=base_rate,
            volatility=volatility
        )
        
        # Calculate statistics
        final_rates = [s.monthly_rates[-1] * 12 for s in scenarios]
        avg_rates = [np.mean(s.monthly_rates) * 12 for s in scenarios]
        cumulative_factors = [s.cumulative_factor[-1] for s in scenarios]
        
        # Generate stress scenarios
        stress_scenarios = engine.generate_stress_scenarios(
            n_months=n_years * 12,
            base_rate=base_rate
        )
        
        return {
            "success": True,
            "regime": regime,
            "n_scenarios": n_scenarios,
            "n_years": n_years,
            "statistics": {
                "final_inflation": {
                    "mean": float(np.mean(final_rates)),
                    "median": float(np.median(final_rates)),
                    "p10": float(np.percentile(final_rates, 10)),
                    "p25": float(np.percentile(final_rates, 25)),
                    "p75": float(np.percentile(final_rates, 75)),
                    "p90": float(np.percentile(final_rates, 90)),
                    "std": float(np.std(final_rates))
                },
                "average_inflation": {
                    "mean": float(np.mean(avg_rates)),
                    "median": float(np.median(avg_rates)),
                    "p10": float(np.percentile(avg_rates, 10)),
                    "p90": float(np.percentile(avg_rates, 90))
                },
                "cumulative_inflation": {
                    "mean": float(np.mean(cumulative_factors)),
                    "median": float(np.median(cumulative_factors)),
                    "p10": float(np.percentile(cumulative_factors, 10)),
                    "p90": float(np.percentile(cumulative_factors, 90))
                }
            },
            "stress_scenarios": {
                name: {
                    "final_rate": float(scenario.monthly_rates[-1] * 12),
                    "average_rate": float(np.mean(scenario.monthly_rates) * 12),
                    "cumulative_factor": float(scenario.cumulative_factor[-1])
                }
                for name, scenario in stress_scenarios.items()
            },
            "sample_scenarios": [
                {
                    "scenario_id": i,
                    "final_rate": float(scenarios[i].monthly_rates[-1] * 12),
                    "average_rate": float(np.mean(scenarios[i].monthly_rates) * 12),
                    "cumulative_factor": float(scenarios[i].cumulative_factor[-1])
                }
                for i in range(min(10, len(scenarios)))
            ]
        }
        
    except Exception as e:
        logger.error(f"Inflation analysis error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/analyze-longevity", response_model=dict)
async def analyze_longevity(
    current_age: int = 65,
    gender: str = "male",
    health_status: str = "average",
    smoker: bool = False,
    has_spouse: bool = False,
    spouse_age: Optional[int] = None,
    spouse_gender: Optional[str] = None,
    spouse_health: Optional[str] = "average",
    spouse_smoker: bool = False,
    annual_spending: float = 80000,
    seed: Optional[int] = None
):
    """
    Analyze probabilistic longevity and calculate planning horizons.
    
    Standalone endpoint for longevity analysis without full simulation.
    Provides life expectancy, planning horizons, and longevity risk premium.
    
    **Parameters:**
    - current_age: Client's current age
    - gender: "male" or "female"
    - health_status: "poor", "average", "good", or "excellent"
    - smoker: Smoking status
    - has_spouse: Whether to include spouse in joint life analysis
    - spouse_*: Spouse demographics (if has_spouse=True)
    - annual_spending: For calculating longevity risk premium
    - seed: Random seed
    
    **Returns:**
    - Life expectancy and percentiles
    - Planning horizons (75th, 90th, 95th percentile ages)
    - Longevity risk premium (extra capital needed for tail risk)
    - Joint life metrics (if spouse included)
    """
    try:
        from core.longevity_engine import (
            LongevityEngine, 
            LongevityParameters, 
            Gender, 
            HealthStatus
        )
        
        logger.info(f"Analyzing longevity: age {current_age}, {gender}, {health_status}")
        
        # Map strings to enums
        gender_map = {"male": Gender.MALE, "female": Gender.FEMALE}
        health_map = {
            "poor": HealthStatus.POOR,
            "average": HealthStatus.AVERAGE,
            "good": HealthStatus.GOOD,
            "excellent": HealthStatus.EXCELLENT
        }
        
        # Build primary parameters
        primary_gender = gender_map.get(gender.lower(), Gender.MALE)
        primary_health = health_map.get(health_status.lower(), HealthStatus.AVERAGE)
        
        primary_params = LongevityParameters(
            current_age=current_age,
            gender=primary_gender,
            health_status=primary_health,
            smoker=smoker
        )
        
        # Run analysis
        engine = LongevityEngine(seed=seed)
        
        death_ages = engine.simulate_lifetime(primary_params, n_scenarios=10000)
        
        life_exp = float(np.mean(death_ages))
        median_age = float(np.median(death_ages))
        p75 = float(np.percentile(death_ages, 75))
        p90 = float(np.percentile(death_ages, 90))
        p95 = float(np.percentile(death_ages, 95))
        
        # Planning horizons
        horizon_75 = engine.get_planning_horizon(primary_params, 75)
        horizon_90 = engine.get_planning_horizon(primary_params, 90)
        horizon_95 = engine.get_planning_horizon(primary_params, 95)
        
        # Risk premium
        risk_metrics_90 = engine.calculate_longevity_risk_premium(
            primary_params, annual_spending, percentile=90
        )
        
        result = {
            "success": True,
            "primary": {
                "life_expectancy": life_exp,
                "median_age": median_age,
                "p75_age": p75,
                "p90_age": p90,
                "p95_age": p95,
                "planning_horizons": {
                    "p75": int(horizon_75),
                    "p90": int(horizon_90),
                    "p95": int(horizon_95)
                },
                "longevity_risk": {
                    "years_beyond_life_expectancy": float(risk_metrics_90['years_beyond_life_expectancy']),
                    "risk_premium_90": float(risk_metrics_90['risk_premium_90'])
                }
            }
        }
        
        # Joint life analysis
        if has_spouse and spouse_age:
            spouse_g = gender_map.get((spouse_gender or "female").lower(), Gender.FEMALE)
            spouse_h = health_map.get((spouse_health or "average").lower(), HealthStatus.AVERAGE)
            
            spouse_params = LongevityParameters(
                current_age=spouse_age,
                gender=spouse_g,
                health_status=spouse_h,
                smoker=spouse_smoker
            )
            
            first_death, second_death, survivor = engine.simulate_joint_lifetime(
                primary_params, spouse_params, n_scenarios=10000
            )
            
            joint_life_exp = float(np.mean(second_death))
            joint_planning_90 = int(np.percentile(second_death, 90))
            
            result["joint"] = {
                "joint_life_expectancy": joint_life_exp,
                "first_death_age": {
                    "mean": float(np.mean(first_death)),
                    "median": float(np.median(first_death)),
                    "p10": float(np.percentile(first_death, 10)),
                    "p90": float(np.percentile(first_death, 90))
                },
                "second_death_age": {
                    "mean": joint_life_exp,
                    "median": float(np.median(second_death)),
                    "p10": float(np.percentile(second_death, 10)),
                    "p90": float(np.percentile(second_death, 90))
                },
                "joint_planning_horizon": joint_planning_90,
                "years_beyond_primary_life_expectancy": joint_life_exp - life_exp
            }
        
        return result
        
    except Exception as e:
        logger.error(f"Longevity analysis error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
