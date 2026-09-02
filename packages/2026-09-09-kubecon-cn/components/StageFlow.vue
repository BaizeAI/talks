<script setup lang="ts">
interface Stage {
  id: string
  name: string
  sub?: string
  icon?: string
  metrics?: string[]
}
const props = defineProps<{ stages: Stage[], highlight?: string[], compact?: boolean }>()
function st(id: string) {
  if (!props.highlight?.length)
    return ''
  return props.highlight.includes(id) ? 'hot' : 'dim'
}
</script>

<template>
  <div class="sf" :class="{ compact }">
    <template v-for="(s, i) in stages" :key="s.id">
      <div class="sf-stage" :class="st(s.id)">
        <div v-if="s.icon" :class="s.icon" class="sf-icon" />
        <div class="sf-name">
          {{ s.name }}
        </div>
        <div v-if="s.sub" class="sf-sub">
          {{ s.sub }}
        </div>
        <div v-if="s.metrics?.length && !compact" class="sf-metrics">
          <span v-for="m in s.metrics" :key="m">{{ m }}</span>
        </div>
      </div>
      <div v-if="i < stages.length - 1" class="sf-arrow">
        <div i-carbon:chevron-right />
      </div>
    </template>
  </div>
</template>

<style scoped>
.sf { display: flex; align-items: stretch; gap: 3px; width: 100%; }
.sf-stage {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 3px;
  padding: 12px 10px;
  border: 1px solid #ffffff1e;
  border-radius: 11px;
  background: #ffffff08;
  transition: all 300ms ease;
}
.sf-icon { font-size: 21px; color: #b0ddff; }
.sf-name { font-size: 14.5px; font-weight: 600; color: #fffffff0; text-align: center; }
.sf-sub { font-size: 11px; opacity: 0.58; text-align: center; }
.sf-metrics {
  display: flex;
  flex-direction: column;
  gap: 2px;
  margin-top: 5px;
  align-items: center;
}
.sf-metrics span {
  font-size: 9.5px;
  font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
  opacity: 0.5;
  white-space: nowrap;
}
.sf-arrow {
  display: flex;
  align-items: center;
  color: #ffffff40;
  font-size: 16px;
  flex: none;
}
.sf-stage.hot {
  border-color: #ffc217;
  background: #ffc21716;
  box-shadow: 0 0 18px #ffc21733;
}
.sf-stage.hot .sf-name, .sf-stage.hot .sf-icon { color: #ffc217; }
.sf-stage.dim { opacity: 0.34; }

.sf.compact .sf-stage { padding: 7px 8px; border-radius: 8px; }
.sf.compact .sf-icon { font-size: 15px; }
.sf.compact .sf-name { font-size: 12px; }
.sf.compact .sf-sub { font-size: 9.5px; }
</style>
