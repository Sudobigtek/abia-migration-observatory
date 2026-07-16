#!/bin/bash
# =============================================================================
# Codebase Doctor — Docker Wrapper for Abia Migration Observatory
# =============================================================================
# This script runs the Codebase Doctor audit tool inside your Docker container,
# then copies the reports back to your WSL host.
#
# Usage:
#   chmod +x audit.sh
#   ./audit.sh [--fix] [--ai]
# =============================================================================

set -euo pipefail

# --- Configuration ---
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
AUDIT_SCRIPT="${SCRIPT_DIR}/codebase_doctor.py"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
HOST_OUTPUT_DIR="${SCRIPT_DIR}/audit_output_${TIMESTAMP}"

# --- Detect Container ---
# Try to find a running container with Django (looks for manage.py)
echo "🔍 Detecting Django container..."

CONTAINER=$(docker ps --format "{{.Names}}" | while read -r name; do
    if docker exec "$name" test -f /app/manage.py 2>/dev/null; then
        echo "$name"
        break
    fi
done)

if [ -z "$CONTAINER" ]; then
    # Fallback: try common naming patterns
    CONTAINER=$(docker ps --format "{{.Names}}" | grep -iE "(django|app|web|api)" | head -1 || true)
fi

if [ -z "$CONTAINER" ]; then
    echo "❌ Error: No running Django container found."
    echo "   Start your Docker stack first: docker-compose up -d"
    exit 1
fi

echo "✅ Found container: $CONTAINER"

# --- Parse Arguments ---
FIX_FLAG=""
AI_FLAG=""
MODEL_FLAG=""

while [[ $# -gt 0 ]]; do
    case "$1" in
        --fix)
            FIX_FLAG="--fix"
            shift
            ;;
        --ai)
            AI_FLAG="--ai"
            shift
            ;;
        --model)
            MODEL_FLAG="--model $2"
            shift 2
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

# --- Install Dependencies in Container ---
echo "📦 Installing audit dependencies in container..."
docker exec "$CONTAINER" bash -c "
    pip install --quiet rich bandit flake8 mypy pytest pytest-json-report 2>/dev/null || true
" || echo "⚠️  Some dependencies may already be installed"

# --- Copy Audit Script into Container ---
echo "📋 Copying audit script into container..."
docker cp "$AUDIT_SCRIPT" "$CONTAINER:/tmp/codebase_doctor.py"

# --- Run Audit ---
echo "🚀 Running Codebase Doctor..."
docker exec -it "$CONTAINER" python /tmp/codebase_doctor.py \
    --path /app \
    --docker \
    --container "$CONTAINER" \
    --output /app/audit_output \
    $FIX_FLAG \
    $AI_FLAG \
    $MODEL_FLAG

# --- Copy Reports Back to Host ---
echo "📥 Copying reports back to WSL..."
mkdir -p "$HOST_OUTPUT_DIR"
docker cp "$CONTAINER:/app/audit_output/." "$HOST_OUTPUT_DIR/" 2>/dev/null || true

# --- Display Results ---
echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "  ✅ Audit Complete!"
echo "═══════════════════════════════════════════════════════════════"
echo ""
echo "📁 Reports saved to:"
echo "   $HOST_OUTPUT_DIR"
echo ""

if [ -f "$HOST_OUTPUT_DIR/audit_report.md" ]; then
    echo "📄 Quick Summary:"
    echo "   ─────────────────────────────────────────────────────────"
    head -20 "$HOST_OUTPUT_DIR/audit_report.md"
    echo "   ─────────────────────────────────────────────────────────"
    echo "   (See full report in $HOST_OUTPUT_DIR/audit_report.md)"
fi

if [ -f "$HOST_OUTPUT_DIR/fix_script.sh" ]; then
    echo ""
    echo "🔧 Auto-fix script available:"
    echo "   $HOST_OUTPUT_DIR/fix_script.sh"
    echo "   Run with: bash $HOST_OUTPUT_DIR/fix_script.sh"
fi

echo ""
echo "═══════════════════════════════════════════════════════════════"
