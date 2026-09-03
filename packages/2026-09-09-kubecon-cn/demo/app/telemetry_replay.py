#!/usr/bin/env python3
"""Prometheus exporter for cross-layer signals unavailable on a GPU-less Mac."""

from __future__ import annotations

import argparse
import json
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse


MODEL = "demo-model"

SCENARIOS = {
    "baseline": {
        "gateway_healthy": 1,
        "ready_endpoints": 2,
        "ttft_p95": 0.35,
        "route_p95": 0.015,
        "epp_queue": 1,
        "prefill_waiting": 1,
        "decode_waiting": 1,
        "swapped": 0,
        "prefill_time": 0.12,
        "decode_time": 0.40,
        "itl_p95": 0.035,
        "kv_transfer_p99": 0.08,
        "kv_get_p99": 0.08,
        "kv_evictions_per_second": 0,
        "kv_remote_no_space_per_second": 0,
        "kv_bytes_per_second": 2_000_000_000,
        "kv_retries": 0,
        "kv_errors": 0,
        "kv_cache_usage": 0.42,
        "kv_cache_hit_ratio": 0.82,
        "gpu_utilization": 72,
        "gpu_memory_used": 0.68,
        "network_drops": 0,
        "gpu_xid_errors": 0,
        "error_rate": 0.002,
        "gateway_error_rate": 0,
        "vllm_error_rate": 0,
        "gpu_error_rate": 0,
        "gateway_errors_per_second": 0,
        "vllm_errors_per_second": 0,
        "gpu_errors_per_second": 0,
    },
    "load": {
        "gateway_healthy": 1,
        "ready_endpoints": 2,
        "ttft_p95": 1.20,
        "route_p95": 0.016,
        "epp_queue": 2,
        "prefill_waiting": 6,
        "decode_waiting": 1,
        "swapped": 0,
        "prefill_time": 0.65,
        "decode_time": 0.44,
        "itl_p95": 0.04,
        "kv_transfer_p99": 0.09,
        "kv_get_p99": 0.10,
        "kv_evictions_per_second": 0,
        "kv_remote_no_space_per_second": 0,
        "kv_bytes_per_second": 2_100_000_000,
        "kv_retries": 0,
        "kv_errors": 0,
        "kv_cache_usage": 0.58,
        "kv_cache_hit_ratio": 0.80,
        "gpu_utilization": 86,
        "gpu_memory_used": 0.76,
        "network_drops": 0,
        "gpu_xid_errors": 0,
        "error_rate": 0.002,
        "gateway_error_rate": 0,
        "vllm_error_rate": 0,
        "gpu_error_rate": 0,
        "gateway_errors_per_second": 0,
        "vllm_errors_per_second": 0,
        "gpu_errors_per_second": 0,
    },
    # Optional P:D sizing lab: demand is unchanged between this profile and
    # pd_tuned. The default incident story below keeps the topology fixed.
    "prefill_pressure": {
        "gateway_healthy": 1,
        "ready_endpoints": 2,
        "ttft_p95": 1.80,
        "route_p95": 0.016,
        "epp_queue": 2,
        "prefill_waiting": 14,
        "decode_waiting": 1,
        "swapped": 0,
        "prefill_time": 1.45,
        "decode_time": 0.44,
        "itl_p95": 0.04,
        "kv_transfer_p99": 0.09,
        "kv_get_p99": 0.10,
        "kv_evictions_per_second": 0,
        "kv_remote_no_space_per_second": 0,
        "kv_bytes_per_second": 2_100_000_000,
        "kv_retries": 0,
        "kv_errors": 0,
        "kv_cache_usage": 0.60,
        "kv_cache_hit_ratio": 0.80,
        "gpu_utilization": 68,
        "gpu_memory_used": 0.76,
        "network_drops": 0,
        "gpu_xid_errors": 0,
        "error_rate": 0.002,
        "gateway_error_rate": 0,
        "vllm_error_rate": 0,
        "gpu_error_rate": 0,
        "gateway_errors_per_second": 0,
        "vllm_errors_per_second": 0,
        "gpu_errors_per_second": 0,
        "prefill_replicas": 2,
        "decode_replicas": 4,
        "prefill_arrival_rate": 18,
        "prefill_service_rate": 10,
        "decode_service_rate": 22,
        "prefill_batch_fill_ratio": 0.42,
        "max_num_batched_tokens": 4096,
        "action": "observe_only",
        "production_mapping": "inspect_prefill_capacity",
    },
    "pd_tuned": {
        "gateway_healthy": 1,
        "ready_endpoints": 2,
        "ttft_p95": 0.55,
        "route_p95": 0.016,
        "epp_queue": 2,
        "prefill_waiting": 2,
        "decode_waiting": 1,
        "swapped": 0,
        "prefill_time": 0.38,
        "decode_time": 0.46,
        "itl_p95": 0.04,
        "kv_transfer_p99": 0.09,
        "kv_get_p99": 0.10,
        "kv_evictions_per_second": 0,
        "kv_remote_no_space_per_second": 0,
        "kv_bytes_per_second": 2_100_000_000,
        "kv_retries": 0,
        "kv_errors": 0,
        "kv_cache_usage": 0.60,
        "kv_cache_hit_ratio": 0.80,
        "gpu_utilization": 72,
        "gpu_memory_used": 0.76,
        "network_drops": 0,
        "gpu_xid_errors": 0,
        "error_rate": 0.002,
        "gateway_error_rate": 0,
        "vllm_error_rate": 0,
        "gpu_error_rate": 0,
        "gateway_errors_per_second": 0,
        "vllm_errors_per_second": 0,
        "gpu_errors_per_second": 0,
        "prefill_replicas": 3,
        "decode_replicas": 3,
        "prefill_arrival_rate": 18,
        "prefill_service_rate": 20,
        "decode_service_rate": 18,
        "prefill_batch_fill_ratio": 0.74,
        "max_num_batched_tokens": 4096,
        "action": "pd_ratio_2p4d_to_3p3d",
        "production_mapping": "benchmark_pd_ratio",
    },
    "gateway_error": {
        "gateway_healthy": 0,
        "ready_endpoints": 2,
        "ttft_p95": 0.60,
        "route_p95": 0.80,
        "epp_queue": 1,
        "prefill_waiting": 1,
        "decode_waiting": 1,
        "swapped": 0,
        "prefill_time": 0.14,
        "decode_time": 0.42,
        "itl_p95": 0.04,
        "kv_transfer_p99": 0.09,
        "kv_get_p99": 0.09,
        "kv_evictions_per_second": 0,
        "kv_remote_no_space_per_second": 0,
        "kv_bytes_per_second": 1_900_000_000,
        "kv_retries": 0,
        "kv_errors": 0,
        "kv_cache_usage": 0.50,
        "kv_cache_hit_ratio": 0.81,
        "gpu_utilization": 70,
        "gpu_memory_used": 0.70,
        "network_drops": 0,
        "gpu_xid_errors": 0,
        "error_rate": 0.35,
        "gateway_error_rate": 0.35,
        "vllm_error_rate": 0,
        "gpu_error_rate": 0,
        "gateway_errors_per_second": 5,
        "vllm_errors_per_second": 0,
        "gpu_errors_per_second": 0,
    },
    "vllm_error": {
        "gateway_healthy": 1,
        "ready_endpoints": 2,
        "ttft_p95": 2.20,
        "route_p95": 0.016,
        "epp_queue": 1,
        "prefill_waiting": 8,
        "decode_waiting": 3,
        "swapped": 2,
        "prefill_time": 1.40,
        "decode_time": 0.80,
        "itl_p95": 0.12,
        "kv_transfer_p99": 0.10,
        "kv_get_p99": 0.11,
        "kv_evictions_per_second": 0,
        "kv_remote_no_space_per_second": 0,
        "kv_bytes_per_second": 1_600_000_000,
        "kv_retries": 0,
        "kv_errors": 0,
        "kv_cache_usage": 0.62,
        "kv_cache_hit_ratio": 0.78,
        "gpu_utilization": 74,
        "gpu_memory_used": 0.78,
        "network_drops": 0,
        "gpu_xid_errors": 0,
        "error_rate": 1.0,
        "gateway_error_rate": 0,
        "vllm_error_rate": 1.0,
        "gpu_error_rate": 0,
        "gateway_errors_per_second": 0,
        "vllm_errors_per_second": 8,
        "gpu_errors_per_second": 0,
    },
    "gpu_error": {
        "gateway_healthy": 1,
        "ready_endpoints": 2,
        "ttft_p95": 3.20,
        "route_p95": 0.016,
        "epp_queue": 1,
        "prefill_waiting": 10,
        "decode_waiting": 5,
        "swapped": 4,
        "prefill_time": 1.80,
        "decode_time": 1.30,
        "itl_p95": 0.18,
        "kv_transfer_p99": 0.10,
        "kv_get_p99": 0.11,
        "kv_evictions_per_second": 0,
        "kv_remote_no_space_per_second": 0,
        "kv_bytes_per_second": 1_400_000_000,
        "kv_retries": 0,
        "kv_errors": 0,
        "kv_cache_usage": 0.66,
        "kv_cache_hit_ratio": 0.77,
        "gpu_utilization": 18,
        "gpu_memory_used": 0.95,
        "network_drops": 0,
        "gpu_xid_errors": 6,
        "error_rate": 0.08,
        "gateway_error_rate": 0,
        "vllm_error_rate": 0,
        "gpu_error_rate": 0.08,
        "gateway_errors_per_second": 0,
        "vllm_errors_per_second": 0,
        "gpu_errors_per_second": 3,
    },
    "incident": {
        "gateway_healthy": 1,
        "ready_endpoints": 2,
        "ttft_p95": 2.80,
        "route_p95": 0.016,
        "epp_queue": 1,
        "prefill_waiting": 14,
        "decode_waiting": 0,
        "swapped": 3,
        "prefill_time": 2.10,
        "decode_time": 0.42,
        "itl_p95": 0.04,
        "kv_transfer_p99": 0.10,
        "kv_get_p99": 2.40,
        "kv_evictions_per_second": 689,
        "kv_remote_no_space_per_second": 8,
        "kv_bytes_per_second": 820_000_000,
        "kv_retries": 0,
        "kv_errors": 0,
        "kv_cache_usage": 0.93,
        "kv_cache_hit_ratio": 0.42,
        "gpu_utilization": 68,
        "gpu_memory_used": 0.91,
        "network_drops": 0,
        "gpu_xid_errors": 0,
        "error_rate": 0.002,
        "gateway_error_rate": 0,
        "vllm_error_rate": 0,
        "gpu_error_rate": 0,
        "gateway_errors_per_second": 0,
        "vllm_errors_per_second": 0,
        "gpu_errors_per_second": 0,
    },
    "recovery": {
        "gateway_healthy": 1,
        "ready_endpoints": 2,
        "ttft_p95": 0.55,
        "route_p95": 0.016,
        "epp_queue": 1,
        "prefill_waiting": 1,
        "decode_waiting": 1,
        "swapped": 0,
        "prefill_time": 0.12,
        "decode_time": 0.52,
        "itl_p95": 0.05,
        "kv_transfer_p99": 0.10,
        "kv_get_p99": 0.10,
        "kv_evictions_per_second": 0,
        "kv_remote_no_space_per_second": 0,
        "kv_bytes_per_second": 1_900_000_000,
        "kv_retries": 0,
        "kv_errors": 0,
        "kv_cache_usage": 0.48,
        "kv_cache_hit_ratio": 0.79,
        "gpu_utilization": 73,
        "gpu_memory_used": 0.71,
        "network_drops": 0,
        "gpu_xid_errors": 0,
        "error_rate": 0.01,
        "gateway_error_rate": 0,
        "vllm_error_rate": 0,
        "gpu_error_rate": 0,
        "gateway_errors_per_second": 0,
        "vllm_errors_per_second": 0,
        "gpu_errors_per_second": 0,
    },
}


class DemoState:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._scenario = "baseline"
        self._last_update = time.monotonic()
        self._counters = {"gateway": 0.0, "vllm": 0.0, "gpu": 0.0}

    def _advance_locked(self) -> None:
        now = time.monotonic()
        elapsed = max(0.0, now - self._last_update)
        values = SCENARIOS[self._scenario]
        self._counters["gateway"] += elapsed * values.get("gateway_errors_per_second", 0)
        self._counters["vllm"] += elapsed * values.get("vllm_errors_per_second", 0)
        self._counters["gpu"] += elapsed * values.get("gpu_errors_per_second", 0)
        self._last_update = now

    def set(self, scenario: str, *, reset_counters: bool = False) -> None:
        if scenario not in SCENARIOS:
            raise ValueError(f"unknown scenario: {scenario}")
        with self._lock:
            self._advance_locked()
            self._scenario = scenario
            if reset_counters:
                self._counters = {"gateway": 0.0, "vllm": 0.0, "gpu": 0.0}

    def snapshot(self) -> tuple[str, dict[str, float | int], dict[str, float]]:
        with self._lock:
            self._advance_locked()
            return self._scenario, dict(SCENARIOS[self._scenario]), dict(self._counters)


def sample(name: str, value: float | int, *, metric_type: str = "gauge", **labels: str) -> str:
    label_text = ""
    if labels:
        label_text = "{" + ",".join(f'{key}="{item}"' for key, item in labels.items()) + "}"
    return f"# TYPE {name} {metric_type}\n{name}{label_text} {value}\n"


def render_metrics(state: DemoState) -> str:
    scenario, values, counters = state.snapshot()
    model = {"model": MODEL, "signal_source": "simulated"}
    # Older fault-lab profiles predate the focused PD story.  Defaults keep
    # them usable without pretending that they exercised a tuning action.
    # The default fault labs all run against one fixed PD-disaggregated
    # topology.  Fault diagnosis must not look like a P:D scaling demo.
    prefill_replicas = values.get("prefill_replicas", 3)
    decode_replicas = values.get("decode_replicas", 2)
    prefill_arrival_rate = values.get("prefill_arrival_rate", 8)
    prefill_service_rate = values.get("prefill_service_rate", 12)
    decode_service_rate = values.get("decode_service_rate", 18)
    prefill_batch_fill_ratio = values.get("prefill_batch_fill_ratio", 0.65)
    max_num_batched_tokens = values.get("max_num_batched_tokens", 4096)
    action = values.get("action", "none")
    production_mapping = values.get("production_mapping", "none")
    gateway_desired_replicas = 1
    gateway_healthy_replicas = int(values["gateway_healthy"] > 0)
    epp_desired_replicas = 1
    epp_healthy_replicas = int(values["ready_endpoints"] > 0)
    prefill_healthy_replicas = values.get("prefill_healthy_replicas", prefill_replicas)
    decode_healthy_replicas = values.get("decode_healthy_replicas", decode_replicas)
    pd_profile = f"{int(prefill_replicas)}P × {int(decode_replicas)}D"
    scenario_metrics = "# TYPE kubecon_demo_scenario_info gauge\n" + "".join(
        f'kubecon_demo_scenario_info{{scenario="{name}",signal_source="simulated"}} {int(name == scenario)}\n'
        for name in SCENARIOS
    )
    action_metric = (
        "# TYPE kubecon_demo_action_info gauge\n"
        f'kubecon_demo_action_info{{action="{action}",production_mapping="{production_mapping}",'
        f'signal_source="simulated"}} 1\n'
    )
    profile_metric = (
        "# TYPE kubecon_pd_profile_info gauge\n"
        f'kubecon_pd_profile_info{{profile="{pd_profile}",signal_source="simulated"}} 1\n'
    )
    return "".join(
        [
            scenario_metrics,
            action_metric,
            profile_metric,
            sample("kubecon_gateway_healthy", values["gateway_healthy"], signal_source="simulated"),
            sample("kubecon_gateway_desired_replicas", gateway_desired_replicas, signal_source="simulated"),
            sample("kubecon_gateway_healthy_replicas", gateway_healthy_replicas, signal_source="simulated"),
            sample("kubecon_epp_desired_replicas", epp_desired_replicas, signal_source="simulated"),
            sample("kubecon_epp_healthy_replicas", epp_healthy_replicas, signal_source="simulated"),
            sample(
                "inference_pool_ready_pods",
                values["ready_endpoints"],
                model_name=MODEL,
                signal_source="simulated",
            ),
            sample("kubecon_ttft_p95_seconds", values["ttft_p95"], **model),
            sample("kubecon_route_latency_p95_seconds", values["route_p95"], **model),
            sample("kubecon_epp_queue_depth", values["epp_queue"], **model),
            sample("inference_pool_average_queue_size", values["epp_queue"], model_name=MODEL, signal_source="simulated"),
            sample("kubecon_vllm_prefill_waiting", values["prefill_waiting"], **model),
            sample("kubecon_vllm_decode_waiting", values["decode_waiting"], **model),
            sample("kubecon_vllm_swapped_requests", values["swapped"], **model),
            sample("kubecon_vllm_prefill_time_seconds", values["prefill_time"], **model),
            sample("kubecon_vllm_decode_time_seconds", values["decode_time"], **model),
            sample("kubecon_vllm_itl_p95_seconds", values["itl_p95"], **model),
            sample("kubecon_pd_prefill_replicas", prefill_replicas, **model),
            sample("kubecon_pd_decode_replicas", decode_replicas, **model),
            sample("kubecon_pd_prefill_healthy_replicas", prefill_healthy_replicas, **model),
            sample("kubecon_pd_decode_healthy_replicas", decode_healthy_replicas, **model),
            sample("kubecon_pd_prefill_arrival_rate_rps", prefill_arrival_rate, **model),
            sample("kubecon_pd_prefill_service_rate_rps", prefill_service_rate, **model),
            sample("kubecon_pd_decode_service_rate_rps", decode_service_rate, **model),
            sample("kubecon_prefill_batch_fill_ratio", prefill_batch_fill_ratio, **model),
            sample("kubecon_tuning_max_num_batched_tokens", max_num_batched_tokens, **model),
            sample("kubecon_kv_transfer_latency_p99_seconds", values["kv_transfer_p99"], **model),
            sample("kubecon_kv_get_p99_seconds", values["kv_get_p99"], **model),
            sample("kubecon_kv_evictions_per_second", values["kv_evictions_per_second"], **model),
            sample(
                "kubecon_kv_remote_no_space_per_second",
                values["kv_remote_no_space_per_second"],
                **model,
            ),
            sample("kubecon_kv_transfer_bytes_per_second", values["kv_bytes_per_second"], **model),
            sample("kubecon_kv_transfer_retries_total", values["kv_retries"], metric_type="counter", **model),
            sample("kubecon_kv_transfer_errors_total", values["kv_errors"], metric_type="counter", **model),
            sample("kubecon_kv_cache_usage_ratio", values["kv_cache_usage"], **model),
            sample("kubecon_kv_cache_hit_ratio", values["kv_cache_hit_ratio"], **model),
            sample("kubecon_gpu_utilization_percent", values["gpu_utilization"], **model),
            sample("kubecon_gpu_memory_used_ratio", values["gpu_memory_used"], **model),
            sample("kubecon_network_drops_per_second", values["network_drops"], **model),
            sample("kubecon_gpu_xid_errors", values["gpu_xid_errors"], **model),
            sample("kubecon_error_rate", values["error_rate"], **model),
            sample("kubecon_gateway_error_rate", values["gateway_error_rate"], **model),
            sample("kubecon_vllm_error_rate", values["vllm_error_rate"], **model),
            sample("kubecon_gpu_error_rate", values["gpu_error_rate"], **model),
            sample("kubecon_gateway_errors_total", int(counters["gateway"]), metric_type="counter", **model),
            sample("kubecon_vllm_errors_total", int(counters["vllm"]), metric_type="counter", **model),
            sample("kubecon_gpu_xid_errors_total", int(counters["gpu"]), metric_type="counter", **model),
        ]
    )


class Handler(BaseHTTPRequestHandler):
    state: DemoState

    def do_GET(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        if parsed.path == "/metrics":
            body = render_metrics(self.state).encode()
            self._send(200, body, "text/plain; version=0.0.4")
            return
        if parsed.path == "/healthz":
            self._send(200, b'{"status":"ok"}', "application/json")
            return
        if parsed.path == "/control":
            requested = parse_qs(parsed.query).get("scenario", [None])[0]
            if requested:
                try:
                    reset_counters = parse_qs(parsed.query).get("reset", ["0"])[0] == "1"
                    self.state.set(requested, reset_counters=reset_counters)
                except ValueError as exc:
                    self._send(400, json.dumps({"error": str(exc)}).encode(), "application/json")
                    return
            scenario, _, counters = self.state.snapshot()
            rounded_counters = {name: int(value) for name, value in counters.items()}
            self._send(200, json.dumps({"scenario": scenario, "counters": rounded_counters}).encode(), "application/json")
            return
        self._send(404, b'{"error":"not found"}', "application/json")

    def _send(self, status: int, body: bytes, content_type: str) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, _format: str, *_args: object) -> None:
        return


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=9108)
    args = parser.parse_args()
    Handler.state = DemoState()
    ThreadingHTTPServer((args.host, args.port), Handler).serve_forever()


if __name__ == "__main__":
    main()
