<script setup lang="ts">
const props = defineProps<{
  /** group keys to highlight */
  highlight?: string[]
  compact?: boolean
  /** stack the four groups as rows — fits a narrow side column */
  vertical?: boolean
}>()

interface Sig { id: string, label: string, metric: string }
interface Group { no: string, name: string, ask: string, icon: string, color: string, sigs: Sig[] }

const groups: Group[] = [
  {
    no: '01',
    name: 'HEALTH',
    ask: 'Can we accept traffic?',
    icon: 'i-carbon:health-cross',
    color: '#b0ddff',
    sigs: [
      { id: 'ready', label: 'ready endpoints', metric: 'llm_d_epp_ready_endpoints' },
      { id: 'err', label: 'error / timeout rate', metric: 'llm_d_epp_request_error_total' },
    ],
  },
  {
    no: '02',
    name: 'LOAD',
    ask: 'How much work arrived?',
    icon: 'i-carbon:traffic-flow',
    color: '#2ee59d',
    sigs: [
      { id: 'rps', label: 'requests / s', metric: 'rate(vllm:request_success_total)' },
      { id: 'tpm', label: 'input / output tok/s', metric: 'vllm:*_tokens_total' },
    ],
  },
  {
    no: '03',
    name: 'USER SLO',
    ask: 'How long do users wait?',
    icon: 'i-carbon:user-multiple',
    color: '#ffc217',
    sigs: [
      { id: 'ttft', label: 'TTFT p95 / p99', metric: 'vllm:time_to_first_token_seconds' },
      { id: 'tpot', label: 'TPOT p95 / p99', metric: 'vllm:time_per_output_token_seconds' },
    ],
  },
  {
    no: '04',
    name: 'PD STAGE',
    ask: 'Which stage owns it?',
    icon: 'i-carbon:flow',
    color: '#ffa35f',
    sigs: [
      { id: 'pwait', label: 'Prefill waiting', metric: 'vllm:num_requests_waiting{role=P}' },
      { id: 'dwait', label: 'Decode waiting', metric: 'vllm:num_requests_waiting{role=D}' },
    ],
  },
]

function st(id: string) {
  if (!props.highlight?.length)
    return ''
  return props.highlight.includes(id) ? 'hot' : 'dim'
}
</script>

<template>
  <div class="es" :class="{ compact, vertical }">
    <div v-for="g in groups" :key="g.no" class="es-col" :style="{ borderColor: `${g.color}3a` }">
      <div class="es-head">
        <span class="es-no" :style="{ color: g.color }">{{ g.no }}</span>
        <div :class="g.icon" :style="{ color: g.color }" />
        <span class="es-name" :style="{ color: g.color }">{{ g.name }}</span>
      </div>
      <div v-if="!compact && !vertical" class="es-ask">
        {{ g.ask }}
      </div>
      <div class="es-sigs">
        <div v-for="s in g.sigs" :key="s.id" class="es-sig" :class="st(s.id)">
          <span class="es-label">{{ s.label }}</span>
          <span v-if="!compact && !vertical" class="es-metric">{{ s.metric }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.es { display: flex; gap: 12px; width: 100%; }
.es-col {
  flex: 1;
  min-width: 0;
  padding: 12px 14px;
  border: 1px solid;
  border-radius: 12px;
  background: #ffffff07;
}
.es-head { display: flex; align-items: center; gap: 7px; }
.es-no {
  font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
  font-size: 13px;
  font-weight: 700;
  opacity: 0.75;
}
.es-name { font-size: 14.5px; font-weight: 700; letter-spacing: 0.04em; }
.es-ask { font-size: 12.5px; opacity: 0.6; margin-top: 4px; }
.es-sigs { display: flex; flex-direction: column; gap: 7px; margin-top: 10px; }
.es-sig {
  display: flex;
  flex-direction: column;
  gap: 2px;
  padding: 7px 10px;
  border-radius: 8px;
  border: 1px solid #ffffff18;
  background: #ffffff09;
  transition: all 300ms ease;
  min-width: 0;
}
.es-label { font-size: 13.5px; font-weight: 600; color: #ffffffe8; white-space: nowrap; }
.es-metric {
  font-size: 9.5px;
  letter-spacing: -0.2px;
  font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
  opacity: 0.45;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.es-sig.hot {
  border-color: #ffc217;
  background: #ffc21722;
  box-shadow: 0 0 14px #ffc21744;
}
.es-sig.hot .es-label { color: #ffc217; }
.es-sig.dim { opacity: 0.3; }

.es.compact { gap: 7px; }
.es.compact .es-col { padding: 7px 9px; border-radius: 8px; }
.es.compact .es-name { font-size: 11.5px; }
.es.compact .es-sigs { gap: 4px; margin-top: 6px; }
.es.compact .es-sig { padding: 4px 7px; border-radius: 6px; }
.es.compact .es-label { font-size: 11px; }

/* vertical: four groups stacked as rows, for narrow side columns */
.es.vertical {
  flex-direction: column;
  gap: 6px;
}
.es.vertical .es-col {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 6px 11px;
  border-radius: 9px;
}
.es.vertical .es-head { flex: 0 0 112px; }
.es.vertical .es-name { font-size: 12.5px; }
.es.vertical .es-sigs {
  flex-direction: row;
  flex-wrap: wrap;
  gap: 5px;
  margin-top: 0;
  flex: 1;
}
.es.vertical .es-sig { padding: 3px 9px; border-radius: 6px; }
.es.vertical .es-label { font-size: 11.5px; white-space: normal; }
</style>
