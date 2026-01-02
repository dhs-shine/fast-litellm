# Features Overview

Fast LiteLLM provides Rust-accelerated implementations of core LiteLLM components. Each component is designed to be a drop-in replacement with significant performance improvements.

## Accelerated Components

| Component | Speedup | Description |
|-----------|---------|-------------|
| [Connection Pool](connection-pool.md) | 3.2x | Lock-free connection management using DashMap |
| [Rate Limiting](rate-limiting.md) | 1.6x | Atomic rate limiting with token bucket algorithm |
| [Token Counting](token-counting.md) | 1.5-1.7x | Fast token counting for large texts |
| [Routing](routing.md) | Variable | Advanced deployment routing strategies |

## How Acceleration Works

Fast LiteLLM uses a monkeypatching strategy to replace LiteLLM's Python implementations with Rust-accelerated versions:

```
                    ┌─────────────────────┐
  User Code ───────▶│ import fast_litellm │
                    └─────────────────────┘
                              │
                              ▼
                    ┌─────────────────────┐
                    │ Apply Monkeypatches │
                    └─────────────────────┘
                              │
                              ▼
                    ┌─────────────────────┐
  User Code ───────▶│   import litellm    │
                    └─────────────────────┘
                              │
                              ▼
                    ┌─────────────────────┐
                    │ Accelerated Calls   │
                    │ ┌─────────────────┐ │
                    │ │  Rust Backend   │ │
                    │ └─────────────────┘ │
                    └─────────────────────┘
```

## Safety Features

### Automatic Fallback

If the Rust implementation encounters an error, Fast LiteLLM automatically falls back to the Python implementation:

```python
import fast_litellm

# If Rust fails, Python implementation is used transparently
response = litellm.completion(...)
```

### Feature Flags

Each accelerated component can be individually enabled or disabled:

```python
import fast_litellm

# Check feature status
features = fast_litellm.get_feature_status()
print(features)
# {'rust_routing': {'enabled': True, ...},
#  'rust_token_counting': {'enabled': True, ...}, ...}
```

### Error Tracking

Fast LiteLLM tracks errors per feature and can automatically disable problematic features:

```python
import fast_litellm

# Reset error counts
fast_litellm.reset_errors()

# Or reset for a specific feature
fast_litellm.reset_errors("rust_routing")
```

## When to Use Rust Acceleration

### Best For

- **Connection pooling** - 3x+ speedup with lock-free DashMap
- **Rate limiting** - 1.5x+ speedup with atomic operations
- **Large text token counting** - 1.5x+ speedup for longer texts
- **High-cardinality workloads** - 40x+ lower memory for many unique keys
- **Production deployments** - Thread-safety guarantees

### Consider Carefully

- **Small text token counting** - Python tiktoken has lower FFI overhead
- **Routing with Python objects** - FFI conversion overhead may dominate
- **Simple single-threaded use cases** - FFI overhead may not be worth it

## Performance Monitoring

Monitor the performance of accelerated operations in real-time:

```python
import fast_litellm

# Get statistics
stats = fast_litellm.get_performance_stats()

# Compare implementations
comparison = fast_litellm.compare_implementations(
    "rust_rate_limiter",
    "python_rate_limiter"
)

# Get recommendations
recommendations = fast_litellm.get_recommendations()
```

## Next Steps

- [Connection Pool](connection-pool.md) - Learn about accelerated connection management
- [Rate Limiting](rate-limiting.md) - Explore atomic rate limiting
- [Token Counting](token-counting.md) - Fast token counting details
- [Routing](routing.md) - Advanced routing strategies
