<script setup lang="ts">
import { computed } from 'vue'

interface Level {
  name: string
  sub: string
  value: number
  /** what this hop costs, i.e. previous level minus this one */
  deltaNote?: string
  hot?: boolean
}

const props = defineProps<{ levels: Level[], unit?: string }>()

const max = computed(() => Math.max(...props.levels.map(l => l.value)))

function delta(i: number) {
  if (i === 0)
    return null
  return props.levels[i - 1].value - props.levels[i].value
}
</script>

<template>
  <div class="ll">
    <div v-for="(l, i) in levels" :key="l.name" class="ll-row" :class="{ hot: l.hot }">
      <div class="ll-label">
        <div class="ll-name">
          {{ l.name }}
        </div>
        <div class="ll-sub">
          {{ l.sub }}
        </div>
      </div>

      <div class="ll-track">
        <div class="ll-bar" :style="{ width: `${(l.value / max) * 100}%` }" />
      </div>

      <div class="ll-val">
        {{ l.value.toLocaleString() }} {{ unit ?? 'ms' }}
      </div>

      <div class="ll-delta">
        <template v-if="delta(i) !== null">
          <span class="ll-dnum">+{{ delta(i)!.toLocaleString() }}</span>
          <span class="ll-dnote">{{ l.deltaNote }}</span>
        </template>
        <span v-else class="ll-dnote ll-first">用户实际感受</span>
      </div>
    </div>
  </div>
</template>

<style scoped>
.ll {
  display: flex;
  flex-direction: column;
  gap: 7px;
  width: 100%;
}
.ll-row {
  display: flex;
  align-items: center;
  gap: 12px;
}
.ll-label {
  flex: 0 0 168px;
}
.ll-name {
  font-size: 15px;
  font-weight: 600;
  color: #ffffffe6;
}
.ll-sub {
  font-size: 10.5px;
  opacity: 0.5;
  font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.ll-track {
  flex: 1;
  height: 28px;
  border-radius: 7px;
  background: #ffffff08;
  border: 1px solid #ffffff12;
  overflow: hidden;
}
.ll-bar {
  height: 100%;
  min-width: 4px;
  border-radius: 6px;
  background: linear-gradient(90deg, #b0ddff33, #b0ddff66);
  border-right: 2px solid #b0ddff;
  transition: width 400ms ease;
}
.ll-val {
  flex: 0 0 78px;
  text-align: right;
  font-size: 13px;
  font-weight: 600;
  font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
  color: #ffffffdd;
  white-space: nowrap;
}
.ll-delta {
  flex: 0 0 218px;
  display: flex;
  align-items: baseline;
  gap: 7px;
}
.ll-dnum {
  font-size: 14.5px;
  font-weight: 700;
  font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
  color: #ffffffaa;
}
.ll-dnote {
  font-size: 12.5px;
  opacity: 0.7;
  line-height: 1.3;
}
.ll-first {
  opacity: 0.45;
}

.ll-row.hot .ll-bar {
  background: linear-gradient(90deg, #2ee59d2e, #2ee59d5c);
  border-right-color: #2ee59d;
}
.ll-row.hot .ll-dnum {
  color: #ff6b6b;
  font-size: 17px;
}
.ll-row.hot .ll-dnote {
  color: #ff9b9b;
  opacity: 1;
  font-weight: 600;
}
</style>
