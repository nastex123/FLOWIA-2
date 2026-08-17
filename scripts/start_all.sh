#!/usr/bin/env bash
# FlowMind AI — Unified Startup Script (scripts/)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec "$SCRIPT_DIR/../start.sh" "$@"
