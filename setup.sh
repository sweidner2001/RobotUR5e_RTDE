#!/usr/bin/env bash
# Exit immediately on errors, treat unset variables as errors, and fail on pipeline errors.
set -euo pipefail

# Resolve the repository root to make path handling independent of current working directory.
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# Path to the local virtual environment folder.
VENV_DIR="$PROJECT_ROOT/.venv"
# Path to the dependency file used for pip installation.
REQ_FILE="$PROJECT_ROOT/requirements.txt"

# Create a virtual environment using python3 -m venv if available.
# If that fails, try virtualenv as a fallback.
create_venv() {
  # Preferred approach: stdlib venv from python3.
  if command -v python3 >/dev/null 2>&1; then
    if python3 -m venv "$VENV_DIR" >/dev/null 2>&1; then
      return 0
    fi
  fi

  # Fallback approach: external virtualenv tool.
  if command -v virtualenv >/dev/null 2>&1; then
    virtualenv "$VENV_DIR"
    return 0
  fi

  # Neither approach worked. Print actionable install hints and stop.
  echo "Failed to create virtual environment."
  echo "Install one of the following and rerun:"
  echo "  - python3-venv (for python3 -m venv) (Command: 'sudo apt install python3.12-venv')"
  echo "  - virtualenv (Command: 'sudo apt install virtualenv')"
  exit 1
}

# Create the venv when it does not exist yet.
if [[ ! -d "$VENV_DIR" ]]; then
  echo "Creating virtual environment in: $VENV_DIR"
  create_venv
else
  # Reuse existing venv if already present.
  echo "Using existing virtual environment: $VENV_DIR"
fi

# Repair case: folder exists but activation script is missing -> incomplete/broken venv.
if [[ ! -f "$VENV_DIR/bin/activate" ]]; then
  echo "Existing virtual environment is incomplete. Recreating: $VENV_DIR"
  # Remove broken environment and recreate from scratch.
  rm -rf "$VENV_DIR"
  create_venv
fi

# Activate the virtual environment in this shell process.
# shellcheck disable=SC1091
source "$VENV_DIR/bin/activate"

# Sanity-check that pip is available inside the venv before trying installs.
if ! python -m pip --version >/dev/null 2>&1; then
  echo "The virtual environment exists, but pip is not available inside it."
  echo "Install one of the following and rerun setup.sh:"
  echo "  - python3-venv"
  echo "  - python3-pip"
  exit 1
fi

# Keep pip up to date to reduce install issues with older bundled versions.
python -m pip install --upgrade pip

# Install dependencies if requirements.txt exists.
if [[ -f "$REQ_FILE" ]]; then
  python -m pip install -r "$REQ_FILE"
else
  # Continue without failing if the dependency file is missing.
  echo "No requirements.txt found. Skipping dependency install."
fi

# Final usage hint for the user.
echo "Setup complete. Activate with: source .venv/bin/activate"
