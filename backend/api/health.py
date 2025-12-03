"""
Health check and system status endpoints.
"""
from fastapi import APIRouter
from models.schemas import HealthCheckResponse
from datetime import datetime
import platform
import sys

router = APIRouter()

APP_VERSION = "2.0.0"


@router.get("/health", response_model=HealthCheckResponse)
async def health_check():
    """
    Health check endpoint for monitoring and load balancers.
    Returns operational status and system information.
    """
    return {
        "status": "healthy",
        "version": APP_VERSION,
        "timestamp": datetime.utcnow().isoformat()
    }


@router.get("/status")
async def system_status():
    """
    Detailed system status information.
    """
    return {
        "status": "operational",
        "version": APP_VERSION,
        "timestamp": datetime.utcnow().isoformat(),
        "system": {
            "platform": platform.platform(),
            "python_version": sys.version,
            "architecture": platform.machine()
        }
    }
