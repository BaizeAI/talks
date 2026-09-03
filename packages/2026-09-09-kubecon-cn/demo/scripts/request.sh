#!/usr/bin/env bash
set -euo pipefail

REQUEST_ID="${REQUEST_ID:-demo-0042}"

curl --silent --show-error --no-buffer --fail-with-body http://127.0.0.1:8000/v1/chat/completions \
  -H 'Content-Type: application/json' \
  -H "X-Request-ID: $REQUEST_ID" \
  -d '{
    "model": "demo-model",
    "messages": [{"role": "user", "content": "Why can TTFT lie in a PD-disaggregated system?"}],
    "max_tokens": 32,
    "temperature": 0,
    "stream": true
  }' \
  --write-out "\nrequest_id=$REQUEST_ID time_to_first_byte=%{time_starttransfer}s total=%{time_total}s\n"
