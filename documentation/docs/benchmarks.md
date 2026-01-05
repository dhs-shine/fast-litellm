# Benchmarks

Comprehensive performance benchmarks comparing Fast LiteLLM's Rust implementation with Python baselines.

## Summary

| Component | Speedup | Memory | Best For |
|-----------|---------|--------|----------|
| **Connection Pool** | **3.2x faster** | Same | HTTP connection management |
| **Rate Limiting** | **1.6x faster** | Same | Request throttling |
| **Large Text Tokenization** | **1.7x faster** | Same | Long documents |
| **High-Cardinality Rate Limits** | **1.2x faster** | **42x less** | Many unique keys |

## Detailed Results

### Connection Pool

The connection pool uses DashMap for lock-free concurrent access.

| Benchmark | Python | Rust | Speedup |
|-----------|--------|------|---------|
| Single-threaded | 0.136ms | 0.042ms | **3.2x** |
| 8 threads concurrent | 0.016ms | 0.013ms | **1.2x** |

**Why Rust is faster:** DashMap provides lock-free reads and fine-grained write locking, eliminating contention in concurrent scenarios.

### Rate Limiting

The rate limiter uses atomic operations for thread-safe request throttling.

| Benchmark | Python | Rust | Speedup |
|-----------|--------|------|---------|
| Single-threaded | 1.885ms | 1.219ms | **1.55x** |
| High-cardinality (1000 keys) | 9.15ms | 8.12ms | **1.13x** |

**Memory Usage (1000 unique keys):**

| Implementation | Peak Memory |
|----------------|-------------|
| Python | 7.03 MB |
| Rust | 0.17 MB |

**Why Rust is faster:** Atomic operations avoid lock overhead. Memory efficiency comes from Rust's compact data structures.

### Token Counting

Token counting performance depends on text size due to FFI overhead.

| Text Size | Python | Rust | Speedup |
|-----------|--------|------|---------|
| Small (< 100 tokens) | 1.6ms | 3.1ms | 0.5x (Python faster) |
| Large (1000+ chars) | 23.4ms | 13.9ms | **1.68x** |

**Why results vary:** For small texts, Python's tiktoken has lower overhead since there's no FFI boundary. For large texts, Rust's optimized implementation outweighs FFI costs.

### Routing

Routing performance depends on model list complexity.

| Benchmark | Python | Rust | Speedup |
|-----------|--------|------|---------|
| Simple routing | 0.756ms | 1.732ms | 0.44x (Python faster) |
| 8 threads concurrent | 0.016ms | 0.027ms | 0.57x (Python faster) |

**Why Python is sometimes faster:** For simple routing with Python objects, FFI conversion overhead dominates. Rust routing shines in complex scenarios with many deployments.

## Running Benchmarks

### Quick Benchmark

```bash
python scripts/run_benchmarks.py
```

### Detailed Benchmark

```bash
python scripts/run_benchmarks.py --iterations 200 --workload medium
```

### Custom Benchmark

```python
import time
import statistics
from fast_litellm import SimpleRateLimiter

def benchmark_rate_limiter(iterations=1000):
    limiter = SimpleRateLimiter()
    times = []

    for i in range(iterations):
        start = time.perf_counter()
        limiter.check(f"key_{i % 100}")
        elapsed = time.perf_counter() - start
        times.append(elapsed * 1000)

    return {
        "mean_ms": statistics.mean(times),
        "min_ms": min(times),
        "max_ms": max(times),
        "ops_per_sec": iterations / (sum(times) / 1000),
    }

print(benchmark_rate_limiter())
```

## When to Use Rust Acceleration

### Recommended

| Use Case | Reason |
|----------|--------|
| Connection pooling | 3x+ speedup with lock-free access |
| Rate limiting | 1.5x+ speedup, 42x memory savings |
| Large text tokenization | 1.5x+ speedup for long documents |
| High-cardinality workloads | Massive memory savings |
| Multi-threaded applications | Lock-free data structures |

### Consider Carefully

| Use Case | Reason |
|----------|--------|
| Small text tokenization | FFI overhead may exceed benefits |
| Simple routing | Python dict access is very fast |
| Single-threaded workloads | FFI overhead with no contention benefit |

## Benchmark Environment

Results were collected on:

| Property | Value |
|----------|-------|
| Platform | Linux x86_64 |
| Python | 3.12.3 |
| CPU | AMD Ryzen 9 (16 cores) |
| Memory | 64 GB |
| Fast LiteLLM | 0.1.0 |
| LiteLLM | 1.80.0 |

## Methodology

### Fair Comparison

Both implementations include equivalent features:

1. **Token Counting**: Both use tiktoken for accurate BPE tokenization
2. **Rate Limiting**: Both implement token bucket + sliding window
3. **Connection Pool**: Both provide thread-safe management
4. **Routing**: Both support multiple strategies

### Measurement

- **Warmup**: 3 iterations before timing
- **Iterations**: 200 per benchmark (configurable)
- **Timing**: `time.perf_counter()` for high precision
- **Memory**: `psutil` for process memory tracking

### Concurrency Testing

Concurrent benchmarks use Python's `ThreadPoolExecutor` with 8 workers to simulate real-world multi-threaded usage.

## Understanding FFI Overhead

Fast LiteLLM uses PyO3 for Python-Rust interop. Each call across the FFI boundary has overhead:

```
Python Call → PyO3 Conversion → Rust Execution → PyO3 Conversion → Python Return
              ~1-5μs overhead                     ~1-5μs overhead
```

For micro-operations (small texts, simple routing), this overhead can exceed the Rust speedup. For larger operations, Rust's performance advantage dominates.

## Optimizing for Your Workload

### Profile First

```python
import fast_litellm

# Collect metrics
stats = fast_litellm.get_performance_stats()

# Get recommendations
recommendations = fast_litellm.get_recommendations()
for rec in recommendations:
    print(rec)
```

### Selective Enablement

```bash
# Disable features where Python is faster
export FAST_LITELLM_RUST_ROUTING=false

# Keep features where Rust excels
export FAST_LITELLM_RUST_CONNECTION_POOL=true
export FAST_LITELLM_RUST_RATE_LIMITING=true
```

## Historical Benchmarks

Performance improvements across versions:

| Version | Connection Pool | Rate Limiting | Token Counting |
|---------|-----------------|---------------|----------------|
| 0.1.0 | 3.2x | 1.6x | 1.7x |

## Contributing Benchmarks

To contribute benchmark results:

1. Run benchmarks: `python scripts/run_benchmarks.py --full`
2. Include system info in your report
3. Submit via GitHub Issues

See [CONTRIBUTING.md](https://github.com/neul-labs/fast-litellm/blob/main/CONTRIBUTING.md) for details.
