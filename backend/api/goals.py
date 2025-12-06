"""
Goal-Based Planning API Endpoints

Provides REST API for goal-based financial planning:
- POST /analyze: Analyze multiple financial goals
- GET /health: Health check

Author: Salem Investment Counselors
Last Updated: December 2024
"""

from fastapi import APIRouter, HTTPException
from typing import List
import logging

from models.schemas import (
    GoalAnalysisRequest,
    GoalAnalysisResponse,
    GoalResultModel,
    GoalConflictModel,
    GoalInputModel,
    GoalPriorityEnum,
    GoalStatusEnum
)
from core.goal_engine import (
    GoalEngine,
    FinancialGoal,
    GoalPriority,
    GoalStatus
)

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/goals",
    tags=["goal-planning"],
    responses={404: {"description": "Not found"}},
)


@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "goal-planning"}


@router.post("/analyze", response_model=GoalAnalysisResponse)
async def analyze_goals(request: GoalAnalysisRequest):
    """
    Analyze financial goals and return probability of success for each goal.
    
    Runs Monte Carlo simulation for each goal independently, considering:
    - Goal-specific asset allocation
    - Glide path (if enabled)
    - Current funding and contribution schedule
    - Time horizon
    
    Returns:
    - Per-goal success probability
    - Funding recommendations
    - Conflict detection (competing priorities, funding gaps)
    """
    try:
        logger.info(f"Analyzing {len(request.goals)} goals")
        
        # Validate request
        if not request.goals:
            raise HTTPException(status_code=400, detail="At least one goal is required")
        
        # Initialize goal engine
        engine = GoalEngine(
            current_year=request.current_year,
            default_equity_return=request.equity_return_annual or 0.07,
            default_fi_return=request.fi_return_annual or 0.02,
            default_cash_return=request.cash_return_annual or 0.00,
            default_equity_vol=request.equity_volatility or 0.18,
            default_fi_vol=request.fi_volatility or 0.06,
            default_cash_vol=request.cash_volatility or 0.01,
            n_scenarios=request.n_scenarios,
        )
        
        # Convert API models to engine models and add goals
        for goal_input in request.goals:
            goal = _convert_to_financial_goal(goal_input, request.current_year)
            engine.add_goal(goal)
        
        # Run simulations
        results = engine.simulate_all_goals()
        
        # Check for conflicts
        conflicts = engine.check_goal_conflicts()
        
        # Convert results to API models
        goal_results = [_convert_to_goal_result_model(result) for result in results]
        conflict_models = [_convert_to_conflict_model(conflict) for conflict in conflicts]
        
        # Calculate summary statistics
        total_funding_needed = sum(r.additional_funding_needed for r in goal_results)
        critical_count = sum(1 for r in goal_results if r.priority == GoalPriorityEnum.CRITICAL)
        on_track_count = sum(1 for r in goal_results if r.status == GoalStatusEnum.ON_TRACK)
        at_risk_count = sum(1 for r in goal_results if r.status in [
            GoalStatusEnum.AT_RISK, 
            GoalStatusEnum.UNDERFUNDED, 
            GoalStatusEnum.CRITICAL
        ])
        
        # Generate overall summary
        summary = _generate_overall_summary(goal_results, conflict_models)
        
        response = GoalAnalysisResponse(
            goals=goal_results,
            conflicts=conflict_models,
            overall_summary=summary,
            total_annual_funding_needed=total_funding_needed,
            critical_goals_count=critical_count,
            on_track_count=on_track_count,
            at_risk_count=at_risk_count,
        )
        
        logger.info(f"Analysis complete: {on_track_count}/{len(goal_results)} goals on track")
        return response
        
    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error analyzing goals: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


def _convert_to_financial_goal(goal_input: GoalInputModel, current_year: int) -> FinancialGoal:
    """Convert API model to engine model"""
    # Map API priority enum to engine enum
    priority_map = {
        GoalPriorityEnum.CRITICAL: GoalPriority.CRITICAL,
        GoalPriorityEnum.HIGH: GoalPriority.HIGH,
        GoalPriorityEnum.MEDIUM: GoalPriority.MEDIUM,
        GoalPriorityEnum.LOW: GoalPriority.LOW,
    }
    
    return FinancialGoal(
        name=goal_input.name,
        target_amount=goal_input.target_amount,
        target_year=goal_input.target_year,
        priority=priority_map[goal_input.priority],
        current_funding=goal_input.current_funding,
        annual_contribution=goal_input.annual_contribution,
        contribution_start_year=goal_input.contribution_start_year,
        contribution_end_year=goal_input.contribution_end_year,
        equity_pct=goal_input.equity_pct,
        fi_pct=goal_input.fi_pct,
        cash_pct=goal_input.cash_pct,
        use_glide_path=goal_input.use_glide_path,
        years_before_goal_to_derisk=goal_input.years_before_goal_to_derisk,
        target_equity_at_goal=goal_input.target_equity_at_goal,
        success_threshold=goal_input.success_threshold,
        acceptable_shortfall_pct=goal_input.acceptable_shortfall_pct,
        id=goal_input.id,
        notes=goal_input.notes,
    )


def _convert_to_goal_result_model(result) -> GoalResultModel:
    """Convert engine result to API model"""
    # Map engine status enum to API enum
    status_map = {
        GoalStatus.ON_TRACK: GoalStatusEnum.ON_TRACK,
        GoalStatus.AT_RISK: GoalStatusEnum.AT_RISK,
        GoalStatus.UNDERFUNDED: GoalStatusEnum.UNDERFUNDED,
        GoalStatus.CRITICAL: GoalStatusEnum.CRITICAL,
        GoalStatus.ACHIEVED: GoalStatusEnum.ACHIEVED,
        GoalStatus.ABANDONED: GoalStatusEnum.ABANDONED,
    }
    
    priority_map = {
        GoalPriority.CRITICAL: GoalPriorityEnum.CRITICAL,
        GoalPriority.HIGH: GoalPriorityEnum.HIGH,
        GoalPriority.MEDIUM: GoalPriorityEnum.MEDIUM,
        GoalPriority.LOW: GoalPriorityEnum.LOW,
    }
    
    return GoalResultModel(
        goal_name=result.goal.name,
        goal_id=result.goal.id,
        priority=priority_map[result.goal.priority],
        status=status_map[result.status],
        target_amount=result.goal.target_amount,
        target_year=result.goal.target_year,
        years_remaining=result.goal.years_until_goal(2024),  # TODO: use current_year from request
        probability_of_success=result.probability_of_success,
        median_value_at_target=result.median_value_at_target,
        percentile_10=result.percentile_10_value,
        percentile_90=result.percentile_90_value,
        current_funding_pct=result.current_funding_pct,
        expected_shortfall=result.expected_shortfall,
        shortfall_probability=result.shortfall_probability,
        additional_funding_needed=result.additional_funding_needed,
        recommendation=result.recommendation,
        scenarios_succeeded=result.scenarios_succeeded,
        scenarios_failed=result.scenarios_failed,
    )


def _convert_to_conflict_model(conflict: dict) -> GoalConflictModel:
    """Convert engine conflict dict to API model"""
    return GoalConflictModel(
        conflict_type=conflict['type'],
        description=conflict['description'],
        goals_affected=conflict['goals_affected'],
        total_funding_gap=conflict.get('total_funding_gap'),
        recommendation=conflict['recommendation'],
    )


def _generate_overall_summary(
    goals: List[GoalResultModel],
    conflicts: List[GoalConflictModel]
) -> str:
    """Generate human-readable overall summary"""
    total_goals = len(goals)
    on_track = sum(1 for g in goals if g.status == GoalStatusEnum.ON_TRACK)
    at_risk = sum(1 for g in goals if g.status == GoalStatusEnum.AT_RISK)
    critical = sum(1 for g in goals if g.status in [GoalStatusEnum.CRITICAL, GoalStatusEnum.UNDERFUNDED])
    
    # Overall status
    if on_track == total_goals:
        overall_status = "All goals are on track! Continue current funding strategy."
    elif on_track >= total_goals * 0.75:
        overall_status = f"Most goals ({on_track}/{total_goals}) are on track."
    elif critical >= total_goals * 0.5:
        overall_status = f"Portfolio needs attention: {critical} goals critically underfunded."
    else:
        overall_status = f"Mixed results: {on_track} on track, {at_risk} at risk, {critical} critical."
    
    # Priority analysis
    critical_priority_goals = [g for g in goals if g.priority == GoalPriorityEnum.CRITICAL]
    critical_priority_at_risk = [
        g for g in critical_priority_goals 
        if g.status != GoalStatusEnum.ON_TRACK
    ]
    
    priority_note = ""
    if critical_priority_at_risk:
        priority_note = f" IMPORTANT: {len(critical_priority_at_risk)} critical-priority goals need attention."
    
    # Funding summary
    total_funding_needed = sum(g.additional_funding_needed for g in goals)
    funding_note = ""
    if total_funding_needed > 0:
        funding_note = f" Additional annual funding needed: ${total_funding_needed:,.0f}."
    
    # Conflicts
    conflict_note = ""
    if conflicts:
        conflict_note = f" {len(conflicts)} potential conflicts detected - review recommendations."
    
    return overall_status + priority_note + funding_note + conflict_note


# Optional: Add CRUD endpoints for managing goals

@router.post("/", response_model=dict)
async def create_goal(goal: GoalInputModel):
    """Create a new goal (placeholder for future implementation)"""
    # TODO: Implement goal persistence
    raise HTTPException(status_code=501, detail="Goal persistence not yet implemented")


@router.get("/", response_model=List[GoalInputModel])
async def list_goals():
    """List all goals (placeholder for future implementation)"""
    # TODO: Implement goal retrieval
    raise HTTPException(status_code=501, detail="Goal persistence not yet implemented")


@router.get("/{goal_id}", response_model=GoalInputModel)
async def get_goal(goal_id: str):
    """Get specific goal (placeholder for future implementation)"""
    # TODO: Implement goal retrieval
    raise HTTPException(status_code=501, detail="Goal persistence not yet implemented")


@router.put("/{goal_id}", response_model=GoalInputModel)
async def update_goal(goal_id: str, goal: GoalInputModel):
    """Update existing goal (placeholder for future implementation)"""
    # TODO: Implement goal update
    raise HTTPException(status_code=501, detail="Goal persistence not yet implemented")


@router.delete("/{goal_id}")
async def delete_goal(goal_id: str):
    """Delete goal (placeholder for future implementation)"""
    # TODO: Implement goal deletion
    raise HTTPException(status_code=501, detail="Goal persistence not yet implemented")
