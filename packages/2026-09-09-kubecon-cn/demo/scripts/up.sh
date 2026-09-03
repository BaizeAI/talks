#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEMO_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
CLUSTER_NAME="${PPT_DEMO_CLUSTER:-ppt-demo}"
CONTEXT="kind-${CLUSTER_NAME}"
NAMESPACE="ppt-demo"
SOURCE_DASHBOARD="$DEMO_DIR/dashboard-template.json"

for command_name in docker kind kubectl python3 curl; do
  if ! command -v "$command_name" >/dev/null 2>&1; then
    echo "missing required command: $command_name" >&2
    exit 1
  fi
done

if ! kind get clusters 2>/dev/null | grep -Fxq "$CLUSTER_NAME"; then
  echo "Creating kind cluster: $CLUSTER_NAME"
  # kind forwards proxy variables into the node. A host-loopback proxy such as
  # 127.0.0.1:7890 is unreachable from inside the node container, so let Docker
  # Desktop handle its own configured proxy instead.
  env -u HTTP_PROXY -u HTTPS_PROXY -u ALL_PROXY \
    -u http_proxy -u https_proxy -u all_proxy \
    kind create cluster --name "$CLUSTER_NAME" --config "$DEMO_DIR/kind-config.yaml" --wait 120s
else
  echo "Reusing kind cluster: $CLUSTER_NAME"
fi

if docker inspect "${CLUSTER_NAME}-control-plane" --format '{{range .Config.Env}}{{println .}}{{end}}' 2>/dev/null | \
  grep -Eiq 'https?_proxy=https?://(127\.0\.0\.1|localhost)'; then
  echo "The kind node has a loopback HTTP proxy that cannot be reached from the container." >&2
  echo "Recreate this dedicated cluster with: $DEMO_DIR/scripts/down.sh --cluster && $0" >&2
  exit 1
fi

if ! kubectl config get-contexts -o name | grep -Fxq "$CONTEXT"; then
  echo "kubectl context not found: $CONTEXT" >&2
  exit 1
fi

TMP_BUILD_DIR="$(mktemp -d "${TMPDIR:-/tmp}/ppt-demo.XXXXXX")"
trap 'rm -rf "$TMP_BUILD_DIR"' EXIT
python3 "$DEMO_DIR/app/prepare_dashboard.py" "$SOURCE_DASHBOARD" "$TMP_BUILD_DIR/dashboard.json"

kubectl --context "$CONTEXT" apply -f "$DEMO_DIR/k8s/namespace.yaml"
kubectl --context "$CONTEXT" -n "$NAMESPACE" create configmap ppt-demo-app \
  --from-file=loadgen.py="$DEMO_DIR/app/loadgen.py" \
  --from-file=traffic_proxy.py="$DEMO_DIR/app/traffic_proxy.py" \
  --from-file=telemetry_replay.py="$DEMO_DIR/app/telemetry_replay.py" \
  --dry-run=client -o yaml | kubectl --context "$CONTEXT" apply -f -
kubectl --context "$CONTEXT" -n "$NAMESPACE" create configmap ppt-demo-dashboard \
  --from-file=dashboard.json="$TMP_BUILD_DIR/dashboard.json" \
  --dry-run=client -o yaml | kubectl --context "$CONTEXT" apply -f -
kubectl --context "$CONTEXT" apply -f "$DEMO_DIR/k8s/stack.yaml"

# ConfigMap volume updates do not restart the Python processes, and Grafana may
# keep the old provisioned UID until restart. Make every `make up` deterministic.
kubectl --context "$CONTEXT" -n "$NAMESPACE" rollout restart \
  deployment/gateway-demo deployment/epp-demo deployment/telemetry-replay \
  deployment/loadgen deployment/prometheus deployment/grafana

for deployment in inference-sim gateway-demo epp-demo telemetry-replay loadgen prometheus grafana; do
  kubectl --context "$CONTEXT" -n "$NAMESPACE" rollout status "deployment/$deployment" --timeout=300s
done

"$DEMO_DIR/scripts/scenario.sh" baseline

echo
echo "Demo is ready."
echo "  Grafana:    http://127.0.0.1:3000/d/inferx-model-ops-ppt-demo"
echo "  Prometheus: http://127.0.0.1:9090"
echo "  OpenAI API: http://127.0.0.1:8000/v1/chat/completions"
echo
echo "Baseline is active. Primary story: make incident -> make evidence -> make recovery -> make status"
