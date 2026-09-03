#!/usr/bin/env python3
"""Fail-fast acceptance test for the local baseline scenario."""

from __future__ import annotations

import argparse
import json
import math
import sys
import urllib.parse
import urllib.request
from dataclasses import dataclass


@dataclass
class Check:
    name: str
    value: float | str
    ok: bool
    expectation: str


def get_json(url: str) -> dict:
    with urllib.request.urlopen(url, timeout=10) as response:
        return json.load(response)


def query(prometheus_url: str, expression: str) -> float:
    url = f"{prometheus_url}/api/v1/query?" + urllib.parse.urlencode({"query": expression})
    payload = get_json(url)
    if payload.get("status") != "success":
        raise RuntimeError(f"Prometheus query failed: {expression}")
    result = payload["data"]["result"]
    if not result:
        raise RuntimeError(f"Prometheus query returned no series: {expression}")
    value = float(result[0]["value"][1])
    if not math.isfinite(value):
        raise RuntimeError(f"Prometheus query returned a non-finite value: {expression}")
    return value


def target_checks(prometheus_url: str) -> list[Check]:
    payload = get_json(f"{prometheus_url}/api/v1/targets?state=active")
    targets = payload["data"]["activeTargets"]
    required_jobs = {
        "cross-layer-telemetry",
        "demo-loadgen",
        "llm-d-inference-sim",
        "ppt-demo-epp",
        "ppt-demo-gateway",
    }
    checks: list[Check] = []
    for job in sorted(required_jobs):
        matching = [target for target in targets if target.get("labels", {}).get("job") == job]
        up = sum(target.get("health") == "up" for target in matching)
        checks.append(Check(f"Prometheus target {job}", f"{up}/{len(matching)} up", bool(matching) and up == len(matching), "all active targets are up"))
    return checks


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate the running ppt-demo baseline")
    parser.add_argument("--prometheus-url", default="http://127.0.0.1:9090")
    args = parser.parse_args()
    base = args.prometheus_url.rstrip("/")

    try:
        checks = target_checks(base)
        scenario = query(base, 'max(kubecon_demo_scenario_info{scenario="baseline"})')
        gateway_total = query(base, 'sum(ppt_demo_proxy_requests_total{role="gateway",model="demo-model"})')
        gateway_rpm = query(base, 'sum(rate(ppt_demo_proxy_requests_total{role="gateway",model="demo-model"}[20s])) * 60')
        epp_rpm = query(base, 'sum(rate(ppt_demo_proxy_requests_total{role="epp",model="demo-model"}[20s])) * 60')
        vllm_rpm = query(base, 'sum(rate(vllm:request_success_total{model_name="demo-model"}[20s])) * 60')
        input_tpm = query(base, 'sum(rate(vllm:prompt_tokens_total{model_name="demo-model"}[20s])) * 60')
        output_tpm = query(base, 'sum(rate(vllm:generation_tokens_total{model_name="demo-model"}[20s])) * 60')
        client_error_rate = query(
            base,
            'sum(rate(ppt_demo_client_requests_total{model="demo-model",status_class=~"4xx|5xx|transport"}[20s])) '
            '/ clamp_min(sum(rate(ppt_demo_client_requests_total{model="demo-model"}[20s])), 0.001)',
        )
        gateway_5xx_rpm = query(
            base,
            '(sum(rate(ppt_demo_proxy_requests_total{role="gateway",model="demo-model",status_class="5xx"}[20s])) * 60 or vector(0))',
        )
        ttft_p95 = query(
            base,
            'histogram_quantile(0.95, sum by (le) (rate(vllm:time_to_first_token_seconds_bucket{model_name="demo-model"}[20s])))',
        )
        waiting = query(base, 'sum(vllm:num_requests_waiting{model_name="demo-model"})')
    except (OSError, KeyError, ValueError, RuntimeError) as exc:
        print(f"BASELINE FAIL: {exc}", file=sys.stderr)
        return 1

    epp_gateway_ratio = epp_rpm / gateway_rpm if gateway_rpm > 0 else math.inf
    vllm_gateway_ratio = vllm_rpm / gateway_rpm if gateway_rpm > 0 else math.inf

    checks.extend(
        [
            Check("Scenario", "baseline", scenario == 1, "baseline is active"),
            Check("Gateway total requests", gateway_total, gateway_total > 0, "> 0"),
            Check("Gateway RPM", gateway_rpm, gateway_rpm > 0, "> 0"),
            Check("EPP RPM", epp_rpm, epp_rpm > 0, "> 0"),
            Check("vLLM completed RPM", vllm_rpm, vllm_rpm > 0, "> 0"),
            Check("Gateway → EPP alignment", epp_gateway_ratio, 0.65 <= epp_gateway_ratio <= 1.35, "ratio 0.65–1.35"),
            Check("Gateway → vLLM alignment", vllm_gateway_ratio, 0.55 <= vllm_gateway_ratio <= 1.45, "ratio 0.55–1.45"),
            Check("Input TPM", input_tpm, input_tpm > 0, "> 0"),
            Check("Output TPM", output_tpm, output_tpm > 0, "> 0"),
            Check("Client error rate", client_error_rate, client_error_rate <= 0.01, "≤ 1%"),
            Check("Gateway 5xx RPM", gateway_5xx_rpm, gateway_5xx_rpm <= 0.1, "≈ 0"),
            Check("TTFT p95", ttft_p95, 0 < ttft_p95 <= 1.0, "0–1 s"),
            Check("vLLM waiting", waiting, waiting <= 1, "≤ 1"),
        ]
    )

    print("\nBaseline acceptance")
    print("-" * 88)
    for check in checks:
        marker = "PASS" if check.ok else "FAIL"
        value = f"{check.value:.4g}" if isinstance(check.value, float) else check.value
        print(f"{marker:4}  {check.name:<40} {value:<16} expected {check.expectation}")
    failed = [check for check in checks if not check.ok]
    print("-" * 88)
    if failed:
        print(f"BASELINE FAIL: {len(failed)} check(s) failed")
        return 1
    print("BASELINE PASS: request path and inference service signals are healthy")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
