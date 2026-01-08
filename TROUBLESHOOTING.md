# Troubleshooting Guide

This guide covers common issues when using Fast LiteLLM.

## Installation Issues

### "Module not found: fast_litellm._rust"

**Cause**: The Rust extension was not compiled or installed correctly.

**Solutions**:

1. Ensure Rust toolchain is installed:
   ```bash
   curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
   ```

2. Rebuild with maturin:
   ```bash
   uv run maturin develop
   ```

3. Verify installation:
   ```bash
   uv run python -c "import fast_litellm._rust; print('OK')"
   ```

### "maturin develop fails with compilation errors"

**Solutions**:

1. Update Rust toolchain:
   ```bash
   rustup update stable
   ```

2. Clear build cache and rebuild:
   ```bash
   cargo clean
   uv run maturin develop
   ```

3. Check Python version - requires Python 3.9+:
   ```bash
   python --version
   ```

### "ImportError: cannot import name X from fast_litellm"

**Cause**: Version mismatch or partial installation.

**Solution**: Reinstall the package:
```bash
uv run maturin develop --release
```

## Runtime Issues

### Rust acceleration not being applied

**Symptoms**: Performance is similar to vanilla LiteLLM.

**Diagnosis**:
```python
import fast_litellm
print(fast_litellm.health_check())  # Should show rust_available: true
```

**Solutions**:

1. Ensure `fast_litellm` is imported BEFORE `litellm`:
   ```python
   import fast_litellm  # Must be first
   import litellm
   ```

2. Check feature flags:
   ```python
   from fast_litellm import get_feature_status
   print(get_feature_status())
   ```

3. Verify patch status:
   ```python
   from fast_litellm import get_patch_status
   print(get_patch_status())
   ```

### Feature auto-disabled due to errors

**Symptoms**: Log shows "Feature disabled due to errors" or performance reverts to Python.

**Cause**: After 10 errors (default threshold), features auto-disable as a circuit breaker.

**Solution**: Reset error counts:
```python
from fast_litellm import reset_errors
reset_errors()  # Reset all features
reset_errors("rust_routing")  # Reset specific feature
```

### Performance degradation with small inputs

**Symptoms**: Rust implementation slower than Python for small text.

**Cause**: FFI (Foreign Function Interface) overhead dominates for small operations.

**Expected behavior**: This is normal. Rust acceleration provides benefits for:
- Large text tokenization (1000+ tokens)
- High-concurrency scenarios
- Connection pooling with many endpoints
- Rate limiting with high cardinality

**Diagnosis**:
```python
from fast_litellm import get_performance_stats
stats = get_performance_stats()
print(stats)
```

### LiteLLM import fails on Python 3.9

**Symptoms**: `TypeError` when importing LiteLLM on Python 3.9.

**Cause**: Some LiteLLM versions use Python 3.10+ syntax (`str | List[str]`).

**Solutions**:

1. Upgrade to Python 3.10+
2. Use an older LiteLLM version compatible with Python 3.9
3. Fast LiteLLM gracefully handles this - core features work without LiteLLM

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `LITELLM_RUST_DISABLE_ALL` | Disable all Rust acceleration | `false` |
| `LITELLM_RUST_ROUTING` | Control routing feature | `enabled` |
| `LITELLM_RUST_TOKEN_COUNTING` | Control token counting | `enabled` |
| `LITELLM_RUST_RATE_LIMITING` | Control rate limiting | `enabled` |
| `LITELLM_RUST_CONNECTION_POOLING` | Control connection pooling | `enabled` |
| `LITELLM_ROLLOUT_SECRET` | Secret for consistent rollout hashing | None |

### Feature Flag Syntax

```bash
# Enable/disable
export LITELLM_RUST_ROUTING=enabled
export LITELLM_RUST_ROUTING=disabled

# Canary deployment (5% of requests)
export LITELLM_RUST_ROUTING=canary:5

# Gradual rollout (50% of requests)
export LITELLM_RUST_ROUTING=rollout:50
```

## Diagnostics

### Full Health Check

```python
import fast_litellm

# Basic health
print(fast_litellm.health_check())

# Patch status
print(fast_litellm.get_patch_status())

# Feature status
print(fast_litellm.get_feature_status())

# Performance stats
print(fast_litellm.get_performance_stats())
```

### Version Information

```python
import fast_litellm
print(f"Fast LiteLLM version: {fast_litellm.__version__}")
```

## Getting Help

1. Check [GitHub Issues](https://github.com/neul-labs/fast-litellm/issues)
2. Include in bug reports:
   - Python version (`python --version`)
   - Platform (`uname -a` or Windows version)
   - Fast LiteLLM version
   - Output of `fast_litellm.health_check()`
   - Minimal reproduction steps
