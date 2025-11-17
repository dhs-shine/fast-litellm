#!/bin/bash
# Setup LiteLLM for integration testing
# This script clones LiteLLM and sets up the environment for testing

set -e  # Exit on error

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
LITELLM_DIR="${PROJECT_ROOT}/.litellm"
LITELLM_REPO="https://github.com/BerriAI/litellm.git"
LITELLM_BRANCH="${LITELLM_BRANCH:-main}"

echo "========================================="
echo "Fast LiteLLM - LiteLLM Integration Setup"
echo "========================================="
echo ""

# Check if we're in a virtual environment
check_venv() {
    if [[ -n "$VIRTUAL_ENV" ]]; then
        echo "✅ Virtual environment detected: $VIRTUAL_ENV"
        return 0
    else
        return 1
    fi
}

# Check for externally-managed-environment marker
is_externally_managed() {
    python3 -c "import sys; import os; marker = os.path.join(sys.base_prefix, 'EXTERNALLY-MANAGED'); exit(0 if os.path.exists(marker) else 1)" 2>/dev/null
}

# Setup virtual environment if needed
setup_venv() {
    local venv_dir="$PROJECT_ROOT/.venv"

    if [ -d "$venv_dir" ]; then
        echo "📦 Virtual environment already exists at: $venv_dir"
        read -p "Do you want to use it? (Y/n): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Nn]$ ]]; then
            source "$venv_dir/bin/activate"
            echo "✅ Activated existing virtual environment"
            return 0
        fi
    fi

    echo "📦 Creating virtual environment at: $venv_dir"
    python3 -m venv "$venv_dir" || {
        echo "❌ Failed to create virtual environment"
        echo ""
        echo "Please install python3-venv:"
        echo "  sudo apt install python3-venv  # Ubuntu/Debian"
        echo "  sudo dnf install python3-virtualenv  # Fedora"
        exit 1
    }

    source "$venv_dir/bin/activate"
    echo "✅ Created and activated virtual environment"

    # Upgrade pip in the venv
    pip install --upgrade pip

    # Install essential build tools
    echo "📦 Installing build tools (maturin, pytest)..."
    pip install maturin pytest pytest-asyncio
}

# Check virtual environment
if ! check_venv; then
    if is_externally_managed; then
        echo "⚠️  Detected externally-managed Python environment (PEP 668)"
        echo ""
        echo "You have two options:"
        echo "  1. Let this script create a virtual environment (recommended)"
        echo "  2. Activate your own virtual environment and run this script again"
        echo ""
        read -p "Create virtual environment? (Y/n): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Nn]$ ]]; then
            setup_venv
        else
            echo ""
            echo "Please activate a virtual environment and run this script again:"
            echo "  python3 -m venv .venv"
            echo "  source .venv/bin/activate"
            echo "  ./scripts/setup_litellm.sh"
            exit 1
        fi
    else
        echo "⚠️  No virtual environment detected"
        echo ""
        read -p "Create virtual environment? (Y/n): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Nn]$ ]]; then
            setup_venv
        fi
    fi
fi

# Check if LiteLLM directory exists
if [ -d "$LITELLM_DIR" ]; then
    echo "📁 LiteLLM directory exists at: $LITELLM_DIR"
    read -p "Do you want to update it? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "🔄 Updating LiteLLM..."
        cd "$LITELLM_DIR"
        git fetch origin
        git checkout "$LITELLM_BRANCH"
        git pull origin "$LITELLM_BRANCH"
    else
        echo "✅ Using existing LiteLLM installation"
    fi
else
    echo "📥 Cloning LiteLLM from $LITELLM_REPO..."
    git clone --branch "$LITELLM_BRANCH" --depth 1 "$LITELLM_REPO" "$LITELLM_DIR"
fi

echo ""
echo "📦 Installing LiteLLM dependencies..."
cd "$LITELLM_DIR"

# Try to install LiteLLM with proxy support, fall back to minimal
if pip install -e ".[proxy]" 2>/dev/null; then
    echo "✅ LiteLLM installed with proxy support"
elif pip install -e . 2>/dev/null; then
    echo "✅ LiteLLM installed (minimal)"
else
    echo "❌ Failed to install LiteLLM"
    echo ""
    echo "This might be due to missing system dependencies."
    echo "Try installing them manually:"
    echo "  cd $LITELLM_DIR"
    echo "  pip install -e ."
    exit 1
fi

echo ""
echo "✅ LiteLLM setup complete!"
echo ""
echo "LiteLLM Location: $LITELLM_DIR"
echo "Branch: $(cd "$LITELLM_DIR" && git branch --show-current)"
echo "Commit: $(cd "$LITELLM_DIR" && git rev-parse --short HEAD)"

if [[ -n "$VIRTUAL_ENV" ]]; then
    echo "Virtual Environment: $VIRTUAL_ENV"
fi

echo ""
echo "Next steps:"
echo "  1. Build Fast LiteLLM: maturin develop"
echo "  2. Run integration tests: ./scripts/run_litellm_tests.sh"
echo "  3. Or run specific test: ./scripts/run_litellm_tests.sh tests/test_completion.py"
echo ""
echo "💡 Tip: Keep this terminal session open to maintain the virtual environment"
