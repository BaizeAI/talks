#!/usr/bin/env python3
"""Small, dependency-free HTTP proxy for the local traffic path.

The demo deliberately keeps the proxy metrics under the ``ppt_demo_*``
namespace.  They are measured observations of this proxy, not Istio,
kgateway, EPP, or GPU telemetry.
"""

from __future__ import annotations

import argparse
import json
import math
import threading
import time
import urllib.error
import urllib.request
from collections import defaultdict
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any
from urllib.parse import urlsplit


MODEL_DEFAULT = "unknown"
METRIC_ROLE_LABELS = ("gateway", "epp")
HISTOGRAM_BUCKETS = (
    0.005,
    0.01,
    0.025,
    0.05,
    0.1,
    0.25,
    0.5,
    1.0,
    2.5,
    5.0,
    10.0,
    30.0,
)
HOP_BY_HOP_HEADERS = {
    "connection",
    "keep-alive",
    "proxy-authenticate",
    "proxy-authorization",
    "te",
    "trailer",
    "transfer-encoding",
    "upgrade",
}


def _escape_label(value: str) -> str:
    """Escape a Prometheus label value."""

    return value.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")


def _safe_label(value: Any, default: str = MODEL_DEFAULT) -> str:
    if not isinstance(value, str) or not value:
        return default
    # Model and endpoint are bounded, low-cardinality demo labels.  Do not
    # allow an arbitrary request body to create an unbounded label value.
    return value[:128]


def _status_class(status_code: int) -> str:
    if 100 <= status_code <= 599:
        return f"{status_code // 100}xx"
    return "unknown"


def _json_body(body: bytes) -> dict[str, Any]:
    if not body:
        return {}
    try:
        value = json.loads(body.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return {}
    return value if isinstance(value, dict) else {}


class ProxyState:
    """Thread-safe configuration and Prometheus counters for one proxy."""

    def __init__(self, role: str, upstream: str) -> None:
        self.role = role
        self.upstream = upstream.rstrip("/")
        self._lock = threading.Lock()
        self._failure_status: int | None = None
        self._delay_seconds = 0.0
        self._inflight: dict[str, int] = defaultdict(int)
        self._requests: dict[tuple[str, str, str, str], int] = defaultdict(int)
        self._durations: dict[str, dict[str, Any]] = {}
        self._endpoint_selections: dict[tuple[str, str], int] = defaultdict(int)

    def proxy_config(self) -> dict[str, Any]:
        with self._lock:
            return {
                "role": self.role,
                "failure-status": self._failure_status,
                "delay-ms": round(self._delay_seconds * 1000, 3),
            }

    def configure(self, failure_status: int | None, delay_ms: float) -> None:
        with self._lock:
            self._failure_status = failure_status
            self._delay_seconds = delay_ms / 1000.0

    def request_config(self) -> tuple[int | None, float]:
        with self._lock:
            return self._failure_status, self._delay_seconds

    def begin(self, model: str) -> None:
        with self._lock:
            self._inflight[model] += 1

    def end(self, model: str) -> None:
        with self._lock:
            self._inflight[model] = max(0, self._inflight[model] - 1)

    def observe_request(self, model: str, status_code: int, duration_seconds: float) -> None:
        status_code_label = str(status_code)
        status_class = _status_class(status_code)
        key = (model, status_code_label, status_class, self.role)
        with self._lock:
            self._requests[key] += 1
            histogram = self._durations.setdefault(
                model,
                {
                    "count": 0,
                    "sum": 0.0,
                    "buckets": [0] * len(HISTOGRAM_BUCKETS),
                },
            )
            histogram["count"] += 1
            histogram["sum"] += duration_seconds
            for index, bucket in enumerate(HISTOGRAM_BUCKETS):
                if duration_seconds <= bucket:
                    histogram["buckets"][index] += 1

    def select_endpoint(self, model: str) -> None:
        if self.role != "epp":
            return
        endpoint = _safe_label(urlsplit(self.upstream).hostname, "upstream")
        with self._lock:
            self._endpoint_selections[(model, endpoint)] += 1

    def render_metrics(self) -> str:
        with self._lock:
            requests = dict(self._requests)
            inflight = dict(self._inflight)
            durations = {
                model: {
                    "count": int(values["count"]),
                    "sum": float(values["sum"]),
                    "buckets": list(values["buckets"]),
                }
                for model, values in self._durations.items()
            }
            selections = dict(self._endpoint_selections)

        lines = [
            "# HELP ppt_demo_proxy_requests_total Requests observed by a demo traffic proxy.",
            "# TYPE ppt_demo_proxy_requests_total counter",
        ]
        for (model, response_code, status_class, role), value in sorted(requests.items()):
            lines.append(
                "ppt_demo_proxy_requests_total{"
                f'role="{_escape_label(role)}",model="{_escape_label(model)}",'
                f'response_code="{_escape_label(response_code)}",status_class="{_escape_label(status_class)}",'
                f'signal_source="measured"}} {value}'
            )

        lines.extend(
            [
                "# HELP ppt_demo_proxy_request_duration_seconds Request duration observed by a demo traffic proxy.",
                "# TYPE ppt_demo_proxy_request_duration_seconds histogram",
            ]
        )
        for model, values in sorted(durations.items()):
            for bucket, value in zip(HISTOGRAM_BUCKETS, values["buckets"]):
                lines.append(
                    "ppt_demo_proxy_request_duration_seconds_bucket{"
                    f'role="{_escape_label(self.role)}",model="{_escape_label(model)}",le="{bucket}"}} {value}'
                )
            lines.append(
                "ppt_demo_proxy_request_duration_seconds_bucket{"
                f'role="{_escape_label(self.role)}",model="{_escape_label(model)}",le="+Inf"}} {values["count"]}'
            )
            lines.append(
                "ppt_demo_proxy_request_duration_seconds_sum{"
                f'role="{_escape_label(self.role)}",model="{_escape_label(model)}"}} {values["sum"]:.9f}'
            )
            lines.append(
                "ppt_demo_proxy_request_duration_seconds_count{"
                f'role="{_escape_label(self.role)}",model="{_escape_label(model)}"}} {values["count"]}'
            )

        lines.extend(
            [
                "# HELP ppt_demo_proxy_inflight_requests Requests currently being handled by a demo traffic proxy.",
                "# TYPE ppt_demo_proxy_inflight_requests gauge",
            ]
        )
        models = set(inflight)
        models.update(durations)
        for model in sorted(models):
            lines.append(
                "ppt_demo_proxy_inflight_requests{"
                f'role="{_escape_label(self.role)}",model="{_escape_label(model)}"}} {inflight.get(model, 0)}'
            )

        if self.role == "epp":
            lines.extend(
                [
                    "# HELP ppt_demo_epp_endpoint_selections_total Endpoint selections made by the demo EPP proxy.",
                    "# TYPE ppt_demo_epp_endpoint_selections_total counter",
                ]
            )
            for (model, endpoint), value in sorted(selections.items()):
                lines.append(
                    "ppt_demo_epp_endpoint_selections_total{"
                    f'model="{_escape_label(model)}",endpoint="{_escape_label(endpoint)}",'
                    f'signal_source="measured"}} {value}'
                )
        return "\n".join(lines) + "\n"


class ProxyHTTPServer(ThreadingHTTPServer):
    daemon_threads = True
    allow_reuse_address = True

    def __init__(self, address: tuple[str, int], handler: type[BaseHTTPRequestHandler], state: ProxyState, metrics_only: bool) -> None:
        self.state = state
        self.metrics_only = metrics_only
        super().__init__(address, handler)


class ProxyHandler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def do_GET(self) -> None:  # noqa: N802
        self._dispatch()

    def do_POST(self) -> None:  # noqa: N802
        self._dispatch()

    def do_PUT(self) -> None:  # noqa: N802
        self._dispatch()

    def do_PATCH(self) -> None:  # noqa: N802
        self._dispatch()

    def do_DELETE(self) -> None:  # noqa: N802
        self._dispatch()

    def _dispatch(self) -> None:
        state = self.server.state  # type: ignore[attr-defined]
        if self.path == "/metrics":
            self._send(200, state.render_metrics().encode(), "text/plain; version=0.0.4")
            return
        if self.path == "/healthz":
            self._send(200, b'{"status":"ok"}', "application/json")
            return
        if getattr(self.server, "metrics_only", False):  # type: ignore[attr-defined]
            self._send_json(404, {"error": "metrics endpoint only"})
            return
        if self.path == "/admin/proxy-config":
            self._handle_proxy_config(state)
            return

        body = self._read_body()
        model = _safe_label(_json_body(body).get("model"))
        # Admin/config must pass through the chain so that host:8000 remains a
        # useful simulator control path, but it is not user traffic and does
        # not enter the request metrics.
        observe = not self.path.startswith("/admin/")
        if observe:
            state.begin(model)
        started = time.monotonic()
        status_code = 502
        response_body = b""
        response_headers: list[tuple[str, str]] = []
        try:
            failure_status, delay_seconds = state.request_config()
            if delay_seconds > 0:
                time.sleep(delay_seconds)
            if failure_status is not None:
                status_code = failure_status
                response_body = json.dumps(
                    {
                        "error": f"ppt_demo_{state.role}_injected_failure",
                        "status": status_code,
                    }
                ).encode()
                response_headers = [("Content-Type", "application/json")]
            else:
                if observe:
                    state.select_endpoint(model)
                status_code, response_headers, response_body = self._forward(state, body)
        finally:
            duration_seconds = time.monotonic() - started
            if observe:
                state.observe_request(model, status_code, duration_seconds)
                state.end(model)
        self._send(status_code, response_body, self._content_type(response_headers), response_headers)

    def _handle_proxy_config(self, state: ProxyState) -> None:
        if self.command != "POST":
            self._send_json(405, {"error": "POST required"})
            return
        values = _json_body(self._read_body())
        try:
            failure_status = self._parse_failure_status(values.get("failure-status"))
            delay_ms = self._parse_delay_ms(values.get("delay-ms", 0))
        except ValueError as exc:
            self._send_json(400, {"error": str(exc)})
            return
        state.configure(failure_status, delay_ms)
        self._send_json(200, state.proxy_config())

    @staticmethod
    def _parse_failure_status(value: Any) -> int | None:
        if value is None or value == "" or value is False:
            return None
        if isinstance(value, bool):
            raise ValueError("failure-status must be an integer or null")
        try:
            status = int(value)
        except (TypeError, ValueError) as exc:
            raise ValueError("failure-status must be an integer or null") from exc
        if status < 100 or status > 599:
            raise ValueError("failure-status must be between 100 and 599")
        return status

    @staticmethod
    def _parse_delay_ms(value: Any) -> float:
        if isinstance(value, bool):
            raise ValueError("delay-ms must be a non-negative number")
        try:
            delay_ms = float(value)
        except (TypeError, ValueError) as exc:
            raise ValueError("delay-ms must be a non-negative number") from exc
        if not math.isfinite(delay_ms) or delay_ms < 0 or delay_ms > 120_000:
            raise ValueError("delay-ms must be between 0 and 120000")
        return delay_ms

    def _forward(self, state: ProxyState, body: bytes) -> tuple[int, list[tuple[str, str]], bytes]:
        target = f"{state.upstream}{self.path}"
        headers: dict[str, str] = {}
        for name in ("Accept", "Authorization", "Content-Type", "User-Agent", "X-Request-ID", "X-Demo-Traffic-Profile"):
            value = self.headers.get(name)
            if value:
                headers[name] = value
        request = urllib.request.Request(
            target,
            data=body if body else None,
            headers=headers,
            method=self.command,
        )
        try:
            with urllib.request.urlopen(request, timeout=120) as response:
                return response.status, list(response.headers.items()), response.read()
        except urllib.error.HTTPError as exc:
            return exc.code, list(exc.headers.items()), exc.read()
        except (TimeoutError, urllib.error.URLError):
            return 502, [("Content-Type", "application/json")], b'{"error":"ppt_demo_upstream_unavailable"}'

    @staticmethod
    def _content_type(headers: list[tuple[str, str]]) -> str:
        for name, value in headers:
            if name.lower() == "content-type":
                return value
        return "application/octet-stream"

    def _read_body(self) -> bytes:
        raw_length = self.headers.get("Content-Length", "0")
        try:
            length = max(0, min(int(raw_length), 10 * 1024 * 1024))
        except ValueError:
            length = 0
        return self.rfile.read(length) if length else b""

    def _send_json(self, status_code: int, value: dict[str, Any]) -> None:
        self._send(status_code, json.dumps(value).encode(), "application/json")

    def _send(
        self,
        status_code: int,
        body: bytes,
        content_type: str,
        headers: list[tuple[str, str]] | None = None,
    ) -> None:
        self.send_response(status_code)
        content_type_sent = False
        for name, value in headers or []:
            lower_name = name.lower()
            if lower_name in HOP_BY_HOP_HEADERS or lower_name == "content-length":
                continue
            if lower_name == "content-type":
                self.send_header("Content-Type", value)
                content_type_sent = True
                continue
            self.send_header(name, value)
        if not content_type_sent:
            self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Connection", "close")
        self.end_headers()
        if body:
            self.wfile.write(body)

    def log_message(self, _format: str, *_args: object) -> None:
        return


def main() -> None:
    parser = argparse.ArgumentParser(description="Measured HTTP proxy for the local PPT demo")
    parser.add_argument("--role", choices=METRIC_ROLE_LABELS, required=True)
    parser.add_argument("--upstream", required=True)
    parser.add_argument("--listen-host", default="0.0.0.0")
    parser.add_argument("--listen-port", type=int, default=8000)
    parser.add_argument("--metrics-port", type=int, default=9109)
    args = parser.parse_args()

    state = ProxyState(args.role, args.upstream)
    traffic_server = ProxyHTTPServer(
        (args.listen_host, args.listen_port),
        ProxyHandler,
        state,
        metrics_only=False,
    )
    metrics_server = ProxyHTTPServer(
        (args.listen_host, args.metrics_port),
        ProxyHandler,
        state,
        metrics_only=True,
    )
    threading.Thread(target=metrics_server.serve_forever, daemon=True).start()
    try:
        traffic_server.serve_forever()
    finally:
        traffic_server.server_close()
        metrics_server.shutdown()
        metrics_server.server_close()


if __name__ == "__main__":
    main()
