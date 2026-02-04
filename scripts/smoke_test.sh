#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
BASE="${BASE_URL:-http://localhost:8000}"
curl -sf "$BASE/health" || exit 1
echo "Smoke OK"
