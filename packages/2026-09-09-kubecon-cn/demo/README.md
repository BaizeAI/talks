# macOS + kind：PD 分离推理故障诊断 Demo

这套 Demo 服务于 KubeCon 主题“Why Your TTFT Lies”：先从运营视角确认推理服务是否持续交付 token，再沿 Gateway、EPP、Prefill / Decode、KV / NIXL、GPU 一层层定位 fault owner。

默认拓扑固定为 **3P × 2D**，所有主场景都不改变 P:D。这个比例只是为了让 Mac 上的演示同时具有 Prefill 和 Decode 冗余，不代表生产最优解；生产比例必须根据输入/输出长度、并发、KV 容量和硬件 benchmark 决定。

```text
loadgen → gateway-demo → epp-demo → llm-d-inference-sim
              │              │                 │
       request/status    handoff/RPM       vllm:* / TPM
              └──────────────┴─────────────────┴→ Prometheus → Grafana
scenario controller → telemetry replay → P/D、KV/NIXL、GPU、network
```

## 数据边界

- **实测**：请求真实经过 `gateway-demo → epp-demo → inference-sim`；请求数、RPM、HTTP 状态码、Input/Output TPM、client error、TTFT 与 simulator queue 来自实际流量。
- **受控回放**：Mac 没有 GPU/RDMA，也没有真正的 3P×2D worker；P/D 健康、KV、NIXL、GPU 和网络信号使用 `kubecon_*{signal_source="simulated"}`。
- Gateway/EPP 是轻量代理，用来保持请求边界真实一致，不冒充 Istio/kgateway 或 llm-d EPP 的生产实现。
- 默认不安装真正的 Istio/kgateway、LMCache、NIXL、RDMA 或 vLLM GPU runtime，保证现场可重复性。

## 启动

需要 Docker Desktop、`kind`、`kubectl`、`python3`、`curl`，并确保本机 `3000`、`8000`、`9090` 端口可用。

```bash
cd packages/2026-09-09-kubecon-cn/demo
make up
make baseline-test
make open-dashboard
```

- Grafana：<http://127.0.0.1:3000/d/inferx-model-ops-ppt-demo?orgId=1&refresh=5s>
- Prometheus：<http://127.0.0.1:9090>
- OpenAI-compatible API：<http://127.0.0.1:8000/v1/chat/completions>

重复演示前无需重建 kind。执行下面的命令会暂停 loadgen、重启使用 `emptyDir` 的 Prometheus 以清空历史 TSDB，然后启动 1× loadgen 的全新 baseline：

```bash
make reset-metrics
```

`baseline-test` 默认等待 35 秒，让高压场景留下的在途请求和 20 秒指标窗口充分排空。可用 `BASELINE_WAIT_SECONDS=45 make baseline-test` 调整。`reset-metrics` 可用 `RESET_METRICS_WAIT_SECONDS=8 make reset-metrics` 调整等待时间；Grafana Dashboard 与配置不会被删除。

## 主演示：固定 3P×2D 的故障闭环

```bash
make baseline
make incident
make evidence
make recovery
make status
```

`incident` 与 `recovery` 都保持 6 个 loadgen，恢复不能用“降低流量”解释。切换场景后等待约 20 秒，让 Grafana 的 20 秒 rate window 稳定。

`baseline`、`incident`、`recovery` 会先打印中英文场景卡：`Control / 控制变量` 表示保持不变的条件，`Action / 改变变量` 表示本次真正注入或清除的变量，绿色 `Healthy / 正常` 表示应保持健康的反证指标。

### 1. Entry：服务还在交付 token 吗？

先看请求数/RPM、2xx/4xx/5xx、Input/Output TPM、TTFT 和 client error。`incident` 中 Gateway → EPP → vLLM 仍贯通、5xx 接近 0，但 TTFT 上升，因此这不是入口中断。

### 2. Localize：哪一层先异常？

Route 与 EPP queue 保持正常；Prefill waiting 明显上升，Decode waiting 仍低；KV hit ratio 下降、arena 使用率和 GET p99 上升。异常边界从 Gateway/EPP 收敛到 Prefill/KV。

### 3. Evidence：谁拥有这个故障？

`make evidence` 会自动识别当前场景并输出彩色分层健康报告。每一行显示当前值、健康阈值和健康/告警状态。Dashboard 同时显示 eviction、remote no-space、swap 上升，而 Gateway/vLLM/GPU/network fault rate 保持平稳，形成 KV/cache owner 的证据与反证。

### 4. Recovery：同一负载下恢复了吗？

3P×2D 与 6 个 loadgen 不变；TTFT、Prefill waiting、KV GET/eviction/no-space 回落，Output TPM 与完成 RPM 恢复。关单条件是持续交付 token，而不是单个 panel 变绿。

## 同一面板下的其他故障指纹

每个场景都保持固定 3P×2D，只改变故障信号：

| 命令 | 请求路径与主要变化 | 定位结论 |
|---|---|---|
| `make load` | 三层 RPM 对齐，5xx≈0，TTFT/queue 上升 | 纯压力或容量问题 |
| `make gateway-error` | Gateway 有请求和 503，EPP/vLLM RPM≈0 | Gateway owner |
| `make vllm-error` | Gateway≈EPP，vLLM completed/TPM≈0，client error 上升 | engine/vLLM owner |
| `make gpu-error` | 请求贯通但 TTFT 变差；XID rate 上升，network flat | GPU/device owner（回放） |
| `make incident` | 请求贯通；Prefill waiting、KV GET、eviction/no-space 上升 | KV/cache 或 Prefill owner（回放） |

查看指定故障的相关事件：

```bash
make evidence SCENARIO=gateway_error
make evidence SCENARIO=vllm_error
make evidence SCENARIO=gpu_error
```

默认仅在终端中启用颜色；重定向输出时可以显式控制：

```bash
EVIDENCE_COLOR=always make evidence  # 重定向时仍强制保留颜色
EVIDENCE_COLOR=never make evidence   # 无 ANSI 颜色
SCENARIO_COLOR=never make recovery   # 场景卡无颜色
```

累计 error counter 代表历史；判断“当前是否还在坏”应看 rate 是否继续增长。

## Dashboard 结构

1. **Entry**：请求量、状态码、TPM、TTFT、Gateway/EPP/P/D 健康数量；
2. **Localize**：请求路径、Route/EPP、Prefill/Decode waiting、KV/NIXL；
3. **Evidence**：HTTP outcomes、KV failure proof、GPU/infra、分层 error rate；
4. **Recovery**：同一拓扑与同一请求压力下，路径、SLO、token delivery 是否恢复。

## 可选：P:D 调优实验

以下命令保留用于讲 benchmark 方法，不属于默认故障故事：

```bash
make prefill-pressure
make pd-tune
make pd-validation
```

其中 P:D profile 是受控回放，不能作为生产 sizing 结论。公开案例也没有统一比例：NVIDIA Dynamo 示例为 3P+4D；llm-d 的长上下文 TPU 案例在特定 workload 下为 2P:6D。两者都强调按 Prefill/Decode 各自瓶颈独立 sizing。

## 常用检查与清理

```bash
make request
make status
kubectl --context kind-ppt-demo -n ppt-demo logs deployment/inference-sim -f
```

```bash
make down          # 删除 ppt-demo namespace
make down-cluster  # 删除专用 kind 集群
```

## 来源

- [llm-d inference simulator](https://github.com/llm-d/llm-d-inference-sim)
- [llm-d PD disaggregation architecture](https://github.com/llm-d/llm-d/blob/main/docs/architecture/advanced/disaggregation/README.md)
- [NVIDIA Dynamo disaggregated serving](https://docs.nvidia.com/dynamo/dev/kubernetes/disaggregated-serving/overview)
- [llm-d Qwen3 Coder 480B TPU sizing case](https://github.com/llm-d/llm-d/blob/main/guides/agentic-serving/qwen3-coder-480b-tpu.md)
- [Istio standard metrics](https://istio.io/latest/docs/reference/config/metrics/)
- [kgateway Envoy metrics](https://kgateway.dev/docs/envoy/latest/observability/gateway-metrics/)
