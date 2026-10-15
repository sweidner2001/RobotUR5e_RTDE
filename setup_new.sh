#!/usr/bin/env bash
# Exit immediately on errors, treat unset variables as errors, and fail on pipeline errors.
set -euo pipefail

#************************ Variables: ************************
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BASE_CODE_DIR="sys-code"
VENV_DIR="$PROJECT_ROOT/.venv"
REQ_FILE="$PROJECT_ROOT/requirements.txt"
PYTHON_VERSION_FILE="$PROJECT_ROOT/.python-version"
USE_UV=false

cd "$PROJECT_ROOT"




#********************* Functions ************************
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
  local target_python="$1"
  local venv_package="${target_python}-venv"

  echo "Failed to create virtual environment."
  echo "Install one of the following and rerun:"
  echo "  - $venv_package (for $target_python -m venv) (Command: 'sudo apt install $venv_package')"
  echo "  - virtualenv (Command: 'sudo apt install virtualenv')"
}




# 2. Resolve Python version, display user's current version, and offer fallback or hints if missing.
resolve_python_version() {
  local target_python="python3"
  local current_system_version="unknown"

  if command -v python3 >/dev/null 2>&1; then
    current_system_version=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")' 2>/dev/null || echo "unknown")
  fi

  if [[ -f "$PYTHON_VERSION_FILE" ]]; then
    local pinned_version
    pinned_version=$(tr -d '[:space:]' < "$PYTHON_VERSION_FILE")
    if [[ -n "$pinned_version" ]]; then
      local short_version
      short_version=$(echo "$pinned_version" | cut -d. -f1-2)
      
      if command -v "python$short_version" >/dev/null 2>&1; then
        target_python="python$short_version"
        echo "Found .python-version ($pinned_version). Using $target_python for creating the .venv" >&2
      else
        echo "" >&2
        echo "========================================================" >&2
        echo "WARNING: Specified Python version ($pinned_version) from .python-version" >&2
        echo "         is not installed on your system." >&2
        echo "         Your current system Python version is: $current_system_version" >&2
        echo "========================================================" >&2
        echo "Hint: You can install version $pinned_version using:" >&2
        echo "  - pyenv:   pyenv install $pinned_version" >&2
        echo "  - Website: https://www.python.org/downloads/" >&2
        echo "" >&2

        read -rp "Would you like to use your default system Python ($current_system_version) instead? (y/N): " choice
        case "$choice" in
          [yY][eE][sS]|[yY])
            echo "Proceeding with default system python3..." >&2
            target_python="python3"
            ;;
          *)
            echo "Error: Required Python version $pinned_version is not available and system Python fallback was declined." >&2
            exit 1
            ;;
        esac
      fi
    fi
  fi

  echo "$target_python"
}

# 3. Create virtual environment with uv.
create_venv_uv() {
  echo "Creating virtual environment with uv..."
  uv venv "$VENV_DIR"
}

# 4. Create virtual environment with python3-venv or virtualenv
create_venv_std() {
  local target_python
  target_python=$(resolve_python_version)

  # Preferred approach: stdlib venv from target python.
  if command -v "$target_python" >/dev/null 2>&1; then
    if "$target_python" -m venv "$VENV_DIR" >/dev/null 2>&1; then
      return 0
    fi
  fi

  # Fallback approach: external virtualenv tool.
  if command -v virtualenv >/dev/null 2>&1; then
    virtualenv "$VENV_DIR"
    return 0
  fi

  error_text_create_venv_std "$target_python"
  exit 1
}

# 5. Register $BASE_CODE_DIR as a source root (.pth file)
register_python_source_root() {
  local venv_python="$VENV_DIR/bin/python"
  local py_ver
  py_ver=$("$venv_python" -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
  SITE_PACKAGES="$VENV_DIR/lib/python$py_ver/site-packages"

  # SITE_PACKAGES="$VENV_DIR/lib/python$(python -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')/site-packages"
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
    echo "No requirements.txt found. Skipping dependency install."
  fi
}


# 8. Checks
pip_check_in_venv() {
  if ! python -m pip --version >/dev/null 2>&1; then
    echo "The virtual environment exists, but pip is not available inside it."
    echo "Install one of the following and rerun setup.sh:"
    echo "  - python3-venv"
    echo "  - python3-pip"
    exit 1
  fi
}





#********************* Workflows ************************
uv_workflow() {
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

  # shellcheck disable=SC1091
  source "$VENV_DIR/bin/activate"
  pip_check_in_venv
  register_python_source_root
  install_dependencies_std
}



#******************* Main Execution ******************************
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