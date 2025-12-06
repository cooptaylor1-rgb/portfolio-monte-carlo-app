"""
FastAPI Backend - Main application entry point.
Serves REST API for Monte Carlo portfolio analysis.
"""
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import time
from datetime import datetime
import logging

from api import simulation, presets, health, social_security, tax_optimization, goals, enhanced_simulation
from models.schemas import HealthCheckResponse

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Application metadata
APP_VERSION = "2.0.0"
APP_NAME = "Salem Investment Counselors - Portfolio Analysis API"


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler"""
    logger.info(f"Starting {APP_NAME} v{APP_VERSION}")
    yield
    logger.info(f"Shutting down {APP_NAME}")


# Initialize FastAPI application
app = FastAPI(
    title=APP_NAME,
    description="REST API for institutional-grade Monte Carlo portfolio analysis and scenario planning",
    version=APP_VERSION,
    lifespan=lifespan,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)

# Configure CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # React dev server
        "http://localhost:5173",  # Vite dev server
        "http://localhost:4173",  # Vite preview
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all incoming requests"""
    start_time = time.time()
    
    # Process request
    response = await call_next(request)
    
    # Calculate duration
    duration = time.time() - start_time
    
    # Log request details
    logger.info(
        f"{request.method} {request.url.path} - "
        f"Status: {response.status_code} - "
        f"Duration: {duration:.3f}s"
    )
    
    return response


# Error handling
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions with consistent format"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "message": exc.detail,
            "timestamp": datetime.utcnow().isoformat()
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "message": "Internal server error",
            "timestamp": datetime.utcnow().isoformat()
        }
    )


# Root endpoint
@app.get("/", response_model=HealthCheckResponse)
async def root():
    """API root endpoint"""
    return {
        "status": "operational",
        "version": APP_VERSION,
        "timestamp": datetime.utcnow().isoformat()
    }


# Include routers
app.include_router(health.router, prefix="/api", tags=["health"])
app.include_router(simulation.router, prefix="/api/simulation", tags=["simulation"])
app.include_router(enhanced_simulation.router, prefix="/api/simulation", tags=["enhanced-simulation"])
app.include_router(presets.router, prefix="/api/presets", tags=["presets"])
app.include_router(social_security.router)
app.include_router(tax_optimization.router, prefix="/api/tax", tags=["tax-optimization"])
app.include_router(goals.router, prefix="/api", tags=["goal-planning"])


# Application entry point
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
