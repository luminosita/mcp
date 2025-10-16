# CLAUDE-validation-api.md - API Rate Limiting & Validation


> **Specialized Guide**: API rate limiting, request validation patterns, error handling, and security checklists.

> **Specialized Guide**: Comprehensive Pydantic validation patterns, security best practices, and input handling for Python projects.
## 🚦 API Rate Limiting

### slowapi Rate Limiting (Redis-Based)

```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import FastAPI, Request
from redis.asyncio import Redis
import redis.asyncio as redis

app = FastAPI()

# Initialize Redis connection
redis_client = redis.from_url("redis://localhost:6379", decode_responses=True)

# Initialize limiter
limiter = Limiter(
    key_func=get_remote_address,  # Rate limit by IP
    storage_uri="redis://localhost:6379",
    default_limits=["100/hour"]  # Global default
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Per-route rate limiting
@app.get("/api/data")
@limiter.limit("5/minute")  # 5 requests per minute
async def get_data(request: Request):
    """Endpoint with rate limiting."""
    return {"data": "value"}

@app.post("/api/upload")
@limiter.limit("10/hour")  # Stricter limit for expensive operations
async def upload_data(request: Request):
    """Upload endpoint with strict rate limit."""
    return {"status": "uploaded"}

# Multiple rate limits
@app.get("/api/search")
@limiter.limit("10/minute;100/hour")  # Both minute and hour limits
async def search(request: Request):
    """Search with multiple rate limit windows."""
    return {"results": []}
```

### Custom Rate Limiter with Redis

```python
from datetime import datetime, timedelta
from typing import Optional
from fastapi import HTTPException, status
import redis.asyncio as redis
from pydantic import BaseModel

class RateLimitConfig(BaseModel):
    """Rate limit configuration."""
    max_requests: int
    window_seconds: int
    identifier: str  # User ID or IP address

class TokenBucketLimiter:
    """
    Token bucket rate limiting algorithm.

    Advantages:
    - Allows burst traffic
    - Smooth rate limiting
    - Configurable bucket size and refill rate
    """

    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client

    async def is_allowed(
        self,
        identifier: str,
        max_tokens: int,
        refill_rate: float,  # Tokens per second
        bucket_size: int
    ) -> bool:
        """
        Check if request is allowed under token bucket algorithm.

        Args:
            identifier: User ID or IP address
            max_tokens: Maximum tokens in bucket
            refill_rate: Token refill rate (per second)
            bucket_size: Maximum bucket capacity

        Returns:
            True if request allowed, False otherwise
        """
        now = datetime.utcnow().timestamp()
        key = f"rate_limit:token_bucket:{identifier}"

        # Get current bucket state
        bucket_data = await self.redis.hgetall(key)

        if not bucket_data:
            # Initialize bucket
            tokens = bucket_size - 1  # Consume one token
            last_refill = now
        else:
            tokens = float(bucket_data.get('tokens', bucket_size))
            last_refill = float(bucket_data.get('last_refill', now))

            # Calculate tokens to add based on time elapsed
            elapsed = now - last_refill
            tokens_to_add = elapsed * refill_rate
            tokens = min(bucket_size, tokens + tokens_to_add)

            # Try to consume token
            if tokens >= 1:
                tokens -= 1
            else:
                return False  # No tokens available

        # Update bucket state
        await self.redis.hset(key, mapping={
            'tokens': str(tokens),
            'last_refill': str(now)
        })
        await self.redis.expire(key, int(bucket_size / refill_rate) + 60)

        return True

class SlidingWindowLimiter:
    """
    Sliding window rate limiting algorithm.

    Advantages:
    - More accurate than fixed window
    - Prevents burst at window boundaries
    - Smooth rate limiting
    """

    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client

    async def is_allowed(
        self,
        identifier: str,
        max_requests: int,
        window_seconds: int
    ) -> tuple[bool, dict]:
        """
        Check if request is allowed under sliding window algorithm.

        Returns:
            Tuple of (is_allowed, rate_limit_info)
        """
        now = datetime.utcnow().timestamp()
        window_start = now - window_seconds
        key = f"rate_limit:sliding:{identifier}"

        # Remove old entries
        await self.redis.zremrangebyscore(key, 0, window_start)

        # Count requests in current window
        request_count = await self.redis.zcard(key)

        # Check if limit exceeded
        if request_count >= max_requests:
            # Get oldest request timestamp for retry-after calculation
            oldest = await self.redis.zrange(key, 0, 0, withscores=True)
            if oldest:
                retry_after = int(oldest[0][1] + window_seconds - now)
            else:
                retry_after = window_seconds

            return False, {
                'allowed': False,
                'limit': max_requests,
                'remaining': 0,
                'reset': int(now + retry_after),
                'retry_after': retry_after
            }

        # Add current request
        await self.redis.zadd(key, {str(now): now})
        await self.redis.expire(key, window_seconds)

        return True, {
            'allowed': True,
            'limit': max_requests,
            'remaining': max_requests - request_count - 1,
            'reset': int(now + window_seconds)
        }

# Initialize limiters
token_bucket = TokenBucketLimiter(redis_client)
sliding_window = SlidingWindowLimiter(redis_client)
```

### Rate Limiting Dependency

```python
from fastapi import Depends, Request, HTTPException, status
from typing import Callable

async def get_client_identifier(request: Request) -> str:
    """
    Get client identifier for rate limiting.

    Priority:
    1. Authenticated user ID (if available)
    2. API key (if provided)
    3. IP address (fallback)
    """
    # Check for authenticated user
    user = getattr(request.state, 'user', None)
    if user:
        return f"user:{user.id}"

    # Check for API key
    api_key = request.headers.get('X-API-Key')
    if api_key:
        return f"api_key:{api_key}"

    # Fallback to IP address
    forwarded = request.headers.get('X-Forwarded-For')
    if forwarded:
        return f"ip:{forwarded.split(',')[0].strip()}"

    return f"ip:{request.client.host}"

def rate_limit(
    max_requests: int,
    window_seconds: int,
    identifier_func: Callable = get_client_identifier
):
    """
    Dependency factory for rate limiting.

    Usage:
        @app.get("/api/data")
        async def get_data(
            _: None = Depends(rate_limit(max_requests=10, window_seconds=60))
        ):
            return {"data": "value"}
    """
    async def check_rate_limit(request: Request) -> None:
        # Get client identifier
        identifier = await identifier_func(request)

        # Check rate limit
        allowed, info = await sliding_window.is_allowed(
            identifier,
            max_requests,
            window_seconds
        )

        # Set rate limit headers
        request.state.rate_limit_info = info

        if not allowed:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail={
                    "error": "Rate limit exceeded",
                    "retry_after": info['retry_after']
                },
                headers={
                    "X-RateLimit-Limit": str(info['limit']),
                    "X-RateLimit-Remaining": str(info['remaining']),
                    "X-RateLimit-Reset": str(info['reset']),
                    "Retry-After": str(info['retry_after'])
                }
            )

    return check_rate_limit

# Usage
@app.get("/api/protected")
async def protected_endpoint(
    request: Request,
    _: None = Depends(rate_limit(max_requests=10, window_seconds=60))
):
    """Endpoint with rate limiting."""
    return {"data": "value"}
```

### Rate Limit Response Headers Middleware

```python
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

class RateLimitHeadersMiddleware(BaseHTTPMiddleware):
    """
    Add rate limit headers to all responses.

    Standard headers:
    - X-RateLimit-Limit: Maximum requests allowed
    - X-RateLimit-Remaining: Remaining requests
    - X-RateLimit-Reset: Unix timestamp when limit resets
    - Retry-After: Seconds to wait (if rate limited)
    """

    async def dispatch(self, request: Request, call_next):
        # Process request
        response = await call_next(request)

        # Add rate limit headers if available
        if hasattr(request.state, 'rate_limit_info'):
            info = request.state.rate_limit_info

            response.headers['X-RateLimit-Limit'] = str(info['limit'])
            response.headers['X-RateLimit-Remaining'] = str(info['remaining'])
            response.headers['X-RateLimit-Reset'] = str(info['reset'])

            if not info['allowed']:
                response.headers['Retry-After'] = str(info.get('retry_after', 60))

        return response

# Add middleware
app.add_middleware(RateLimitHeadersMiddleware)
```

### Per-User Rate Limiting

```python
from fastapi.security import HTTPBearer
from typing import Optional

security = HTTPBearer()

class UserRateLimiter:
    """
    Rate limit based on user tier/subscription.

    Different limits for different user types:
    - Free users: 100 requests/hour
    - Basic users: 1000 requests/hour
    - Premium users: 10000 requests/hour
    """

    RATE_LIMITS = {
        'free': (100, 3600),      # 100 requests per hour
        'basic': (1000, 3600),    # 1000 requests per hour
        'premium': (10000, 3600),  # 10000 requests per hour
        'anonymous': (10, 3600)    # 10 requests per hour for unauthenticated
    }

    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
        self.limiter = SlidingWindowLimiter(redis_client)

    async def check_user_limit(
        self,
        user_id: Optional[str],
        user_tier: str = 'free'
    ) -> tuple[bool, dict]:
        """
        Check rate limit for specific user.

        Returns:
            Tuple of (is_allowed, rate_limit_info)
        """
        # Get rate limit config for user tier
        max_requests, window = self.RATE_LIMITS.get(
            user_tier,
            self.RATE_LIMITS['free']
        )

        # Use user ID or mark as anonymous
        identifier = f"user:{user_id}" if user_id else "anonymous"

        # Check rate limit
        return await self.limiter.is_allowed(
            identifier,
            max_requests,
            window
        )

user_limiter = UserRateLimiter(redis_client)

def user_rate_limit():
    """
    Dependency for per-user rate limiting.

    Usage:
        @app.get("/api/user/data")
        async def get_user_data(
            user: TokenData = Depends(get_current_user),
            _: None = Depends(user_rate_limit())
        ):
            return {"data": "value"}
    """
    async def check_limit(request: Request) -> None:
        # Get user from request state (if authenticated)
        user = getattr(request.state, 'user', None)

        if user:
            user_id = user.id
            user_tier = getattr(user, 'tier', 'free')
        else:
            user_id = None
            user_tier = 'anonymous'

        # Check rate limit
        allowed, info = await user_limiter.check_user_limit(user_id, user_tier)

        # Store info for headers
        request.state.rate_limit_info = info

        if not allowed:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail={
                    "error": "Rate limit exceeded for your tier",
                    "tier": user_tier,
                    "limit": info['limit'],
                    "retry_after": info.get('retry_after', 60)
                },
                headers={
                    "Retry-After": str(info.get('retry_after', 60))
                }
            )

    return check_limit

# Usage
@app.get("/api/user/data")
async def get_user_data(
    request: Request,
    _: None = Depends(user_rate_limit())
):
    """User-specific rate limited endpoint."""
    return {"data": "value"}
```

### Rate Limiting by Endpoint Cost

```python
from enum import IntEnum

class EndpointCost(IntEnum):
    """Cost of different endpoint operations."""
    READ = 1
    WRITE = 5
    SEARCH = 10
    EXPENSIVE = 50

class CostBasedLimiter:
    """
    Rate limit based on operation cost.

    Users have credit pool that refills over time.
    Different operations consume different amounts of credits.
    """

    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client

    async def consume_credits(
        self,
        identifier: str,
        cost: int,
        max_credits: int = 1000,
        refill_rate: float = 10.0  # Credits per second
    ) -> tuple[bool, int]:
        """
        Try to consume credits for operation.

        Args:
            identifier: User identifier
            cost: Credit cost of operation
            max_credits: Maximum credit pool size
            refill_rate: Credits refilled per second

        Returns:
            Tuple of (success, remaining_credits)
        """
        now = datetime.utcnow().timestamp()
        key = f"rate_limit:credits:{identifier}"

        # Get current credits
        credit_data = await self.redis.hgetall(key)

        if not credit_data:
            # Initialize credits
            credits = max_credits - cost
            last_refill = now
        else:
            credits = float(credit_data.get('credits', max_credits))
            last_refill = float(credit_data.get('last_refill', now))

            # Refill credits based on elapsed time
            elapsed = now - last_refill
            credits_to_add = elapsed * refill_rate
            credits = min(max_credits, credits + credits_to_add)

            # Try to consume credits
            if credits >= cost:
                credits -= cost
            else:
                return False, int(credits)

        # Update credit state
        await self.redis.hset(key, mapping={
            'credits': str(credits),
            'last_refill': str(now)
        })
        await self.redis.expire(key, 3600)

        return True, int(credits)

cost_limiter = CostBasedLimiter(redis_client)

def cost_based_limit(cost: EndpointCost):
    """
    Dependency for cost-based rate limiting.

    Usage:
        @app.get("/api/search")
        async def search(
            _: None = Depends(cost_based_limit(EndpointCost.SEARCH))
        ):
            return {"results": []}
    """
    async def check_credits(request: Request) -> None:
        identifier = await get_client_identifier(request)

        # Try to consume credits
        allowed, remaining = await cost_limiter.consume_credits(
            identifier,
            cost=cost
        )

        if not allowed:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail={
                    "error": "Insufficient credits",
                    "cost": cost,
                    "remaining": remaining
                }
            )

    return check_credits

# Usage with different costs
@app.get("/api/data")
async def get_data(
    _: None = Depends(cost_based_limit(EndpointCost.READ))
):
    """Low-cost read operation."""
    return {"data": "value"}

@app.post("/api/process")
async def process_data(
    _: None = Depends(cost_based_limit(EndpointCost.EXPENSIVE))
):
    """High-cost processing operation."""
    return {"status": "processed"}
```

### Distributed Rate Limiting (Redis Cluster)

```python
from redis.cluster import RedisCluster
from redis.cluster import ClusterNode

class DistributedRateLimiter:
    """
    Rate limiting across multiple servers using Redis Cluster.

    Ensures consistent rate limits even with multiple API servers.
    """

    def __init__(self, redis_nodes: list[ClusterNode]):
        """
        Initialize distributed rate limiter.

        Args:
            redis_nodes: List of Redis cluster nodes
        """
        self.redis = RedisCluster(
            startup_nodes=redis_nodes,
            decode_responses=True
        )

    async def check_limit_distributed(
        self,
        identifier: str,
        max_requests: int,
        window_seconds: int
    ) -> tuple[bool, dict]:
        """
        Check rate limit across distributed system.

        Uses Redis transactions for atomic operations.
        """
        now = int(datetime.utcnow().timestamp())
        window_start = now - window_seconds
        key = f"rate_limit:distributed:{identifier}"

        # Use Lua script for atomic operation
        lua_script = """
        local key = KEYS[1]
        local now = tonumber(ARGV[1])
        local window_start = tonumber(ARGV[2])
        local max_requests = tonumber(ARGV[3])
        local window_seconds = tonumber(ARGV[4])

        -- Remove old entries
        redis.call('ZREMRANGEBYSCORE', key, 0, window_start)

        -- Count requests in window
        local count = redis.call('ZCARD', key)

        if count >= max_requests then
            return {0, count, 0}
        end

        -- Add current request
        redis.call('ZADD', key, now, now)
        redis.call('EXPIRE', key, window_seconds)

        return {1, max_requests, max_requests - count - 1}
        """

        # Execute Lua script
        result = await self.redis.eval(
            lua_script,
            1,
            key,
            now,
            window_start,
            max_requests,
            window_seconds
        )

        allowed, limit, remaining = result

        return bool(allowed), {
            'allowed': bool(allowed),
            'limit': limit,
            'remaining': remaining,
            'reset': now + window_seconds
        }

# Initialize distributed limiter
distributed_limiter = DistributedRateLimiter([
    ClusterNode("redis-node-1", 6379),
    ClusterNode("redis-node-2", 6379),
    ClusterNode("redis-node-3", 6379)
])
```

### Complete Rate Limiting Example

```python
@app.get("/api/complete-rate-limit")
async def complete_rate_limit_example(
    request: Request,
    user: Optional[TokenData] = Depends(get_current_user),
    _: None = Depends(user_rate_limit())
):
    """
    Complete endpoint with:
    - Per-user rate limiting
    - Rate limit headers
    - Proper error handling
    """
    # Rate limit info available in request.state
    rate_info = request.state.rate_limit_info

    return {
        "data": "value",
        "rate_limit": {
            "limit": rate_info['limit'],
            "remaining": rate_info['remaining'],
            "reset": rate_info['reset']
        }
    }

# Custom rate limit exceeded handler
@app.exception_handler(HTTPException)
async def rate_limit_exception_handler(request: Request, exc: HTTPException):
    """Custom handler for rate limit errors."""
    if exc.status_code == 429:
        return JSONResponse(
            status_code=429,
            content={
                "error": "Rate limit exceeded",
                "message": "Too many requests. Please try again later.",
                "retry_after": exc.headers.get("Retry-After", 60)
            },
            headers=exc.headers
        )

    # Re-raise other exceptions
    raise exc
```

---

## 🔍 API Validation Patterns

### FastAPI Integration

```python
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field, field_validator
from typing import Annotated

app = FastAPI()

class ItemCreate(BaseModel):
    """Item creation schema."""
    name: Annotated[str, Field(
        min_length=1,
        max_length=100,
        description="Item name",
        examples=["Widget"]
    )]
    price: Annotated[float, Field(
        gt=0,
        le=1000000,
        description="Price in USD",
        examples=[19.99]
    )]
    quantity: Annotated[int, Field(
        ge=0,
        description="Available quantity",
        examples=[100]
    )]

@app.post("/items/", response_model=ItemResponse, status_code=status.HTTP_201_CREATED)
async def create_item(item: ItemCreate) -> ItemResponse:
    """Create a new item with validation."""
    # Pydantic automatically validates the input
    # If validation fails, returns 422 Unprocessable Entity
    return ItemResponse(**item.model_dump(), id=1)
```

### Error Handling

```python
from pydantic import ValidationError
from fastapi import Request, status
from fastapi.responses import JSONResponse

@app.exception_handler(ValidationError)
async def validation_exception_handler(request: Request, exc: ValidationError):
    """Handle Pydantic validation errors."""
    errors = []
    for error in exc.errors():
        errors.append({
            "field": ".".join(str(loc) for loc in error["loc"]),
            "message": error["msg"],
            "type": error["type"],
        })

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": "Validation error",
            "errors": errors
        }
    )
```

---

## 🔐 Security Best Practices

### Password Handling

```python
from pydantic import BaseModel, SecretStr, field_validator
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserLogin(BaseModel):
    """User login with secure password handling."""
    email: str
    password: SecretStr  # Never logged or serialized

    def verify_password(self, hashed_password: str) -> bool:
        """Verify password against hash."""
        return pwd_context.verify(
            self.password.get_secret_value(),
            hashed_password
        )

class UserPasswordChange(BaseModel):
    """Password change with validation."""
    current_password: SecretStr
    new_password: SecretStr
    confirm_password: SecretStr

    @model_validator(mode='after')
    def validate_passwords(self) -> 'UserPasswordChange':
        """Validate password change requirements."""
        new_pwd = self.new_password.get_secret_value()
        confirm_pwd = self.confirm_password.get_secret_value()

        if new_pwd != confirm_pwd:
            raise ValueError('New passwords do not match')

        if len(new_pwd) < 12:
            raise ValueError('Password must be at least 12 characters')

        return self
```

### Token Validation

```python
from pydantic import BaseModel, Field, field_validator
import secrets

class APIToken(BaseModel):
    """API token with validation."""
    token: str = Field(min_length=32, max_length=256)

    @field_validator('token')
    @classmethod
    def validate_token_format(cls, v: str) -> str:
        """Ensure token is properly formatted."""
        if not re.match(r'^[A-Za-z0-9_-]+$', v):
            raise ValueError('Invalid token format')
        return v

def generate_secure_token() -> str:
    """Generate cryptographically secure token."""
    return secrets.token_urlsafe(32)
```

---

## ⚠️ Validation Best Practices

1. **Validate at boundaries** - All external inputs
2. **Use Field constraints** - Min/max length, patterns
3. **Custom validators for complex logic** - Business rules
4. **Fail fast** - Validate early in the request lifecycle
5. **Clear error messages** - Help users fix issues
6. **Sanitize HTML content** - Prevent XSS attacks
7. **Prevent SQL injection** - Validate queries
8. **Block path traversal** - Secure file operations
9. **Use SecretStr for passwords** - Never log secrets
10. **Validate in context** - Consider related fields

---

## 📋 Security Checklist

- [ ] All user inputs validated with Pydantic
- [ ] Field constraints defined (min/max, patterns)
- [ ] Custom validators for complex rules
- [ ] HTML content sanitized (bleach)
- [ ] SQL injection prevented
- [ ] Path traversal blocked
- [ ] Passwords use SecretStr
- [ ] Tokens validated and secure
- [ ] Environment variables validated
- [ ] Error messages don't leak sensitive data

---

**Back to [Core Guide](./CLAUDE-core.md)**
