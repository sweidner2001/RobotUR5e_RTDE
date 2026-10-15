#!/usr/bin/env bash
# Exit immediately on errors, treat unset variables as errors, and fail on pipeline errors.
set -euo pipefail

# Variables:
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BASE_CODE_DIR="sys-code"
VENV_DIR="$PROJECT_ROOT/.venv"
REQ_FILE="$PROJECT_ROOT/requirements.txt"
USE_UV=false

cd "$PROJECT_ROOT"


# 1. Ask user about uv preference, check or install uv, and abort if impossible when chosen.
use_uv_for_create_venv() {
  read -rp "Would you like to use uv for environment creation? (Y/n): " choice
  case "$choice" in 
    [nN][oO]|[nN])
      echo "Skipping uv. Using standard python3 -m venv / virtualenv..."
      USE_UV=false
      ;;
    *)
      if command -v uv >/dev/null 2>&1; then
        echo "uv is already installed."
        USE_UV=true
      else
        echo "Installing uv..."
        if curl -LsSf https://astral.sh/uv/install.sh | sh >/dev/null 2>&1; then
          export PATH="$HOME/.local/bin:$PATH"
        fi
        
        if command -v uv >/dev/null 2>&1; then
          USE_UV=true
        else
          echo "Failed to install uv. Aborting."
          exit 1
        fi
      fi
      ;;
  esac
}

error_text_create_venv_std() {
  echo "Failed to create virtual environment."
  echo "Install one of the following and rerun:"
  echo "  - python3-venv (for python3 -m venv) (Command: 'sudo apt install python3.12-venv')"
  echo "  - virtualenv (Command: 'sudo apt install virtualenv')"
}



# 3. Create virtual environment with uv.
create_venv_uv() {
  echo "Creating virtual environment with uv..."
  uv venv "$VENV_DIR"
}

# 4. Create virtual environment with python3-venv or virtualenv
create_venv_std() {

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

  error_text_create_venv_std
  exit 1
}


# 5. Register $BASE_CODE_DIR as a source root (.pth file)
register_python_source_root() {
  SITE_PACKAGES="$VENV_DIR/lib/python$(python -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')/site-packages"
  if [[ -d "$PROJECT_ROOT/$BASE_CODE_DIR" && -d "$SITE_PACKAGES" ]]; then
    echo "$PROJECT_ROOT/$BASE_CODE_DIR" > "$SITE_PACKAGES/$BASE_CODE_DIR.pth"
  else
    echo "Warning: Could not register $BASE_CODE_DIR as a Python source root; source or site-packages directory is missing." >&2
  fi
}

# 6. Install dependencies using uv pip.
install_dependencies_uv() {
  if [[ -f "$REQ_FILE" ]]; then
    echo "Installing dependencies with uv..."
    uv pip install -r "$REQ_FILE"
  else
    echo "No requirements.txt found. Skipping dependency install."
  fi
}

# 7. Install dependencies using standard pip.
install_dependencies_std() {
  # Keep pip up to date to reduce install issues with older bundled versions.
  python -m pip install --upgrade pip

  # Install dependencies if requirements.txt exists.
  if [[ -f "$REQ_FILE" ]]; then
    echo "Installing dependencies with standard pip..."
    python -m pip install -r "$REQ_FILE"
  else
    # Continue without failing if the dependency file is missing.
    echo "No requirements.txt found. Skipping dependency install."
  fi
}




# --- Execution Workflow ---
uv_workflow() {
  # Create or repair venv
  if [[ ! -d "$VENV_DIR" ]]; then
    echo "Creating virtual environment in: $VENV_DIR"
    create_venv_uv
  elif [[ ! -f "$VENV_DIR/bin/activate" ]]; then
    echo "Existing virtual environment is incomplete. Recreating: $VENV_DIR"
    rm -rf "$VENV_DIR"
    create_venv_uv
  else
    echo "Using existing virtual environment: $VENV_DIR"
  fi

  source "$VENV_DIR/bin/activate"
  register_python_source_root
  install_dependencies_uv
}

std_workflow() {
  # Create or repair venv
  if [[ ! -d "$VENV_DIR" ]]; then
    echo "Creating virtual environment in: $VENV_DIR"
    create_venv_std
  elif [[ ! -f "$VENV_DIR/bin/activate" ]]; then
    echo "Existing virtual environment is incomplete. Recreating: $VENV_DIR"
    rm -rf "$VENV_DIR"
    create_venv_std
  else
    echo "Using existing virtual environment: $VENV_DIR"
  fi

  # Activate the virtual environment
  # shellcheck disable=SC1091
  source "$VENV_DIR/bin/activate"

  # Sanity-check only in the standard workflow: pip available inside .venv?
  if ! python -m pip --version >/dev/null 2>&1; then
    echo "The virtual environment exists, but pip is not available inside it."
    echo "Install one of the following and rerun setup.sh:"
    echo "  - python3-venv"
    echo "  - python3-pip"
    exit 1
  fi

  register_python_source_root
  install_dependencies_std
}





# --- Main Execution ---
# Ask user for uv preference first
use_uv_for_create_venv

# Run the appropriate workflow
if [[ "$USE_UV" == "true" ]]; then
  uv_workflow
else
  std_workflow
fi

# Final usage hint for the user.
echo "Setup complete. Activate with: source .venv/bin/activate"




