#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CLUSTER_NAME="${PPT_DEMO_CLUSTER:-ppt-demo}"
CONTEXT="kind-${CLUSTER_NAME}"
NAMESPACE="ppt-demo"
WAIT_SECONDS="${RESET_METRICS_WAIT_SECONDS:-25}"

if ! [[ "$WAIT_SECONDS" =~ ^[0-9]+$ ]] || (( WAIT_SECONDS > 120 )); then
  echo "RESET_METRICS_WAIT_SECONDS must be an integer between 0 and 120" >&2
  exit 2
fi

echo "Pausing load generation（暂停请求流量）..."
kubectl --context "$CONTEXT" -n "$NAMESPACE" scale deployment/loadgen --replicas=0
kubectl --context "$CONTEXT" -n "$NAMESPACE" rollout status deployment/loadgen --timeout=120s

echo "Clearing Prometheus history（清空 Prometheus 历史指标）..."
kubectl --context "$CONTEXT" -n "$NAMESPACE" rollout restart deployment/prometheus
kubectl --context "$CONTEXT" -n "$NAMESPACE" rollout status deployment/prometheus --timeout=120s

echo "Starting a fresh baseline（启动全新基线）..."
"$SCRIPT_DIR/scenario.sh" baseline

if (( WAIT_SECONDS > 0 )); then
  echo "Collecting ${WAIT_SECONDS}s of clean baseline metrics（采集全新基线数据）..."
  sleep "$WAIT_SECONDS"
fi

echo "Metrics reset complete（指标重置完成）."
echo "Grafana now contains only the new baseline window（Grafana 现在只显示新的基线窗口）."
