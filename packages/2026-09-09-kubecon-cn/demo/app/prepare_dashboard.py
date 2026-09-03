#!/usr/bin/env python3
"""Build the focused demo dashboard from the bundled panel template."""

from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path
from typing import Any


PROMETHEUS = {"type": "prometheus", "uid": "prometheus"}


def query(expr: str, legend: str, ref_id: str, *, instant: bool = False) -> dict[str, Any]:
    target = {
        "datasource": dict(PROMETHEUS),
        "editorMode": "code",
        "expr": expr,
        "legendFormat": legend,
        "range": not instant,
        "refId": ref_id,
    }
    if instant:
        target["instant"] = True
    return target


def row(panel_id: int, title: str, y: int) -> dict[str, Any]:
    return {
        "collapsed": False,
        "gridPos": {"h": 1, "w": 24, "x": 0, "y": y},
        "id": panel_id,
        "panels": [],
        "title": title,
        "type": "row",
    }


def thresholds(green: float | None, yellow: float | None = None, red: float | None = None) -> dict[str, Any]:
    steps: list[dict[str, Any]] = [{"color": "green", "value": green}]
    if yellow is not None:
        steps.append({"color": "yellow", "value": yellow})
    if red is not None:
        steps.append({"color": "red", "value": red})
    return {"mode": "absolute", "steps": steps}


def healthy_thresholds(minimum: float = 1) -> dict[str, Any]:
    return {
        "mode": "absolute",
        "steps": [
            {"color": "red", "value": None},
            {"color": "green", "value": minimum},
        ],
    }


def clone_panel(
    templates: dict[int, dict[str, Any]],
    template_id: int,
    panel_id: int,
    title: str,
    description: str,
    grid_pos: dict[str, int],
    targets: list[dict[str, Any]],
) -> dict[str, Any]:
    panel = copy.deepcopy(templates[template_id])
    panel["id"] = panel_id
    panel["title"] = title
    panel["description"] = description
    panel["gridPos"] = grid_pos
    panel["datasource"] = dict(PROMETHEUS)
    panel["targets"] = targets
    panel.pop("repeat", None)
    panel.pop("repeatDirection", None)
    panel.pop("transformations", None)
    return panel


def stat_panel(
    templates: dict[int, dict[str, Any]],
    template_id: int,
    panel_id: int,
    title: str,
    description: str,
    grid_pos: dict[str, int],
    targets: list[dict[str, Any]],
    unit: str,
    panel_thresholds: dict[str, Any],
    *,
    text_mode: str = "auto",
) -> dict[str, Any]:
    panel = clone_panel(templates, template_id, panel_id, title, description, grid_pos, targets)
    panel["fieldConfig"]["defaults"]["unit"] = unit
    panel["fieldConfig"]["defaults"]["thresholds"] = panel_thresholds
    panel["fieldConfig"]["defaults"]["mappings"] = []
    panel["fieldConfig"]["overrides"] = []
    panel["options"]["textMode"] = text_mode
    panel["options"]["reduceOptions"]["calcs"] = ["lastNotNull"]
    return panel


def timeseries_panel(
    templates: dict[int, dict[str, Any]],
    template_id: int,
    panel_id: int,
    title: str,
    description: str,
    grid_pos: dict[str, int],
    targets: list[dict[str, Any]],
    unit: str,
    *,
    unit_overrides: dict[str, str] | None = None,
) -> dict[str, Any]:
    panel = clone_panel(templates, template_id, panel_id, title, description, grid_pos, targets)
    panel["fieldConfig"]["defaults"]["unit"] = unit
    panel["fieldConfig"]["overrides"] = [
        {
            "matcher": {"id": "byName", "options": field_name},
            "properties": [{"id": "unit", "value": field_unit}],
        }
        for field_name, field_unit in (unit_overrides or {}).items()
    ]
    return panel


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path, help="bundled Grafana panel template")
    parser.add_argument("output", type=Path)
    args = parser.parse_args()

    source = json.loads(args.source.read_text())
    templates = {panel["id"]: panel for panel in source["panels"] if "id" in panel}
    required_templates = {101, 102, 106, 110, 124, 142, 151, 187, 190}
    missing = required_templates.difference(templates)
    if missing:
        raise SystemExit(f"source dashboard is missing panel templates: {sorted(missing)}")

    dashboard = copy.deepcopy(source)
    dashboard.pop("id", None)
    dashboard.pop("iteration", None)
    dashboard["title"] = "InferX | Model Operations — KubeCon Demo"
    dashboard["uid"] = "inferx-model-ops-ppt-demo"
    dashboard["version"] = 1
    dashboard["editable"] = True
    dashboard["refresh"] = "5s"
    dashboard["tags"] = ["inferx", "kubecon", "ttft", "demo", "signal-provenance"]
    dashboard["time"] = {"from": "now-5m", "to": "now"}
    dashboard["links"] = []
    dashboard["templating"] = {
        "list": [
            {
                "name": "model",
                "label": "Model",
                "type": "custom",
                "query": "demo-model",
                "options": [{"text": "demo-model", "value": "demo-model", "selected": True}],
                "current": {"text": "demo-model", "value": "demo-model"},
            }
        ]
    }

    ttft_p50 = 'histogram_quantile(0.50, sum by (le) (rate(vllm:time_to_first_token_seconds_bucket{model_name="$model"}[20s])))'
    ttft_p95 = 'histogram_quantile(0.95, sum by (le) (rate(vllm:time_to_first_token_seconds_bucket{model_name="$model"}[20s])))'
    ttft_p99 = 'histogram_quantile(0.99, sum by (le) (rate(vllm:time_to_first_token_seconds_bucket{model_name="$model"}[20s])))'
    queue_p95 = 'histogram_quantile(0.95, sum by (le) (rate(vllm:request_queue_time_seconds_bucket{model_name="$model"}[20s])))'
    e2e_p95 = 'histogram_quantile(0.95, sum by (le) (rate(vllm:e2e_request_latency_seconds_bucket{model_name="$model"}[20s])))'
    tpot_p95 = 'histogram_quantile(0.95, sum by (le) (rate(vllm:time_per_output_token_seconds_bucket{model_name="$model"}[20s])))'
    gateway_total = 'sum(ppt_demo_proxy_requests_total{role="gateway",model="$model"})'
    # A 20-second rolling rate keeps a live talk responsive; multiplying by 60
    # presents the result in the standard RPM/TPM unit.
    gateway_rpm = 'sum(rate(ppt_demo_proxy_requests_total{role="gateway",model="$model"}[20s])) * 60'
    epp_rpm = 'sum(rate(ppt_demo_proxy_requests_total{role="epp",model="$model"}[20s])) * 60'
    vllm_rpm = 'sum(rate(vllm:request_success_total{model_name="$model"}[20s])) * 60'
    input_tpm = 'sum(rate(vllm:prompt_tokens_total{model_name="$model"}[20s])) * 60'
    output_tpm = 'sum(rate(vllm:generation_tokens_total{model_name="$model"}[20s])) * 60'
    client_error_rate = (
        'sum(rate(ppt_demo_client_requests_total{model="$model",status_class=~"4xx|5xx|transport"}[20s])) '
        '/ clamp_min(sum(rate(ppt_demo_client_requests_total{model="$model"}[20s])), 0.001)'
    )

    requests_2xx_rpm = 'sum(rate(ppt_demo_proxy_requests_total{role="gateway",model="$model",status_class="2xx"}[20s])) * 60'
    requests_5xx_rpm = '(sum(rate(ppt_demo_proxy_requests_total{role="gateway",model="$model",status_class="5xx"}[20s])) * 60 or vector(0))'

    panels: list[dict[str, Any]] = [row(1000, "1 Entry | Is the inference service delivering tokens?", 0)]
    top_stats = [
        (1001, 101, "Scenario", "kubecon_demo_scenario_info == 1", "{{scenario}}", "short", thresholds(None), "name"),
        (1002, 101, "PD Topology [REPLAY]", "kubecon_pd_profile_info == 1", "{{profile}}", "short", thresholds(None), "name"),
        (1003, 106, "Ingress RPM", gateway_rpm, "RPM", "short", thresholds(None), "auto"),
        (1004, 106, "5xx RPM", requests_5xx_rpm, "5xx", "short", thresholds(None, red=1), "auto"),
        (1005, 106, "Input TPM", input_tpm, "input", "short", thresholds(None), "auto"),
        (1006, 106, "Output TPM", output_tpm, "output", "short", thresholds(None), "auto"),
        (1007, 110, "TTFT p95", ttft_p95, "TTFT", "s", thresholds(None, yellow=0.8, red=2.0), "auto"),
        (1008, 106, "Client Error", client_error_rate, "error", "percentunit", thresholds(None, yellow=0.02, red=0.05), "auto"),
    ]
    for index, (panel_id, template_id, title, expression, legend, unit, panel_thresholds, text_mode) in enumerate(top_stats):
        panels.append(
            stat_panel(
                templates,
                template_id,
                panel_id,
                title,
                "MEASURED unless the title is marked [REPLAY]. Rolling window: 20 seconds.",
                {"h": 4, "w": 3, "x": index * 3, "y": 1},
                [query(expression, legend, "A", instant=text_mode == "name")],
                unit,
                panel_thresholds,
                text_mode=text_mode,
            )
        )
    health_panels = [
        (1020, "Gateway | Healthy [REPLAY]", "kubecon_gateway_healthy_replicas"),
        (1021, "EPP | Healthy [REPLAY]", "kubecon_epp_healthy_replicas"),
        (1022, "Prefill | Healthy [REPLAY]", "kubecon_pd_prefill_healthy_replicas"),
        (1023, "Decode | Healthy [REPLAY]", "kubecon_pd_decode_healthy_replicas"),
    ]
    for index, (panel_id, title, healthy_metric) in enumerate(health_panels):
        panels.append(
            stat_panel(
                templates,
                106,
                panel_id,
                title,
                "Current healthy replica count. Capacity targets vary by workload and production environment.",
                {"h": 4, "w": 6, "x": index * 6, "y": 5},
                [query(f'{healthy_metric}{{signal_source="simulated"}}', "Healthy", "A")],
                "short",
                healthy_thresholds(),
            )
        )
    panels.extend(
        [
            timeseries_panel(
                templates, 151, 1010, "Request Path | Gateway → EPP → vLLM",
                "MEASURED request handoff. A gap identifies where requests stop progressing.",
                {"h": 7, "w": 8, "x": 0, "y": 9},
                [query(gateway_rpm, "1 Gateway", "A"), query(epp_rpm, "2 EPP", "B"), query(vllm_rpm, "3 vLLM", "C")],
                "short",
            ),
            timeseries_panel(
                templates, 151, 1011, "Token Flow | Demand vs Delivery",
                "MEASURED Input TPM is accepted work; Output TPM is service delivered.",
                {"h": 7, "w": 8, "x": 8, "y": 9},
                [query(input_tpm, "Input TPM", "A"), query(output_tpm, "Output TPM", "B")],
                "short",
            ),
            timeseries_panel(
                templates, 124, 1012, "User SLO | TTFT vs TPOT",
                "MEASURED. TTFT localizes first-token delay; TPOT protects Decode cadence.",
                {"h": 7, "w": 8, "x": 16, "y": 9},
                [query(ttft_p95, "TTFT p95", "A"), query(tpot_p95, "TPOT p95", "B")],
                "s",
            ),
        ]
    )

    panels.append(row(1100, "2 Localize | Which layer turns abnormal first?", 16))
    panels.extend(
        [
            timeseries_panel(
                templates, 142, 1101, "Control Plane [REPLAY] | Route + EPP",
                "Negative control: route latency and EPP queue remain bounded.",
                {"h": 7, "w": 6, "x": 0, "y": 17},
                [query('kubecon_route_latency_p95_seconds{model="$model",signal_source="simulated"}', "route p95", "A"), query('kubecon_epp_queue_depth{model="$model",signal_source="simulated"}', "EPP queue", "B")],
                "s", unit_overrides={"EPP queue": "short"},
            ),
            timeseries_panel(
                templates, 151, 1102, "Stage Waiting [REPLAY] | Prefill vs Decode",
                "Compare P and D directly. The first queue that moves determines the next proof view.",
                {"h": 7, "w": 6, "x": 6, "y": 17},
                [query('kubecon_vllm_prefill_waiting{model="$model",signal_source="simulated"}', "Prefill waiting", "A"), query('kubecon_vllm_decode_waiting{model="$model",signal_source="simulated"}', "Decode waiting", "B")],
                "short",
            ),
            timeseries_panel(
                templates, 187, 1103, "KV / NIXL [REPLAY] | Hit + Arena + GET",
                "A low hit ratio, full arena, or slow GET localizes a PD handoff/cache incident without changing P:D replicas.",
                {"h": 7, "w": 6, "x": 12, "y": 17},
                [
                    query('kubecon_kv_cache_hit_ratio{model="$model",signal_source="simulated"}', "hit ratio", "A"),
                    query('kubecon_kv_cache_usage_ratio{model="$model",signal_source="simulated"}', "arena usage", "B"),
                    query('kubecon_kv_get_p99_seconds{model="$model",signal_source="simulated"}', "GET p99", "C"),
                ],
                "percentunit", unit_overrides={"GET p99": "s"},
            ),
            timeseries_panel(
                templates, 151, 1104, "Fault Owner [REPLAY] | GW · vLLM · GPU · Net",
                "Owner counters are mutually distinguishable fault fingerprints; they are replayed on the GPU-less Mac.",
                {"h": 7, "w": 6, "x": 18, "y": 17},
                [
                    query('kubecon_gateway_errors_total{model="$model",signal_source="simulated"}', "Gateway errors", "A"),
                    query('kubecon_vllm_errors_total{model="$model",signal_source="simulated"}', "vLLM errors", "B"),
                    query('kubecon_gpu_xid_errors_total{model="$model",signal_source="simulated"}', "GPU XID", "C"),
                    query('kubecon_network_drops_per_second{model="$model",signal_source="simulated"}', "network drops/s", "D"),
                ],
                "short",
            ),
        ]
    )

    panels.append(row(1200, "3 Evidence | Confirm the owner before choosing an action", 24))
    panels.extend(
        [
            timeseries_panel(
                templates, 151, 1201, "HTTP Outcomes | 2xx + 429 + 5xx",
                "MEASURED at Gateway. Gateway failure stops before EPP; vLLM failure reaches EPP but has no completed engine RPM.",
                {"h": 7, "w": 6, "x": 0, "y": 25},
                [
                    query(requests_2xx_rpm, "2xx", "A"),
                    query('sum(rate(ppt_demo_proxy_requests_total{role="gateway",model="$model",response_code="429"}[20s])) * 60', "429", "B"),
                    query(requests_5xx_rpm, "5xx", "C"),
                ],
                "short",
            ),
            timeseries_panel(
                templates, 151, 1202, "KV Failure Proof [REPLAY] | Eviction + No Space + Swap",
                "The default incident is a fixed-3P×2D KV-cache pressure case: eviction/no-space rises before recovery.",
                {"h": 7, "w": 6, "x": 6, "y": 25},
                [
                    query('kubecon_kv_evictions_per_second{model="$model",signal_source="simulated"}', "evictions/s", "A"),
                    query('kubecon_kv_remote_no_space_per_second{model="$model",signal_source="simulated"}', "remote no-space/s", "B"),
                    query('kubecon_vllm_swapped_requests{model="$model",signal_source="simulated"}', "swapped", "C"),
                ],
                "short",
            ),
            timeseries_panel(
                templates, 187, 1203, "GPU / Infra [REPLAY] | Util + Memory + XID",
                "A GPU case has XID or abnormal utilization/memory while Gateway/EPP remain healthy.",
                {"h": 7, "w": 6, "x": 12, "y": 25},
                [
                    query('kubecon_gpu_utilization_percent{model="$model",signal_source="simulated"} / 100', "GPU util", "A"),
                    query('kubecon_gpu_memory_used_ratio{model="$model",signal_source="simulated"}', "GPU memory", "B"),
                    query('kubecon_gpu_xid_errors_total{model="$model",signal_source="simulated"}', "GPU XID", "C"),
                ],
                "percentunit", unit_overrides={"GPU XID": "short"},
            ),
            timeseries_panel(
                templates, 151, 1204, "Layer Error Rate [REPLAY] | Gateway vs vLLM vs GPU",
                "Use the owner-specific error rate only after the measured request path identifies where traffic stopped.",
                {"h": 7, "w": 6, "x": 18, "y": 25},
                [
                    query('kubecon_gateway_error_rate{model="$model",signal_source="simulated"} * 100', "Gateway", "A"),
                    query('kubecon_vllm_error_rate{model="$model",signal_source="simulated"} * 100', "vLLM", "B"),
                    query('kubecon_gpu_error_rate{model="$model",signal_source="simulated"} * 100', "GPU", "C"),
                ],
                "percent",
            ),
        ]
    )

    panels.append(row(1300, "4 Recovery | Is the same 3P×2D service delivering tokens again?", 32))
    panels.extend(
        [
            timeseries_panel(
                templates, 151, 1301, "Request Path | Gateway → EPP → vLLM",
                "MEASURED recovery requires the three request rates to align again.",
                {"h": 7, "w": 8, "x": 0, "y": 33},
                [query(gateway_rpm, "1 Gateway", "A"), query(epp_rpm, "2 EPP", "B"), query(vllm_rpm, "3 vLLM", "C")],
                "short",
            ),
            timeseries_panel(
                templates, 124, 1302, "User SLO | TTFT vs TPOT",
                "MEASURED recovery requires first-token and decode cadence to return to their healthy bands.",
                {"h": 7, "w": 8, "x": 8, "y": 33},
                [query(ttft_p95, "TTFT p95", "A"), query(tpot_p95, "TPOT p95", "B")],
                "s",
            ),
            timeseries_panel(
                templates, 151, 1303, "Token Delivery | Input TPM + Output TPM + Completed RPM",
                "MEASURED recovery is not complete until the service is producing tokens, not merely returning HTTP 200.",
                {"h": 7, "w": 8, "x": 16, "y": 33},
                [query(input_tpm, "Input TPM", "A"), query(output_tpm, "Output TPM", "B"), query(vllm_rpm, "Completed RPM", "C")],
                "short",
            ),
        ]
    )

    dashboard["panels"] = panels
    args.output.write_text(json.dumps(dashboard, indent=2) + "\n")


if __name__ == "__main__":
    main()
