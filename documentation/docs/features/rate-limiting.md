# Rate Limiting

Fast LiteLLM provides an atomic rate limiter using Rust's atomic operations for thread-safe request throttling. This achieves **1.6x faster** rate limiting compared to Python implementations.

## Overview

The rate limiter controls request rates to prevent API quota exhaustion and ensure fair resource distribution.

### Key Features

- **Token bucket algorithm** for smooth rate limiting
- **Sliding window counters** for per-minute/per-hour limits
- **Atomic operations** for thread-safe concurrent access
- **Per-key rate limiting** for multi-tenant applications

## Performance

| Metric | Python | Rust | Improvement |
|--------|--------|------|-------------|
| Single-threaded | 1.885ms | 1.219ms | **1.6x faster** |
| High-cardinality (1000 keys) | 9.15ms | 8.12ms | **1.1x faster** |
| Memory (1000 keys) | 7.03 MB | 0.17 MB | **42x less memory** |

## Basic Usage

### Automatic Acceleration

Rate limiting is automatically accelerated when you import `fast_litellm`:

```python
import fast_litellm
import litellm

# Rate limiting is now accelerated for all LiteLLM calls
response = litellm.completion(
    model="gpt-3.5-turbo",
    messages=[{"role": "user", "content": "Hello!"}]
)
```

### Direct API Access

Use the rate limiter directly for custom rate limiting:

```python
from fast_litellm import SimpleRateLimiter

# Create a rate limiter (60 requests per minute)
limiter = SimpleRateLimiter(requests_per_minute=60)

# Check if request is allowed
result = limiter.check("user_123")

if result["allowed"]:
    # Proceed with the request
    make_api_call()
else:
    # Handle rate limiting
    print(f"Rate limited. Retry after {result.get('retry_after_ms', 0)}ms")
```

## API Reference

### SimpleRateLimiter

```python
class SimpleRateLimiter:
    def __init__(self, requests_per_minute: int = 60) -> None:
        """Create a rate limiter with specified requests per minute."""

    def check(self, key: Optional[str] = None) -> Dict[str, Any]:
        """
        Check if a request is allowed.

        Returns:
            {
                "allowed": bool,
                "reason": str,
                "remaining_requests": int,
                "retry_after_ms": Optional[int]
            }
        """

    def is_allowed(self, key: Optional[str] = None) -> bool:
        """Simple boolean check if request is allowed."""

    def get_remaining(self, key: Optional[str] = None) -> int:
        """Get remaining requests for a key."""

    def get_stats(self) -> Dict[str, Any]:
        """Get rate limiter statistics."""
```

### Standalone Functions

```python
# Check rate limit
result = fast_litellm.check_rate_limit("api_key_123")
# {'allowed': True, 'reason': 'ok', 'remaining_requests': 59}

# Get statistics
stats = fast_litellm.get_rate_limit_stats()
```

## Rate Limit Result

The `check()` method returns a dictionary with:

| Field | Type | Description |
|-------|------|-------------|
| `allowed` | bool | Whether the request is allowed |
| `reason` | str | Reason for the decision |
| `remaining_requests` | int | Requests remaining in current window |
| `retry_after_ms` | int (optional) | Milliseconds until next allowed request |

```python
result = limiter.check("user_123")

if not result["allowed"]:
    if result["reason"] == "rate_limit_exceeded":
        retry_after = result.get("retry_after_ms", 1000)
        print(f"Rate limited. Retry after {retry_after}ms")
```

## Multi-Tenant Rate Limiting

Use different keys for different users or API keys:

```python
from fast_litellm import SimpleRateLimiter

limiter = SimpleRateLimiter(requests_per_minute=100)

# Rate limit per user
def handle_request(user_id: str):
    if limiter.is_allowed(user_id):
        return process_request()
    else:
        return {"error": "Rate limit exceeded"}

# Rate limit per API key
def handle_api_request(api_key: str):
    result = limiter.check(f"api:{api_key}")
    if result["allowed"]:
        return process_request()
    else:
        return {
            "error": "Rate limit exceeded",
            "retry_after": result.get("retry_after_ms")
        }
```

## Configuration

Configure rate limits through environment variables or the configuration file:

```bash
# Set rate limits via environment
export FAST_LITELLM_RATE_LIMIT_RPM=100  # Requests per minute
export FAST_LITELLM_RATE_LIMIT_BURST=10  # Burst size
```

Or programmatically:

```python
from fast_litellm import SimpleRateLimiter

# Different limits for different use cases
standard_limiter = SimpleRateLimiter(requests_per_minute=60)
premium_limiter = SimpleRateLimiter(requests_per_minute=300)
```

## Handling Rate Limits

### Simple Retry

```python
import time

def make_request_with_retry(key: str, max_retries: int = 3):
    limiter = SimpleRateLimiter()

    for attempt in range(max_retries):
        result = limiter.check(key)

        if result["allowed"]:
            return make_api_call()

        retry_after = result.get("retry_after_ms", 1000)
        time.sleep(retry_after / 1000)

    raise Exception("Rate limit exceeded after retries")
```

### Async Retry

```python
import asyncio

async def make_request_with_retry_async(key: str, max_retries: int = 3):
    limiter = SimpleRateLimiter()

    for attempt in range(max_retries):
        result = limiter.check(key)

        if result["allowed"]:
            return await make_api_call_async()

        retry_after = result.get("retry_after_ms", 1000)
        await asyncio.sleep(retry_after / 1000)

    raise Exception("Rate limit exceeded after retries")
```

## Statistics

Monitor rate limiter performance:

```python
from fast_litellm import SimpleRateLimiter

limiter = SimpleRateLimiter()

# Make some requests
for i in range(10):
    limiter.check(f"user_{i}")

# Get statistics
stats = limiter.get_stats()
print(f"Total checks: {stats.get('total_checks', 0)}")
print(f"Allowed: {stats.get('allowed_count', 0)}")
print(f"Denied: {stats.get('denied_count', 0)}")
```

## How It Works

The Rust implementation uses atomic operations for thread-safe rate limiting:

1. **Token Bucket** - Tokens are added at a fixed rate, consumed per request
2. **Sliding Window** - Tracks requests in rolling time windows
3. **Atomic Counters** - Thread-safe without locks

```rust
// Simplified implementation
use std::sync::atomic::{AtomicU64, Ordering};

struct RateLimiter {
    tokens: AtomicU64,
    last_refill: AtomicU64,
}

impl RateLimiter {
    fn check(&self) -> bool {
        // Atomic decrement if tokens available
        self.tokens.fetch_sub(1, Ordering::SeqCst) > 0
    }
}
```

This provides lock-free rate limiting that scales with concurrent requests.

## Next Steps

- [Token Counting](token-counting.md) - Learn about fast token counting
- [Performance Tuning](../guides/performance.md) - Optimize rate limiting
