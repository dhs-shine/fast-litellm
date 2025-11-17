# Testing Guide

Fast LiteLLM has a comprehensive testing strategy to ensure it accelerates LiteLLM without breaking functionality.

## Testing Strategy

### 1. Unit Tests
Test individual Fast LiteLLM components in isolation.

```bash
# Run all unit tests
pytest tests/

# Run specific test file
pytest tests/test_accelerator.py

# Run with coverage
pytest tests/ --cov=fast_litellm --cov-report=html
```

### 2. Integration Tests
Test Fast LiteLLM with the actual LiteLLM library to ensure compatibility.

## Integration Testing with LiteLLM

Fast LiteLLM includes scripts to automatically test against LiteLLM's test suite. This ensures that the acceleration layer doesn't break any LiteLLM functionality.

### Quick Start

```bash
# 1. Setup LiteLLM for testing
./scripts/setup_litellm.sh

# 2. Run LiteLLM tests with acceleration
./scripts/run_litellm_tests.sh

# 3. Compare performance (with vs without acceleration)
./scripts/compare_performance.py
```

### Detailed Setup

#### Step 1: Setup LiteLLM

The setup script clones LiteLLM and installs its dependencies:

```bash
./scripts/setup_litellm.sh
```

This will:
- Clone LiteLLM to `.litellm/` directory
- Install LiteLLM and its dependencies
- Set up the test environment

You can specify a different branch:

```bash
LITELLM_BRANCH=development ./scripts/setup_litellm.sh
```

#### Step 2: Run Integration Tests

Run LiteLLM's tests with Fast LiteLLM acceleration enabled:

```bash
# Run all tests
./scripts/run_litellm_tests.sh

# Run specific test file
./scripts/run_litellm_tests.sh tests/test_completion.py

# Run specific test function
./scripts/run_litellm_tests.sh tests/test_completion.py::test_completion_openai

# Pass additional pytest arguments
./scripts/run_litellm_tests.sh tests/ -v --tb=long
```

#### Step 3: Performance Comparison

Compare test execution with and without acceleration:

```bash
# Full comparison (runs tests twice)
./scripts/compare_performance.py tests/test_completion.py

# Skip baseline (faster, only tests with acceleration)
./scripts/compare_performance.py tests/test_completion.py --skip-baseline
```

Example output:

```
======================================================================
                       PERFORMANCE COMPARISON
======================================================================

Metric                         Baseline        Accelerated     Improvement
------------------------------ --------------- --------------- ---------------
Execution Time                       45.23s          12.34s        3.67x faster
Tests Passed                            42              42       ✓ Same
Exit Code                                0               0       ✓ Both passed

Summary
-------
✅ Fast LiteLLM provides 3.67x speedup without breaking tests!
```

## Test Organization

```
tests/
├── test_basic.py                 # Basic import and setup tests
├── test_accelerator.py           # Core acceleration tests
├── test_monkeypatching.py        # Monkeypatch functionality tests
├── test_feature_flags.py         # Feature flag system tests
├── test_performance_benefits.py  # Performance benchmarks
├── test_api_compatibility.py     # API compatibility tests
├── test_connection_pooling.py    # Connection pool tests
├── test_advanced_router.py       # Router tests
└── benchmark_*.py                # Performance benchmarks
```

## Writing Tests

### Testing with Acceleration Enabled

```python
import fast_litellm
import litellm

def test_with_acceleration():
    """Test that acceleration is working"""
    assert fast_litellm.RUST_ACCELERATION_AVAILABLE

    # Your test code here
    response = litellm.completion(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": "test"}]
    )

    # Check performance stats
    stats = fast_litellm.get_performance_stats()
    assert len(stats) > 0
```

### Testing Fallback Behavior

```python
def test_fallback_on_error():
    """Test that fallback works when acceleration fails"""
    import fast_litellm

    # Simulate error condition
    # Should fallback to Python implementation
    # ...
```

### Performance Testing

```python
import time
import fast_litellm
import litellm

def test_performance_improvement():
    """Verify that acceleration provides speedup"""

    # Measure baseline (disable acceleration for this function)
    start = time.time()
    # ... operation ...
    baseline_time = time.time() - start

    # Measure with acceleration
    start = time.time()
    # ... same operation ...
    accel_time = time.time() - start

    speedup = baseline_time / accel_time
    assert speedup > 1.5, f"Expected >1.5x speedup, got {speedup:.2f}x"
```

## Continuous Integration

Fast LiteLLM uses GitHub Actions for automated testing:

### On Pull Request
- Run unit tests
- Run integration tests with LiteLLM
- Check code quality (formatting, linting, type checking)

### On Release
- Run full test suite
- Run performance benchmarks
- Compare with previous versions

## Test Markers

Use pytest markers to organize tests:

```bash
# Run only fast tests
pytest -m "not slow"

# Run only integration tests
pytest -m integration

# Run benchmarks
pytest -m benchmark
```

Available markers:
- `slow`: Long-running tests
- `integration`: Integration tests with LiteLLM
- `benchmark`: Performance benchmarks
- `unit`: Unit tests (default)

## Debugging Failed Tests

### 1. Check Acceleration Status

```python
import fast_litellm

# Check if Rust acceleration is available
print(f"Rust available: {fast_litellm.RUST_ACCELERATION_AVAILABLE}")

# Check patch status
status = fast_litellm.get_patch_status()
print(f"Patches applied: {status}")
```

### 2. Compare with Baseline

Run the same test without acceleration:

```bash
# Disable acceleration
export FAST_LITELLM_DISABLE=true

# Run test
pytest tests/test_failing.py
```

### 3. Check Performance Stats

```python
import fast_litellm

# Get performance data
stats = fast_litellm.get_performance_stats()
print(stats)

# Get recommendations
recommendations = fast_litellm.get_recommendations()
for rec in recommendations:
    print(rec)
```

### 4. Enable Verbose Logging

```python
import logging

logging.basicConfig(level=logging.DEBUG)
```

## Test Coverage

Maintain high test coverage:

```bash
# Generate coverage report
pytest tests/ --cov=fast_litellm --cov-report=html

# View report
open htmlcov/index.html
```

Target coverage: >80% for all components

## Performance Baselines

Track performance over time:

```bash
# Run benchmarks and save results
pytest tests/benchmark_*.py --benchmark-save=baseline

# Compare with baseline
pytest tests/benchmark_*.py --benchmark-compare=baseline
```

## Known Test Limitations

1. **API Keys Required**: Some LiteLLM tests require API keys (OpenAI, Anthropic, etc.)
2. **Network Dependent**: Integration tests require internet connection
3. **Rate Limits**: May hit rate limits with some providers
4. **Platform Specific**: Some tests may behave differently on different platforms

## Contributing Tests

When contributing:

1. Add tests for new features
2. Ensure existing tests pass
3. Add integration tests for LiteLLM compatibility
4. Update this documentation

## Resources

- [LiteLLM Testing Docs](https://github.com/BerriAI/litellm#testing)
- [pytest Documentation](https://docs.pytest.org/)
- [GitHub Actions Workflows](../.github/workflows/)
