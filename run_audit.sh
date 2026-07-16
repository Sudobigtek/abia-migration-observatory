#!/bin/bash
# =============================================================================
# Codebase Doctor — FULLY AUTOMATED Audit Runner for Abia Migration Observatory
# =============================================================================
# INSTRUCTIONS:
#   1. Save this file as run_audit.sh in your project root
#   2. Make it executable: chmod +x run_audit.sh
#   3. Run it: ./run_audit.sh
#   4. That's it. No other steps needed.
# =============================================================================

set -euo pipefail

# --- Colors for output ---
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# --- Script location ---
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# =============================================================================
# STEP 1: FIND THE PROJECT (where manage.py lives)
# =============================================================================
echo -e "${BLUE}🔍 STEP 1: Looking for your Django project...${NC}"

PROJECT_ROOT="/home/abia/abia-migration-observatory/abia-app"
SEARCH_PATHS=(
    "${SCRIPT_DIR}"
    "${SCRIPT_DIR}/.."
    "${SCRIPT_DIR}/../.."
    "${HOME}/abia-migration-observatory"
    "${HOME}/abia"
    "${HOME}/workspace/abia"
    "${HOME}/projects/abia"
    "/home/abia/abia-migration-observatory"
    "/home/abia/abia"
    "."
)

for path in "${SEARCH_PATHS[@]}"; do
    resolved=$(cd "$path" 2>/dev/null && pwd) || continue
    if [ -f "${resolved}/manage.py" ]; then
        PROJECT_ROOT="$resolved"
        break
    fi
    # Check common subdirectories
    for sub in src app backend api; do
        if [ -f "${resolved}/${sub}/manage.py" ]; then
            PROJECT_ROOT="${resolved}/${sub}"
            break 2
        fi
    done
done

if [ -z "$PROJECT_ROOT" ]; then
    echo -e "${RED}❌ Could not find manage.py automatically.${NC}"
    echo "   Searched in these locations:"
    printf '   • %s\n' "${SEARCH_PATHS[@]}"
    echo ""
    read -rp "   Paste the full path to your project folder (where manage.py is): " user_path
    user_path=$(echo "$user_path" | sed 's/\\/\//g')  # Convert Windows backslashes
    user_path=$(cd "$user_path" 2>/dev/null && pwd) || {
        echo -e "${RED}❌ Invalid path: $user_path${NC}"
        exit 1
    }
    if [ ! -f "${user_path}/manage.py" ]; then
        echo -e "${RED}❌ manage.py not found at ${user_path}/manage.py${NC}"
        exit 1
    fi
    PROJECT_ROOT="$user_path"
fi

echo -e "${GREEN}✅ Project found at: $PROJECT_ROOT${NC}"

# =============================================================================
# STEP 2: CHECK / ACTIVATE VIRTUAL ENVIRONMENT
# =============================================================================
echo -e "${BLUE}🔍 STEP 2: Checking Python virtual environment...${NC}"

if [ -z "${VIRTUAL_ENV:-}" ]; then
    echo -e "${YELLOW}⚠️  No virtual environment active.${NC}"

    # Look for common venv locations
    VENV_PATHS=(
        "${PROJECT_ROOT}/.venv"
        "${PROJECT_ROOT}/venv"
        "${PROJECT_ROOT}/env"
        "${HOME}/.venvs/abia"
        "${HOME}/venvs/abia"
    )

    FOUND_VENV=""
    for vpath in "${VENV_PATHS[@]}"; do
        if [ -f "${vpath}/bin/activate" ]; then
            FOUND_VENV="$vpath"
            break
        fi
    done

    if [ -n "$FOUND_VENV" ]; then
        echo -e "${GREEN}✅ Found virtual env at: $FOUND_VENV${NC}"
        echo -e "${BLUE}   Activating it now...${NC}"
        source "$FOUND_VENV/bin/activate"
        echo -e "${GREEN}✅ Virtual env activated: $VIRTUAL_ENV${NC}"
    else
        echo -e "${YELLOW}⚠️  No virtual env found. Will use system Python.${NC}"
        echo "   (This may cause import errors for project-specific packages)"
        read -rp "   Continue with system Python? [y/N]: " confirm
        if [[ ! "$confirm" =~ ^[Yy]$ ]]; then
            echo "   Create a venv first: python3 -m venv .venv && source .venv/bin/activate"
            exit 1
        fi
    fi
else
    echo -e "${GREEN}✅ Virtual env already active: $VIRTUAL_ENV${NC}"
fi

# =============================================================================
# STEP 3: INSTALL DEPENDENCIES (with retry logic for network issues)
# =============================================================================
echo -e "${BLUE}🔍 STEP 3: Installing audit dependencies...${NC}"

DEPS="rich bandit flake8 pytest pytest-json-report black isort autopep8"
MISSING_DEPS=""

for dep in $DEPS; do
    if ! python3 -c "import $dep" 2>/dev/null; then
        # Handle module names that differ from package names
        case "$dep" in
            pytest-json-report) pkg="pytest-json-report" ;;
            *) pkg="$dep" ;;
        esac
        MISSING_DEPS="$MISSING_DEPS $pkg"
    fi
done

if [ -z "$MISSING_DEPS" ]; then
    echo -e "${GREEN}✅ All dependencies already installed.${NC}"
else
    echo -e "${YELLOW}📦 Missing dependencies:$MISSING_DEPS${NC}"
    echo -e "${BLUE}   Installing (this may take a minute)...${NC}"

    # Try up to 3 times with different strategies
    for attempt in 1 2 3; do
        echo -e "${BLUE}   Attempt $attempt/3...${NC}"

        if [ "$attempt" -eq 1 ]; then
            pip install --quiet --default-timeout=120 $MISSING_DEPS 2>/dev/null && break
        elif [ "$attempt" -eq 2 ]; then
            pip install --quiet --default-timeout=300 --retries 5 $MISSING_DEPS 2>/dev/null && break
        else
            # Final attempt: install one by one, skip failures
            for pkg in $MISSING_DEPS; do
                echo -e "${YELLOW}   Trying individual install: $pkg${NC}"
                pip install --quiet --default-timeout=300 "$pkg" 2>/dev/null || {
                    echo -e "${YELLOW}   ⚠️  Could not install $pkg (will be skipped)${NC}"
                }
            done
            break
        fi
    done

    echo -e "${GREEN}✅ Dependency installation complete.${NC}"
fi

# Note: mypy is large and often fails on slow networks — we skip it by default
# If you want type checking, run: pip install mypy

# =============================================================================
# STEP 4: DOWNLOAD / LOCATE codebase_doctor.py
# =============================================================================
echo -e "${BLUE}🔍 STEP 4: Locating codebase_doctor.py...${NC}"

AUDIT_SCRIPT="${SCRIPT_DIR}/codebase_doctor.py"

if [ ! -f "$AUDIT_SCRIPT" ]; then
    # Try common download locations
    DOWNLOAD_PATHS=(
        "/mnt/c/Users/Admin/Downloads/codebase_doctor.py"
        "/mnt/c/Users/$(whoami)/Downloads/codebase_doctor.py"
        "${HOME}/Downloads/codebase_doctor.py"
        "${PROJECT_ROOT}/codebase_doctor.py"
        "${PROJECT_ROOT}/tools/codebase_doctor.py"
    )

    for dpath in "${DOWNLOAD_PATHS[@]}"; do
        if [ -f "$dpath" ]; then
            echo -e "${GREEN}✅ Found at: $dpath${NC}"
            echo -e "${BLUE}   Copying to script directory...${NC}"
            cp "$dpath" "$AUDIT_SCRIPT"
            break
        fi
    done
fi

if [ ! -f "$AUDIT_SCRIPT" ]; then
    echo -e "${RED}❌ codebase_doctor.py not found.${NC}"
    echo "   Searched in:"
    printf '   • %s\n' "${DOWNLOAD_PATHS[@]}"
    echo ""
    read -rp "   Paste the full path to codebase_doctor.py: " user_script
    user_script=$(echo "$user_script" | sed 's/\\/\//g')
    if [ ! -f "$user_script" ]; then
        echo -e "${RED}❌ File not found: $user_script${NC}"
        exit 1
    fi
    cp "$user_script" "$AUDIT_SCRIPT"
fi

echo -e "${GREEN}✅ Using: $AUDIT_SCRIPT${NC}"

# =============================================================================
# STEP 5: RUN THE AUDIT
# =============================================================================
echo ""
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}  🚀 RUNNING CODEBASE DOCTOR${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo ""

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
OUTPUT_DIR="${SCRIPT_DIR}/audit_output_${TIMESTAMP}"

python3 "$AUDIT_SCRIPT" \
    --path "$PROJECT_ROOT" \
    --output "$OUTPUT_DIR" \
    --fix

# =============================================================================
# STEP 6: DISPLAY RESULTS
# =============================================================================
echo ""
echo -e "${GREEN}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}  ✅ AUDIT COMPLETE${NC}"
echo -e "${GREEN}═══════════════════════════════════════════════════════════════${NC}"
echo ""
echo -e "${BLUE}📁 Reports saved to:${NC}"
echo "   $OUTPUT_DIR"
echo ""

if [ -f "$OUTPUT_DIR/audit_report.md" ]; then
    echo -e "${BLUE}📄 Summary:${NC}"
    echo "   ─────────────────────────────────────────────────────────"
    head -25 "$OUTPUT_DIR/audit_report.md"
    echo "   ─────────────────────────────────────────────────────────"
    echo ""
fi

if [ -f "$OUTPUT_DIR/fix_script.sh" ]; then
    echo -e "${YELLOW}🔧 Fix script generated:${NC}"
    echo "   $OUTPUT_DIR/fix_script.sh"
    echo ""
    echo -e "${BLUE}   To apply fixes, run:${NC}"
    echo "   bash $OUTPUT_DIR/fix_script.sh"
    echo ""
fi

# Show errors in red
if [ -f "$OUTPUT_DIR/audit_report.json" ]; then
    ERROR_COUNT=$(python3 -c "
import json
with open('$OUTPUT_DIR/audit_report.json') as f:
    d = json.load(f)
    errors = [i for i in d.get('issues', []) if i.get('severity') == 'error']
    print(len(errors))
" 2>/dev/null || echo "0")

    if [ "$ERROR_COUNT" != "0" ]; then
        echo -e "${RED}⚠️  $ERROR_COUNT errors found. Details:${NC}"
        python3 -c "
import json
with open('$OUTPUT_DIR/audit_report.json') as f:
    d = json.load(f)
    for i in d.get('issues', []):
        if i.get('severity') == 'error':
            print(f\"   ❌ {i['file_path']}:{i['line']} [{i['tool']}] {i['message'][:80]}\")
" 2>/dev/null || true
        echo ""
    fi
fi

echo -e "${GREEN}═══════════════════════════════════════════════════════════════${NC}"
echo ""
