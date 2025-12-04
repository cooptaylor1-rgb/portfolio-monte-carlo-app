"""
Assumption preset endpoints.
Provides industry-standard return and volatility assumptions.
"""
from fastapi import APIRouter, HTTPException
from backend.models.schemas import AssumptionPresetModel
from typing import List

router = APIRouter()


# Predefined assumption presets
PRESETS = {
    "CFP Board (Conservative)": {
        "name": "CFP Board (Conservative)",
        "equity_return": 0.08,
        "fi_return": 0.04,
        "cash_return": 0.02,
        "equity_vol": 0.18,
        "fi_vol": 0.06,
        "cash_vol": 0.01
    },
    "Morningstar (Moderate)": {
        "name": "Morningstar (Moderate)",
        "equity_return": 0.095,
        "fi_return": 0.045,
        "cash_return": 0.025,
        "equity_vol": 0.17,
        "fi_vol": 0.055,
        "cash_vol": 0.01
    },
    "Vanguard (Historical)": {
        "name": "Vanguard (Historical)",
        "equity_return": 0.095,
        "fi_return": 0.042,
        "cash_return": 0.025,
        "equity_vol": 0.16,
        "fi_vol": 0.05,
        "cash_vol": 0.01
    },
    "Conservative": {
        "name": "Conservative",
        "equity_return": 0.07,
        "fi_return": 0.035,
        "cash_return": 0.02,
        "equity_vol": 0.20,
        "fi_vol": 0.07,
        "cash_vol": 0.01
    },
    "Aggressive": {
        "name": "Aggressive",
        "equity_return": 0.11,
        "fi_return": 0.045,
        "cash_return": 0.025,
        "equity_vol": 0.14,
        "fi_vol": 0.045,
        "cash_vol": 0.01
    }
}


@router.get("/", response_model=List[AssumptionPresetModel])
async def list_presets():
    """
    Get list of all available assumption presets.
    
    Returns industry-standard assumptions from various sources:
    - CFP Board: Conservative financial planning assumptions
    - Morningstar: Moderate assumptions based on market research
    - Vanguard: Historical market return data
    - Conservative: Risk-averse assumptions
    - Aggressive: Growth-oriented assumptions
    """
    return list(PRESETS.values())


@router.get("/{preset_name}", response_model=AssumptionPresetModel)
async def get_preset(preset_name: str):
    """
    Get specific assumption preset by name.
    
    **Parameters:**
    - preset_name: Name of the preset (e.g., "Vanguard (Historical)")
    
    **Returns:**
    - Preset with return and volatility assumptions
    """
    if preset_name not in PRESETS:
        raise HTTPException(
            status_code=404,
            detail=f"Preset '{preset_name}' not found. Available presets: {list(PRESETS.keys())}"
        )
    
    return PRESETS[preset_name]
