# CLAUDE-validation-auth.md - JWT Authentication & Authorization


> **Specialized Guide**: JWT token generation, validation, refresh flow, blacklist strategies, and security considerations.

> **Specialized Guide**: Comprehensive Pydantic validation patterns, security best practices, and input handling for Python projects.
## 🔐 JWT Authentication & Authorization

### JWT Token Generation

```python
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field

# Token configuration
SECRET_KEY = "your-secret-key-here"  # Load from environment
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

class TokenPayload(BaseModel):
    """JWT token payload structure."""
    sub: str = Field(description="Subject (user ID)")
    exp: datetime = Field(description="Expiration timestamp")
    iat: datetime = Field(description="Issued at timestamp")
    token_type: str = Field(description="access or refresh")
    scopes: list[str] = Field(default_factory=list, description="User permissions")

class TokenData(BaseModel):
    """Validated token data."""
    user_id: str
    scopes: list[str] = []

class Token(BaseModel):
    """Token response model."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int

def create_access_token(
    data: Dict[str, Any],
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    Create JWT access token with claims.

    Args:
        data: Token payload data (user_id, scopes, etc.)
        expires_delta: Custom expiration time

    Returns:
        Encoded JWT token string
    """
    to_encode = data.copy()

    # Set expiration
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    # Add standard claims
    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "token_type": "access"
    })

    # Encode token
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def create_refresh_token(user_id: str) -> str:
    """
    Create long-lived refresh token.

    Refresh tokens should:
    - Have longer expiration (days/weeks)
    - Be stored in database for revocation
    - Only be used to generate new access tokens
    """
    to_encode = {
        "sub": user_id,
        "exp": datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS),
        "iat": datetime.utcnow(),
        "token_type": "refresh"
    }

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def create_token_pair(user_id: str, scopes: list[str]) -> Token:
    """
    Create access and refresh token pair.

    Usage:
        tokens = create_token_pair(user_id="user123", scopes=["read", "write"])
    """
    access_token = create_access_token(
        data={"sub": user_id, "scopes": scopes}
    )
    refresh_token = create_refresh_token(user_id)

    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )
```

### JWT Token Validation

```python
from jose import JWTError, jwt, ExpiredSignatureError
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional

security = HTTPBearer()

async def decode_token(token: str) -> TokenPayload:
    """
    Decode and validate JWT token.

    Raises:
        HTTPException: If token invalid, expired, or malformed
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        token_payload = TokenPayload(**payload)

        # Validate token type
        if token_payload.token_type != "access":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type"
            )

        return token_payload

    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> TokenData:
    """
    FastAPI dependency to extract and validate current user from JWT.

    Usage:
        @app.get("/protected")
        async def protected_route(user: TokenData = Depends(get_current_user)):
            return {"user_id": user.user_id}
    """
    token = credentials.credentials
    payload = await decode_token(token)

    return TokenData(
        user_id=payload.sub,
        scopes=payload.scopes
    )

async def require_scopes(required_scopes: list[str]):
    """
    Dependency factory for scope-based authorization.

    Usage:
        @app.delete("/admin/users/{user_id}")
        async def delete_user(
            user_id: int,
            user: TokenData = Depends(require_scopes(["admin:write"]))
        ):
            # User must have "admin:write" scope
            pass
    """
    async def scope_checker(user: TokenData = Depends(get_current_user)) -> TokenData:
        for scope in required_scopes:
            if scope not in user.scopes:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Missing required scope: {scope}"
                )
        return user

    return scope_checker
```

### Token Refresh Flow

```python
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

class RefreshTokenRequest(BaseModel):
    """Request to refresh access token."""
    refresh_token: str

async def refresh_access_token(
    request: RefreshTokenRequest,
    session: AsyncSession
) -> Token:
    """
    Generate new access token from refresh token.

    Process:
    1. Validate refresh token format and expiration
    2. Check if token is blacklisted
    3. Verify user still exists and is active
    4. Generate new access token (optionally rotate refresh token)
    """
    try:
        # Decode refresh token
        payload = jwt.decode(
            request.refresh_token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        # Validate token type
        if payload.get("token_type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type"
            )

        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload"
            )

        # Check if refresh token is blacklisted
        is_blacklisted = await check_token_blacklist(session, request.refresh_token)
        if is_blacklisted:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has been revoked"
            )

        # Verify user exists and is active
        user = await get_user_by_id(session, user_id)
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive"
            )

        # Generate new access token
        access_token = create_access_token(
            data={"sub": user_id, "scopes": user.scopes}
        )

        # Optional: Rotate refresh token for added security
        new_refresh_token = create_refresh_token(user_id)

        # Blacklist old refresh token
        await blacklist_token(session, request.refresh_token)

        return Token(
            access_token=access_token,
            refresh_token=new_refresh_token,
            expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )

    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token has expired"
        )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
```

### Token Blacklist Strategy

```python
from sqlalchemy import Column, String, DateTime, Index
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timedelta

class TokenBlacklist(Base):
    """
    Store revoked tokens.

    Cleanup strategy:
    - Periodically delete expired entries
    - Consider Redis for better performance
    """
    __tablename__ = "token_blacklist"

    token = Column(String(500), primary_key=True)
    blacklisted_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    expires_at = Column(DateTime, nullable=False)

    # Index for efficient cleanup
    __table_args__ = (
        Index('idx_expires_at', 'expires_at'),
    )

async def blacklist_token(session: AsyncSession, token: str) -> None:
    """
    Add token to blacklist.

    Store token expiration to enable automatic cleanup.
    """
    try:
        # Decode to get expiration
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        exp_timestamp = payload.get("exp")
        expires_at = datetime.fromtimestamp(exp_timestamp)

        # Add to blacklist
        blacklisted = TokenBlacklist(
            token=token,
            expires_at=expires_at
        )
        session.add(blacklisted)
        await session.commit()

    except JWTError:
        # If token invalid, still blacklist it
        blacklisted = TokenBlacklist(
            token=token,
            expires_at=datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        )
        session.add(blacklisted)
        await session.commit()

async def check_token_blacklist(session: AsyncSession, token: str) -> bool:
    """Check if token is blacklisted."""
    stmt = select(TokenBlacklist).where(TokenBlacklist.token == token)
    result = await session.execute(stmt)
    return result.scalar_one_or_none() is not None

async def cleanup_expired_tokens(session: AsyncSession) -> int:
    """
    Remove expired tokens from blacklist.

    Run periodically (e.g., daily cron job):
        await cleanup_expired_tokens(session)

    Returns:
        Number of tokens removed
    """
    from sqlalchemy import delete

    stmt = delete(TokenBlacklist).where(
        TokenBlacklist.expires_at < datetime.utcnow()
    )
    result = await session.execute(stmt)
    await session.commit()
    return result.rowcount
```

### Redis-Based Token Blacklist (Alternative)

```python
import redis.asyncio as redis
from datetime import datetime

class RedisTokenBlacklist:
    """
    Redis-based token blacklist for better performance.

    Advantages:
    - Faster lookups than database
    - Automatic expiration with TTL
    - No manual cleanup needed
    """

    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
        self.prefix = "blacklist:"

    async def blacklist_token(self, token: str) -> None:
        """Add token to Redis blacklist with automatic expiration."""
        try:
            # Decode to get expiration
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            exp_timestamp = payload.get("exp")

            # Calculate TTL (time until token expires)
            ttl = exp_timestamp - datetime.utcnow().timestamp()

            if ttl > 0:
                # Store token with TTL
                key = f"{self.prefix}{token}"
                await self.redis.setex(key, int(ttl), "1")

        except JWTError:
            # If token invalid, store with default TTL
            key = f"{self.prefix}{token}"
            await self.redis.setex(
                key,
                REFRESH_TOKEN_EXPIRE_DAYS * 86400,
                "1"
            )

    async def is_blacklisted(self, token: str) -> bool:
        """Check if token is blacklisted."""
        key = f"{self.prefix}{token}"
        return await self.redis.exists(key) > 0
```

### Complete Authentication Example

```python
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from passlib.context import CryptContext

app = FastAPI()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class LoginRequest(BaseModel):
    """User login credentials."""
    email: str
    password: str

@app.post("/auth/login", response_model=Token)
async def login(
    credentials: LoginRequest,
    session: AsyncSession = Depends(get_session)
) -> Token:
    """
    Authenticate user and return token pair.

    Process:
    1. Validate credentials
    2. Generate access + refresh token
    3. Store refresh token in database (for revocation)
    4. Return token pair
    """
    # Verify credentials
    user = await authenticate_user(session, credentials.email, credentials.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Generate token pair
    tokens = create_token_pair(
        user_id=str(user.id),
        scopes=user.scopes
    )

    # Store refresh token for tracking (optional)
    await store_refresh_token(session, user.id, tokens.refresh_token)

    return tokens

@app.post("/auth/refresh", response_model=Token)
async def refresh(
    request: RefreshTokenRequest,
    session: AsyncSession = Depends(get_session)
) -> Token:
    """Refresh access token using refresh token."""
    return await refresh_access_token(request, session)

@app.post("/auth/logout")
async def logout(
    user: TokenData = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
) -> Dict[str, str]:
    """
    Logout user by blacklisting tokens.

    Client should:
    1. Call this endpoint
    2. Delete tokens from storage
    3. Redirect to login
    """
    # Blacklist current access token (if provided in header)
    # Note: Client should send refresh token to blacklist it
    return {"message": "Successfully logged out"}

@app.get("/protected")
async def protected_route(
    user: TokenData = Depends(get_current_user)
) -> Dict[str, str]:
    """Protected route requiring valid JWT."""
    return {"message": f"Hello user {user.user_id}"}

@app.get("/admin/users")
async def admin_route(
    user: TokenData = Depends(require_scopes(["admin:read"]))
) -> Dict[str, str]:
    """Protected route requiring specific scope."""
    return {"message": "Admin access granted"}
```

### Security Considerations

#### Token Expiration Strategy

```python
# ✅ DO: Short-lived access tokens
ACCESS_TOKEN_EXPIRE_MINUTES = 15  # 15 minutes

# ✅ DO: Longer-lived refresh tokens
REFRESH_TOKEN_EXPIRE_DAYS = 7  # 7 days

# ❌ DON'T: Long-lived access tokens (security risk)
ACCESS_TOKEN_EXPIRE_MINUTES = 10080  # 1 week - TOO LONG
```

#### Secure Token Storage (Client Side)

```markdown
✅ Recommended Storage:
- **Access Token**: Memory only (JavaScript variable)
  - Never localStorage (XSS risk)
  - httpOnly cookie acceptable for same-domain

- **Refresh Token**: httpOnly, Secure, SameSite cookie
  - httpOnly: Prevents JavaScript access
  - Secure: HTTPS only
  - SameSite: CSRF protection

❌ Avoid:
- localStorage (vulnerable to XSS)
- sessionStorage (vulnerable to XSS)
- Regular cookies without httpOnly flag
```

#### Token Rotation

```python
# ✅ DO: Rotate refresh tokens on use
@app.post("/auth/refresh")
async def refresh_token(request: RefreshTokenRequest):
    # 1. Validate old refresh token
    # 2. Blacklist old refresh token
    # 3. Generate new access + refresh token pair
    # 4. Return new tokens
    pass

# Why? Limits damage if refresh token is compromised
```

#### CSRF Protection with JWT

```python
from fastapi import Cookie, HTTPException

# ✅ DO: Use double-submit cookie pattern for CSRF protection
@app.post("/api/action")
async def protected_action(
    csrf_token: str = Cookie(...),
    x_csrf_token: str = Header(...),
    user: TokenData = Depends(get_current_user)
):
    """
    Verify CSRF token matches cookie.

    Client must:
    1. Read CSRF token from cookie
    2. Send in X-CSRF-Token header
    """
    if csrf_token != x_csrf_token:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="CSRF token mismatch"
        )

    # Process action
    return {"status": "success"}
```

#### Token Claims Validation

```python
from typing import List

def validate_token_claims(payload: dict, expected_audience: str) -> None:
    """
    Validate JWT claims for security.

    Standard claims:
    - iss (Issuer): Who issued the token
    - aud (Audience): Who the token is for
    - sub (Subject): User ID
    - exp (Expiration): When token expires
    - iat (Issued At): When token was created
    - nbf (Not Before): Token not valid before this time
    """
    # Validate audience
    aud = payload.get("aud")
    if aud and aud != expected_audience:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token audience"
        )

    # Validate issuer
    iss = payload.get("iss")
    expected_issuer = "https://your-api.com"
    if iss and iss != expected_issuer:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token issuer"
        )

    # Check not-before claim
    nbf = payload.get("nbf")
    if nbf and datetime.fromtimestamp(nbf) > datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token not yet valid"
        )

# Usage in token creation
def create_secure_token(user_id: str) -> str:
    """Create token with all security claims."""
    to_encode = {
        "sub": user_id,
        "iss": "https://your-api.com",
        "aud": "https://your-api.com",
        "iat": datetime.utcnow(),
        "exp": datetime.utcnow() + timedelta(minutes=15),
        "nbf": datetime.utcnow(),
    }
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
```

---
