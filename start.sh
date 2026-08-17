#!/usr/bin/env bash
# FlowMind AI — Linux / macOS Unified Startup Script
set -e

# Change to repo root directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "=========================================================="
echo "   🧠 Starting FlowMind AI (Backend + Frontend)"
echo "   Platform: Linux / macOS"
echo "   Backend:  http://127.0.0.1:8000"
echo "   Frontend: http://localhost:3000"
echo "=========================================================="

# Check if python3 is available
if command -v python3 &>/dev/null; then
    PYTHON_BIN="python3"
elif command -v python &>/dev/null; then
    PYTHON_BIN="python"
else
    echo "[ERROR] Python 3 was not found on your system PATH."
    exit 1
fi

# Run the cross-platform launcher
exec $PYTHON_BIN start.py "$@"
