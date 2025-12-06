"""
Tax Optimization API Endpoints

Provides Roth conversion optimization and tax-efficient withdrawal analysis.
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional
import logging

from core.tax_optimizer import (
    TaxOptimizer,
    AccountBalances,
    RothConversionSchedule,
)
from models.schemas import (
    ModelInputsModel,
    RothConversionYearModel,
    RothConversionPlanModel,
)

router = APIRouter()
logger = logging.getLogger(__name__)


class TaxOptimizationRequest(BaseModel):
    """Request for tax optimization analysis"""
    inputs: ModelInputsModel
    
    # Account balances (optional - calculated from inputs if not provided)
    current_taxable_balance: Optional[float] = None
    current_ira_balance: Optional[float] = None
    current_roth_balance: Optional[float] = None
    
    # Projected income for conversion optimization
    projected_annual_income: Optional[List[float]] = Field(
        default=None,
        description="Projected annual income by year (excludes conversions)"
    )


class TaxOptimizationResponse(BaseModel):
    """Response with tax optimization recommendations"""
    roth_conversion_plan: RothConversionPlanModel
    analysis_summary: str
    key_recommendations: List[str]
    success: bool = True
    message: str = "Tax optimization analysis completed"


@router.post("/optimize-roth-conversions", response_model=TaxOptimizationResponse)
async def optimize_roth_conversions(request: TaxOptimizationRequest):
    """
    Calculate optimal Roth conversion schedule.
    
    Analyzes client situation and generates year-by-year Roth conversion
    recommendations that:
    - Fill current tax bracket in low-income years
    - Avoid Medicare IRMAA surcharges
    - Reduce future RMD burden
    - Maximize lifetime tax savings
    
    **Returns:**
    - Detailed conversion schedule by year
    - Projected tax savings
    - Implementation recommendations
    """
    try:
        inputs = request.inputs
        
        # Calculate account balances if not provided
        if request.current_ira_balance is not None:
            ira_balance = request.current_ira_balance
        else:
            ira_balance = inputs.starting_portfolio * inputs.ira_pct
        
        if request.current_roth_balance is not None:
            roth_balance = request.current_roth_balance
        else:
            roth_balance = inputs.starting_portfolio * inputs.roth_pct
        
        if request.current_taxable_balance is not None:
            taxable_balance = request.current_taxable_balance
        else:
            taxable_balance = inputs.starting_portfolio * inputs.taxable_pct
        
        # Initialize tax optimizer
        optimizer = TaxOptimizer(
            filing_status=getattr(inputs, 'filing_status', 'single'),
            state_tax_rate=getattr(inputs, 'state_tax_rate', 0.0),
            current_age=inputs.current_age,
        )
        
        # Calculate years until RMD
        years_until_rmd = max(0, inputs.rmd_age - inputs.current_age)
        
        # Generate projected income
        if request.projected_annual_income:
            projected_income = request.projected_annual_income
        else:
            # Estimate based on SS and pension
            annual_ss = inputs.social_security_monthly * 12
            annual_pension = inputs.pension_monthly * 12
            
            projected_income = []
            for year_idx in range(years_until_rmd):
                age = inputs.current_age + year_idx
                year_income = 0.0
                
                # Add SS if age reached
                if age >= inputs.ss_start_age:
                    year_income += annual_ss
                
                # Add pension if age reached
                if age >= inputs.pension_start_age:
                    year_income += annual_pension
                
                projected_income.append(year_income)
        
        # Run Roth conversion optimization
        if inputs.optimize_roth_conversions and ira_balance > 0 and years_until_rmd > 0:
            schedule = optimizer.optimize_roth_conversions(
                ira_balance=ira_balance,
                years_until_rmd=years_until_rmd,
                projected_income_by_year=projected_income[:years_until_rmd],
                current_age=inputs.current_age,
                max_annual_conversion_pct=0.15,  # Max 15% per year
                avoid_irmaa=getattr(inputs, 'avoid_irmaa', True),
            )
            
            # Convert to response model
            conversion_years = [
                RothConversionYearModel(
                    year=schedule.years[i],
                    age=schedule.ages[i],
                    conversion_amount=schedule.conversion_amounts[i],
                    tax_on_conversion=schedule.projected_taxes[i],
                    cumulative_savings=schedule.cumulative_savings[i]
                )
                for i in range(len(schedule.years))
            ]
            
            # Generate recommendation text
            if schedule.total_conversions > 0:
                recommendation = (
                    f"Recommended Roth conversion strategy: Convert ${schedule.total_conversions:,.0f} "
                    f"over {len(schedule.years)} years. "
                    f"Pay ${schedule.total_taxes_on_conversions:,.0f} in taxes now to save "
                    f"${schedule.lifetime_tax_savings:,.0f} (present value) over your lifetime."
                )
            else:
                recommendation = (
                    "No Roth conversions recommended at this time. "
                    "Current income levels and tax situation don't favor conversions."
                )
            
            plan = RothConversionPlanModel(
                enabled=True,
                years=conversion_years,
                total_conversions=schedule.total_conversions,
                total_taxes_paid=schedule.total_taxes_on_conversions,
                lifetime_tax_savings=schedule.lifetime_tax_savings,
                recommendation=recommendation
            )
            
            # Generate key recommendations
            recommendations = []
            
            if schedule.total_conversions > 0:
                recommendations.append(
                    f"Execute Roth conversions annually between ages "
                    f"{schedule.ages[0]}-{schedule.ages[-1]}"
                )
                
                avg_conversion = schedule.total_conversions / len(schedule.years)
                recommendations.append(
                    f"Average annual conversion: ${avg_conversion:,.0f}"
                )
                
                if schedule.lifetime_tax_savings > 100000:
                    recommendations.append(
                        f"High-value opportunity: Over ${schedule.lifetime_tax_savings:,.0f} "
                        f"in lifetime tax savings"
                    )
                
                recommendations.append(
                    "Review annually and adjust based on actual income and tax law changes"
                )
                
                recommendations.append(
                    "Consider working with CPA to implement conversion strategy"
                )
            else:
                recommendations.append("Current income too high for beneficial conversions")
                recommendations.append("Revisit when income decreases (e.g., early retirement)")
                if ira_balance > 500000:
                    recommendations.append("Consider conversions if you have high-income gap years")
            
            # Generate analysis summary
            if schedule.total_conversions > 0:
                roi = (schedule.lifetime_tax_savings / schedule.total_taxes_on_conversions 
                       if schedule.total_taxes_on_conversions > 0 else 0)
                summary = (
                    f"Optimal Roth conversion analysis for {inputs.client_name if hasattr(inputs, 'client_name') else 'client'}:\\n\\n"
                    f"Current IRA Balance: ${ira_balance:,.0f}\\n"
                    f"Years until RMD: {years_until_rmd}\\n\\n"
                    f"RECOMMENDED STRATEGY:\\n"
                    f"• Convert ${schedule.total_conversions:,.0f} over {len(schedule.years)} years\\n"
                    f"• Pay ${schedule.total_taxes_on_conversions:,.0f} in taxes on conversions\\n"
                    f"• Save ${schedule.lifetime_tax_savings:,.0f} (PV) in lifetime taxes\\n"
                    f"• ROI: {roi:.1f}x (${roi:.2f} saved per $1 tax paid)\\n\\n"
                    f"This strategy reduces future RMDs and creates tax-free growth in Roth accounts."
                )
            else:
                summary = (
                    f"Roth conversion analysis for {inputs.client_name if hasattr(inputs, 'client_name') else 'client'}:\\n\\n"
                    f"Current IRA Balance: ${ira_balance:,.0f}\\n"
                    f"Years until RMD: {years_until_rmd}\\n\\n"
                    f"CONCLUSION:\\n"
                    f"No conversions recommended at this time. Current income levels and tax brackets "
                    f"do not favor Roth conversions. Consider revisiting when income decreases."
                )
            
        else:
            # No optimization requested or not applicable
            plan = RothConversionPlanModel(
                enabled=False,
                recommendation="Roth conversion optimization not enabled or not applicable"
            )
            summary = "Roth conversion optimization was not requested or client situation not suitable"
            recommendations = ["Enable 'Optimize Roth Conversions' to see recommendations"]
        
        return TaxOptimizationResponse(
            roth_conversion_plan=plan,
            analysis_summary=summary,
            key_recommendations=recommendations
        )
        
    except Exception as e:
        logger.error(f"Tax optimization failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Tax optimization analysis failed: {str(e)}"
        )


@router.get("/health")
async def tax_optimization_health():
    """Health check for tax optimization service"""
    return {
        "status": "healthy",
        "service": "tax_optimization",
        "features": [
            "roth_conversion_optimization",
            "withdrawal_sequencing",
            "irmaa_avoidance",
            "tax_bracket_analysis"
        ]
    }
