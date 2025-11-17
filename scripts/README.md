# Scripts Directory

This directory contains utility scripts for development, testing, and deployment of Fast LiteLLM.

## Integration Testing Scripts

### `setup_litellm.sh`

Sets up LiteLLM for integration testing by cloning the repository and installing dependencies.

**Usage:**
```bash
./scripts/setup_litellm.sh
```

**Options:**
- `LITELLM_BRANCH`: Specify which branch to clone (default: `main`)

**Example:**
```bash
# Clone specific branch
LITELLM_BRANCH=development ./scripts/setup_litellm.sh
```

**What it does:**
1. Clones LiteLLM to `.litellm/` directory
2. Installs LiteLLM and its dependencies
3. Sets up the test environment

---

### `run_litellm_tests.sh`

Runs LiteLLM's test suite with Fast LiteLLM acceleration enabled.

**Usage:**
```bash
# Run all tests
./scripts/run_litellm_tests.sh

# Run specific test file
./scripts/run_litellm_tests.sh tests/test_completion.py

# Run specific test function
./scripts/run_litellm_tests.sh tests/test_completion.py::test_completion_openai

# Pass additional pytest arguments
./scripts/run_litellm_tests.sh tests/ -v --tb=long -x
```

**What it does:**
1. Verifies Fast LiteLLM is built
2. Creates a pytest configuration that imports `fast_litellm` before running tests
3. Runs the specified tests with acceleration enabled
4. Reports performance statistics

**Exit codes:**
- `0`: All tests passed
- `1+`: Test failures (check output for details)

---

### `compare_performance.py`

Compares LiteLLM test performance with and without Fast LiteLLM acceleration.

**Usage:**
```bash
# Full comparison (runs tests twice)
./scripts/compare_performance.py tests/test_completion.py

# Skip baseline (only test with acceleration)
./scripts/compare_performance.py tests/test_completion.py --skip-baseline

# Specify custom LiteLLM directory
./scripts/compare_performance.py tests/ --litellm-dir /path/to/litellm
```

**What it does:**
1. Runs tests without Fast LiteLLM (baseline)
2. Runs tests with Fast LiteLLM (accelerated)
3. Compares execution time, test results, and exit codes
4. Generates a detailed comparison report

**Example output:**
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

---

## Development Scripts

### `setup_dev.sh`

Quick development environment setup (if it exists in your workflow).

**Usage:**
```bash
./scripts/setup_dev.sh
```

---

### `test_package.py`

Package validation and testing utilities.

**Usage:**
```bash
python scripts/test_package.py
```

---

## Common Workflows

### Initial Setup

```bash
# 1. Setup development environment
pip install maturin
maturin develop

# 2. Setup LiteLLM for integration testing
./scripts/setup_litellm.sh
```

### Development Cycle

```bash
# 1. Make changes to code
# 2. Rebuild
maturin develop

# 3. Run unit tests
pytest tests/

# 4. Run integration tests
./scripts/run_litellm_tests.sh tests/test_completion.py
```

### Before Release

```bash
# 1. Full test suite
pytest tests/ -v

# 2. Integration tests
./scripts/run_litellm_tests.sh

# 3. Performance comparison
./scripts/compare_performance.py tests/

# 4. Build release
maturin build --release
```

### Debugging Failed Tests

```bash
# 1. Run with verbose output
./scripts/run_litellm_tests.sh tests/test_failing.py -vv

# 2. Compare with baseline
./scripts/compare_performance.py tests/test_failing.py

# 3. Run specific test without acceleration
cd .litellm
pytest tests/test_failing.py -v
```

## Environment Variables

### LiteLLM Configuration

- `LITELLM_BRANCH`: Branch to clone (default: `main`)
- `LITELLM_DIR`: Custom LiteLLM directory location

### Fast LiteLLM Configuration

- `FAST_LITELLM_DISABLE`: Disable acceleration (`true`/`false`)
- `FAST_LITELLM_RUST_ROUTING`: Enable/disable routing acceleration
- `FAST_LITELLM_FEATURE_CONFIG`: Path to custom feature config

### Testing

- `PYTEST_PLUGINS`: Additional pytest plugins
- `PYTHONPATH`: Python module search path

## Troubleshooting

### "LiteLLM not found"

**Solution:** Run `./scripts/setup_litellm.sh` first

### "Rust extensions not available"

**Solution:** Build Fast LiteLLM with `maturin develop`

### "Tests failing with acceleration but passing without"

**Possible causes:**
1. Fast LiteLLM broke functionality (report issue)
2. Test environment differences (check API keys, network)
3. Timing-sensitive tests (might need adjustment)

**Debug steps:**
```bash
# 1. Verify baseline passes
cd .litellm && pytest tests/test_failing.py

# 2. Compare behavior
./scripts/compare_performance.py tests/test_failing.py

# 3. Check acceleration status
python -c "import fast_litellm; print(fast_litellm.get_patch_status())"
```

### "Permission denied" errors

**Solution:** Make scripts executable
```bash
chmod +x scripts/*.sh scripts/*.py
```

## Contributing

When adding new scripts:

1. Add executable permissions: `chmod +x script_name.sh`
2. Add usage documentation to this README
3. Include example usage
4. Handle errors gracefully
5. Provide helpful error messages

## Resources

- [Testing Guide](../docs/testing.md)
- [Contributing Guide](../docs/contributing.md)
- [LiteLLM Repository](https://github.com/BerriAI/litellm)
