#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEMO_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
SCENARIO="${1:-}"
REQUEST_ID="${REQUEST_ID:-demo-0042}"
CLUSTER_NAME="${PPT_DEMO_CLUSTER:-ppt-demo}"
CONTEXT="kind-${CLUSTER_NAME}"
NAMESPACE="ppt-demo"
COLOR_MODE="${EVIDENCE_COLOR:-auto}"

if [[ -z "$SCENARIO" ]]; then
  CONTROL_JSON="$(
    kubectl --context "$CONTEXT" -n "$NAMESPACE" exec deployment/telemetry-replay -- \
      python3 -c "import urllib.request; print(urllib.request.urlopen('http://127.0.0.1:9108/control', timeout=5).read().decode())"
  )"
  SCENARIO="$(
    python3 -c 'import json,sys; print(json.loads(sys.argv[1])["scenario"])' "$CONTROL_JSON"
  )"
fi

python3 "$DEMO_DIR/app/evidence_report.py" "$SCENARIO" \
  --request-id "$REQUEST_ID" --color "$COLOR_MODE"
