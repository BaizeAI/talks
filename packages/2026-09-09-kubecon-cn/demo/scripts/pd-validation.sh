#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEMO_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
CLUSTER_NAME="${PPT_DEMO_CLUSTER:-ppt-demo}"
CONTEXT="kind-${CLUSTER_NAME}"
NAMESPACE="ppt-demo"
WAIT_SECONDS="${PD_VALIDATION_WAIT_SECONDS:-28}"
VALIDATION_DIR="$(mktemp -d "${TMPDIR:-/tmp}/ppt-demo-validation.XXXXXX")"
trap 'rm -rf "$VALIDATION_DIR"' EXIT

if ! [[ "$WAIT_SECONDS" =~ ^[0-9]+$ ]] || (( WAIT_SECONDS < 20 || WAIT_SECONDS > 120 )); then
  echo "PD_VALIDATION_WAIT_SECONDS must be an integer between 20 and 120" >&2
  exit 2
fi

replicas() {
  kubectl --context "$CONTEXT" -n "$NAMESPACE" \
    get deployment/loadgen -o jsonpath='{.spec.replicas}'
}

echo "1/3 Reproduce Prefill pressure at constant demand..."
"$SCRIPT_DIR/scenario.sh" prefill_pressure
sleep "$WAIT_SECONDS"
python3 "$DEMO_DIR/app/check_pd_validation.py" snapshot \
  --output "$VALIDATION_DIR/before.json" \
  --loadgen-replicas "$(replicas)"

echo "2/3 Apply the controlled P:D benchmark profile without reducing demand..."
"$SCRIPT_DIR/scenario.sh" pd_tuned
sleep "$WAIT_SECONDS"
python3 "$DEMO_DIR/app/check_pd_validation.py" snapshot \
  --output "$VALIDATION_DIR/after.json" \
  --loadgen-replicas "$(replicas)"

echo "3/3 Compare user impact, first boundary, service guardrails, and negative controls..."
python3 "$DEMO_DIR/app/check_pd_validation.py" compare \
  "$VALIDATION_DIR/before.json" "$VALIDATION_DIR/after.json"

echo
echo "Data boundary: HTTP traffic and TTFT are measured through the simulator path."
echo "P:D allocation, stage service rates, KV, GPU, and network are controlled replay."
