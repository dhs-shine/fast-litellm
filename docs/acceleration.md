# Rust Acceleration Components

This document describes which LiteLLM components are accelerated by Fast LiteLLM's Rust layer.

## Overview

Fast LiteLLM uses PyO3 to create Rust implementations of performance-critical LiteLLM operations. The Rust layer is exposed as `fast_litellm._rust` and automatically applied when you import `fast_litellm`.

## Accelerated Components

### 1. Token Counting (`src/tokens.rs`)

**Status**: ✅ Enabled by default

**Performance**: ~0% improvement (LiteLLM already well-optimized)

**What's Accelerated**:
- `litellm.encode()` - Tokenize text to token IDs
- `litellm.decode()` - Convert token IDs back to text
- `litellm.token_counter()` - Count tokens in messages

**Implementation**:
- Uses `tiktoken-rs` for high-performance tokenization
- Batch processing for multiple texts
- Zero-copy operations where possible
- Cached encodings for repeated models

**Performance Reality**:
Our benchmarks revealed that LiteLLM's token counting is already well-optimized, so Rust acceleration provides minimal performance benefit for individual operations. However, the infrastructure remains in place for potential algorithmic improvements or when used in batch contexts.

**Example**:
```python
import fast_litellm  # Enable acceleration
import litellm

# Uses Rust tokenization (performance similar to Python)
tokens = litellm.encode(model="gpt-3.5-turbo", text="Hello, world!")
count = litellm.token_counter(model="gpt-3.5-turbo", messages=[...])
```

### 2. Advanced Routing (`src/core.rs`)

**Status**: ⏸️ Disabled (10% gradual rollout)

**Performance**: ~+0.7% improvement (marginal improvement over Python)

**What's Accelerated**:
- Model selection logic
- Load balancing across multiple deployments
- Retry logic and fallback routing
- Health-based routing decisions

**Implementation**:
- Lock-free routing with `DashMap`
- Atomic counters for tracking usage
- Zero-allocation path for hot routes
- Concurrent model health checks

**Performance Reality**:
Routing performance showed only marginal improvements over the existing Python implementation, indicating LiteLLM's routing logic is already quite efficient.

**Data Structures**:
```rust
pub struct Router {
    models: DashMap<String, ModelConfig>,
    deployments: DashMap<String, Vec<Deployment>>,
    health: DashMap<String, AtomicU64>,
}
```

### 3. Rate Limiting (`src/rate_limiter.rs`)

**Status**: ⏸️ Disabled (25% gradual rollout)

**Performance**: ~+46% improvement (significant gains in complex operations)

**What's Accelerated**:
- Token bucket rate limiting
- Sliding window rate limiting
- Per-model and per-deployment limits
- Concurrent rate limit checks

**Implementation**:
- Atomic operations for lock-free updates
- Async-ready design
- Memory-efficient sliding windows
- Automatic cleanup of expired entries

**Performance Reality**:
Rate limiting showed the most significant improvements (~46% gain) due to Rust's concurrent primitives and atomic operations, which provide advantages over Python's Global Interpreter Lock (GIL) for concurrent operations.

**Algorithms**:
- **Token Bucket**: Classic algorithm with atomic refill
- **Sliding Window**: Time-bucketed approach for precise limiting

### 4. Connection Pooling (`src/connection_pool.rs`)

**Status**: ⏸️ Disabled (canary deployment)

**Performance**: ~+39% improvement (meaningful gains in concurrent operations)

**What's Accelerated**:
- HTTP connection reuse
- Connection lifecycle management
- Pool size management
- Health checking of connections

**Implementation**:
- Lock-free connection pool with `DashMap`
- Atomic reference counting
- Automatic connection recycling
- Configurable pool sizes per provider

**Performance Reality**:
Connection pooling achieved ~39% improvement, particularly beneficial for high-concurrency scenarios where Rust's lock-free data structures outperform Python's GIL-bound operations.

### 5. Feature Flags (`src/feature_flags.rs`)

**Status**: ✅ Always active

**What It Does**:
- Controls which Rust components are enabled
- Gradual rollout percentages
- Canary deployment support
- Error tracking and circuit breaking

**Configuration** (`fast_litellm/feature_flags.json`):
```json
{
  "features": {
    "rust_token_counting": {
      "enabled": true
    },
    "rust_routing": {
      "enabled": false,
      "rollout_percentage": 10
    },
    "rust_rate_limiting": {
      "enabled": false,
      "rollout_percentage": 25
    },
    "rust_connection_pool": {
      "enabled": false,
      "deployment_type": "canary"
    }
  }
}
```

### 6. Performance Monitoring (`src/performance_monitor.rs`)

**Status**: ✅ Always active

**What It Does**:
- Tracks Rust vs Python performance
- Collects timing metrics
- Generates performance recommendations
- Circuit breaker for failing components

**Metrics Collected**:
- Execution time (Rust vs Python)
- Success/failure rates
- Error counts per component
- Throughput measurements

## Architecture

### Module Structure

```
fast_litellm/
├── _rust           # Compiled Rust extension (.so)
├── __init__.py     # Auto-applies acceleration
├── enhanced_monkeypatch.py  # Wraps LiteLLM functions
├── feature_flags.py         # Controls rollout
└── performance_monitor.py   # Tracks metrics

src/
├── lib.rs          # PyO3 module definition
├── core.rs         # Routing logic
├── tokens.rs       # Token counting
├── connection_pool.rs  # Connection management
├── rate_limiter.rs     # Rate limiting
├── feature_flags.rs    # Feature control
└── performance_monitor.rs  # Monitoring
```

### Call Flow

```
User Code
    ↓
import fast_litellm  (applies acceleration)
    ↓
import litellm
    ↓
litellm.encode()  →  Enhanced wrapper checks feature flag
    ↓                       ↓
    ↓                   Enabled? → Call Rust: fast_litellm._rust.encode()
    ↓                       ↓
    ↓                   Disabled? → Call Python: tiktoken.encode()
    ↓
Result (with performance tracking)
```

## Enabling/Disabling Components

### Check Status

```python
import fast_litellm

# Check overall health
status = fast_litellm.health_check()
print(status)
# {'status': 'ok', 'rust_available': True, 'components': [...]}

# Check specific features
features = fast_litellm.get_feature_status()
print(features['rust_token_counting'])
# {'enabled': True, 'error_count': 0, ...}
```

### Enable Components

Edit `fast_litellm/feature_flags.json`:

```json
{
  "features": {
    "rust_routing": {
      "enabled": true
    },
    "rust_rate_limiting": {
      "enabled": true
    }
  }
}
```

Or use environment variables:
```bash
export FAST_LITELLM_RUST_ROUTING=true
export FAST_LITELLM_RUST_RATE_LIMITING=true
```

### Gradual Rollout

Enable for a percentage of requests:

```json
{
  "features": {
    "rust_routing": {
      "enabled": false,
      "rollout_percentage": 25
    }
  }
}
```

This uses Rust for 25% of requests, Python for 75%.

## Performance Benefits

### Real-World Performance Results

Our comprehensive benchmarking revealed that LiteLLM is already well-optimized for many operations:

| Component | Baseline Time | Accelerated Time | Improvement | Status |
|-----------|---------------|------------------|-------------|--------|
| Token Counting | 0.000035s | 0.000036s | -0.6% | ⚠️ Baseline already optimized |
| Batch Token Counting | 0.000001s | 0.000001s | +9.1% | ✅ Small but consistent |
| Request Routing | 0.001309s | 0.001299s | +0.7% | ✅ Marginal improvement |
| Rate Limiting | 0.000000s | 0.000000s | +45.9% | ✅ Significant gains for complex ops |
| Connection Pooling | 0.000000s | 0.000000s | +38.7% | ✅ Meaningful for high-concurrency |

**Key Findings**:
- Core token counting operations show minimal improvement because LiteLLM is already well-optimized
- Complex operations (rate limiting, connection pooling) benefit significantly from Rust's concurrent primitives
- Performance gains are most meaningful in high-throughput scenarios
- The most significant improvements come from operations that benefit from Rust's lock-free data structures and atomic operations

### When Rust Acceleration Provides Value

1. **High-Concurrency Scenarios**: Rate limiting and connection pooling show significant gains under load
2. **Batch Operations**: Large-scale token counting operations can benefit from Rust's memory efficiency
3. **Complex Algorithms**: Operations involving multiple concurrent checks benefit from Rust's primitives
4. **Memory Efficiency**: Long-running processes benefit from Rust's memory management

## Fallback Behavior

If Rust acceleration fails:
1. Error is logged
2. Error counter incremented
3. Python implementation is used
4. After 10 errors, component auto-disables
5. Circuit breaker prevents cascade failures

**Example**:
```python
# Even if Rust fails, your code still works
import fast_litellm
import litellm

# Will use Python fallback if Rust fails
tokens = litellm.encode(model="gpt-3.5-turbo", text="Hello")
```

## Debugging

### Check What's Running

```python
import fast_litellm

# Is Rust available?
print(fast_litellm.RUST_ACCELERATION_AVAILABLE)

# What's enabled?
status = fast_litellm.get_patch_status()
print(status)
# {'applied': True, 'components': ['routing', 'token_counting', ...]}

# Get performance stats
stats = fast_litellm.get_performance_stats()
print(stats)
```

### Force Disable

```python
import fast_litellm

# Disable all Rust acceleration
fast_litellm.remove_acceleration()

# Re-enable
fast_litellm.apply_acceleration()
```

## Future Enhancements

### Planned Additions

1. **Caching** - Rust-based LRU cache for responses
2. **Streaming** - Zero-copy streaming responses
3. **Embeddings** - Batch embedding operations
4. **Retries** - Smart retry logic with exponential backoff

### Performance Targets

- Token counting: Optimization likely minimal (LiteLLM already well-optimized)
- Routing: Marginal improvements expected
- Rate limiting: Maintain ~46% improvement in high-concurrency scenarios
- Connection pooling: Maintain ~39% improvement under load
- Focus on algorithmic improvements rather than raw speedup targets

## See Also

- [Architecture](architecture.md) - Overall system design
- [Testing](testing.md) - How to test acceleration
- [API Reference](api.md) - Python API documentation
- [Configuration](configuration.md) - Configuration options
