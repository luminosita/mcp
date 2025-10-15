# Extension Guide: Adding External Service Integration

**Last Updated**: 2025-10-15
**Version**: 1.0
**Status**: Active

## Purpose

This guide provides patterns for integrating external services (REST APIs, gRPC, etc.) into MCP tools with proper error handling, retry logic, timeouts, and circuit breakers.

**After following this guide, you will understand**:
- How to access shared HTTP client via dependency injection
- Error handling patterns for external API calls
- Retry strategies and timeout configuration
- Circuit breaker pattern for service degradation
- Authentication patterns (API keys, OAuth, JWT)
- Testing with mocked external services

**Prerequisites**:
- Understanding of HTTP/REST APIs
- Familiarity with async/await patterns
- Basic knowledge of httpx library

---

## HTTP Client Architecture Overview

**Technology**: httpx (async HTTP client)

**Key Features**:
- **Connection Pooling**: Reuses connections (reduces handshake overhead)
- **Async/Await**: Non-blocking HTTP requests
- **Timeout Configuration**: Per-request and global timeouts
- **Retry Logic**: Automatic retries with exponential backoff
- **HTTP/2 Support**: Modern protocol support

**Shared Client**: Single httpx.AsyncClient instance shared across all tools (initialized at app startup, closed at shutdown).

---

## Step 1: Access Shared HTTP Client

Use dependency injection to access shared HTTP client.

```python
import httpx
from mcp_server.core.dependencies import get_http_client


# Business logic function (testable)
async def fetch_external_data(
    resource_id: str,
    client: httpx.AsyncClient,  # Injected dependency
    logger: logging.Logger,
) -> dict:
    """
    Fetch data from external API.

    Args:
        resource_id: Resource identifier
        client: HTTP client (injected)
        logger: Logger instance (injected)

    Returns:
        dict: API response data

    Raises:
        BusinessLogicError: If API call fails
    """
    logger.info(f"Fetching external data for resource: {resource_id}")

    try:
        # Make HTTP request
        response = await client.get(
            f"https://api.example.com/resources/{resource_id}",
            timeout=10.0,  # 10 second timeout
        )

        # Raise exception for 4xx/5xx status codes
        response.raise_for_status()

        # Parse JSON response
        data = response.json()

        logger.info(f"External data fetched successfully: {resource_id}")
        return data

    except httpx.TimeoutException:
        logger.error(f"External API timeout: {resource_id}")
        raise BusinessLogicError(
            "External API request timed out",
            details={"resource_id": resource_id, "timeout_seconds": "10"},
        )

    except httpx.HTTPStatusError as e:
        logger.error(f"External API error: {e.response.status_code}")
        raise BusinessLogicError(
            f"External API returned error: {e.response.status_code}",
            details={
                "resource_id": resource_id,
                "status_code": str(e.response.status_code),
                "response": e.response.text,
            },
        )

    except Exception as e:
        logger.exception(f"Unexpected error calling external API: {e}")
        raise BusinessLogicError(
            "Failed to call external API",
            details={"resource_id": resource_id, "error": str(e)},
        )


# MCP tool wrapper (accesses dependencies directly)
@mcp.tool(name="external.fetch_data")
async def fetch_data_tool(params: FetchDataInput) -> FetchDataOutput:
    """MCP tool wrapper for fetching external data."""
    from mcp_server.core.dependencies import get_http_client, get_logger

    client = get_http_client()
    logger = get_logger("mcp_server.tools.external")

    data = await fetch_external_data(params.resource_id, client, logger)

    return FetchDataOutput(
        resource_id=params.resource_id,
        data=data,
    )
```

---

## Step 2: HTTP Request Patterns

### Pattern 1: GET Request

```python
async def get_resource(
    resource_id: str,
    client: httpx.AsyncClient,
) -> dict:
    """Fetch resource by ID."""
    response = await client.get(
        f"https://api.example.com/resources/{resource_id}",
        headers={"Accept": "application/json"},
        timeout=10.0,
    )
    response.raise_for_status()
    return response.json()
```

### Pattern 2: POST Request with JSON Body

```python
async def create_resource(
    name: str,
    description: str,
    client: httpx.AsyncClient,
) -> dict:
    """Create new resource."""
    response = await client.post(
        "https://api.example.com/resources",
        json={
            "name": name,
            "description": description,
        },
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
        timeout=10.0,
    )
    response.raise_for_status()
    return response.json()
```

### Pattern 3: PUT Request (Update)

```python
async def update_resource(
    resource_id: str,
    status: str,
    client: httpx.AsyncClient,
) -> dict:
    """Update resource status."""
    response = await client.put(
        f"https://api.example.com/resources/{resource_id}",
        json={"status": status},
        timeout=10.0,
    )
    response.raise_for_status()
    return response.json()
```

### Pattern 4: DELETE Request

```python
async def delete_resource(
    resource_id: str,
    client: httpx.AsyncClient,
) -> bool:
    """Delete resource."""
    response = await client.delete(
        f"https://api.example.com/resources/{resource_id}",
        timeout=10.0,
    )
    response.raise_for_status()
    return response.status_code == 204
```

### Pattern 5: Request with Query Parameters

```python
async def search_resources(
    query: str,
    limit: int,
    client: httpx.AsyncClient,
) -> list[dict]:
    """Search resources with query parameters."""
    response = await client.get(
        "https://api.example.com/resources/search",
        params={
            "q": query,
            "limit": limit,
            "sort": "created_at",
        },
        timeout=10.0,
    )
    response.raise_for_status()
    return response.json()["results"]
```

---

## Step 3: Authentication Patterns

### Pattern 1: API Key Authentication (Header)

```python
async def call_api_with_key(
    resource_id: str,
    api_key: str,
    client: httpx.AsyncClient,
) -> dict:
    """Call API with API key in header."""
    response = await client.get(
        f"https://api.example.com/resources/{resource_id}",
        headers={
            "X-API-Key": api_key,  # API key in custom header
            "Accept": "application/json",
        },
        timeout=10.0,
    )
    response.raise_for_status()
    return response.json()
```

### Pattern 2: Bearer Token Authentication (JWT)

```python
async def call_api_with_token(
    resource_id: str,
    access_token: str,
    client: httpx.AsyncClient,
) -> dict:
    """Call API with Bearer token."""
    response = await client.get(
        f"https://api.example.com/resources/{resource_id}",
        headers={
            "Authorization": f"Bearer {access_token}",  # JWT token
            "Accept": "application/json",
        },
        timeout=10.0,
    )
    response.raise_for_status()
    return response.json()
```

### Pattern 3: Basic Authentication

```python
async def call_api_with_basic_auth(
    resource_id: str,
    username: str,
    password: str,
    client: httpx.AsyncClient,
) -> dict:
    """Call API with Basic authentication."""
    response = await client.get(
        f"https://api.example.com/resources/{resource_id}",
        auth=(username, password),  # httpx handles Basic auth encoding
        timeout=10.0,
    )
    response.raise_for_status()
    return response.json()
```

### Pattern 4: OAuth 2.0 with Token Refresh

```python
class OAuthClient:
    """OAuth 2.0 client with automatic token refresh."""

    def __init__(
        self,
        client_id: str,
        client_secret: str,
        token_url: str,
        http_client: httpx.AsyncClient,
    ):
        self.client_id = client_id
        self.client_secret = client_secret
        self.token_url = token_url
        self.http_client = http_client
        self.access_token: str | None = None
        self.token_expires_at: float = 0

    async def get_access_token(self) -> str:
        """Get valid access token (refresh if expired)."""
        import time

        if self.access_token and time.time() < self.token_expires_at:
            return self.access_token

        # Request new token
        response = await self.http_client.post(
            self.token_url,
            data={
                "grant_type": "client_credentials",
                "client_id": self.client_id,
                "client_secret": self.client_secret,
            },
            timeout=10.0,
        )
        response.raise_for_status()

        token_data = response.json()
        self.access_token = token_data["access_token"]
        self.token_expires_at = time.time() + token_data["expires_in"] - 60  # Refresh 60s early

        return self.access_token

    async def call_api(self, url: str) -> dict:
        """Call API with automatic token refresh."""
        token = await self.get_access_token()

        response = await self.http_client.get(
            url,
            headers={"Authorization": f"Bearer {token}"},
            timeout=10.0,
        )
        response.raise_for_status()
        return response.json()
```

---

## Step 4: Error Handling Patterns

### Comprehensive Error Handling

```python
async def call_external_api_with_error_handling(
    resource_id: str,
    client: httpx.AsyncClient,
    logger: logging.Logger,
) -> dict:
    """Call external API with comprehensive error handling."""
    try:
        response = await client.get(
            f"https://api.example.com/resources/{resource_id}",
            timeout=10.0,
        )
        response.raise_for_status()
        return response.json()

    except httpx.TimeoutException as e:
        # Request timeout (network slow or server unresponsive)
        logger.error(f"API timeout: {resource_id}")
        raise BusinessLogicError(
            "External API request timed out after 10 seconds",
            details={"resource_id": resource_id},
        )

    except httpx.ConnectError as e:
        # Connection failed (DNS lookup failed, connection refused)
        logger.error(f"API connection error: {e}")
        raise BusinessLogicError(
            "Failed to connect to external API",
            details={"resource_id": resource_id, "error": str(e)},
        )

    except httpx.HTTPStatusError as e:
        # HTTP error status (4xx or 5xx)
        status_code = e.response.status_code

        if status_code == 404:
            # Resource not found
            logger.warning(f"Resource not found: {resource_id}")
            raise BusinessLogicError(
                f"Resource {resource_id} not found in external system",
                details={"resource_id": resource_id, "status_code": "404"},
            )

        elif status_code == 401:
            # Unauthorized (authentication failed)
            logger.error("API authentication failed")
            raise BusinessLogicError(
                "External API authentication failed",
                details={"status_code": "401"},
            )

        elif status_code == 429:
            # Rate limit exceeded
            logger.error("API rate limit exceeded")
            raise BusinessLogicError(
                "External API rate limit exceeded",
                details={"status_code": "429", "retry_after": e.response.headers.get("Retry-After")},
            )

        elif 500 <= status_code < 600:
            # Server error (5xx)
            logger.error(f"API server error: {status_code}")
            raise BusinessLogicError(
                f"External API server error: {status_code}",
                details={"status_code": str(status_code), "response": e.response.text},
            )

        else:
            # Other HTTP error
            logger.error(f"API error: {status_code}")
            raise BusinessLogicError(
                f"External API error: {status_code}",
                details={"status_code": str(status_code), "response": e.response.text},
            )

    except httpx.RequestError as e:
        # Generic request error (catch-all for httpx errors)
        logger.exception(f"API request error: {e}")
        raise BusinessLogicError(
            "Failed to communicate with external API",
            details={"error": str(e)},
        )

    except Exception as e:
        # Unexpected error
        logger.exception(f"Unexpected error: {e}")
        raise BusinessLogicError(
            "Unexpected error calling external API",
            details={"error": str(e)},
        )
```

---

## Step 5: Retry Logic with Backoff

Use `tenacity` library for automatic retries with exponential backoff.

```python
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
)


@retry(
    stop=stop_after_attempt(3),  # Retry up to 3 times
    wait=wait_exponential(multiplier=1, min=1, max=10),  # Exponential backoff: 1s, 2s, 4s
    retry=retry_if_exception_type(httpx.TimeoutException),  # Only retry on timeout
)
async def call_api_with_retry(
    resource_id: str,
    client: httpx.AsyncClient,
    logger: logging.Logger,
) -> dict:
    """Call API with automatic retry on timeout."""
    logger.info(f"Calling API for resource: {resource_id}")

    response = await client.get(
        f"https://api.example.com/resources/{resource_id}",
        timeout=10.0,
    )
    response.raise_for_status()

    return response.json()
```

**Retry Strategy**:
- **Idempotent requests** (GET, PUT, DELETE): Safe to retry
- **Non-idempotent requests** (POST): Avoid retries (may create duplicates)
- **Transient errors**: Retry (timeout, 503 Service Unavailable)
- **Permanent errors**: Don't retry (404 Not Found, 401 Unauthorized)

---

## Step 6: Circuit Breaker Pattern

Implement circuit breaker to prevent cascading failures.

```python
class CircuitBreaker:
    """
    Circuit breaker for external service calls.

    States:
    - CLOSED: Normal operation (calls pass through)
    - OPEN: Failure threshold exceeded (calls fail immediately)
    - HALF_OPEN: Testing if service recovered (limited calls pass through)
    """

    def __init__(self, failure_threshold: int = 5, timeout: float = 60.0):
        self.failure_threshold = failure_threshold
        self.timeout = timeout  # Time to wait before trying again
        self.failure_count = 0
        self.last_failure_time: float = 0
        self.state = "CLOSED"

    async def call(self, func, *args, **kwargs):
        """Execute function with circuit breaker protection."""
        import time

        # Check if circuit is OPEN
        if self.state == "OPEN":
            if time.time() - self.last_failure_time > self.timeout:
                # Transition to HALF_OPEN (try again)
                self.state = "HALF_OPEN"
            else:
                # Circuit still OPEN, fail immediately
                raise BusinessLogicError(
                    "Circuit breaker OPEN - external service unavailable",
                    details={"state": self.state, "failure_count": str(self.failure_count)},
                )

        try:
            # Execute function
            result = await func(*args, **kwargs)

            # Success - reset circuit breaker
            if self.state == "HALF_OPEN":
                self.state = "CLOSED"
            self.failure_count = 0

            return result

        except Exception as e:
            # Failure - increment counter
            self.failure_count += 1
            self.last_failure_time = time.time()

            # Check if threshold exceeded
            if self.failure_count >= self.failure_threshold:
                self.state = "OPEN"

            raise


# Usage
circuit_breaker = CircuitBreaker(failure_threshold=5, timeout=60.0)


async def call_api_with_circuit_breaker(
    resource_id: str,
    client: httpx.AsyncClient,
) -> dict:
    """Call API with circuit breaker protection."""
    return await circuit_breaker.call(
        call_external_api,
        resource_id,
        client,
    )
```

---

## Step 7: Testing with Mocked External Services

### Pattern 1: Mock httpx.AsyncClient

```python
import pytest
from unittest.mock import AsyncMock

@pytest.fixture
def mock_http_client():
    """Mock HTTP client for testing."""
    mock_client = AsyncMock(spec=httpx.AsyncClient)

    # Mock successful response
    mock_response = AsyncMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "id": "res-123",
        "name": "Test Resource",
        "status": "active",
    }

    mock_client.get.return_value = mock_response

    return mock_client


@pytest.mark.asyncio
async def test_fetch_external_data(mock_http_client, mock_logger):
    """Test fetching data with mocked HTTP client."""
    # Act
    result = await fetch_external_data("res-123", mock_http_client, mock_logger)

    # Assert
    assert result["id"] == "res-123"
    assert result["name"] == "Test Resource"

    # Verify HTTP call was made
    mock_http_client.get.assert_called_once_with(
        "https://api.example.com/resources/res-123",
        timeout=10.0,
    )
```

### Pattern 2: Mock HTTP Errors

```python
@pytest.mark.asyncio
async def test_fetch_external_data_timeout(mock_http_client, mock_logger):
    """Test timeout error handling."""
    # Arrange: Mock timeout
    mock_http_client.get.side_effect = httpx.TimeoutException("Request timeout")

    # Act & Assert
    with pytest.raises(BusinessLogicError) as exc_info:
        await fetch_external_data("res-123", mock_http_client, mock_logger)

    assert "timed out" in str(exc_info.value)


@pytest.mark.asyncio
async def test_fetch_external_data_404(mock_http_client, mock_logger):
    """Test 404 error handling."""
    # Arrange: Mock 404 response
    mock_response = AsyncMock()
    mock_response.status_code = 404
    mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
        "Not found",
        request=AsyncMock(),
        response=mock_response,
    )

    mock_http_client.get.return_value = mock_response

    # Act & Assert
    with pytest.raises(BusinessLogicError) as exc_info:
        await fetch_external_data("res-123", mock_http_client, mock_logger)

    assert "not found" in str(exc_info.value).lower()
```

### Pattern 3: Use httpx-mock for Real HTTP Mocking

```python
import pytest
from pytest_httpx import HTTPXMock


@pytest.mark.asyncio
async def test_fetch_external_data_with_httpx_mock(httpx_mock: HTTPXMock):
    """Test with httpx-mock library (real HTTP client, mocked responses)."""
    # Arrange: Mock HTTP response
    httpx_mock.add_response(
        url="https://api.example.com/resources/res-123",
        method="GET",
        json={"id": "res-123", "name": "Test Resource"},
        status_code=200,
    )

    # Act: Use real HTTP client (responses mocked)
    async with httpx.AsyncClient() as client:
        result = await fetch_external_data("res-123", client, mock_logger)

    # Assert
    assert result["id"] == "res-123"
```

---

## Best Practices

### 1. Use Timeouts Always

```python
# ❌ BAD: No timeout (can hang forever)
response = await client.get("https://api.example.com/resource")

# ✅ GOOD: Explicit timeout
response = await client.get("https://api.example.com/resource", timeout=10.0)
```

### 2. Validate Response Data

```python
from pydantic import BaseModel

class ExternalResourceResponse(BaseModel):
    """Validate external API response."""
    id: str
    name: str
    status: str

async def fetch_resource(resource_id: str, client: httpx.AsyncClient) -> ExternalResourceResponse:
    response = await client.get(f"https://api.example.com/resources/{resource_id}", timeout=10.0)
    response.raise_for_status()

    # Validate response with Pydantic
    return ExternalResourceResponse(**response.json())
```

### 3. Log External API Calls

```python
logger.info(
    "Calling external API",
    extra={
        "method": "GET",
        "url": url,
        "resource_id": resource_id,
        "timeout": timeout,
    },
)
```

### 4. Handle Rate Limits

```python
if response.status_code == 429:
    retry_after = int(response.headers.get("Retry-After", "60"))
    logger.warning(f"Rate limited, retry after {retry_after} seconds")
    await asyncio.sleep(retry_after)
    # Retry request
```

### 5. Use Connection Pooling

Shared HTTP client reuses connections automatically (configured at app startup):

```python
_http_client = httpx.AsyncClient(
    timeout=30.0,
    limits=httpx.Limits(
        max_keepalive_connections=10,  # Keepalive connections
        max_connections=20,             # Total connections
    ),
)
```

---

## Troubleshooting

### Error: "Connection pool exhausted"

**Cause**: Too many concurrent requests.

**Solution**: Increase `max_connections` limit or reduce concurrency.

### Error: "Timeout after 10 seconds"

**Cause**: External API slow or unresponsive.

**Solution**:
- Increase timeout for slow APIs
- Implement retry logic with exponential backoff
- Add circuit breaker to prevent cascading failures

### Error: "SSL certificate verification failed"

**Cause**: Invalid or self-signed SSL certificate.

**Solution** (development only):
```python
# ⚠️ DEVELOPMENT ONLY - DO NOT USE IN PRODUCTION
client = httpx.AsyncClient(verify=False)
```

---

## Related Documentation

- **Dependency Injection**: [../dependency-injection.md](../dependency-injection.md) - DI patterns
- **Extension Guide**: [add-new-tool.md](add-new-tool.md) - Tool implementation patterns
- **httpx Docs**: https://www.python-httpx.org/

### CLAUDE.md Standards

- **CLAUDE-testing.md**: Testing patterns, mocking
- **CLAUDE-validation.md**: Input/output validation

---

## Changelog

- **2025-10-15** (v1.0): Initial external service integration guide (US-013)
