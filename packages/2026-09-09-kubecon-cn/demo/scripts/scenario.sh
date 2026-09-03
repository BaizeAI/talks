#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEMO_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
SCENARIO="${1:-}"
CLUSTER_NAME="${PPT_DEMO_CLUSTER:-ppt-demo}"
CONTEXT="kind-${CLUSTER_NAME}"
NAMESPACE="ppt-demo"
COLOR_MODE="${SCENARIO_COLOR:-auto}"

case "$SCENARIO" in
  baseline)
    LOADGEN_REPLICAS=1
    ENGINE_CONFIG='{"time-to-first-token":"200ms","inter-token-latency":"15ms","failure-injection-rate":0}'
    RESET_QUERY='&reset=1'
    ;;
  load)
    LOADGEN_REPLICAS=8
    ENGINE_CONFIG='{"time-to-first-token":"700ms","inter-token-latency":"25ms","failure-injection-rate":0}'
    RESET_QUERY=''
    ;;
  prefill_pressure)
    # Primary talk profile.  The load level is intentionally identical to
    # pd_tuned so the validation cannot be explained by reducing demand.
    LOADGEN_REPLICAS=8
    ENGINE_CONFIG='{"time-to-first-token":"1600ms","inter-token-latency":"25ms","failure-injection-rate":0}'
    RESET_QUERY=''
    ;;
  pd_tuned)
    # CPU simulator response profile for a controlled P:D-ratio benchmark.
    # The P/D allocation itself is replayed; this is not a real replica change.
    LOADGEN_REPLICAS=8
    ENGINE_CONFIG='{"time-to-first-token":"300ms","inter-token-latency":"25ms","failure-injection-rate":0}'
    RESET_QUERY=''
    ;;
  gateway_error)
    LOADGEN_REPLICAS=6
    ENGINE_CONFIG='{"time-to-first-token":"250ms","inter-token-latency":"20ms","failure-injection-rate":0}'
    RESET_QUERY=''
    ;;
  vllm_error)
    LOADGEN_REPLICAS=6
    ENGINE_CONFIG='{"time-to-first-token":"1200ms","inter-token-latency":"50ms","failure-injection-rate":100,"failure-types":["server_error"]}'
    RESET_QUERY=''
    ;;
  gpu_error)
    LOADGEN_REPLICAS=6
    ENGINE_CONFIG='{"time-to-first-token":"1800ms","inter-token-latency":"60ms","failure-injection-rate":0}'
    RESET_QUERY=''
    ;;
  incident)
    # Primary fault story.  P:D remains at the default replayed 3P x 2D;
    # only demand, measured simulator latency, and KV-cache evidence change.
    LOADGEN_REPLICAS=6
    ENGINE_CONFIG='{"time-to-first-token":"2500ms","inter-token-latency":"80ms","failure-injection-rate":0}'
    RESET_QUERY=''
    ;;
  recovery)
    # Recovery keeps the incident demand so the improvement is attributable
    # to clearing the fault, not to reducing traffic.
    LOADGEN_REPLICAS=6
    ENGINE_CONFIG='{"time-to-first-token":"350ms","inter-token-latency":"20ms","failure-injection-rate":0}'
    RESET_QUERY=''
    ;;
  *)
    echo "usage: $0 baseline|load|prefill_pressure|pd_tuned|gateway_error|vllm_error|gpu_error|incident|recovery" >&2
    exit 2
    ;;
esac

# Always clear a previous Gateway injection before changing the simulator.
# This keeps host:8000/admin/config usable through gateway-demo -> epp-demo ->
# inference-sim.  gateway_error is enabled only after that control request
# succeeds, so its user traffic receives a real HTTP 503 from Gateway.
curl --silent --show-error --fail-with-body \
  -X POST http://127.0.0.1:8000/admin/proxy-config \
  -H 'Content-Type: application/json' \
  -d '{"failure-status":null,"delay-ms":0}' >/dev/null

curl --silent --show-error --fail-with-body \
  -X POST http://127.0.0.1:8000/admin/config \
  -H 'Content-Type: application/json' \
  -d "$ENGINE_CONFIG" >/dev/null

if [[ "$SCENARIO" == "gateway_error" ]]; then
  curl --silent --show-error --fail-with-body \
    -X POST http://127.0.0.1:8000/admin/proxy-config \
    -H 'Content-Type: application/json' \
    -d '{"failure-status":503,"delay-ms":0}' >/dev/null
else
  # Make the desired non-Gateway state explicit even if the script is
  # interrupted between the reset and the simulator update above.
  curl --silent --show-error --fail-with-body \
    -X POST http://127.0.0.1:8000/admin/proxy-config \
    -H 'Content-Type: application/json' \
    -d '{"failure-status":null,"delay-ms":0}' >/dev/null
fi

kubectl --context "$CONTEXT" -n "$NAMESPACE" exec deployment/telemetry-replay -- \
  python3 -c "import urllib.request; print(urllib.request.urlopen('http://127.0.0.1:9108/control?scenario=$SCENARIO$RESET_QUERY').read().decode())"
kubectl --context "$CONTEXT" -n "$NAMESPACE" scale deployment/loadgen --replicas="$LOADGEN_REPLICAS"
kubectl --context "$CONTEXT" -n "$NAMESPACE" rollout status deployment/loadgen --timeout=120s

python3 "$DEMO_DIR/app/scenario_banner.py" "$SCENARIO" --color "$COLOR_MODE"

echo "scenario=$SCENARIO loadgen_replicas=$LOADGEN_REPLICAS"
if [[ "$SCENARIO" == "pd_tuned" ]]; then
  echo "action=controlled P:D profile 2P:4D -> 3P:3D (allocation replayed; request latency measured)"
fi
if [[ "$SCENARIO" == "incident" || "$SCENARIO" == "recovery" ]]; then
  echo "topology=fixed 3P:2D controlled replay (no P:D scaling in the primary story)"
fi
echo "Grafana: http://127.0.0.1:3000/d/inferx-model-ops-ppt-demo"
echo "Allow about 20 seconds for the measured TTFT p95 window to move."
