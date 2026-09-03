#!/usr/bin/env bash
set -euo pipefail

CLUSTER_NAME="${PPT_DEMO_CLUSTER:-ppt-demo}"
CONTEXT="kind-${CLUSTER_NAME}"
NAMESPACE="ppt-demo"

kubectl --context "$CONTEXT" -n "$NAMESPACE" get pods -o wide
echo
echo -n "Active loadgen replicas: "
kubectl --context "$CONTEXT" -n "$NAMESPACE" get deployment/loadgen \
  -o jsonpath='{.status.readyReplicas}/{.spec.replicas}{"\n"}'
echo
echo "Prometheus targets:"
curl --silent --fail 'http://127.0.0.1:9090/api/v1/targets?state=active' | \
  python3 -c 'import json,sys; data=json.load(sys.stdin); [print("  {}: {}".format(x["labels"].get("job"), x["health"])) for x in data["data"]["activeTargets"]]'
echo
echo "Active scenario:"
kubectl --context "$CONTEXT" -n "$NAMESPACE" exec deployment/telemetry-replay -- \
  python3 -c "import urllib.request; print(urllib.request.urlopen('http://127.0.0.1:9108/control').read().decode())"
echo
echo "Dashboard signals:"
python3 - <<'PY'
import json
import urllib.parse
import urllib.request

queries = {
    "fixed PD topology (Prefill replicas)": 'kubecon_pd_prefill_replicas{model="demo-model"}',
    "fixed PD topology (Decode replicas)": 'kubecon_pd_decode_replicas{model="demo-model"}',
    "Gateway healthy / desired": 'kubecon_gateway_healthy_replicas / clamp_min(kubecon_gateway_desired_replicas, 1)',
    "EPP healthy / desired": 'kubecon_epp_healthy_replicas / clamp_min(kubecon_epp_desired_replicas, 1)',
    "Prefill healthy / desired": 'kubecon_pd_prefill_healthy_replicas{model="demo-model"} / clamp_min(kubecon_pd_prefill_replicas{model="demo-model"}, 1)',
    "Decode healthy / desired": 'kubecon_pd_decode_healthy_replicas{model="demo-model"} / clamp_min(kubecon_pd_decode_replicas{model="demo-model"}, 1)',
    "gateway total requests": 'sum(ppt_demo_proxy_requests_total{role="gateway",model="demo-model"})',
    "gateway RPM (20s rolling)": 'sum(rate(ppt_demo_proxy_requests_total{role="gateway",model="demo-model"}[20s])) * 60',
    "EPP RPM (20s rolling)": 'sum(rate(ppt_demo_proxy_requests_total{role="epp",model="demo-model"}[20s])) * 60',
    "vLLM completed RPM (20s rolling)": 'sum(rate(vllm:request_success_total{model_name="demo-model"}[20s])) * 60',
    "gateway 2xx total": 'sum(ppt_demo_proxy_requests_total{role="gateway",model="demo-model",status_class="2xx"})',
    "gateway 4xx total": '(sum(ppt_demo_proxy_requests_total{role="gateway",model="demo-model",status_class="4xx"}) or vector(0))',
    "gateway 5xx total": '(sum(ppt_demo_proxy_requests_total{role="gateway",model="demo-model",status_class="5xx"}) or vector(0))',
    "input TPM (20s rolling)": 'sum(rate(vllm:prompt_tokens_total{model_name="demo-model"}[20s])) * 60',
    "output TPM (20s rolling)": 'sum(rate(vllm:generation_tokens_total{model_name="demo-model"}[20s])) * 60',
    "measured TTFT p95": 'histogram_quantile(0.95, sum by (le) (rate(vllm:time_to_first_token_seconds_bucket{model_name="demo-model"}[20s])))',
    "measured waiting": 'sum(vllm:num_requests_waiting{model_name="demo-model"})',
    "replayed Prefill waiting": 'kubecon_vllm_prefill_waiting{model="demo-model"}',
    "replayed Decode waiting": 'kubecon_vllm_decode_waiting{model="demo-model"}',
    "replayed Prefill arrival rps": 'kubecon_pd_prefill_arrival_rate_rps{model="demo-model"}',
    "replayed Prefill service rps": 'kubecon_pd_prefill_service_rate_rps{model="demo-model"}',
    "measured client error rate (20s rolling)": 'sum(rate(ppt_demo_client_requests_total{model="demo-model",status_class=~"4xx|5xx|transport"}[20s])) / clamp_min(sum(rate(ppt_demo_client_requests_total{model="demo-model"}[20s])), 0.001)',
    "simulated KV hit ratio": 'kubecon_kv_cache_hit_ratio{model="demo-model"}',
    "simulated KV arena usage": 'kubecon_kv_cache_usage_ratio{model="demo-model"}',
    "simulated KV GET p99": 'kubecon_kv_get_p99_seconds{model="demo-model"}',
    "simulated KV evictions/s": 'kubecon_kv_evictions_per_second{model="demo-model"}',
    "simulated KV remote no-space/s": 'kubecon_kv_remote_no_space_per_second{model="demo-model"}',
    "simulated KV transfer MB/s": 'kubecon_kv_transfer_bytes_per_second{model="demo-model"} / 1000000',
    "simulated GPU utilization": 'kubecon_gpu_utilization_percent{model="demo-model"}',
    "simulated GPU memory used": 'kubecon_gpu_memory_used_ratio{model="demo-model"}',
    "simulated network drops/s": 'kubecon_network_drops_per_second{model="demo-model"}',
    "gateway replay error rate": 'kubecon_gateway_error_rate{model="demo-model"}',
    "vLLM replay error rate": 'kubecon_vllm_error_rate{model="demo-model"}',
    "GPU replay error rate": 'kubecon_gpu_error_rate{model="demo-model"}',
    "gateway errors growing/s": 'rate(kubecon_gateway_errors_total{model="demo-model"}[20s])',
    "vLLM errors growing/s": 'rate(kubecon_vllm_errors_total{model="demo-model"}[20s])',
    "GPU XID growing/s": 'rate(kubecon_gpu_xid_errors_total{model="demo-model"}[20s])',
}
for label, query in queries.items():
    url = "http://127.0.0.1:9090/api/v1/query?" + urllib.parse.urlencode({"query": query})
    result = json.load(urllib.request.urlopen(url))["data"]["result"]
    value = result[0]["value"][1] if result else "warming-up"
    print(f"  {label}: {value}")
PY
