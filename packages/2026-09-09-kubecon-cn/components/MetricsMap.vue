<script setup lang="ts">
const props = defineProps<{
  /** metric ids to highlight; empty/undefined = all shown normally */
  highlight?: string[]
  /** compact mode for use beside diagnosis cards */
  compact?: boolean
}>()

interface Metric { id: string, label: string, metric: string }
interface Layer { name: string, sub: string, icon: string, color: string, metrics: Metric[] }

const layers: Layer[] = [
  {
    name: 'Gateway / EPP',
    sub: '用户等多久',
    icon: 'i-carbon:gateway',
    color: '#b0ddff',
    metrics: [
      { id: 'ttft', label: 'TTFT p95', metric: 'llm_d_epp_request_ttft_seconds' },
      { id: 'qdepth', label: '池排队深度', metric: 'inference_pool_average_queue_size' },
      { id: 'err', label: '错误率', metric: 'llm_d_epp_request_error_total' },
    ],
  },
  {
    name: 'Prefill Engine',
    sub: 'compute-bound',
    icon: 'i-carbon:model-alt',
    color: '#2ee59d',
    metrics: [
      { id: 'p-wait', label: '等待队列', metric: 'vllm:num_requests_waiting' },
      { id: 'p-batch', label: '批次 token 数', metric: 'vllm:iteration_tokens_total' },
      { id: 'p-time', label: 'Prefill 耗时', metric: 'vllm:request_prefill_time_seconds' },
    ],
  },
  {
    name: 'Decode Engine',
    sub: 'memory-bound',
    icon: 'i-carbon:chat-bot',
    color: '#2ee59d',
    metrics: [
      { id: 'd-run', label: '在跑请求数', metric: 'vllm:num_requests_running' },
      { id: 'd-kv', label: 'KV 使用率', metric: 'vllm:kv_cache_usage_perc' },
      { id: 'd-preempt', label: '抢占次数', metric: 'vllm:num_preemptions_total' },
      { id: 'd-hit', label: '前缀命中率', metric: 'vllm:prefix_cache_hit_rate' },
    ],
  },
  {
    name: 'KV Transfer',
    sub: 'PD 分离独有',
    icon: 'i-carbon:data-share',
    color: '#ffa35f',
    metrics: [
      { id: 'net-lat', label: '传输耗时 p95', metric: 'agent_xfer_time_us' },
      { id: 'net-bw', label: '传输字节数', metric: 'agent_tx_bytes' },
      { id: 'net-err', label: '传输错误', metric: 'agent_errors_total' },
    ],
  },
  {
    name: 'GPU / Network',
    sub: '底座还好吗',
    icon: 'i-carbon:chip',
    color: '#ffc217',
    metrics: [
      { id: 'gpu-sm', label: 'GPU 利用率', metric: 'DCGM_FI_DEV_GPU_UTIL' },
      { id: 'gpu-mem', label: '显存占用', metric: 'DCGM_FI_DEV_FB_USED' },
      { id: 'net-drop', label: '丢包 / 重传', metric: 'container_network_*_dropped' },
    ],
  },
]

function state(id: string): 'normal' | 'hot' | 'dim' {
  if (!props.highlight?.length)
    return 'normal'
  return props.highlight.includes(id) ? 'hot' : 'dim'
}
</script>

<template>
  <div class="mmap" :class="{ compact }">
    <div v-for="layer in layers" :key="layer.name" class="mmap-row">
      <div class="mmap-label" :style="{ borderColor: `${layer.color}55` }">
        <div flex items-center gap-1.5>
          <div :class="layer.icon" :style="{ color: layer.color }" />
          <span font-semibold :style="{ color: layer.color }">{{ layer.name }}</span>
        </div>
        <span class="mmap-sub">{{ layer.sub }}</span>
      </div>
      <div class="mmap-chips">
        <div
          v-for="m in layer.metrics" :key="m.id"
          class="mmap-chip" :class="[state(m.id)]"
        >
          <span class="mmap-name">{{ m.label }}</span>
          <span class="mmap-metric">{{ m.metric }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.mmap {
  display: flex;
  flex-direction: column;
  gap: 8px;
  width: 100%;
}
.mmap-row {
  display: flex;
  align-items: stretch;
  gap: 10px;
}
.mmap-label {
  flex: 0 0 158px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  gap: 1px;
  padding: 6px 12px;
  border: 1px solid;
  border-radius: 8px;
  background: #ffffff08;
  font-size: 15px;
}
.mmap-sub {
  font-size: 11.5px;
  opacity: 0.55;
}
.mmap-chips {
  flex: 1;
  display: flex;
  gap: 8px;
}
.mmap-chip {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
  gap: 2px;
  padding: 6px 10px;
  border-radius: 8px;
  border: 1px solid #ffffff1c;
  background: #ffffff0a;
  transition: all 300ms ease;
  min-width: 0;
  overflow: hidden;
}
.mmap-name {
  font-size: 14px;
  font-weight: 600;
  color: #ffffffe8;
  white-space: nowrap;
}
.mmap-metric {
  font-size: 9.5px;
  letter-spacing: -0.15px;
  font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
  opacity: 0.5;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.mmap-chip.hot {
  border-color: #ffc217;
  background: #ffc21722;
  box-shadow: 0 0 14px #ffc21755;
}
.mmap-chip.hot .mmap-name {
  color: #ffc217;
}
.mmap-chip.hot .mmap-metric {
  opacity: 0.8;
  color: #ffe9ad;
}
.mmap-chip.dim {
  opacity: 0.28;
}

.mmap.compact {
  gap: 5px;
}
.mmap.compact .mmap-row {
  gap: 6px;
}
.mmap.compact .mmap-label {
  flex: 0 0 120px;
  padding: 4px 8px;
  font-size: 12px;
  border-radius: 6px;
}
.mmap.compact .mmap-sub {
  display: none;
}
.mmap.compact .mmap-chips {
  gap: 5px;
}
.mmap.compact .mmap-chip {
  padding: 4px 7px;
  border-radius: 6px;
  gap: 0;
}
.mmap.compact .mmap-name {
  font-size: 11.5px;
}
.mmap.compact .mmap-metric {
  display: none;
}
</style>
