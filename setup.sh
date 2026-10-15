#!/usr/bin/env bash

# Infos:
#   - '>/dev/null' sends standard output (file descriptor 1) to /dev/null, a special destination that throws away anything written to it.
#   - '2>&1' sends standard error (file descriptor 2) to the same place standard output is currently going.



# Exit immediately on errors, treat unset variables as errors, and fail on pipeline errors.
set -euo pipefail

# Variables:
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$PROJECT_ROOT/.venv"
REQ_FILE="$PROJECT_ROOT/requirements.txt"
TOML_FILE="$PROJECT_ROOT/pyproject.toml"
BASE_CODE_DIR="sys-code"
USE_UV=false

# 1. Check if 'uv' is available and install it
if command -v uv >/dev/null 2>&1; then
  USE_UV=true
else
  echo "Notice: 'uv' is not installed."
  read -rp "Would you like to automatically install uv in your user directory? (Y/n): " choice
  case "$choice" in 
    [nN][oO]|[nN])
      echo "Skipping uv. Using classic python3 -m venv..."
      ;;
    *)
      echo "Installing uv..."
      if curl -LsSf https://astral.sh/uv/install.sh | sh >/dev/null 2>&1; then
        # Add a new place to search while preserving the existing search paths
        export PATH="$HOME/.local/bin:$PATH"

        # Check if 'uv' is now available
        if command -v uv >/dev/null 2>&1; then
          USE_UV=true
        else
          echo "Automatic installation of uv failed. Falling back to classic venv..."
        fi
      else
        echo "Automatic installation of uv failed. Falling back to classic venv..."
      fi
      ;;
  esac
fi



# 2. If uv is not used, check Python version against pyproject.toml requirements
if [ "$USE_UV" = false ] && [ -f "$TOML_FILE" ]; then
  # Try to read requires-python from pyproject.toml (e.g., ">=3.11,<3.13")
  REQUIRED_RANGE=$(grep -E '^\s*requires-python\s*=' "$TOML_FILE" | sed -E 's/.*=\s*"(.*)"/\1/' || true)
  
  if [ -n "$REQUIRED_RANGE" ]; then
    CURRENT_PYTHON_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")' 2>/dev/null || echo "0.0.0")
    
    echo "Required Python version (from pyproject.toml): $REQUIRED_RANGE"
    echo "Currently active system Python version:       $CURRENT_PYTHON_VERSION"
    echo "WARNING: Without 'uv', your system Python ($CURRENT_PYTHON_VERSION) will be used."
    echo "Please ensure this version satisfies the project requirements ($REQUIRED_RANGE)."
    
    read -rp "Do you want to continue with this Python version? (y/N): " proceed
    case "$proceed" in
      [yY][eE][sS]|[yY])
        echo "Proceeding..."
        ;;
      *)
        echo "Setup aborted. Please install the correct Python version or use 'uv'."
        exit 1
        ;;
    esac
  fi
fi

# Function to create the virtual environment
create_venv() {
  if [ "$USE_UV" = true ]; then
    echo "Creating virtual environment with uv (automatically fetches the correct Python version)..."
    if uv venv "$VENV_DIR" >/dev/null 2>&1; then
      return 0
    fi
    echo "uv venv failed, attempting classic fallback..."
    USE_UV=false
  fi

  # Fallback: python3 -m venv virtualenv
  if command -v python3 >/dev/null 2>&1; then
    if python3 -m venv "$VENV_DIR" >/dev/null 2>&1; then
      return 0
    fi
  fi

    # Fallback: virtualenv
  if command -v virtualenv >/dev/null 2>&1; then
    virtualenv "$VENV_DIR"
    return 0
  fi

  echo "Error: Failed to create virtual environment."
  echo "Please install 'python3-venv' or 'uv'."
  exit 1
}

# Create or check the venv
if [[ ! -d "$VENV_DIR" ]]; then
  echo "Creating virtual environment in: $VENV_DIR"
  create_venv
else
  echo "Using existing virtual environment: $VENV_DIR"
fi

# Repair case: folder exists, but the activate script is missing
if [[ ! -f "$VENV_DIR/bin/activate" ]]; then
  echo "Virtual environment is incomplete. Recreating..."
  rm -rf "$VENV_DIR"
  create_venv
fi

# Activate the virtual environment
# shellcheck disable=SC1091
source "$VENV_DIR/bin/activate"

# Sanity-check for pip / python
if ! python -m pip --version >/dev/null 2>&1 && [ "$USE_UV" = false ]; then
  echo "Error: pip is not available inside the virtual environment."
  echo "Please install python3-pip / python3-venv."
  exit 1
fi

# Register the sys-code module path
SITE_PACKAGES="$VENV_DIR/lib/python$(python -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')/site-packages"
if [[ -d "$PROJECT_ROOT/$BASE_CODE_DIR" ]]; then
  echo "$PROJECT_ROOT/$BASE_CODE_DIR" > "$SITE_PACKAGES/$BASE_CODE_DIR.pth"
fi

# Install dependencies
if [[ -f "$REQ_FILE" ]]; then
  if [ "$USE_UV" = true ]; then
    echo "Installing dependencies with uv (blazing fast)..."
    uv pip install -r "$REQ_FILE"
  else
    echo "Upgrading pip..."
    python -m pip install --upgrade pip
    echo "Installing dependencies with classic pip..."
    python -m pip install -r "$REQ_FILE"
  fi
else
  echo "No requirements.txt found. Skipping dependency installation."
fi

echo "Setup completed successfully! Activate with: source .venv/bin/activate"