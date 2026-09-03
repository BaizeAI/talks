#!/usr/bin/env bash
set -euo pipefail

CLUSTER_NAME="${PPT_DEMO_CLUSTER:-ppt-demo}"
CONTEXT="kind-${CLUSTER_NAME}"

if [[ "${1:-}" == "--cluster" ]]; then
  kind delete cluster --name "$CLUSTER_NAME"
  exit 0
fi

kubectl --context "$CONTEXT" delete namespace ppt-demo --ignore-not-found
echo "Namespace removed. Keep the kind cluster, or run: $0 --cluster"

