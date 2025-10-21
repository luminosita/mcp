# CLAUDE-architecture-middleware.md - Exception Handling & CORS


> **Specialized Guide**: Exception handling patterns and CORS configuration for FastAPI REST API applications.

> **Scope**: This guide covers FastAPI REST endpoint exception handling. For MCP tools/resources, see **[CLAUDE-mcp.md](./CLAUDE-mcp.md)** which uses FastMCP ErrorHandlingMiddleware with JSON-RPC error format instead.

## 🔒 Exception Handling (FastAPI REST Endpoints)

**Note**: This section applies to **FastAPI REST API endpoints only**. For MCP tools and resources, use standard Python exceptions (FileNotFoundError, ValueError, etc.) and let FastMCP ErrorHandlingMiddleware convert to JSON-RPC format. See **[CLAUDE-mcp.md § Exception Handling for MCP Tools](./CLAUDE-mcp.md#🛡️-exception-handling-for-mcp-tools)** for MCP-specific patterns.

### Custom Exceptions

```python
# src/mcp_server/core/exceptions.py
class AppException(Exception):
    """Base application exception."""
    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)

class UserNotFoundError(AppException):
    """User not found exception."""
    def __init__(self, message: str = "User not found"):
        super().__init__(message, status_code=404)

class DuplicateEmailError(AppException):
    """Duplicate email exception."""
    def __init__(self, message: str = "Email already exists"):
        super().__init__(message, status_code=409)

class UnauthorizedError(AppException):
    """Unauthorized access exception."""
    def __init__(self, message: str = "Unauthorized"):
        super().__init__(message, status_code=401)

class ValidationError(AppException):
    """Validation error exception."""
    def __init__(self, message: str = "Validation failed"):
        super().__init__(message, status_code=422)
```

### Exception Handlers

```python
# src/mcp_server/core/exception_handlers.py
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from .exceptions import AppException
import logging

logger = logging.getLogger(__name__)

def setup_exception_handlers(app: FastAPI) -> None:
    """Setup application exception handlers."""

    @app.exception_handler(AppException)
    async def app_exception_handler(request: Request, exc: AppException):
        """Handle application exceptions."""
        logger.error(f"Application error: {exc.message}", exc_info=True)
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": exc.__class__.__name__,
                "message": exc.message,
                "path": str(request.url)
            }
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        """Handle unexpected exceptions."""
        logger.error(f"Unexpected error: {str(exc)}", exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": "InternalServerError",
                "message": "An unexpected error occurred",
                "path": str(request.url)
            }
        )
```

---

## 🌐 CORS (Cross-Origin Resource Sharing) Configuration

### Basic CORS Setup

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Basic CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend origin
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)
```

### Production CORS Configuration

```python
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from typing import List
import re
from pydantic_settings import BaseSettings

class CORSSettings(BaseSettings):
    """CORS configuration settings."""
    # Allowed origins (exact match)
    allowed_origins: List[str] = [
        "https://app.example.com",
        "https://admin.example.com",
    ]

    # Allowed origin patterns (regex)
    allowed_origin_patterns: List[str] = [
        r"^https://.*\.example\.com$",  # All subdomains
        r"^http://localhost:\d+$",       # Any localhost port (dev only)
    ]

    # CORS settings
    allow_credentials: bool = True
    allowed_methods: List[str] = ["GET", "POST", "PUT", "DELETE", "PATCH"]
    allowed_headers: List[str] = [
        "Content-Type",
        "Authorization",
        "X-Request-ID",
        "X-API-Key",
    ]
    expose_headers: List[str] = [
        "X-Total-Count",
        "X-Page-Count",
    ]
    max_age: int = 3600  # Cache preflight requests for 1 hour

def is_allowed_origin(origin: str, settings: CORSSettings) -> bool:
    """
    Check if origin is allowed.

    Validates against:
    1. Exact match in allowed_origins
    2. Pattern match in allowed_origin_patterns
    """
    # Check exact match
    if origin in settings.allowed_origins:
        return True

    # Check pattern match
    for pattern in settings.allowed_origin_patterns:
        if re.match(pattern, origin):
            return True

    return False

# Configure CORS
cors_settings = CORSSettings()

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_settings.allowed_origins,
    allow_origin_regex="|".join(cors_settings.allowed_origin_patterns),
    allow_credentials=cors_settings.allow_credentials,
    allow_methods=cors_settings.allowed_methods,
    allow_headers=cors_settings.allowed_headers,
    expose_headers=cors_settings.expose_headers,
    max_age=cors_settings.max_age,
)
```

### Custom CORS Middleware (Advanced Control)

```python
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from fastapi import Request
import re

class CustomCORSMiddleware(BaseHTTPMiddleware):
    """
    Custom CORS middleware with fine-grained control.

    Features:
    - Dynamic origin validation
    - Per-route CORS policies
    - Credentials handling
    - Custom preflight optimization
    """

    def __init__(
        self,
        app,
        allowed_origins: List[str],
        allowed_origin_patterns: List[str],
        allow_credentials: bool = True,
        allowed_methods: List[str] = None,
        allowed_headers: List[str] = None,
        expose_headers: List[str] = None,
        max_age: int = 3600
    ):
        super().__init__(app)
        self.allowed_origins = set(allowed_origins)
        self.allowed_origin_patterns = [re.compile(p) for p in allowed_origin_patterns]
        self.allow_credentials = allow_credentials
        self.allowed_methods = allowed_methods or ["GET", "POST", "PUT", "DELETE"]
        self.allowed_headers = allowed_headers or ["*"]
        self.expose_headers = expose_headers or []
        self.max_age = max_age

    def is_origin_allowed(self, origin: str) -> bool:
        """Check if origin is allowed."""
        # Exact match
        if origin in self.allowed_origins:
            return True

        # Pattern match
        for pattern in self.allowed_origin_patterns:
            if pattern.match(origin):
                return True

        return False

    async def dispatch(self, request: Request, call_next):
        """Process CORS headers for all requests."""
        origin = request.headers.get("origin")

        # Handle preflight requests (OPTIONS)
        if request.method == "OPTIONS":
            return self.handle_preflight(request, origin)

        # Process actual request
        response = await call_next(request)

        # Add CORS headers to response
        if origin and self.is_origin_allowed(origin):
            response.headers["Access-Control-Allow-Origin"] = origin

            if self.allow_credentials:
                response.headers["Access-Control-Allow-Credentials"] = "true"

            if self.expose_headers:
                response.headers["Access-Control-Expose-Headers"] = ", ".join(
                    self.expose_headers
                )

        return response

    def handle_preflight(self, request: Request, origin: str) -> Response:
        """
        Handle CORS preflight (OPTIONS) request.

        Preflight optimization:
        - Cache preflight responses (max_age)
        - Validate requested method and headers
        - Return minimal response
        """
        # Validate origin
        if not origin or not self.is_origin_allowed(origin):
            return Response(status_code=403, content="Origin not allowed")

        # Get requested method and headers
        requested_method = request.headers.get("Access-Control-Request-Method")
        requested_headers = request.headers.get("Access-Control-Request-Headers", "")

        # Validate requested method
        if requested_method and requested_method not in self.allowed_methods:
            return Response(status_code=403, content="Method not allowed")

        # Build preflight response headers
        headers = {
            "Access-Control-Allow-Origin": origin,
            "Access-Control-Allow-Methods": ", ".join(self.allowed_methods),
            "Access-Control-Max-Age": str(self.max_age),
        }

        if self.allow_credentials:
            headers["Access-Control-Allow-Credentials"] = "true"

        # Handle requested headers
        if self.allowed_headers == ["*"]:
            # Allow all requested headers
            headers["Access-Control-Allow-Headers"] = requested_headers or "*"
        else:
            # Only allow specific headers
            headers["Access-Control-Allow-Headers"] = ", ".join(self.allowed_headers)

        if self.expose_headers:
            headers["Access-Control-Expose-Headers"] = ", ".join(self.expose_headers)

        return Response(status_code=200, headers=headers)

# Usage
app.add_middleware(
    CustomCORSMiddleware,
    allowed_origins=["https://app.example.com"],
    allowed_origin_patterns=[r"^https://.*\.example\.com$"],
    allow_credentials=True,
    allowed_methods=["GET", "POST", "PUT", "DELETE"],
    allowed_headers=["Content-Type", "Authorization"],
    expose_headers=["X-Total-Count"],
    max_age=3600
)
```

### Per-Route CORS Policies

```python
from fastapi import FastAPI, Request, Response
from typing import Optional, List
from functools import wraps

class RouteCORSPolicy:
    """Per-route CORS policy definition."""
    def __init__(
        self,
        allowed_origins: List[str],
        allow_credentials: bool = False,
        allowed_methods: Optional[List[str]] = None,
        allowed_headers: Optional[List[str]] = None
    ):
        self.allowed_origins = set(allowed_origins)
        self.allow_credentials = allow_credentials
        self.allowed_methods = allowed_methods or ["GET", "POST"]
        self.allowed_headers = allowed_headers or ["Content-Type"]

def cors_route(policy: RouteCORSPolicy):
    """
    Decorator for route-specific CORS policies.

    Usage:
        @app.get("/api/public")
        @cors_route(public_policy)
        async def public_endpoint():
            return {"data": "public"}
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, request: Request, **kwargs):
            origin = request.headers.get("origin")

            # Handle preflight
            if request.method == "OPTIONS":
                if origin and origin in policy.allowed_origins:
                    headers = {
                        "Access-Control-Allow-Origin": origin,
                        "Access-Control-Allow-Methods": ", ".join(policy.allowed_methods),
                        "Access-Control-Allow-Headers": ", ".join(policy.allowed_headers),
                        "Access-Control-Max-Age": "3600",
                    }
                    if policy.allow_credentials:
                        headers["Access-Control-Allow-Credentials"] = "true"

                    return Response(status_code=200, headers=headers)
                else:
                    return Response(status_code=403)

            # Execute route
            response = await func(*args, request=request, **kwargs)

            # Add CORS headers
            if origin and origin in policy.allowed_origins:
                response.headers["Access-Control-Allow-Origin"] = origin
                if policy.allow_credentials:
                    response.headers["Access-Control-Allow-Credentials"] = "true"

            return response

        return wrapper
    return decorator

# Define policies
public_policy = RouteCORSPolicy(
    allowed_origins=["*"],
    allow_credentials=False
)

authenticated_policy = RouteCORSPolicy(
    allowed_origins=["https://app.example.com"],
    allow_credentials=True,
    allowed_methods=["GET", "POST", "PUT", "DELETE"]
)

# Apply to routes
@app.get("/api/public")
@cors_route(public_policy)
async def public_endpoint(request: Request):
    """Public endpoint with relaxed CORS."""
    return {"data": "public"}

@app.post("/api/secure")
@cors_route(authenticated_policy)
async def secure_endpoint(request: Request):
    """Secure endpoint with strict CORS."""
    return {"data": "secure"}
```

### Environment-Based CORS Configuration

```python
from pydantic_settings import BaseSettings
from typing import List
from enum import Enum

class Environment(str, Enum):
    """Application environment."""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"

class Settings(BaseSettings):
    """Application settings with environment-aware CORS."""
    environment: Environment = Environment.DEVELOPMENT

    @property
    def cors_origins(self) -> List[str]:
        """Get CORS origins based on environment."""
        if self.environment == Environment.DEVELOPMENT:
            return [
                "http://localhost:3000",
                "http://localhost:8080",
                "http://127.0.0.1:3000",
            ]
        elif self.environment == Environment.STAGING:
            return [
                "https://staging.example.com",
                "https://staging-admin.example.com",
            ]
        else:  # PRODUCTION
            return [
                "https://app.example.com",
                "https://admin.example.com",
            ]

    @property
    def cors_allow_credentials(self) -> bool:
        """Allow credentials in CORS."""
        # Disable credentials in development for easier testing
        return self.environment != Environment.DEVELOPMENT

    @property
    def cors_max_age(self) -> int:
        """CORS preflight cache duration."""
        # Longer cache in production
        if self.environment == Environment.PRODUCTION:
            return 7200  # 2 hours
        return 600  # 10 minutes

settings = Settings()

# Configure CORS based on environment
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=settings.cors_allow_credentials,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    allow_headers=["*"],
    max_age=settings.cors_max_age,
)
```

### CORS Security Best Practices

```python
"""
CORS Security Guidelines:

✅ DO:

1. Explicitly list allowed origins
   - allow_origins=["https://app.example.com"]
   - Use environment variables for different environments

2. Use allow_credentials=True only when necessary
   - Required for cookies, authorization headers
   - Must specify exact origins (not "*")

3. Limit allowed methods
   - allow_methods=["GET", "POST", "PUT", "DELETE"]
   - Don't use ["*"] in production

4. Limit allowed headers
   - List specific headers needed
   - ["Content-Type", "Authorization", "X-API-Key"]

5. Set appropriate max_age
   - Cache preflight requests (3600-7200 seconds)
   - Reduces OPTIONS requests

6. Use regex patterns carefully
   - Validate subdomain patterns: r"^https://.*\.example\.com$"
   - Escape special characters

7. Log CORS violations
   - Monitor rejected origins
   - Detect potential attacks

❌ DON'T:

1. Use allow_origins=["*"] with credentials
   - Security risk: exposes authentication to all origins
   - Browser will reject this configuration

2. Use wildcard (*) in production
   - Allow specific origins only
   - Wildcard acceptable only for public APIs

3. Allow all methods
   - Limit to what's actually needed
   - Reduces attack surface

4. Trust user-provided origin header
   - Always validate against whitelist
   - Origin header can be spoofed (but browser enforces it)

5. Forget about preflight caching
   - Missing max_age causes excessive OPTIONS requests
   - Set reasonable cache duration

6. Mix HTTP and HTTPS origins
   - Use HTTPS everywhere in production
   - HTTP allowed only for localhost development

EXAMPLE - Secure Production Configuration:

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://app.example.com",
        "https://admin.example.com"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Content-Type", "Authorization", "X-Request-ID"],
    expose_headers=["X-Total-Count", "X-Page-Number"],
    max_age=3600
)
"""
```

### Troubleshooting CORS Issues

```python
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
import logging

logger = logging.getLogger(__name__)

class CORSDebugMiddleware(BaseHTTPMiddleware):
    """
    Debug middleware to log CORS requests.

    Helps diagnose CORS issues in development.
    """

    async def dispatch(self, request: Request, call_next):
        origin = request.headers.get("origin")

        # Log CORS-related info
        if origin:
            logger.info(f"CORS Request: {request.method} {request.url.path}")
            logger.info(f"  Origin: {origin}")
            logger.info(f"  Headers: {dict(request.headers)}")

            if request.method == "OPTIONS":
                logger.info("  Preflight Request Detected")
                logger.info(f"    Requested Method: {request.headers.get('Access-Control-Request-Method')}")
                logger.info(f"    Requested Headers: {request.headers.get('Access-Control-Request-Headers')}")

        response = await call_next(request)

        # Log CORS response headers
        if origin:
            cors_headers = {
                k: v for k, v in response.headers.items()
                if k.lower().startswith('access-control-')
            }
            logger.info(f"  Response CORS Headers: {cors_headers}")

        return response

# Use in development only
if settings.environment == Environment.DEVELOPMENT:
    app.add_middleware(CORSDebugMiddleware)

# Common CORS errors and solutions:
"""
1. "No 'Access-Control-Allow-Origin' header present"
   - Origin not in allowed_origins list
   - Check CORS middleware is installed
   - Verify origin matches exactly (including protocol and port)

2. "Credentials flag is true, but Access-Control-Allow-Credentials header is not present"
   - Set allow_credentials=True in CORS config
   - Ensure origin is specific (not "*")

3. "Method X not allowed by Access-Control-Allow-Methods"
   - Add method to allowed_methods list
   - Check if using correct HTTP method

4. "Request header X not allowed by Access-Control-Allow-Headers"
   - Add header to allowed_headers list
   - Or use allow_headers=["*"] (not recommended for production)

5. "Preflight request didn't succeed"
   - OPTIONS request failing
   - Check if endpoint exists
   - Verify CORS middleware is before route handlers
"""
```

---
