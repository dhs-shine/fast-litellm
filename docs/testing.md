# Testing Guide

Fast LiteLLM has a focused testing strategy to verify Rust acceleration works correctly with LiteLLM.

## Quick Start

```bash
# Run all Rust acceleration tests
./scripts/test_rust.sh

# With verbose output
./scripts/test_rust.sh -v

# With coverage report
./scripts/test_rust.sh --coverage
```

## Test Suites

### 1. Rust Acceleration Tests (Primary)

**22 tests** that verify Rust extensions work correctly.

**Location**: `tests/test_rust_*.py`

**Run**:
```bash
.venv/bin/pytest tests/test_rust_*.py -v
```

**What's Tested**:
- ✅ Rust module loads correctly
- ✅ Acceleration is applied to LiteLLM
- ✅ Rust code paths are executed
- ✅ Token counting uses Rust
- ✅ Feature flags control behavior
- ✅ LiteLLM compatibility maintained

**Example Output**:
```
test_rust_acceleration.py::test_rust_module_available PASSED
test_rust_acceleration.py::test_health_check PASSED
  Health check: {'status': 'ok', 'rust_available': True}
test_rust_code_paths.py::test_encode_tokens PASSED
  ✓ Encoded 9 tokens with Rust acceleration
test_rust_code_paths.py::test_token_counter_with_messages PASSED
  ✓ Counted 19 tokens in messages

22 passed in 4.30s
```

### 2. LiteLLM Integration Tests

Tests that Fast LiteLLM works with LiteLLM's own test suite.

**Self-Contained Tests** (123 tests, no API keys needed):
```bash
cd .litellm

# Core utility tests (108 tests)
poetry run pytest tests/test_litellm/test_utils.py -v

# Cost calculator tests (14 tests)
poetry run pytest tests/test_litellm/test_cost_calculator.py -v

# Parameter filtering (1 test)
poetry run pytest tests/test_litellm/test_filter_out_litellm_params.py -v
```

**Full Integration** (requires setup):
```bash
# Setup LiteLLM
./scripts/setup_litellm.sh

# Run LiteLLM tests with Fast LiteLLM acceleration
./scripts/run_litellm_tests.sh

# Run specific test file
./scripts/run_litellm_tests.sh tests/test_litellm/test_utils.py
```

## Test Organization

### Core Rust Tests

```
tests/
├── test_rust_acceleration.py    # Verify Rust loads and applies (9 tests)
└── test_rust_code_paths.py      # Verify Rust executes (13 tests)
```

#### `test_rust_acceleration.py`

**Purpose**: Verify Rust module and acceleration application

**Tests**:
- `test_rust_module_available` - Rust module loads
- `test_rust_functions_exported` - Functions are accessible
- `test_health_check` - Health endpoint works
- `test_acceleration_applied` - Monkeypatching successful
- `test_feature_flags_enabled` - Feature flags work
- `test_feature_status` - Status reporting works
- `test_performance_stats` - Metrics collection works
- `test_import_litellm_after_acceleration` - LiteLLM imports
- `test_litellm_model_info` - Model info still works

#### `test_rust_code_paths.py`

**Purpose**: Verify Rust code is actually executed

**Tests**:
- `test_token_counter_import` - Token counter accessible
- `test_encode_tokens` - Encoding uses Rust
- `test_token_counter_with_messages` - Message counting uses Rust
- `test_get_model_info` - Model lookups work
- `test_get_model_cost` - Cost calculations work
- `test_supports_function_calling` - Function calling checks work
- `test_performance_stats_updated` - Stats are collected
- `test_check_enabled_features` - Feature status checks work
- `test_feature_status_details` - Detailed status available
- `test_litellm_basic_imports` - Core functions importable
- `test_litellm_utils_work` - Utility functions work
- `test_model_list_functions` - Model lists accessible

## Writing Tests

### Test Template

```python
"""Test Rust acceleration for <component>"""
import pytest
import fast_litellm  # IMPORTANT: Import first!
import litellm

def test_component_uses_rust():
    """Verify <component> uses Rust acceleration"""
    # Check feature is enabled
    assert fast_litellm.is_enabled('rust_<component>')

    # Perform operation that should use Rust
    result = litellm.some_operation(...)

    # Verify result is correct
    assert result is not None

    # Check performance was tracked
    stats = fast_litellm.get_performance_stats()
    assert '<component>' in stats
```

### Testing Best Practices

1. **Always import fast_litellm first**:
   ```python
   import fast_litellm  # Enable acceleration
   import litellm       # Now accelerated
   ```

2. **Check feature status**:
   ```python
   if not fast_litellm.is_enabled('rust_feature'):
       pytest.skip("Feature not enabled")
   ```

3. **Verify Rust is called**:
   ```python
   # Get initial stats
   initial = fast_litellm.get_performance_stats()

   # Perform operation
   result = litellm.encode(...)

   # Verify stats updated (indicates Rust was called)
   updated = fast_litellm.get_performance_stats()
   ```

4. **Test both success and fallback**:
   ```python
   # Test normal operation
   result = litellm.encode(model="gpt-3.5-turbo", text="test")
   assert result is not None

   # Test fallback with invalid input
   result = litellm.encode(model="invalid-model", text="test")
   # Should still work via Python fallback
   ```

## Continuous Integration

### GitHub Actions Workflow

```yaml
name: Test Rust Acceleration

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.12'

      - name: Set up Rust
        uses: actions-rs/toolchain@v1
        with:
          toolchain: stable

      - name: Install dependencies
        run: |
          python -m venv .venv
          .venv/bin/pip install maturin

      - name: Build Rust extensions
        run: .venv/bin/maturin develop --release

      - name: Run Rust tests
        run: ./scripts/test_rust.sh

      - name: Run LiteLLM integration tests
        run: |
          cd .litellm
          poetry run pytest tests/test_litellm/test_utils.py -v
```

## Debugging Test Failures

### Check Rust Build

```bash
# Verify Rust is built
.venv/bin/python -c "
import fast_litellm
print('Rust available:', fast_litellm.RUST_ACCELERATION_AVAILABLE)
"

# Rebuild if needed
.venv/bin/maturin develop --release
```

### Check Feature Status

```python
import fast_litellm

# Get health status
print(fast_litellm.health_check())

# Check specific feature
status = fast_litellm.get_feature_status()
print(status['rust_token_counting'])
```

### Enable Debug Logging

```python
import logging
logging.basicConfig(level=logging.DEBUG)

import fast_litellm
import litellm

# Operations will now log details
result = litellm.encode(model="gpt-3.5-turbo", text="test")
```

### Common Issues

**Issue**: `Rust available: False`
```bash
# Solution: Build Rust extensions
.venv/bin/maturin develop --release
```

**Issue**: Tests fail with import errors
```bash
# Solution: Install test dependencies
.venv/bin/pip install pytest pytest-cov pytest-asyncio
```

**Issue**: Feature shows as disabled
```bash
# Solution: Check feature flags configuration
cat fast_litellm/feature_flags.json

# Or enable via environment
export FAST_LITELLM_RUST_TOKEN_COUNTING=true
```

**Issue**: Performance stats are empty
```bash
# This is normal - stats are only collected when operations run
# Run some operations first, then check stats
```

## Performance Testing

### Benchmark Template

```python
import pytest
import time
import fast_litellm
import litellm

def test_token_counting_performance():
    """Verify Rust is faster than Python"""
    text = "Hello world " * 100

    # Warmup
    for _ in range(10):
        litellm.encode(model="gpt-3.5-turbo", text=text)

    # Measure Rust (with acceleration)
    start = time.perf_counter()
    for _ in range(100):
        litellm.encode(model="gpt-3.5-turbo", text=text)
    rust_time = time.perf_counter() - start

    # Disable acceleration
    fast_litellm.remove_acceleration()

    # Measure Python
    start = time.perf_counter()
    for _ in range(100):
        litellm.encode(model="gpt-3.5-turbo", text=text)
    python_time = time.perf_counter() - start

    # Re-enable for other tests
    fast_litellm.apply_acceleration()

    speedup = python_time / rust_time
    print(f"Speedup: {speedup:.2f}x")
    assert speedup > 2.0, f"Expected >2x speedup, got {speedup:.2f}x"
```

### Run Benchmarks

```bash
# Run with pytest-benchmark
.venv/bin/pip install pytest-benchmark
.venv/bin/pytest tests/benchmark_*.py --benchmark-only

# Run custom performance tests
.venv/bin/pytest tests/test_performance_*.py -v -s
```

## Test Coverage

### Generate Coverage Report

```bash
# HTML report
./scripts/test_rust.sh --coverage
open htmlcov/index.html

# Terminal report
.venv/bin/pytest tests/test_rust_*.py --cov=fast_litellm --cov-report=term

# XML report (for CI)
.venv/bin/pytest tests/test_rust_*.py --cov=fast_litellm --cov-report=xml
```

### Current Coverage

**Rust Tests**: 22 tests covering:
- ✅ Module loading (100%)
- ✅ Function exports (100%)
- ✅ Feature flags (100%)
- ✅ Token counting (100%)
- ✅ LiteLLM compatibility (100%)

**Python Layer**: ~1% (mostly covered by functional tests, not line coverage)

## See Also

- [Acceleration Components](acceleration.md) - What's accelerated
- [Architecture](architecture.md) - System design
- [Contributing](contributing.md) - Development guidelines
- [Configuration](configuration.md) - Feature flags and settings
