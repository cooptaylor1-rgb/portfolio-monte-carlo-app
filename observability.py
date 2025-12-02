"""
Health checks, metrics, and observability for Portfolio Analysis Platform.
Provides endpoints for container orchestration and monitoring.
"""

import time
import logging
import json
import uuid
from datetime import datetime
from typing import Dict, Any, Optional
from functools import wraps
from contextlib import contextmanager
import psutil

# Configure structured logging
from pythonjsonlogger import jsonlogger

logger = logging.getLogger(__name__)


class StructuredLogger:
    """Structured logging with correlation IDs and context."""
    
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
        self._setup_logger()
    
    def _setup_logger(self):
        """Configure JSON logger for structured logging."""
        handler = logging.StreamHandler()
        formatter = jsonlogger.JsonFormatter(
            fmt='%(timestamp)s %(level)s %(name)s %(correlation_id)s %(message)s'
        )
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)
    
    def _add_context(self, extra: dict) -> dict:
        """Add standard context to log entries."""
        if extra is None:
            extra = {}
        
        extra.setdefault('timestamp', datetime.utcnow().isoformat())
        extra.setdefault('correlation_id', get_correlation_id())
        extra.setdefault('environment', 'production')
        
        return extra
    
    def debug(self, message: str, **kwargs):
        """Log debug message with context."""
        self.logger.debug(message, extra=self._add_context(kwargs))
    
    def info(self, message: str, **kwargs):
        """Log info message with context."""
        self.logger.info(message, extra=self._add_context(kwargs))
    
    def warning(self, message: str, **kwargs):
        """Log warning message with context."""
        self.logger.warning(message, extra=self._add_context(kwargs))
    
    def error(self, message: str, **kwargs):
        """Log error message with context."""
        self.logger.error(message, extra=self._add_context(kwargs))
    
    def critical(self, message: str, **kwargs):
        """Log critical message with context."""
        self.logger.critical(message, extra=self._add_context(kwargs))


# Correlation ID management
_correlation_id = None


def set_correlation_id(correlation_id: str):
    """Set correlation ID for current request."""
    global _correlation_id
    _correlation_id = correlation_id


def get_correlation_id() -> str:
    """Get or generate correlation ID."""
    global _correlation_id
    if _correlation_id is None:
        _correlation_id = str(uuid.uuid4())
    return _correlation_id


def new_correlation_id() -> str:
    """Generate and set new correlation ID."""
    correlation_id = str(uuid.uuid4())
    set_correlation_id(correlation_id)
    return correlation_id


@contextmanager
def correlation_context(correlation_id: Optional[str] = None):
    """Context manager for correlation ID scope."""
    old_id = get_correlation_id()
    new_id = correlation_id or str(uuid.uuid4())
    set_correlation_id(new_id)
    try:
        yield new_id
    finally:
        set_correlation_id(old_id)


class HealthChecker:
    """Health check system for container orchestration."""
    
    def __init__(self):
        self.start_time = time.time()
        self.ready = False
        self.dependencies = {}
        self.logger = StructuredLogger(__name__)
    
    def mark_ready(self):
        """Mark application as ready to serve traffic."""
        self.ready = True
        self.logger.info("Application marked as ready")
    
    def add_dependency(self, name: str, check_func):
        """Add a dependency health check."""
        self.dependencies[name] = check_func
    
    def check_liveness(self) -> Dict[str, Any]:
        """
        Liveness check - Is the application alive?
        Used by Kubernetes liveness probe.
        """
        return {
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'uptime_seconds': int(time.time() - self.start_time)
        }
    
    def check_readiness(self) -> Dict[str, Any]:
        """
        Readiness check - Is the application ready for traffic?
        Used by Kubernetes readiness probe.
        """
        if not self.ready:
            return {
                'status': 'not_ready',
                'reason': 'Application still initializing',
                'timestamp': datetime.utcnow().isoformat()
            }
        
        # Check all dependencies
        dependency_status = {}
        all_healthy = True
        
        for name, check_func in self.dependencies.items():
            try:
                is_healthy = check_func()
                dependency_status[name] = 'healthy' if is_healthy else 'unhealthy'
                if not is_healthy:
                    all_healthy = False
            except Exception as e:
                dependency_status[name] = f'error: {str(e)}'
                all_healthy = False
                self.logger.error(f"Dependency check failed: {name}", error=str(e))
        
        return {
            'status': 'ready' if all_healthy else 'not_ready',
            'dependencies': dependency_status,
            'timestamp': datetime.utcnow().isoformat()
        }
    
    def check_startup(self) -> Dict[str, Any]:
        """
        Startup check - Has the application finished starting?
        Used by Kubernetes startup probe.
        """
        return {
            'status': 'started' if self.ready else 'starting',
            'uptime_seconds': int(time.time() - self.start_time),
            'timestamp': datetime.utcnow().isoformat()
        }


# Global health checker
health_checker = HealthChecker()


class MetricsCollector:
    """Prometheus-compatible metrics collector."""
    
    def __init__(self):
        self.metrics = {
            'request_count': 0,
            'request_duration_sum': 0.0,
            'request_duration_count': 0,
            'error_count': 0,
            'simulation_count': 0,
            'simulation_scenarios_total': 0,
            'simulation_duration_sum': 0.0,
            'cache_hits': 0,
            'cache_misses': 0,
        }
        self.histogram_buckets = [0.01, 0.05, 0.1, 0.5, 1.0, 2.0, 5.0, 10.0]
        self.request_durations = []
        self.logger = StructuredLogger(__name__)
    
    def increment(self, metric: str, value: float = 1.0):
        """Increment a counter metric."""
        if metric in self.metrics:
            self.metrics[metric] += value
        else:
            self.metrics[metric] = value
    
    def record_duration(self, metric: str, duration: float):
        """Record a duration metric."""
        self.metrics[f'{metric}_sum'] = self.metrics.get(f'{metric}_sum', 0) + duration
        self.metrics[f'{metric}_count'] = self.metrics.get(f'{metric}_count', 0) + 1
        
        # Store for histogram
        if metric == 'request_duration':
            self.request_durations.append(duration)
            # Keep only last 1000 for memory
            if len(self.request_durations) > 1000:
                self.request_durations = self.request_durations[-1000:]
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get all metrics in Prometheus format."""
        metrics_output = []
        
        # Counters
        for name, value in self.metrics.items():
            if not name.endswith('_sum') and not name.endswith('_count'):
                metrics_output.append(f'{name} {value}')
        
        # Gauges (current values)
        process = psutil.Process()
        metrics_output.append(f'process_cpu_percent {process.cpu_percent()}')
        metrics_output.append(f'process_memory_mb {process.memory_info().rss / 1024 / 1024:.2f}')
        metrics_output.append(f'process_threads {process.num_threads()}')
        
        # Summaries (avg duration)
        if self.metrics.get('request_duration_count', 0) > 0:
            avg_duration = self.metrics['request_duration_sum'] / self.metrics['request_duration_count']
            metrics_output.append(f'request_duration_avg {avg_duration:.6f}')
        
        # Cache hit rate
        total_cache = self.metrics['cache_hits'] + self.metrics['cache_misses']
        if total_cache > 0:
            hit_rate = self.metrics['cache_hits'] / total_cache
            metrics_output.append(f'cache_hit_rate {hit_rate:.4f}')
        
        return '\n'.join(metrics_output)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get metrics as JSON for /metrics endpoint."""
        process = psutil.Process()
        
        stats = {
            'counters': {k: v for k, v in self.metrics.items() 
                        if not k.endswith('_sum') and not k.endswith('_count')},
            'system': {
                'cpu_percent': process.cpu_percent(),
                'memory_mb': process.memory_info().rss / 1024 / 1024,
                'memory_percent': process.memory_percent(),
                'threads': process.num_threads(),
            },
            'performance': {},
            'cache': {
                'hits': self.metrics['cache_hits'],
                'misses': self.metrics['cache_misses'],
                'hit_rate': self.metrics['cache_hits'] / max(1, self.metrics['cache_hits'] + self.metrics['cache_misses'])
            }
        }
        
        # Calculate averages
        if self.metrics.get('request_duration_count', 0) > 0:
            stats['performance']['avg_request_duration_ms'] = \
                (self.metrics['request_duration_sum'] / self.metrics['request_duration_count']) * 1000
        
        if self.metrics.get('simulation_count', 0) > 0:
            stats['performance']['avg_simulation_duration_ms'] = \
                (self.metrics['simulation_duration_sum'] / self.metrics['simulation_count']) * 1000
            stats['performance']['avg_scenarios_per_simulation'] = \
                self.metrics['simulation_scenarios_total'] / self.metrics['simulation_count']
        
        return stats


# Global metrics collector
metrics = MetricsCollector()


def track_request(func):
    """Decorator to track request metrics."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        correlation_id = new_correlation_id()
        
        logger = StructuredLogger(func.__name__)
        logger.info(f"Request started: {func.__name__}", 
                   correlation_id=correlation_id)
        
        try:
            result = func(*args, **kwargs)
            metrics.increment('request_count')
            duration = time.time() - start_time
            metrics.record_duration('request_duration', duration)
            
            logger.info(f"Request completed: {func.__name__}", 
                       duration_ms=duration * 1000,
                       correlation_id=correlation_id)
            
            return result
        
        except Exception as e:
            metrics.increment('error_count')
            duration = time.time() - start_time
            
            logger.error(f"Request failed: {func.__name__}", 
                        error=str(e),
                        duration_ms=duration * 1000,
                        correlation_id=correlation_id)
            raise
    
    return wrapper


def track_simulation(scenarios: int):
    """Decorator to track simulation metrics."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            
            logger = StructuredLogger(func.__name__)
            logger.info(f"Simulation started: {scenarios} scenarios")
            
            try:
                result = func(*args, **kwargs)
                
                duration = time.time() - start_time
                metrics.increment('simulation_count')
                metrics.increment('simulation_scenarios_total', scenarios)
                metrics.record_duration('simulation_duration', duration)
                
                logger.info(f"Simulation completed", 
                           scenarios=scenarios,
                           duration_ms=duration * 1000,
                           throughput=scenarios / duration if duration > 0 else 0)
                
                return result
            
            except Exception as e:
                logger.error(f"Simulation failed", 
                            scenarios=scenarios,
                            error=str(e))
                raise
        
        return wrapper
    return decorator


def init_error_tracking(sentry_dsn: Optional[str] = None):
    """Initialize Sentry error tracking."""
    if not sentry_dsn:
        logger.info("Sentry DSN not provided, error tracking disabled")
        return
    
    try:
        import sentry_sdk
        from sentry_sdk.integrations.logging import LoggingIntegration
        
        sentry_sdk.init(
            dsn=sentry_dsn,
            traces_sample_rate=0.1,  # 10% of transactions
            profiles_sample_rate=0.1,  # 10% of transactions
            integrations=[
                LoggingIntegration(
                    level=logging.INFO,
                    event_level=logging.ERROR
                )
            ],
            environment='production',
            release='portfolio-analyzer@1.0.0',
        )
        
        logger.info("Sentry error tracking initialized")
    
    except ImportError:
        logger.warning("sentry-sdk not installed, error tracking disabled")
    except Exception as e:
        logger.error(f"Failed to initialize Sentry: {e}")


def capture_exception(exception: Exception, context: Optional[Dict] = None):
    """Capture exception with Sentry."""
    try:
        import sentry_sdk
        with sentry_sdk.push_scope() as scope:
            if context:
                for key, value in context.items():
                    scope.set_context(key, value)
            scope.set_tag('correlation_id', get_correlation_id())
            sentry_sdk.capture_exception(exception)
    except ImportError:
        logger.error("Sentry not available", error=str(exception))


# Initialize on module load
structured_logger = StructuredLogger(__name__)
