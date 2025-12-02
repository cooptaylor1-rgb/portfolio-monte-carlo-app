"""
Security, input validation, and rate limiting for Portfolio Analysis Platform.
"""

import time
import hashlib
import re
from typing import Any, Optional, Dict, Callable
from functools import wraps
from dataclasses import dataclass
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


@dataclass
class ValidationRule:
    """Validation rule with min/max and custom validator."""
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    allowed_values: Optional[list] = None
    custom_validator: Optional[Callable] = None
    error_message: str = "Invalid value"


class InputValidator:
    """Validates and sanitizes user inputs."""
    
    # Validation rules for portfolio inputs
    VALIDATION_RULES = {
        'starting_portfolio': ValidationRule(
            min_value=1_000,
            max_value=100_000_000,
            error_message="Portfolio value must be between $1,000 and $100,000,000"
        ),
        'monthly_spending': ValidationRule(
            min_value=0,
            max_value=1_000_000,
            error_message="Monthly spending must be between $0 and $1,000,000"
        ),
        'years_to_model': ValidationRule(
            min_value=1,
            max_value=100,
            error_message="Years must be between 1 and 100"
        ),
        'n_scenarios': ValidationRule(
            min_value=10,
            max_value=10_000,
            error_message="Scenarios must be between 10 and 10,000"
        ),
        'equity_pct': ValidationRule(
            min_value=0.0,
            max_value=1.0,
            error_message="Equity percentage must be between 0% and 100%"
        ),
        'current_age': ValidationRule(
            min_value=18,
            max_value=120,
            error_message="Age must be between 18 and 120"
        ),
        'inflation_annual': ValidationRule(
            min_value=-0.05,
            max_value=0.20,
            error_message="Inflation must be between -5% and 20%"
        ),
        'expected_return_equity': ValidationRule(
            min_value=-0.50,
            max_value=0.50,
            error_message="Equity return must be between -50% and 50%"
        ),
        'volatility_equity': ValidationRule(
            min_value=0.0,
            max_value=1.0,
            error_message="Volatility must be between 0% and 100%"
        ),
    }
    
    @classmethod
    def validate(cls, field: str, value: Any) -> tuple[bool, Optional[str]]:
        """
        Validate a field value.
        Returns (is_valid, error_message).
        """
        if field not in cls.VALIDATION_RULES:
            # No validation rule defined, allow value
            return True, None
        
        rule = cls.VALIDATION_RULES[field]
        
        # Check min/max
        if rule.min_value is not None and value < rule.min_value:
            return False, f"{rule.error_message} (got {value})"
        
        if rule.max_value is not None and value > rule.max_value:
            return False, f"{rule.error_message} (got {value})"
        
        # Check allowed values
        if rule.allowed_values is not None and value not in rule.allowed_values:
            return False, f"{rule.error_message} (got {value})"
        
        # Custom validator
        if rule.custom_validator is not None:
            try:
                is_valid = rule.custom_validator(value)
                if not is_valid:
                    return False, rule.error_message
            except Exception as e:
                return False, f"{rule.error_message}: {str(e)}"
        
        return True, None
    
    @classmethod
    def validate_all(cls, inputs: Dict[str, Any]) -> tuple[bool, Dict[str, str]]:
        """
        Validate all inputs.
        Returns (all_valid, errors_dict).
        """
        errors = {}
        
        for field, value in inputs.items():
            is_valid, error_msg = cls.validate(field, value)
            if not is_valid:
                errors[field] = error_msg
        
        return len(errors) == 0, errors
    
    @classmethod
    def sanitize_string(cls, value: str, max_length: int = 1000) -> str:
        """Sanitize string input (prevent XSS, injection)."""
        if not isinstance(value, str):
            return str(value)
        
        # Trim to max length
        value = value[:max_length]
        
        # Remove potentially dangerous characters
        # Allow alphanumeric, spaces, basic punctuation
        value = re.sub(r'[<>{}[\]\\|`]', '', value)
        
        # Remove multiple spaces
        value = re.sub(r'\s+', ' ', value)
        
        return value.strip()
    
    @classmethod
    def sanitize_filename(cls, filename: str) -> str:
        """Sanitize filename for safe file operations."""
        # Remove path separators
        filename = filename.replace('/', '').replace('\\', '')
        
        # Allow only alphanumeric, dash, underscore, dot
        filename = re.sub(r'[^a-zA-Z0-9._-]', '_', filename)
        
        # Limit length
        if len(filename) > 255:
            name, ext = filename.rsplit('.', 1) if '.' in filename else (filename, '')
            filename = name[:240] + '.' + ext if ext else name[:255]
        
        return filename


class RateLimiter:
    """Token bucket rate limiter."""
    
    def __init__(self, requests_per_minute: int = 60, burst_size: Optional[int] = None):
        self.requests_per_minute = requests_per_minute
        self.burst_size = burst_size or requests_per_minute
        self.buckets: Dict[str, Dict] = {}
        self.cleanup_interval = 300  # Clean up old buckets every 5 minutes
        self.last_cleanup = time.time()
    
    def _get_client_id(self, request) -> str:
        """Extract client identifier from request."""
        # For Streamlit, we can use session ID or IP
        # In production, use user ID or IP address
        try:
            import streamlit as st
            if hasattr(st, 'session_state') and hasattr(st.session_state, 'session_id'):
                return st.session_state.session_id
        except:
            pass
        
        # Fallback to a generic client (not ideal for production)
        return "default_client"
    
    def _cleanup_old_buckets(self):
        """Remove old buckets to prevent memory leak."""
        if time.time() - self.last_cleanup < self.cleanup_interval:
            return
        
        current_time = time.time()
        cutoff_time = current_time - 3600  # Remove buckets older than 1 hour
        
        self.buckets = {
            client_id: bucket
            for client_id, bucket in self.buckets.items()
            if bucket['last_access'] > cutoff_time
        }
        
        self.last_cleanup = current_time
    
    def is_allowed(self, client_id: Optional[str] = None) -> tuple[bool, Dict[str, Any]]:
        """
        Check if request is allowed under rate limit.
        Returns (is_allowed, rate_limit_info).
        """
        self._cleanup_old_buckets()
        
        if client_id is None:
            client_id = self._get_client_id(None)
        
        current_time = time.time()
        
        # Initialize bucket if not exists
        if client_id not in self.buckets:
            self.buckets[client_id] = {
                'tokens': self.burst_size,
                'last_refill': current_time,
                'last_access': current_time
            }
        
        bucket = self.buckets[client_id]
        
        # Refill tokens based on time elapsed
        time_elapsed = current_time - bucket['last_refill']
        tokens_to_add = time_elapsed * (self.requests_per_minute / 60.0)
        bucket['tokens'] = min(self.burst_size, bucket['tokens'] + tokens_to_add)
        bucket['last_refill'] = current_time
        bucket['last_access'] = current_time
        
        # Check if token available
        if bucket['tokens'] >= 1.0:
            bucket['tokens'] -= 1.0
            is_allowed = True
            retry_after = 0
        else:
            is_allowed = False
            # Calculate time until next token available
            retry_after = (1.0 - bucket['tokens']) * (60.0 / self.requests_per_minute)
        
        rate_limit_info = {
            'limit': self.requests_per_minute,
            'remaining': int(bucket['tokens']),
            'retry_after_seconds': retry_after
        }
        
        return is_allowed, rate_limit_info
    
    def reset(self, client_id: Optional[str] = None):
        """Reset rate limit for client."""
        if client_id is None:
            client_id = self._get_client_id(None)
        
        if client_id in self.buckets:
            del self.buckets[client_id]


def rate_limit(requests_per_minute: int = 60):
    """Decorator to apply rate limiting to functions."""
    limiter = RateLimiter(requests_per_minute=requests_per_minute)
    
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            is_allowed, rate_info = limiter.is_allowed()
            
            if not is_allowed:
                logger.warning(f"Rate limit exceeded for {func.__name__}", extra=rate_info)
                raise RateLimitExceeded(
                    f"Rate limit exceeded. Try again in {rate_info['retry_after_seconds']:.1f} seconds.",
                    rate_info
                )
            
            return func(*args, **kwargs)
        
        return wrapper
    return decorator


class RateLimitExceeded(Exception):
    """Exception raised when rate limit is exceeded."""
    
    def __init__(self, message: str, rate_limit_info: Dict[str, Any]):
        super().__init__(message)
        self.rate_limit_info = rate_limit_info


class SecurityHeaders:
    """Security headers for HTTP responses."""
    
    @staticmethod
    def get_security_headers() -> Dict[str, str]:
        """Get recommended security headers."""
        return {
            # Prevent clickjacking
            'X-Frame-Options': 'DENY',
            
            # Prevent MIME type sniffing
            'X-Content-Type-Options': 'nosniff',
            
            # Enable XSS protection
            'X-XSS-Protection': '1; mode=block',
            
            # Strict Transport Security (HTTPS only)
            'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
            
            # Content Security Policy
            'Content-Security-Policy': (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
                "style-src 'self' 'unsafe-inline'; "
                "img-src 'self' data: https:; "
                "font-src 'self' data:; "
                "connect-src 'self'"
            ),
            
            # Referrer policy
            'Referrer-Policy': 'strict-origin-when-cross-origin',
            
            # Permissions policy
            'Permissions-Policy': 'geolocation=(), microphone=(), camera=()'
        }


def hash_sensitive_data(data: str) -> str:
    """Hash sensitive data for logging/storage."""
    return hashlib.sha256(data.encode()).hexdigest()[:16]


def validate_session():
    """Validate user session."""
    try:
        import streamlit as st
        
        # Check if session exists
        if not hasattr(st, 'session_state'):
            return False
        
        # Check session timeout (example: 1 hour)
        if 'session_start' not in st.session_state:
            st.session_state.session_start = datetime.now()
            return True
        
        session_age = datetime.now() - st.session_state.session_start
        if session_age > timedelta(hours=1):
            logger.warning("Session expired")
            return False
        
        return True
    
    except Exception as e:
        logger.error(f"Session validation failed: {e}")
        return False


# Initialize global rate limiter
default_rate_limiter = RateLimiter(requests_per_minute=60)


def check_rate_limit() -> tuple[bool, Dict[str, Any]]:
    """Check global rate limit."""
    return default_rate_limiter.is_allowed()


if __name__ == '__main__':
    # Test input validation
    validator = InputValidator()
    
    test_cases = [
        ('starting_portfolio', 1_000_000, True),
        ('starting_portfolio', 500, False),
        ('n_scenarios', 1000, True),
        ('n_scenarios', 20000, False),
        ('equity_pct', 0.6, True),
        ('equity_pct', 1.5, False),
    ]
    
    print("Testing input validation:")
    for field, value, expected_valid in test_cases:
        is_valid, error = validator.validate(field, value)
        status = "✓" if is_valid == expected_valid else "✗"
        print(f"{status} {field}={value}: valid={is_valid}, error={error}")
    
    # Test rate limiting
    print("\nTesting rate limiting:")
    limiter = RateLimiter(requests_per_minute=60)
    
    for i in range(65):
        is_allowed, info = limiter.is_allowed("test_client")
        if not is_allowed:
            print(f"Request {i+1}: Rate limited! Retry after {info['retry_after_seconds']:.2f}s")
            break
        elif i % 10 == 0:
            print(f"Request {i+1}: Allowed (remaining: {info['remaining']})")
