#!/usr/bin/env python3
"""Render a compact, colored cross-layer evidence report from Prometheus + JSONL."""

from __future__ import annotations

import argparse
import json
import math
import os
import sys
import urllib.parse
import urllib.request
from dataclasses import dataclass


MODEL = "demo-model"
SEVERITY = {"INFO": 0, "HEALTHY": 1, "UNKNOWN": 2, "WARNING": 3, "CRITICAL": 4}


@dataclass
class Row:
    section: str
    status: str
    metric: str
    value: str
    healthy: str


class Palette:
    def __init__(self, mode: str) -> None:
        enabled = mode == "always" or (
            mode == "auto"
            and "NO_COLOR" not in os.environ
            and (
                os.environ.get("FORCE_COLOR", "") not in ("", "0")
                or (sys.stdout.isatty() and os.environ.get("TERM", "") != "dumb")
            )
        )
        self.reset = "\033[0m" if enabled else ""
        self.bold = "\033[1m" if enabled else ""
        self.dim = "\033[2m" if enabled else ""
        self.red = "\033[31m" if enabled else ""
        self.green = "\033[32m" if enabled else ""
        self.yellow = "\033[33m" if enabled else ""
        self.cyan = "\033[36m" if enabled else ""
        self.gray = "\033[90m" if enabled else ""

    def paint(self, value: str, color: str) -> str:
        return f"{color}{value}{self.reset}"


class Prometheus:
    def __init__(self, base_url: str) -> None:
        self.base_url = base_url.rstrip("/")
        self.error: str | None = None

    def query(self, expression: str) -> float | None:
        if self.error:
            return None
        url = self.base_url + "/api/v1/query?" + urllib.parse.urlencode({"query": expression})
        try:
            with urllib.request.urlopen(url, timeout=4) as response:
                payload = json.load(response)
            result = payload["data"]["result"]
            if not result:
                return None
            return float(result[0]["value"][1])
        except Exception as exc:  # Keep the synthetic timeline usable if Prometheus is unavailable.
            self.error = str(exc)
            return None


def status_high_bad(value: float | None, healthy_max: float, warning_max: float) -> str:
    if value is None or not math.isfinite(value):
        return "UNKNOWN"
    if value <= healthy_max:
        return "HEALTHY"
    if value <= warning_max:
        return "WARNING"
    return "CRITICAL"


def status_low_bad(value: float | None, healthy_min: float, warning_min: float) -> str:
    if value is None or not math.isfinite(value):
        return "UNKNOWN"
    if value >= healthy_min:
        return "HEALTHY"
    if value >= warning_min:
        return "WARNING"
    return "CRITICAL"


def number(value: float | None, digits: int = 1) -> str:
    if value is None or not math.isfinite(value):
        return "warming up"
    if abs(value) >= 1000:
        return f"{value / 1000:.1f}k"
    if abs(value - round(value)) < 0.001:
        return str(int(round(value)))
    return f"{value:.{digits}f}"


def percent(value: float | None) -> str:
    if value is None or not math.isfinite(value):
        return "warming up"
    return f"{value * 100:.1f}%"


def seconds(value: float | None) -> str:
    if value is None or not math.isfinite(value):
        return "no successful samples"
    if value < 1:
        return f"{value * 1000:.0f}ms"
    return f"{value:.2f}s"


def all_equal(values: list[tuple[float | None, float | None]]) -> str:
    if any(actual is None or desired is None for actual, desired in values):
        return "UNKNOWN"
    return "HEALTHY" if all(actual == desired for actual, desired in values) else "CRITICAL"


def request_path_status(gateway: float | None, epp: float | None, vllm: float | None) -> str:
    values = (gateway, epp, vllm)
    if any(value is None or not math.isfinite(value) for value in values):
        return "UNKNOWN"
    assert gateway is not None and epp is not None and vllm is not None
    if gateway < 0.1:
        return "WARNING"
    if epp < 0.1 or vllm < 0.1:
        return "CRITICAL"
    epp_ratio = epp / gateway
    vllm_ratio = vllm / gateway
    if 0.65 <= epp_ratio <= 1.35 and 0.55 <= vllm_ratio <= 1.45:
        return "HEALTHY"
    return "WARNING"


def build_rows(prom: Prometheus, scenario: str) -> tuple[list[Row], dict[str, float | None]]:
    q = prom.query
    values: dict[str, float | None] = {
        "gateway_rpm": q('sum(rate(ppt_demo_proxy_requests_total{role="gateway",model="demo-model"}[20s])) * 60'),
        "epp_rpm": q('sum(rate(ppt_demo_proxy_requests_total{role="epp",model="demo-model"}[20s])) * 60'),
        "vllm_rpm": q('sum(rate(vllm:request_success_total{model_name="demo-model"}[20s])) * 60'),
        "five_xx_rpm": q('(sum(rate(ppt_demo_proxy_requests_total{role="gateway",model="demo-model",status_class="5xx"}[20s])) * 60) or vector(0)'),
        "client_error": q('(sum(rate(ppt_demo_client_requests_total{model="demo-model",status_class=~"4xx|5xx|transport"}[20s])) / clamp_min(sum(rate(ppt_demo_client_requests_total{model="demo-model"}[20s])), 0.001)) or vector(0)'),
        "input_tpm": q('sum(rate(vllm:prompt_tokens_total{model_name="demo-model"}[20s])) * 60'),
        "output_tpm": q('sum(rate(vllm:generation_tokens_total{model_name="demo-model"}[20s])) * 60'),
        "ttft": q('histogram_quantile(0.95, sum by (le) (rate(vllm:time_to_first_token_seconds_bucket{model_name="demo-model"}[20s])))'),
        "gateway_healthy": q("kubecon_gateway_healthy_replicas"),
        "gateway_desired": q("kubecon_gateway_desired_replicas"),
        "epp_healthy": q("kubecon_epp_healthy_replicas"),
        "epp_desired": q("kubecon_epp_desired_replicas"),
        "prefill_healthy": q('kubecon_pd_prefill_healthy_replicas{model="demo-model"}'),
        "prefill_desired": q('kubecon_pd_prefill_replicas{model="demo-model"}'),
        "decode_healthy": q('kubecon_pd_decode_healthy_replicas{model="demo-model"}'),
        "decode_desired": q('kubecon_pd_decode_replicas{model="demo-model"}'),
        "prefill_waiting": q('kubecon_vllm_prefill_waiting{model="demo-model"}'),
        "decode_waiting": q('kubecon_vllm_decode_waiting{model="demo-model"}'),
        "kv_hit": q('kubecon_kv_cache_hit_ratio{model="demo-model"}'),
        "kv_usage": q('kubecon_kv_cache_usage_ratio{model="demo-model"}'),
        "kv_get": q('kubecon_kv_get_p99_seconds{model="demo-model"}'),
        "kv_evictions": q('kubecon_kv_evictions_per_second{model="demo-model"}'),
        "kv_no_space": q('kubecon_kv_remote_no_space_per_second{model="demo-model"}'),
        "gateway_error": q('kubecon_gateway_error_rate{model="demo-model"}'),
        "vllm_error": q('kubecon_vllm_error_rate{model="demo-model"}'),
        "gpu_error": q('kubecon_gpu_error_rate{model="demo-model"}'),
        "gpu_util": q('kubecon_gpu_utilization_percent{model="demo-model"}'),
        "gpu_memory": q('kubecon_gpu_memory_used_ratio{model="demo-model"}'),
        "gpu_xid": q('kubecon_gpu_xid_errors{model="demo-model"}'),
        "network_drops": q('kubecon_network_drops_per_second{model="demo-model"}'),
        "scenario_active": q(
            f'max(kubecon_demo_scenario_info{{scenario="{scenario}",signal_source="simulated"}})'
        ),
    }

    rows: list[Row] = []
    rows.append(
        Row(
            "Impact / User",
            request_path_status(values["gateway_rpm"], values["epp_rpm"], values["vllm_rpm"]),
            "Request path RPM",
            f'GW {number(values["gateway_rpm"])} → EPP {number(values["epp_rpm"])} → vLLM {number(values["vllm_rpm"])}',
            "all stages >0 and aligned",
        )
    )
    rows.append(
        Row(
            "Impact / User",
            status_high_bad(values["five_xx_rpm"], 0.1, 1.0),
            "Gateway 5xx",
            f'{number(values["five_xx_rpm"])} RPM',
            "healthy ≤0.1 RPM",
        )
    )
    rows.append(
        Row(
            "Impact / User",
            status_high_bad(values["client_error"], 0.01, 0.05),
            "Client error",
            percent(values["client_error"]),
            "healthy ≤1%",
        )
    )
    rows.append(
        Row(
            "Impact / User",
            status_high_bad(values["ttft"], 0.8, 2.0),
            "TTFT p95",
            seconds(values["ttft"]),
            "healthy ≤800ms; critical >2s",
        )
    )
    token_status = "UNKNOWN"
    if values["output_tpm"] is not None and math.isfinite(values["output_tpm"]):
        token_status = "HEALTHY" if values["output_tpm"] > 0 else "CRITICAL"
    rows.append(
        Row(
            "Impact / User",
            token_status,
            "Token delivery",
            f'input {number(values["input_tpm"])} / output {number(values["output_tpm"])} TPM',
            "healthy when output TPM >0",
        )
    )

    scenario_status = "UNKNOWN"
    if values["scenario_active"] is not None:
        scenario_status = "HEALTHY" if values["scenario_active"] == 1 else "CRITICAL"
    scenario_value = {
        "HEALTHY": "selected scenario is active",
        "CRITICAL": "SCENARIO MISMATCH",
        "UNKNOWN": "unable to verify active scenario",
    }[scenario_status]
    rows.append(
        Row(
            "Health / Topology",
            scenario_status,
            "Scenario selection",
            scenario_value,
            "selected scenario = active scenario",
        )
    )
    rows.append(
        Row(
            "Health / Topology",
            all_equal(
                [
                    (values["gateway_healthy"], values["gateway_desired"]),
                    (values["epp_healthy"], values["epp_desired"]),
                ]
            ),
            "Gateway / EPP health",
            (
                f'GW {number(values["gateway_healthy"])}/{number(values["gateway_desired"])} · '
                f'EPP {number(values["epp_healthy"])}/{number(values["epp_desired"])}'
            ),
            "healthy = desired",
        )
    )
    rows.append(
        Row(
            "Health / Topology",
            all_equal(
                [
                    (values["prefill_healthy"], values["prefill_desired"]),
                    (values["decode_healthy"], values["decode_desired"]),
                ]
            ),
            "Prefill / Decode health",
            (
                f'P {number(values["prefill_healthy"])}/{number(values["prefill_desired"])} · '
                f'D {number(values["decode_healthy"])}/{number(values["decode_desired"])}'
            ),
            "healthy = desired",
        )
    )

    rows.append(
        Row(
            "Layer boundary",
            status_high_bad(values["prefill_waiting"], 2, 8),
            "Prefill waiting",
            number(values["prefill_waiting"]),
            "healthy ≤2; critical >8",
        )
    )
    rows.append(
        Row(
            "Layer boundary",
            status_high_bad(values["decode_waiting"], 2, 5),
            "Decode waiting",
            number(values["decode_waiting"]),
            "healthy ≤2; critical >5",
        )
    )

    rows.append(
        Row(
            "Owner evidence",
            status_low_bad(values["kv_hit"], 0.75, 0.60),
            "KV hit ratio",
            percent(values["kv_hit"]),
            "healthy ≥75%; critical <60%",
        )
    )
    rows.append(
        Row(
            "Owner evidence",
            status_high_bad(values["kv_usage"], 0.80, 0.90),
            "KV arena usage",
            percent(values["kv_usage"]),
            "healthy ≤80%; critical >90%",
        )
    )
    rows.append(
        Row(
            "Owner evidence",
            status_high_bad(values["kv_get"], 0.20, 1.0),
            "KV GET p99",
            seconds(values["kv_get"]),
            "healthy ≤200ms; critical >1s",
        )
    )
    eviction_status = "UNKNOWN"
    if values["kv_evictions"] is not None and values["kv_no_space"] is not None:
        eviction_status = (
            "HEALTHY"
            if values["kv_evictions"] == 0 and values["kv_no_space"] == 0
            else "CRITICAL"
        )
    rows.append(
        Row(
            "Owner evidence",
            eviction_status,
            "KV eviction / no-space",
            f'{number(values["kv_evictions"])}/s · {number(values["kv_no_space"])}/s',
            "healthy when both are 0",
        )
    )

    layer_error = max(
        (
            value
            for value in (values["gateway_error"], values["vllm_error"], values["gpu_error"])
            if value is not None and math.isfinite(value)
        ),
        default=None,
    )
    rows.append(
        Row(
            "Negative controls",
            status_high_bad(layer_error, 0.001, 0.05),
            "Layer error rate",
            (
                f'GW {percent(values["gateway_error"])} · '
                f'vLLM {percent(values["vllm_error"])} · '
                f'GPU {percent(values["gpu_error"])}'
            ),
            "healthy when all ≤0.1%",
        )
    )
    gpu_status = "UNKNOWN"
    if values["gpu_xid"] is not None:
        gpu_status = "HEALTHY" if values["gpu_xid"] == 0 else "CRITICAL"
    rows.append(
        Row(
            "Negative controls",
            gpu_status,
            "GPU XID",
            (
                f'active {number(values["gpu_xid"])} · util {number(values["gpu_util"])}% · '
                f'memory {percent(values["gpu_memory"])}'
            ),
            "healthy when active XID = 0",
        )
    )
    rows.append(
        Row(
            "Negative controls",
            status_high_bad(values["network_drops"], 0, 1),
            "Network drops",
            f'{number(values["network_drops"])}/s',
            "healthy = 0/s",
        )
    )
    return rows, values


def infer_owner(values: dict[str, float | None], scenario: str) -> str:
    def above(key: str, threshold: float) -> bool:
        value = values.get(key)
        return value is not None and math.isfinite(value) and value > threshold

    gateway = values.get("gateway_rpm") or 0
    epp = values.get("epp_rpm") or 0
    vllm = values.get("vllm_rpm") or 0
    if above("gateway_error", 0.05) or (
        values.get("gateway_healthy") is not None and values["gateway_healthy"] == 0
    ) or (gateway > 1 and epp < 0.1):
        return "Gateway"
    if above("vllm_error", 0.05) or (epp > 1 and vllm < 0.1):
        return "vLLM / engine"
    if above("gpu_error", 0.01) or above("gpu_xid", 0):
        return "GPU / device"
    if (
        above("kv_no_space", 0)
        or above("kv_evictions", 0)
        or above("kv_get", 1.0)
        or (
            values.get("kv_hit") is not None
            and math.isfinite(values["kv_hit"])
            and values["kv_hit"] < 0.60
        )
    ):
        return "KV / cache"
    if above("prefill_waiting", 8):
        return "Prefill capacity"
    if not any(value is not None for value in values.values()):
        return {
            "incident": "KV / cache",
            "gateway_error": "Gateway",
            "vllm_error": "vLLM / engine",
            "gpu_error": "GPU / device",
            "load": "Prefill capacity",
            "prefill_pressure": "Prefill capacity",
        }.get(scenario, "none identified")
    return "none identified"


def render(
    scenario: str,
    request_id: str,
    rows: list[Row],
    values: dict[str, float | None],
    palette: Palette,
    prometheus_error: str | None,
) -> None:
    overall = max((row.status for row in rows), key=lambda item: SEVERITY[item])
    counts = {status: sum(row.status == status for row in rows) for status in SEVERITY}
    owner = infer_owner(values, scenario)
    badge_colors = {
        "INFO": palette.cyan,
        "HEALTHY": palette.green,
        "UNKNOWN": palette.gray,
        "WARNING": palette.yellow,
        "CRITICAL": palette.red,
    }
    icons = {"INFO": "•", "HEALTHY": "✓", "UNKNOWN": "?", "WARNING": "!", "CRITICAL": "✗"}

    print()
    print(palette.paint("INFERENCE EVIDENCE", palette.bold + palette.cyan))
    print(f"Scenario : {palette.paint(scenario, palette.bold)}")
    print(f"Request  : {request_id}  |  Model: {MODEL}")
    summary = (
        f"{overall}  |  suspected owner: {owner}  |  "
        f"critical {counts['CRITICAL']} · warning {counts['WARNING']} · healthy {counts['HEALTHY']}"
    )
    print("Summary  : " + palette.paint(summary, badge_colors[overall]))
    if prometheus_error:
        print(palette.paint(f"Prometheus unavailable: {prometheus_error}", palette.yellow))

    current_section = ""
    for row in rows:
        if row.section != current_section:
            current_section = row.section
            print()
            print(palette.paint(f"── {current_section}", palette.bold + palette.cyan))
            print(f"  {'STATUS':<10} {'METRIC':<27} {'CURRENT':<35} HEALTHY CONDITION")
        badge = f"{icons[row.status]} {row.status}"
        colored_badge = palette.paint(f"{badge:<10}", badge_colors[row.status])
        print(
            f"  {colored_badge} {row.metric:<27} "
            f"{row.value:<35} {row.healthy}"
        )

    conclusions = {
        "Gateway": (
            "Traffic stops after Gateway; inspect Gateway health, routing, and HTTP 5xx.",
            "流量在 Gateway 后中断；检查 Gateway 健康状态、路由和 HTTP 5xx。",
        ),
        "vLLM / engine": (
            "Requests reach EPP, but engine completions drop to zero; vLLM is the fault owner.",
            "请求到达 EPP，但 engine 完成量降为零；故障归属 vLLM。",
        ),
        "GPU / device": (
            "The request path remains live, but GPU XID/error signals identify the device layer.",
            "请求路径仍然贯通，但 GPU XID/错误信号将故障定位到设备层。",
        ),
        "KV / cache": (
            "KV exhaustion or slow access → misses/evictions → Prefill recomputation → higher TTFT.",
            "KV 空间不足或访问变慢 → miss/eviction → Prefill 重算 → TTFT 上升。",
        ),
        "Prefill capacity": (
            "Prefill arrival rate exceeds service capacity → queue growth → higher TTFT.",
            "Prefill 到达率超过服务能力 → 队列增长 → TTFT 上升。",
        ),
        "none identified": (
            "No active fault owner identified; verify token delivery and the SLO before closure.",
            "未识别到活跃故障归属；关单前确认 token delivery 与 SLO。",
        ),
    }
    print()
    diagnosis_en, diagnosis_zh = conclusions[owner]
    print(palette.paint("Diagnosis :", palette.bold))
    print(f"  EN   : {diagnosis_en}")
    print(f"  中文 : {diagnosis_zh}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("scenario")
    parser.add_argument("--request-id", default="demo-0042")
    parser.add_argument("--prometheus-url", default=os.environ.get("PROMETHEUS_URL", "http://127.0.0.1:9090"))
    parser.add_argument("--color", choices=("auto", "always", "never"), default="auto")
    args = parser.parse_args()

    palette = Palette(args.color)
    prometheus = Prometheus(args.prometheus_url)
    rows, values = build_rows(prometheus, args.scenario)
    render(
        args.scenario,
        args.request_id,
        rows,
        values,
        palette,
        prometheus.error,
    )


if __name__ == "__main__":
    main()
