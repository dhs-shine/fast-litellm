# Virtual Environment Guide

Fast LiteLLM's integration testing scripts automatically handle virtual environments to comply with PEP 668 (externally-managed-environment).

## What is PEP 668?

Starting with Python 3.11 on modern Linux distributions (Debian, Ubuntu, Fedora, etc.), the system Python is marked as "externally-managed" to prevent conflicts between pip and the system package manager.

This means you'll see errors like:
```
error: externally-managed-environment

× This environment is externally managed
```

## Automatic Virtual Environment Handling

The Fast LiteLLM integration scripts automatically detect and handle this:

### Option 1: Automatic Setup (Recommended)

Just run the setup script - it will detect PEP 668 and offer to create a virtual environment:

```bash
./scripts/setup_litellm.sh
```

The script will:
1. Detect if you're in an externally-managed environment
2. Offer to create a `.venv` directory automatically
3. Activate it for you
4. Install all dependencies in the venv

**Interactive prompts:**
```
⚠️  Detected externally-managed Python environment (PEP 668)

You have two options:
  1. Let this script create a virtual environment (recommended)
  2. Activate your own virtual environment and run this script again

Create virtual environment? (Y/n):
```

### Option 2: Manual Virtual Environment

If you prefer to manage your own virtual environment:

```bash
# Create virtual environment
python3 -m venv .venv

# Activate it
source .venv/bin/activate

# Now run setup
./scripts/setup_litellm.sh
```

## Using the Scripts

### First Time Setup

```bash
# Run setup (it will create .venv automatically if needed)
./scripts/setup_litellm.sh

# The script will activate the venv and install everything
# Keep this terminal session open!
```

### Subsequent Usage

The test runner scripts automatically handle activation:

```bash
# Run tests (auto-activates .venv if it exists)
./scripts/run_litellm_tests.sh

# Compare performance (checks for active venv)
./scripts/compare_performance.py tests/
```

### Manual Activation

If you prefer to activate manually:

```bash
# Activate the venv
source .venv/bin/activate

# Your prompt will change to show (venv)
# Now you can run any command

./scripts/run_litellm_tests.sh
pytest tests/
maturin develop
```

## Virtual Environment Location

The scripts create and look for `.venv` in the project root:

```
fast-litellm/
├── .venv/              # Virtual environment (auto-created)
├── .litellm/           # LiteLLM clone (for testing)
├── scripts/
├── tests/
└── ...
```

## Troubleshooting

### "No virtual environment detected"

**Cause:** You're not in a venv and one doesn't exist.

**Solution:**
```bash
./scripts/setup_litellm.sh
# Accept the prompt to create one
```

### "Virtual environment exists but not activated"

**Cause:** `.venv` exists but you haven't activated it.

**Solution:**
```bash
source .venv/bin/activate
./scripts/run_litellm_tests.sh
```

Or let the script auto-activate it (for bash scripts only).

### "python3-venv not found"

**Cause:** The `venv` module isn't installed.

**Solution:**
```bash
# Ubuntu/Debian
sudo apt install python3-venv python3-full

# Fedora
sudo dnf install python3-virtualenv

# Arch
sudo pacman -S python-virtualenv
```

### "Failed to create virtual environment"

**Possible causes:**
1. Missing `python3-venv` package (install as above)
2. Permission issues (check directory permissions)
3. Insufficient disk space

### Want to use a different location?

You can use your own virtual environment:

```bash
# Create wherever you want
python3 -m venv ~/myenvs/fast-litellm

# Activate it
source ~/myenvs/fast-litellm/bin/activate

# Run scripts (they'll detect the active venv)
./scripts/setup_litellm.sh
```

## Multiple Python Versions

If you have multiple Python versions:

```bash
# Use specific Python version
python3.11 -m venv .venv
source .venv/bin/activate

# Verify version
python --version

# Now setup
./scripts/setup_litellm.sh
```

## CI/CD Environments

In CI/CD, virtual environments are typically created automatically:

```yaml
# GitHub Actions example
- name: Set up Python
  uses: actions/setup-python@v5
  with:
    python-version: '3.11'

- name: Create venv and install
  run: |
    python -m venv .venv
    source .venv/bin/activate
    ./scripts/setup_litellm.sh
```

## Cleanup

To remove the virtual environment:

```bash
# Simply delete the directory
rm -rf .venv

# Next time you run setup, it will recreate it
./scripts/setup_litellm.sh
```

## Best Practices

1. **Use `.venv`**: Keep the default location for consistency
2. **Keep Terminal Open**: Venv activation lasts for the terminal session
3. **Check Before Running**: Verify venv is active (`echo $VIRTUAL_ENV`)
4. **One Venv Per Project**: Don't share venvs between projects
5. **Don't Commit**: `.venv` is in `.gitignore` - never commit it

## Script Behavior Summary

| Script | Auto-Activates .venv? | Creates .venv? | Requires Active Venv? |
|--------|----------------------|----------------|----------------------|
| `setup_litellm.sh` | Yes | Yes (with prompt) | No (creates if needed) |
| `run_litellm_tests.sh` | Yes (bash only) | No | Strongly recommended |
| `compare_performance.py` | No | No | Yes (checks and warns) |

## System-Wide Installation (Not Recommended)

If you really want to bypass PEP 668 and install system-wide:

```bash
# NOT RECOMMENDED - can break your system
pip install --break-system-packages litellm

# Or use pipx for isolated app installation
pipx install litellm
```

**We strongly recommend using virtual environments instead** - they're safer, cleaner, and the standard Python practice.

## Further Reading

- [Python Virtual Environments Tutorial](https://docs.python.org/3/tutorial/venv.html)
- [PEP 668 Specification](https://peps.python.org/pep-0668/)
- [Real Python venv Guide](https://realpython.com/python-virtual-environments-a-primer/)
