#!/usr/bin/env python3
"""Continuously send small OpenAI-compatible requests to the demo engine."""

from __future__ import annotations

import json
import os
import random
import threading
import time
import urllib.error
import urllib.request
from collections import defaultdict
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer


URL = os.environ.get("TARGET_URL", "http://inference-sim:8000/v1/chat/completions")
MODEL = os.environ.get("MODEL", "demo-model")
INTERVAL = float(os.environ.get("INTERVAL_SECONDS", "0.25"))
POD = os.environ.get("POD_NAME", "loadgen")
METRICS_PORT = int(os.environ.get("METRICS_PORT", "9109"))
COUNTERS: dict[tuple[str, str, str], int] = defaultdict(
    int,
    {
        ("200", "2xx", "success"): 0,
        ("400", "4xx", "http_400"): 0,
        ("429", "4xx", "http_429"): 0,
        ("500", "5xx", "http_500"): 0,
        ("503", "5xx", "http_503"): 0,
        ("transport_error", "transport", "transport_error"): 0,
    },
)
COUNTER_LOCK = threading.Lock()

REQUEST_PROFILES = (
    (
        "short",
        "Why can TTFT increase while route latency stays flat?",
        8,
    ),
    (
        "medium",
        "Explain how Gateway, EPP, Prefill, Decode, and KV-cache evidence should change the next incident owner.",
        16,
    ),
    (
        "long",
        "Compare request admission, prefix-cache reuse, queue pressure, and first-token latency. "
        "Then summarize which metrics distinguish a Gateway failure from an EPP scheduling problem or a vLLM capacity issue.",
        32,
    ),
)


class MetricsHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:  # noqa: N802
        if self.path == "/healthz":
            body = b'{"status":"ok"}'
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
        elif self.path == "/metrics":
            with COUNTER_LOCK:
                snapshot = dict(COUNTERS)
            lines = [
                "# HELP ppt_demo_client_requests_total Requests observed by the demo load generator.",
                "# TYPE ppt_demo_client_requests_total counter",
            ]
            for (http_status_code, status_class, status), value in sorted(snapshot.items()):
                lines.append(
                    f'ppt_demo_client_requests_total{{model="{MODEL}",http_status_code="{http_status_code}",'
                    f'status_class="{status_class}",status="{status}",signal_source="measured"}} {value}'
                )
            body = ("\n".join(lines) + "\n").encode()
            self.send_response(200)
            self.send_header("Content-Type", "text/plain; version=0.0.4")
        else:
            body = b'{"error":"not found"}'
            self.send_response(404)
            self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, _format: str, *_args: object) -> None:
        return


def count(http_status_code: int | str) -> None:
    if isinstance(http_status_code, int):
        status_code = str(http_status_code)
        status_class = f"{http_status_code // 100}xx"
        status = "success" if 200 <= http_status_code < 400 else f"http_{http_status_code}"
    else:
        status_code = http_status_code
        status_class = "transport"
        status = http_status_code
    with COUNTER_LOCK:
        COUNTERS[(status_code, status_class, status)] += 1


def send_request(sequence: int) -> None:
    profile, prompt, max_tokens = random.choice(REQUEST_PROFILES)
    payload = json.dumps(
        {
            "model": MODEL,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": max_tokens,
            "temperature": 0,
            "stream": False,
        }
    ).encode("utf-8")
    request = urllib.request.Request(
        URL,
        data=payload,
        headers={
            "Content-Type": "application/json",
            "X-Request-ID": f"ppt-demo-{POD}-{sequence}",
            "X-Demo-Traffic-Profile": profile,
        },
        method="POST",
    )
    started = time.monotonic()
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            response.read()
            http_status = response.status
        count(http_status)
        elapsed = time.monotonic() - started
        print(
            json.dumps(
                {
                    "sequence": sequence,
                    "status": "ok",
                    "http_status": http_status,
                    "profile": profile,
                    "max_tokens": max_tokens,
                    "elapsed_s": round(elapsed, 3),
                }
            ),
            flush=True,
        )
    except urllib.error.HTTPError as exc:
        count(exc.code)
        print(
            json.dumps(
                {"sequence": sequence, "status": "error", "http_status": exc.code, "profile": profile}
            ),
            flush=True,
        )
    except (urllib.error.URLError, TimeoutError) as exc:
        count("transport_error")
        print(json.dumps({"sequence": sequence, "status": "error", "error": str(exc)}), flush=True)


def main() -> None:
    threading.Thread(
        target=ThreadingHTTPServer(("0.0.0.0", METRICS_PORT), MetricsHandler).serve_forever,
        daemon=True,
    ).start()
    sequence = 0
    while True:
        sequence += 1
        send_request(sequence)
        time.sleep(INTERVAL)


if __name__ == "__main__":
    main()
