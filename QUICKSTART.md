# Quick Start Guide

Get Fast LiteLLM up and running with integration tests in 5 minutes.

## Prerequisites

- Python 3.8+
- Rust toolchain (install from https://rustup.rs)
- Git

### Install Rust (if needed)

```bash
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
source $HOME/.cargo/env
```

## Step-by-Step Setup

### 1. Clone and Enter Repository

```bash
git clone https://github.com/neul-labs/fast-litellm.git
cd fast-litellm
```

### 2. Run Automated Setup

This single command will:
- Create a virtual environment (`.venv`)
- Install maturin and pytest
- Clone LiteLLM
- Install LiteLLM dependencies

```bash
./scripts/setup_litellm.sh
```

**When prompted:**
```
Create virtual environment? (Y/n): Y  [Press Y]
```

The script will handle everything automatically!

### 3. Build Fast LiteLLM

```bash
# The venv is still active from the previous step
maturin develop
```

This compiles the Rust code and creates the Python extension.

### 4. Run Integration Tests

```bash
# Run a quick test to verify everything works
./scripts/run_litellm_tests.sh tests/test_completion.py -k test_completion_openai
```

Or run all tests:

```bash
./scripts/run_litellm_tests.sh
```

### 5. Compare Performance

```bash
# See the speedup!
./scripts/compare_performance.py tests/test_completion.py
```

## Complete Workflow Example

```bash
# One-time setup
git clone https://github.com/neul-labs/fast-litellm.git
cd fast-litellm
./scripts/setup_litellm.sh  # Press Y when prompted
maturin develop

# Run tests
./scripts/run_litellm_tests.sh tests/test_completion.py

# Compare performance
./scripts/compare_performance.py tests/test_completion.py
```

## What Each Command Does

| Command | What it does |
|---------|--------------|
| `setup_litellm.sh` | Creates venv, clones LiteLLM, installs deps |
| `maturin develop` | Builds Rust code into Python extension |
| `run_litellm_tests.sh` | Runs LiteLLM tests with acceleration |
| `compare_performance.py` | Measures speedup vs baseline |

## Expected Output

### After `setup_litellm.sh`:
```
✅ Virtual environment activated
📥 Cloning LiteLLM...
📦 Installing LiteLLM dependencies...
✅ LiteLLM setup complete!
```

### After `maturin develop`:
```
📦 Compiling fast-litellm v0.1.0
    Finished dev [unoptimized + debuginfo] target(s) in 45.23s
📦 Built wheel for CPython 3.11
✅ Successfully installed fast-litellm-0.1.0
```

### After `run_litellm_tests.sh`:
```
✅ Fast LiteLLM is built and ready
🧪 Running LiteLLM tests with Fast LiteLLM acceleration...
============================================================
Fast LiteLLM Integration Test Session
============================================================
Fast LiteLLM Version: 0.1.0
Rust Acceleration: True
============================================================

tests/test_completion.py::test_completion_openai PASSED

✅ Tests completed successfully!
```

### After `compare_performance.py`:
```
======================================================================
                       PERFORMANCE COMPARISON
======================================================================

Metric                         Baseline        Accelerated     Improvement
------------------------------ --------------- --------------- ---------------
Execution Time                       45.23s          12.34s        3.67x faster
Tests Passed                            42              42       ✓ Same
Exit Code                                0               0       ✓ Both passed

✅ Fast LiteLLM provides 3.67x speedup without breaking tests!
```

## Troubleshooting

### "maturin: command not found"

The venv wasn't activated or maturin wasn't installed:

```bash
source .venv/bin/activate
pip install maturin
```

### "Rust toolchain not found"

Install Rust:

```bash
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
source $HOME/.cargo/env
```

### "externally-managed-environment" error

This is normal! The setup script handles it automatically. Just run:

```bash
./scripts/setup_litellm.sh
```

And press Y when it offers to create a virtual environment.

### "No module named 'fast_litellm'"

You need to build the package:

```bash
source .venv/bin/activate
maturin develop
```

### "LiteLLM not found"

You need to run setup first:

```bash
./scripts/setup_litellm.sh
```

## Next Steps

Once setup is complete:

1. **Make changes** to the Rust code in `src/`
2. **Rebuild** with `maturin develop`
3. **Test** with `./scripts/run_litellm_tests.sh`
4. **Benchmark** with `./scripts/compare_performance.py`

## Keeping Virtual Environment Active

The virtual environment stays active in your current terminal session.

**Tips:**
- Keep the terminal open while working
- Or activate manually: `source .venv/bin/activate`
- Your prompt shows `(.venv)` when active

## Clean Start

If you want to start over:

```bash
# Remove everything
rm -rf .venv .litellm

# Start fresh
./scripts/setup_litellm.sh
maturin develop
```

## Resources

- [Full Testing Guide](docs/testing.md)
- [Virtual Environment Guide](docs/virtual-environments.md)
- [Contributing Guide](docs/contributing.md)
- [Scripts README](scripts/README.md)

## Getting Help

- Issues: https://github.com/neul-labs/fast-litellm/issues
- Discussions: https://github.com/neul-labs/fast-litellm/discussions

---

**Time to first test:** ~5 minutes
**Time to full setup:** ~10 minutes (including Rust compilation)
