#!/usr/bin/env python3
"""Print a bilingual, colored summary when a demo scenario changes."""

from __future__ import annotations

import argparse

from evidence_report import Palette


SCENARIOS = {
    "baseline": {
        "status": "HEALTHY",
        "title": "健康基线（HEALTHY BASELINE）",
        "simulate": "健康的 PD 分离推理服务（Healthy PD-disaggregated serving）",
        "healthy": "Gateway ✓ → EPP ✓ → Prefill 3/3 ✓ → Decode 2/2 ✓",
        "observe": "各层 RPM 对齐、5xx≈0、TPM>0、TTFT≤1s（Healthy traffic and latency）",
    },
    "incident": {
        "status": "CRITICAL",
        "title": "KV 压力故障（KV PRESSURE INCIDENT）",
        "simulate": "远程 loadgen 压力从 1× 升至 6×（Remote loadgen pressure: 1× → 6×）",
        "healthy": "Gateway ✓ · EPP ✓ · Prefill 3/3 ✓ · Decode 2/2 ✓ · 5xx≈0",
        "observe": "TTFT↑、P waiting=14、KV hit=42%、arena=93%、GET=2.4s（KV pressure）",
    },
    "recovery": {
        "status": "HEALTHY",
        "title": "恢复验证（RECOVERY）",
        "simulate": "相同请求压力下清除 KV 故障（Clear the KV fault under the same demand）",
        "healthy": "Gateway ✓ → EPP ✓ → Prefill 3/3 ✓ → Decode 2/2 ✓",
        "observe": "P waiting→1、KV GET→100ms、eviction/no-space→0、TPM 恢复（Recovered）",
    },
    "load": {
        "status": "WARNING",
        "title": "请求压力（LOAD PRESSURE）",
        "simulate": "提高请求压力但不注入组件故障（Higher demand without component failure）",
        "change": "8× loadgen，拓扑保持 3P×2D（8× loadgen; fixed topology）",
        "healthy": "Gateway ✓ · EPP ✓ · vLLM path aligned · 5xx≈0",
        "observe": "TTFT↑ · Prefill waiting↑",
        "cause": "Demand approaches capacity / 请求到达率接近服务能力",
        "next": "make recovery",
    },
    "gateway_error": {
        "status": "CRITICAL",
        "title": "网关故障（GATEWAY FAILURE）",
        "simulate": "请求在进入 EPP 前被 Gateway 以 HTTP 503 拒绝（Gateway rejects before EPP）",
        "change": "6× loadgen；Gateway failure-status=503（Injected Gateway failure）",
        "healthy": "EPP/Prefill/Decode replay health remains available",
        "observe": "Gateway RPM/5xx↑ · EPP RPM≈0 · vLLM completed≈0",
        "cause": "Traffic stops at the first hop / 流量停在第一层",
        "next": "make evidence, then make recovery",
    },
    "vllm_error": {
        "status": "CRITICAL",
        "title": "模型服务故障（ENGINE FAILURE）",
        "simulate": "请求到达 EPP 后由 engine 返回 HTTP 503（Engine fails after EPP）",
        "change": "6× loadgen；simulator server-error=100%（Injected engine failure）",
        "healthy": "Gateway ✓ · EPP ✓",
        "observe": "Gateway≈EPP RPM · vLLM completed=0 · Output TPM=0",
        "cause": "The handoff succeeds, but the engine cannot complete / 模型服务是 owner",
        "next": "make evidence, then make recovery",
    },
    "gpu_error": {
        "status": "CRITICAL",
        "title": "GPU 故障回放（GPU FAILURE REPLAY）",
        "simulate": "请求路径仍成功但 GPU 设备退化（GPU degradation with a live request path）",
        "change": "6× loadgen；HTTP 保持成功；GPU 信号回放（Controlled GPU replay）",
        "healthy": "Gateway ✓ · EPP ✓ · request path remains aligned",
        "observe": "GPU util=18% · memory=95% · XID growth≈3/s · TTFT↑",
        "cause": "Device evidence changes while network drops stay flat / owner 收敛到 GPU",
        "next": "make evidence, then make recovery",
    },
    "prefill_pressure": {
        "status": "WARNING",
        "title": "Prefill 容量实验（PREFILL CAPACITY LAB）",
        "simulate": "可选的 P:D sizing 实验（Optional P:D sizing experiment）",
        "change": "8× loadgen；受控回放 2P×4D（Controlled 2P×4D replay）",
        "healthy": "Gateway ✓ · EPP ✓ · Decode waiting bounded",
        "observe": "arrival 18rps > service 10rps · Prefill waiting=14",
        "cause": "Service deficit predicts queue growth / 服务率缺口导致排队",
        "next": "make pd-tune",
    },
    "pd_tuned": {
        "status": "HEALTHY",
        "title": "P:D 验证实验（P:D VALIDATION LAB）",
        "simulate": "可选的受控 P:D profile 验证（Optional controlled profile validation）",
        "change": "8× loadgen 不变；回放 2P×4D→3P×3D（Fixed demand; profile replay）",
        "healthy": "Prefill waiting↓ · Decode waiting remains bounded",
        "observe": "service 20rps > arrival 18rps · TTFT↓",
        "cause": "One controlled action is checked against guardrails / 单变量验证",
        "next": "make pd-validation",
    },
}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("scenario", choices=tuple(SCENARIOS))
    parser.add_argument("--color", choices=("auto", "always", "never"), default="auto")
    args = parser.parse_args()

    palette = Palette(args.color)
    item = SCENARIOS[args.scenario]
    color = {
        "HEALTHY": palette.green,
        "WARNING": palette.yellow,
        "CRITICAL": palette.red,
    }[item["status"]]
    icon = {"HEALTHY": "✓", "WARNING": "!", "CRITICAL": "✗"}[item["status"]]

    print()
    print(palette.paint("╭────────────────────────────────────────────────────────────────────────────", color))
    print(palette.paint(f"│ {icon} {item['title']}", palette.bold + color))
    print(f"│ 模拟（Simulates）   : {item['simulate']}")
    if "change" in item:
        print(f"│ 变化（Change）     : {item['change']}")
    print(palette.paint(f"│ 正常（Healthy）    : {item['healthy']}", palette.green))
    print(palette.paint(f"│ 观察（Observe）    : {item['observe']}", color))
    print(palette.paint("╰────────────────────────────────────────────────────────────────────────────", color))


if __name__ == "__main__":
    main()
