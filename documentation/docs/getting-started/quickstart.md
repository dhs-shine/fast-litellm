# Quick Start

This guide will help you get started with Fast LiteLLM in just a few minutes.

## Basic Usage

The simplest way to use Fast LiteLLM is to import it before importing LiteLLM:

```python
import fast_litellm  # Must be imported first!
import litellm

# Now all LiteLLM operations use Rust acceleration
response = litellm.completion(
    model="gpt-3.5-turbo",
    messages=[{"role": "user", "content": "Hello!"}]
)
```

!!! important
    Always import `fast_litellm` **before** `litellm`. This allows Fast LiteLLM to apply its acceleration patches.

## Check Acceleration Status

Verify that Rust acceleration is active:

```python
import fast_litellm

# Check if Rust acceleration is available
print(f"Rust acceleration: {fast_litellm.RUST_ACCELERATION_AVAILABLE}")

# Get health status
health = fast_litellm.health_check()
print(f"Status: {health['status']}")
print(f"Components: {', '.join(health['components'])}")
```

## Feature Status

Check which features are enabled:

```python
import fast_litellm

features = fast_litellm.get_feature_status()
for name, status in features.items():
    enabled = "enabled" if status.get("enabled") else "disabled"
    print(f"  {name}: {enabled}")
```

## Token Counting

Fast LiteLLM accelerates token counting operations:

```python
import fast_litellm
import litellm

# Encode text to tokens
text = "Hello, world! This is a test of Fast LiteLLM."
tokens = litellm.encode(model="gpt-3.5-turbo", text=text)
print(f"Token count: {len(tokens)}")

# Count tokens in messages
messages = [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "What is 2+2?"},
]
count = litellm.token_counter(model="gpt-3.5-turbo", messages=messages)
print(f"Message tokens: {count}")
```

## Using the Connection Pool

Access the accelerated connection pool directly:

```python
from fast_litellm import SimpleConnectionPool

pool = SimpleConnectionPool()

# Get a connection
conn_id = pool.get_connection("https://api.openai.com")
if conn_id:
    print(f"Got connection: {conn_id}")

    # Use the connection...

    # Return it to the pool
    pool.return_connection(conn_id)

# Get pool statistics
stats = pool.get_stats()
print(f"Pool stats: {stats}")
```

## Using the Rate Limiter

Control request rates with the accelerated rate limiter:

```python
from fast_litellm import SimpleRateLimiter

# Create a rate limiter (60 requests per minute)
limiter = SimpleRateLimiter(requests_per_minute=60)

# Check if request is allowed
result = limiter.check("api_key_123")
if result["allowed"]:
    # Proceed with the request
    print("Request allowed!")
else:
    print(f"Rate limited. Retry after {result.get('retry_after_ms', 0)}ms")

# Simple boolean check
if limiter.is_allowed("api_key_123"):
    # Make request
    pass
```

## Performance Monitoring

Monitor the performance of accelerated operations:

```python
import fast_litellm

# Get performance statistics
stats = fast_litellm.get_performance_stats()
for key, value in stats.items():
    print(f"{key}: {value}")

# Get optimization recommendations
recommendations = fast_litellm.get_recommendations()
for rec in recommendations:
    print(f"Recommendation: {rec}")
```

## Complete Example

Here's a complete example showing all the features together:

```python
#!/usr/bin/env python3
"""Complete Fast LiteLLM example."""

import fast_litellm
import litellm

def main():
    # 1. Check acceleration status
    print("=== Acceleration Status ===")
    print(f"Rust available: {fast_litellm.RUST_ACCELERATION_AVAILABLE}")

    health = fast_litellm.health_check()
    print(f"Status: {health['status']}")
    print(f"Components: {', '.join(health['components'])}")
    print()

    # 2. Feature status
    print("=== Feature Status ===")
    features = fast_litellm.get_feature_status()
    for name, status in features.items():
        enabled = "ON" if status.get("enabled") else "OFF"
        print(f"  [{enabled}] {name}")
    print()

    # 3. Token counting
    print("=== Token Counting ===")
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Explain quantum computing in simple terms."},
    ]
    token_count = litellm.token_counter(model="gpt-3.5-turbo", messages=messages)
    print(f"Message token count: {token_count}")
    print()

    # 4. Performance stats
    print("=== Performance Stats ===")
    stats = fast_litellm.get_performance_stats()
    if stats:
        for key, value in list(stats.items())[:5]:
            print(f"  {key}: {value}")
    else:
        print("  No stats collected yet")
    print()

    print("Done!")

if __name__ == "__main__":
    main()
```

## Next Steps

- [Features Overview](../features/overview.md) - Learn about all accelerated components
- [Configuration Guide](../guides/configuration.md) - Configure Fast LiteLLM behavior
- [Performance Tuning](../guides/performance.md) - Optimize for your use case
