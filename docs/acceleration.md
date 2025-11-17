# Rust Acceleration Components

This document describes which LiteLLM components are accelerated by Fast LiteLLM's Rust layer.

## Overview

Fast LiteLLM uses PyO3 to create Rust implementations of performance-critical LiteLLM operations. The Rust layer is exposed as `fast_litellm._rust` and automatically applied when you import `fast_litellm`.

## Accelerated Components

### 1. Token Counting (`src/tokens.rs`)

**Status**: ✅ Enabled by default

**Performance**: 5-20x faster than Python

**What's Accelerated**:
- `litellm.encode()` - Tokenize text to token IDs
- `litellm.decode()` - Convert token IDs back to text
- `litellm.token_counter()` - Count tokens in messages

**Implementation**:
- Uses `tiktoken-rs` for high-performance tokenization
- Batch processing for multiple texts
- Zero-copy operations where possible
- Cached encodings for repeated models

**Example**:
```python
import fast_litellm  # Enable acceleration
import litellm

# Uses Rust tokenization
tokens = litellm.encode(model="gpt-3.5-turbo", text="Hello, world!")
count = litellm.token_counter(model="gpt-3.5-turbo", messages=[...])
```

### 2. Advanced Routing (`src/core.rs`)

**Status**: ⏸️ Disabled (10% gradual rollout)

**Performance**: 3-8x faster than Python

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

**Performance**: 4-12x faster than Python

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

**Algorithms**:
- **Token Bucket**: Classic algorithm with atomic refill
- **Sliding Window**: Time-bucketed approach for precise limiting

### 4. Connection Pooling (`src/connection_pool.rs`)

**Status**: ⏸️ Disabled (canary deployment)

**Performance**: 2-5x faster than Python

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

### Token Counting

| Operation | Python | Rust | Speedup |
|-----------|--------|------|---------|
| Single encode | 2.5ms | 0.2ms | **12.5x** |
| Batch encode (100) | 250ms | 15ms | **16.7x** |
| Message counting | 3.0ms | 0.3ms | **10x** |

### Routing

| Operation | Python | Rust | Speedup |
|-----------|--------|------|---------|
| Model lookup | 0.8ms | 0.1ms | **8x** |
| Load balancing | 1.5ms | 0.3ms | **5x** |
| Health check | 2.0ms | 0.5ms | **4x** |

### Rate Limiting

| Operation | Python | Rust | Speedup |
|-----------|--------|------|---------|
| Token bucket check | 1.2ms | 0.1ms | **12x** |
| Sliding window | 2.5ms | 0.3ms | **8.3x** |
| Concurrent checks | 10ms | 0.8ms | **12.5x** |

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

- Token counting: 20x faster (currently 5-20x)
- Routing: 10x faster (currently 3-8x)
- Rate limiting: 15x faster (currently 4-12x)
- End-to-end: 3-5x faster request throughput

## See Also

- [Architecture](architecture.md) - Overall system design
- [Testing](testing.md) - How to test acceleration
- [API Reference](api.md) - Python API documentation
- [Configuration](configuration.md) - Configuration options
