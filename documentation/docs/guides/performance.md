# Performance Tuning

Optimize Fast LiteLLM for your specific workload and requirements.

## Understanding Performance Characteristics

### When Rust Excels

| Scenario | Speedup | Reason |
|----------|---------|--------|
| Connection pooling | 3.2x | Lock-free DashMap |
| Rate limiting | 1.6x | Atomic operations |
| Large text tokenization | 1.7x | Optimized tiktoken-rs |
| High-cardinality rate limiting | 42x memory savings | Efficient data structures |

### When Python May Be Better

| Scenario | Overhead | Reason |
|----------|----------|--------|
| Small text tokenization | ~0.5x | FFI overhead dominates |
| Simple routing | ~0.4x | Python dict access is fast |
| Single-threaded workloads | Variable | FFI overhead |

## Optimization Strategies

### 1. Profile Your Workload

Start by understanding where time is spent:

```python
import fast_litellm
import time

# Enable performance tracking
start = time.perf_counter()

# Your workload here
for i in range(1000):
    fast_litellm.check_rate_limit(f"user_{i}")

elapsed = time.perf_counter() - start
print(f"1000 rate limit checks: {elapsed:.3f}s")

# Get detailed stats
stats = fast_litellm.get_performance_stats()
for key, value in stats.items():
    print(f"  {key}: {value}")
```

### 2. Batch Operations

For token counting, batch operations are more efficient:

```python
from fast_litellm import SimpleTokenCounter

counter = SimpleTokenCounter()

# Less efficient: individual calls
texts = ["text1", "text2", "text3", ...]
counts = [counter.count_tokens(t) for t in texts]

# More efficient: batch call
counts = counter.count_tokens_batch(texts)
```

### 3. Connection Pool Sizing

Optimize connection pool for your traffic:

```python
# For high-throughput APIs
# Configure via environment or config file
# Default is usually sufficient for most use cases

import fast_litellm

# Monitor pool usage
stats = fast_litellm.get_connection_pool_stats()
active = stats.get('active_connections', 0)
idle = stats.get('idle_connections', 0)

print(f"Active: {active}, Idle: {idle}")
```

### 4. Rate Limiter Tuning

Choose appropriate rate limits:

```python
from fast_litellm import SimpleRateLimiter

# For burst traffic (allows temporary spikes)
limiter = SimpleRateLimiter(requests_per_minute=100)

# The internal token bucket allows some burst capacity
# Burst size is automatically calculated as rpm/10
```

### 5. Feature Selection

Disable features that don't benefit your workload:

```bash
# If routing overhead outweighs benefits
export FAST_LITELLM_RUST_ROUTING=false

# If only processing small texts
export FAST_LITELLM_RUST_TOKEN_COUNTING=false
```

## Benchmarking Your Setup

### Built-in Benchmarks

Run the built-in benchmark suite:

```bash
python scripts/run_benchmarks.py --iterations 200
```

### Custom Benchmarks

Create benchmarks for your specific use case:

```python
import time
import statistics
import fast_litellm
from fast_litellm import SimpleRateLimiter

def benchmark_rate_limiter(iterations=1000):
    limiter = SimpleRateLimiter()
    times = []

    for i in range(iterations):
        start = time.perf_counter()
        limiter.check(f"key_{i % 100}")
        elapsed = time.perf_counter() - start
        times.append(elapsed * 1000)  # Convert to ms

    return {
        "mean_ms": statistics.mean(times),
        "median_ms": statistics.median(times),
        "stdev_ms": statistics.stdev(times),
        "min_ms": min(times),
        "max_ms": max(times),
        "throughput_ops": iterations / sum(times) * 1000,
    }

results = benchmark_rate_limiter()
print(f"Mean: {results['mean_ms']:.3f}ms")
print(f"Throughput: {results['throughput_ops']:.0f} ops/s")
```

## Memory Optimization

### High-Cardinality Workloads

For applications with many unique keys:

```python
# Rust is 42x more memory efficient for 1000+ unique keys
from fast_litellm import SimpleRateLimiter

limiter = SimpleRateLimiter()

# Handle many unique users efficiently
for user_id in unique_user_ids:  # Could be millions
    result = limiter.check(user_id)
```

### Monitor Memory Usage

```python
import psutil
import os

def get_memory_mb():
    process = psutil.Process(os.getpid())
    return process.memory_info().rss / 1024 / 1024

print(f"Memory: {get_memory_mb():.1f} MB")
```

## Concurrency Optimization

### Thread Pool Sizing

Fast LiteLLM's Rust components are thread-safe. Optimize thread count:

```python
import concurrent.futures
from fast_litellm import SimpleRateLimiter

limiter = SimpleRateLimiter()

def check_rate(user_id):
    return limiter.check(user_id)

# Optimal thread count depends on your workload
# Start with CPU count, adjust based on benchmarks
with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
    results = list(executor.map(check_rate, user_ids))
```

### Async Integration

For async applications:

```python
import asyncio
from fast_litellm import SimpleRateLimiter

limiter = SimpleRateLimiter()

async def check_rate_async(user_id):
    # Run in thread pool for blocking Rust calls
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, limiter.check, user_id)

async def main():
    tasks = [check_rate_async(f"user_{i}") for i in range(100)]
    results = await asyncio.gather(*tasks)
```

## Production Checklist

### Before Deployment

- [ ] Run benchmarks with production-like data
- [ ] Configure feature flags appropriately
- [ ] Set up monitoring and alerting
- [ ] Test fallback behavior
- [ ] Configure connection pool cleanup

### Monitoring in Production

```python
import fast_litellm

# Periodic health check
health = fast_litellm.health_check()
assert health['status'] == 'ok'

# Monitor performance
stats = fast_litellm.get_performance_stats()

# Check for recommendations
recommendations = fast_litellm.get_recommendations()
for rec in recommendations:
    print(f"Recommendation: {rec}")
```

### Gradual Rollout

1. Start at 5% traffic
2. Monitor error rates and latency
3. Increase to 25%, 50%, 100%
4. Roll back if issues detected

## Troubleshooting Performance Issues

### Symptom: Rust Slower Than Expected

1. Check FFI overhead vs operation size
2. Verify Rust extensions are loaded
3. Profile with `get_performance_stats()`

### Symptom: High Memory Usage

1. Check for connection leaks
2. Run `cleanup_expired_connections()`
3. Monitor with `get_connection_pool_stats()`

### Symptom: Rate Limit Errors

1. Verify rate limit configuration
2. Check for clock skew in distributed systems
3. Reset errors with `reset_errors()`

## Next Steps

- [Monitoring](monitoring.md) - Set up comprehensive monitoring
- [Configuration](configuration.md) - Fine-tune settings
