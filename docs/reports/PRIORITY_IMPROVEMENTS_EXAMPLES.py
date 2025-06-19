#!/usr/bin/env python3
"""
Priority Improvements for Dashboard API - Code Examples
These examples show specific implementations for the highest-priority improvements
identified in the code quality analysis.
"""

from typing import Dict, List, Optional, Union, Any, Callable, TypeVar
from dataclasses import dataclass, asdict
from enum import Enum
import structlog
import logging
import time
import threading
import os
from functools import wraps
import asyncio
import aiohttp

# ===== 1. COMPREHENSIVE TYPE HINTS =====

T = TypeVar('T')

@dataclass
class ServiceConfig:
    """Type-safe service configuration"""
    container_name: str
    port: Optional[int]
    health_url: Optional[str]
    env_file: Optional[str]
    config_files: List[str]
    data_dir: Optional[str]
    description: str
    category: str
    auth_header: Optional[str] = None

@dataclass
class CacheEntry:
    """Type-safe cache entry"""
    data: Any
    timestamp: float
    ttl: int

class CacheManager:
    """Thread-safe cache manager with type safety"""
    
    def __init__(self):
        self._cache: Dict[str, CacheEntry] = {}
        self._lock = threading.RLock()  # Recursive lock for nested operations
    
    def get(self, key: str) -> Optional[Any]:
        """Get cached data if not expired"""
        with self._lock:
            if key not in self._cache:
                return None
            
            entry = self._cache[key]
            if time.time() - entry.timestamp > entry.ttl:
                del self._cache[key]
                return None
            
            return entry.data
    
    def set(self, key: str, data: Any, ttl: int) -> None:
        """Set cached data with TTL"""
        with self._lock:
            self._cache[key] = CacheEntry(data=data, timestamp=time.time(), ttl=ttl)
    
    def clear_expired(self) -> int:
        """Remove expired entries and return count"""
        with self._lock:
            now = time.time()
            expired_keys = [
                key for key, entry in self._cache.items()
                if now - entry.timestamp > entry.ttl
            ]
            
            for key in expired_keys:
                del self._cache[key]
            
            return len(expired_keys)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        with self._lock:
            now = time.time()
            stats = {
                'total_entries': len(self._cache),
                'expired_entries': 0,
                'entries': {}
            }
            
            for key, entry in self._cache.items():
                age = now - entry.timestamp
                expires_in = entry.ttl - age
                
                if expires_in <= 0:
                    stats['expired_entries'] += 1
                
                stats['entries'][key] = {
                    'age': age,
                    'expires_in': expires_in,
                    'size': len(str(entry.data))
                }
            
            return stats

def get_cached_data(
    cache_manager: CacheManager,
    cache_key: str,
    cache_duration: int,
    fetch_function: Callable[..., T],
    *args: Any,
    **kwargs: Any
) -> T:
    """Type-safe cached data retrieval"""
    # Try to get from cache first
    cached_data = cache_manager.get(cache_key)
    if cached_data is not None:
        return cached_data
    
    # Fetch new data
    try:
        data = fetch_function(*args, **kwargs)
        cache_manager.set(cache_key, data, cache_duration)
        return data
    except Exception as e:
        # Try to return stale data if available
        with cache_manager._lock:
            if cache_key in cache_manager._cache:
                return cache_manager._cache[cache_key].data
        raise e

# ===== 2. STRUCTURED LOGGING =====

def setup_structured_logging(log_level: str = "INFO") -> structlog.BoundLogger:
    """Configure structured logging"""
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, log_level.upper()),
    )
    
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer()
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )
    
    return structlog.get_logger()

# Usage example
logger = setup_structured_logging()

def log_api_request(func):
    """Decorator for logging API requests"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        
        logger.info("api_request_start",
                   endpoint=func.__name__,
                   args_count=len(args),
                   kwargs_keys=list(kwargs.keys()))
        
        try:
            result = func(*args, **kwargs)
            duration = time.time() - start_time
            
            logger.info("api_request_success",
                       endpoint=func.__name__,
                       duration=duration,
                       response_type=type(result).__name__)
            
            return result
        
        except Exception as e:
            duration = time.time() - start_time
            
            logger.error("api_request_error",
                        endpoint=func.__name__,
                        duration=duration,
                        error_type=type(e).__name__,
                        error_message=str(e))
            raise
    
    return wrapper

# ===== 3. ENHANCED ERROR HANDLING =====

class APIErrorCode(Enum):
    """Standardized API error codes"""
    SERVICE_NOT_FOUND = "SERVICE_NOT_FOUND"
    DOCKER_UNAVAILABLE = "DOCKER_UNAVAILABLE"
    CACHE_ERROR = "CACHE_ERROR"
    INVALID_INPUT = "INVALID_INPUT"
    EXTERNAL_SERVICE_ERROR = "EXTERNAL_SERVICE_ERROR"
    TIMEOUT_ERROR = "TIMEOUT_ERROR"

@dataclass
class APIError(Exception):
    """Structured API error"""
    message: str
    code: APIErrorCode
    status_code: int = 500
    details: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON response"""
        result = {
            'error': {
                'message': self.message,
                'code': self.code.value,
                'status_code': self.status_code
            }
        }
        
        if self.details:
            result['error']['details'] = self.details
        
        return result

def handle_api_errors(func):
    """Decorator for consistent error handling"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        
        except APIError as e:
            logger.error("api_error",
                        endpoint=func.__name__,
                        error_code=e.code.value,
                        error_message=e.message,
                        status_code=e.status_code)
            
            return jsonify(e.to_dict()), e.status_code
        
        except Exception as e:
            logger.error("unexpected_error",
                        endpoint=func.__name__,
                        error_type=type(e).__name__,
                        error_message=str(e))
            
            error = APIError(
                message="Internal server error",
                code=APIErrorCode.EXTERNAL_SERVICE_ERROR,
                status_code=500,
                details={'original_error': str(e)}
            )
            
            return jsonify(error.to_dict()), 500
    
    return wrapper

# ===== 4. CONFIGURATION MANAGEMENT =====

from pydantic import BaseSettings, validator

class DashboardSettings(BaseSettings):
    """Type-safe configuration management"""
    
    # API Settings
    api_host: str = "0.0.0.0"
    api_port: int = 5002
    debug_mode: bool = False
    
    # External Services
    litellm_api_key: str = "sk-1234567890abcdef"
    docker_compose_file: str = "compose.local.yml"
    
    # Cache Settings
    cache_system_metrics_ttl: int = 10
    cache_docker_stats_ttl: int = 15
    cache_service_health_ttl: int = 30
    cache_container_resources_ttl: int = 20
    cache_cleanup_interval: int = 300  # 5 minutes
    
    # Timeouts
    health_check_timeout: int = 3
    docker_operation_timeout: int = 30
    
    # Logging
    log_level: str = "INFO"
    log_format: str = "json"
    
    @validator('log_level')
    def validate_log_level(cls, v):
        valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if v.upper() not in valid_levels:
            raise ValueError(f'log_level must be one of {valid_levels}')
        return v.upper()
    
    @validator('api_port')
    def validate_port(cls, v):
        if not 1 <= v <= 65535:
            raise ValueError('api_port must be between 1 and 65535')
        return v
    
    class Config:
        env_file = ".env"
        env_prefix = "DASHBOARD_"

# ===== 5. ASYNC IMPLEMENTATION EXAMPLE =====

class AsyncServiceHealthChecker:
    """Async service health checking"""
    
    def __init__(self, settings: DashboardSettings):
        self.settings = settings
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=self.settings.health_check_timeout)
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def check_service_health(
        self, 
        service_name: str, 
        config: ServiceConfig
    ) -> Dict[str, Any]:
        """Async health check for a single service"""
        
        if not config.health_url:
            return {
                'container_status': 'unknown',
                'health_status': 'unknown',
                'timestamp': time.time()
            }
        
        try:
            headers = {}
            if config.auth_header:
                headers['Authorization'] = config.auth_header
            
            async with self.session.get(config.health_url, headers=headers) as response:
                health_status = 'healthy' if response.status == 200 else 'unhealthy'
                
                return {
                    'container_status': 'running',  # Simplified for async example
                    'health_status': health_status,
                    'response_time': response.headers.get('X-Response-Time'),
                    'timestamp': time.time()
                }
        
        except asyncio.TimeoutError:
            raise APIError(
                message=f"Health check timeout for service {service_name}",
                code=APIErrorCode.TIMEOUT_ERROR,
                status_code=503
            )
        
        except Exception as e:
            logger.warning("health_check_failed",
                          service=service_name,
                          error=str(e))
            
            return {
                'container_status': 'unknown',
                'health_status': 'unhealthy',
                'error': str(e),
                'timestamp': time.time()
            }
    
    async def check_all_services(
        self, 
        services: Dict[str, ServiceConfig]
    ) -> Dict[str, Dict[str, Any]]:
        """Check health of all services concurrently"""
        
        tasks = [
            self.check_service_health(name, config)
            for name, config in services.items()
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        return {
            name: result if not isinstance(result, Exception) else {
                'container_status': 'error',
                'health_status': 'error',
                'error': str(result),
                'timestamp': time.time()
            }
            for (name, _), result in zip(services.items(), results)
        }

# ===== 6. USAGE EXAMPLE =====

def create_improved_api():
    """Example of how to integrate all improvements"""
    
    # Load configuration
    settings = DashboardSettings()
    
    # Setup logging
    logger = setup_structured_logging(settings.log_level)
    
    # Initialize cache manager
    cache_manager = CacheManager()
    
    # Setup cache cleanup
    def cleanup_cache():
        expired_count = cache_manager.clear_expired()
        logger.info("cache_cleanup", expired_count=expired_count)
        threading.Timer(settings.cache_cleanup_interval, cleanup_cache).start()
    
    cleanup_cache()
    
    logger.info("api_initialized",
               port=settings.api_port,
               cache_ttl_settings={
                   'system_metrics': settings.cache_system_metrics_ttl,
                   'docker_stats': settings.cache_docker_stats_ttl,
                   'service_health': settings.cache_service_health_ttl
               })
    
    return {
        'settings': settings,
        'logger': logger,
        'cache_manager': cache_manager
    }

if __name__ == "__main__":
    # Example usage
    components = create_improved_api()
    print("✅ Improved API components initialized successfully!")
    print(f"📊 Cache stats: {components['cache_manager'].get_stats()}")
