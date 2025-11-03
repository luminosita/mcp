# Python Microservice Architecture Research Report

**Document Version:** 1.0
**Research Date:** 2025-11-01
**Researcher:** Context Engineering PoC Team
**Target Framework:** FastAPI 0.100+, Python 3.10+

## Executive Summary

This research report establishes architectural standards for scalable Python microservice implementations using FastAPI, focusing on production-ready patterns that align with SOLID principles, Clean Architecture, and Domain-Driven Design (DDD). Based on analysis of official documentation, established open-source projects, and community best practices, this report provides actionable guidance across critical architectural areas including configuration, logging, caching, data access, error handling, telemetry, and audit logging.

**Key Findings:**
1. **Configuration Management:** Pydantic's `BaseSettings` with `@lru_cache` optimization provides type-safe, environment-based configuration with minimal overhead[^1]
2. **Dependency Injection:** FastAPI's native `Depends()` system sufficient for most use cases; external DI containers (dependency-injector) recommended only for complex enterprise scenarios[^2]
3. **Database Layer:** Async SQLAlchemy with Repository pattern achieves both Clean Architecture compliance and high performance, with `expire_on_commit=False` critical for async operations[^3]
4. **Structured Logging:** structlog with JSON rendering provides production-grade observability with request correlation[^4]
5. **Caching:** Redis with async client (redis-py 4.2+) using cache-aside pattern balances performance and data freshness[^5]
6. **Telemetry & Observability:** OpenTelemetry with Prometheus delivers vendor-neutral distributed tracing and metrics without lock-in[^42][^43]
7. **Audit Logging:** Structured audit events with immutable storage (append-only tables or event streams) ensures compliance with SOC 2, GDPR, and HIPAA requirements[^51][^52]

**Critical Architectural Decision:** Adopt layered Clean Architecture (Domain → Application → Infrastructure → Presentation) over feature-based organization for microservices exceeding 5,000 lines of code, as this enforces dependency inversion and enables independent layer testing[^6].

---

## 1. Configuration Management

### 1.1 Recommended Approach: Pydantic BaseSettings with LRU Cache

FastAPI leverages Pydantic's `BaseSettings` for type-safe configuration management with automatic environment variable binding[^1]. This approach provides runtime validation, IDE autocomplete support, and seamless integration with FastAPI's dependency injection system.

**Core Benefits:**
- **Type Safety:** Automatic conversion and validation of environment variables to Python types
- **12-Factor Compliance:** Strict separation of configuration from code[^7]
- **Zero Boilerplate:** Environment variables loaded automatically without explicit `os.getenv()` calls
- **Case Insensitivity:** Handles `APP_NAME`, `app_name`, or `App_Name` uniformly

### 1.2 Configuration Initialization Patterns

Proper configuration initialization is critical for reliable application startup, especially in containerized and multi-environment deployments. The `Settings` object must be initialized with appropriate environment-specific values before any application components access configuration.

#### 1.2.1 Pattern 1: Lifespan-Based Initialization with Singleton (Recommended)

Initialize configuration during FastAPI application lifespan startup, making it available throughout the application lifecycle via `@lru_cache` optimization[^27][^28].

```python
# File: src/core/config.py
from functools import lru_cache
from pydantic import Field, PostgresDsn, RedisDsn, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Literal
import structlog

logger = structlog.get_logger(__name__)

class Settings(BaseSettings):
    """
    Application configuration loaded from environment variables.

    Uses Pydantic BaseSettings for type-safe configuration management
    with automatic environment variable binding and validation.
    """

    # Application metadata
    app_name: str = Field(default="AI Agent MCP Server")
    environment: Literal["development", "staging", "production"] = Field(
        default="development",
        description="Deployment environment"
    )
    debug: bool = Field(default=False)
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = Field(default="INFO")

    # Server configuration
    host: str = Field(default="0.0.0.0")
    port: int = Field(default=8000, ge=1024, le=65535)
    workers: int = Field(default=1, ge=1, le=16)

    # Database configuration
    database_url: PostgresDsn = Field(
        description="PostgreSQL connection string (async driver: postgresql+asyncpg://...)"
    )
    db_pool_size: int = Field(default=10, ge=5, le=50)
    db_max_overflow: int = Field(default=20, ge=5, le=100)
    db_pool_recycle: int = Field(default=3600)  # 1 hour
    db_pool_pre_ping: bool = Field(default=True)

    # Cache configuration
    redis_url: RedisDsn = Field(description="Redis connection string (redis://...)")
    cache_ttl_default: int = Field(default=300, ge=10, le=86400)  # 5 minutes
    redis_max_connections: int = Field(default=20, ge=5, le=100)

    # Security
    secret_key: str = Field(min_length=32, description="Secret key for JWT signing")
    allowed_origins: list[str] = Field(
        default=["http://localhost:3000"],
        description="CORS allowed origins"
    )
    api_key_header: str = Field(default="X-API-Key")

    # External services
    external_api_url: str | None = Field(default=None)
    external_api_timeout: int = Field(default=30, ge=5, le=300)

    model_config = SettingsConfigDict(
        env_file=".env",               # Load from .env file if present
        env_file_encoding="utf-8",
        case_sensitive=False,          # APP_NAME and app_name both work
        extra="forbid",                # Raise error on unknown env vars (typo detection)
        validate_default=True          # Validate default values
    )

    @field_validator("database_url")
    @classmethod
    def validate_async_database_url(cls, v: PostgresDsn) -> PostgresDsn:
        """
        Ensure database URL uses async driver (asyncpg for PostgreSQL).

        Common mistake: Using psycopg2 (sync) instead of asyncpg (async).
        """
        if v.scheme not in ["postgresql+asyncpg"]:
            raise ValueError(
                f"Database URL must use async driver (postgresql+asyncpg), got: {v.scheme}"
            )
        return v

    @field_validator("secret_key")
    @classmethod
    def validate_secret_key_strength(cls, v: str) -> str:
        """
        Validate secret key is not a weak default.

        Production deployments must use strong, unique secret keys.
        """
        weak_keys = [
            "changeme",
            "secret",
            "password",
            "12345678901234567890123456789012"  # 32 character default
        ]
        if v.lower() in weak_keys:
            raise ValueError(
                "Secret key must not be a weak default. "
                "Generate with: python -c 'import secrets; print(secrets.token_urlsafe(32))'"
            )
        return v

    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.environment == "production"

    def is_debug_enabled(self) -> bool:
        """Check if debug mode enabled (never true in production)."""
        return self.debug and not self.is_production()

@lru_cache
def get_settings() -> Settings:
    """
    Create cached settings instance (singleton pattern).

    Uses lru_cache to ensure .env file is read only once per application
    lifecycle, not per request. Without caching, each request would
    perform file I/O and validation, degrading performance by ~5-10ms/request.

    Cache cleared only when application restarts (configuration changes
    require restart to take effect).
    """
    return Settings()

# File: src/main.py
from contextlib import asynccontextmanager
from fastapi import FastAPI
from src.core.config import get_settings
from src.core.logging import configure_logging
import structlog
import sys

logger = structlog.get_logger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.

    Startup order is critical:
    1. Load and validate configuration (FIRST - validates env vars)
    2. Configure logging based on environment
    3. Initialize database engine
    4. Initialize Redis cache
    5. Initialize external service clients
    """
    # Step 1: Load configuration (validates all env vars, fails fast on error)
    try:
        settings = get_settings()
        logger.info(
            "configuration_loaded",
            app_name=settings.app_name,
            environment=settings.environment,
            debug=settings.debug
        )
    except Exception as e:
        # Configuration validation failed - log and exit immediately
        logger.error("configuration_validation_failed", error=str(e))
        sys.exit(1)  # Exit with error code (container orchestrator will restart)

    # Step 2: Configure logging based on environment
    configure_logging(
        environment="production" if settings.is_production() else "development"
    )
    logger.info("logging_configured", log_level=settings.log_level)

    # Step 3: Initialize database engine
    from src.infrastructure.database.engine import session_manager
    session_manager.init(
        database_url=str(settings.database_url),
        pool_size=settings.db_pool_size,
        max_overflow=settings.db_max_overflow,
        pool_recycle=settings.db_pool_recycle
    )
    logger.info("database_initialized", pool_size=settings.db_pool_size)

    # Step 4: Initialize Redis cache
    from src.infrastructure.cache.redis_manager import redis_manager
    await redis_manager.connect(
        redis_url=str(settings.redis_url),
        max_connections=settings.redis_max_connections
    )
    logger.info("cache_initialized", max_connections=settings.redis_max_connections)

    # Step 5: Verify critical configuration values
    if settings.is_production():
        # Production-specific validation
        if settings.debug:
            logger.warning(
                "debug_mode_in_production",
                message="DEBUG mode should be disabled in production"
            )

        if "localhost" in settings.allowed_origins:
            logger.warning(
                "localhost_cors_in_production",
                message="Localhost should not be in allowed_origins for production"
            )

    logger.info(
        "application_ready",
        environment=settings.environment,
        host=settings.host,
        port=settings.port
    )

    yield  # Application runs here

    # Shutdown: Close resources in reverse order
    logger.info("application_shutdown_started")

    await redis_manager.disconnect()
    logger.info("cache_closed")

    await session_manager.close()
    logger.info("database_closed")

    logger.info("application_shutdown_complete")

def create_app() -> FastAPI:
    """Create and configure FastAPI application."""
    settings = get_settings()

    app = FastAPI(
        title=settings.app_name,
        debug=settings.is_debug_enabled(),
        lifespan=lifespan
    )

    # Add middleware
    from src.middleware.logging_middleware import RequestLoggingMiddleware
    app.add_middleware(RequestLoggingMiddleware)

    # Add CORS middleware
    from fastapi.middleware.cors import CORSMiddleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"]
    )

    # Register routes
    from src.api.routes import users, health
    app.include_router(health.router, tags=["Health"])
    app.include_router(users.router, prefix="/api/v1", tags=["Users"])

    return app

app = create_app()

if __name__ == "__main__":
    import uvicorn

    settings = get_settings()

    # For programmatic run, ensure logging configured before uvicorn starts
    if not hasattr(sys, "_called_from_test"):
        configure_logging(
            environment="production" if settings.is_production() else "development"
        )

    uvicorn.run(
        "src.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.is_debug_enabled(),
        log_level=settings.log_level.lower(),
        workers=settings.workers if settings.is_production() else 1
    )
```

**Usage in FastAPI routes:**

```python
# File: src/api/routes/health.py
from fastapi import APIRouter, Depends
from src.core.config import Settings, get_settings
import structlog

router = APIRouter()
logger = structlog.get_logger(__name__)

@router.get("/health")
async def health_check(settings: Settings = Depends(get_settings)):
    """
    Health check endpoint with configuration access.

    Settings injected via dependency injection (cached singleton).
    No file I/O per request - configuration loaded once at startup.
    """
    return {
        "status": "healthy",
        "app_name": settings.app_name,
        "environment": settings.environment,
        "debug_mode": settings.is_debug_enabled()
    }

@router.get("/health/config")
async def config_health(settings: Settings = Depends(get_settings)):
    """
    Configuration health check (non-sensitive values only).

    Use to verify configuration loaded correctly in deployed environment.
    """
    return {
        "status": "healthy",
        "configuration": {
            "app_name": settings.app_name,
            "environment": settings.environment,
            "debug": settings.is_debug_enabled(),
            "database_pool_size": settings.db_pool_size,
            "redis_max_connections": settings.redis_max_connections,
            "log_level": settings.log_level,
            # DO NOT expose sensitive values (secret_key, database_url, etc.)
        }
    }
```

**Benefits:**
- ✅ Configuration validated at startup (fail-fast on misconfiguration)
- ✅ Singleton pattern ensures .env file read only once (no per-request overhead)
- ✅ Type safety with Pydantic validation (catches typos and invalid values)
- ✅ Environment-specific behavior (production vs development checks)
- ✅ Proper shutdown sequence (resources released in reverse order)
- ✅ Structured logging of configuration events

**Use When:** Production applications requiring robust configuration management (default recommendation)

#### 1.2.2 Pattern 2: Module-Level Initialization (Simple Applications)

Initialize configuration at module level for immediate availability. Suitable for simple applications with minimal configuration requirements[^29].

```python
# File: src/core/config.py
from functools import lru_cache
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """Application configuration with minimal settings."""

    app_name: str = Field(default="Simple Microservice")
    debug: bool = Field(default=False)
    log_level: str = Field(default="INFO")

    # Database
    database_url: str = Field(description="Database connection string")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="forbid"
    )

@lru_cache
def get_settings() -> Settings:
    """Create cached settings instance."""
    return Settings()

# Initialize at module level (runs when module imported)
_settings = get_settings()

# File: src/main.py
from fastapi import FastAPI
from src.core.config import _settings  # Configuration loaded on import

# Configuration available immediately
app = FastAPI(
    title=_settings.app_name,
    debug=_settings.debug
)

@app.get("/health")
async def health():
    """Health check using module-level config."""
    return {
        "status": "healthy",
        "app_name": _settings.app_name,
        "debug": _settings.debug
    }

if __name__ == "__main__":
    import uvicorn

    # Configuration already loaded
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=8000,
        reload=_settings.debug
    )
```

**Benefits:**
- ✅ Simple, minimal boilerplate
- ✅ Configuration available immediately when module imported
- ✅ No explicit initialization step needed

**Drawbacks:**
- ❌ Module-level side effects (configuration loaded on import)
- ❌ Harder to override for testing (module already imported)
- ❌ No control over initialization order
- ❌ Cannot handle initialization failures gracefully (no lifespan context)

**Use When:**
- Simple applications with <10 configuration values
- Single-file FastAPI applications
- Prototypes or proof-of-concept projects

#### 1.2.3 Pattern 3: Lazy Initialization with Singleton (Test-Friendly)

Use lazy initialization with explicit singleton management for better test isolation and configuration reloading capabilities[^30].

```python
# File: src/core/config.py
from pydantic import Field, PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional
import structlog

logger = structlog.get_logger(__name__)

class Settings(BaseSettings):
    """Application configuration with lazy initialization support."""

    app_name: str = Field(default="Test-Friendly Microservice")
    environment: str = Field(default="development")
    debug: bool = Field(default=False)

    database_url: PostgresDsn = Field(
        description="PostgreSQL connection string"
    )
    db_pool_size: int = Field(default=10, ge=5, le=50)

    redis_url: str = Field(description="Redis connection string")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="forbid"
    )

class SettingsManager:
    """
    Singleton settings manager with lazy initialization and reset support.

    Enables test isolation by providing reset() method to clear cached
    settings between tests.
    """

    def __init__(self):
        self._settings: Optional[Settings] = None
        self._initialized: bool = False

    def get_settings(self, force_reload: bool = False) -> Settings:
        """
        Get settings instance (creates on first access).

        Args:
            force_reload: Force reload from environment (for testing)

        Returns:
            Cached Settings instance
        """
        if self._settings is None or force_reload:
            logger.info(
                "loading_configuration",
                force_reload=force_reload,
                initialized=self._initialized
            )

            try:
                self._settings = Settings()
                self._initialized = True

                logger.info(
                    "configuration_loaded",
                    app_name=self._settings.app_name,
                    environment=self._settings.environment
                )
            except Exception as e:
                logger.error("configuration_load_failed", error=str(e))
                raise

        return self._settings

    def reset(self) -> None:
        """
        Reset settings (for testing only).

        Clears cached settings, allowing next get_settings() call
        to reload from environment variables.
        """
        logger.debug("resetting_configuration")
        self._settings = None
        self._initialized = False

    def is_initialized(self) -> bool:
        """Check if settings have been loaded."""
        return self._initialized

# Global singleton instance
_settings_manager = SettingsManager()

def get_settings(force_reload: bool = False) -> Settings:
    """
    Get application settings (lazy initialization).

    Args:
        force_reload: Force reload from environment (testing only)

    Returns:
        Settings instance (cached after first call)
    """
    return _settings_manager.get_settings(force_reload=force_reload)

def reset_settings() -> None:
    """
    Reset settings singleton (for testing only).

    Call in test fixtures to ensure clean state between tests.
    """
    _settings_manager.reset()

# File: src/main.py
from contextlib import asynccontextmanager
from fastapi import FastAPI
from src.core.config import get_settings
import structlog

logger = structlog.get_logger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan with lazy configuration initialization."""
    # Configuration loaded lazily on first get_settings() call
    settings = get_settings()

    logger.info(
        "application_startup",
        app_name=settings.app_name,
        environment=settings.environment
    )

    # Initialize resources...
    yield

    logger.info("application_shutdown")

app = FastAPI(lifespan=lifespan)

@app.get("/health")
async def health():
    """Health check with lazy configuration access."""
    settings = get_settings()  # Lazy load on first access
    return {
        "status": "healthy",
        "app_name": settings.app_name,
        "environment": settings.environment
    }

# File: tests/conftest.py
import pytest
from src.core.config import reset_settings
import os

@pytest.fixture(autouse=True)
def configure_test_environment():
    """
    Configure test environment with clean settings for each test.

    This fixture runs automatically before each test, ensuring:
    1. Settings singleton reset
    2. Test-specific environment variables set
    3. Clean state between tests
    """
    # Reset settings from previous test
    reset_settings()

    # Set test-specific environment variables
    os.environ["ENVIRONMENT"] = "testing"
    os.environ["DEBUG"] = "true"
    os.environ["DATABASE_URL"] = "postgresql+asyncpg://test:test@localhost:5432/test_db"
    os.environ["REDIS_URL"] = "redis://localhost:6379/1"

    yield  # Run test

    # Cleanup: Reset settings after test
    reset_settings()

@pytest.fixture
def settings_with_override():
    """
    Provide settings with custom overrides for specific tests.

    Example usage:
        def test_with_custom_config(settings_with_override):
            settings = settings_with_override({"DEBUG": "false"})
            assert not settings.debug
    """
    def _create_settings(overrides: dict[str, str]):
        """Apply environment variable overrides and force reload."""
        # Reset existing settings
        reset_settings()

        # Apply overrides
        for key, value in overrides.items():
            os.environ[key] = value

        # Load settings with overrides
        from src.core.config import get_settings
        return get_settings(force_reload=True)

    return _create_settings

# File: tests/unit/test_config.py
import pytest
from src.core.config import get_settings, reset_settings
import os

def test_settings_singleton():
    """Test settings singleton behavior."""
    settings1 = get_settings()
    settings2 = get_settings()

    # Same instance returned
    assert settings1 is settings2

def test_settings_force_reload():
    """Test force reload clears cache."""
    settings1 = get_settings()

    # Change environment variable
    os.environ["APP_NAME"] = "Modified Name"

    # Without force_reload, old value returned (cached)
    settings2 = get_settings()
    assert settings2.app_name == settings1.app_name

    # With force_reload, new value loaded
    settings3 = get_settings(force_reload=True)
    assert settings3.app_name == "Modified Name"

def test_settings_reset_between_tests():
    """Test reset_settings() clears cache."""
    settings1 = get_settings()

    reset_settings()

    settings2 = get_settings()

    # Different instances after reset
    assert settings1 is not settings2

def test_settings_with_custom_config(settings_with_override):
    """Test custom configuration override fixture."""
    # Override debug setting for this test only
    settings = settings_with_override({"DEBUG": "false"})

    assert not settings.debug

    # Next test will have clean environment (via autouse fixture)
```

**Benefits:**
- ✅ Lazy initialization (configuration loaded on first access, not at import)
- ✅ Test-friendly with reset() method for clean state between tests
- ✅ Explicit control over initialization timing
- ✅ Force reload capability for testing different configurations
- ✅ Singleton pattern ensures single Settings instance per application lifecycle

**Drawbacks:**
- ❌ More boilerplate than `@lru_cache` approach
- ❌ Requires explicit reset in test fixtures
- ❌ Global mutable state (_settings_manager)

**Use When:**
- Applications with complex test requirements (need to test multiple configurations)
- Need to reload configuration without restarting application (rare - usually anti-pattern)
- Testing framework requires explicit control over singleton lifecycle

#### 1.2.4 Pattern 4: Environment-Specific Configuration Loading

Use separate configuration classes for different environments with factory pattern for selection[^31].

```python
# File: src/core/config.py
from pydantic import Field, PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Literal
from functools import lru_cache
import structlog

logger = structlog.get_logger(__name__)

class BaseEnvironmentSettings(BaseSettings):
    """Base settings shared across all environments."""

    app_name: str = Field(default="Multi-Environment Microservice")
    environment: Literal["development", "staging", "production"]

    # Database
    database_url: PostgresDsn
    db_pool_size: int = Field(default=10, ge=5, le=50)

    # Cache
    redis_url: str
    cache_ttl_default: int = Field(default=300)

    # Security
    secret_key: str = Field(min_length=32)

    model_config = SettingsConfigDict(
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="forbid"
    )

class DevelopmentSettings(BaseEnvironmentSettings):
    """Development-specific configuration."""

    # Override defaults for development
    environment: Literal["development"] = "development"
    debug: bool = Field(default=True)
    log_level: str = Field(default="DEBUG")

    # Development uses smaller pool sizes
    db_pool_size: int = Field(default=5)
    db_pool_recycle: int = Field(default=300)  # 5 minutes

    # Development allows all CORS origins
    allowed_origins: list[str] = Field(default=["*"])

    # Development-specific features
    reload_on_change: bool = Field(default=True)
    enable_debug_toolbar: bool = Field(default=True)

    model_config = SettingsConfigDict(
        env_file=".env.development",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="forbid"
    )

class StagingSettings(BaseEnvironmentSettings):
    """Staging-specific configuration."""

    environment: Literal["staging"] = "staging"
    debug: bool = Field(default=False)
    log_level: str = Field(default="INFO")

    # Staging uses medium pool sizes
    db_pool_size: int = Field(default=10)
    db_pool_recycle: int = Field(default=3600)  # 1 hour

    # Staging allows specific test domains
    allowed_origins: list[str] = Field(
        default=["https://staging.example.com"]
    )

    # Staging-specific features
    enable_debug_toolbar: bool = Field(default=False)
    enable_profiling: bool = Field(default=True)

    model_config = SettingsConfigDict(
        env_file=".env.staging",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="forbid"
    )

class ProductionSettings(BaseEnvironmentSettings):
    """Production-specific configuration."""

    environment: Literal["production"] = "production"
    debug: bool = Field(default=False)
    log_level: str = Field(default="WARNING")

    # Production uses large pool sizes
    db_pool_size: int = Field(default=20)
    db_max_overflow: int = Field(default=40)
    db_pool_recycle: int = Field(default=3600)  # 1 hour

    # Production restricts CORS to specific domains
    allowed_origins: list[str] = Field(
        default=["https://example.com", "https://www.example.com"]
    )

    # Production-specific features
    enable_debug_toolbar: bool = Field(default=False)
    enable_profiling: bool = Field(default=False)
    enable_monitoring: bool = Field(default=True)

    # Production security hardening
    require_https: bool = Field(default=True)
    strict_security_headers: bool = Field(default=True)

    model_config = SettingsConfigDict(
        env_file=".env.production",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="forbid"
    )

# Type alias for all settings types
SettingsType = DevelopmentSettings | StagingSettings | ProductionSettings

def create_settings(environment: str | None = None) -> SettingsType:
    """
    Factory function to create environment-specific settings.

    Args:
        environment: Target environment ("development", "staging", "production")
                    If None, read from ENVIRONMENT env var

    Returns:
        Environment-specific Settings instance

    Raises:
        ValueError: If environment is invalid
    """
    if environment is None:
        import os
        environment = os.getenv("ENVIRONMENT", "development").lower()

    logger.info("creating_settings", environment=environment)

    settings_map = {
        "development": DevelopmentSettings,
        "staging": StagingSettings,
        "production": ProductionSettings
    }

    settings_class = settings_map.get(environment)

    if settings_class is None:
        raise ValueError(
            f"Invalid environment: {environment}. "
            f"Must be one of: {list(settings_map.keys())}"
        )

    try:
        settings = settings_class()
        logger.info(
            "settings_created",
            environment=settings.environment,
            app_name=settings.app_name,
            debug=settings.debug
        )
        return settings
    except Exception as e:
        logger.error(
            "settings_creation_failed",
            environment=environment,
            error=str(e)
        )
        raise

@lru_cache
def get_settings() -> SettingsType:
    """
    Get cached environment-specific settings.

    Environment determined by ENVIRONMENT env var.
    Creates singleton instance for application lifecycle.
    """
    return create_settings()

# File: src/main.py
from contextlib import asynccontextmanager
from fastapi import FastAPI
from src.core.config import get_settings, DevelopmentSettings
import structlog

logger = structlog.get_logger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan with environment-specific initialization."""
    settings = get_settings()

    logger.info(
        "application_startup",
        environment=settings.environment,
        app_name=settings.app_name,
        debug=settings.debug
    )

    # Environment-specific initialization
    if isinstance(settings, DevelopmentSettings):
        logger.info("development_mode_enabled", features={
            "reload_on_change": settings.reload_on_change,
            "debug_toolbar": settings.enable_debug_toolbar
        })

    # Initialize resources...
    yield

    logger.info("application_shutdown")

def create_app() -> FastAPI:
    """Create FastAPI app with environment-specific configuration."""
    settings = get_settings()

    app = FastAPI(
        title=settings.app_name,
        debug=settings.debug,
        lifespan=lifespan
    )

    # Environment-specific middleware
    if settings.debug:
        # Add debug toolbar in development
        if isinstance(settings, DevelopmentSettings) and settings.enable_debug_toolbar:
            # from debug_toolbar import DebugToolbarMiddleware
            # app.add_middleware(DebugToolbarMiddleware)
            logger.info("debug_toolbar_enabled")

    # Add CORS with environment-specific origins
    from fastapi.middleware.cors import CORSMiddleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"]
    )

    return app

app = create_app()

# File: .env.development (example)
"""
ENVIRONMENT=development
APP_NAME=My Microservice (Dev)
DEBUG=true
LOG_LEVEL=DEBUG

DATABASE_URL=postgresql+asyncpg://dev:dev@localhost:5432/dev_db
REDIS_URL=redis://localhost:6379/0

SECRET_KEY=dev-secret-key-minimum-32-characters-required-here
"""

# File: .env.production (example)
"""
ENVIRONMENT=production
APP_NAME=My Microservice
DEBUG=false
LOG_LEVEL=WARNING

DATABASE_URL=postgresql+asyncpg://prod:${DB_PASSWORD}@db.example.com:5432/prod_db
REDIS_URL=redis://:${REDIS_PASSWORD}@cache.example.com:6379/0

SECRET_KEY=${SECRET_KEY}
ALLOWED_ORIGINS=https://example.com,https://www.example.com
"""
```

**Benefits:**
- ✅ Clear separation of environment-specific configuration
- ✅ Type-safe environment-specific fields (IDE autocomplete)
- ✅ Separate .env files per environment (prevents production config leaks)
- ✅ Easy to add environment-specific features (debug toolbar, profiling, monitoring)
- ✅ Factory pattern allows explicit environment selection (useful for testing)

**Drawbacks:**
- ❌ More boilerplate (separate class per environment)
- ❌ Configuration duplication across environment classes
- ❌ Must maintain multiple .env files

**Use When:**
- Applications deployed to multiple environments (dev, staging, production)
- Environments require significantly different configuration (not just value changes)
- Need environment-specific features or middleware
- Compliance requirements for separate configuration files per environment

### 1.2.2 Common Configuration Mistakes

**❌ Mistake 1: Not validating configuration at startup**

```python
# BAD: Configuration errors discovered during request handling
from src.core.config import get_settings

app = FastAPI()

@app.get("/users")
async def get_users():
    settings = get_settings()
    # ERROR: database_url is invalid, but only discovered here!
    conn = await asyncpg.connect(settings.database_url)
    # Application crashes during request
```

**✅ Fix: Validate configuration during startup**

```python
# GOOD: Configuration validated during lifespan startup
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load and validate ALL configuration at startup
    try:
        settings = get_settings()
        logger.info("configuration_validated", app_name=settings.app_name)
    except Exception as e:
        logger.error("configuration_invalid", error=str(e))
        sys.exit(1)  # Exit immediately, don't start with invalid config

    # Test database connection
    try:
        from src.infrastructure.database.engine import session_manager
        session_manager.init(database_url=str(settings.database_url))
        logger.info("database_connection_verified")
    except Exception as e:
        logger.error("database_connection_failed", error=str(e))
        sys.exit(1)

    yield

app = FastAPI(lifespan=lifespan)
# Application will not start if configuration invalid
```

**❌ Mistake 2: Exposing sensitive configuration in health endpoints**

```python
# BAD: Health endpoint exposes secrets
@router.get("/health")
async def health(settings: Settings = Depends(get_settings)):
    return {
        "status": "healthy",
        "config": settings.dict()  # DANGER: Exposes secret_key, database_url!
    }
```

**✅ Fix: Only expose non-sensitive configuration**

```python
# GOOD: Whitelist non-sensitive fields
@router.get("/health/config")
async def config_health(settings: Settings = Depends(get_settings)):
    """Configuration health check (non-sensitive values only)."""
    return {
        "status": "healthy",
        "configuration": {
            "app_name": settings.app_name,
            "environment": settings.environment,
            "debug": settings.debug,
            "log_level": settings.log_level,
            # NEVER expose: secret_key, database_url, redis_url, api keys
        }
    }
```

**❌ Mistake 3: Using weak or default secrets in production**

```python
# BAD: Weak secret key in .env file
SECRET_KEY=changeme  # Will fail validation
SECRET_KEY=12345678901234567890123456789012  # Common default
```

**✅ Fix: Generate strong secrets with validation**

```python
# GOOD: Generate strong secret key
# Command: python -c 'import secrets; print(secrets.token_urlsafe(32))'
SECRET_KEY=A3xK9m2pR7wE5qT8nL4jH6sV1cZ0yB9fG2uD8oP5kN3

# Validation in Settings class prevents weak keys
@field_validator("secret_key")
@classmethod
def validate_secret_key_strength(cls, v: str) -> str:
    """Validate secret key is not a weak default."""
    weak_keys = ["changeme", "secret", "password"]
    if v.lower() in weak_keys:
        raise ValueError("Secret key must not be a weak default")
    return v
```

### 1.2.3 Verification and Troubleshooting

**Verify configuration health with dedicated endpoint:**

```python
# File: src/api/routes/health.py
from fastapi import APIRouter, Depends, status
from src.core.config import Settings, get_settings
import structlog

router = APIRouter()
logger = structlog.get_logger(__name__)

@router.get("/health/config")
async def configuration_health(settings: Settings = Depends(get_settings)):
    """
    Configuration health check endpoint.

    Returns non-sensitive configuration values to verify
    application loaded configuration correctly.

    Use for deployment verification and troubleshooting.
    """
    logger.info("configuration_health_check_requested")

    # Collect non-sensitive configuration
    config_status = {
        "status": "healthy",
        "configuration": {
            # Application
            "app_name": settings.app_name,
            "environment": settings.environment,
            "debug": settings.is_debug_enabled(),
            "log_level": settings.log_level,

            # Server
            "host": settings.host,
            "port": settings.port,
            "workers": settings.workers,

            # Database (non-sensitive)
            "database_pool_size": settings.db_pool_size,
            "database_max_overflow": settings.db_max_overflow,
            "database_pool_recycle": settings.db_pool_recycle,
            "database_pre_ping": settings.db_pool_pre_ping,

            # Cache (non-sensitive)
            "cache_ttl_default": settings.cache_ttl_default,
            "redis_max_connections": settings.redis_max_connections,

            # Security (non-sensitive)
            "allowed_origins": settings.allowed_origins,
            "api_key_header": settings.api_key_header,

            # External services (non-sensitive)
            "external_api_timeout": settings.external_api_timeout,
        }
    }

    return config_status

@router.get("/health/config/validation")
async def configuration_validation(settings: Settings = Depends(get_settings)):
    """
    Configuration validation endpoint.

    Performs validation checks on configuration values and
    reports any warnings or issues (without exposing secrets).
    """
    warnings = []
    errors = []

    # Check production safety
    if settings.is_production():
        if settings.debug:
            warnings.append({
                "field": "debug",
                "message": "DEBUG mode should be disabled in production",
                "severity": "high"
            })

        if "localhost" in settings.allowed_origins:
            warnings.append({
                "field": "allowed_origins",
                "message": "Localhost should not be in allowed_origins for production",
                "severity": "medium"
            })

        if settings.db_pool_size < 10:
            warnings.append({
                "field": "db_pool_size",
                "message": f"Database pool size ({settings.db_pool_size}) may be too small for production",
                "severity": "low"
            })

    # Check database configuration
    if settings.db_max_overflow < settings.db_pool_size:
        warnings.append({
            "field": "db_max_overflow",
            "message": f"max_overflow ({settings.db_max_overflow}) should be >= pool_size ({settings.db_pool_size})",
            "severity": "medium"
        })

    # Check cache configuration
    if settings.cache_ttl_default < 10:
        warnings.append({
            "field": "cache_ttl_default",
            "message": f"Very low cache TTL ({settings.cache_ttl_default}s) may cause high database load",
            "severity": "low"
        })

    status_code = status.HTTP_200_OK
    if errors:
        status_code = status.HTTP_500_INTERNAL_SERVER_ERROR

    return {
        "status": "healthy" if not errors else "unhealthy",
        "validation": {
            "errors": errors,
            "warnings": warnings,
            "warnings_count": len(warnings),
            "errors_count": len(errors)
        }
    }, status_code
```

**Example health check response:**

```json
{
  "status": "healthy",
  "configuration": {
    "app_name": "AI Agent MCP Server",
    "environment": "production",
    "debug": false,
    "log_level": "INFO",
    "host": "0.0.0.0",
    "port": 8000,
    "workers": 4,
    "database_pool_size": 20,
    "database_max_overflow": 40,
    "database_pool_recycle": 3600,
    "database_pre_ping": true,
    "cache_ttl_default": 300,
    "redis_max_connections": 20,
    "allowed_origins": ["https://example.com"],
    "api_key_header": "X-API-Key",
    "external_api_timeout": 30
  }
}
```

**Troubleshooting common configuration issues:**

```bash
# Issue 1: Configuration not loading from .env file
# Symptom: Application uses default values instead of .env values
# Solution: Check .env file location and SettingsConfigDict

# Verify .env file exists in correct location
ls -la .env

# Check .env file is readable
cat .env

# Ensure SettingsConfigDict points to correct file
# File: src/core/config.py
model_config = SettingsConfigDict(
    env_file=".env",  # Must be relative to working directory
    env_file_encoding="utf-8"
)

# Issue 2: Pydantic validation errors on startup
# Symptom: Application exits with "ValidationError" during Settings() initialization
# Solution: Check environment variable types and constraints

# Example error:
# pydantic_core._pydantic_core.ValidationError: 1 validation error for Settings
# database_url
#   Invalid URL format (type=value_error.url)

# Fix: Ensure DATABASE_URL follows correct format
DATABASE_URL=postgresql+asyncpg://user:password@host:5432/dbname

# Issue 3: Configuration changes not taking effect
# Symptom: Changed .env values but application still uses old values
# Solution: Restart application (lru_cache prevents reloading without restart)

# Clear cache if needed (development only)
from src.core.config import get_settings
get_settings.cache_clear()  # Clear lru_cache
settings = get_settings()   # Reload from .env

# Issue 4: Environment variables not overriding .env file
# Symptom: Set DATABASE_URL in shell but .env value used instead
# Solution: Environment variables take precedence over .env (verify setting is correct)

# Check environment variable is set
echo $DATABASE_URL

# Ensure no extra quotes or spaces
export DATABASE_URL="postgresql+asyncpg://user:pass@host:5432/db"  # Correct
export DATABASE_URL= "postgresql+asyncpg://..."  # Incorrect (space before value)
```


### 1.2.4 Type Safety Patterns with Pydantic Settings

Type safety in configuration management prevents runtime errors by catching type mismatches at application startup. Pydantic Settings provides comprehensive type validation with minimal boilerplate, leveraging Python's type hint system[^32].

**Core Type Safety Features:**
- **Automatic Type Coercion:** Environment variable strings converted to target types (int, bool, list, etc.)
- **Type Hint Validation:** All field types validated against declared type hints
- **Custom Validators:** Complex validation logic with `@field_validator` decorator
- **Generic Types:** Support for `list[str]`, `dict[str, int]`, `Optional[T]` patterns
- **Strict Mode:** Reject invalid type coercions when strictness required

#### Pattern 1: Advanced Type Annotations for Complex Configuration

```python
# File: src/core/config.py
from functools import lru_cache
from pydantic import Field, field_validator, model_validator, PostgresDsn, RedisDsn
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Literal, Annotated, TypedDict
from pathlib import Path
import structlog

logger = structlog.get_logger(__name__)

class DatabaseConfig(TypedDict):
    """Typed dictionary for database connection parameters."""
    pool_size: int
    max_overflow: int
    pool_recycle: int
    pool_pre_ping: bool
    pool_timeout: int

class CacheConfig(TypedDict):
    """Typed dictionary for cache configuration."""
    default_ttl: int
    max_connections: int
    socket_timeout: int
    socket_connect_timeout: int

class Settings(BaseSettings):
    """
    Type-safe application configuration with advanced validation.

    Uses Pydantic's type system to enforce type constraints at
    configuration load time, preventing runtime type errors.
    """

    # Application metadata with literal types for enums
    app_name: str = Field(default="AI Agent MCP Server", min_length=1, max_length=100)
    environment: Literal["development", "staging", "production"] = Field(
        default="development",
        description="Deployment environment (controls debug mode, logging level)"
    )

    # Integer fields with range constraints
    port: Annotated[int, Field(ge=1024, le=65535)] = 8000
    workers: Annotated[int, Field(ge=1, le=32, description="Number of Uvicorn workers")] = 4

    # String fields with regex patterns
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"

    # URL fields with automatic validation
    database_url: PostgresDsn = Field(
        description="Async PostgreSQL connection string (postgresql+asyncpg://...)"
    )
    redis_url: RedisDsn = Field(description="Redis connection string (redis://...)")

    # Complex structured types
    allowed_origins: list[str] = Field(
        default=["http://localhost:3000"],
        description="CORS allowed origins (comma-separated in env var)"
    )

    feature_flags: dict[str, bool] = Field(
        default_factory=dict,
        description="Feature toggle flags (JSON dict in env var)"
    )

    # Optional fields with None default
    external_api_url: str | None = Field(
        default=None,
        description="External API base URL (optional)"
    )

    # Path fields with automatic validation
    upload_dir: Path = Field(
        default=Path("/tmp/uploads"),
        description="Upload directory for file storage"
    )

    # Sensitive fields (marked for exclusion from logs)
    secret_key: str = Field(
        min_length=32,
        max_length=128,
        description="JWT signing key (generate with secrets.token_urlsafe(32))"
    )

    api_keys: list[str] = Field(
        default_factory=list,
        description="Valid API keys for authentication (comma-separated)"
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="forbid",                    # Reject unknown environment variables
        validate_default=True,             # Validate default values
        str_strip_whitespace=True,         # Strip whitespace from string values
        json_loads=lambda v: v,            # Custom JSON loader if needed
    )

    @field_validator("database_url")
    @classmethod
    def validate_async_database_url(cls, v: PostgresDsn) -> PostgresDsn:
        """
        Enforce async driver for database URL.

        Common mistake: Using sync driver (psycopg2) with async FastAPI.
        This validator ensures only async drivers are used.
        """
        if v.scheme not in ["postgresql+asyncpg", "postgres+asyncpg"]:
            raise ValueError(
                f"Database URL must use async driver (postgresql+asyncpg), got: {v.scheme}. "
                f"Install with: pip install asyncpg"
            )
        return v

    @field_validator("redis_url")
    @classmethod
    def validate_redis_url_scheme(cls, v: RedisDsn) -> RedisDsn:
        """Ensure Redis URL uses correct scheme."""
        if v.scheme not in ["redis", "rediss"]:  # rediss = Redis with TLS
            raise ValueError(
                f"Redis URL must use redis:// or rediss:// scheme, got: {v.scheme}"
            )
        return v

    @field_validator("upload_dir")
    @classmethod
    def validate_upload_dir_exists(cls, v: Path) -> Path:
        """
        Ensure upload directory exists and is writable.

        Creates directory if missing, validates write permissions.
        """
        if not v.exists():
            try:
                v.mkdir(parents=True, exist_ok=True)
                logger.info("upload_directory_created", path=str(v))
            except PermissionError:
                raise ValueError(
                    f"Upload directory {v} does not exist and cannot be created. "
                    f"Check file system permissions."
                )

        if not v.is_dir():
            raise ValueError(f"Upload path {v} exists but is not a directory")

        # Test write permission
        test_file = v / ".write_test"
        try:
            test_file.touch(exist_ok=True)
            test_file.unlink()
        except PermissionError:
            raise ValueError(f"Upload directory {v} is not writable")

        return v

    @field_validator("allowed_origins")
    @classmethod
    def validate_cors_origins(cls, v: list[str]) -> list[str]:
        """
        Validate CORS origins are valid URLs or wildcard.

        Prevents common misconfigurations that expose application to
        unauthorized cross-origin requests.
        """
        if not v:
            raise ValueError("At least one CORS origin must be specified")

        for origin in v:
            if origin == "*":
                logger.warning(
                    "wildcard_cors_origin_detected",
                    message="Using '*' for CORS allows all origins (security risk in production)"
                )
                continue

            if not origin.startswith(("http://", "https://")):
                raise ValueError(
                    f"CORS origin must start with http:// or https://, got: {origin}"
                )

        return v

    @field_validator("secret_key")
    @classmethod
    def validate_secret_key_strength(cls, v: str) -> str:
        """
        Validate secret key meets security requirements.

        Rejects common weak keys that appear in documentation or examples.
        Production keys must be cryptographically random.
        """
        # Check for common weak patterns
        weak_patterns = [
            "changeme", "secret", "password", "example", "test", "demo",
            "12345", "abcde", "qwerty", "admin"
        ]

        v_lower = v.lower()
        for pattern in weak_patterns:
            if pattern in v_lower:
                raise ValueError(
                    f"Secret key contains weak pattern '{pattern}'. "
                    f"Generate strong key with: python -c 'import secrets; print(secrets.token_urlsafe(32))'"
                )

        # Check for repeated characters (weak randomness)
        if len(set(v)) < len(v) / 2:
            raise ValueError(
                "Secret key has low entropy (too many repeated characters). "
                "Use cryptographically random generator."
            )

        return v

    @model_validator(mode="after")
    def validate_production_settings(self) -> "Settings":
        """
        Cross-field validation for production environment.

        Enforces security best practices when environment=production.
        Uses model_validator to access multiple fields.
        """
        if self.environment != "production":
            return self

        # Production-specific validations
        errors = []

        if self.debug:
            errors.append("DEBUG mode must be disabled in production")

        if "localhost" in self.allowed_origins or "*" in self.allowed_origins:
            errors.append(
                "CORS origins must not include 'localhost' or '*' in production"
            )

        if self.workers < 2:
            logger.warning(
                "production_worker_count_low",
                workers=self.workers,
                recommendation="Use at least 2 workers for high availability"
            )

        if not self.api_keys:
            logger.warning(
                "production_api_keys_missing",
                message="No API keys configured (authentication disabled)"
            )

        if errors:
            raise ValueError(
                f"Production configuration validation failed: {'; '.join(errors)}"
            )

        return self

    # Computed properties for structured config groups
    def get_database_config(self) -> DatabaseConfig:
        """
        Return database configuration as typed dictionary.

        Useful for passing to database engine initialization.
        """
        return DatabaseConfig(
            pool_size=10,
            max_overflow=20,
            pool_recycle=3600,
            pool_pre_ping=True,
            pool_timeout=30
        )

    def get_cache_config(self) -> CacheConfig:
        """Return cache configuration as typed dictionary."""
        return CacheConfig(
            default_ttl=300,
            max_connections=20,
            socket_timeout=5,
            socket_connect_timeout=10
        )

    def is_production(self) -> bool:
        """Type-safe production environment check."""
        return self.environment == "production"

    def model_dump_safe(self) -> dict[str, any]:
        """
        Dump configuration with sensitive fields masked.

        Use for logging or health check endpoints to prevent secret leakage.
        """
        data = self.model_dump()

        # Mask sensitive fields
        sensitive_fields = ["secret_key", "api_keys", "database_url", "redis_url"]
        for field in sensitive_fields:
            if field in data and data[field]:
                if isinstance(data[field], str):
                    data[field] = "***REDACTED***"
                elif isinstance(data[field], list):
                    data[field] = ["***REDACTED***"] * len(data[field])

        return data

@lru_cache
def get_settings() -> Settings:
    """
    Cached settings singleton.

    Returns same Settings instance for application lifetime.
    Cache cleared only on application restart.
    """
    return Settings()
```

**✅ Benefits:**
- **Type Safety:** All configuration fields validated against type hints at load time
- **IDE Support:** Full autocomplete and type checking in IDEs (PyCharm, VS Code)
- **Early Failure:** Invalid configuration detected at startup, not during request handling
- **Documentation:** Type hints serve as inline documentation for configuration schema
- **Structured Config:** TypedDict enables grouped configuration with type safety

**❌ Drawbacks:**
- **Learning Curve:** Requires understanding of Python type hints and Pydantic validators
- **Validation Overhead:** Field validators add ~50-100ms to startup time (negligible)
- **Rigid Schema:** Extra fields rejected by default (can disable with `extra="allow"`)

**Use When:**
- Building production microservices (always)
- Configuration has >10 fields (complexity benefits from type safety)
- Multiple developers working on codebase (type hints prevent misconfiguration)
- Configuration mistakes would cause runtime errors (database URLs, API endpoints)

#### Pattern 2: Environment-Specific Type Coercion

Different environments often require different configuration value formats. Pydantic Settings handles automatic type coercion from environment variables[^33].

```python
# File: src/core/config.py
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings
import json

class Settings(BaseSettings):
    """Configuration with automatic type coercion from environment variables."""

    # Boolean coercion (handles: "true", "1", "yes", "on", "True")
    debug: bool = Field(default=False)
    enable_metrics: bool = Field(default=True)

    # Integer coercion from string env vars
    port: int = Field(default=8000)
    max_connections: int = Field(default=100)

    # Float coercion
    timeout_seconds: float = Field(default=30.0)
    cache_ttl_hours: float = Field(default=1.5)

    # List coercion (comma-separated strings)
    allowed_origins: list[str] = Field(
        default_factory=list,
        description="Comma-separated: http://localhost:3000,https://example.com"
    )

    # Dict coercion (JSON strings)
    feature_flags: dict[str, bool] = Field(
        default_factory=dict,
        description='JSON dict: {"new_ui": true, "beta_api": false}'
    )

    # Set coercion (unique values only)
    supported_languages: set[str] = Field(
        default={"en", "es", "fr"},
        description="Comma-separated, deduplicated automatically"
    )

    # Tuple coercion (fixed-length sequences)
    api_version: tuple[int, int, int] = Field(
        default=(1, 0, 0),
        description="Comma-separated: 1,0,0"
    )

    @field_validator("allowed_origins", mode="before")
    @classmethod
    def split_comma_separated(cls, v):
        """
        Parse comma-separated environment variable into list.

        Example env var:
            ALLOWED_ORIGINS="http://localhost:3000,https://example.com"

        Becomes:
            ["http://localhost:3000", "https://example.com"]
        """
        if isinstance(v, str):
            # Split on comma, strip whitespace, filter empty strings
            return [item.strip() for item in v.split(",") if item.strip()]
        return v

    @field_validator("feature_flags", mode="before")
    @classmethod
    def parse_json_dict(cls, v):
        """
        Parse JSON string environment variable into dictionary.

        Example env var:
            FEATURE_FLAGS='{"new_ui": true, "beta_api": false}'

        Becomes:
            {"new_ui": True, "beta_api": False}
        """
        if isinstance(v, str):
            try:
                return json.loads(v)
            except json.JSONDecodeError as e:
                raise ValueError(f"Invalid JSON for feature_flags: {e}")
        return v

    @field_validator("supported_languages", mode="before")
    @classmethod
    def parse_set(cls, v):
        """
        Parse comma-separated string into set (deduplicates automatically).

        Example env var:
            SUPPORTED_LANGUAGES="en,es,fr,en,es"  # Duplicates

        Becomes:
            {"en", "es", "fr"}  # Deduplicated
        """
        if isinstance(v, str):
            return set(item.strip() for item in v.split(",") if item.strip())
        return v

    @field_validator("api_version", mode="before")
    @classmethod
    def parse_version_tuple(cls, v):
        """
        Parse semantic version string into tuple.

        Example env var:
            API_VERSION="1.2.3"

        Becomes:
            (1, 2, 3)
        """
        if isinstance(v, str):
            try:
                parts = v.split(".")
                if len(parts) != 3:
                    raise ValueError("API version must have exactly 3 parts (major.minor.patch)")
                return tuple(int(part) for part in parts)
            except ValueError as e:
                raise ValueError(f"Invalid API version format: {e}")
        return v
```

**Example .env file:**

```bash
# Boolean values (flexible formats)
DEBUG=true                    # Parsed as: True
ENABLE_METRICS=1              # Parsed as: True

# Numeric values
PORT=8000                     # Parsed as: int 8000
MAX_CONNECTIONS=100           # Parsed as: int 100
TIMEOUT_SECONDS=30.5          # Parsed as: float 30.5

# List values (comma-separated)
ALLOWED_ORIGINS=http://localhost:3000,https://example.com,https://app.example.com

# Dict values (JSON)
FEATURE_FLAGS={"new_ui": true, "beta_api": false, "experimental_cache": true}

# Set values (deduplicated)
SUPPORTED_LANGUAGES=en,es,fr,de,en,es  # Becomes: {"en", "es", "fr", "de"}

# Tuple values (fixed-length)
API_VERSION=1.2.3             # Parsed as: (1, 2, 3)
```

**✅ Benefits:**
- **Flexible Input:** Accepts multiple formats for boolean values ("true", "1", "yes")
- **Automatic Parsing:** No manual `str.split()` or `json.loads()` in application code
- **Type Safety:** Invalid formats caught at startup with clear error messages
- **Environment Friendly:** Works with container orchestrators (Kubernetes, Docker Compose)

**❌ Drawbacks:**
- **Hidden Complexity:** Type coercion rules not obvious from reading code
- **Validation Errors:** Complex formats can produce cryptic Pydantic errors
- **Performance:** Parsing overhead during startup (~10-50ms depending on complexity)

**Use When:**
- Configuration uses complex types (lists, dicts, sets)
- Deploying to environments with string-only env vars (most container platforms)
- Multiple configuration formats need support (development vs. production)

### 1.2.5 Validation Patterns for Configuration Security

Configuration validation prevents security vulnerabilities by enforcing constraints on sensitive fields. Pydantic's validator system provides declarative validation with custom error messages[^34].

#### Pattern 1: Multi-Layer Validation Strategy

```python
# File: src/core/config.py
from pydantic import Field, field_validator, model_validator
from pydantic_settings import BaseSettings
import re
from urllib.parse import urlparse
import structlog

logger = structlog.get_logger(__name__)

class Settings(BaseSettings):
    """Configuration with multi-layer security validation."""

    # Layer 1: Type and Format Validation (automatic)
    database_url: str = Field(
        min_length=10,
        pattern=r"^postgresql\+asyncpg://.*",
        description="Must be async PostgreSQL connection string"
    )

    # Layer 2: Field-Level Validation (custom logic)
    secret_key: str = Field(min_length=32, max_length=128)

    api_rate_limit: int = Field(default=100, ge=1, le=10000)

    admin_emails: list[str] = Field(default_factory=list)

    jwt_expiry_hours: int = Field(default=24, ge=1, le=720)  # Max 30 days

    allowed_origins: list[str] = Field(default_factory=list)

    # Layer 3: Cross-Field Validation (model-level)
    environment: str = Field(default="development")
    debug: bool = Field(default=False)

    @field_validator("database_url")
    @classmethod
    def validate_database_security(cls, v: str) -> str:
        """
        Validate database URL security configuration.

        Checks:
        1. Uses SSL/TLS for production databases
        2. No hardcoded credentials in URL
        3. Hostname is not localhost in production
        """
        parsed = urlparse(v)

        # Check for SSL requirement (production databases)
        if "sslmode" not in v:
            logger.warning(
                "database_ssl_not_configured",
                message="Database URL does not specify sslmode parameter. "
                        "Production databases should use sslmode=require or sslmode=verify-full"
            )

        # Warn about hardcoded credentials (should use secrets management)
        if parsed.password:
            logger.warning(
                "database_password_in_url",
                message="Database password hardcoded in URL. "
                        "Consider using environment variable interpolation or secrets management."
            )

        # Check hostname (production shouldn't use localhost)
        if parsed.hostname in ["localhost", "127.0.0.1"] and "prod" in v.lower():
            raise ValueError(
                "Production database URL should not use localhost. "
                "Use actual database hostname."
            )

        return v

    @field_validator("secret_key")
    @classmethod
    def validate_secret_key_complexity(cls, v: str) -> str:
        """
        Enforce secret key complexity requirements.

        Requirements:
        - Minimum 32 characters
        - Mix of uppercase, lowercase, digits, special characters
        - No repeated sequences
        - Not a common weak key
        """
        # Check minimum length (Field already enforces this, but explicit check)
        if len(v) < 32:
            raise ValueError("Secret key must be at least 32 characters")

        # Check character diversity
        has_upper = any(c.isupper() for c in v)
        has_lower = any(c.islower() for c in v)
        has_digit = any(c.isdigit() for c in v)
        has_special = any(not c.isalnum() for c in v)

        char_types = sum([has_upper, has_lower, has_digit, has_special])
        if char_types < 3:
            raise ValueError(
                "Secret key must contain at least 3 of: uppercase, lowercase, digits, special characters. "
                "Generate with: python -c 'import secrets; print(secrets.token_urlsafe(32))'"
            )

        # Check for repeated sequences (weak randomness indicator)
        for i in range(len(v) - 3):
            sequence = v[i:i+4]
            if v.count(sequence) > 1:
                raise ValueError(
                    f"Secret key contains repeated sequence '{sequence}'. "
                    "Use cryptographically random generator."
                )

        # Blacklist common weak keys
        weak_keys_sha256 = [
            # Common examples from documentation
            "changeme", "secret", "supersecret", "secretkey",
            # Common patterns
            "12345678901234567890123456789012",
            "abcdefghijklmnopqrstuvwxyz012345",
        ]

        for weak_key in weak_keys_sha256:
            if weak_key in v.lower():
                raise ValueError(
                    f"Secret key matches known weak pattern. Generate secure key with: "
                    f"python -c 'import secrets; print(secrets.token_urlsafe(32))'"
                )

        return v

    @field_validator("api_rate_limit")
    @classmethod
    def validate_rate_limit_reasonable(cls, v: int) -> int:
        """
        Validate API rate limit is reasonable for production use.

        Warn if rate limit is too low (impacts usability) or too high (DDoS risk).
        """
        if v < 10:
            logger.warning(
                "rate_limit_very_low",
                rate_limit=v,
                message="Rate limit <10 req/min may impact user experience"
            )
        elif v > 1000:
            logger.warning(
                "rate_limit_very_high",
                rate_limit=v,
                message="Rate limit >1000 req/min may not prevent abuse effectively"
            )

        return v

    @field_validator("admin_emails")
    @classmethod
    def validate_admin_emails(cls, v: list[str]) -> list[str]:
        """
        Validate admin email addresses are properly formatted.

        Ensures email format correctness and warns about suspicious patterns.
        """
        if not v:
            logger.warning(
                "no_admin_emails_configured",
                message="No admin emails configured for notifications"
            )
            return v

        email_regex = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")

        validated_emails = []
        for email in v:
            email = email.strip().lower()

            if not email_regex.match(email):
                raise ValueError(f"Invalid email format: {email}")

            # Warn about disposable email domains
            disposable_domains = ["tempmail.com", "throwaway.email", "guerrillamail.com"]
            domain = email.split("@")[1]
            if domain in disposable_domains:
                logger.warning(
                    "disposable_email_detected",
                    email=email,
                    message="Admin email uses disposable domain (not recommended)"
                )

            validated_emails.append(email)

        return validated_emails

    @field_validator("jwt_expiry_hours")
    @classmethod
    def validate_jwt_expiry(cls, v: int) -> int:
        """
        Validate JWT expiry time is secure.

        Short expiry (< 1 hour) improves security but impacts UX.
        Long expiry (> 7 days) convenient but increases token theft risk.
        """
        if v < 1:
            raise ValueError("JWT expiry must be at least 1 hour")

        if v > 168:  # 7 days
            logger.warning(
                "jwt_expiry_long",
                expiry_hours=v,
                message="JWT expiry >7 days increases risk if token stolen. "
                        "Consider shorter expiry with refresh tokens."
            )

        return v

    @field_validator("allowed_origins")
    @classmethod
    def validate_cors_origins_security(cls, v: list[str]) -> list[str]:
        """
        Validate CORS origins follow security best practices.

        Checks:
        1. No wildcard "*" in production
        2. All origins use HTTPS (except localhost)
        3. No IP addresses (use DNS names)
        """
        if not v:
            raise ValueError("At least one CORS origin must be specified")

        for origin in v:
            # Check for wildcard
            if origin == "*":
                logger.warning(
                    "cors_wildcard_detected",
                    message="CORS wildcard '*' allows all origins (security risk)"
                )
                continue

            # Parse origin URL
            parsed = urlparse(origin)

            # Enforce HTTPS (except localhost for development)
            if parsed.scheme != "https":
                if parsed.hostname not in ["localhost", "127.0.0.1"]:
                    raise ValueError(
                        f"CORS origin must use HTTPS, got {origin}. "
                        "HTTP allowed only for localhost in development."
                    )

            # Warn about IP addresses (should use DNS names)
            if parsed.hostname and re.match(r"^\d+\.\d+\.\d+\.\d+$", parsed.hostname):
                logger.warning(
                    "cors_origin_ip_address",
                    origin=origin,
                    message="CORS origin uses IP address instead of DNS name (not recommended)"
                )

        return v

    @model_validator(mode="after")
    def validate_environment_consistency(self) -> "Settings":
        """
        Cross-field validation for environment-specific requirements.

        Enforces security policies based on environment (development vs. production).
        Uses model_validator to access multiple fields simultaneously.
        """
        environment = self.environment.lower()

        if environment == "production":
            # Production-specific validations
            errors = []
            warnings = []

            # Debug mode must be disabled
            if self.debug:
                errors.append("Debug mode must be disabled in production")

            # CORS must not allow all origins
            if "*" in self.allowed_origins:
                errors.append("CORS wildcard '*' not allowed in production")

            # Rate limiting must be reasonable
            if self.api_rate_limit > 5000:
                warnings.append(f"High rate limit ({self.api_rate_limit}) may not prevent abuse")

            # JWT expiry should be secure
            if self.jwt_expiry_hours > 168:
                warnings.append(f"Long JWT expiry ({self.jwt_expiry_hours}h) increases security risk")

            # Log warnings
            for warning in warnings:
                logger.warning("production_configuration_warning", message=warning)

            # Raise errors
            if errors:
                raise ValueError(
                    f"Production configuration validation failed:\n" +
                    "\n".join(f"  - {error}" for error in errors)
                )

        elif environment == "development":
            # Development-specific warnings (less strict)
            if not self.debug:
                logger.info(
                    "development_debug_disabled",
                    message="Debug mode disabled in development (unusual)"
                )

            if "https://" in str(self.allowed_origins):
                logger.info(
                    "development_https_cors",
                    message="HTTPS CORS origin in development (may cause issues with localhost)"
                )

        return self
```

**✅ Benefits:**
- **Defense in Depth:** Multiple validation layers catch different types of errors
- **Security by Default:** Enforces security best practices automatically
- **Clear Error Messages:** Validation errors include context and remediation guidance
- **Audit Trail:** Warnings logged for security team review

**❌ Drawbacks:**
- **Startup Overhead:** Complex validators add 100-200ms to startup time
- **Strict Defaults:** May require adjusting validators for edge cases
- **Maintenance:** Validators need updates as security requirements evolve

**Use When:**
- Handling sensitive data (PII, financial, healthcare)
- Production deployments with compliance requirements (SOC 2, HIPAA, PCI-DSS)
- Multi-tenant applications (prevent cross-tenant configuration errors)
- Public-facing APIs (strict input validation required)

### 1.2.6 Configuration Validation Best Practices

**Best Practice 1: Fail Fast on Invalid Configuration**

```python
# File: src/main.py
from contextlib import asynccontextmanager
from fastapi import FastAPI
from src.core.config import get_settings
import structlog
import sys

logger = structlog.get_logger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan with fail-fast configuration validation.

    Validates all configuration at startup before initializing any services.
    Exits immediately if configuration invalid (prevents partial initialization).
    """
    # Step 1: Validate configuration (FIRST - before any service initialization)
    try:
        settings = get_settings()
        logger.info(
            "configuration_validated",
            app_name=settings.app_name,
            environment=settings.environment,
            validation_passed=True
        )
    except Exception as e:
        logger.error(
            "configuration_validation_failed",
            error=str(e),
            error_type=type(e).__name__
        )
        # Exit immediately - don't start application with invalid config
        sys.exit(1)

    # Step 2: Test critical external connections (database, cache, etc.)
    try:
        # Test database connection
        from src.infrastructure.database.engine import test_connection
        await test_connection(settings.database_url)
        logger.info("database_connection_verified")

        # Test Redis connection
        from src.infrastructure.cache.client import test_redis_connection
        await test_redis_connection(settings.redis_url)
        logger.info("redis_connection_verified")

    except Exception as e:
        logger.error(
            "external_service_connection_failed",
            error=str(e),
            error_type=type(e).__name__
        )
        sys.exit(1)

    # Application startup complete
    logger.info("application_startup_complete")

    yield

    # Cleanup on shutdown
    logger.info("application_shutdown_initiated")

app = FastAPI(lifespan=lifespan)
```

**Best Practice 2: Provide Configuration Health Endpoint**

```python
# File: src/api/routes/health.py
from fastapi import APIRouter, Depends
from src.core.config import Settings, get_settings
import structlog

router = APIRouter()
logger = structlog.get_logger(__name__)

@router.get("/health/config")
async def config_health(settings: Settings = Depends(get_settings)):
    """
    Configuration health check endpoint.

    Returns validated configuration (non-sensitive fields only)
    for deployment verification and troubleshooting.
    """
    return {
        "status": "healthy",
        "configuration": settings.model_dump_safe(),  # Sensitive fields masked
        "validation": {
            "all_validators_passed": True,
            "environment": settings.environment,
            "is_production": settings.is_production()
        }
    }

@router.get("/health/config/schema")
async def config_schema():
    """
    Return configuration schema for documentation.

    Useful for infrastructure teams to understand required env vars.
    """
    return {
        "schema": Settings.model_json_schema(),
        "required_fields": [
            field for field, info in Settings.model_fields.items()
            if info.is_required()
        ],
        "optional_fields": [
            field for field, info in Settings.model_fields.items()
            if not info.is_required()
        ]
    }
```

**Best Practice 3: Document Configuration in Code**

```python
# File: src/core/config.py
from pydantic import Field
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """
    Application configuration loaded from environment variables.

    Configuration Schema:
    ---------------------
    Core Application:
        - APP_NAME: Application name (default: "AI Agent MCP Server")
        - ENVIRONMENT: Deployment environment [development, staging, production]
        - DEBUG: Enable debug mode [true, false]
        - LOG_LEVEL: Logging level [DEBUG, INFO, WARNING, ERROR]

    Database:
        - DATABASE_URL: PostgreSQL connection string (async driver required)
          Format: postgresql+asyncpg://user:pass@host:5432/dbname
        - DB_POOL_SIZE: Connection pool size (default: 10, range: 5-50)
        - DB_MAX_OVERFLOW: Max overflow connections (default: 20)

    Cache:
        - REDIS_URL: Redis connection string
          Format: redis://host:6379/0 or rediss://host:6379/0 (TLS)
        - CACHE_TTL_DEFAULT: Default cache TTL in seconds (default: 300)

    Security:
        - SECRET_KEY: JWT signing key (min 32 chars, cryptographically random)
          Generate: python -c 'import secrets; print(secrets.token_urlsafe(32))'
        - ALLOWED_ORIGINS: CORS allowed origins (comma-separated)
          Example: https://app.example.com,https://admin.example.com

    Example .env file:
    ------------------
    # Core
    APP_NAME="AI Agent MCP Server"
    ENVIRONMENT=production
    DEBUG=false
    LOG_LEVEL=INFO

    # Database
    DATABASE_URL=postgresql+asyncpg://user:pass@db.example.com:5432/prod_db
    DB_POOL_SIZE=20
    DB_MAX_OVERFLOW=40

    # Cache
    REDIS_URL=rediss://redis.example.com:6379/0
    CACHE_TTL_DEFAULT=600

    # Security
    SECRET_KEY=A3xK9m2pR7wE5qT8nL4jH6sV1cZ0yB9fG2uD8oP5kN3
    ALLOWED_ORIGINS=https://app.example.com,https://admin.example.com
    """

    # Field definitions with inline documentation
    app_name: str = Field(
        default="AI Agent MCP Server",
        description="Application name (used in logs, metrics, health checks)",
        examples=["AI Agent MCP Server", "My FastAPI App"]
    )

    environment: str = Field(
        default="development",
        description="Deployment environment (controls security settings)",
        examples=["development", "staging", "production"]
    )

    # ... additional fields with comprehensive Field() documentation
```

**Use When:**
- Deploying to production (always validate configuration)
- Configuration has >5 fields (complexity benefits from health endpoint)
- Multiple developers or ops teams need configuration visibility
- Debugging configuration issues in deployed environments
### 1.3 Alternative Approaches

**Alternative 1: python-dotenv with Manual Parsing**

Uses `python-dotenv` to load variables into `os.environ`, then manually parse with `os.getenv()`. While simpler for small projects, this lacks type validation and requires extensive error handling[^8].

*Pros:* Minimal dependencies, explicit control
*Cons:* No type safety, manual validation, boilerplate code
*Use When:* Prototypes or scripts with <10 configuration values

**Alternative 2: dynaconf for Multi-Environment Management**

Dynaconf provides sophisticated environment layering (dev/staging/prod) with file-based overrides. Adds complexity beneficial only for applications with 5+ distinct deployment environments[^9].

*Pros:* Advanced environment switching, secrets management integration
*Cons:* Steeper learning curve, additional dependency
*Use When:* Enterprise apps with complex multi-tenant configurations

### 1.4 Decision Criteria

| Factor | Pydantic BaseSettings | python-dotenv | dynaconf |
|--------|----------------------|---------------|----------|
| Type Safety | ✅ Built-in | ❌ Manual | ✅ Supported |
| Validation | ✅ Automatic | ❌ Manual | ✅ Automatic |
| FastAPI Integration | ✅ Native | ⚠️ Manual | ⚠️ Manual |
| Multi-Environment | ⚠️ Basic | ❌ Manual | ✅ Advanced |
| Learning Curve | Low | Very Low | Medium |
| **Recommended For** | **Most FastAPI apps** | Prototypes | Enterprise |

**Decision Rule:** Use Pydantic BaseSettings unless you have 5+ deployment environments requiring complex layering, in which case evaluate dynaconf.

---

## 2. Structured Logging

### 2.1 Recommended Approach: structlog with JSON Rendering

structlog provides structured, context-rich logging with JSON output for production environments and human-readable output for development[^4]. Integration with FastAPI middleware enables automatic request correlation tracking.

**Core Benefits:**
- **Machine-Parsable Output:** JSON logs integrate seamlessly with ELK, CloudWatch, or Datadog
- **Context Binding:** Attach request IDs, user IDs, or tenant IDs to all log entries within request scope
- **Performance:** Async-safe with minimal overhead (<1ms per log call)
- **Developer Experience:** Pretty-printed console logs in development

### 2.2 Implementation Example

```python
# File: src/core/logging.py
import structlog
from typing import Any
import logging.config

def configure_logging(environment: str = "development") -> None:
    """
    Configure structlog for structured JSON logging.

    In development: Pretty console output with colors
    In production: JSON lines for log aggregation systems
    """
    shared_processors = [
        structlog.contextvars.merge_contextvars,  # Merge context vars
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
    ]

    if environment == "production":
        processors = shared_processors + [
            structlog.processors.format_exc_info,
            structlog.processors.JSONRenderer()  # JSON output
        ]
    else:
        processors = shared_processors + [
            structlog.dev.ConsoleRenderer()  # Pretty console output
        ]

    structlog.configure(
        processors=processors,
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

# File: src/middleware/logging_middleware.py
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
import structlog
import uuid

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Attach request correlation ID to all logs within request scope."""

    async def dispatch(self, request: Request, call_next):
        # Generate unique request ID
        request_id = str(uuid.uuid4())

        # Bind to structlog context (available to all loggers in this request)
        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(
            request_id=request_id,
            method=request.method,
            path=request.url.path,
        )

        logger = structlog.get_logger()
        logger.info("request_started")

        response = await call_next(request)

        logger.info(
            "request_completed",
            status_code=response.status_code,
        )

        return response
```

### 2.2.1 Logging Initialization Patterns

Proper logging initialization is critical for consistent log formatting and context propagation. The `configure_logging()` function must be called **before any loggers are created** to ensure all log output uses the configured processors.

#### Pattern 1: Initialization in Application Lifespan (Recommended)

Call `configure_logging()` during FastAPI application startup, before any request handlers execute[^24].

```python
# File: src/main.py
from contextlib import asynccontextmanager
from fastapi import FastAPI
from src.core.config import get_settings
from src.core.logging import configure_logging
from src.middleware.logging_middleware import RequestLoggingMiddleware
import structlog

logger = structlog.get_logger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.

    Startup order is critical:
    1. Load configuration
    2. Configure logging (MUST be first - before any log calls)
    3. Initialize other resources (database, cache, HTTP clients)
    """
    settings = get_settings()

    # Step 1: Configure logging BEFORE any other initialization
    # This ensures all subsequent log calls use structured logging
    configure_logging(
        environment="production" if not settings.debug else "development"
    )

    logger.info(
        "application_startup",
        app_name=settings.app_name,
        debug=settings.debug,
        python_version=sys.version
    )

    # Step 2: Initialize database engine
    from src.infrastructure.database.engine import session_manager
    session_manager.init(
        database_url=str(settings.database_url),
        pool_size=settings.db_pool_size
    )
    logger.info("database_initialized")

    # Step 3: Initialize Redis cache
    from src.infrastructure.cache.redis_manager import redis_manager
    await redis_manager.connect(str(settings.redis_url))
    logger.info("cache_initialized")

    # Step 4: Initialize HTTP clients
    # app.state.http_client = ResilientHTTPClient(...)
    # logger.info("http_clients_initialized")

    logger.info("application_ready")

    yield  # Application runs here

    # Shutdown: Close resources in reverse order
    logger.info("application_shutdown_started")

    await redis_manager.disconnect()
    logger.info("cache_closed")

    await session_manager.close()
    logger.info("database_closed")

    logger.info("application_shutdown_complete")

def create_app() -> FastAPI:
    """Create and configure FastAPI application."""
    app = FastAPI(
        title="Microservice with Structured Logging",
        lifespan=lifespan
    )

    # Add logging middleware AFTER logging is configured
    # (middleware is registered but not executed until requests arrive)
    app.add_middleware(RequestLoggingMiddleware)

    # Register routes
    from src.api.routes import users, health
    app.include_router(health.router, tags=["Health"])
    app.include_router(users.router, prefix="/api/v1", tags=["Users"])

    return app

app = create_app()

if __name__ == "__main__":
    import uvicorn
    import sys

    settings = get_settings()

    # For uvicorn CLI, logging configured via lifespan
    # For programmatic run, configure here before uvicorn starts
    if not hasattr(sys, "_called_from_test"):
        configure_logging(
            environment="production" if not settings.debug else "development"
        )

    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level="info"
    )
```

**Key Points:**
- ✅ `configure_logging()` called **first** in lifespan startup
- ✅ All subsequent initialization logs use structured format
- ✅ Middleware added to app but not executed until requests arrive
- ✅ Shutdown logs captured before resources closed

**Benefits:**
- Single initialization point for entire application
- Consistent logging from application start to shutdown
- All resource initialization logged with structured format
- Proper log capture during startup failures

#### Pattern 2: Initialization in main.py Module Level (Alternative)

Configure logging at module level for immediate availability[^25].

```python
# File: src/main.py
from fastapi import FastAPI
from src.core.config import get_settings
from src.core.logging import configure_logging
import structlog

# Configure logging at module level (runs when module imported)
settings = get_settings()
configure_logging(
    environment="production" if not settings.debug else "development"
)

logger = structlog.get_logger(__name__)

# Logger now available for use throughout module
logger.info("module_loaded", module=__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    logger.info("application_startup")

    # Initialize resources...
    yield

    logger.info("application_shutdown")

app = FastAPI(lifespan=lifespan)
```

**Benefits:**
- ✅ Logging available immediately when module imported
- ✅ Simpler code flow (no nested initialization)

**Drawbacks:**
- ❌ Module-level side effects (runs on import)
- ❌ Harder to override for testing
- ❌ Configuration loaded before application starts

**Use When:** Simple applications without complex startup requirements

#### Pattern 3: Lazy Initialization with Singleton (Testing-Friendly)

Use singleton pattern with lazy initialization for better test isolation[^26].

```python
# File: src/core/logging.py
import structlog
from typing import Optional

_logging_configured: bool = False

def configure_logging(environment: str = "development", force: bool = False) -> None:
    """
    Configure structlog with idempotency protection.

    Args:
        environment: "development" or "production"
        force: Force reconfiguration even if already configured
    """
    global _logging_configured

    if _logging_configured and not force:
        return  # Already configured, skip

    shared_processors = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
    ]

    if environment == "production":
        processors = shared_processors + [
            structlog.processors.format_exc_info,
            structlog.processors.JSONRenderer()
        ]
    else:
        processors = shared_processors + [
            structlog.dev.ConsoleRenderer()
        ]

    structlog.configure(
        processors=processors,
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    _logging_configured = True

def reset_logging() -> None:
    """Reset logging configuration (for testing only)."""
    global _logging_configured
    _logging_configured = False
    structlog.reset_defaults()

# File: tests/conftest.py
import pytest
from src.core.logging import configure_logging, reset_logging

@pytest.fixture(autouse=True)
def configure_test_logging():
    """Configure logging for test environment."""
    # Reset any existing configuration
    reset_logging()

    # Configure for testing (development mode)
    configure_logging(environment="development", force=True)

    yield

    # Reset after test
    reset_logging()
```

**Benefits:**
- ✅ Idempotent (safe to call multiple times)
- ✅ Test isolation via reset function
- ✅ Explicit configuration control

**Use When:** Applications with complex test requirements

#### Pattern 4: Environment-Specific Configuration Files

Use separate configuration files for different environments.

```python
# File: src/core/logging_config.py
from typing import Dict, Any

LOGGING_CONFIGS: Dict[str, Dict[str, Any]] = {
    "development": {
        "processors": [
            "merge_contextvars",
            "add_log_level",
            "add_logger_name",
            "timestamp",
            "console_renderer"  # Pretty output
        ],
        "log_level": "DEBUG",
        "include_source": True
    },
    "production": {
        "processors": [
            "merge_contextvars",
            "add_log_level",
            "add_logger_name",
            "timestamp",
            "format_exc_info",
            "json_renderer"  # JSON output
        ],
        "log_level": "INFO",
        "include_source": False  # Reduce log size
    },
    "testing": {
        "processors": [
            "add_log_level",
            "console_renderer"  # No request ID in tests
        ],
        "log_level": "WARNING",  # Quieter tests
        "include_source": False
    }
}

# File: src/core/logging.py
import structlog
from src.core.logging_config import LOGGING_CONFIGS

def configure_logging(environment: str = "development") -> None:
    """Configure logging from environment-specific config."""
    config = LOGGING_CONFIGS.get(environment, LOGGING_CONFIGS["development"])

    processor_map = {
        "merge_contextvars": structlog.contextvars.merge_contextvars,
        "add_log_level": structlog.stdlib.add_log_level,
        "add_logger_name": structlog.stdlib.add_logger_name,
        "timestamp": structlog.processors.TimeStamper(fmt="iso"),
        "format_exc_info": structlog.processors.format_exc_info,
        "console_renderer": structlog.dev.ConsoleRenderer(),
        "json_renderer": structlog.processors.JSONRenderer()
    }

    processors = [
        processor_map[name] for name in config["processors"]
    ]

    structlog.configure(
        processors=processors,
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )
```

**Benefits:**
- ✅ Centralized configuration
- ✅ Easy to add new environments
- ✅ Configuration visible without reading code

**Use When:** Multiple deployment environments with distinct logging requirements

### 2.2.2 Common Initialization Mistakes

**❌ Mistake 1: Creating loggers before configuration**

```python
# BAD: Logger created before configure_logging() called
import structlog
logger = structlog.get_logger()  # Uses default configuration!

from src.core.logging import configure_logging
configure_logging()  # Too late - logger already created

logger.info("test")  # May not use configured processors
```

**✅ Fix: Configure first, then create loggers**

```python
# GOOD: Configure before creating any loggers
from src.core.logging import configure_logging
configure_logging()

import structlog
logger = structlog.get_logger()  # Now uses configured processors

logger.info("test")  # Properly formatted
```

**❌ Mistake 2: Configuring logging multiple times**

```python
# BAD: Multiple configuration calls can cause inconsistent behavior
configure_logging("development")
# ... some code ...
configure_logging("production")  # Overwrites previous config!
```

**✅ Fix: Configure once during startup**

```python
# GOOD: Single configuration call in lifespan
@asynccontextmanager
async def lifespan(app: FastAPI):
    configure_logging(settings.environment)  # Once, at startup
    yield
```

**❌ Mistake 3: Not configuring logging in tests**

```python
# BAD: Tests use default logging (hard to debug failures)
def test_user_creation():
    response = client.post("/users", json={"email": "test@example.com"})
    assert response.status_code == 201
    # No structured logs available if test fails
```

**✅ Fix: Configure logging in conftest.py**

```python
# GOOD: Configure logging for all tests
@pytest.fixture(autouse=True)
def setup_logging():
    configure_logging("testing")
```

### 2.2.3 Verification and Troubleshooting

**Verify logging configuration:**

```python
# File: src/api/routes/health.py
from fastapi import APIRouter
import structlog

router = APIRouter()

@router.get("/health/logging")
async def logging_health():
    """Verify structured logging configuration."""
    logger = structlog.get_logger()

    # Test log with context
    logger.info(
        "logging_health_check",
        processors_configured=True,
        test_context="verification"
    )

    return {
        "status": "healthy",
        "logging_configured": True,
        "processors": [
            p.__class__.__name__
            for p in structlog.get_config().get("processors", [])
        ]
    }
```

**Example health check response:**

```json
{
  "status": "healthy",
  "logging_configured": true,
  "processors": [
    "merge_contextvars",
    "add_log_level",
    "add_logger_name",
    "TimeStamper",
    "StackInfoRenderer",
    "JSONRenderer"
  ]
}
```

**Usage in application code:**

```python
# File: src/services/user_service.py
import structlog

logger = structlog.get_logger()

async def create_user(email: str) -> User:
    """Create new user with structured logging."""
    logger.info("creating_user", email=email)

    try:
        user = await user_repository.save(User(email=email))
        logger.info("user_created", user_id=user.id, email=email)
        return user
    except IntegrityError:
        logger.warning("user_creation_failed", email=email, reason="duplicate_email")
        raise
```

**Example JSON log output (production):**

```json
{
  "event": "user_created",
  "timestamp": "2025-11-01T14:23:45.123456Z",
  "level": "info",
  "logger": "src.services.user_service",
  "request_id": "a3f2c1d4-5e6f-7g8h-9i0j-1k2l3m4n5o6p",
  "method": "POST",
  "path": "/api/users",
  "user_id": 42,
  "email": "user@example.com"
}
```

### 2.3 Alternative Approaches

**Alternative 1: Python stdlib logging with JSON Formatter**

Use Python's built-in `logging` module with `python-json-logger` for JSON formatting. Lacks context binding and async safety of structlog[^10].

*Pros:* No external dependencies, familiar API
*Cons:* Manual context propagation, less flexible
*Use When:* Legacy codebases already using stdlib logging

**Alternative 2: loguru for Simplified API**

loguru provides intuitive API with automatic exception catching. Better for standalone applications than microservices due to limited structured logging support[^11].

*Pros:* Minimal configuration, beautiful backtraces
*Cons:* Not async-first, weaker structured logging
*Use When:* CLI tools or batch processing scripts

### 2.4 Decision Criteria

**Use structlog when:**
- Application has >3 microservices requiring correlation tracking
- Logs shipped to centralized aggregation (ELK, Splunk, Datadog)
- Need request-scoped context binding (user ID, tenant ID, trace ID)

**Use stdlib logging when:**
- Migrating legacy application with existing logging infrastructure
- Minimal external dependencies required (compliance/security constraints)

**Use loguru when:**
- Building CLI tools or standalone scripts
- Team unfamiliar with structured logging concepts

---

*(Continuing with remaining sections...)*

## 3. Caching Strategies

### 3.1 Recommended Approach: Redis with Cache-Aside Pattern

Redis with async client (redis-py 4.2+) using cache-aside (lazy loading) pattern provides optimal balance between performance, data freshness, and implementation simplicity for FastAPI applications[^5].

**Core Benefits:**
- **Async Native:** redis-py includes async support (aioredis merged into redis-py 4.2+)[^12]
- **Cache-Aside Simplicity:** Check cache first; on miss, load from database and populate cache
- **TTL Control:** Configure expiration per key to prevent stale data
- **Battle-Tested:** Used in production by Stripe, GitHub, and Shopify at massive scale

### 3.2 Implementation Example

```python
# File: src/infrastructure/cache/redis_cache.py
from redis.asyncio import Redis
from typing import Any, Optional
import json

class CacheService:
    """Async Redis cache service with JSON serialization."""

    def __init__(self, redis_client: Redis):
        self._redis = redis_client

    async def get(self, key: str) -> Optional[Any]:
        """Retrieve value from cache, return None if not found."""
        value = await self._redis.get(key)
        return json.loads(value) if value else None

    async def set(
        self,
        key: str,
        value: Any,
        ttl: int = 300  # 5 minutes default
    ) -> None:
        """Store value in cache with TTL."""
        await self._redis.set(
            key,
            json.dumps(value),
            ex=ttl  # Expiration in seconds
        )

    async def delete(self, key: str) -> None:
        """Remove key from cache."""
        await self._redis.delete(key)

    async def exists(self, key: str) -> bool:
        """Check if key exists in cache."""
        return await self._redis.exists(key) > 0

# File: src/api/dependencies/cache.py
from redis.asyncio import Redis, ConnectionPool
from src.core.config import Settings, get_settings
from fastapi import Depends

async def get_redis_client(
    settings: Settings = Depends(get_settings)
) -> Redis:
    """
    Create Redis client with connection pool.

    Connection pool reuses TCP connections across requests,
    reducing overhead from repeated connects/disconnects.
    """
    pool = ConnectionPool.from_url(
        str(settings.redis_url),
        max_connections=10,
        decode_responses=False  # Handle decoding manually
    )
    return Redis(connection_pool=pool)

async def get_cache_service(
    redis_client: Redis = Depends(get_redis_client)
) -> CacheService:
    """
    Provide CacheService with Redis client dependency.

    This dependency chain ensures:
    1. Settings loaded once (via @lru_cache)
    2. Redis connection pool created per request scope
    3. CacheService wraps Redis client with domain-specific operations
    """
    return CacheService(redis_client)
```

**Cache-aside pattern in repository:**

```python
# File: src/infrastructure/repositories/user_repository.py
from src.infrastructure.cache.redis_cache import CacheService

class UserRepository:
    """User repository with cache-aside pattern."""

    def __init__(
        self,
        db_session: AsyncSession,
        cache: CacheService
    ):
        self._session = db_session
        self._cache = cache

    async def get_by_id(self, user_id: int) -> Optional[User]:
        """Retrieve user with cache-aside pattern."""
        cache_key = f"user:{user_id}"

        # 1. Check cache first
        cached = await self._cache.get(cache_key)
        if cached:
            return User(**cached)  # Cache hit

        # 2. Cache miss: load from database
        result = await self._session.execute(
            select(UserModel).where(UserModel.id == user_id)
        )
        user_model = result.scalar_one_or_none()

        if user_model:
            user = user_model.to_domain()

            # 3. Populate cache for next request
            await self._cache.set(
                cache_key,
                user.dict(),
                ttl=300  # 5 minute TTL
            )

            return user

        return None
```

### 3.2.1 CacheService Initialization Patterns

FastAPI provides multiple approaches for initializing CacheService with proper lifecycle management. The choice depends on whether you need application-scoped (singleton) or request-scoped instances.

#### Pattern 1: Application Lifespan with Singleton Redis Client (Recommended)

This pattern creates a single Redis connection pool during application startup and closes it on shutdown, maximizing connection reuse and minimizing overhead[^15][^16].

```python
# File: src/main.py
from contextlib import asynccontextmanager
from fastapi import FastAPI
from redis.asyncio import Redis, ConnectionPool
import structlog

logger = structlog.get_logger()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager for resource initialization/cleanup.

    Startup (before yield):
    - Create Redis connection pool
    - Initialize other singletons (DB engine, HTTP clients)

    Shutdown (after yield):
    - Close Redis connections
    - Cleanup resources
    """
    settings = get_settings()

    # Startup: Create global Redis connection pool
    logger.info("initializing_redis_pool", url=str(settings.redis_url))

    redis_pool = ConnectionPool.from_url(
        str(settings.redis_url),
        max_connections=20,           # Max concurrent connections
        socket_connect_timeout=5,     # Connection timeout (seconds)
        socket_keepalive=True,        # Enable TCP keepalive
        health_check_interval=30,     # Health check every 30s
        decode_responses=False        # Manual decoding for flexibility
    )

    # Create Redis client from pool
    redis_client = Redis(connection_pool=redis_pool)

    # Store in app.state for access via dependencies
    app.state.redis_client = redis_client
    app.state.redis_pool = redis_pool

    # Test connection
    try:
        await redis_client.ping()
        logger.info("redis_connection_established")
    except Exception as e:
        logger.error("redis_connection_failed", error=str(e))
        raise

    yield  # Application runs here

    # Shutdown: Close Redis connections
    logger.info("closing_redis_connections")

    await redis_client.close()
    await redis_pool.disconnect()

    logger.info("redis_connections_closed")

# Create FastAPI app with lifespan
app = FastAPI(
    title="Microservice with Redis Caching",
    lifespan=lifespan
)

# File: src/api/dependencies/cache.py
from fastapi import Request
from src.infrastructure.cache.redis_cache import CacheService

def get_cache_service(request: Request) -> CacheService:
    """
    Retrieve CacheService from app.state (singleton pattern).

    Redis client initialized once during startup, reused across
    all requests. This is the most efficient pattern for production.
    """
    return CacheService(request.app.state.redis_client)
```

**Benefits:**
- ✅ Single connection pool for entire application lifecycle
- ✅ Maximum connection reuse, minimal overhead
- ✅ Proper cleanup on shutdown (no resource leaks)
- ✅ Health checks ensure connection stability

**Use When:** Production applications requiring optimal performance (default recommendation)

#### Pattern 2: Request-Scoped Redis Client (For Testing)

This pattern creates a new Redis client per request, useful for testing scenarios where you need isolation between tests[^17].

```python
# File: src/api/dependencies/cache.py
from redis.asyncio import Redis, ConnectionPool
from src.core.config import Settings, get_settings
from fastapi import Depends
from typing import AsyncGenerator

async def get_redis_client_per_request(
    settings: Settings = Depends(get_settings)
) -> AsyncGenerator[Redis, None]:
    """
    Create Redis client per request (for testing isolation).

    WARNING: Less efficient than singleton pattern due to repeated
    connection pool creation. Use only for testing or when explicitly
    needed for isolation.
    """
    pool = ConnectionPool.from_url(
        str(settings.redis_url),
        max_connections=5  # Smaller pool for request scope
    )
    redis_client = Redis(connection_pool=pool)

    yield redis_client  # Provide to request handler

    # Cleanup after request
    await redis_client.close()
    await pool.disconnect()

def get_cache_service_per_request(
    redis_client: Redis = Depends(get_redis_client_per_request)
) -> CacheService:
    """Provide CacheService with request-scoped Redis client."""
    return CacheService(redis_client)
```

**Benefits:**
- ✅ Isolation between requests/tests
- ✅ Automatic cleanup after each request
- ✅ Easy to override for testing

**Drawbacks:**
- ❌ Higher overhead (pool created per request)
- ❌ Not suitable for high-traffic production use

**Use When:** Integration testing requiring clean slate per test

#### Pattern 3: Hybrid Approach with Dependency Override

Combine singleton pattern for production with override capability for testing[^18].

```python
# File: src/api/dependencies/cache.py
from fastapi import Request

# Default: Use singleton from app.state
def get_redis_client(request: Request) -> Redis:
    """Get Redis client from application state (singleton)."""
    return request.app.state.redis_client

def get_cache_service(
    redis_client: Redis = Depends(get_redis_client)
) -> CacheService:
    """Provide CacheService (production: singleton, tests: overridable)."""
    return CacheService(redis_client)

# File: tests/conftest.py
import pytest
from fakeredis.aioredis import FakeRedis
from src.api.dependencies.cache import get_redis_client

@pytest.fixture
def fake_redis():
    """Provide fake Redis client for testing (no real Redis needed)."""
    return FakeRedis(decode_responses=False)

@pytest.fixture
def client(fake_redis):
    """Test client with overridden Redis dependency."""
    from src.main import app
    from fastapi.testclient import TestClient

    # Override Redis dependency with fake implementation
    app.dependency_overrides[get_redis_client] = lambda request: fake_redis

    with TestClient(app) as test_client:
        yield test_client

    # Cleanup
    app.dependency_overrides.clear()
```

**Benefits:**
- ✅ Production uses efficient singleton pattern
- ✅ Tests use fast in-memory fake Redis (no external dependency)
- ✅ Same code paths for production and testing

**Use When:** You want optimal performance in production while maintaining testability (best of both worlds)

### 3.2.2 Connection Pool Configuration Best Practices

Redis connection pool settings significantly impact performance and reliability[^19].

```python
from redis.asyncio import ConnectionPool

# Production-optimized configuration
pool = ConnectionPool.from_url(
    redis_url,
    # Connection limits
    max_connections=20,              # Max concurrent connections
    # Scale based on: (expected_concurrent_requests * 1.5)
    # Example: 100 RPS → 20 connections sufficient

    # Timeouts
    socket_connect_timeout=5,        # Connection establishment timeout (seconds)
    socket_timeout=2,                # Read/write operation timeout (seconds)
    socket_keepalive=True,           # Enable TCP keepalive
    socket_keepalive_options={       # Linux keepalive settings
        1: 60,                       # TCP_KEEPIDLE: 60s before first probe
        2: 10,                       # TCP_KEEPINTVL: 10s between probes
        3: 3                         # TCP_KEEPCNT: 3 probes before timeout
    },

    # Health checks
    health_check_interval=30,        # Health check every 30 seconds
    # Detects stale connections before use

    # Retry behavior
    retry_on_timeout=True,           # Retry operations on timeout

    # Encoding
    decode_responses=False,          # Manual decode for binary data support
    encoding="utf-8",                # Encoding for string operations

    # Client identification
    client_name="fastapi-microservice",  # Client identifier in Redis logs
)
```

**Configuration Guidelines:**

| Setting | Recommended Value | Rationale |
|---------|------------------|-----------|
| `max_connections` | `concurrent_requests * 1.5` | Handles request spikes without exhaustion |
| `socket_connect_timeout` | `5s` | Balance between retry speed and giving Redis time |
| `socket_timeout` | `2s` | Fast failure for read/write operations |
| `health_check_interval` | `30s` | Detects stale connections proactively |
| `socket_keepalive` | `True` | Prevents firewall/load balancer connection drops |
| `decode_responses` | `False` | Flexibility for binary data (images, msgpack) |

**Monitoring Connection Pool Health:**

```python
# File: src/api/routes/health.py
from fastapi import APIRouter, Request
from redis.asyncio import Redis

router = APIRouter()

@router.get("/health/redis")
async def redis_health(request: Request):
    """Redis health check endpoint."""
    redis_client: Redis = request.app.state.redis_client

    try:
        # Test connection with ping
        await redis_client.ping()

        # Get connection pool stats
        pool = redis_client.connection_pool
        pool_info = {
            "max_connections": pool.max_connections,
            "available_connections": len(pool._available_connections),
            "in_use_connections": len(pool._in_use_connections),
        }

        return {
            "status": "healthy",
            "pool_info": pool_info
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }
```

### 3.3 Alternative Approaches

**Alternative 1: In-Memory Cache with async-lru**

Use `async_lru` decorator for function-level memoization. Suitable only for single-instance deployments (cache not shared across replicas)[^13].

*Pros:* Zero infrastructure, sub-millisecond latency
*Cons:* Not shared across instances, data lost on restart
*Use When:* Development environment or single-instance deployment

**Alternative 2: Write-Through Cache**

Write to cache and database simultaneously. Ensures cache always fresh but adds latency to write operations[^14].

*Pros:* Cache always up-to-date, simpler read logic
*Cons:* Higher write latency, wasted cache writes for rarely-read data
*Use When:* Read-heavy workloads (>90% reads) with infrequent writes

### 3.4 Decision Criteria

| Pattern | Best For | Cache Freshness | Write Performance |
|---------|----------|----------------|-------------------|
| **Cache-Aside** | **General use** | ✅ Configurable TTL | ✅ Fast (no cache write) |
| Write-Through | Read-heavy (>90%) | ✅✅ Always fresh | ⚠️ Slower (dual write) |
| Write-Behind | High write volume | ⚠️ Eventually consistent | ✅✅ Fastest |
| In-Memory | Single instance | ✅ Instant | ✅ Instant |

**TTL Selection Guidelines:**
- **User profiles:** 300s (5 min) - infrequently changed
- **Product catalog:** 600s (10 min) - stable data
- **Real-time inventory:** 10s - frequently updated
- **Session data:** 1800s (30 min) - bound to session lifetime

---

## 4. Data Access Patterns

### 4.1 Recommended Approach: Async SQLAlchemy with Repository Pattern

The Repository pattern with async SQLAlchemy provides Clean Architecture compliance while leveraging Python's async capabilities for high-concurrency database access[^3][^20]. This pattern abstracts persistence details from domain logic, enabling database-agnostic business rules.

**Core Benefits:**
- **Dependency Inversion:** Domain layer depends on repository interface (port), not SQLAlchemy (adapter)
- **Testability:** Mock repositories in unit tests without database overhead
- **Performance:** Async operations prevent blocking event loop during I/O
- **Type Safety:** SQLAlchemy 2.0+ with type stubs provides full IDE support

### 4.2 Database Engine and Session Initialization

#### Pattern 1: Lifespan with Singleton Engine (Recommended)

Create a single async engine during application startup and manage per-request sessions via dependency injection[^21][^22].

```python
# File: src/infrastructure/database/engine.py
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine
)
from sqlalchemy.pool import NullPool
from src.core.config import Settings
import structlog

logger = structlog.get_logger()

class DatabaseSessionManager:
    """
    Manages database engine and session factory lifecycle.

    Singleton engine created at startup, sessions created per-request.
    """

    def __init__(self):
        self._engine: AsyncEngine | None = None
        self._session_factory: async_sessionmaker[AsyncSession] | None = None

    def init(self, database_url: str, **engine_kwargs):
        """
        Initialize async engine and session factory.

        Called during FastAPI lifespan startup.
        """
        logger.info("initializing_database_engine", url=database_url)

        self._engine = create_async_engine(
            database_url,
            # Connection pooling
            pool_size=10,              # Max persistent connections
            max_overflow=20,           # Max overflow connections
            pool_recycle=3600,         # Recycle connections after 1 hour
            pool_pre_ping=True,        # Verify connections before use

            # Query execution
            echo=False,                # Don't log SQL (use logging middleware instead)
            future=True,               # Enable SQLAlchemy 2.0 future mode

            **engine_kwargs
        )

        self._session_factory = async_sessionmaker(
            self._engine,
            class_=AsyncSession,
            expire_on_commit=False,   # CRITICAL: Prevent implicit I/O after commit
            autoflush=False,          # Manual flush for explicit control
            autocommit=False          # Manual commit for transaction control
        )

        logger.info("database_engine_initialized")

    async def close(self):
        """
        Close database engine and release connections.

        Called during FastAPI lifespan shutdown.
        """
        if self._engine is None:
            return

        logger.info("closing_database_engine")

        await self._engine.dispose()

        self._engine = None
        self._session_factory = None

        logger.info("database_engine_closed")

    async def get_session(self) -> AsyncSession:
        """
        Create new database session.

        Use via dependency injection (yields session per request).
        """
        if self._session_factory is None:
            raise RuntimeError(
                "DatabaseSessionManager not initialized. "
                "Call init() during application startup."
            )

        async with self._session_factory() as session:
            try:
                yield session
                await session.commit()  # Commit if no exceptions
            except Exception:
                await session.rollback()  # Rollback on error
                raise
            finally:
                await session.close()

# Global instance
session_manager = DatabaseSessionManager()

# File: src/main.py
from contextlib import asynccontextmanager
from fastapi import FastAPI
from src.infrastructure.database.engine import session_manager
from src.core.config import get_settings

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.

    Initializes database engine at startup, closes at shutdown.
    """
    settings = get_settings()

    # Startup: Initialize database engine
    session_manager.init(
        database_url=str(settings.database_url),
        pool_size=settings.db_pool_size,
        pool_recycle=settings.db_pool_recycle
    )

    # Optionally: Run migrations, seed data, etc.
    # await run_migrations()

    yield  # Application runs here

    # Shutdown: Close database engine
    await session_manager.close()

app = FastAPI(lifespan=lifespan)

# File: src/api/dependencies/database.py
from sqlalchemy.ext.asyncio import AsyncSession
from src.infrastructure.database.engine import session_manager

async def get_db_session() -> AsyncSession:
    """
    Dependency for database session.

    Creates new session per request, commits on success, rolls back on error.
    """
    async for session in session_manager.get_session():
        yield session
```

**Benefits:**
- ✅ Single engine for entire application (optimal connection pooling)
- ✅ Per-request sessions (transaction isolation)
- ✅ Automatic commit/rollback handling
- ✅ Proper cleanup on shutdown

**Use When:** Production applications (default recommendation)

#### Pattern 2: Direct Engine Per Request (Testing Only)

Create new engine and session per request for complete isolation[^23].

```python
# File: src/api/dependencies/database.py
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from src.core.config import get_settings
from typing import AsyncGenerator

async def get_db_session_isolated() -> AsyncGenerator[AsyncSession, None]:
    """
    Create isolated database session per request (testing only).

    WARNING: Creates new engine per request - extremely inefficient.
    Use only for integration tests requiring complete isolation.
    """
    settings = get_settings()

    # Create new engine per request
    engine = create_async_engine(str(settings.database_url))
    session_factory = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False
    )

    async with session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
            await engine.dispose()  # Clean up engine
```

**Drawbacks:**
- ❌ Extremely inefficient (new engine per request)
- ❌ No connection pooling benefits
- ❌ High latency (connection establishment overhead)

**Use When:** Integration tests with pytest fixtures requiring isolation

### 4.3 Repository Pattern Implementation

#### Repository Interface (Domain Layer)

```python
# File: src/domain/repositories/user_repository.py
from typing import Protocol, Optional, List
from src.domain.entities.user import User

class UserRepositoryPort(Protocol):
    """
    Repository interface (port) - defined in domain layer.

    Domain defines WHAT operations it needs, infrastructure defines HOW.
    This achieves Dependency Inversion Principle (DIP).
    """

    async def get_by_id(self, user_id: int) -> Optional[User]:
        """Retrieve user by ID."""
        ...

    async def get_by_email(self, email: str) -> Optional[User]:
        """Retrieve user by email address."""
        ...

    async def list_all(self, limit: int = 100, offset: int = 0) -> List[User]:
        """List users with pagination."""
        ...

    async def save(self, user: User) -> User:
        """Persist user (create or update)."""
        ...

    async def delete(self, user_id: int) -> None:
        """Remove user from persistence."""
        ...

    async def exists(self, user_id: int) -> bool:
        """Check if user exists."""
        ...
```

#### Repository Implementation (Infrastructure Layer)

```python
# File: src/infrastructure/repositories/sqlalchemy_user_repository.py
from sqlalchemy import select, exists
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List
from src.domain.repositories.user_repository import UserRepositoryPort
from src.domain.entities.user import User
from src.infrastructure.models.user_model import UserModel
import structlog

logger = structlog.get_logger()

class SQLAlchemyUserRepository:
    """
    SQLAlchemy implementation of UserRepositoryPort.

    Infrastructure layer - knows about SQLAlchemy, database tables.
    Can be replaced with MongoDB, DynamoDB, or in-memory implementation
    without changing domain logic.
    """

    def __init__(self, session: AsyncSession):
        self._session = session

    async def get_by_id(self, user_id: int) -> Optional[User]:
        """Retrieve user by ID with async query."""
        logger.debug("fetching_user_by_id", user_id=user_id)

        result = await self._session.execute(
            select(UserModel).where(UserModel.id == user_id)
        )
        user_model = result.scalar_one_or_none()

        if user_model:
            return user_model.to_domain()  # Map ORM → domain entity
        return None

    async def get_by_email(self, email: str) -> Optional[User]:
        """Retrieve user by email address."""
        logger.debug("fetching_user_by_email", email=email)

        result = await self._session.execute(
            select(UserModel).where(UserModel.email == email)
        )
        user_model = result.scalar_one_or_none()

        if user_model:
            return user_model.to_domain()
        return None

    async def list_all(self, limit: int = 100, offset: int = 0) -> List[User]:
        """List users with pagination."""
        logger.debug("listing_users", limit=limit, offset=offset)

        result = await self._session.execute(
            select(UserModel).limit(limit).offset(offset)
        )
        user_models = result.scalars().all()

        return [model.to_domain() for model in user_models]

    async def save(self, user: User) -> User:
        """Persist user entity to database."""
        logger.debug("saving_user", user_id=user.id, email=user.email)

        if user.id:
            # Update existing user
            result = await self._session.execute(
                select(UserModel).where(UserModel.id == user.id)
            )
            user_model = result.scalar_one_or_none()

            if not user_model:
                raise ValueError(f"User with ID {user.id} not found")

            # Update model from domain entity
            user_model.email = user.email
            user_model.name = user.name
            user_model.updated_at = user.updated_at
        else:
            # Create new user
            user_model = UserModel.from_domain(user)
            self._session.add(user_model)

        # Flush to assign ID without committing transaction
        await self._session.flush()
        await self._session.refresh(user_model)

        logger.info("user_saved", user_id=user_model.id)

        return user_model.to_domain()

    async def delete(self, user_id: int) -> None:
        """Remove user from persistence."""
        logger.debug("deleting_user", user_id=user_id)

        result = await self._session.execute(
            select(UserModel).where(UserModel.id == user_id)
        )
        user_model = result.scalar_one_or_none()

        if user_model:
            await self._session.delete(user_model)
            await self._session.flush()
            logger.info("user_deleted", user_id=user_id)

    async def exists(self, user_id: int) -> bool:
        """Check if user exists."""
        result = await self._session.execute(
            select(exists().where(UserModel.id == user_id))
        )
        return result.scalar()

# File: src/infrastructure/models/user_model.py
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import DeclarativeBase
from datetime import datetime
from src.domain.entities.user import User

class Base(DeclarativeBase):
    pass

class UserModel(Base):
    """
    SQLAlchemy ORM model for users table.

    Knows about database structure, separate from domain entity.
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_domain(self) -> User:
        """Map ORM model to domain entity."""
        return User(
            id=self.id,
            email=self.email,
            name=self.name,
            created_at=self.created_at,
            updated_at=self.updated_at
        )

    @staticmethod
    def from_domain(user: User) -> "UserModel":
        """Map domain entity to ORM model."""
        return UserModel(
            id=user.id,
            email=user.email,
            name=user.name,
            created_at=user.created_at,
            updated_at=user.updated_at
        )
```

### 4.4 Repository Dependency Injection

#### Dependency Chain Setup

```python
# File: src/api/dependencies/repositories.py
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.api.dependencies.database import get_db_session
from src.infrastructure.repositories.sqlalchemy_user_repository import (
    SQLAlchemyUserRepository
)
from src.domain.repositories.user_repository import UserRepositoryPort

def get_user_repository(
    session: AsyncSession = Depends(get_db_session)
) -> UserRepositoryPort:
    """
    Provide user repository with database session dependency.

    Dependency chain: UserRepository → DBSession → Engine (singleton)

    Request-scoped: New repository instance per request.
    Session automatically committed/rolled back after request.
    """
    return SQLAlchemyUserRepository(session)
```

#### Usage in API Routes

```python
# File: src/api/routes/users.py
from fastapi import APIRouter, Depends, HTTPException, status
from src.domain.repositories.user_repository import UserRepositoryPort
from src.api.dependencies.repositories import get_user_repository
from src.api.schemas.user import UserCreate, UserResponse, UserList
import structlog

router = APIRouter(prefix="/users", tags=["users"])
logger = structlog.get_logger()

@router.post(
    "",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED
)
async def create_user(
    user_data: UserCreate,
    user_repo: UserRepositoryPort = Depends(get_user_repository)
):
    """
    Create new user.

    FastAPI automatically:
    1. Creates database session (via get_db_session)
    2. Injects repository with session (via get_user_repository)
    3. Commits session after successful response
    4. Rolls back session on exception
    5. Closes session after request completes
    """
    logger.info("creating_user", email=user_data.email)

    # Check if email exists
    existing = await user_repo.get_by_email(user_data.email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"User with email '{user_data.email}' already exists"
        )

    # Create domain entity
    from src.domain.entities.user import User
    from datetime import datetime

    user = User(
        email=user_data.email,
        name=user_data.name,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )

    # Save via repository
    saved_user = await user_repo.save(user)

    logger.info("user_created", user_id=saved_user.id)

    return UserResponse.from_domain(saved_user)

@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    user_repo: UserRepositoryPort = Depends(get_user_repository)
):
    """Retrieve user by ID."""
    logger.info("fetching_user", user_id=user_id)

    user = await user_repo.get_by_id(user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found"
        )

    return UserResponse.from_domain(user)

@router.get("", response_model=UserList)
async def list_users(
    limit: int = 100,
    offset: int = 0,
    user_repo: UserRepositoryPort = Depends(get_user_repository)
):
    """List users with pagination."""
    logger.info("listing_users", limit=limit, offset=offset)

    users = await user_repo.list_all(limit=limit, offset=offset)

    return UserList(
        users=[UserResponse.from_domain(u) for u in users],
        total=len(users),
        limit=limit,
        offset=offset
    )

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    user_repo: UserRepositoryPort = Depends(get_user_repository)
):
    """Delete user by ID."""
    logger.info("deleting_user", user_id=user_id)

    # Check if exists
    if not await user_repo.exists(user_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found"
        )

    await user_repo.delete(user_id)

    logger.info("user_deleted", user_id=user_id)
```

### 4.5 Testing with Mocked Repositories

```python
# File: tests/unit/test_user_routes.py
import pytest
from fastapi.testclient import TestClient
from src.api.dependencies.repositories import get_user_repository
from src.domain.entities.user import User
from datetime import datetime

class MockUserRepository:
    """Mock repository for testing (no database needed)."""

    def __init__(self):
        self._users: dict[int, User] = {}
        self._next_id = 1

    async def get_by_id(self, user_id: int) -> User | None:
        return self._users.get(user_id)

    async def get_by_email(self, email: str) -> User | None:
        for user in self._users.values():
            if user.email == email:
                return user
        return None

    async def save(self, user: User) -> User:
        if not user.id:
            user.id = self._next_id
            self._next_id += 1
        self._users[user.id] = user
        return user

    async def delete(self, user_id: int) -> None:
        self._users.pop(user_id, None)

    async def exists(self, user_id: int) -> bool:
        return user_id in self._users

    async def list_all(self, limit: int = 100, offset: int = 0) -> list[User]:
        users = list(self._users.values())
        return users[offset:offset + limit]

@pytest.fixture
def mock_user_repo():
    """Provide mock user repository."""
    return MockUserRepository()

@pytest.fixture
def client(mock_user_repo):
    """Test client with mocked repository dependency."""
    from src.main import app

    # Override repository dependency
    app.dependency_overrides[get_user_repository] = lambda: mock_user_repo

    with TestClient(app) as test_client:
        yield test_client

    # Cleanup
    app.dependency_overrides.clear()

def test_create_user(client: TestClient):
    """Test user creation endpoint."""
    response = client.post(
        "/users",
        json={"email": "test@example.com", "name": "Test User"}
    )

    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "test@example.com"
    assert data["name"] == "Test User"
    assert "id" in data

def test_get_user(client: TestClient, mock_user_repo: MockUserRepository):
    """Test get user endpoint."""
    # Setup: Create user in mock repo
    user = User(
        id=1,
        email="test@example.com",
        name="Test User",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    mock_user_repo._users[1] = user

    # Test
    response = client.get("/users/1")

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 1
    assert data["email"] == "test@example.com"

def test_get_nonexistent_user(client: TestClient):
    """Test get user with invalid ID."""
    response = client.get("/users/999")

    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()
```

### 4.6 Connection Pool Configuration Best Practices

```python
# File: src/infrastructure/database/engine.py
from sqlalchemy.ext.asyncio import create_async_engine

# Production-optimized engine configuration
engine = create_async_engine(
    database_url,

    # Connection pooling
    pool_size=10,                   # Persistent connections (scale: concurrent_requests / 2)
    max_overflow=20,                # Additional connections during spikes
    pool_recycle=3600,              # Recycle connections after 1 hour (prevents stale connections)
    pool_pre_ping=True,             # Verify connection health before use (adds ~1ms overhead)
    pool_timeout=30,                # Max wait time for connection from pool (seconds)

    # Query execution
    echo=False,                     # Don't log SQL (use middleware instead)
    echo_pool=False,                # Don't log connection pool events
    future=True,                    # Enable SQLAlchemy 2.0 future mode

    # Connection lifecycle
    connect_args={
        "timeout": 10,              # Connection timeout (seconds)
        "command_timeout": 60,      # Query timeout (seconds)
        "server_settings": {
            "application_name": "fastapi-microservice",  # Identify in pg_stat_activity
        }
    }
)
```

**Configuration Guidelines:**

| Setting | Recommended Value | Rationale |
|---------|------------------|-----------|
| `pool_size` | `concurrent_requests / 2` | Each request typically uses 1 connection briefly |
| `max_overflow` | `pool_size * 2` | Handle traffic spikes without exhaustion |
| `pool_recycle` | `3600s` (1 hour) | Prevent stale connections, align with database timeouts |
| `pool_pre_ping` | `True` | Detect dead connections before use (adds ~1ms) |
| `expire_on_commit` | `False` | **CRITICAL for async** - prevents implicit I/O after commit |
| `autoflush` | `False` | Manual flush for explicit control |

### 4.7 Decision Criteria

**Use Lifespan + Singleton Engine when:**
- Building production application (default)
- Want optimal connection pooling
- Need per-request transaction isolation

**Use Per-Request Engine when:**
- Integration testing with complete isolation
- Temporary workaround during migration

**Use Repository Pattern when:**
- Application has business logic beyond CRUD
- Need to support multiple databases
- Want to unit test without database

---

### 4.8 Type Safety with SQLAlchemy ORM

SQLAlchemy 2.0+ provides comprehensive type hint support for declarative models, enabling static type checking with mypy and improving IDE autocomplete[^35]. Type safety at the ORM layer prevents attribute errors and ensures correct query construction.

#### Pattern 1: Fully Typed SQLAlchemy Models

```python
# File: src/domain/models/user.py
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, Boolean, DateTime, ForeignKey, CheckConstraint
from datetime import datetime
from typing import Optional
import structlog

logger = structlog.get_logger(__name__)

class Base(DeclarativeBase):
    """
    Base class for all SQLAlchemy models with type safety.

    SQLAlchemy 2.0+ uses Mapped[] generic type for full type hint support.
    """
    pass

class User(Base):
    """
    User domain model with comprehensive type safety.

    Type hints enable:
    - Static type checking with mypy
    - IDE autocomplete for attributes
    - Runtime validation of attribute types
    """
    __tablename__ = "users"

    # Primary key (required, never null)
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # Required string fields (NOT NULL in database)
    email: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        unique=True,
        index=True,
        doc="User email address (unique identifier)"
    )

    username: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        unique=True,
        index=True,
        doc="User display name (alphanumeric, 3-50 chars)"
    )

    # Optional string fields (NULL allowed in database)
    full_name: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        doc="User's full legal name"
    )

    bio: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True,
        doc="User biography (max 500 characters)"
    )

    # Required boolean with default
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        server_default="true",
        doc="User account active status"
    )

    is_verified: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        server_default="false",
        doc="Email verification status"
    )

    # Timestamp fields with automatic defaults
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.utcnow,
        server_default="now()",
        doc="Account creation timestamp (UTC)"
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        server_default="now()",
        doc="Last update timestamp (UTC)"
    )

    # Optional timestamp (nullable)
    last_login_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        doc="Last successful login timestamp"
    )

    # Integer with range constraint
    login_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        server_default="0",
        doc="Number of successful logins"
    )

    # Relationships with type hints
    posts: Mapped[list["Post"]] = relationship(
        "Post",
        back_populates="author",
        cascade="all, delete-orphan",
        lazy="selectin",  # Eager loading by default
        doc="All posts authored by this user"
    )

    # Table-level constraints
    __table_args__ = (
        CheckConstraint("LENGTH(username) >= 3", name="username_min_length"),
        CheckConstraint("LENGTH(email) >= 5", name="email_min_length"),
        CheckConstraint("login_count >= 0", name="login_count_non_negative"),
    )

    def __repr__(self) -> str:
        """String representation for debugging."""
        return f"<User(id={self.id}, email='{self.email}', active={self.is_active})>"

    # Type-safe property methods
    def is_email_verified(self) -> bool:
        """Check if user's email is verified."""
        return self.is_verified

    def increment_login_count(self) -> None:
        """Increment login counter (type-safe mutation)."""
        self.login_count += 1
        self.last_login_at = datetime.utcnow()
        logger.info(
            "user_login_recorded",
            user_id=self.id,
            login_count=self.login_count
        )

class Post(Base):
    """Blog post model demonstrating foreign key relationships with type safety."""
    __tablename__ = "posts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    title: Mapped[str] = mapped_column(String(200), nullable=False)

    content: Mapped[str] = mapped_column(String(10000), nullable=False)

    published: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        server_default="false"
    )

    # Foreign key with type hint
    author_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    # Relationship back to User (bidirectional)
    author: Mapped["User"] = relationship(
        "User",
        back_populates="posts",
        lazy="joined"  # Eager load author with post
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.utcnow,
        server_default="now()"
    )

    def __repr__(self) -> str:
        return f"<Post(id={self.id}, title='{self.title[:30]}...', author_id={self.author_id})>"
```

**✅ Benefits:**
- **Static Type Checking:** mypy validates attribute access at development time
- **IDE Autocomplete:** Full IntelliSense support for model attributes
- **Self-Documenting:** Type hints serve as inline documentation
- **Runtime Safety:** SQLAlchemy validates types when setting attributes
- **Relationship Safety:** Typed relationships prevent attribute errors

**❌ Drawbacks:**
- **Learning Curve:** Requires understanding of SQLAlchemy 2.0 `Mapped[]` syntax
- **Verbosity:** More code than untyped models (trade-off for safety)
- **Migration Complexity:** Migrating from SQLAlchemy 1.x requires rewriting models

**Use When:**
- Building new SQLAlchemy 2.0+ applications (always use Mapped[])
- Team uses mypy for static type checking (type safety enforced)
- Codebase has >10 models (complexity benefits from type hints)

#### Pattern 2: Type-Safe Repository with Generic Types

```python
# File: src/infrastructure/database/repository.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from typing import TypeVar, Generic, Type, Optional, Sequence
from src.domain.models.user import Base
import structlog

logger = structlog.get_logger(__name__)

# Generic type variable for model classes
ModelType = TypeVar("ModelType", bound=Base)

class Repository(Generic[ModelType]):
    """
    Generic repository with type-safe CRUD operations.

    Uses Python generics to provide type safety for repository methods.
    Enables static type checking and IDE autocomplete for all operations.

    Example usage:
        user_repo = Repository[User](session)
        user = await user_repo.get_by_id(123)  # Returns: User | None
        users = await user_repo.get_all()       # Returns: list[User]
    """

    def __init__(self, session: AsyncSession, model_class: Type[ModelType]) -> None:
        """
        Initialize repository for specific model type.

        Args:
            session: SQLAlchemy async session
            model_class: Model class (e.g., User, Post)
        """
        self.session = session
        self.model_class = model_class

    async def get_by_id(self, id: int) -> Optional[ModelType]:
        """
        Get single model instance by primary key.

        Args:
            id: Primary key value

        Returns:
            Model instance if found, None otherwise

        Type-safe: Return type is Optional[ModelType] (e.g., Optional[User])
        """
        result = await self.session.execute(
            select(self.model_class).where(self.model_class.id == id)
        )
        instance = result.scalar_one_or_none()

        if instance:
            logger.debug(
                "repository_get_by_id_found",
                model=self.model_class.__name__,
                id=id
            )
        else:
            logger.debug(
                "repository_get_by_id_not_found",
                model=self.model_class.__name__,
                id=id
            )

        return instance

    async def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        order_by: Optional[str] = None
    ) -> Sequence[ModelType]:
        """
        Get all model instances with pagination.

        Args:
            skip: Number of records to skip (offset)
            limit: Maximum number of records to return
            order_by: Column name to order by (default: id ascending)

        Returns:
            List of model instances (type-safe: list[ModelType])
        """
        query = select(self.model_class).offset(skip).limit(limit)

        if order_by:
            # Type-safe: Ensure order_by column exists on model
            if hasattr(self.model_class, order_by):
                query = query.order_by(getattr(self.model_class, order_by))
            else:
                logger.warning(
                    "repository_invalid_order_by_column",
                    model=self.model_class.__name__,
                    column=order_by,
                    message=f"Column '{order_by}' does not exist on {self.model_class.__name__}"
                )

        result = await self.session.execute(query)
        instances = result.scalars().all()

        logger.debug(
            "repository_get_all",
            model=self.model_class.__name__,
            count=len(instances),
            skip=skip,
            limit=limit
        )

        return instances

    async def create(self, instance: ModelType) -> ModelType:
        """
        Create new model instance.

        Args:
            instance: Model instance to create (type: ModelType)

        Returns:
            Created instance with populated ID and defaults
        """
        self.session.add(instance)
        await self.session.flush()  # Get ID without committing transaction
        await self.session.refresh(instance)  # Load defaults and generated values

        logger.info(
            "repository_create",
            model=self.model_class.__name__,
            id=instance.id
        )

        return instance

    async def update(self, id: int, **kwargs) -> Optional[ModelType]:
        """
        Update model instance by ID.

        Args:
            id: Primary key of instance to update
            **kwargs: Field values to update

        Returns:
            Updated instance if found, None otherwise

        Type-safe: Validates kwargs keys match model columns
        """
        # Validate all kwargs keys exist as model columns
        invalid_keys = [
            key for key in kwargs.keys()
            if not hasattr(self.model_class, key)
        ]
        if invalid_keys:
            raise ValueError(
                f"Invalid update fields for {self.model_class.__name__}: {invalid_keys}"
            )

        # Execute update
        await self.session.execute(
            update(self.model_class)
            .where(self.model_class.id == id)
            .values(**kwargs)
        )

        # Fetch and return updated instance
        updated_instance = await self.get_by_id(id)

        if updated_instance:
            logger.info(
                "repository_update",
                model=self.model_class.__name__,
                id=id,
                fields_updated=list(kwargs.keys())
            )
        else:
            logger.warning(
                "repository_update_not_found",
                model=self.model_class.__name__,
                id=id
            )

        return updated_instance

    async def delete(self, id: int) -> bool:
        """
        Delete model instance by ID.

        Args:
            id: Primary key of instance to delete

        Returns:
            True if deleted, False if not found
        """
        result = await self.session.execute(
            delete(self.model_class).where(self.model_class.id == id)
        )

        deleted = result.rowcount > 0

        if deleted:
            logger.info(
                "repository_delete",
                model=self.model_class.__name__,
                id=id
            )
        else:
            logger.warning(
                "repository_delete_not_found",
                model=self.model_class.__name__,
                id=id
            )

        return deleted

    async def exists(self, id: int) -> bool:
        """
        Check if instance exists by ID.

        Args:
            id: Primary key to check

        Returns:
            True if exists, False otherwise
        """
        result = await self.session.execute(
            select(self.model_class.id).where(self.model_class.id == id)
        )

        exists = result.scalar_one_or_none() is not None

        logger.debug(
            "repository_exists_check",
            model=self.model_class.__name__,
            id=id,
            exists=exists
        )

        return exists
```

**Usage with type safety:**

```python
# File: src/api/routes/users.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from src.infrastructure.database.repository import Repository
from src.infrastructure.database.session import get_session
from src.domain.models.user import User
from typing import List

router = APIRouter()

# Type-safe repository dependency
def get_user_repository(
    session: AsyncSession = Depends(get_session)
) -> Repository[User]:
    """
    Create User repository dependency.

    Return type Repository[User] provides full type safety:
    - repo.get_by_id(1) returns Optional[User]
    - repo.get_all() returns list[User]
    - IDE autocomplete knows exact return types
    """
    return Repository[User](session, User)

@router.get("/users/{user_id}", response_model=dict)
async def get_user(
    user_id: int,
    repo: Repository[User] = Depends(get_user_repository)
):
    """
    Get user by ID.

    Type safety ensures:
    - repo is Repository[User] (not generic Repository)
    - user is Optional[User] (mypy validates null check)
    - user.email is str (autocomplete works)
    """
    user: Optional[User] = await repo.get_by_id(user_id)  # Type-safe

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Type-safe access to user attributes (mypy validates)
    return {
        "id": user.id,
        "email": user.email,
        "username": user.username,
        "is_active": user.is_active,
        "created_at": user.created_at.isoformat()
    }

@router.get("/users", response_model=List[dict])
async def list_users(
    skip: int = 0,
    limit: int = 100,
    repo: Repository[User] = Depends(get_user_repository)
):
    """
    List all users with pagination.

    Type safety:
    - users is Sequence[User] (not generic list)
    - Iteration over users is type-safe
    - Each user has validated User attributes
    """
    users: Sequence[User] = await repo.get_all(skip=skip, limit=limit)

    return [
        {
            "id": user.id,
            "email": user.email,
            "username": user.username,
            "is_active": user.is_active
        }
        for user in users  # Type-safe iteration
    ]
```

**✅ Benefits:**
- **Generic Type Safety:** Repository methods return correctly typed results
- **IDE Autocomplete:** Full IntelliSense for repository operations
- **Compile-Time Validation:** mypy catches type errors before runtime
- **Refactoring Safety:** Rename refactors update all usages
- **Code Reusability:** Single repository class for all models

**❌ Drawbacks:**
- **Generic Complexity:** Requires understanding of Python generics
- **Type Annotation Verbosity:** More type hints than untyped code
- **Limited Dynamic Operations:** Type safety restricts dynamic column access

**Use When:**
- Team uses mypy for static type checking (always)
- Codebase has >3 model types (generics reduce duplication)
- Developers use IDEs with type hint support (VSCode, PyCharm)

### 4.9 Domain Model Validation with Pydantic

While SQLAlchemy models handle database persistence, Pydantic models validate business logic and API contracts. Combining both provides type safety across all application layers[^36].

#### Pattern 1: Pydantic Schemas for Domain Validation

```python
# File: src/api/schemas/user.py
from pydantic import BaseModel, Field, EmailStr, field_validator, model_validator
from typing import Optional
from datetime import datetime
import re
import structlog

logger = structlog.get_logger(__name__)

class UserBase(BaseModel):
    """
    Base user schema with common validation rules.

    Shared between request/response schemas to ensure
    consistent validation across API boundary.
    """

    email: EmailStr = Field(
        description="User email address (must be valid email format)",
        examples=["user@example.com"]
    )

    username: str = Field(
        min_length=3,
        max_length=50,
        pattern=r"^[a-zA-Z0-9_]+$",
        description="Username (alphanumeric and underscores only)",
        examples=["john_doe_123"]
    )

    full_name: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=100,
        description="User's full name",
        examples=["John Doe"]
    )

    @field_validator("username")
    @classmethod
    def validate_username_not_reserved(cls, v: str) -> str:
        """
        Prevent reserved usernames that conflict with system routes.

        Reserved names: admin, root, api, health, docs, etc.
        """
        reserved_usernames = {
            "admin", "administrator", "root", "system",
            "api", "health", "docs", "openapi", "swagger",
            "me", "self", "null", "undefined"
        }

        if v.lower() in reserved_usernames:
            raise ValueError(
                f"Username '{v}' is reserved and cannot be used. "
                f"Choose a different username."
            )

        return v

    @field_validator("full_name")
    @classmethod
    def validate_full_name_format(cls, v: Optional[str]) -> Optional[str]:
        """
        Validate full name contains only letters, spaces, hyphens.

        Allows international characters (Unicode letters).
        """
        if v is None:
            return v

        # Allow letters (including international), spaces, hyphens, apostrophes
        if not re.match(r"^[\w\s\-']+$", v, re.UNICODE):
            raise ValueError(
                "Full name must contain only letters, spaces, hyphens, and apostrophes"
            )

        # Check for suspicious patterns (multiple consecutive spaces)
        if "  " in v:
            raise ValueError("Full name contains excessive whitespace")

        return v.strip()

class UserCreate(UserBase):
    """
    Schema for creating new user (request validation).

    Inherits base validation, adds password requirements.
    """

    password: str = Field(
        min_length=8,
        max_length=128,
        description="Password (min 8 chars, mix of upper/lower/digit/special)",
        examples=["SecureP@ssw0rd"]
    )

    password_confirm: str = Field(
        description="Password confirmation (must match password)",
        examples=["SecureP@ssw0rd"]
    )

    @field_validator("password")
    @classmethod
    def validate_password_complexity(cls, v: str) -> str:
        """
        Enforce password complexity requirements.

        Requirements:
        - Minimum 8 characters
        - At least one uppercase letter
        - At least one lowercase letter
        - At least one digit
        - At least one special character
        """
        errors = []

        if len(v) < 8:
            errors.append("at least 8 characters")

        if not re.search(r"[A-Z]", v):
            errors.append("at least one uppercase letter")

        if not re.search(r"[a-z]", v):
            errors.append("at least one lowercase letter")

        if not re.search(r"\d", v):
            errors.append("at least one digit")

        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", v):
            errors.append("at least one special character")

        if errors:
            raise ValueError(
                f"Password must contain {', '.join(errors)}. "
                f"Example: SecureP@ssw0rd123"
            )

        return v

    @model_validator(mode="after")
    def validate_passwords_match(self) -> "UserCreate":
        """
        Ensure password and password_confirm match.

        Cross-field validation using model_validator.
        """
        if self.password != self.password_confirm:
            raise ValueError("Password and password confirmation do not match")

        return self

class UserUpdate(BaseModel):
    """
    Schema for updating existing user (partial updates allowed).

    All fields optional for PATCH semantics.
    """

    email: Optional[EmailStr] = None
    username: Optional[str] = Field(default=None, min_length=3, max_length=50)
    full_name: Optional[str] = Field(default=None, max_length=100)
    is_active: Optional[bool] = None

    @model_validator(mode="after")
    def validate_at_least_one_field(self) -> "UserUpdate":
        """
        Ensure at least one field provided for update.

        Empty updates (no fields changed) are rejected.
        """
        # Check if any field has a non-None value
        if not any([
            self.email is not None,
            self.username is not None,
            self.full_name is not None,
            self.is_active is not None
        ]):
            raise ValueError("At least one field must be provided for update")

        return self

class UserResponse(UserBase):
    """
    Schema for user response (includes database-generated fields).

    Used for API responses, excludes sensitive fields like password.
    """

    id: int = Field(description="User ID (auto-generated)")

    is_active: bool = Field(description="Account active status")

    is_verified: bool = Field(description="Email verification status")

    created_at: datetime = Field(description="Account creation timestamp (UTC)")

    updated_at: datetime = Field(description="Last update timestamp (UTC)")

    login_count: int = Field(description="Number of successful logins")

    class Config:
        """Pydantic configuration."""
        from_attributes = True  # Enable ORM mode (load from SQLAlchemy models)
        json_schema_extra = {
            "example": {
                "id": 123,
                "email": "user@example.com",
                "username": "john_doe",
                "full_name": "John Doe",
                "is_active": True,
                "is_verified": True,
                "created_at": "2025-11-01T12:00:00Z",
                "updated_at": "2025-11-01T15:30:00Z",
                "login_count": 42
            }
        }
```

**Usage in API endpoints:**

```python
# File: src/api/routes/users.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from src.api.schemas.user import UserCreate, UserUpdate, UserResponse
from src.domain.models.user import User
from src.infrastructure.database.repository import Repository
from src.infrastructure.database.session import get_session
import structlog

router = APIRouter()
logger = structlog.get_logger(__name__)

@router.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreate,  # Automatic request validation with Pydantic
    session: AsyncSession = Depends(get_session)
):
    """
    Create new user with validated input.

    Request body validation (automatic via Pydantic):
    - Email format validated (EmailStr)
    - Username format validated (regex pattern)
    - Password complexity validated (custom validator)
    - Password confirmation validated (model validator)
    - Reserved usernames rejected (custom validator)

    Returns validated UserResponse schema.
    """
    repo = Repository[User](session, User)

    # Check if email already exists
    existing_user_query = await session.execute(
        select(User).where(User.email == user_data.email)
    )
    if existing_user_query.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"User with email {user_data.email} already exists"
        )

    # Create SQLAlchemy model from Pydantic schema
    new_user = User(
        email=user_data.email,
        username=user_data.username,
        full_name=user_data.full_name,
        # Password hashing logic here (not shown)
    )

    created_user = await repo.create(new_user)
    await session.commit()

    logger.info(
        "user_created",
        user_id=created_user.id,
        email=created_user.email
    )

    # Return Pydantic schema (automatic serialization)
    return UserResponse.from_orm(created_user)

@router.patch("/users/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_data: UserUpdate,  # Partial update validation
    session: AsyncSession = Depends(get_session)
):
    """
    Update user with validated partial input.

    Validation ensures:
    - At least one field provided (model validator)
    - Email format valid (if provided)
    - Username format valid (if provided)
    """
    repo = Repository[User](session, User)

    user = await repo.get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Update only provided fields (Pydantic excludes unset)
    update_data = user_data.model_dump(exclude_unset=True)

    updated_user = await repo.update(user_id, **update_data)
    await session.commit()

    logger.info(
        "user_updated",
        user_id=user_id,
        fields_updated=list(update_data.keys())
    )

    return UserResponse.from_orm(updated_user)
```

**✅ Benefits:**
- **Automatic Request Validation:** FastAPI validates requests using Pydantic schemas
- **Type-Safe API Contract:** Request/response types enforced at compile time
- **Self-Documenting:** Pydantic schemas generate OpenAPI documentation
- **Business Logic Validation:** Custom validators enforce domain rules
- **Error Messages:** Validation errors return structured, actionable messages

**❌ Drawbacks:**
- **Schema Duplication:** Separate schemas for SQLAlchemy models and Pydantic schemas
- **Maintenance Overhead:** Changes to domain require updating both model and schema
- **Learning Curve:** Requires understanding both SQLAlchemy and Pydantic validation

**Use When:**
- Building REST APIs with FastAPI (always use Pydantic schemas)
- Need input validation before database operations (prevent invalid data persistence)
- Enforcing business rules (username restrictions, password policies, etc.)
- Generating API documentation (OpenAPI schema generation)

---


## 9. Error Handling and Validation

### 9.1 Recommended Approach: Pydantic Request/Response Validation with Structured Exceptions

FastAPI's integration with Pydantic provides automatic request validation with structured error responses[^37]. Combined with custom exception handlers, this approach delivers consistent error messages across all API endpoints.

**Core Benefits:**
- **Automatic Validation:** FastAPI validates request bodies, query params, path params using Pydantic
- **Structured Error Responses:** Validation errors return RFC 7807-compliant Problem Details[^38]
- **Type Safety:** Validation errors caught before handler execution (fail-fast principle)
- **Developer Experience:** Detailed validation errors with field paths and error types

### 9.2 Request and Response Validation with Pydantic

#### Pattern 1: Comprehensive Request Validation

```python
# File: src/api/schemas/resource.py
from pydantic import BaseModel, Field, HttpUrl, field_validator, model_validator
from typing import Optional, Literal
from datetime import datetime
from enum import Enum
import re
import structlog

logger = structlog.get_logger(__name__)

class ResourceType(str, Enum):
    """Enum for valid resource types (type-safe)."""
    FILE = "file"
    URL = "url"
    DATABASE = "database"
    API = "api"

class ResourceCreateRequest(BaseModel):
    """
    Request schema for creating resources with comprehensive validation.

    Validation layers:
    1. Type validation (automatic from type hints)
    2. Field constraints (min/max length, patterns, ranges)
    3. Field-level validators (custom business logic)
    4. Model-level validators (cross-field validation)
    """

    # Required fields with constraints
    name: str = Field(
        min_length=1,
        max_length=100,
        description="Resource name (alphanumeric, spaces, hyphens)",
        examples=["My Resource", "data-pipeline-01"]
    )

    type: ResourceType = Field(
        description="Resource type (enum validation)",
        examples=["file", "url"]
    )

    url: Optional[HttpUrl] = Field(
        default=None,
        description="Resource URL (required if type=url, validated format)",
        examples=["https://example.com/resource"]
    )

    description: Optional[str] = Field(
        default=None,
        max_length=500,
        description="Resource description (max 500 characters)"
    )

    # Numeric fields with range constraints
    priority: int = Field(
        default=1,
        ge=1,
        le=10,
        description="Priority level (1=lowest, 10=highest)"
    )

    # List fields with item validation
    tags: list[str] = Field(
        default_factory=list,
        max_length=10,
        description="Resource tags (max 10 tags, each max 50 chars)"
    )

    # Dict fields with structured validation
    metadata: dict[str, str] = Field(
        default_factory=dict,
        description="Additional metadata (string keys/values only)"
    )

    @field_validator("name")
    @classmethod
    def validate_name_format(cls, v: str) -> str:
        """
        Validate resource name format.

        Allowed: Letters, numbers, spaces, hyphens, underscores
        Forbidden: Special characters, leading/trailing spaces
        """
        # Strip whitespace
        v = v.strip()

        # Check for valid characters
        if not re.match(r"^[a-zA-Z0-9\s\-_]+$", v):
            raise ValueError(
                "Resource name must contain only letters, numbers, spaces, hyphens, and underscores"
            )

        # Prevent multiple consecutive spaces
        if "  " in v:
            raise ValueError("Resource name must not contain consecutive spaces")

        return v

    @field_validator("tags")
    @classmethod
    def validate_tags_format(cls, v: list[str]) -> list[str]:
        """
        Validate tag format and uniqueness.

        Requirements:
        - Each tag: 1-50 characters
        - Alphanumeric and hyphens only
        - No duplicates
        - Lowercase normalization
        """
        if not v:
            return v

        validated_tags = []
        seen_tags = set()

        for tag in v:
            # Normalize to lowercase
            tag = tag.strip().lower()

            # Check length
            if not (1 <= len(tag) <= 50):
                raise ValueError(f"Tag '{tag}' must be 1-50 characters long")

            # Check format
            if not re.match(r"^[a-z0-9\-]+$", tag):
                raise ValueError(
                    f"Tag '{tag}' must contain only lowercase letters, numbers, and hyphens"
                )

            # Check for duplicates
            if tag in seen_tags:
                logger.warning("duplicate_tag_removed", tag=tag)
                continue

            seen_tags.add(tag)
            validated_tags.append(tag)

        return validated_tags

    @field_validator("metadata")
    @classmethod
    def validate_metadata_size(cls, v: dict[str, str]) -> dict[str, str]:
        """
        Validate metadata dictionary constraints.

        Limits:
        - Max 20 key-value pairs
        - Keys: 1-50 characters
        - Values: max 500 characters
        - Total size: <10KB
        """
        if not v:
            return v

        # Check number of entries
        if len(v) > 20:
            raise ValueError("Metadata must not exceed 20 key-value pairs")

        # Validate each key-value pair
        total_size = 0
        for key, value in v.items():
            # Validate key format
            if not (1 <= len(key) <= 50):
                raise ValueError(f"Metadata key '{key}' must be 1-50 characters")

            if not re.match(r"^[a-zA-Z0-9_\-\.]+$", key):
                raise ValueError(
                    f"Metadata key '{key}' must contain only letters, numbers, underscores, hyphens, dots"
                )

            # Validate value length
            if len(value) > 500:
                raise ValueError(f"Metadata value for key '{key}' exceeds 500 characters")

            # Track total size
            total_size += len(key) + len(value)

        # Check total size (prevent abuse)
        if total_size > 10000:  # 10KB
            raise ValueError("Metadata total size exceeds 10KB limit")

        return v

    @model_validator(mode="after")
    def validate_url_required_for_url_type(self) -> "ResourceCreateRequest":
        """
        Cross-field validation: URL required when type=url.

        Uses model_validator to access multiple fields.
        """
        if self.type == ResourceType.URL and not self.url:
            raise ValueError("URL is required when resource type is 'url'")

        if self.type != ResourceType.URL and self.url:
            logger.warning(
                "url_provided_for_non_url_type",
                type=self.type,
                message="URL provided but resource type is not 'url' (URL will be ignored)"
            )

        return self

    class Config:
        """Pydantic configuration."""
        json_schema_extra = {
            "example": {
                "name": "External API Resource",
                "type": "url",
                "url": "https://api.example.com/data",
                "description": "Third-party API endpoint",
                "priority": 5,
                "tags": ["api", "external", "production"],
                "metadata": {
                    "auth_type": "bearer",
                    "rate_limit": "1000/hour"
                }
            }
        }

class ResourceResponse(BaseModel):
    """Response schema for resource (includes database-generated fields)."""

    id: int = Field(description="Resource ID (auto-generated)")

    name: str

    type: ResourceType

    url: Optional[HttpUrl] = None

    description: Optional[str] = None

    priority: int

    tags: list[str]

    metadata: dict[str, str]

    # Database-generated fields
    created_at: datetime = Field(description="Creation timestamp (UTC)")

    updated_at: datetime = Field(description="Last update timestamp (UTC)")

    created_by_user_id: Optional[int] = Field(
        default=None,
        description="ID of user who created resource"
    )

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 123,
                "name": "External API Resource",
                "type": "url",
                "url": "https://api.example.com/data",
                "description": "Third-party API endpoint",
                "priority": 5,
                "tags": ["api", "external", "production"],
                "metadata": {"auth_type": "bearer"},
                "created_at": "2025-11-01T10:00:00Z",
                "updated_at": "2025-11-01T10:00:00Z",
                "created_by_user_id": 42
            }
        }
```

**Usage in API endpoints (automatic validation):**

```python
# File: src/api/routes/resources.py
from fastapi import APIRouter, Depends, HTTPException, status
from src.api.schemas.resource import ResourceCreateRequest, ResourceResponse
from src.domain.models.resource import Resource
from src.infrastructure.database.repository import Repository
from sqlalchemy.ext.asyncio import AsyncSession
from src.infrastructure.database.session import get_session
import structlog

router = APIRouter()
logger = structlog.get_logger(__name__)

@router.post("/resources", response_model=ResourceResponse, status_code=status.HTTP_201_CREATED)
async def create_resource(
    resource_data: ResourceCreateRequest,  # Automatic validation by FastAPI + Pydantic
    session: AsyncSession = Depends(get_session)
):
    """
    Create new resource with validated input.

    FastAPI automatically validates request body against ResourceCreateRequest schema.
    Validation occurs BEFORE handler execution:
    - Type validation (str, int, HttpUrl, enum)
    - Field constraints (min/max length, patterns, ranges)
    - Custom validators (name format, tag format, metadata size)
    - Model validators (URL required for URL type)

    If validation fails, FastAPI returns 422 Unprocessable Entity with detailed errors.
    Handler only executes if ALL validation passes.
    """
    repo = Repository[Resource](session, Resource)

    # Create domain model from validated Pydantic schema
    new_resource = Resource(
        name=resource_data.name,
        type=resource_data.type.value,  # Enum to string
        url=str(resource_data.url) if resource_data.url else None,
        description=resource_data.description,
        priority=resource_data.priority,
        tags=resource_data.tags,
        metadata=resource_data.metadata
    )

    created_resource = await repo.create(new_resource)
    await session.commit()

    logger.info(
        "resource_created",
        resource_id=created_resource.id,
        name=created_resource.name,
        type=created_resource.type
    )

    return ResourceResponse.from_orm(created_resource)
```

**Example validation error response (automatic):**

```json
{
  "detail": [
    {
      "type": "string_too_short",
      "loc": ["body", "name"],
      "msg": "String should have at least 1 character",
      "input": "",
      "ctx": {"min_length": 1}
    },
    {
      "type": "value_error",
      "loc": ["body", "url"],
      "msg": "Value error, URL is required when resource type is 'url'",
      "input": null
    },
    {
      "type": "int_parsing",
      "loc": ["body", "priority"],
      "msg": "Input should be a valid integer",
      "input": "high"
    }
  ]
}
```

**✅ Benefits:**
- **Automatic Validation:** FastAPI validates requests before handler execution
- **Fail-Fast:** Invalid requests rejected immediately with detailed errors
- **Type Safety:** Pydantic ensures type correctness at API boundary
- **Self-Documenting:** Validation rules generate OpenAPI schema automatically
- **Consistent Errors:** All validation errors use same structured format

**❌ Drawbacks:**
- **Validation Overhead:** Complex schemas add 1-5ms per request validation time
- **Error Verbosity:** Detailed validation errors expose internal field names
- **Schema Maintenance:** Changes to validation require updating Pydantic schemas

**Use When:**
- Building REST APIs (always use request validation)
- Accepting user input (never trust client data)
- Enforcing business rules at API boundary
- Generating API documentation (OpenAPI schema)

### 9.3 Custom Exception Hierarchy

Define custom exceptions for domain-specific errors with structured error responses[^39].

```python
# File: src/core/exceptions.py
from typing import Optional, Any
import structlog

logger = structlog.get_logger(__name__)

class ApplicationException(Exception):
    """
    Base exception for all application errors.

    Attributes:
        message: Human-readable error message
        error_code: Machine-readable error code
        status_code: HTTP status code
        details: Additional error context (optional)
    """

    def __init__(
        self,
        message: str,
        error_code: str,
        status_code: int = 500,
        details: Optional[dict[str, Any]] = None
    ) -> None:
        self.message = message
        self.error_code = error_code
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)

        logger.error(
            "application_exception",
            error_code=error_code,
            message=message,
            status_code=status_code,
            details=details
        )

class ValidationException(ApplicationException):
    """
    Validation error (client provided invalid data).

    HTTP 422 Unprocessable Entity
    """

    def __init__(
        self,
        message: str,
        field: Optional[str] = None,
        details: Optional[dict[str, Any]] = None
    ) -> None:
        error_details = details or {}
        if field:
            error_details["field"] = field

        super().__init__(
            message=message,
            error_code="VALIDATION_ERROR",
            status_code=422,
            details=error_details
        )

class ResourceNotFoundException(ApplicationException):
    """
    Resource not found error.

    HTTP 404 Not Found
    """

    def __init__(
        self,
        resource_type: str,
        resource_id: int | str,
        details: Optional[dict[str, Any]] = None
    ) -> None:
        error_details = details or {}
        error_details.update({
            "resource_type": resource_type,
            "resource_id": str(resource_id)
        })

        super().__init__(
            message=f"{resource_type} with ID {resource_id} not found",
            error_code="RESOURCE_NOT_FOUND",
            status_code=404,
            details=error_details
        )

class DuplicateResourceException(ApplicationException):
    """
    Resource already exists error (duplicate constraint violation).

    HTTP 409 Conflict
    """

    def __init__(
        self,
        resource_type: str,
        field: str,
        value: str,
        details: Optional[dict[str, Any]] = None
    ) -> None:
        error_details = details or {}
        error_details.update({
            "resource_type": resource_type,
            "duplicate_field": field,
            "duplicate_value": value
        })

        super().__init__(
            message=f"{resource_type} with {field}='{value}' already exists",
            error_code="DUPLICATE_RESOURCE",
            status_code=409,
            details=error_details
        )

class AuthorizationException(ApplicationException):
    """
    Authorization error (user lacks permission).

    HTTP 403 Forbidden
    """

    def __init__(
        self,
        message: str = "Insufficient permissions to perform this action",
        required_permission: Optional[str] = None,
        details: Optional[dict[str, Any]] = None
    ) -> None:
        error_details = details or {}
        if required_permission:
            error_details["required_permission"] = required_permission

        super().__init__(
            message=message,
            error_code="AUTHORIZATION_ERROR",
            status_code=403,
            details=error_details
        )

class AuthenticationException(ApplicationException):
    """
    Authentication error (invalid or missing credentials).

    HTTP 401 Unauthorized
    """

    def __init__(
        self,
        message: str = "Authentication required",
        details: Optional[dict[str, Any]] = None
    ) -> None:
        super().__init__(
            message=message,
            error_code="AUTHENTICATION_ERROR",
            status_code=401,
            details=details
        )

class ExternalServiceException(ApplicationException):
    """
    External service error (third-party API failure).

    HTTP 502 Bad Gateway
    """

    def __init__(
        self,
        service_name: str,
        message: str,
        details: Optional[dict[str, Any]] = None
    ) -> None:
        error_details = details or {}
        error_details["service_name"] = service_name

        super().__init__(
            message=f"External service '{service_name}' error: {message}",
            error_code="EXTERNAL_SERVICE_ERROR",
            status_code=502,
            details=error_details
        )

class RateLimitException(ApplicationException):
    """
    Rate limit exceeded error.

    HTTP 429 Too Many Requests
    """

    def __init__(
        self,
        limit: int,
        window_seconds: int,
        retry_after_seconds: int,
        details: Optional[dict[str, Any]] = None
    ) -> None:
        error_details = details or {}
        error_details.update({
            "rate_limit": limit,
            "window_seconds": window_seconds,
            "retry_after_seconds": retry_after_seconds
        })

        super().__init__(
            message=f"Rate limit exceeded ({limit} requests per {window_seconds}s). Retry after {retry_after_seconds}s.",
            error_code="RATE_LIMIT_EXCEEDED",
            status_code=429,
            details=error_details
        )
```

### 9.4 Global Exception Handlers

Register global exception handlers to convert custom exceptions into structured JSON responses[^40].

```python
# File: src/core/error_handlers.py
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError
from src.core.exceptions import ApplicationException
from sqlalchemy.exc import IntegrityError
import structlog
from typing import Any

logger = structlog.get_logger(__name__)

def register_exception_handlers(app: FastAPI) -> None:
    """
    Register global exception handlers for FastAPI application.

    Converts exceptions into RFC 7807-compliant Problem Details responses.
    """

    @app.exception_handler(ApplicationException)
    async def application_exception_handler(
        request: Request,
        exc: ApplicationException
    ) -> JSONResponse:
        """
        Handle custom application exceptions.

        Returns structured error response with error code, message, and details.
        """
        logger.error(
            "application_exception_caught",
            path=request.url.path,
            method=request.method,
            error_code=exc.error_code,
            status_code=exc.status_code,
            message=exc.message
        )

        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": {
                    "code": exc.error_code,
                    "message": exc.message,
                    "details": exc.details,
                    "path": request.url.path,
                    "method": request.method
                }
            }
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request,
        exc: RequestValidationError
    ) -> JSONResponse:
        """
        Handle Pydantic request validation errors.

        Formats validation errors into user-friendly structure.
        """
        # Extract validation errors
        errors = []
        for error in exc.errors():
            errors.append({
                "field": ".".join(str(loc) for loc in error["loc"]),
                "message": error["msg"],
                "type": error["type"],
                "input": error.get("input")
            })

        logger.warning(
            "request_validation_failed",
            path=request.url.path,
            method=request.method,
            errors=errors
        )

        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": "Request validation failed",
                    "details": {
                        "validation_errors": errors
                    },
                    "path": request.url.path,
                    "method": request.method
                }
            }
        )

    @app.exception_handler(IntegrityError)
    async def integrity_error_handler(
        request: Request,
        exc: IntegrityError
    ) -> JSONResponse:
        """
        Handle database integrity constraint violations.

        Converts SQLAlchemy IntegrityError into user-friendly message.
        """
        error_message = str(exc.orig)

        # Parse constraint violation type
        if "duplicate key" in error_message.lower() or "unique constraint" in error_message.lower():
            status_code = status.HTTP_409_CONFLICT
            error_code = "DUPLICATE_RESOURCE"
            message = "Resource already exists (unique constraint violation)"
        elif "foreign key constraint" in error_message.lower():
            status_code = status.HTTP_409_CONFLICT
            error_code = "FOREIGN_KEY_VIOLATION"
            message = "Cannot delete resource (referenced by other records)"
        elif "not null constraint" in error_message.lower():
            status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
            error_code = "MISSING_REQUIRED_FIELD"
            message = "Required field is missing"
        else:
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
            error_code = "DATABASE_INTEGRITY_ERROR"
            message = "Database constraint violation"

        logger.error(
            "database_integrity_error",
            path=request.url.path,
            method=request.method,
            error_code=error_code,
            constraint_error=error_message
        )

        return JSONResponse(
            status_code=status_code,
            content={
                "error": {
                    "code": error_code,
                    "message": message,
                    "details": {
                        "constraint_violation": error_message
                    },
                    "path": request.url.path,
                    "method": request.method
                }
            }
        )

    @app.exception_handler(Exception)
    async def generic_exception_handler(
        request: Request,
        exc: Exception
    ) -> JSONResponse:
        """
        Catch-all handler for unexpected exceptions.

        Logs full exception details, returns generic error to client.
        """
        logger.exception(
            "unexpected_exception",
            path=request.url.path,
            method=request.method,
            exception_type=type(exc).__name__,
            exception_message=str(exc)
        )

        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": {
                    "code": "INTERNAL_SERVER_ERROR",
                    "message": "An unexpected error occurred. Please try again later.",
                    "details": {},
                    "path": request.url.path,
                    "method": request.method
                }
            }
        )
```

**Registration in FastAPI application:**

```python
# File: src/main.py
from fastapi import FastAPI
from src.core.error_handlers import register_exception_handlers

app = FastAPI(title="AI Agent MCP Server")

# Register exception handlers
register_exception_handlers(app)
```

**✅ Benefits:**
- **Consistent Error Format:** All errors use same JSON structure
- **Client-Friendly Messages:** Error codes and messages actionable
- **Security:** Internal exceptions sanitized before returning to client
- **Logging:** All exceptions logged with context for debugging
- **RFC 7807 Compliance:** Error responses follow Problem Details standard

**❌ Drawbacks:**
- **Exception Overhead:** Exception handlers add 1-2ms per error response
- **Error Code Maintenance:** Error codes must stay consistent across versions
- **Generic Errors:** Catch-all handler may hide specific error types

**Use When:**
- Building production APIs (always use structured error responses)
- Need consistent error format across all endpoints
- Supporting multiple clients (web, mobile, CLI)
- Compliance requirements for error handling (SOC 2, ISO 27001)

### 9.5 Validation Error Formatting

Format Pydantic validation errors into user-friendly API responses.

```python
# File: src/api/utils/validation.py
from pydantic import ValidationError
from typing import Any

def format_validation_errors(exc: ValidationError) -> list[dict[str, Any]]:
    """
    Format Pydantic validation errors into structured format.

    Converts Pydantic error format into user-friendly structure
    suitable for API responses.

    Args:
        exc: Pydantic ValidationError

    Returns:
        List of formatted error dictionaries

    Example output:
        [
            {
                "field": "email",
                "message": "value is not a valid email address",
                "type": "value_error.email",
                "input": "invalid-email"
            }
        ]
    """
    formatted_errors = []

    for error in exc.errors():
        # Extract field path (e.g., "body.user.email" -> "user.email")
        field_path = ".".join(str(loc) for loc in error["loc"] if loc != "body")

        # Format error
        formatted_errors.append({
            "field": field_path,
            "message": error["msg"],
            "type": error["type"],
            "input": error.get("input"),
            "context": error.get("ctx", {})
        })

    return formatted_errors
```

**Example error response:**

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Request validation failed",
    "details": {
      "validation_errors": [
        {
          "field": "email",
          "message": "value is not a valid email address",
          "type": "value_error.email",
          "input": "not-an-email",
          "context": {}
        },
        {
          "field": "priority",
          "message": "ensure this value is greater than or equal to 1",
          "type": "value_error.number.not_ge",
          "input": 0,
          "context": {"limit_value": 1}
        }
      ]
    },
    "path": "/api/resources",
    "method": "POST"
  }
}
```

### 9.6 Decision Criteria

**Use Pydantic Request Validation when:**
- Building REST APIs with FastAPI (always)
- Accepting user input (never trust client data)
- Need automatic OpenAPI schema generation
- Want type-safe request/response contracts

**Use Custom Exception Hierarchy when:**
- Need domain-specific error types (ResourceNotFound, DuplicateResource, etc.)
- Want consistent error responses across all endpoints
- Building client SDKs (error codes enable programmatic handling)
- Compliance requires structured error logging

**Use Global Exception Handlers when:**
- Need to catch and format all exceptions consistently
- Want to prevent internal error details from leaking to clients
- Building production APIs (always use exception handlers)
- Need RFC 7807-compliant error responses

### 9.7 Error Correlation with Distributed Tracing

When errors occur in distributed systems, correlating them with trace context is critical for debugging. OpenTelemetry provides standardized trace propagation across service boundaries, enabling end-to-end request tracking[^41].

**Core Benefits:**
- **Distributed Context:** Link errors to distributed traces across services
- **Root Cause Analysis:** Navigate from error to originating request span
- **Error Sampling:** Sample high-cardinality errors while preserving trace context
- **Cross-Service Debugging:** Track errors through microservice call chains

#### Pattern 1: Propagating Trace Context in Exceptions

```python
# File: src/core/tracing_exceptions.py
from typing import Optional, Any
from opentelemetry import trace
from opentelemetry.trace import Status, StatusCode
import structlog

logger = structlog.get_logger(__name__)
tracer = trace.get_tracer(__name__)

class TraceableException(Exception):
    """
    Exception that captures trace context for distributed debugging.

    Automatically captures:
    - Trace ID (request identifier across services)
    - Span ID (current operation identifier)
    - Parent Span ID (caller operation)
    - Trace flags (sampling decision)
    """

    def __init__(
        self,
        message: str,
        error_code: str,
        status_code: int = 500,
        details: Optional[dict[str, Any]] = None
    ) -> None:
        self.message = message
        self.error_code = error_code
        self.status_code = status_code
        self.details = details or {}

        # Capture current span context
        current_span = trace.get_current_span()
        span_context = current_span.get_span_context()

        if span_context.is_valid:
            self.trace_id = format(span_context.trace_id, '032x')
            self.span_id = format(span_context.span_id, '016x')
            self.trace_flags = span_context.trace_flags

            # Record exception on span
            current_span.record_exception(self)
            current_span.set_status(Status(StatusCode.ERROR, message))

            # Add trace context to exception details
            self.details['trace_id'] = self.trace_id
            self.details['span_id'] = self.span_id
        else:
            self.trace_id = None
            self.span_id = None
            self.trace_flags = None

        super().__init__(self.message)

        logger.error(
            "traceable_exception",
            error_code=error_code,
            message=message,
            status_code=status_code,
            trace_id=self.trace_id,
            span_id=self.span_id,
            details=details
        )

class TraceableResourceNotFound(TraceableException):
    """Resource not found with trace context."""

    def __init__(
        self,
        resource_type: str,
        resource_id: int | str,
        details: Optional[dict[str, Any]] = None
    ) -> None:
        error_details = details or {}
        error_details.update({
            "resource_type": resource_type,
            "resource_id": str(resource_id)
        })

        super().__init__(
            message=f"{resource_type} with ID {resource_id} not found",
            error_code="RESOURCE_NOT_FOUND",
            status_code=404,
            details=error_details
        )
```

#### Pattern 2: Linking Errors to Spans

```python
# File: src/api/routes/traced_resources.py
from fastapi import APIRouter, Depends, HTTPException, status
from opentelemetry import trace
from opentelemetry.trace import Status, StatusCode
from src.core.tracing_exceptions import TraceableResourceNotFound
from src.domain.models.resource import Resource
from src.infrastructure.database.repository import Repository
from sqlalchemy.ext.asyncio import AsyncSession
from src.infrastructure.database.session import get_session
import structlog

router = APIRouter()
logger = structlog.get_logger(__name__)
tracer = trace.get_tracer(__name__)

@router.get("/resources/{resource_id}", response_model=dict)
async def get_resource_with_tracing(
    resource_id: int,
    session: AsyncSession = Depends(get_session)
):
    """
    Get resource with distributed tracing.

    Errors automatically linked to trace spans:
    - Exception recorded on span
    - Span status set to ERROR
    - Trace ID propagated in error response
    """
    with tracer.start_as_current_span(
        "get_resource",
        attributes={
            "resource.id": resource_id,
            "db.system": "postgresql",
            "db.operation": "select"
        }
    ) as span:
        try:
            repo = Repository[Resource](session, Resource)
            resource = await repo.get_by_id(resource_id)

            if not resource:
                # Exception automatically captured on span
                raise TraceableResourceNotFound(
                    resource_type="Resource",
                    resource_id=resource_id
                )

            # Add success attributes
            span.set_attribute("resource.name", resource.name)
            span.set_attribute("resource.type", resource.type)
            span.set_status(Status(StatusCode.OK))

            logger.info(
                "resource_retrieved",
                resource_id=resource_id,
                trace_id=format(span.get_span_context().trace_id, '032x')
            )

            return {
                "id": resource.id,
                "name": resource.name,
                "type": resource.type,
                "trace_id": format(span.get_span_context().trace_id, '032x')
            }

        except TraceableResourceNotFound:
            # Exception already recorded on span
            raise
        except Exception as e:
            # Unexpected exception - record on span
            span.record_exception(e)
            span.set_status(Status(StatusCode.ERROR, str(e)))
            logger.exception(
                "unexpected_error",
                resource_id=resource_id,
                trace_id=format(span.get_span_context().trace_id, '032x')
            )
            raise
```

#### Pattern 3: Error Sampling Strategies

```python
# File: src/core/tracing_config.py
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.sampling import (
    Sampler,
    SamplingResult,
    Decision,
    ParentBased,
    TraceIdRatioBased
)
from opentelemetry.trace import SpanKind, Link
from typing import Optional, Sequence, Mapping
import structlog

logger = structlog.get_logger(__name__)

class ErrorAwareSampler(Sampler):
    """
    Custom sampler that always samples traces with errors.

    Sampling strategy:
    - Always sample if span has error status
    - Always sample if error attribute present
    - Otherwise use ratio-based sampling (e.g., 10%)
    """

    def __init__(self, base_sampler: Sampler):
        self.base_sampler = base_sampler

    def should_sample(
        self,
        parent_context: Optional[trace.SpanContext],
        trace_id: int,
        name: str,
        kind: Optional[SpanKind] = None,
        attributes: Optional[Mapping[str, Any]] = None,
        links: Optional[Sequence[Link]] = None,
        trace_state: Optional[trace.TraceState] = None
    ) -> SamplingResult:
        """
        Decide whether to sample span.

        Always samples if:
        - Attributes contain 'error' key
        - Attributes contain 'exception.type'
        - Span name contains 'error' or 'exception'
        """
        attributes = attributes or {}

        # Always sample errors
        if any(key in attributes for key in ('error', 'exception.type', 'error.type')):
            logger.debug(
                "error_span_sampled",
                span_name=name,
                trace_id=format(trace_id, '032x')
            )
            return SamplingResult(
                decision=Decision.RECORD_AND_SAMPLE,
                attributes=attributes,
                trace_state=trace_state
            )

        # Always sample if span name indicates error
        if 'error' in name.lower() or 'exception' in name.lower():
            return SamplingResult(
                decision=Decision.RECORD_AND_SAMPLE,
                attributes=attributes,
                trace_state=trace_state
            )

        # Use base sampler for normal spans
        return self.base_sampler.should_sample(
            parent_context, trace_id, name, kind, attributes, links, trace_state
        )

    def get_description(self) -> str:
        return f"ErrorAwareSampler({self.base_sampler.get_description()})"

def configure_error_aware_tracing() -> TracerProvider:
    """
    Configure OpenTelemetry with error-aware sampling.

    Ensures all error traces captured while sampling 10% of normal traffic.
    """
    # Base sampler: 10% of normal traffic
    base_sampler = TraceIdRatioBased(0.1)

    # Error-aware sampler: always sample errors + 10% base
    error_sampler = ErrorAwareSampler(base_sampler)

    # Parent-based: respect parent sampling decision
    sampler = ParentBased(root=error_sampler)

    provider = TracerProvider(sampler=sampler)
    trace.set_tracer_provider(provider)

    logger.info("error_aware_tracing_configured", base_sample_rate=0.1)

    return provider
```

**✅ Benefits:**
- **Full Error Context:** Every error includes trace ID for debugging
- **Cross-Service Correlation:** Track errors through microservice boundaries
- **Intelligent Sampling:** Capture all errors without storing all traces
- **Root Cause Analysis:** Navigate from error to originating request

**❌ Drawbacks:**
- **Trace Overhead:** Adding trace context to exceptions adds 100-500μs
- **Storage Cost:** Error-aware sampling increases trace storage by 20-40%
- **Complexity:** Requires OpenTelemetry SDK integration

**Use When:**
- Building distributed systems (multiple microservices)
- Debugging cross-service errors
- Need to correlate logs with traces
- Compliance requires error traceability

---

## 10. Telemetry and Observability

### 10.1 Recommended Approach: OpenTelemetry with Prometheus and FastAPI

OpenTelemetry provides vendor-neutral instrumentation for metrics, traces, and logs[^42]. Combined with Prometheus for metrics collection and Jaeger/Tempo for trace visualization, this approach delivers production-grade observability without vendor lock-in[^43].

**Core Benefits:**
- **Vendor Neutral:** Export to any backend (Prometheus, Jaeger, Datadog, New Relic)
- **Automatic Instrumentation:** FastAPI integration captures HTTP metrics automatically
- **Distributed Tracing:** Track requests across microservice boundaries
- **Custom Metrics:** Business metrics (user signups, revenue, etc.) alongside system metrics
- **Standardized:** CNCF standard, supported by all major observability vendors

**Architecture:**
```
FastAPI Application
    ├─ OpenTelemetry SDK (instrumentation)
    │   ├─ Trace Exporter → Jaeger/Tempo (distributed tracing)
    │   ├─ Metrics Exporter → Prometheus (metrics collection)
    │   └─ Logs Exporter → Loki/CloudWatch (log aggregation)
    │
    ├─ Prometheus Client (custom metrics)
    │   └─ /metrics endpoint (Prometheus scraping)
    │
    └─ Structlog (structured logging with trace context)
```

### 10.2 Implementation Examples

#### Pattern 1: OpenTelemetry Initialization with FastAPI

```python
# File: src/core/telemetry.py
from opentelemetry import trace, metrics
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk.resources import Resource, SERVICE_NAME, SERVICE_VERSION
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from opentelemetry.instrumentation.redis import RedisInstrumentor
from fastapi import FastAPI
from sqlalchemy.ext.asyncio import AsyncEngine
from redis.asyncio import Redis
import structlog
from typing import Optional

logger = structlog.get_logger(__name__)

class TelemetryManager:
    """
    Centralized telemetry management for OpenTelemetry.

    Responsibilities:
    - Initialize OpenTelemetry SDK (tracer, meter)
    - Configure exporters (OTLP, Prometheus)
    - Auto-instrument FastAPI, SQLAlchemy, Redis
    - Provide custom metric recorders
    """

    def __init__(
        self,
        service_name: str,
        service_version: str,
        otlp_endpoint: Optional[str] = None,
        enable_console_export: bool = False
    ):
        self.service_name = service_name
        self.service_version = service_version
        self.otlp_endpoint = otlp_endpoint
        self.enable_console_export = enable_console_export

        # Resource attributes (service metadata)
        self.resource = Resource.create({
            SERVICE_NAME: service_name,
            SERVICE_VERSION: service_version,
            "deployment.environment": "production"
        })

        # Tracer and meter (initialized in setup)
        self.tracer: Optional[trace.Tracer] = None
        self.meter: Optional[metrics.Meter] = None

    def setup_tracing(self) -> None:
        """
        Initialize OpenTelemetry tracing with OTLP exporter.

        Exports traces to Jaeger/Tempo via OTLP gRPC.
        """
        provider = TracerProvider(resource=self.resource)

        # OTLP exporter (Jaeger/Tempo)
        if self.otlp_endpoint:
            otlp_exporter = OTLPSpanExporter(endpoint=self.otlp_endpoint, insecure=True)
            provider.add_span_processor(BatchSpanProcessor(otlp_exporter))
            logger.info("otlp_trace_exporter_configured", endpoint=self.otlp_endpoint)

        # Console exporter (development only)
        if self.enable_console_export:
            from opentelemetry.sdk.trace.export import ConsoleSpanExporter
            console_exporter = ConsoleSpanExporter()
            provider.add_span_processor(BatchSpanProcessor(console_exporter))
            logger.info("console_trace_exporter_configured")

        trace.set_tracer_provider(provider)
        self.tracer = trace.get_tracer(__name__)

        logger.info(
            "tracing_initialized",
            service_name=self.service_name,
            service_version=self.service_version
        )

    def setup_metrics(self) -> None:
        """
        Initialize OpenTelemetry metrics with OTLP exporter.

        Exports metrics to Prometheus via OTLP.
        """
        # OTLP metric exporter
        if self.otlp_endpoint:
            otlp_exporter = OTLPMetricExporter(endpoint=self.otlp_endpoint, insecure=True)
            reader = PeriodicExportingMetricReader(otlp_exporter, export_interval_millis=60000)
            provider = MeterProvider(resource=self.resource, metric_readers=[reader])

            metrics.set_meter_provider(provider)
            self.meter = metrics.get_meter(__name__)

            logger.info("metrics_initialized", otlp_endpoint=self.otlp_endpoint)
        else:
            logger.warning("metrics_not_configured", reason="otlp_endpoint_not_provided")

    def instrument_fastapi(self, app: FastAPI) -> None:
        """
        Auto-instrument FastAPI application.

        Captures:
        - HTTP request/response metrics (latency, status codes)
        - Distributed trace spans per request
        - Exception tracking
        """
        FastAPIInstrumentor.instrument_app(app)
        logger.info("fastapi_instrumented", app_name=app.title)

    def instrument_sqlalchemy(self, engine: AsyncEngine) -> None:
        """
        Auto-instrument SQLAlchemy engine.

        Captures:
        - Database query spans
        - Query duration
        - Connection pool metrics
        """
        SQLAlchemyInstrumentor().instrument(engine=engine.sync_engine)
        logger.info("sqlalchemy_instrumented")

    def instrument_redis(self, redis_client: Redis) -> None:
        """
        Auto-instrument Redis client.

        Captures:
        - Redis command spans
        - Command duration
        - Connection metrics
        """
        RedisInstrumentor().instrument(redis_client=redis_client)
        logger.info("redis_instrumented")

# Global telemetry instance
telemetry: Optional[TelemetryManager] = None

def get_telemetry() -> TelemetryManager:
    """Get global telemetry manager instance."""
    if telemetry is None:
        raise RuntimeError("Telemetry not initialized. Call setup_telemetry() first.")
    return telemetry

def setup_telemetry(
    service_name: str,
    service_version: str,
    otlp_endpoint: Optional[str] = None,
    enable_console_export: bool = False
) -> TelemetryManager:
    """
    Initialize global telemetry manager.

    Call during application startup (lifespan event).
    """
    global telemetry

    telemetry = TelemetryManager(
        service_name=service_name,
        service_version=service_version,
        otlp_endpoint=otlp_endpoint,
        enable_console_export=enable_console_export
    )

    telemetry.setup_tracing()
    telemetry.setup_metrics()

    return telemetry
```

**Usage in FastAPI application:**

```python
# File: src/main.py
from fastapi import FastAPI
from contextlib import asynccontextmanager
from src.core.telemetry import setup_telemetry, get_telemetry
from src.core.config import get_settings
from src.infrastructure.database.session import get_engine
from src.infrastructure.cache.redis_client import get_redis_client
import structlog

logger = structlog.get_logger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan with telemetry initialization."""
    settings = get_settings()

    # Initialize telemetry
    telemetry = setup_telemetry(
        service_name=settings.app_name,
        service_version="1.0.0",
        otlp_endpoint=settings.otlp_endpoint,  # e.g., "http://localhost:4317"
        enable_console_export=settings.debug
    )

    # Auto-instrument FastAPI
    telemetry.instrument_fastapi(app)

    # Auto-instrument database
    engine = get_engine()
    telemetry.instrument_sqlalchemy(engine)

    # Auto-instrument Redis
    redis_client = await get_redis_client()
    telemetry.instrument_redis(redis_client)

    logger.info("application_started", telemetry_enabled=True)

    yield

    logger.info("application_shutdown")

app = FastAPI(
    title="AI Agent MCP Server",
    version="1.0.0",
    lifespan=lifespan
)
```

#### Pattern 2: Custom Business Metrics with Prometheus

```python
# File: src/core/metrics.py
from prometheus_client import Counter, Histogram, Gauge, Info
from typing import Optional
import structlog

logger = structlog.get_logger(__name__)

# HTTP request metrics (automatic via OpenTelemetry, but can define custom)
http_requests_total = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

http_request_duration_seconds = Histogram(
    'http_request_duration_seconds',
    'HTTP request latency',
    ['method', 'endpoint'],
    buckets=[0.01, 0.05, 0.1, 0.5, 1.0, 5.0]
)

# Business metrics
resources_created_total = Counter(
    'resources_created_total',
    'Total resources created',
    ['resource_type']
)

resource_operations_duration_seconds = Histogram(
    'resource_operations_duration_seconds',
    'Duration of resource operations',
    ['operation', 'resource_type'],
    buckets=[0.001, 0.01, 0.05, 0.1, 0.5, 1.0]
)

active_resources = Gauge(
    'active_resources_total',
    'Number of active resources',
    ['resource_type']
)

cache_operations_total = Counter(
    'cache_operations_total',
    'Total cache operations',
    ['operation', 'status']
)

cache_hit_ratio = Gauge(
    'cache_hit_ratio',
    'Cache hit ratio (hits / total requests)'
)

database_connection_pool_size = Gauge(
    'database_connection_pool_size',
    'Database connection pool size',
    ['state']  # state: idle, active
)

# Application info
app_info = Info(
    'app_info',
    'Application information'
)

def initialize_metrics(app_name: str, version: str, environment: str) -> None:
    """
    Initialize application metrics.

    Call during startup to set application info.
    """
    app_info.info({
        'app_name': app_name,
        'version': version,
        'environment': environment
    })

    logger.info(
        "metrics_initialized",
        app_name=app_name,
        version=version,
        environment=environment
    )

class MetricsRecorder:
    """Helper class for recording business metrics."""

    @staticmethod
    def record_resource_created(resource_type: str) -> None:
        """Record resource creation."""
        resources_created_total.labels(resource_type=resource_type).inc()
        logger.debug("metric_recorded", metric="resources_created", resource_type=resource_type)

    @staticmethod
    def record_resource_operation(
        operation: str,
        resource_type: str,
        duration_seconds: float
    ) -> None:
        """Record resource operation duration."""
        resource_operations_duration_seconds.labels(
            operation=operation,
            resource_type=resource_type
        ).observe(duration_seconds)

        logger.debug(
            "metric_recorded",
            metric="resource_operation_duration",
            operation=operation,
            duration_seconds=duration_seconds
        )

    @staticmethod
    def update_active_resources(resource_type: str, count: int) -> None:
        """Update active resource count."""
        active_resources.labels(resource_type=resource_type).set(count)

    @staticmethod
    def record_cache_operation(operation: str, status: str) -> None:
        """Record cache operation (hit, miss, set, delete)."""
        cache_operations_total.labels(operation=operation, status=status).inc()
```

**Expose Prometheus metrics endpoint:**

```python
# File: src/api/routes/metrics.py
from fastapi import APIRouter
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
from starlette.responses import Response

router = APIRouter()

@router.get("/metrics")
async def get_metrics():
    """
    Prometheus metrics endpoint.

    Exposes all registered Prometheus metrics in Prometheus text format.
    Scraped by Prometheus server (typically every 15-60 seconds).
    """
    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST
    )
```

### 10.2.1 Telemetry Initialization Patterns

#### Pattern 1: Auto-Instrumentation (Recommended for Most Cases)

```python
# File: src/core/auto_telemetry.py
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from opentelemetry.instrumentation.redis import RedisInstrumentor
from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor
from fastapi import FastAPI
from sqlalchemy.ext.asyncio import AsyncEngine
from redis.asyncio import Redis
import structlog

logger = structlog.get_logger(__name__)

def auto_instrument_all(
    app: FastAPI,
    db_engine: AsyncEngine,
    redis_client: Redis
) -> None:
    """
    Auto-instrument all components with OpenTelemetry.

    Zero-code instrumentation for:
    - FastAPI (HTTP requests/responses)
    - SQLAlchemy (database queries)
    - Redis (cache operations)
    - HTTPX (external HTTP calls)
    """
    # FastAPI auto-instrumentation
    FastAPIInstrumentor.instrument_app(app)
    logger.info("fastapi_auto_instrumented")

    # SQLAlchemy auto-instrumentation
    SQLAlchemyInstrumentor().instrument(engine=db_engine.sync_engine)
    logger.info("sqlalchemy_auto_instrumented")

    # Redis auto-instrumentation
    RedisInstrumentor().instrument(redis_client=redis_client)
    logger.info("redis_auto_instrumented")

    # HTTPX auto-instrumentation (external API calls)
    HTTPXClientInstrumentor().instrument()
    logger.info("httpx_auto_instrumented")
```

#### Pattern 2: Manual Instrumentation (Fine-Grained Control)

```python
# File: src/api/routes/traced_endpoints.py
from fastapi import APIRouter, Depends
from opentelemetry import trace
from opentelemetry.trace import Status, StatusCode
from src.infrastructure.database.repository import Repository
from src.domain.models.resource import Resource
from sqlalchemy.ext.asyncio import AsyncSession
from src.infrastructure.database.session import get_session
import structlog
import time

router = APIRouter()
logger = structlog.get_logger(__name__)
tracer = trace.get_tracer(__name__)

@router.post("/resources/batch")
async def create_resources_batch(
    resources: list[dict],
    session: AsyncSession = Depends(get_session)
):
    """
    Create multiple resources with manual tracing.

    Manual instrumentation provides:
    - Custom span names
    - Business-specific attributes
    - Nested span hierarchy
    """
    with tracer.start_as_current_span(
        "create_resources_batch",
        attributes={"batch_size": len(resources)}
    ) as batch_span:
        repo = Repository[Resource](session, Resource)
        created_resources = []

        for idx, resource_data in enumerate(resources):
            # Create child span for each resource
            with tracer.start_as_current_span(
                f"create_resource_{idx}",
                attributes={
                    "resource.name": resource_data.get("name"),
                    "resource.type": resource_data.get("type")
                }
            ) as resource_span:
                start_time = time.time()

                try:
                    new_resource = Resource(**resource_data)
                    created = await repo.create(new_resource)
                    created_resources.append(created)

                    resource_span.set_attribute("resource.id", created.id)
                    resource_span.set_status(Status(StatusCode.OK))

                except Exception as e:
                    resource_span.record_exception(e)
                    resource_span.set_status(Status(StatusCode.ERROR, str(e)))
                    raise
                finally:
                    duration = time.time() - start_time
                    resource_span.set_attribute("duration_ms", duration * 1000)

        await session.commit()

        batch_span.set_attribute("resources_created", len(created_resources))
        batch_span.set_status(Status(StatusCode.OK))

        logger.info(
            "batch_resources_created",
            batch_size=len(resources),
            created_count=len(created_resources)
        )

        return {"created": len(created_resources)}
```

#### Pattern 3: Prometheus Metrics Integration

```python
# File: src/api/middleware/metrics_middleware.py
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from src.core.metrics import (
    http_requests_total,
    http_request_duration_seconds,
    MetricsRecorder
)
import time
import structlog

logger = structlog.get_logger(__name__)

class PrometheusMetricsMiddleware(BaseHTTPMiddleware):
    """
    Middleware to record Prometheus metrics for HTTP requests.

    Records:
    - Request count by method, endpoint, status
    - Request duration by method, endpoint
    """

    async def dispatch(self, request: Request, call_next):
        # Record request start time
        start_time = time.time()

        # Extract request metadata
        method = request.method
        endpoint = request.url.path

        try:
            # Process request
            response = await call_next(request)
            status_code = response.status_code

            # Record metrics
            http_requests_total.labels(
                method=method,
                endpoint=endpoint,
                status=status_code
            ).inc()

            duration = time.time() - start_time
            http_request_duration_seconds.labels(
                method=method,
                endpoint=endpoint
            ).observe(duration)

            logger.debug(
                "http_request_completed",
                method=method,
                endpoint=endpoint,
                status_code=status_code,
                duration_seconds=duration
            )

            return response

        except Exception as e:
            # Record error metrics
            http_requests_total.labels(
                method=method,
                endpoint=endpoint,
                status=500
            ).inc()

            logger.error(
                "http_request_failed",
                method=method,
                endpoint=endpoint,
                error=str(e)
            )
            raise
```

#### Pattern 4: Hybrid Approach (Auto + Manual)

```python
# File: src/main.py (hybrid telemetry)
from fastapi import FastAPI
from contextlib import asynccontextmanager
from src.core.telemetry import setup_telemetry
from src.core.auto_telemetry import auto_instrument_all
from src.core.metrics import initialize_metrics
from src.api.middleware.metrics_middleware import PrometheusMetricsMiddleware
from src.infrastructure.database.session import get_engine
from src.infrastructure.cache.redis_client import get_redis_client
import structlog

logger = structlog.get_logger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Hybrid telemetry: auto-instrumentation + custom metrics."""

    # 1. Initialize OpenTelemetry (auto-instrumentation)
    telemetry = setup_telemetry(
        service_name="ai-agent-mcp-server",
        service_version="1.0.0",
        otlp_endpoint="http://localhost:4317"
    )

    # 2. Auto-instrument components
    engine = get_engine()
    redis_client = await get_redis_client()
    auto_instrument_all(app, engine, redis_client)

    # 3. Initialize custom Prometheus metrics
    initialize_metrics(
        app_name="ai-agent-mcp-server",
        version="1.0.0",
        environment="production"
    )

    logger.info("hybrid_telemetry_initialized")

    yield

    logger.info("application_shutdown")

app = FastAPI(title="AI Agent MCP Server", lifespan=lifespan)

# Add Prometheus metrics middleware (custom)
app.add_middleware(PrometheusMetricsMiddleware)
```

### 10.2.2 Common Telemetry Mistakes

#### Mistake 1: Missing Trace Context Propagation

**❌ Incorrect:**
```python
# Trace context NOT propagated to background tasks
from fastapi import BackgroundTasks

async def process_resource(resource_id: int):
    # This runs without trace context - can't correlate with parent request
    await heavy_processing(resource_id)

@app.post("/resources/{resource_id}/process")
async def trigger_processing(
    resource_id: int,
    background_tasks: BackgroundTasks
):
    background_tasks.add_task(process_resource, resource_id)
    return {"status": "processing"}
```

**✅ Correct:**
```python
# Explicitly propagate trace context to background tasks
from fastapi import BackgroundTasks
from opentelemetry import trace, context
from opentelemetry.context import attach, detach

async def process_resource(resource_id: int, trace_context: dict):
    # Restore trace context in background task
    token = attach(trace_context)

    try:
        tracer = trace.get_tracer(__name__)
        with tracer.start_as_current_span("background_processing"):
            await heavy_processing(resource_id)
    finally:
        detach(token)

@app.post("/resources/{resource_id}/process")
async def trigger_processing(
    resource_id: int,
    background_tasks: BackgroundTasks
):
    # Capture current trace context
    current_context = context.get_current()

    background_tasks.add_task(process_resource, resource_id, current_context)
    return {"status": "processing"}
```

#### Mistake 2: High-Cardinality Metric Labels

**❌ Incorrect:**
```python
# User ID as label creates millions of unique metric series
requests_by_user = Counter(
    'requests_by_user_total',
    'Requests by user',
    ['user_id']  # PROBLEM: unbounded cardinality
)

@app.get("/resources/{resource_id}")
async def get_resource(resource_id: int, user_id: int):
    requests_by_user.labels(user_id=user_id).inc()  # Memory explosion
```

**✅ Correct:**
```python
# Use low-cardinality labels (user_type instead of user_id)
requests_by_user_type = Counter(
    'requests_by_user_type_total',
    'Requests by user type',
    ['user_type']  # Low cardinality: admin, premium, free
)

@app.get("/resources/{resource_id}")
async def get_resource(resource_id: int, user_id: int, user_type: str):
    requests_by_user_type.labels(user_type=user_type).inc()  # Safe

    # Log high-cardinality data instead
    logger.info("resource_accessed", resource_id=resource_id, user_id=user_id)
```

#### Mistake 3: Missing Correlation IDs in Logs and Traces

**❌ Incorrect:**
```python
# Logs and traces not correlated
@app.get("/resources/{resource_id}")
async def get_resource(resource_id: int):
    logger.info("fetching_resource", resource_id=resource_id)  # No trace ID

    with tracer.start_as_current_span("get_resource"):
        resource = await fetch_resource(resource_id)

    return resource
```

**✅ Correct:**
```python
# Inject trace ID into logs for correlation
from opentelemetry import trace

@app.get("/resources/{resource_id}")
async def get_resource(resource_id: int):
    # Get current trace context
    span = trace.get_current_span()
    trace_id = format(span.get_span_context().trace_id, '032x')

    # Log with trace ID for correlation
    logger.info(
        "fetching_resource",
        resource_id=resource_id,
        trace_id=trace_id
    )

    with tracer.start_as_current_span("get_resource"):
        resource = await fetch_resource(resource_id)

    return resource
```

### 10.2.3 Verification and Troubleshooting

#### Health Check Endpoint with Telemetry Status

```python
# File: src/api/routes/health.py
from fastapi import APIRouter
from opentelemetry import trace, metrics
from prometheus_client import REGISTRY
import structlog

router = APIRouter()
logger = structlog.get_logger(__name__)

@router.get("/health/telemetry")
async def telemetry_health():
    """
    Check telemetry system health.

    Verifies:
    - OpenTelemetry tracer configured
    - OpenTelemetry meter configured
    - Prometheus metrics registered
    """
    health_status = {
        "status": "healthy",
        "checks": {}
    }

    # Check tracer
    try:
        tracer_provider = trace.get_tracer_provider()
        health_status["checks"]["tracer"] = {
            "status": "ok",
            "provider": str(type(tracer_provider).__name__)
        }
    except Exception as e:
        health_status["checks"]["tracer"] = {"status": "error", "error": str(e)}
        health_status["status"] = "degraded"

    # Check meter
    try:
        meter_provider = metrics.get_meter_provider()
        health_status["checks"]["meter"] = {
            "status": "ok",
            "provider": str(type(meter_provider).__name__)
        }
    except Exception as e:
        health_status["checks"]["meter"] = {"status": "error", "error": str(e)}
        health_status["status"] = "degraded"

    # Check Prometheus metrics
    try:
        metric_count = len(list(REGISTRY.collect()))
        health_status["checks"]["prometheus"] = {
            "status": "ok",
            "registered_metrics": metric_count
        }
    except Exception as e:
        health_status["checks"]["prometheus"] = {"status": "error", "error": str(e)}
        health_status["status"] = "degraded"

    return health_status
```

### 10.3 Alternative Approaches

| Approach | Traces | Metrics | Logs | Vendor Lock-in | Complexity |
|----------|--------|---------|------|----------------|------------|
| **OpenTelemetry + Prometheus** | ✅ Jaeger/Tempo | ✅ Prometheus | ✅ Loki/CloudWatch | None | Medium |
| **Datadog APM** | ✅ Datadog | ✅ Datadog | ✅ Datadog | High | Low |
| **New Relic** | ✅ New Relic | ✅ New Relic | ✅ New Relic | High | Low |
| **AWS CloudWatch** | ✅ X-Ray | ✅ CloudWatch | ✅ CloudWatch | High (AWS) | Low |
| **Elastic APM** | ✅ Elastic APM | ✅ Elasticsearch | ✅ Elasticsearch | Medium | Medium |
| **Prometheus Only** | ❌ None | ✅ Prometheus | ❌ None | None | Low |

### 10.4 Decision Criteria

**Use OpenTelemetry + Prometheus when:**
- Need vendor-neutral observability (avoid lock-in)
- Building distributed systems (microservices)
- Want to switch backends without code changes
- Open-source preference (CNCF projects)

**Use Managed APM (Datadog, New Relic) when:**
- Need turnkey solution (zero infrastructure management)
- Budget allows for per-host pricing
- Want advanced features (AI-powered anomaly detection)
- Small team (no dedicated observability engineers)

**Use AWS CloudWatch when:**
- Already on AWS (native integration)
- Cost-conscious (pay-per-use vs. per-host)
- Need AWS-specific integrations (Lambda, ECS, RDS)

### 10.5 OpenTelemetry Logging Integration with Structlog

OpenTelemetry supports automatic trace context injection into logs, enabling correlation between logs, traces, and metrics[^51]. Integrating structlog with OTeL provides structured logs with automatic trace/span ID enrichment[^52].

**Key Benefits:**
- **Automatic Trace Context:** Every log includes trace_id and span_id
- **Correlated Debugging:** Jump from trace span to related logs instantly
- **Structured Output:** JSON logs with consistent fields across services
- **Zero Manual Work:** Context propagation happens automatically

#### Pattern 1: Structlog with OpenTelemetry Processor

```python
# File: src/core/logging.py
import structlog
from opentelemetry import trace
from typing import Any
import sys

def add_opentelemetry_context(
    logger: Any,
    method_name: str,
    event_dict: dict
) -> dict:
    """
    Structlog processor to inject OpenTelemetry trace context.

    Adds trace_id and span_id to every log entry automatically.
    """
    span = trace.get_current_span()
    if span and span.is_recording():
        ctx = span.get_span_context()
        if ctx.is_valid:
            # Add trace context in W3C format (32-char hex)
            event_dict["trace_id"] = format(ctx.trace_id, "032x")
            event_dict["span_id"] = format(ctx.span_id, "016x")
            event_dict["trace_flags"] = f"{ctx.trace_flags:02x}"

    return event_dict

def setup_structured_logging(
    service_name: str,
    log_level: str = "INFO",
    json_output: bool = True
) -> None:
    """
    Configure structlog with OpenTelemetry integration.

    Processors:
    1. Add timestamp (ISO 8601)
    2. Add log level
    3. Add service name
    4. Add trace context (trace_id, span_id)
    5. Format as JSON or console
    """
    processors = [
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso", utc=True),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        # OpenTelemetry trace context injection
        add_opentelemetry_context,
        # Add service name to every log
        structlog.processors.CallsiteParameterAdder(
            parameters=[
                structlog.processors.CallsiteParameter.FUNC_NAME,
                structlog.processors.CallsiteParameter.LINENO,
            ]
        ),
    ]

    if json_output:
        # Production: JSON output
        processors.append(structlog.processors.JSONRenderer())
    else:
        # Development: Console output with colors
        processors.append(structlog.dev.ConsoleRenderer(colors=True))

    structlog.configure(
        processors=processors,
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    # Configure root logger
    import logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, log_level.upper()),
    )
```

**Usage Example:**

```python
# File: src/api/routes/resources.py
from fastapi import APIRouter, HTTPException
from opentelemetry import trace
import structlog

router = APIRouter()
logger = structlog.get_logger(__name__)
tracer = trace.get_tracer(__name__)

@router.post("/resources")
async def create_resource(resource_data: dict):
    """
    Create resource with automatic trace-correlated logging.

    All logs automatically include trace_id and span_id.
    """
    # Start trace span
    with tracer.start_as_current_span("create_resource") as span:
        span.set_attribute("resource.type", resource_data.get("type"))

        # Log with automatic trace context
        logger.info(
            "creating_resource",
            resource_type=resource_data.get("type"),
            resource_name=resource_data.get("name")
        )
        # Output: {"event": "creating_resource", "trace_id": "abc123...", "span_id": "def456...", ...}

        try:
            # Simulate resource creation
            resource_id = await save_resource(resource_data)

            logger.info(
                "resource_created",
                resource_id=resource_id,
                resource_type=resource_data.get("type")
            )
            # Same trace_id and span_id in this log

            span.set_attribute("resource.id", resource_id)
            return {"id": resource_id, "status": "created"}

        except Exception as e:
            logger.error(
                "resource_creation_failed",
                error=str(e),
                resource_type=resource_data.get("type")
            )
            # Error log has same trace_id - easy debugging

            span.record_exception(e)
            raise HTTPException(status_code=500, detail="Resource creation failed")
```

**Sample Log Output (JSON):**

```json
{
  "event": "creating_resource",
  "timestamp": "2025-11-03T10:15:30.123456Z",
  "level": "info",
  "logger": "src.api.routes.resources",
  "trace_id": "4bf92f3577b34da6a3ce929d0e0e4736",
  "span_id": "00f067aa0ba902b7",
  "trace_flags": "01",
  "resource_type": "file",
  "resource_name": "example.txt",
  "func_name": "create_resource",
  "lineno": 18
}
```

#### Pattern 2: OpenTelemetry Logs API (Beta)

OpenTelemetry Logs API provides native log signal support (currently in beta)[^53].

```python
# File: src/core/otel_logging.py
from opentelemetry._logs import set_logger_provider
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
from opentelemetry.exporter.otlp.proto.grpc._log_exporter import OTLPLogExporter
from opentelemetry.sdk.resources import Resource
import logging
import structlog

def setup_otel_logs(
    service_name: str,
    otlp_endpoint: str,
    resource: Resource
) -> None:
    """
    Configure OpenTelemetry Logs API (beta).

    Exports logs directly to OTLP endpoint (e.g., Grafana Loki, CloudWatch).
    """
    # Create logger provider
    logger_provider = LoggerProvider(resource=resource)

    # Add OTLP log exporter
    otlp_log_exporter = OTLPLogExporter(endpoint=otlp_endpoint, insecure=True)
    logger_provider.add_log_record_processor(
        BatchLogRecordProcessor(otlp_log_exporter)
    )

    set_logger_provider(logger_provider)

    # Configure Python logging to use OTeL handler
    handler = LoggingHandler(
        level=logging.INFO,
        logger_provider=logger_provider
    )

    # Attach to root logger
    logging.getLogger().addHandler(handler)

    structlog.get_logger(__name__).info(
        "otel_logs_configured",
        service_name=service_name,
        otlp_endpoint=otlp_endpoint
    )
```

**Complete Setup Example:**

```python
# File: src/main.py
from fastapi import FastAPI
from contextlib import asynccontextmanager
from src.core.telemetry import setup_telemetry, get_telemetry
from src.core.logging import setup_structured_logging
from src.core.otel_logging import setup_otel_logs
from src.core.config import get_settings
import structlog

logger = structlog.get_logger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup with logging + tracing."""
    settings = get_settings()

    # 1. Setup structured logging (structlog)
    setup_structured_logging(
        service_name=settings.app_name,
        log_level=settings.log_level,
        json_output=not settings.debug
    )

    # 2. Setup OpenTelemetry (traces + metrics)
    telemetry = setup_telemetry(
        service_name=settings.app_name,
        service_version="1.0.0",
        otlp_endpoint=settings.otlp_endpoint
    )

    # 3. Setup OTeL Logs API (optional - beta)
    if settings.enable_otel_logs:
        setup_otel_logs(
            service_name=settings.app_name,
            otlp_endpoint=settings.otlp_endpoint,
            resource=telemetry.resource
        )

    # 4. Instrument FastAPI
    telemetry.instrument_fastapi(app)

    logger.info(
        "application_started",
        service_name=settings.app_name,
        log_level=settings.log_level,
        otel_enabled=True
    )

    yield

    logger.info("application_shutdown")

app = FastAPI(title="AI Agent MCP Server", lifespan=lifespan)
```

#### Pattern 3: Logging Best Practices with OTeL

```python
# File: src/domain/services/resource_service.py
import structlog
from opentelemetry import trace
from typing import Optional
import time

logger = structlog.get_logger(__name__)
tracer = trace.get_tracer(__name__)

class ResourceService:
    """Service with trace-correlated logging best practices."""

    async def process_resource(
        self,
        resource_id: int,
        user_id: int
    ) -> dict:
        """
        Process resource with detailed logging and tracing.

        Best practices:
        1. Log at operation boundaries (start, success, failure)
        2. Include business context (resource_id, user_id)
        3. Use consistent event names (verb_noun pattern)
        4. Add performance metrics (duration)
        5. Leverage automatic trace context
        """
        with tracer.start_as_current_span(
            "process_resource",
            attributes={
                "resource.id": resource_id,
                "user.id": user_id
            }
        ) as span:
            start_time = time.time()

            # Log operation start
            logger.info(
                "processing_resource_started",
                resource_id=resource_id,
                user_id=user_id
            )

            try:
                # Business logic
                resource = await self._fetch_resource(resource_id)

                logger.debug(
                    "resource_fetched",
                    resource_id=resource_id,
                    resource_type=resource.type
                )

                result = await self._transform_resource(resource, user_id)

                duration = time.time() - start_time
                span.set_attribute("processing.duration_ms", duration * 1000)

                # Log success with metrics
                logger.info(
                    "processing_resource_completed",
                    resource_id=resource_id,
                    user_id=user_id,
                    duration_seconds=duration,
                    result_size=len(result)
                )

                return result

            except ValueError as e:
                # Business exception (user error)
                logger.warning(
                    "processing_resource_invalid",
                    resource_id=resource_id,
                    user_id=user_id,
                    error=str(e),
                    error_type="validation_error"
                )
                span.set_attribute("error.type", "validation_error")
                raise

            except Exception as e:
                # System exception (internal error)
                duration = time.time() - start_time
                logger.error(
                    "processing_resource_failed",
                    resource_id=resource_id,
                    user_id=user_id,
                    error=str(e),
                    error_type=type(e).__name__,
                    duration_seconds=duration
                )
                span.record_exception(e)
                span.set_attribute("error", True)
                raise

    async def _fetch_resource(self, resource_id: int) -> dict:
        """Fetch resource with nested span."""
        with tracer.start_as_current_span("fetch_resource") as span:
            span.set_attribute("resource.id", resource_id)

            logger.debug("fetching_resource_from_db", resource_id=resource_id)

            # Simulate DB fetch
            resource = {"id": resource_id, "type": "file", "data": "..."}

            return resource

    async def _transform_resource(self, resource: dict, user_id: int) -> dict:
        """Transform resource with nested span."""
        with tracer.start_as_current_span("transform_resource") as span:
            span.set_attribute("resource.type", resource["type"])
            span.set_attribute("user.id", user_id)

            logger.debug(
                "transforming_resource",
                resource_id=resource["id"],
                resource_type=resource["type"]
            )

            # Simulate transformation
            transformed = {**resource, "processed": True, "user_id": user_id}

            return transformed
```

**Trace-to-Log Correlation Workflow:**

1. **Jaeger Trace View:**
   - Trace ID: `4bf92f3577b34da6a3ce929d0e0e4736`
   - Spans: `process_resource → fetch_resource → transform_resource`
   - Duration: 245ms

2. **Loki/CloudWatch Log Query:**
   ```
   {trace_id="4bf92f3577b34da6a3ce929d0e0e4736"}
   ```
   Returns ALL logs for that trace:
   - `processing_resource_started`
   - `fetching_resource_from_db`
   - `resource_fetched`
   - `transforming_resource`
   - `processing_resource_completed`

3. **Grafana Dashboard:**
   - Click trace span → "View Logs" → Filtered logs for that span_id
   - Click log entry → "View Trace" → Full distributed trace

---

### 10.6 OpenTelemetry Metrics Deep Dive

OpenTelemetry Metrics API provides three core metric types: Counter, Gauge, and Histogram[^54]. Unlike Prometheus client, OTeL metrics support push-based export to OTLP endpoints.

**Metric Types:**

| Type | Use Case | Example | Aggregation |
|------|----------|---------|-------------|
| **Counter** | Monotonically increasing values | Request count, errors, cache hits | Sum |
| **UpDownCounter** | Values that increase/decrease | Active connections, queue size | Sum |
| **Histogram** | Distribution of values | Request latency, payload size | Sum, Count, Buckets |
| **Gauge** | Point-in-time snapshot | CPU usage, memory, temperature | Last Value |

#### Pattern 1: OpenTelemetry Metrics with OTLP Export

```python
# File: src/core/otel_metrics.py
from opentelemetry import metrics
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.sdk.resources import Resource
import structlog

logger = structlog.get_logger(__name__)

class OTelMetricsManager:
    """
    OpenTelemetry Metrics Manager.

    Provides business metrics using OTeL Metrics API.
    Exports to Prometheus, Datadog, or any OTLP-compatible backend.
    """

    def __init__(
        self,
        service_name: str,
        otlp_endpoint: str,
        resource: Resource,
        export_interval_ms: int = 60000
    ):
        # Configure OTLP exporter
        otlp_exporter = OTLPMetricExporter(
            endpoint=otlp_endpoint,
            insecure=True
        )

        # Configure metric reader (export every 60s)
        reader = PeriodicExportingMetricReader(
            otlp_exporter,
            export_interval_millis=export_interval_ms
        )

        # Create meter provider
        provider = MeterProvider(
            resource=resource,
            metric_readers=[reader]
        )

        metrics.set_meter_provider(provider)
        self.meter = metrics.get_meter(__name__)

        # Create metrics
        self._create_metrics()

        logger.info(
            "otel_metrics_configured",
            service_name=service_name,
            otlp_endpoint=otlp_endpoint,
            export_interval_ms=export_interval_ms
        )

    def _create_metrics(self) -> None:
        """Create OpenTelemetry metrics."""

        # Counter: HTTP requests
        self.http_requests_total = self.meter.create_counter(
            name="http.server.requests",
            description="Total HTTP requests",
            unit="1"
        )

        # Histogram: HTTP request duration
        self.http_request_duration = self.meter.create_histogram(
            name="http.server.duration",
            description="HTTP request duration",
            unit="ms"
        )

        # Counter: Resources created
        self.resources_created_total = self.meter.create_counter(
            name="app.resources.created",
            description="Total resources created",
            unit="1"
        )

        # Histogram: Resource operation duration
        self.resource_operation_duration = self.meter.create_histogram(
            name="app.resources.operation.duration",
            description="Resource operation duration",
            unit="ms"
        )

        # UpDownCounter: Active resources
        self.active_resources = self.meter.create_up_down_counter(
            name="app.resources.active",
            description="Number of active resources",
            unit="1"
        )

        # Counter: Cache operations
        self.cache_operations_total = self.meter.create_counter(
            name="app.cache.operations",
            description="Total cache operations",
            unit="1"
        )

        # Gauge: Cache hit ratio (async observable)
        self.cache_hit_ratio = self.meter.create_observable_gauge(
            name="app.cache.hit_ratio",
            description="Cache hit ratio",
            unit="1",
            callbacks=[self._observe_cache_hit_ratio]
        )

        logger.info("otel_metrics_created", metric_count=7)

    def _observe_cache_hit_ratio(self, observer) -> None:
        """
        Callback for observable gauge.

        Called periodically by OTeL SDK to collect current value.
        """
        # Calculate cache hit ratio from cache stats
        from src.infrastructure.cache.redis_client import get_cache_stats

        stats = get_cache_stats()
        if stats["total_requests"] > 0:
            hit_ratio = stats["hits"] / stats["total_requests"]
            observer.observe(hit_ratio, attributes={})

    def record_http_request(
        self,
        method: str,
        endpoint: str,
        status_code: int,
        duration_ms: float
    ) -> None:
        """Record HTTP request metrics."""
        attributes = {
            "http.method": method,
            "http.route": endpoint,
            "http.status_code": status_code
        }

        self.http_requests_total.add(1, attributes=attributes)
        self.http_request_duration.record(duration_ms, attributes=attributes)

    def record_resource_created(self, resource_type: str) -> None:
        """Record resource creation."""
        self.resources_created_total.add(
            1,
            attributes={"resource.type": resource_type}
        )

    def record_resource_operation(
        self,
        operation: str,
        resource_type: str,
        duration_ms: float,
        success: bool
    ) -> None:
        """Record resource operation."""
        attributes = {
            "operation": operation,
            "resource.type": resource_type,
            "success": str(success).lower()
        }

        self.resource_operation_duration.record(duration_ms, attributes=attributes)

    def increment_active_resources(self, resource_type: str, delta: int = 1) -> None:
        """Increment active resources count."""
        self.active_resources.add(delta, attributes={"resource.type": resource_type})

    def decrement_active_resources(self, resource_type: str, delta: int = 1) -> None:
        """Decrement active resources count."""
        self.active_resources.add(-delta, attributes={"resource.type": resource_type})

    def record_cache_operation(self, operation: str, status: str) -> None:
        """Record cache operation (hit, miss, set, delete)."""
        self.cache_operations_total.add(
            1,
            attributes={
                "operation": operation,
                "status": status
            }
        )
```

**Usage Example:**

```python
# File: src/api/routes/resources.py
from fastapi import APIRouter, Depends
from src.core.otel_metrics import OTelMetricsManager
from src.core.telemetry import get_telemetry
import time
import structlog

router = APIRouter()
logger = structlog.get_logger(__name__)

def get_metrics() -> OTelMetricsManager:
    """Dependency to get metrics manager."""
    return get_telemetry().metrics

@router.post("/resources")
async def create_resource(
    resource_data: dict,
    metrics: OTelMetricsManager = Depends(get_metrics)
):
    """Create resource with OTeL metrics."""
    start_time = time.time()
    resource_type = resource_data.get("type")

    try:
        # Business logic
        resource_id = await save_resource(resource_data)

        # Record metrics
        duration_ms = (time.time() - start_time) * 1000
        metrics.record_resource_created(resource_type)
        metrics.record_resource_operation(
            operation="create",
            resource_type=resource_type,
            duration_ms=duration_ms,
            success=True
        )
        metrics.increment_active_resources(resource_type)

        logger.info(
            "resource_created",
            resource_id=resource_id,
            resource_type=resource_type,
            duration_ms=duration_ms
        )

        return {"id": resource_id, "status": "created"}

    except Exception as e:
        duration_ms = (time.time() - start_time) * 1000
        metrics.record_resource_operation(
            operation="create",
            resource_type=resource_type,
            duration_ms=duration_ms,
            success=False
        )

        logger.error(
            "resource_creation_failed",
            resource_type=resource_type,
            error=str(e)
        )
        raise
```

#### Pattern 2: Hybrid Prometheus + OpenTelemetry Metrics

Many teams run Prometheus for metrics storage but want OTeL instrumentation. This hybrid approach uses OTeL for collection and Prometheus for storage[^55].

```python
# File: src/core/hybrid_metrics.py
from opentelemetry import metrics
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.exporter.prometheus import PrometheusMetricReader
from prometheus_client import start_http_server, REGISTRY
from opentelemetry.sdk.resources import Resource
import structlog

logger = structlog.get_logger(__name__)

def setup_hybrid_metrics(
    service_name: str,
    resource: Resource,
    prometheus_port: int = 9090
) -> metrics.Meter:
    """
    Hybrid metrics: OTeL instrumentation + Prometheus export.

    Benefits:
    - Use OTeL Metrics API (vendor-neutral)
    - Export to Prometheus (native /metrics endpoint)
    - No OTLP endpoint required
    """
    # Create Prometheus exporter (pull-based)
    prometheus_reader = PrometheusMetricReader()

    # Create meter provider
    provider = MeterProvider(
        resource=resource,
        metric_readers=[prometheus_reader]
    )

    metrics.set_meter_provider(provider)
    meter = metrics.get_meter(__name__)

    # Start Prometheus HTTP server
    start_http_server(port=prometheus_port, registry=REGISTRY)

    logger.info(
        "hybrid_metrics_configured",
        service_name=service_name,
        prometheus_port=prometheus_port,
        metrics_endpoint=f"http://localhost:{prometheus_port}/metrics"
    )

    return meter
```

**Prometheus Scrape Configuration:**

```yaml
# prometheus.yml
scrape_configs:
  - job_name: 'ai-agent-mcp-server'
    scrape_interval: 15s
    static_configs:
      - targets: ['localhost:9090']
        labels:
          service: 'ai-agent-mcp-server'
          environment: 'production'
```

#### Pattern 3: Custom Observable Metrics (Callbacks)

Observable metrics (gauges) are updated via callbacks, useful for system metrics[^56].

```python
# File: src/core/system_metrics.py
from opentelemetry import metrics
import psutil
import structlog

logger = structlog.get_logger(__name__)

class SystemMetrics:
    """System resource metrics (CPU, memory, disk)."""

    def __init__(self, meter: metrics.Meter):
        self.meter = meter

        # CPU usage (observable gauge)
        self.cpu_usage = self.meter.create_observable_gauge(
            name="system.cpu.usage",
            description="CPU usage percentage",
            unit="%",
            callbacks=[self._observe_cpu_usage]
        )

        # Memory usage (observable gauge)
        self.memory_usage = self.meter.create_observable_gauge(
            name="system.memory.usage",
            description="Memory usage",
            unit="bytes",
            callbacks=[self._observe_memory_usage]
        )

        # Disk usage (observable gauge)
        self.disk_usage = self.meter.create_observable_gauge(
            name="system.disk.usage",
            description="Disk usage",
            unit="bytes",
            callbacks=[self._observe_disk_usage]
        )

        logger.info("system_metrics_configured")

    def _observe_cpu_usage(self, observer) -> None:
        """Observe CPU usage."""
        cpu_percent = psutil.cpu_percent(interval=0.1)
        observer.observe(cpu_percent, attributes={})

    def _observe_memory_usage(self, observer) -> None:
        """Observe memory usage."""
        memory = psutil.virtual_memory()
        observer.observe(
            memory.used,
            attributes={"type": "used"}
        )
        observer.observe(
            memory.available,
            attributes={"type": "available"}
        )

    def _observe_disk_usage(self, observer) -> None:
        """Observe disk usage."""
        disk = psutil.disk_usage('/')
        observer.observe(
            disk.used,
            attributes={"mount": "/", "type": "used"}
        )
        observer.observe(
            disk.free,
            attributes={"mount": "/", "type": "free"}
        )
```

---

### 10.7 OpenTelemetry Distributed Tracing Patterns

Distributed tracing tracks requests across multiple services, providing end-to-end visibility[^57]. OpenTelemetry automatically propagates trace context via HTTP headers (W3C Trace Context standard)[^58].

#### Pattern 1: Automatic FastAPI Instrumentation

```python
# File: src/core/tracing.py
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.resources import Resource
from fastapi import FastAPI
import structlog

logger = structlog.get_logger(__name__)

def setup_tracing(
    service_name: str,
    otlp_endpoint: str,
    resource: Resource
) -> trace.Tracer:
    """
    Setup OpenTelemetry distributed tracing.

    Configuration:
    - OTLP gRPC exporter (Jaeger, Tempo, Datadog)
    - Batch span processor (performance optimization)
    - W3C Trace Context propagation (automatic)
    """
    # Create tracer provider
    provider = TracerProvider(resource=resource)

    # Add OTLP exporter
    otlp_exporter = OTLPSpanExporter(
        endpoint=otlp_endpoint,
        insecure=True
    )
    provider.add_span_processor(BatchSpanProcessor(otlp_exporter))

    # Set global tracer provider
    trace.set_tracer_provider(provider)

    tracer = trace.get_tracer(__name__)

    logger.info(
        "tracing_configured",
        service_name=service_name,
        otlp_endpoint=otlp_endpoint
    )

    return tracer

def instrument_fastapi_tracing(app: FastAPI) -> None:
    """
    Auto-instrument FastAPI with OpenTelemetry.

    Automatic instrumentation:
    - Creates span per HTTP request
    - Captures HTTP method, path, status code
    - Propagates trace context to downstream services
    - Records exceptions as span events
    """
    FastAPIInstrumentor.instrument_app(app)

    logger.info("fastapi_tracing_instrumented", app_title=app.title)
```

**Automatic Span Attributes (FastAPI):**

```
Span Name: GET /resources/{resource_id}
Span Kind: SERVER
Attributes:
  - http.method: GET
  - http.route: /resources/{resource_id}
  - http.url: http://localhost:8000/resources/123
  - http.status_code: 200
  - http.target: /resources/123
  - net.host.name: localhost
  - net.host.port: 8000
```

#### Pattern 2: Manual Span Creation (Fine-Grained Control)

```python
# File: src/domain/services/resource_processor.py
from opentelemetry import trace
from opentelemetry.trace import Status, StatusCode, SpanKind
import structlog
import time

logger = structlog.get_logger(__name__)
tracer = trace.get_tracer(__name__)

class ResourceProcessor:
    """Resource processor with manual tracing."""

    async def process_resource_pipeline(
        self,
        resource_id: int,
        user_id: int
    ) -> dict:
        """
        Process resource through multi-stage pipeline with nested spans.

        Span hierarchy:
        - process_resource_pipeline (root)
          ├─ validate_resource (child)
          ├─ fetch_resource (child)
          ├─ transform_resource (child)
          └─ save_result (child)
        """
        with tracer.start_as_current_span(
            "process_resource_pipeline",
            kind=SpanKind.INTERNAL,
            attributes={
                "resource.id": resource_id,
                "user.id": user_id,
                "pipeline.version": "v2.0"
            }
        ) as root_span:
            start_time = time.time()

            try:
                # Stage 1: Validate
                with tracer.start_as_current_span("validate_resource") as span:
                    span.set_attribute("validation.schema", "v1.2")
                    validation_result = await self._validate_resource(resource_id)
                    span.set_attribute("validation.passed", validation_result)

                    if not validation_result:
                        span.set_status(Status(StatusCode.ERROR, "Validation failed"))
                        raise ValueError("Resource validation failed")

                # Stage 2: Fetch
                with tracer.start_as_current_span("fetch_resource") as span:
                    span.set_attribute("fetch.source", "database")
                    resource = await self._fetch_resource(resource_id)
                    span.set_attribute("resource.type", resource["type"])
                    span.set_attribute("resource.size_bytes", len(str(resource)))

                # Stage 3: Transform
                with tracer.start_as_current_span("transform_resource") as span:
                    span.set_attribute("transform.algorithm", "v2_enhanced")
                    transform_start = time.time()

                    result = await self._transform_resource(resource, user_id)

                    transform_duration = (time.time() - transform_start) * 1000
                    span.set_attribute("transform.duration_ms", transform_duration)
                    span.set_attribute("result.size_bytes", len(str(result)))

                # Stage 4: Save
                with tracer.start_as_current_span("save_result") as span:
                    span.set_attribute("save.destination", "database")
                    saved_id = await self._save_result(result)
                    span.set_attribute("saved.id", saved_id)

                # Record pipeline success
                total_duration = (time.time() - start_time) * 1000
                root_span.set_attribute("pipeline.duration_ms", total_duration)
                root_span.set_attribute("pipeline.status", "success")
                root_span.set_status(Status(StatusCode.OK))

                logger.info(
                    "pipeline_completed",
                    resource_id=resource_id,
                    duration_ms=total_duration
                )

                return result

            except Exception as e:
                # Record exception in span
                root_span.record_exception(e)
                root_span.set_status(Status(StatusCode.ERROR, str(e)))
                root_span.set_attribute("pipeline.status", "failed")
                root_span.set_attribute("error.type", type(e).__name__)

                logger.error(
                    "pipeline_failed",
                    resource_id=resource_id,
                    error=str(e)
                )
                raise

    async def _validate_resource(self, resource_id: int) -> bool:
        """Validate resource (nested span created automatically)."""
        # Validation logic
        return True

    async def _fetch_resource(self, resource_id: int) -> dict:
        """Fetch resource."""
        return {"id": resource_id, "type": "file", "data": "..."}

    async def _transform_resource(self, resource: dict, user_id: int) -> dict:
        """Transform resource."""
        return {**resource, "processed": True, "user_id": user_id}

    async def _save_result(self, result: dict) -> int:
        """Save result."""
        return 12345
```

**Trace Visualization (Jaeger/Tempo):**

```
Trace ID: 4bf92f3577b34da6a3ce929d0e0e4736
Total Duration: 245ms

├─ [245ms] process_resource_pipeline
   ├─ [12ms] validate_resource
   ├─ [85ms] fetch_resource
   ├─ [120ms] transform_resource
   └─ [28ms] save_result

Attributes:
  resource.id: 123
  user.id: 456
  pipeline.version: v2.0
  pipeline.status: success
```

#### Pattern 3: Cross-Service Trace Propagation

OpenTelemetry automatically propagates trace context via HTTP headers when using instrumented HTTP clients[^59].

```python
# File: src/infrastructure/external/api_client.py
from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor
from opentelemetry import trace
import httpx
import structlog

logger = structlog.get_logger(__name__)
tracer = trace.get_tracer(__name__)

# Auto-instrument HTTPX (propagates trace context automatically)
HTTPXClientInstrumentor().instrument()

class ExternalAPIClient:
    """
    External API client with automatic trace propagation.

    Trace context propagated via W3C Trace Context headers:
    - traceparent: 00-{trace_id}-{span_id}-{flags}
    - tracestate: vendor-specific data
    """

    def __init__(self, base_url: str):
        self.base_url = base_url
        self.client = httpx.AsyncClient(base_url=base_url, timeout=30.0)

    async def create_resource(self, resource_data: dict) -> dict:
        """
        Create resource in external service.

        Trace context automatically propagated to downstream service.
        """
        with tracer.start_as_current_span(
            "external_api_create_resource",
            kind=trace.SpanKind.CLIENT,
            attributes={
                "http.method": "POST",
                "http.url": f"{self.base_url}/resources",
                "resource.type": resource_data.get("type")
            }
        ) as span:
            try:
                # HTTPX automatically adds traceparent header
                response = await self.client.post(
                    "/resources",
                    json=resource_data
                )
                response.raise_for_status()

                span.set_attribute("http.status_code", response.status_code)
                span.set_status(Status(StatusCode.OK))

                logger.info(
                    "external_api_request_success",
                    method="POST",
                    url="/resources",
                    status_code=response.status_code
                )

                return response.json()

            except httpx.HTTPStatusError as e:
                span.record_exception(e)
                span.set_attribute("http.status_code", e.response.status_code)
                span.set_status(Status(StatusCode.ERROR, str(e)))

                logger.error(
                    "external_api_request_failed",
                    method="POST",
                    url="/resources",
                    status_code=e.response.status_code,
                    error=str(e)
                )
                raise
```

**Trace Context Propagation Flow:**

```
Service A (AI Agent MCP Server)
  └─ Span: process_resource (trace_id: abc123...)
      └─ HTTP POST /resources (traceparent header sent)

↓ HTTP Request Headers ↓
traceparent: 00-abc123...-def456...-01

Service B (External Resource API)
  └─ Span: handle_create_resource (same trace_id: abc123...)
      └─ Database operation

Trace View (Jaeger):
├─ [Service A] process_resource (245ms)
│   └─ [Service A] external_api_create_resource (180ms)
│       └─ [Service B] handle_create_resource (175ms)
│           └─ [Service B] database_insert (120ms)
```

#### Pattern 4: Span Events and Annotations

Span events add timestamped annotations to spans for key moments[^60].

```python
# File: src/domain/services/batch_processor.py
from opentelemetry import trace
import structlog
import time

logger = structlog.get_logger(__name__)
tracer = trace.get_tracer(__name__)

class BatchProcessor:
    """Batch processor with span events."""

    async def process_batch(self, items: list[dict]) -> dict:
        """
        Process batch with span events for progress tracking.

        Span events capture:
        - Batch validation started/completed
        - Item processing milestones (25%, 50%, 75%, 100%)
        - Errors and retries
        """
        with tracer.start_as_current_span(
            "process_batch",
            attributes={"batch.size": len(items)}
        ) as span:
            # Event: Batch validation started
            span.add_event("batch_validation_started")

            # Validate batch
            await self._validate_batch(items)

            span.add_event(
                "batch_validation_completed",
                attributes={"validation.passed": True}
            )

            processed = 0
            failed = 0

            for idx, item in enumerate(items):
                try:
                    await self._process_item(item)
                    processed += 1

                    # Event: Progress milestones
                    progress = (idx + 1) / len(items) * 100
                    if progress in [25, 50, 75, 100]:
                        span.add_event(
                            f"batch_progress_{int(progress)}pct",
                            attributes={"processed_count": processed}
                        )

                except Exception as e:
                    failed += 1

                    # Event: Item processing failed
                    span.add_event(
                        "item_processing_failed",
                        attributes={
                            "item.index": idx,
                            "error.type": type(e).__name__,
                            "error.message": str(e)
                        }
                    )

                    logger.warning(
                        "batch_item_failed",
                        item_index=idx,
                        error=str(e)
                    )

            # Final span attributes
            span.set_attribute("batch.processed", processed)
            span.set_attribute("batch.failed", failed)
            span.set_attribute("batch.success_rate", processed / len(items))

            logger.info(
                "batch_completed",
                batch_size=len(items),
                processed=processed,
                failed=failed
            )

            return {"processed": processed, "failed": failed}

    async def _validate_batch(self, items: list[dict]) -> None:
        """Validate batch."""
        pass

    async def _process_item(self, item: dict) -> None:
        """Process single item."""
        pass
```

**Span Events Timeline (Jaeger):**

```
Span: process_batch (duration: 1.2s)

Timeline:
0.000s - Span Start
0.050s - Event: batch_validation_started
0.120s - Event: batch_validation_completed (validation.passed=true)
0.300s - Event: batch_progress_25pct (processed_count=25)
0.600s - Event: batch_progress_50pct (processed_count=50)
0.750s - Event: item_processing_failed (item.index=67, error.type=ValueError)
0.900s - Event: batch_progress_75pct (processed_count=74)
1.200s - Event: batch_progress_100pct (processed_count=99)
1.200s - Span End
```

---

### 10.8 OpenTelemetry Exporter Configuration

OpenTelemetry supports multiple exporters for traces, metrics, and logs[^61]. This section covers production-ready exporter configurations for common backends.

#### Pattern 1: OTLP Exporter (Recommended)

OTLP (OpenTelemetry Protocol) is the vendor-neutral standard for telemetry export[^62]. Supports gRPC and HTTP protocols.

```python
# File: src/core/exporters/otlp_config.py
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.exporter.otlp.proto.http.trace_exporter import (
    OTLPSpanExporter as OTLPSpanExporterHTTP
)
from opentelemetry.sdk.resources import Resource
import structlog

logger = structlog.get_logger(__name__)

class OTLPExporterConfig:
    """
    OTLP Exporter Configuration.

    Supports:
    - Jaeger (via OTLP)
    - Grafana Tempo (OTLP)
    - Datadog (OTLP)
    - New Relic (OTLP)
    - AWS X-Ray (via OTLP)
    """

    @staticmethod
    def setup_otlp_grpc_traces(
        otlp_endpoint: str,
        resource: Resource,
        use_tls: bool = False,
        headers: dict = None
    ) -> TracerProvider:
        """
        Configure OTLP gRPC trace exporter.

        Args:
            otlp_endpoint: OTLP endpoint (e.g., "localhost:4317")
            resource: Service resource attributes
            use_tls: Enable TLS (default: False for local dev)
            headers: Custom headers (auth tokens, API keys)

        Example endpoints:
        - Jaeger: localhost:4317
        - Grafana Cloud: tempo-us-central1.grafana.net:443
        - Datadog: agent:4317
        """
        exporter = OTLPSpanExporter(
            endpoint=otlp_endpoint,
            insecure=not use_tls,
            headers=headers or {}
        )

        provider = TracerProvider(resource=resource)
        provider.add_span_processor(BatchSpanProcessor(exporter))

        logger.info(
            "otlp_grpc_traces_configured",
            endpoint=otlp_endpoint,
            tls_enabled=use_tls
        )

        return provider

    @staticmethod
    def setup_otlp_http_traces(
        otlp_endpoint: str,
        resource: Resource,
        headers: dict = None
    ) -> TracerProvider:
        """
        Configure OTLP HTTP trace exporter.

        Args:
            otlp_endpoint: OTLP HTTP endpoint (e.g., "http://localhost:4318/v1/traces")
            resource: Service resource attributes
            headers: Custom headers (auth tokens)

        Example endpoints:
        - Jaeger: http://localhost:4318/v1/traces
        - Grafana Cloud: https://tempo-us-central1.grafana.net/v1/traces
        """
        exporter = OTLPSpanExporterHTTP(
            endpoint=otlp_endpoint,
            headers=headers or {}
        )

        provider = TracerProvider(resource=resource)
        provider.add_span_processor(BatchSpanProcessor(exporter))

        logger.info(
            "otlp_http_traces_configured",
            endpoint=otlp_endpoint
        )

        return provider

    @staticmethod
    def setup_otlp_grpc_metrics(
        otlp_endpoint: str,
        resource: Resource,
        export_interval_ms: int = 60000,
        use_tls: bool = False,
        headers: dict = None
    ) -> MeterProvider:
        """
        Configure OTLP gRPC metric exporter.

        Args:
            otlp_endpoint: OTLP endpoint
            resource: Service resource attributes
            export_interval_ms: Export interval (default: 60s)
            use_tls: Enable TLS
            headers: Custom headers
        """
        exporter = OTLPMetricExporter(
            endpoint=otlp_endpoint,
            insecure=not use_tls,
            headers=headers or {}
        )

        reader = PeriodicExportingMetricReader(
            exporter,
            export_interval_millis=export_interval_ms
        )

        provider = MeterProvider(
            resource=resource,
            metric_readers=[reader]
        )

        logger.info(
            "otlp_grpc_metrics_configured",
            endpoint=otlp_endpoint,
            export_interval_ms=export_interval_ms
        )

        return provider
```

**Usage with Jaeger:**

```python
# File: src/main.py (Jaeger via OTLP)
from src.core.exporters.otlp_config import OTLPExporterConfig
from opentelemetry.sdk.resources import Resource, SERVICE_NAME, SERVICE_VERSION
from opentelemetry import trace, metrics

# Create resource
resource = Resource.create({
    SERVICE_NAME: "ai-agent-mcp-server",
    SERVICE_VERSION: "1.0.0",
    "deployment.environment": "production"
})

# Setup traces (Jaeger OTLP endpoint)
trace_provider = OTLPExporterConfig.setup_otlp_grpc_traces(
    otlp_endpoint="localhost:4317",  # Jaeger OTLP receiver
    resource=resource,
    use_tls=False
)
trace.set_tracer_provider(trace_provider)

# Setup metrics
metrics_provider = OTLPExporterConfig.setup_otlp_grpc_metrics(
    otlp_endpoint="localhost:4317",
    resource=resource
)
metrics.set_meter_provider(metrics_provider)
```

**Jaeger Docker Setup:**

```bash
# Run Jaeger with OTLP support
docker run -d \
  --name jaeger \
  -e COLLECTOR_OTLP_ENABLED=true \
  -p 4317:4317 \
  -p 4318:4318 \
  -p 16686:16686 \
  jaegertracing/all-in-one:latest

# Access Jaeger UI: http://localhost:16686
```

#### Pattern 2: Grafana Cloud (Tempo + Prometheus + Loki)

```python
# File: src/core/exporters/grafana_cloud.py
from src.core.exporters.otlp_config import OTLPExporterConfig
from opentelemetry.sdk.resources import Resource
import structlog
import base64

logger = structlog.get_logger(__name__)

class GrafanaCloudExporter:
    """
    Grafana Cloud telemetry exporter.

    Components:
    - Grafana Tempo (traces)
    - Grafana Cloud Prometheus (metrics)
    - Grafana Loki (logs)
    """

    @staticmethod
    def setup_grafana_cloud(
        service_name: str,
        service_version: str,
        tempo_endpoint: str,
        tempo_api_key: str,
        instance_id: str
    ):
        """
        Configure Grafana Cloud exporters.

        Args:
            service_name: Service name
            service_version: Service version
            tempo_endpoint: Tempo OTLP endpoint (e.g., "tempo-us-central1.grafana.net:443")
            tempo_api_key: Grafana Cloud API key
            instance_id: Grafana Cloud instance ID
        """
        resource = Resource.create({
            "service.name": service_name,
            "service.version": service_version,
            "deployment.environment": "production"
        })

        # Encode API key for Authorization header
        auth_header = f"{instance_id}:{tempo_api_key}"
        encoded_auth = base64.b64encode(auth_header.encode()).decode()

        # Grafana Cloud headers
        headers = {
            "Authorization": f"Basic {encoded_auth}"
        }

        # Setup traces (Grafana Tempo)
        trace_provider = OTLPExporterConfig.setup_otlp_grpc_traces(
            otlp_endpoint=tempo_endpoint,
            resource=resource,
            use_tls=True,
            headers=headers
        )

        # Setup metrics (Grafana Cloud Prometheus)
        metrics_provider = OTLPExporterConfig.setup_otlp_grpc_metrics(
            otlp_endpoint=tempo_endpoint.replace("tempo", "prometheus"),
            resource=resource,
            use_tls=True,
            headers=headers
        )

        logger.info(
            "grafana_cloud_configured",
            service_name=service_name,
            tempo_endpoint=tempo_endpoint
        )

        return trace_provider, metrics_provider
```

**Environment Configuration:**

```python
# File: src/core/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Grafana Cloud configuration
    grafana_tempo_endpoint: str = "tempo-us-central1.grafana.net:443"
    grafana_api_key: str
    grafana_instance_id: str

    class Config:
        env_file = ".env"
```

#### Pattern 3: Multi-Backend Export (Development + Production)

Export to multiple backends simultaneously for local development and production monitoring[^63].

```python
# File: src/core/exporters/multi_backend.py
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import (
    BatchSpanProcessor,
    ConsoleSpanExporter
)
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
import structlog

logger = structlog.get_logger(__name__)

class MultiBackendExporter:
    """
    Export traces to multiple backends.

    Use cases:
    - Development: Console + Jaeger (local visibility)
    - Production: Grafana Cloud + Datadog (redundancy)
    """

    @staticmethod
    def setup_multi_backend_traces(
        resource: Resource,
        enable_console: bool = False,
        jaeger_endpoint: str = None,
        grafana_endpoint: str = None,
        grafana_headers: dict = None
    ) -> TracerProvider:
        """
        Configure multiple trace exporters.

        Args:
            resource: Service resource
            enable_console: Enable console export (dev mode)
            jaeger_endpoint: Jaeger OTLP endpoint
            grafana_endpoint: Grafana Tempo endpoint
            grafana_headers: Grafana auth headers
        """
        provider = TracerProvider(resource=resource)

        # Console exporter (development)
        if enable_console:
            console_exporter = ConsoleSpanExporter()
            provider.add_span_processor(BatchSpanProcessor(console_exporter))
            logger.info("console_trace_exporter_enabled")

        # Jaeger exporter (local/staging)
        if jaeger_endpoint:
            jaeger_exporter = OTLPSpanExporter(
                endpoint=jaeger_endpoint,
                insecure=True
            )
            provider.add_span_processor(BatchSpanProcessor(jaeger_exporter))
            logger.info("jaeger_trace_exporter_enabled", endpoint=jaeger_endpoint)

        # Grafana Tempo exporter (production)
        if grafana_endpoint:
            grafana_exporter = OTLPSpanExporter(
                endpoint=grafana_endpoint,
                insecure=False,
                headers=grafana_headers or {}
            )
            provider.add_span_processor(BatchSpanProcessor(grafana_exporter))
            logger.info("grafana_trace_exporter_enabled", endpoint=grafana_endpoint)

        return provider
```

**Environment-Based Configuration:**

```python
# File: src/main.py (environment-aware exporters)
from src.core.exporters.multi_backend import MultiBackendExporter
from src.core.config import get_settings
from opentelemetry.sdk.resources import Resource, SERVICE_NAME
from opentelemetry import trace

settings = get_settings()

resource = Resource.create({
    SERVICE_NAME: settings.app_name,
    "deployment.environment": settings.environment
})

# Multi-backend based on environment
if settings.environment == "development":
    # Development: Console + Local Jaeger
    trace_provider = MultiBackendExporter.setup_multi_backend_traces(
        resource=resource,
        enable_console=True,
        jaeger_endpoint="localhost:4317"
    )
elif settings.environment == "production":
    # Production: Grafana Cloud only
    trace_provider = MultiBackendExporter.setup_multi_backend_traces(
        resource=resource,
        grafana_endpoint=settings.grafana_tempo_endpoint,
        grafana_headers={"Authorization": f"Bearer {settings.grafana_api_key}"}
    )

trace.set_tracer_provider(trace_provider)
```

#### Pattern 4: Prometheus Remote Write (Metrics Only)

For metrics-only export to Prometheus-compatible backends (Grafana Cloud, Thanos, Cortex)[^64].

```python
# File: src/core/exporters/prometheus_remote_write.py
from prometheus_client import CollectorRegistry, Counter, Histogram, push_to_gateway
import structlog
import time

logger = structlog.get_logger(__name__)

class PrometheusRemoteWriteExporter:
    """
    Prometheus Remote Write exporter.

    Use cases:
    - Push metrics to Prometheus Pushgateway
    - Push to Grafana Cloud Prometheus
    - Push to Thanos/Cortex
    """

    def __init__(
        self,
        pushgateway_url: str,
        job_name: str,
        instance_label: str,
        push_interval_seconds: int = 60
    ):
        self.pushgateway_url = pushgateway_url
        self.job_name = job_name
        self.instance_label = instance_label
        self.push_interval = push_interval_seconds

        # Create custom registry (isolated from global)
        self.registry = CollectorRegistry()

        logger.info(
            "prometheus_remote_write_configured",
            pushgateway_url=pushgateway_url,
            job_name=job_name
        )

    def create_counter(self, name: str, description: str, labels: list[str]) -> Counter:
        """Create counter metric."""
        return Counter(
            name,
            description,
            labelnames=labels,
            registry=self.registry
        )

    def create_histogram(self, name: str, description: str, labels: list[str]) -> Histogram:
        """Create histogram metric."""
        return Histogram(
            name,
            description,
            labelnames=labels,
            registry=self.registry
        )

    def push_metrics(self) -> None:
        """
        Push metrics to Pushgateway.

        Should be called periodically (background task).
        """
        try:
            push_to_gateway(
                gateway=self.pushgateway_url,
                job=self.job_name,
                registry=self.registry,
                grouping_key={"instance": self.instance_label}
            )

            logger.debug(
                "metrics_pushed",
                pushgateway_url=self.pushgateway_url,
                job_name=self.job_name
            )

        except Exception as e:
            logger.error(
                "metrics_push_failed",
                pushgateway_url=self.pushgateway_url,
                error=str(e)
            )
```

**Background Task for Periodic Push:**

```python
# File: src/main.py (metrics push background task)
from fastapi import FastAPI
from contextlib import asynccontextmanager
import asyncio
from src.core.exporters.prometheus_remote_write import PrometheusRemoteWriteExporter

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Setup Prometheus remote write
    exporter = PrometheusRemoteWriteExporter(
        pushgateway_url="http://localhost:9091",
        job_name="ai-agent-mcp-server",
        instance_label="instance-1",
        push_interval_seconds=60
    )

    # Start background task for periodic push
    async def push_metrics_task():
        while True:
            await asyncio.sleep(exporter.push_interval)
            exporter.push_metrics()

    task = asyncio.create_task(push_metrics_task())

    yield

    # Cancel background task on shutdown
    task.cancel()

app = FastAPI(lifespan=lifespan)
```

---

### 10.9 Common OpenTelemetry Troubleshooting

#### Issue 1: Traces Not Appearing in Backend

**Symptoms:**
- Application starts successfully
- No traces visible in Jaeger/Tempo UI
- No errors in logs

**Diagnosis:**

```python
# File: src/api/routes/debug.py
from fastapi import APIRouter
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
import structlog

router = APIRouter()
logger = structlog.get_logger(__name__)

@router.get("/debug/tracing")
async def debug_tracing():
    """
    Debug tracing configuration.

    Checks:
    - Tracer provider configured
    - Span processors registered
    - Current span recording
    """
    provider = trace.get_tracer_provider()

    # Check if tracer provider is configured
    if not isinstance(provider, TracerProvider):
        return {
            "status": "error",
            "message": "TracerProvider not configured (using NoOp)",
            "fix": "Call setup_telemetry() during application startup"
        }

    # Check if span processors exist
    if not provider._active_span_processor._span_processors:
        return {
            "status": "error",
            "message": "No span processors registered",
            "fix": "Add BatchSpanProcessor with exporter"
        }

    # Create test span
    tracer = trace.get_tracer(__name__)
    with tracer.start_as_current_span("test_span") as span:
        span.set_attribute("test", "true")

        ctx = span.get_span_context()

        return {
            "status": "ok",
            "tracer_provider": str(type(provider).__name__),
            "span_processors": len(provider._active_span_processor._span_processors),
            "test_trace_id": format(ctx.trace_id, "032x"),
            "test_span_id": format(ctx.span_id, "016x"),
            "message": "Tracing configured correctly"
        }
```

**Common Fixes:**

1. **Telemetry not initialized:**
   ```python
   # ❌ Missing
   # app = FastAPI()

   # ✅ Initialize in lifespan
   @asynccontextmanager
   async def lifespan(app: FastAPI):
       setup_telemetry(...)  # Initialize here
       yield

   app = FastAPI(lifespan=lifespan)
   ```

2. **Wrong OTLP endpoint:**
   ```python
   # ❌ Incorrect
   OTLPSpanExporter(endpoint="http://localhost:4317")  # HTTP protocol on gRPC port

   # ✅ Correct
   OTLPSpanExporter(endpoint="localhost:4317", insecure=True)  # gRPC endpoint
   ```

3. **Firewall blocking OTLP:**
   ```bash
   # Test OTLP endpoint connectivity
   nc -zv localhost 4317
   ```

#### Issue 2: High Memory Usage from Metrics

**Symptoms:**
- Memory usage grows over time
- OOM errors in production
- Slow metric export

**Diagnosis:**

```python
# File: src/api/routes/debug.py
from prometheus_client import REGISTRY

@router.get("/debug/metrics")
async def debug_metrics():
    """
    Debug metrics cardinality.

    Checks:
    - Number of unique metric series
    - Label cardinality
    - Memory usage
    """
    metric_families = list(REGISTRY.collect())

    cardinality = {}
    for family in metric_families:
        series_count = len(list(family.samples))
        cardinality[family.name] = series_count

    # Check for high-cardinality metrics (>1000 series)
    high_cardinality = {
        name: count
        for name, count in cardinality.items()
        if count > 1000
    }

    if high_cardinality:
        return {
            "status": "warning",
            "total_series": sum(cardinality.values()),
            "high_cardinality_metrics": high_cardinality,
            "message": "High cardinality detected - review metric labels",
            "fix": "Use low-cardinality labels (user_type instead of user_id)"
        }

    return {
        "status": "ok",
        "total_series": sum(cardinality.values()),
        "metric_count": len(cardinality)
    }
```

**Fix: Reduce Label Cardinality:**

```python
# ❌ High cardinality (millions of series)
requests_by_user = Counter(
    'requests_by_user_total',
    'Requests by user',
    ['user_id']  # PROBLEM: unbounded
)

# ✅ Low cardinality (10-100 series)
requests_by_user_type = Counter(
    'requests_by_user_type_total',
    'Requests by user type',
    ['user_type', 'subscription_tier']  # Bounded: admin/user × free/premium
)
```

#### Issue 3: Missing Trace Context in Logs

**Symptoms:**
- Logs don't include trace_id or span_id
- Can't correlate logs with traces

**Diagnosis:**

```python
# File: src/api/routes/test.py
from fastapi import APIRouter
from opentelemetry import trace
import structlog

router = APIRouter()
logger = structlog.get_logger(__name__)

@router.get("/test/trace-context")
async def test_trace_context():
    """Test trace context in logs."""
    span = trace.get_current_span()
    ctx = span.get_span_context()

    # Log with trace context
    logger.info(
        "test_log_entry",
        test_field="test_value"
    )

    if ctx.is_valid:
        return {
            "status": "ok",
            "trace_id": format(ctx.trace_id, "032x"),
            "span_id": format(ctx.span_id, "016x"),
            "message": "Check logs for trace_id and span_id fields"
        }
    else:
        return {
            "status": "error",
            "message": "No valid span context - tracing not initialized"
        }
```

**Fix: Add OTeL Processor to Structlog:**

```python
# File: src/core/logging.py
import structlog
from opentelemetry import trace

def add_opentelemetry_context(logger, method_name, event_dict):
    """Inject trace context into logs."""
    span = trace.get_current_span()
    if span and span.is_recording():
        ctx = span.get_span_context()
        if ctx.is_valid:
            event_dict["trace_id"] = format(ctx.trace_id, "032x")
            event_dict["span_id"] = format(ctx.span_id, "016x")
    return event_dict

# Configure structlog
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        add_opentelemetry_context,  # Add this processor
        structlog.processors.JSONRenderer()
    ]
)
```

#### Issue 4: Slow Application Startup

**Symptoms:**
- Application takes 10+ seconds to start
- High CPU during initialization
- Blocking during OTeL setup

**Fix: Async Initialization:**

```python
# File: src/main.py
from fastapi import FastAPI
from contextlib import asynccontextmanager
import asyncio

@asynccontextmanager
async def lifespan(app: FastAPI):
    # ❌ Blocking initialization (10s startup)
    # setup_telemetry(...)
    # instrument_fastapi(app)
    # initialize_metrics(...)

    # ✅ Async initialization (1s startup)
    await asyncio.gather(
        asyncio.to_thread(setup_telemetry, ...),
        asyncio.to_thread(instrument_fastapi, app),
        asyncio.to_thread(initialize_metrics, ...)
    )

    yield

app = FastAPI(lifespan=lifespan)
```

---

### 10.10 References

[^41]: OpenTelemetry Documentation, "Traces," https://opentelemetry.io/docs/concepts/signals/traces/, accessed 2025-11-02.

[^42]: OpenTelemetry Documentation, "Getting Started," https://opentelemetry.io/docs/getting-started/, accessed 2025-11-02.

[^43]: Prometheus Documentation, "OpenTelemetry Integration," https://prometheus.io/docs/prometheus/latest/feature_flags/#opentelemetry-receiver, accessed 2025-11-02.

[^44]: OpenTelemetry Python Documentation, "FastAPI Instrumentation," https://opentelemetry-python-contrib.readthedocs.io/en/latest/instrumentation/fastapi/fastapi.html, accessed 2025-11-02.

[^45]: Prometheus Client Python Documentation, "Prometheus Python Client," https://github.com/prometheus/client_python, accessed 2025-11-02.

[^46]: Jaeger Documentation, "Architecture," https://www.jaegertracing.io/docs/latest/architecture/, accessed 2025-11-02.

[^47]: Grafana Tempo Documentation, "Introduction," https://grafana.com/docs/tempo/latest/, accessed 2025-11-02.

[^48]: CNCF, "OpenTelemetry Best Practices," https://opentelemetry.io/docs/best-practices/, accessed 2025-11-02.

[^49]: Prometheus Documentation, "Metric and Label Naming," https://prometheus.io/docs/practices/naming/, accessed 2025-11-02.

[^50]: OpenTelemetry Documentation, "Context Propagation," https://opentelemetry.io/docs/concepts/context-propagation/, accessed 2025-11-02.

[^51]: OpenTelemetry Documentation, "Logs," https://opentelemetry.io/docs/concepts/signals/logs/, accessed 2025-11-02.

[^52]: Structlog Documentation, "OpenTelemetry Integration," https://www.structlog.org/en/stable/integrations.html#opentelemetry, accessed 2025-11-02.

[^53]: OpenTelemetry Python Documentation, "Logs API," https://opentelemetry-python.readthedocs.io/en/latest/sdk/logs.html, accessed 2025-11-02.

[^54]: OpenTelemetry Documentation, "Metrics," https://opentelemetry.io/docs/concepts/signals/metrics/, accessed 2025-11-02.

[^55]: Prometheus Documentation, "OpenTelemetry Metrics," https://prometheus.io/docs/concepts/metric_types/, accessed 2025-11-02.

[^56]: OpenTelemetry Python Documentation, "Metrics API," https://opentelemetry-python.readthedocs.io/en/latest/sdk/metrics.html, accessed 2025-11-02.

[^57]: OpenTelemetry Documentation, "Distributed Tracing," https://opentelemetry.io/docs/concepts/observability-primer/#distributed-tracing, accessed 2025-11-02.

[^58]: W3C Trace Context Specification, "W3C Recommendation," https://www.w3.org/TR/trace-context/, accessed 2025-11-02.

[^59]: OpenTelemetry Python Documentation, "Propagators," https://opentelemetry-python.readthedocs.io/en/latest/api/propagate.html, accessed 2025-11-02.

[^60]: OpenTelemetry Documentation, "Span Events," https://opentelemetry.io/docs/concepts/signals/traces/#span-events, accessed 2025-11-02.

[^61]: OpenTelemetry Documentation, "Exporters," https://opentelemetry.io/docs/instrumentation/python/exporters/, accessed 2025-11-02.

[^62]: OpenTelemetry Protocol Specification, "OTLP," https://opentelemetry.io/docs/specs/otlp/, accessed 2025-11-02.

[^63]: OpenTelemetry Documentation, "Multiple Exporters," https://opentelemetry.io/docs/instrumentation/python/exporters/#multiple-exporters, accessed 2025-11-02.

[^64]: Prometheus Documentation, "Remote Write," https://prometheus.io/docs/prometheus/latest/configuration/configuration/#remote_write, accessed 2025-11-02.

---

## 11. Audit Logging

### 11.1 Recommended Approach: Structured Audit Events with Immutable Storage

Audit logging captures **who did what, when, and why** for compliance and security investigations[^51]. Unlike application logs (debugging), audit logs are **immutable, tamper-evident records** designed for regulatory compliance (SOC 2, GDPR, HIPAA)[^52].

**Core Requirements:**
- **Immutable Storage:** Audit records cannot be modified or deleted after creation
- **User Attribution:** Every action linked to authenticated user (user ID, IP address, session)
- **Action Traceability:** Complete event context (before/after state, reason, outcome)
- **Retention Policy:** Long-term storage (typically 1-7 years depending on compliance)
- **Tamper Detection:** Cryptographic signatures or append-only storage

**Architecture:**
```
API Request
    ↓
Authentication Middleware (extract user context)
    ↓
Business Logic (domain operation)
    ↓
Audit Middleware (capture event)
    ↓
Audit Event Model (Pydantic validation)
    ↓
Audit Repository (immutable storage)
    ↓
Database (append-only table) OR Event Stream (Kafka/Kinesis)
```

### 11.2 Implementation Examples

#### Pattern 1: Audit Event Model (Pydantic)

```python
# File: src/domain/models/audit_event.py
from pydantic import BaseModel, Field, field_validator
from datetime import datetime, UTC
from typing import Optional, Literal, Any
from enum import Enum
import hashlib
import json
import structlog

logger = structlog.get_logger(__name__)

class AuditAction(str, Enum):
    """Enumeration of auditable actions."""
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    VIEW = "view"
    EXPORT = "export"
    LOGIN = "login"
    LOGOUT = "logout"
    PERMISSION_CHANGE = "permission_change"

class AuditOutcome(str, Enum):
    """Audit event outcome."""
    SUCCESS = "success"
    FAILURE = "failure"
    PARTIAL = "partial"

class AuditEvent(BaseModel):
    """
    Immutable audit event record.

    Compliance Requirements:
    - SOC 2: User attribution, timestamp, action, outcome
    - GDPR Article 30: Processing activities record
    - HIPAA: Access control audit trail
    """

    # Event metadata
    event_id: str = Field(description="Unique event ID (UUID)")
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="Event timestamp (UTC)"
    )

    # User context (who)
    user_id: Optional[int] = Field(default=None, description="Authenticated user ID")
    username: Optional[str] = Field(default=None, description="Username")
    ip_address: str = Field(description="Client IP address")
    user_agent: Optional[str] = Field(default=None, description="Client user agent")
    session_id: Optional[str] = Field(default=None, description="Session identifier")

    # Action context (what)
    action: AuditAction = Field(description="Action performed")
    resource_type: str = Field(description="Type of resource affected (e.g., 'User', 'Resource')")
    resource_id: Optional[str] = Field(default=None, description="ID of affected resource")

    # Action details (how)
    outcome: AuditOutcome = Field(description="Action outcome")
    reason: Optional[str] = Field(default=None, description="Reason for action (optional)")
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional event context (before/after state, etc.)"
    )

    # Request context (where)
    api_endpoint: Optional[str] = Field(default=None, description="API endpoint invoked")
    http_method: Optional[str] = Field(default=None, description="HTTP method (GET, POST, etc.)")

    # Tamper detection
    event_hash: Optional[str] = Field(
        default=None,
        description="SHA-256 hash of event for tamper detection"
    )

    @field_validator("metadata")
    @classmethod
    def validate_metadata_serializable(cls, v: dict[str, Any]) -> dict[str, Any]:
        """
        Ensure metadata is JSON-serializable.

        Prevents storing non-serializable objects (datetime, custom classes, etc.).
        """
        try:
            json.dumps(v)
            return v
        except (TypeError, ValueError) as e:
            raise ValueError(f"Metadata must be JSON-serializable: {e}")

    def compute_hash(self) -> str:
        """
        Compute SHA-256 hash of audit event.

        Used for tamper detection:
        - Hash stored with event
        - Recompute hash during retrieval
        - Mismatch indicates tampering
        """
        # Create deterministic string representation (exclude hash field)
        event_dict = self.model_dump(exclude={"event_hash"})
        event_str = json.dumps(event_dict, sort_keys=True, default=str)

        # Compute SHA-256 hash
        hash_obj = hashlib.sha256(event_str.encode('utf-8'))
        return hash_obj.hexdigest()

    def model_post_init(self, __context) -> None:
        """Automatically compute hash after initialization."""
        if self.event_hash is None:
            self.event_hash = self.compute_hash()

    class Config:
        json_schema_extra = {
            "example": {
                "event_id": "550e8400-e29b-41d4-a716-446655440000",
                "timestamp": "2025-11-02T10:30:00Z",
                "user_id": 42,
                "username": "john.doe",
                "ip_address": "192.168.1.100",
                "user_agent": "Mozilla/5.0",
                "session_id": "abc123",
                "action": "update",
                "resource_type": "Resource",
                "resource_id": "123",
                "outcome": "success",
                "reason": "User requested profile update",
                "metadata": {
                    "before": {"name": "Old Name"},
                    "after": {"name": "New Name"}
                },
                "api_endpoint": "/api/resources/123",
                "http_method": "PUT",
                "event_hash": "a1b2c3d4e5f6..."
            }
        }
```

#### Pattern 2: Audit Logging Middleware

```python
# File: src/api/middleware/audit_middleware.py
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from src.domain.models.audit_event import AuditEvent, AuditAction, AuditOutcome
from src.infrastructure.audit.audit_repository import AuditRepository
from src.infrastructure.database.session import get_session
import uuid
import structlog
from typing import Optional

logger = structlog.get_logger(__name__)

class AuditLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware to capture audit events for API requests.

    Captures:
    - User context (from authentication)
    - API endpoint and HTTP method
    - Request outcome (success/failure)
    """

    # Define auditable endpoints (whitelist or blacklist)
    AUDITABLE_PATHS = {
        "/api/resources",
        "/api/users",
        "/api/permissions"
    }

    # Define actions requiring audit (state-changing operations)
    AUDITABLE_METHODS = {"POST", "PUT", "PATCH", "DELETE"}

    async def dispatch(self, request: Request, call_next):
        # Check if request should be audited
        if not self._should_audit(request):
            return await call_next(request)

        # Extract user context from request state (set by auth middleware)
        user_id = getattr(request.state, "user_id", None)
        username = getattr(request.state, "username", None)
        session_id = getattr(request.state, "session_id", None)

        # Extract request metadata
        ip_address = request.client.host if request.client else "unknown"
        user_agent = request.headers.get("user-agent")

        try:
            # Process request
            response = await call_next(request)

            # Determine outcome
            outcome = (
                AuditOutcome.SUCCESS
                if 200 <= response.status_code < 400
                else AuditOutcome.FAILURE
            )

            # Create audit event
            await self._create_audit_event(
                user_id=user_id,
                username=username,
                ip_address=ip_address,
                user_agent=user_agent,
                session_id=session_id,
                action=self._map_method_to_action(request.method),
                resource_type=self._extract_resource_type(request.url.path),
                resource_id=self._extract_resource_id(request.url.path),
                outcome=outcome,
                api_endpoint=request.url.path,
                http_method=request.method,
                metadata={
                    "status_code": response.status_code,
                    "query_params": dict(request.query_params)
                }
            )

            return response

        except Exception as e:
            # Log failure audit event
            await self._create_audit_event(
                user_id=user_id,
                username=username,
                ip_address=ip_address,
                user_agent=user_agent,
                session_id=session_id,
                action=self._map_method_to_action(request.method),
                resource_type=self._extract_resource_type(request.url.path),
                resource_id=self._extract_resource_id(request.url.path),
                outcome=AuditOutcome.FAILURE,
                api_endpoint=request.url.path,
                http_method=request.method,
                metadata={"error": str(e)}
            )
            raise

    def _should_audit(self, request: Request) -> bool:
        """Determine if request should be audited."""
        # Audit state-changing methods on auditable paths
        path_match = any(
            request.url.path.startswith(path)
            for path in self.AUDITABLE_PATHS
        )
        method_match = request.method in self.AUDITABLE_METHODS

        return path_match and method_match

    def _map_method_to_action(self, http_method: str) -> AuditAction:
        """Map HTTP method to audit action."""
        method_map = {
            "POST": AuditAction.CREATE,
            "PUT": AuditAction.UPDATE,
            "PATCH": AuditAction.UPDATE,
            "DELETE": AuditAction.DELETE,
            "GET": AuditAction.VIEW
        }
        return method_map.get(http_method, AuditAction.VIEW)

    def _extract_resource_type(self, path: str) -> str:
        """Extract resource type from path (e.g., /api/resources/123 → Resource)."""
        parts = path.strip("/").split("/")
        if len(parts) >= 2:
            return parts[1].capitalize().rstrip("s")  # /api/resources → Resource
        return "Unknown"

    def _extract_resource_id(self, path: str) -> Optional[str]:
        """Extract resource ID from path (e.g., /api/resources/123 → 123)."""
        parts = path.strip("/").split("/")
        if len(parts) >= 3 and parts[2].isdigit():
            return parts[2]
        return None

    async def _create_audit_event(
        self,
        user_id: Optional[int],
        username: Optional[str],
        ip_address: str,
        user_agent: Optional[str],
        session_id: Optional[str],
        action: AuditAction,
        resource_type: str,
        resource_id: Optional[str],
        outcome: AuditOutcome,
        api_endpoint: str,
        http_method: str,
        metadata: dict
    ) -> None:
        """Create and persist audit event."""
        event = AuditEvent(
            event_id=str(uuid.uuid4()),
            user_id=user_id,
            username=username,
            ip_address=ip_address,
            user_agent=user_agent,
            session_id=session_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            outcome=outcome,
            api_endpoint=api_endpoint,
            http_method=http_method,
            metadata=metadata
        )

        # Persist to audit repository (async)
        async for session in get_session():
            repo = AuditRepository(session)
            await repo.create_event(event)
            await session.commit()
            break

        logger.info(
            "audit_event_created",
            event_id=event.event_id,
            user_id=user_id,
            action=action,
            outcome=outcome
        )
```

#### Pattern 3: Audit Repository (Immutable Storage)

```python
# File: src/infrastructure/audit/audit_repository.py
from sqlalchemy import Column, String, Integer, DateTime, Text, JSON, Index
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import declarative_base
from src.domain.models.audit_event import AuditEvent
from datetime import datetime, UTC
from typing import Optional, List
import structlog

logger = structlog.get_logger(__name__)

Base = declarative_base()

class AuditEventRecord(Base):
    """
    Immutable audit event storage (append-only table).

    Database Constraints:
    - No UPDATE or DELETE operations allowed (enforced via triggers)
    - Primary key: event_id (UUID)
    - Indexes: user_id, timestamp, action (for efficient queries)
    - Retention: 7 years (compliance requirement)
    """
    __tablename__ = "audit_events"

    event_id = Column(String(36), primary_key=True)
    timestamp = Column(DateTime(timezone=True), nullable=False, index=True)

    # User context
    user_id = Column(Integer, nullable=True, index=True)
    username = Column(String(255), nullable=True)
    ip_address = Column(String(45), nullable=False)  # IPv6 support
    user_agent = Column(Text, nullable=True)
    session_id = Column(String(255), nullable=True)

    # Action context
    action = Column(String(50), nullable=False, index=True)
    resource_type = Column(String(100), nullable=False, index=True)
    resource_id = Column(String(255), nullable=True, index=True)

    # Action details
    outcome = Column(String(20), nullable=False)
    reason = Column(Text, nullable=True)
    metadata = Column(JSON, nullable=False, default={})

    # Request context
    api_endpoint = Column(String(500), nullable=True)
    http_method = Column(String(10), nullable=True)

    # Tamper detection
    event_hash = Column(String(64), nullable=False)

    __table_args__ = (
        Index('ix_audit_user_action', 'user_id', 'action'),
        Index('ix_audit_timestamp_action', 'timestamp', 'action'),
    )

class AuditRepository:
    """Repository for audit event operations (append-only)."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_event(self, event: AuditEvent) -> AuditEventRecord:
        """
        Create immutable audit event record.

        Note: This is the ONLY write operation allowed.
        Updates and deletes prohibited by database triggers.
        """
        record = AuditEventRecord(
            event_id=event.event_id,
            timestamp=event.timestamp,
            user_id=event.user_id,
            username=event.username,
            ip_address=event.ip_address,
            user_agent=event.user_agent,
            session_id=event.session_id,
            action=event.action.value,
            resource_type=event.resource_type,
            resource_id=event.resource_id,
            outcome=event.outcome.value,
            reason=event.reason,
            metadata=event.metadata,
            api_endpoint=event.api_endpoint,
            http_method=event.http_method,
            event_hash=event.event_hash
        )

        self.session.add(record)

        logger.debug(
            "audit_event_persisted",
            event_id=event.event_id,
            user_id=event.user_id,
            action=event.action
        )

        return record

    async def get_events_by_user(
        self,
        user_id: int,
        limit: int = 100,
        offset: int = 0
    ) -> List[AuditEventRecord]:
        """Retrieve audit events for specific user."""
        stmt = (
            select(AuditEventRecord)
            .where(AuditEventRecord.user_id == user_id)
            .order_by(AuditEventRecord.timestamp.desc())
            .limit(limit)
            .offset(offset)
        )

        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_events_by_resource(
        self,
        resource_type: str,
        resource_id: str,
        limit: int = 100
    ) -> List[AuditEventRecord]:
        """Retrieve audit events for specific resource."""
        stmt = (
            select(AuditEventRecord)
            .where(
                AuditEventRecord.resource_type == resource_type,
                AuditEventRecord.resource_id == resource_id
            )
            .order_by(AuditEventRecord.timestamp.desc())
            .limit(limit)
        )

        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def verify_event_integrity(self, event_id: str) -> bool:
        """
        Verify audit event has not been tampered with.

        Recomputes hash and compares with stored hash.
        """
        stmt = select(AuditEventRecord).where(AuditEventRecord.event_id == event_id)
        result = await self.session.execute(stmt)
        record = result.scalar_one_or_none()

        if not record:
            return False

        # Reconstruct AuditEvent from record
        event = AuditEvent(
            event_id=record.event_id,
            timestamp=record.timestamp,
            user_id=record.user_id,
            username=record.username,
            ip_address=record.ip_address,
            user_agent=record.user_agent,
            session_id=record.session_id,
            action=record.action,
            resource_type=record.resource_type,
            resource_id=record.resource_id,
            outcome=record.outcome,
            reason=record.reason,
            metadata=record.metadata,
            api_endpoint=record.api_endpoint,
            http_method=record.http_method,
            event_hash=record.event_hash
        )

        # Recompute hash
        computed_hash = event.compute_hash()

        # Verify integrity
        is_valid = computed_hash == record.event_hash

        if not is_valid:
            logger.error(
                "audit_event_tampered",
                event_id=event_id,
                stored_hash=record.event_hash,
                computed_hash=computed_hash
            )

        return is_valid
```

### 11.2.1 Audit Logging Patterns

#### Pattern 1: Database Storage (Append-Only Table)

**Use Case:** Small to medium traffic (< 10K events/day), SQL database already in use

```sql
-- Migration: Create audit_events table with immutable constraints
CREATE TABLE audit_events (
    event_id VARCHAR(36) PRIMARY KEY,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    user_id INTEGER,
    username VARCHAR(255),
    ip_address VARCHAR(45) NOT NULL,
    user_agent TEXT,
    session_id VARCHAR(255),
    action VARCHAR(50) NOT NULL,
    resource_type VARCHAR(100) NOT NULL,
    resource_id VARCHAR(255),
    outcome VARCHAR(20) NOT NULL,
    reason TEXT,
    metadata JSONB NOT NULL DEFAULT '{}',
    api_endpoint VARCHAR(500),
    http_method VARCHAR(10),
    event_hash VARCHAR(64) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for common queries
CREATE INDEX ix_audit_user_id ON audit_events(user_id);
CREATE INDEX ix_audit_timestamp ON audit_events(timestamp DESC);
CREATE INDEX ix_audit_action ON audit_events(action);
CREATE INDEX ix_audit_resource ON audit_events(resource_type, resource_id);

-- Trigger: Prevent updates and deletes (immutability)
CREATE OR REPLACE FUNCTION prevent_audit_modifications()
RETURNS TRIGGER AS $$
BEGIN
    RAISE EXCEPTION 'Audit events are immutable. UPDATE and DELETE operations are forbidden.';
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_prevent_update
BEFORE UPDATE ON audit_events
FOR EACH ROW EXECUTE FUNCTION prevent_audit_modifications();

CREATE TRIGGER trigger_prevent_delete
BEFORE DELETE ON audit_events
FOR EACH ROW EXECUTE FUNCTION prevent_audit_modifications();
```

**✅ Benefits:**
- Simple (uses existing database)
- ACID guarantees (transactional consistency)
- SQL queries (easy analytics)

**❌ Drawbacks:**
- Limited scale (database bottleneck at high volume)
- Storage cost (audit data grows indefinitely)

#### Pattern 2: Event Stream (Kafka/Kinesis)

**Use Case:** High traffic (> 100K events/day), distributed systems, real-time analytics

```python
# File: src/infrastructure/audit/kafka_audit_publisher.py
from aiokafka import AIOKafkaProducer
from src.domain.models.audit_event import AuditEvent
import json
import structlog

logger = structlog.get_logger(__name__)

class KafkaAuditPublisher:
    """Publish audit events to Kafka topic."""

    def __init__(self, bootstrap_servers: str, topic: str = "audit-events"):
        self.bootstrap_servers = bootstrap_servers
        self.topic = topic
        self.producer: Optional[AIOKafkaProducer] = None

    async def start(self) -> None:
        """Initialize Kafka producer."""
        self.producer = AIOKafkaProducer(
            bootstrap_servers=self.bootstrap_servers,
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )
        await self.producer.start()
        logger.info("kafka_audit_publisher_started", topic=self.topic)

    async def publish_event(self, event: AuditEvent) -> None:
        """Publish audit event to Kafka topic."""
        if not self.producer:
            raise RuntimeError("Kafka producer not initialized")

        # Serialize event to JSON
        event_data = event.model_dump(mode='json')

        # Publish to Kafka
        await self.producer.send_and_wait(self.topic, event_data)

        logger.debug(
            "audit_event_published",
            event_id=event.event_id,
            topic=self.topic
        )

    async def stop(self) -> None:
        """Shutdown Kafka producer."""
        if self.producer:
            await self.producer.stop()
            logger.info("kafka_audit_publisher_stopped")
```

**✅ Benefits:**
- High throughput (millions of events/day)
- Decoupled (audit doesn't block API response)
- Retention policies (auto-delete old events)
- Real-time analytics (stream processing)

**❌ Drawbacks:**
- Complex infrastructure (Kafka cluster)
- Eventual consistency (async writes)
- No ACID guarantees

#### Pattern 3: Hybrid (Database + Event Stream)

**Use Case:** Best of both worlds - database for compliance queries, stream for analytics

```python
# File: src/infrastructure/audit/hybrid_audit_service.py
from src.domain.models.audit_event import AuditEvent
from src.infrastructure.audit.audit_repository import AuditRepository
from src.infrastructure.audit.kafka_audit_publisher import KafkaAuditPublisher
from sqlalchemy.ext.asyncio import AsyncSession
import structlog

logger = structlog.get_logger(__name__)

class HybridAuditService:
    """
    Hybrid audit service: Database + Event Stream.

    Strategy:
    - Write to database (compliance, immutable storage)
    - Publish to Kafka (analytics, real-time alerting)
    """

    def __init__(
        self,
        session: AsyncSession,
        kafka_publisher: KafkaAuditPublisher
    ):
        self.repository = AuditRepository(session)
        self.kafka_publisher = kafka_publisher

    async def create_event(self, event: AuditEvent) -> None:
        """
        Create audit event in both database and Kafka.

        Guarantees:
        - Database write always succeeds (critical path)
        - Kafka publish best-effort (non-blocking)
        """
        # 1. Write to database (critical - must succeed)
        await self.repository.create_event(event)

        # 2. Publish to Kafka (best-effort - don't block on failure)
        try:
            await self.kafka_publisher.publish_event(event)
        except Exception as e:
            logger.error(
                "kafka_publish_failed",
                event_id=event.event_id,
                error=str(e),
                message="Event persisted to database but Kafka publish failed"
            )

        logger.info(
            "audit_event_created",
            event_id=event.event_id,
            database=True,
            kafka=True
        )
```

#### Pattern 4: Centralized Audit Service (Microservices)

**Use Case:** Multiple microservices need centralized audit logging

```python
# File: src/infrastructure/audit/audit_client.py
import httpx
from src.domain.models.audit_event import AuditEvent
import structlog

logger = structlog.get_logger(__name__)

class AuditServiceClient:
    """
    Client for centralized audit service.

    Microservices send audit events to dedicated audit service via HTTP API.
    """

    def __init__(self, audit_service_url: str):
        self.audit_service_url = audit_service_url
        self.client = httpx.AsyncClient(timeout=5.0)

    async def create_event(self, event: AuditEvent) -> None:
        """Send audit event to centralized audit service."""
        try:
            response = await self.client.post(
                f"{self.audit_service_url}/audit-events",
                json=event.model_dump(mode='json')
            )
            response.raise_for_status()

            logger.debug(
                "audit_event_sent",
                event_id=event.event_id,
                audit_service=self.audit_service_url
            )
        except httpx.HTTPError as e:
            logger.error(
                "audit_service_unavailable",
                event_id=event.event_id,
                error=str(e),
                message="Audit event not persisted (service unavailable)"
            )

    async def close(self) -> None:
        """Close HTTP client."""
        await self.client.aclose()
```

### 11.2.2 Common Audit Logging Mistakes

#### Mistake 1: Missing User Context

**❌ Incorrect:**
```python
# Audit event without user attribution
audit_event = AuditEvent(
    event_id=str(uuid.uuid4()),
    ip_address="192.168.1.1",
    action=AuditAction.DELETE,
    resource_type="Resource",
    resource_id="123",
    outcome=AuditOutcome.SUCCESS,
    # MISSING: user_id, username (can't determine who performed action)
)
```

**✅ Correct:**
```python
# Always capture user context from authentication
audit_event = AuditEvent(
    event_id=str(uuid.uuid4()),
    user_id=request.state.user_id,  # From auth middleware
    username=request.state.username,
    ip_address=request.client.host,
    session_id=request.state.session_id,
    action=AuditAction.DELETE,
    resource_type="Resource",
    resource_id="123",
    outcome=AuditOutcome.SUCCESS
)
```

#### Mistake 2: Mutable Audit Records

**❌ Incorrect:**
```python
# Allow updates to audit records (violates immutability)
@app.put("/audit-events/{event_id}")
async def update_audit_event(event_id: str, updates: dict):
    # NEVER allow audit record updates
    await audit_repo.update(event_id, updates)
```

**✅ Correct:**
```python
# Audit records are append-only (no updates/deletes)
# If correction needed, create new audit event with reason
@app.post("/audit-events/{event_id}/correction")
async def correct_audit_event(event_id: str, correction: AuditCorrection):
    # Create new event documenting correction
    correction_event = AuditEvent(
        event_id=str(uuid.uuid4()),
        user_id=request.state.user_id,
        ip_address=request.client.host,
        action=AuditAction.UPDATE,
        resource_type="AuditEvent",
        resource_id=event_id,
        outcome=AuditOutcome.SUCCESS,
        reason=f"Correction: {correction.reason}",
        metadata={"original_event_id": event_id, "correction": correction.details}
    )
    await audit_repo.create_event(correction_event)
```

#### Mistake 3: Incomplete Event Context

**❌ Incorrect:**
```python
# Missing before/after state (can't reconstruct what changed)
audit_event = AuditEvent(
    event_id=str(uuid.uuid4()),
    user_id=42,
    ip_address="192.168.1.1",
    action=AuditAction.UPDATE,
    resource_type="Resource",
    resource_id="123",
    outcome=AuditOutcome.SUCCESS
    # MISSING: metadata with before/after state
)
```

**✅ Correct:**
```python
# Capture before/after state for UPDATE actions
audit_event = AuditEvent(
    event_id=str(uuid.uuid4()),
    user_id=42,
    ip_address="192.168.1.1",
    action=AuditAction.UPDATE,
    resource_type="Resource",
    resource_id="123",
    outcome=AuditOutcome.SUCCESS,
    metadata={
        "before": {"name": "Old Name", "priority": 5},
        "after": {"name": "New Name", "priority": 8},
        "changed_fields": ["name", "priority"]
    }
)
```

### 11.2.3 Verification and Troubleshooting

#### Audit Completeness Check

```python
# File: src/api/routes/audit_admin.py
from fastapi import APIRouter, Depends
from src.infrastructure.audit.audit_repository import AuditRepository
from src.infrastructure.database.session import get_session
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta
import structlog

router = APIRouter()
logger = structlog.get_logger(__name__)

@router.get("/admin/audit/completeness")
async def check_audit_completeness(
    session: AsyncSession = Depends(get_session)
):
    """
    Verify audit log completeness.

    Checks:
    - No gaps in event timestamps (continuous coverage)
    - All critical actions logged (CREATE, UPDATE, DELETE)
    - User attribution complete (no null user_id for authenticated actions)
    """
    repo = AuditRepository(session)

    # Check for timestamp gaps (> 5 minutes without events)
    # (Implementation depends on database query capabilities)

    # Check user attribution completeness
    # SELECT COUNT(*) FROM audit_events WHERE action IN ('create', 'update', 'delete') AND user_id IS NULL

    # Report findings
    return {
        "status": "complete",
        "checks": {
            "timestamp_continuity": "ok",
            "user_attribution": "ok",
            "critical_actions_logged": "ok"
        }
    }

@router.get("/admin/audit/integrity/{event_id}")
async def verify_event_integrity(
    event_id: str,
    session: AsyncSession = Depends(get_session)
):
    """
    Verify audit event has not been tampered with.

    Recomputes hash and compares with stored value.
    """
    repo = AuditRepository(session)
    is_valid = await repo.verify_event_integrity(event_id)

    return {
        "event_id": event_id,
        "integrity_valid": is_valid,
        "message": "Event is intact" if is_valid else "Event has been tampered with"
    }
```

### 11.3 Alternative Approaches

| Approach | Storage | Immutability | Compliance | Scale | Complexity |
|----------|---------|--------------|------------|-------|------------|
| **Database (Append-Only)** | PostgreSQL | ✅ Triggers | ✅ SOC 2, GDPR | < 10K events/day | Low |
| **Event Stream (Kafka)** | Kafka | ✅ Append-only log | ⚠️ Requires archival | > 100K events/day | High |
| **Hybrid (DB + Stream)** | PostgreSQL + Kafka | ✅ Both | ✅ SOC 2, GDPR | > 100K events/day | Medium |
| **Centralized Service** | Dedicated microservice | ✅ Service-enforced | ✅ SOC 2, GDPR | Variable | Medium |
| **Cloud Audit (CloudTrail)** | AWS S3 | ✅ AWS-managed | ✅ SOC 2, GDPR, HIPAA | Unlimited | Low |
| **SIEM (Splunk, Datadog)** | Vendor-managed | ✅ Vendor-enforced | ✅ SOC 2, GDPR | Unlimited | Low |

### 11.4 Decision Criteria

**Use Database Storage when:**
- Low to medium traffic (< 10K events/day)
- Already using SQL database
- Need SQL queries for compliance reports
- Simple infrastructure preferred

**Use Event Stream when:**
- High traffic (> 100K events/day)
- Real-time analytics required
- Distributed system with multiple microservices
- Have Kafka/Kinesis infrastructure

**Use Hybrid Approach when:**
- Need both compliance (database) and analytics (stream)
- Want best of both worlds
- Can manage dual-write complexity

**Use Centralized Audit Service when:**
- Multiple microservices need audit logging
- Want to isolate audit infrastructure
- Need consistent audit format across services

**Use Cloud/SIEM when:**
- Want managed solution (no infrastructure)
- Multi-cloud or hybrid environment
- Need advanced analytics (anomaly detection, alerting)

### 11.5 References

[^51]: OWASP, "Logging Cheat Sheet - Audit Logs," https://cheatsheetseries.owasp.org/cheatsheets/Logging_Cheat_Sheet.html#audit-logs, accessed 2025-11-02.

[^52]: SOC 2 Trust Services Criteria, "CC6.3 - Logging and Monitoring," https://us.aicpa.org/interestareas/frc/assuranceadvisoryservices/aicpasoc2report, accessed 2025-11-02.

[^53]: GDPR Article 30, "Records of processing activities," https://gdpr-info.eu/art-30-gdpr/, accessed 2025-11-02.

[^54]: HIPAA Security Rule, "Audit Controls (164.312(b))," https://www.hhs.gov/hipaa/for-professionals/security/laws-regulations/index.html, accessed 2025-11-02.

[^55]: NIST SP 800-53, "AU-2: Audit Events," https://csrc.nist.gov/publications/detail/sp/800-53/rev-5/final, accessed 2025-11-02.

[^56]: AWS, "AWS CloudTrail User Guide," https://docs.aws.amazon.com/awscloudtrail/latest/userguide/cloudtrail-user-guide.html, accessed 2025-11-02.

[^57]: Apache Kafka Documentation, "Log Compaction," https://kafka.apache.org/documentation/#compaction, accessed 2025-11-02.

[^58]: PostgreSQL Documentation, "Triggers," https://www.postgresql.org/docs/current/triggers.html, accessed 2025-11-02.

---
## Appendix A: Recommended Libraries

| Category | Library | Version | Justification |
|----------|---------|---------|---------------|
| **Web Framework** | fastapi | ^0.100.0 | Async-first, OpenAPI integration, DI system |
| **ASGI Server** | uvicorn[standard] | ^0.23.0 | Production-grade async server with HTTP/2 |
| **Configuration** | pydantic-settings | ^2.0.0 | Type-safe settings management |
| **Structured Logging** | structlog | ^23.0.0 | Structured logging with context binding |
| **Cache Client** | redis[asyncio] | ^5.0.0 | Official async Redis client |
| **Database** | sqlalchemy[asyncio] | ^2.0.0 | Async ORM with type hints |
| **Testing** | pytest | ^7.4.0 | Feature-rich testing framework |
| **Async Testing** | pytest-asyncio | ^0.21.0 | Async test support for pytest |
| **Telemetry (Traces)** | opentelemetry-api | ^1.20.0 | Vendor-neutral tracing API |
| **Telemetry (SDK)** | opentelemetry-sdk | ^1.20.0 | OpenTelemetry SDK implementation |
| **Telemetry (OTLP)** | opentelemetry-exporter-otlp | ^1.20.0 | OTLP exporter for Jaeger/Tempo |
| **Telemetry (FastAPI)** | opentelemetry-instrumentation-fastapi | ^0.41b0 | Auto-instrumentation for FastAPI |
| **Telemetry (SQLAlchemy)** | opentelemetry-instrumentation-sqlalchemy | ^0.41b0 | Auto-instrumentation for SQLAlchemy |
| **Metrics** | prometheus-client | ^0.18.0 | Prometheus metrics client |
| **Audit Logging** | *(use Pydantic + SQLAlchemy)* | N/A | No separate library needed (custom implementation) |
| **Event Streaming** | aiokafka | ^0.8.0 | Async Kafka client (optional for audit events) |

---

## References

[^1]: FastAPI Documentation, "Settings and Environment Variables," https://fastapi.tiangolo.com/advanced/settings/, accessed 2025-11-01.

[^2]: FastAPI Documentation, "Dependencies - First Steps," https://fastapi.tiangolo.com/tutorial/dependencies/, accessed 2025-11-01.

[^3]: TestDriven.io, "FastAPI with Async SQLAlchemy, SQLModel, and Alembic," https://testdriven.io/blog/fastapi-sqlmodel/, accessed 2025-11-01.

[^4]: Angelos Panagiotopoulos, "Structured logging using structlog and FastAPI," https://www.angelospanag.me/blog/structured-logging-using-structlog-and-fastapi, accessed 2025-11-01.

[^5]: Medium, "Building a REST API with FastAPI and Redis Caching," https://medium.com/@suganthi2496/building-a-rest-api-with-fastapi-and-redis-caching-278c4dc07d70, accessed 2025-11-01.

[^6]: Fueled Engineering, "Clean Architecture with FastAPI," https://fueled.com/the-cache/posts/backend/clean-architecture-with-fastapi/, accessed 2025-11-01.

[^7]: The Twelve-Factor App, "III. Config," https://12factor.net/config, accessed 2025-11-01.

[^8]: PyPI, "python-dotenv," https://pypi.org/project/python-dotenv/, accessed 2025-11-01.

[^9]: Dynaconf Documentation, "Settings Management," https://www.dynaconf.com/, accessed 2025-11-01.

[^10]: PyPI, "python-json-logger," https://pypi.org/project/python-json-logger/, accessed 2025-11-01.

[^11]: Loguru Documentation, "Loguru Python Logging Made Simple," https://loguru.readthedocs.io/, accessed 2025-11-01.

[^12]: redis-py Documentation, "Async Usage," https://redis-py.readthedocs.io/en/stable/examples/asyncio_examples.html, accessed 2025-11-01.

[^13]: PyPI, "async-lru," https://pypi.org/project/async-lru/, accessed 2025-11-01.

[^14]: Redis Documentation, "Caching Patterns," https://redis.io/docs/manual/patterns/caching/, accessed 2025-11-01.

[^15]: FastAPI Documentation, "Lifespan Events," https://fastapi.tiangolo.com/advanced/events/, accessed 2025-11-01.

[^16]: Stack Overflow, "How to use FastAPI's lifespan to manage connection pool creation and release?" https://stackoverflow.com/questions/77765355/how-to-use-fastapis-lifespan-to-manage-connection-pool-creation-and-relase, accessed 2025-11-01.

[^17]: Medium, "Setting Up and Using an Async Redis Client in FastAPI (The Right Way!)," https://medium.com/@geetansh2k1/setting-up-and-using-an-async-redis-client-in-fastapi-the-right-way-0409ad3812e6, accessed 2025-11-01.

[^18]: Stack Overflow, "What is the recommended way to instantiate and pass around a redis client with FastAPI," https://stackoverflow.com/questions/73563804/what-is-the-recommended-way-to-instantiate-and-pass-around-a-redis-client-with-f, accessed 2025-11-01.

[^19]: Developer.redis.com, "Using Redis with FastAPI," https://developer.redis.com/develop/python/fastapi/, accessed 2025-11-01.

[^20]: Medium, "The Repository Pattern in Python: Write Flexible, Testable Code," https://medium.com/@kmuhsinn/the-repository-pattern-in-python-write-flexible-testable-code-with-fastapi-examples-aa0105e40776, accessed 2025-11-01.

[^21]: DEV Community, "Asynchronous Database Sessions in FastAPI with SQLAlchemy," https://dev.to/akarshan/asynchronous-database-sessions-in-fastapi-with-sqlalchemy-1o7e, accessed 2025-11-01.

[^22]: Medium, "Setting up a FastAPI App with Async SQLAlchemy 2.0 & Pydantic V2," https://medium.com/@tclaitken/setting-up-a-fastapi-app-with-async-sqlalchemy-2-0-pydantic-v2-e6c540be4308, accessed 2025-11-01.

[^23]: Stack Overflow, "What is the best approach to hooking up database in FastAPI?" https://stackoverflow.com/questions/68793314/what-is-the-best-approach-to-hooking-up-database-in-fastapi, accessed 2025-11-01.

[^24]: FastAPI Documentation, "Advanced - Lifespan Events," https://fastapi.tiangolo.com/advanced/events/, accessed 2025-11-01.

[^25]: Praciano, "FastAPI and async SQLAlchemy 2.0 with pytest done right," https://praciano.com.br/fastapi-and-async-sqlalchemy-20-with-pytest-done-right.html, accessed 2025-11-01.

[^26]: SigNoz, "Complete Guide to Logging with StructLog in Python," https://signoz.io/guides/structlog/, accessed 2025-11-01.

[^27]: FastAPI Documentation, "Settings and Environment Variables - Settings in a dependency," https://fastapi.tiangolo.com/advanced/settings/#settings-in-a-dependency, accessed 2025-11-01.

[^28]: Pydantic Documentation, "Pydantic Settings - Field value priority," https://docs.pydantic.dev/latest/concepts/pydantic_settings/#field-value-priority, accessed 2025-11-01.

[^29]: Real Python, "Python Application Layouts: A Reference," https://realpython.com/python-application-layouts/, accessed 2025-11-01.

[^30]: TestDriven.io, "Test-Driven Development with FastAPI and Docker," https://testdriven.io/courses/tdd-fastapi/, accessed 2025-11-01.

[^31]: Dynaconf Documentation, "Advanced Usage - Multiple Environments," https://www.dynaconf.com/envvars/, accessed 2025-11-01.

[^32]: Pydantic Documentation, "Settings Management - Field Types," https://docs.pydantic.dev/latest/concepts/pydantic_settings/#field-types, accessed 2025-11-01.

[^33]: Pydantic Documentation, "Type Adapter - Coercion," https://docs.pydantic.dev/latest/concepts/type_adapter/#type-coercion, accessed 2025-11-01.

[^34]: Pydantic Documentation, "Validators," https://docs.pydantic.dev/latest/concepts/validators/, accessed 2025-11-01.

[^35]: SQLAlchemy Documentation, "Declarative Mapping - Using Annotated Declarative Table," https://docs.sqlalchemy.org/en/20/orm/declarative_tables.html#using-annotated-declarative-table-type-annotated-forms-for-mapped-column, accessed 2025-11-01.

[^36]: FastAPI Documentation, "SQL (Relational) Databases - Using Pydantic with SQLAlchemy," https://fastapi.tiangolo.com/tutorial/sql-databases/#create-pydantic-models, accessed 2025-11-01.

[^37]: FastAPI Documentation, "Request Body - Validation," https://fastapi.tiangolo.com/tutorial/body/#request-body-validation, accessed 2025-11-01.

[^38]: RFC 7807, "Problem Details for HTTP APIs," https://datatracker.ietf.org/doc/html/rfc7807, accessed 2025-11-01.

[^39]: FastAPI Documentation, "Handling Errors - Custom Exception Handlers," https://fastapi.tiangolo.com/tutorial/handling-errors/#install-custom-exception-handlers, accessed 2025-11-01.

[^40]: FastAPI Documentation, "Handling Errors - Override the Default Exception Handlers," https://fastapi.tiangolo.com/tutorial/handling-errors/#override-the-default-exception-handlers, accessed 2025-11-01.
