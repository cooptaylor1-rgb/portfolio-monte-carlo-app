"""
Configuration management for Portfolio Analysis Platform.
Supports multiple environments (dev, staging, production) with secure secret handling.
"""

import os
import logging
from dataclasses import dataclass
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()

logger = logging.getLogger(__name__)


@dataclass
class AppConfig:
    """Application configuration with environment-specific defaults."""
    
    # Environment
    env: str = os.getenv('APP_ENV', 'development')
    debug: bool = os.getenv('DEBUG', 'false').lower() == 'true'
    log_level: str = os.getenv('LOG_LEVEL', 'INFO')
    log_format: str = os.getenv('LOG_FORMAT', 'json')
    
    # Performance
    cache_ttl: int = int(os.getenv('CACHE_TTL', '3600'))
    cache_max_size_mb: int = int(os.getenv('CACHE_MAX_SIZE_MB', '500'))
    max_scenarios: int = int(os.getenv('MAX_SCENARIOS', '10000'))
    max_concurrent_simulations: int = int(os.getenv('MAX_CONCURRENT_SIMULATIONS', '5'))
    
    # Redis
    redis_enabled: bool = os.getenv('REDIS_ENABLED', 'false').lower() == 'true'
    redis_host: str = os.getenv('REDIS_HOST', 'localhost')
    redis_port: int = int(os.getenv('REDIS_PORT', '6379'))
    redis_password: Optional[str] = os.getenv('REDIS_PASSWORD')
    redis_db: int = int(os.getenv('REDIS_DB', '0'))
    redis_ssl: bool = os.getenv('REDIS_SSL', 'false').lower() == 'true'
    
    # PostgreSQL
    db_enabled: bool = os.getenv('DB_ENABLED', 'false').lower() == 'true'
    db_host: str = os.getenv('DB_HOST', 'localhost')
    db_port: int = int(os.getenv('DB_PORT', '5432'))
    db_name: str = os.getenv('DB_NAME', 'portfolio_db')
    db_user: str = os.getenv('DB_USER', 'portfolio_user')
    db_password: Optional[str] = os.getenv('DB_PASSWORD')
    db_pool_size: int = int(os.getenv('DB_POOL_SIZE', '10'))
    db_pool_max_overflow: int = int(os.getenv('DB_POOL_MAX_OVERFLOW', '20'))
    
    # Security
    rate_limit_enabled: bool = os.getenv('RATE_LIMIT_ENABLED', 'true').lower() == 'true'
    rate_limit_per_minute: int = int(os.getenv('RATE_LIMIT_PER_MINUTE', '60'))
    allowed_origins: str = os.getenv('ALLOWED_ORIGINS', '*')
    secret_key: str = os.getenv('SECRET_KEY', 'development-secret-key-change-in-production')
    session_timeout: int = int(os.getenv('SESSION_TIMEOUT', '3600'))
    
    # Observability
    enable_metrics: bool = os.getenv('ENABLE_METRICS', 'true').lower() == 'true'
    metrics_port: int = int(os.getenv('METRICS_PORT', '9090'))
    enable_tracing: bool = os.getenv('ENABLE_TRACING', 'false').lower() == 'true'
    sentry_dsn: Optional[str] = os.getenv('SENTRY_DSN')
    sentry_environment: str = os.getenv('SENTRY_ENVIRONMENT', env)
    
    # External Services
    openai_api_key: Optional[str] = os.getenv('OPENAI_API_KEY')
    anthropic_api_key: Optional[str] = os.getenv('ANTHROPIC_API_KEY')
    
    # Feature Flags
    enable_ai_analysis: bool = os.getenv('ENABLE_AI_ANALYSIS', 'true').lower() == 'true'
    enable_stress_testing: bool = os.getenv('ENABLE_STRESS_TESTING', 'true').lower() == 'true'
    enable_pdf_export: bool = os.getenv('ENABLE_PDF_EXPORT', 'true').lower() == 'true'
    enable_excel_export: bool = os.getenv('ENABLE_EXCEL_EXPORT', 'true').lower() == 'true'
    
    # Resource Limits
    max_upload_size_mb: int = int(os.getenv('MAX_UPLOAD_SIZE_MB', '10'))
    max_memory_mb: int = int(os.getenv('MAX_MEMORY_MB', '2048'))
    request_timeout_seconds: int = int(os.getenv('REQUEST_TIMEOUT_SECONDS', '60'))
    simulation_timeout_seconds: int = int(os.getenv('SIMULATION_TIMEOUT_SECONDS', '30'))
    
    def __post_init__(self):
        """Validate configuration after initialization."""
        self._validate_config()
        self._log_config()
    
    def _validate_config(self):
        """Validate critical configuration values."""
        # Check production requirements
        if self.env == 'production':
            if self.secret_key == 'development-secret-key-change-in-production':
                raise ValueError("SECRET_KEY must be changed in production!")
            
            if self.debug:
                logger.warning("DEBUG is enabled in production - this is not recommended!")
            
            if not self.rate_limit_enabled:
                logger.warning("Rate limiting is disabled in production!")
        
        # Validate numeric ranges
        if self.cache_ttl < 0:
            raise ValueError("CACHE_TTL must be positive")
        
        if self.max_scenarios < 1 or self.max_scenarios > 100000:
            raise ValueError("MAX_SCENARIOS must be between 1 and 100,000")
        
        if self.rate_limit_per_minute < 1 or self.rate_limit_per_minute > 10000:
            raise ValueError("RATE_LIMIT_PER_MINUTE must be between 1 and 10,000")
        
        # Validate database config
        if self.db_enabled and not self.db_password:
            raise ValueError("DB_PASSWORD is required when DB_ENABLED=true")
        
        # Validate Redis config
        if self.redis_enabled and self.redis_password is None:
            logger.warning("REDIS_PASSWORD is not set - using unauthenticated Redis connection")
    
    def _log_config(self):
        """Log configuration (without secrets) for debugging."""
        logger.info(f"Application configuration loaded for environment: {self.env}")
        logger.debug(f"Debug mode: {self.debug}")
        logger.debug(f"Log level: {self.log_level}")
        logger.debug(f"Cache TTL: {self.cache_ttl}s")
        logger.debug(f"Max scenarios: {self.max_scenarios}")
        logger.debug(f"Redis enabled: {self.redis_enabled}")
        logger.debug(f"Database enabled: {self.db_enabled}")
        logger.debug(f"Rate limiting: {self.rate_limit_enabled}")
        logger.debug(f"Metrics enabled: {self.enable_metrics}")
        logger.debug(f"Sentry enabled: {bool(self.sentry_dsn)}")
    
    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.env == 'production'
    
    @property
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.env == 'development'
    
    @property
    def is_staging(self) -> bool:
        """Check if running in staging environment."""
        return self.env == 'staging'
    
    @property
    def redis_url(self) -> Optional[str]:
        """Get Redis connection URL."""
        if not self.redis_enabled:
            return None
        
        protocol = 'rediss' if self.redis_ssl else 'redis'
        auth = f':{self.redis_password}@' if self.redis_password else ''
        return f'{protocol}://{auth}{self.redis_host}:{self.redis_port}/{self.redis_db}'
    
    @property
    def database_url(self) -> Optional[str]:
        """Get PostgreSQL connection URL."""
        if not self.db_enabled:
            return None
        
        password = f':{self.db_password}' if self.db_password else ''
        return f'postgresql://{self.db_user}{password}@{self.db_host}:{self.db_port}/{self.db_name}'
    
    def get_safe_dict(self) -> dict:
        """Get configuration as dictionary (without secrets)."""
        config_dict = {
            'env': self.env,
            'debug': self.debug,
            'log_level': self.log_level,
            'cache_ttl': self.cache_ttl,
            'max_scenarios': self.max_scenarios,
            'redis_enabled': self.redis_enabled,
            'db_enabled': self.db_enabled,
            'rate_limit_enabled': self.rate_limit_enabled,
            'metrics_enabled': self.enable_metrics,
            'ai_analysis_enabled': self.enable_ai_analysis,
        }
        return config_dict


# Global configuration instance
config = AppConfig()


def get_config() -> AppConfig:
    """Get the global configuration instance."""
    return config


def reload_config():
    """Reload configuration from environment variables."""
    global config
    load_dotenv(override=True)
    config = AppConfig()
    return config


# Environment-specific configurations
class DevelopmentConfig(AppConfig):
    """Development environment configuration."""
    def __init__(self):
        super().__init__()
        self.env = 'development'
        self.debug = True
        self.log_level = 'DEBUG'
        self.rate_limit_enabled = False


class StagingConfig(AppConfig):
    """Staging environment configuration."""
    def __init__(self):
        super().__init__()
        self.env = 'staging'
        self.debug = False
        self.log_level = 'INFO'
        self.rate_limit_per_minute = 100


class ProductionConfig(AppConfig):
    """Production environment configuration."""
    def __init__(self):
        super().__init__()
        self.env = 'production'
        self.debug = False
        self.log_level = 'WARNING'
        self.rate_limit_per_minute = 60
        self.cache_ttl = 3600


def get_config_for_env(env: str) -> AppConfig:
    """Get configuration for specific environment."""
    env_configs = {
        'development': DevelopmentConfig,
        'staging': StagingConfig,
        'production': ProductionConfig,
    }
    
    config_class = env_configs.get(env, AppConfig)
    return config_class()


if __name__ == '__main__':
    # Test configuration loading
    print("Configuration loaded successfully!")
    print(f"Environment: {config.env}")
    print(f"Debug: {config.debug}")
    print(f"Redis enabled: {config.redis_enabled}")
    print(f"Database enabled: {config.db_enabled}")
    print(f"Safe config: {config.get_safe_dict()}")
