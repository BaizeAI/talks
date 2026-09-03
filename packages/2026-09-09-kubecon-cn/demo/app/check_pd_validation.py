#!/usr/bin/env python3
"""Capture and compare the focused PD diagnosis demo checkpoints."""

from __future__ import annotations

import argparse
import json
import math
import sys
import urllib.parse
import urllib.request
from dataclasses import dataclass
from pathlib import Path


MODEL = "demo-model"


def get_json(url: str) -> dict:
    with urllib.request.urlopen(url, timeout=10) as response:
        return json.load(response)


def query_result(prometheus_url: str, expression: str) -> list[dict]:
    url = f"{prometheus_url}/api/v1/query?" + urllib.parse.urlencode({"query": expression})
    payload = get_json(url)
    if payload.get("status") != "success":
        raise RuntimeError(f"Prometheus query failed: {expression}")
    return payload["data"]["result"]


def query(prometheus_url: str, expression: str) -> float:
    result = query_result(prometheus_url, expression)
    if not result:
        raise RuntimeError(f"Prometheus query returned no series: {expression}")
    value = float(result[0]["value"][1])
    if not math.isfinite(value):
        raise RuntimeError(f"Prometheus query returned a non-finite value: {expression}")
    return value


def active_label(prometheus_url: str, expression: str, label: str) -> str:
    result = query_result(prometheus_url, expression)
    active = [series for series in result if float(series["value"][1]) == 1]
    if len(active) != 1:
        raise RuntimeError(f"expected one active {label}, got {len(active)}")
    return active[0]["metric"].get(label, "unknown")


def snapshot(prometheus_url: str, loadgen_replicas: int) -> dict[str, float | int | str]:
    model = f'model="{MODEL}"'
    engine_model = f'model_name="{MODEL}"'
    return {
        "scenario": active_label(prometheus_url, "kubecon_demo_scenario_info == 1", "scenario"),
        "action": active_label(prometheus_url, "kubecon_demo_action_info == 1", "action"),
        "loadgen_replicas": loadgen_replicas,
        "gateway_rpm": query(
            prometheus_url,
            f'sum(rate(ppt_demo_proxy_requests_total{{role="gateway",{model}}}[20s])) * 60',
        ),
        "epp_rpm": query(
            prometheus_url,
            f'sum(rate(ppt_demo_proxy_requests_total{{role="epp",{model}}}[20s])) * 60',
        ),
        "vllm_rpm": query(
            prometheus_url,
            f"sum(rate(vllm:request_success_total{{{engine_model}}}[20s])) * 60",
        ),
        "output_tpm": query(
            prometheus_url,
            f"sum(rate(vllm:generation_tokens_total{{{engine_model}}}[20s])) * 60",
        ),
        "ttft_p95": query(
            prometheus_url,
            "histogram_quantile(0.95, sum by (le) "
            f"(rate(vllm:time_to_first_token_seconds_bucket{{{engine_model}}}[20s])))",
        ),
        "engine_waiting": query(
            prometheus_url,
            f"sum(vllm:num_requests_waiting{{{engine_model}}})",
        ),
        "prefill_waiting": query(
            prometheus_url,
            f"kubecon_vllm_prefill_waiting{{{model}}}",
        ),
        "decode_waiting": query(
            prometheus_url,
            f"kubecon_vllm_decode_waiting{{{model}}}",
        ),
        "prefill_replicas": query(
            prometheus_url,
            f"kubecon_pd_prefill_replicas{{{model}}}",
        ),
        "decode_replicas": query(
            prometheus_url,
            f"kubecon_pd_decode_replicas{{{model}}}",
        ),
        "gateway_healthy_replicas": query(prometheus_url, "kubecon_gateway_healthy_replicas"),
        "gateway_desired_replicas": query(prometheus_url, "kubecon_gateway_desired_replicas"),
        "epp_healthy_replicas": query(prometheus_url, "kubecon_epp_healthy_replicas"),
        "epp_desired_replicas": query(prometheus_url, "kubecon_epp_desired_replicas"),
        "prefill_healthy_replicas": query(
            prometheus_url,
            f"kubecon_pd_prefill_healthy_replicas{{{model}}}",
        ),
        "decode_healthy_replicas": query(
            prometheus_url,
            f"kubecon_pd_decode_healthy_replicas{{{model}}}",
        ),
        "prefill_arrival_rps": query(
            prometheus_url,
            f"kubecon_pd_prefill_arrival_rate_rps{{{model}}}",
        ),
        "prefill_service_rps": query(
            prometheus_url,
            f"kubecon_pd_prefill_service_rate_rps{{{model}}}",
        ),
        "kv_transfer_p99": query(
            prometheus_url,
            f"kubecon_kv_transfer_latency_p99_seconds{{{model}}}",
        ),
        "network_drops": query(
            prometheus_url,
            f"kubecon_network_drops_per_second{{{model}}}",
        ),
        "client_error_rate": query(
            prometheus_url,
            f'sum(rate(ppt_demo_client_requests_total{{{model},status_class=~"4xx|5xx|transport"}}[20s])) '
            f'/ clamp_min(sum(rate(ppt_demo_client_requests_total{{{model}}}[20s])), 0.001)',
        ),
    }


@dataclass
class Check:
    name: str
    actual: str
    ok: bool
    expectation: str


def ratio(numerator: float, denominator: float) -> float:
    return numerator / denominator if denominator > 0 else math.inf


def compare(before: dict, after: dict) -> int:
    checks = [
        Check("Before checkpoint", str(before["scenario"]), before["scenario"] == "prefill_pressure", "prefill_pressure"),
        Check("After checkpoint", str(after["scenario"]), after["scenario"] == "pd_tuned", "pd_tuned"),
        Check(
            "Single controlled action",
            str(after["action"]),
            after["action"] == "pd_ratio_2p4d_to_3p3d",
            "pd_ratio_2p4d_to_3p3d",
        ),
        Check(
            "Demand held constant",
            f'{before["loadgen_replicas"]} → {after["loadgen_replicas"]}',
            before["loadgen_replicas"] == after["loadgen_replicas"] == 8,
            "8 → 8 loadgen replicas",
        ),
        Check(
            "PD allocation changed",
            f'{before["prefill_replicas"]:.0f}P:{before["decode_replicas"]:.0f}D → '
            f'{after["prefill_replicas"]:.0f}P:{after["decode_replicas"]:.0f}D',
            before["prefill_replicas"] == 2
            and before["decode_replicas"] == 4
            and after["prefill_replicas"] == 3
            and after["decode_replicas"] == 3,
            "2P:4D → 3P:3D (controlled replay)",
        ),
        Check(
            "Gateway/EPP health stayed ready",
            f'Gateway {before["gateway_healthy_replicas"]:.0f}/{before["gateway_desired_replicas"]:.0f} → '
            f'{after["gateway_healthy_replicas"]:.0f}/{after["gateway_desired_replicas"]:.0f}; '
            f'EPP {before["epp_healthy_replicas"]:.0f}/{before["epp_desired_replicas"]:.0f} → '
            f'{after["epp_healthy_replicas"]:.0f}/{after["epp_desired_replicas"]:.0f}',
            before["gateway_healthy_replicas"] == before["gateway_desired_replicas"] == 1
            and after["gateway_healthy_replicas"] == after["gateway_desired_replicas"] == 1
            and before["epp_healthy_replicas"] == before["epp_desired_replicas"] == 1
            and after["epp_healthy_replicas"] == after["epp_desired_replicas"] == 1,
            "Gateway 1/1 and EPP 1/1 before/after",
        ),
        Check(
            "PD health tracks desired profile",
            f'{before["prefill_healthy_replicas"]:.0f}P/{before["prefill_replicas"]:.0f}P, '
            f'{before["decode_healthy_replicas"]:.0f}D/{before["decode_replicas"]:.0f}D → '
            f'{after["prefill_healthy_replicas"]:.0f}P/{after["prefill_replicas"]:.0f}P, '
            f'{after["decode_healthy_replicas"]:.0f}D/{after["decode_replicas"]:.0f}D',
            before["prefill_healthy_replicas"] == before["prefill_replicas"] == 2
            and before["decode_healthy_replicas"] == before["decode_replicas"] == 4
            and after["prefill_healthy_replicas"] == after["prefill_replicas"] == 3
            and after["decode_healthy_replicas"] == after["decode_replicas"] == 3,
            "2P/2P + 4D/4D → 3P/3P + 3D/3D",
        ),
        Check(
            "Prefill queue fell",
            f'{before["prefill_waiting"]:.2f} → {after["prefill_waiting"]:.2f}',
            after["prefill_waiting"] < before["prefill_waiting"] * 0.5,
            "after < 50% of before",
        ),
        Check(
            "Measured TTFT tail improved",
            f'{before["ttft_p95"]:.3f}s → {after["ttft_p95"]:.3f}s',
            after["ttft_p95"] < before["ttft_p95"] * 0.75,
            "after < 75% of before",
        ),
        Check(
            "Decode guardrail bounded",
            f'{after["decode_waiting"]:.2f}',
            after["decode_waiting"] <= 3,
            "≤ 3 waiting",
        ),
        Check(
            "Prefill service covers arrivals",
            f'{after["prefill_service_rps"]:.2f} service / {after["prefill_arrival_rps"]:.2f} arrival',
            after["prefill_service_rps"] >= after["prefill_arrival_rps"],
            "service ≥ arrival",
        ),
        Check(
            "Gateway → EPP remains aligned",
            f'{ratio(after["epp_rpm"], after["gateway_rpm"]):.2f}',
            0.65 <= ratio(after["epp_rpm"], after["gateway_rpm"]) <= 1.35,
            "ratio 0.65–1.35",
        ),
        Check(
            "Gateway → vLLM remains aligned",
            f'{ratio(after["vllm_rpm"], after["gateway_rpm"]):.2f}',
            0.55 <= ratio(after["vllm_rpm"], after["gateway_rpm"]) <= 1.45,
            "ratio 0.55–1.45",
        ),
        Check(
            "Service rate did not regress",
            f'{before["output_tpm"]:.1f} → {after["output_tpm"]:.1f} TPM',
            after["output_tpm"] >= before["output_tpm"] * 0.75,
            "after ≥ 75% of before",
        ),
        Check(
            "Client error rate bounded",
            f'{after["client_error_rate"]:.2%}',
            after["client_error_rate"] <= 0.01,
            "≤ 1%",
        ),
        Check(
            "KV/network negative controls stayed flat",
            f'KV {before["kv_transfer_p99"]:.3f}s → {after["kv_transfer_p99"]:.3f}s; '
            f'network {after["network_drops"]:.0f}/s',
            abs(after["kv_transfer_p99"] - before["kv_transfer_p99"]) <= 0.02
            and after["network_drops"] == 0,
            "KV p99 change ≤ 20ms and network drops = 0",
        ),
    ]

    print("\nPD tuning validation")
    print("-" * 112)
    for check in checks:
        marker = "PASS" if check.ok else "FAIL"
        print(f"{marker:4}  {check.name:<40} {check.actual:<32} expected {check.expectation}")
    failed = [check for check in checks if not check.ok]
    print("-" * 112)
    if failed:
        print(f"PD VALIDATION FAIL: {len(failed)} check(s) failed")
        return 1
    print("PD VALIDATION PASS: first boundary, single action, and guardrails form a closed loop")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Capture or compare PD demo checkpoints")
    parser.add_argument("--prometheus-url", default="http://127.0.0.1:9090")
    subparsers = parser.add_subparsers(dest="command", required=True)
    snapshot_parser = subparsers.add_parser("snapshot")
    snapshot_parser.add_argument("--output", type=Path, required=True)
    snapshot_parser.add_argument("--loadgen-replicas", type=int, required=True)
    compare_parser = subparsers.add_parser("compare")
    compare_parser.add_argument("before", type=Path)
    compare_parser.add_argument("after", type=Path)
    args = parser.parse_args()

    try:
        if args.command == "snapshot":
            values = snapshot(args.prometheus_url.rstrip("/"), args.loadgen_replicas)
            args.output.write_text(json.dumps(values, indent=2) + "\n")
            print(json.dumps(values, indent=2))
            return 0
        return compare(json.loads(args.before.read_text()), json.loads(args.after.read_text()))
    except (OSError, KeyError, TypeError, ValueError, RuntimeError) as exc:
        print(f"PD VALIDATION FAIL: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
