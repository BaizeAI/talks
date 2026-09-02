<script setup lang="ts">
interface Seg { label: string, value: number, color: string }
interface Row { name: string, sub?: string, segs: Seg[], bad?: boolean }
withDefaults(defineProps<{ rows: Row[], max: number, unit?: string }>(), { unit: '×' })

function total(r: Row) {
  return r.segs.reduce((a, s) => a + s.value, 0)
}
</script>

<template>
  <div class="cb">
    <div v-for="r in rows" :key="r.name" class="cb-row">
      <div class="cb-label">
        <div class="cb-name" :class="{ bad: r.bad }">
          {{ r.name }}
        </div>
        <div v-if="r.sub" class="cb-sub">
          {{ r.sub }}
        </div>
      </div>
      <div class="cb-track">
        <div
          v-for="s in r.segs" :key="s.label"
          class="cb-seg"
          :style="{ width: `${(s.value / max) * 100}%`, background: s.color }"
        >
          <span v-if="(s.value / max) > 0.14" class="cb-seglab">{{ s.label }}</span>
        </div>
      </div>
      <div class="cb-total" :class="{ bad: r.bad }">
        {{ total(r).toFixed(1) }}{{ unit }}
      </div>
    </div>
  </div>
</template>

<style scoped>
.cb { display: flex; flex-direction: column; gap: 11px; width: 100%; }
.cb-row { display: flex; align-items: center; gap: 12px; }
.cb-label { flex: 0 0 158px; }
.cb-name { font-size: 14.5px; font-weight: 600; color: #ffffffe6; }
.cb-name.bad { color: #ff8f8f; }
.cb-sub { font-size: 11px; opacity: 0.52; }
.cb-track {
  flex: 1;
  display: flex;
  height: 34px;
  border-radius: 8px;
  background: #ffffff08;
  border: 1px solid #ffffff14;
  overflow: hidden;
}
.cb-seg {
  height: 100%;
  display: flex;
  align-items: center;
  padding-left: 10px;
  transition: width 400ms ease;
  overflow: hidden;
}
.cb-seglab {
  font-size: 11.5px;
  font-weight: 600;
  color: #0d2b23;
  white-space: nowrap;
}
.cb-total {
  flex: 0 0 58px;
  text-align: right;
  font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
  font-size: 15px;
  font-weight: 700;
  color: #ffffffdd;
}
.cb-total.bad { color: #ff6b6b; }
</style>
