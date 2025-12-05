"""
Monte Carlo simulation endpoints.
Core API for running portfolio projections and analysis.
"""
from fastapi import APIRouter, HTTPException
from models.schemas import (
    SimulationRequest,
    SimulationResponse,
    SimulationMetrics,
    ModelInputsModel,
    SensitivityRequest,
    SensitivityResponse,
    SensitivityResult
)
from core.simulation import (
    PortfolioInputs
)
from core.simulation_adapter import (
    run_monte_carlo_adapted as run_monte_carlo,
    calculate_metrics,
    calculate_goal_probabilities,
    sensitivity_analysis,
    get_new_engine_metrics
)
import logging

router = APIRouter()
logger = logging.getLogger(__name__)


def convert_model_to_dataclass(model: ModelInputsModel) -> PortfolioInputs:
    """Convert Pydantic model to dataclass for simulation engine"""
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
        n_scenarios=model.n_scenarios,
        spending_rule=int(model.spending_rule),
        spending_pct_annual=model.spending_pct_annual,
        social_security_monthly=model.social_security_monthly,
        ss_start_age=model.ss_start_age,
        pension_monthly=model.pension_monthly,
        pension_start_age=model.pension_start_age,
        monthly_healthcare=model.monthly_healthcare,
        healthcare_start_age=model.healthcare_start_age,
        healthcare_inflation=model.healthcare_inflation,
        taxable_pct=model.taxable_pct,
        ira_pct=model.ira_pct,
        roth_pct=model.roth_pct,
        tax_rate=model.tax_rate,
        rmd_age=model.rmd_age,
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


@router.post("/run", response_model=SimulationResponse)
async def run_simulation(request: SimulationRequest):
    """
    Run Monte Carlo portfolio simulation.
    
    This endpoint executes a full Monte Carlo simulation based on the provided
    parameters and returns comprehensive metrics and statistics.
    
    **Parameters:**
    - client_info: Client demographic information
    - inputs: Simulation parameters (portfolio, spending, returns, etc.)
    - financial_goals: Optional list of goals to track
    - stress_scenarios: Optional stress test scenarios
    - seed: Optional random seed for reproducibility
    
    **Returns:**
    - metrics: Key performance indicators
    - stats: Monthly statistics (percentiles)
    - goal_probabilities: Achievement probabilities for each goal
    """
    try:
        logger.info(f"=== SIMULATION REQUEST RECEIVED ===")
        logger.info(f"Client: {request.client_info.client_name}")
        logger.info(f"Request data: {request.model_dump()}")
        
        # Validate allocation sums to 1.0
        total_allocation = (
            request.inputs.equity_pct +
            request.inputs.fi_pct +
            request.inputs.cash_pct
        )
        if abs(total_allocation - 1.0) > 0.01:
            raise HTTPException(
                status_code=400,
                detail=f"Asset allocation must sum to 1.0, got {total_allocation}"
            )
        
        # Convert to simulation input format
        sim_inputs = convert_model_to_dataclass(request.inputs)
        
        # Run Monte Carlo simulation
        paths_df, stats_df = run_monte_carlo(sim_inputs, seed=request.seed)
        
        # Calculate metrics
        metrics = calculate_metrics(paths_df, stats_df)
        
        # Get new engine metrics if available
        new_results = get_new_engine_metrics(paths_df)
        if new_results:
            metrics['annual_ruin_probability'] = new_results.annual_ruin_probability
            metrics['cumulative_ruin_probability'] = new_results.cumulative_ruin_probability
            metrics['longevity_metrics'] = new_results.longevity_metrics
            logger.info(f"New engine metrics included: {len(new_results.annual_ruin_probability)} years")
        
        # Calculate goal probabilities if provided
        goal_probs = None
        if request.financial_goals:
            goals = [
                {
                    "name": g.name,
                    "target_amount": g.target_amount,
                    "target_age": g.target_age
                }
                for g in request.financial_goals
            ]
            goal_probs = calculate_goal_probabilities(
                paths_df,
                goals,
                request.inputs.current_age
            )
        
        # Convert stats to list of dictionaries
        stats_list = stats_df.to_dict('records')
        
        logger.info(f"Simulation completed - Success probability: {metrics['success_probability']:.2%}")
        
        return SimulationResponse(
            metrics=SimulationMetrics(**metrics),
            stats=stats_list,
            goal_probabilities=goal_probs,
            inputs=request.inputs,
            success=True,
            message="Simulation completed successfully"
        )
        
    except ValueError as e:
        logger.error(f"Validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Simulation error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Simulation failed: {str(e)}")


@router.post("/sensitivity", response_model=SensitivityResponse)
async def run_sensitivity_analysis(request: SensitivityRequest):
    """
    Run sensitivity analysis on a specific parameter.
    
    Tests how changes in a single parameter affect simulation outcomes.
    
    **Parameters:**
    - inputs: Base simulation parameters
    - parameter: Name of parameter to vary (e.g., 'equity_return_annual')
    - variations: List of values to test for the parameter
    
    **Returns:**
    - results: List of outcomes for each parameter value
    """
    try:
        sim_inputs = convert_model_to_dataclass(request.inputs)
        
        # Verify parameter exists
        if not hasattr(sim_inputs, request.parameter):
            raise HTTPException(
                status_code=400,
                detail=f"Invalid parameter: {request.parameter}"
            )
        
        # Run sensitivity analysis
        results_df = sensitivity_analysis(sim_inputs, request.parameter, request.variations)
        
        # Convert to response model
        results = [
            SensitivityResult(
                parameter_value=row['parameter_value'],
                success_probability=row['success_probability'],
                ending_median=row['ending_median'],
                depletion_probability=row['depletion_probability']
            )
            for _, row in results_df.iterrows()
        ]
        
        return SensitivityResponse(
            success=True,
            parameter=request.parameter,
            results=results
        )
        
    except Exception as e:
        logger.error(f"Sensitivity analysis error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/validate")
async def validate_inputs(inputs: ModelInputsModel):
    """
    Validate simulation inputs without running full simulation.
    
    Performs comprehensive validation and returns any errors or warnings.
    
    **Returns:**
    - is_valid: Boolean indicating if inputs are valid
    - errors: List of validation errors
    - warnings: List of warnings (non-blocking issues)
    """
    errors = []
    warnings = []
    
    # Check allocation
    total_allocation = inputs.equity_pct + inputs.fi_pct + inputs.cash_pct
    if abs(total_allocation - 1.0) > 0.01:
        errors.append(f"Asset allocation must sum to 1.0, currently {total_allocation:.2%}")
    
    # Check age logic
    if inputs.horizon_age <= inputs.current_age:
        errors.append("Horizon age must be greater than current age")
    
    # Check spending
    if inputs.spending_rule == 1 and inputs.monthly_spending >= 0:
        warnings.append("Monthly spending should typically be negative (withdrawal)")
    
    # Check return assumptions
    if inputs.equity_return_annual < inputs.fi_return_annual:
        warnings.append("Equity returns are typically higher than fixed income returns")
    
    if inputs.equity_return_annual > 0.20:
        warnings.append("Equity return assumption above 20% is unusually aggressive")
    
    # Check volatility
    if inputs.equity_vol_annual < inputs.fi_vol_annual:
        warnings.append("Equity volatility is typically higher than fixed income volatility")
    
    return {
        "is_valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings
    }
