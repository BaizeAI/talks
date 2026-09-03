#!/usr/bin/env bash
set -euo pipefail

DASHBOARD_URL="${PPT_DEMO_DASHBOARD_URL:-http://127.0.0.1:3000/d/inferx-model-ops-ppt-demo?orgId=1&refresh=5s}"

echo "Grafana: $DASHBOARD_URL"
case "$(uname -s)" in
  Darwin)
    open "$DASHBOARD_URL"
    ;;
  Linux)
    if command -v xdg-open >/dev/null 2>&1; then
      xdg-open "$DASHBOARD_URL"
    else
      echo "xdg-open is unavailable; copy the URL above into a browser."
    fi
    ;;
  *)
    echo "Copy the URL above into a browser."
    ;;
esac
