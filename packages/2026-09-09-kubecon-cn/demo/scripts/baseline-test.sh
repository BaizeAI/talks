#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEMO_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
WAIT_SECONDS="${BASELINE_WAIT_SECONDS:-35}"

if ! [[ "$WAIT_SECONDS" =~ ^[0-9]+$ ]] || (( WAIT_SECONDS < 4 || WAIT_SECONDS > 120 )); then
  echo "BASELINE_WAIT_SECONDS must be an integer between 4 and 120" >&2
  exit 2
fi

if ! curl --silent --fail http://127.0.0.1:9090/-/ready >/dev/null; then
  echo "Prometheus is not ready at http://127.0.0.1:9090" >&2
  echo "Start the environment first: make up" >&2
  exit 1
fi

echo "Resetting the demo to baseline..."
"$SCRIPT_DIR/scenario.sh" baseline
echo "Waiting ${WAIT_SECONDS}s for the 20-second Prometheus windows..."
sleep "$WAIT_SECONDS"
python3 "$DEMO_DIR/app/check_baseline.py"
