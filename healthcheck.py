#!/usr/bin/env python3
"""
Health check endpoint for container orchestration systems.

This script provides health, readiness, and startup checks that can be called by:
- Docker HEALTHCHECK
- Kubernetes liveness/readiness probes
- ECS health checks
- Load balancer health checks

Exit codes:
- 0: Healthy
- 1: Unhealthy
"""

import sys
import os
import time
import urllib.request
import urllib.error

# Configuration
HEALTH_CHECK_URL = os.getenv("HEALTH_CHECK_URL", "http://localhost:8501")
HEALTH_CHECK_TIMEOUT = int(os.getenv("HEALTH_CHECK_TIMEOUT", "5"))
CHECK_TYPE = os.getenv("CHECK_TYPE", "liveness")  # liveness, readiness, or startup


def check_health():
    """
    Check if the application is responding to HTTP requests.
    
    Returns:
        bool: True if healthy, False otherwise
    """
    try:
        # Attempt to connect to the application
        req = urllib.request.Request(HEALTH_CHECK_URL, method="HEAD")
        with urllib.request.urlopen(req, timeout=HEALTH_CHECK_TIMEOUT) as response:
            # Consider 200-399 as healthy
            return 200 <= response.status < 400
    except urllib.error.HTTPError as e:
        # 4xx and 5xx errors are unhealthy
        print(f"HTTP error: {e.code} {e.reason}", file=sys.stderr)
        return False
    except urllib.error.URLError as e:
        # Connection errors (timeout, refused, etc.)
        print(f"Connection error: {e.reason}", file=sys.stderr)
        return False
    except Exception as e:
        # Any other errors
        print(f"Unexpected error: {e}", file=sys.stderr)
        return False


def check_readiness():
    """
    Check if the application is ready to serve traffic.
    More comprehensive than liveness check - checks dependencies.
    
    Returns:
        bool: True if ready, False otherwise
    """
    try:
        # Try to import and use the health checker
        # This ensures all dependencies are loaded
        from observability import health_checker
        
        status = health_checker.check_readiness()
        return status.get("ready", False)
    except ImportError:
        # If observability module not available, fall back to basic health check
        return check_health()
    except Exception as e:
        print(f"Readiness check error: {e}", file=sys.stderr)
        return False


def check_startup():
    """
    Check if the application has finished starting up.
    Used during container startup to wait for initialization.
    
    Returns:
        bool: True if startup complete, False otherwise
    """
    try:
        from observability import health_checker
        
        status = health_checker.check_startup()
        return status.get("startup_complete", False)
    except ImportError:
        # If observability module not available, fall back to basic health check
        return check_health()
    except Exception as e:
        print(f"Startup check error: {e}", file=sys.stderr)
        return False


def main():
    """Run the appropriate health check based on CHECK_TYPE."""
    start_time = time.time()
    
    # Select check function based on type
    if CHECK_TYPE == "readiness":
        is_healthy = check_readiness()
        check_name = "Readiness"
    elif CHECK_TYPE == "startup":
        is_healthy = check_startup()
        check_name = "Startup"
    else:  # liveness (default)
        is_healthy = check_health()
        check_name = "Liveness"
    
    duration = time.time() - start_time
    
    if is_healthy:
        print(f"✓ {check_name} check passed ({duration:.3f}s)")
        sys.exit(0)
    else:
        print(f"✗ {check_name} check failed ({duration:.3f}s)", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
