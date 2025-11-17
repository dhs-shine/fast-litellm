# Testing Fast LiteLLM with LiteLLM

## Summary of Test Results

### ✅ Success: Core Unit Tests Pass
```bash
poetry run pytest tests/test_litellm/test_utils.py -v
# Result: 108/108 tests PASSED
```

### ⚠️ Warning: Most Integration Tests Fail (Expected)
The majority of LiteLLM's 3000+ tests fail during **collection** (not execution) due to missing:
- **Python dependencies**: Provider SDKs (anthropic, vertexai, mistralai, etc.)
- **Test infrastructure**: Base test classes need PYTHONPATH configuration
- **Environment setup**: API keys, running proxy servers, databases, cloud credentials

**These failures are NOT Fast LiteLLM bugs** - they are test environment configuration issues.

## Recommended Testing Strategy

### Option 1: Run Self-Contained Unit Tests (Best for Quick Validation)

These tests don't require external services:

```bash
cd .litellm

# Core utility tests
poetry run pytest tests/test_litellm/test_utils.py -v

# Token counting tests (relevant for Fast LiteLLM)
poetry run pytest tests/test_litellm/test_token_counter.py -v

# Router tests (if they don't require mocks)
poetry run pytest tests/test_litellm/test_get_llm_provider.py -v

# Exception mapping tests
poetry run pytest tests/test_litellm/test_exception_mapping.py -v
```

### Option 2: Run Tests with Minimal API Key Setup

For basic integration testing with real API calls:

```bash
# Set minimal required API key
export OPENAI_API_KEY="your-key-here"

# Run basic completion tests
poetry run pytest tests/test_litellm/test_completion.py::test_basic_completion -v
```

### Option 3: Full Integration Testing (Advanced)

Requires extensive setup:

1. **Install all provider SDKs**:
   ```bash
   pip install anthropic google-generativeai vertexai mistralai cohere langchain_openai
   ```

2. **Set all API keys**:
   ```bash
   export OPENAI_API_KEY="..."
   export ANTHROPIC_API_KEY="..."
   export COHERE_API_KEY="..."
   # ... etc
   ```

3. **Configure PYTHONPATH for test modules**:
   ```bash
   export PYTHONPATH="${PYTHONPATH}:/path/to/.litellm/tests"
   ```

4. **Run specific provider tests**:
   ```bash
   poetry run pytest tests/llm_translation/test_openai.py -v
   ```

## Fast LiteLLM Specific Testing

To test that Fast LiteLLM doesn't break LiteLLM functionality:

### 1. Compare Behavior With/Without Acceleration

```bash
# Without Fast LiteLLM
cd .litellm
poetry run pytest tests/test_litellm/test_utils.py -v

# With Fast LiteLLM (in your project root)
cd ..
./scripts/run_litellm_tests.sh tests/test_litellm/test_utils.py
```

### 2. Focus on Accelerated Code Paths

Fast LiteLLM accelerates:
- **Routing logic** (`src/core.rs`)
- **Token counting** (`src/tokens.rs`)
- **Connection pooling** (`src/connection_pool.rs`)
- **Rate limiting** (`src/rate_limiter.rs`)

Relevant tests:
```bash
# Router tests
poetry run pytest tests/router_unit_tests/ -v -k "not requires_proxy"

# Token counting tests
poetry run pytest tests/test_litellm/test_token_counter.py -v

# Rate limiting tests (if they exist)
poetry run pytest tests/ -v -k "rate_limit"
```

### 3. Custom Fast LiteLLM Integration Test

Create a simple test in `tests/test_fast_litellm_integration.py`:

```python
import fast_litellm  # Import first to apply acceleration
import litellm

def test_fast_litellm_basic():
    """Test that Fast LiteLLM doesn't break basic functionality"""
    # This should use Rust acceleration if enabled
    result = litellm.completion(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": "Hi"}],
        api_key="sk-test"  # Will fail but tests the code path
    )
```

## Interpreting Test Failures

### Collection Errors (Most Common)
```
ERROR tests/foo.py - ModuleNotFoundError: No module named 'respx'
```
**Meaning**: Test file couldn't be loaded due to missing dependency.
**Solution**: Install the missing package or skip these tests.

### Import Errors
```
ERROR tests/foo.py - ModuleNotFoundError: No module named 'base_test_class'
```
**Meaning**: Test uses relative imports that need PYTHONPATH setup.
**Solution**: Add test directories to PYTHONPATH.

### Connection Errors
```
ERROR tests/foo.py - httpx.ConnectError: [Errno 111] Connection refused
```
**Meaning**: Test expects a proxy server running on localhost.
**Solution**: Start the proxy server or skip these tests.

### Authentication Errors
```
ERROR tests/foo.py - AuthenticationError: Missing API key
```
**Meaning**: Test requires actual API credentials.
**Solution**: Set environment variables or skip these tests.

## Baseline Comparison

To verify Fast LiteLLM doesn't break anything:

1. **Establish baseline** (without Fast LiteLLM):
   ```bash
   cd .litellm
   poetry run pytest tests/test_litellm/test_utils.py -v > /tmp/baseline.txt
   ```

2. **Test with Fast LiteLLM**:
   ```bash
   cd /home/dipankar/Code/fast-litellm
   # Import fast_litellm in test environment
   poetry run pytest .litellm/tests/test_litellm/test_utils.py -v > /tmp/with_acceleration.txt
   ```

3. **Compare results**:
   ```bash
   diff /tmp/baseline.txt /tmp/with_acceleration.txt
   ```

If both show "108 passed", Fast LiteLLM is working correctly!

## Summary

- ✅ **108 core unit tests pass** - LiteLLM test environment is functional
- ⚠️ **Most tests fail during collection** - Missing dependencies/setup (expected)
- 🎯 **Focus on self-contained tests** - Best ROI for validation
- 🔍 **Compare with/without Fast LiteLLM** - Detect regressions
- 📊 **Baseline first** - Run tests without acceleration to see what normally passes

The key insight: **Don't try to run all 3000+ tests**. Focus on the subset that:
1. Doesn't require external services
2. Tests code paths that Fast LiteLLM accelerates
3. Can run in both configurations (with/without acceleration)
