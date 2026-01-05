# Connection Pooling

Fast LiteLLM provides a high-performance connection pool using Rust's DashMap for lock-free concurrent access. This achieves **3.2x faster** connection management compared to traditional Python implementations.

## Overview

The connection pool manages HTTP connections to API endpoints, reducing the overhead of establishing new connections for each request.

### Key Features

- **Lock-free concurrent access** using DashMap
- **Automatic health checking** for connections
- **Idle connection cleanup**
- **Per-endpoint connection limits**

## Performance

| Metric | Python | Rust | Improvement |
|--------|--------|------|-------------|
| Single-threaded | 0.136ms | 0.042ms | **3.2x faster** |
| Multi-threaded (8 threads) | 0.016ms | 0.013ms | **1.2x faster** |

## Basic Usage

### Automatic Acceleration

When you import `fast_litellm`, connection pooling is automatically accelerated:

```python
import fast_litellm
import litellm

# Connection pooling is now accelerated
response = litellm.completion(
    model="gpt-3.5-turbo",
    messages=[{"role": "user", "content": "Hello!"}]
)
```

### Direct API Access

You can also use the connection pool directly:

```python
from fast_litellm import SimpleConnectionPool

# Create a pool
pool = SimpleConnectionPool(pool_name="my_pool")

# Get a connection to an endpoint
conn_id = pool.get_connection("https://api.openai.com")

if conn_id:
    try:
        # Use the connection for your request...
        pass
    finally:
        # Return connection to pool when done
        pool.return_connection(conn_id)
```

## API Reference

### SimpleConnectionPool

```python
class SimpleConnectionPool:
    def __init__(self, pool_name: str = "default") -> None:
        """Create a new connection pool."""

    def get_connection(self, endpoint: str) -> Optional[str]:
        """Get a connection ID for the specified endpoint."""

    def return_connection(self, connection_id: str) -> None:
        """Return a connection to the pool."""

    def health_check(self, connection_id: str) -> bool:
        """Check if a connection is healthy."""

    def cleanup(self) -> None:
        """Clean up expired/idle connections."""

    def get_stats(self) -> Dict[str, Any]:
        """Get pool statistics."""
```

### Standalone Functions

```python
# Get a connection
conn_id = fast_litellm.get_connection("https://api.openai.com")

# Return a connection
fast_litellm.return_connection(conn_id)

# Remove a connection
fast_litellm.remove_connection(conn_id)

# Health check
is_healthy = fast_litellm.health_check_connection(conn_id)

# Cleanup expired connections
fast_litellm.cleanup_expired_connections()

# Get statistics
stats = fast_litellm.get_connection_pool_stats()
```

## Statistics

Monitor your connection pool:

```python
from fast_litellm import SimpleConnectionPool

pool = SimpleConnectionPool()
stats = pool.get_stats()

print(f"Total connections: {stats.get('total_connections', 0)}")
print(f"Active connections: {stats.get('active_connections', 0)}")
print(f"Idle connections: {stats.get('idle_connections', 0)}")
```

## Best Practices

### 1. Always Return Connections

Always return connections to the pool when done:

```python
conn_id = pool.get_connection(endpoint)
try:
    # Use connection
    pass
finally:
    pool.return_connection(conn_id)
```

### 2. Periodic Cleanup

For long-running applications, periodically clean up idle connections:

```python
import threading
import time

def cleanup_loop():
    while True:
        fast_litellm.cleanup_expired_connections()
        time.sleep(60)  # Clean up every minute

cleanup_thread = threading.Thread(target=cleanup_loop, daemon=True)
cleanup_thread.start()
```

### 3. Monitor Pool Health

Regularly check pool statistics to ensure optimal performance:

```python
stats = fast_litellm.get_connection_pool_stats()
if stats.get('active_connections', 0) > 100:
    print("Warning: High number of active connections")
```

## How It Works

The Rust implementation uses DashMap, a concurrent hash map that provides:

1. **Lock-free reads** - Multiple threads can read simultaneously
2. **Fine-grained locking** - Writes only lock specific buckets
3. **Atomic operations** - Thread-safe without global locks

```rust
// Simplified implementation
use dashmap::DashMap;

struct ConnectionPool {
    connections: DashMap<String, Connection>,
}

impl ConnectionPool {
    fn get_connection(&self, endpoint: &str) -> Option<String> {
        // Lock-free lookup
        self.connections.get(endpoint).map(|c| c.id.clone())
    }
}
```

This architecture provides significant performance improvements under concurrent workloads compared to Python's `threading.Lock`-based approach.

## Next Steps

- [Rate Limiting](rate-limiting.md) - Learn about atomic rate limiting
- [Performance Tuning](../guides/performance.md) - Optimize for your workload
