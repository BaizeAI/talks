<script setup lang="ts">
interface Seg { name: string, value: number, color: string }
interface Scenario {
  title: string
  segs: Seg[]
  cause: string
  action: string
  wrong: string
}

defineProps<{ scenarios: Scenario[], unit?: string }>()

function total(segs: Seg[]) {
  return segs.reduce((a, b) => a + b.value, 0)
}
</script>

<template>
  <div class="tb">
    <div v-for="s in scenarios" :key="s.title" class="tb-col">
      <div class="tb-title">
        {{ s.title }}
      </div>

      <div class="tb-bar">
        <div
          v-for="seg in s.segs" :key="seg.name"
          class="tb-seg"
          :style="{ flexGrow: seg.value, background: seg.color }"
          :title="`${seg.name} ${seg.value}`"
        />
      </div>

      <div class="tb-legend">
        <div v-for="seg in s.segs" :key="seg.name" class="tb-item" :class="{ dominant: seg.value / total(s.segs) > 0.5 }">
          <span class="tb-dot" :style="{ background: seg.color }" />
          <span class="tb-name">{{ seg.name }}</span>
          <span class="tb-val">{{ seg.value }}{{ unit ?? 'ms' }}</span>
        </div>
      </div>

      <div class="tb-cause">
        <span class="tb-tag">根因</span>{{ s.cause }}
      </div>
      <div class="tb-action">
        <span class="tb-tag tb-tag-do">动作</span>{{ s.action }}
      </div>
      <div class="tb-wrong">
        <div i-carbon:close-outline style="flex: none; margin-top: 3px" />
        <span>{{ s.wrong }}</span>
      </div>
    </div>
  </div>
</template>

<style scoped>
.tb {
  display: flex;
  gap: 16px;
  width: 100%;
}
.tb-col {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 14px;
  border: 1px solid #ffffff1c;
  border-radius: 12px;
  background: #ffffff07;
  min-width: 0;
}
.tb-title {
  font-size: 17px;
  font-weight: 600;
  color: #ffffffe8;
}
.tb-bar {
  display: flex;
  height: 26px;
  border-radius: 6px;
  overflow: hidden;
  gap: 1px;
}
.tb-seg {
  min-width: 3px;
  transition: all 300ms ease;
}
.tb-legend {
  display: flex;
  flex-direction: column;
  gap: 2px;
}
.tb-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  opacity: 0.6;
}
.tb-item.dominant {
  opacity: 1;
  font-weight: 600;
}
.tb-dot {
  width: 9px;
  height: 9px;
  border-radius: 2px;
  flex: none;
}
.tb-name {
  flex: 1;
}
.tb-val {
  font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
  font-size: 12.5px;
}
.tb-cause,
.tb-action {
  display: flex;
  align-items: flex-start;
  gap: 7px;
  font-size: 14px;
  line-height: 1.4;
}
.tb-cause {
  color: #ffb3b3;
}
.tb-action {
  color: #b9f4d9;
}
.tb-tag {
  flex: none;
  padding: 0 7px;
  border-radius: 5px;
  font-size: 12px;
  font-weight: 600;
  border: 1px solid #ff6b6b55;
  background: #ff6b6b14;
  color: #ff9b9b;
}
.tb-tag-do {
  border-color: #2ee59d55;
  background: #2ee59d14;
  color: #2ee59d;
}
.tb-wrong {
  display: flex;
  gap: 5px;
  font-size: 12.5px;
  color: #ffc217;
  opacity: 0.85;
  line-height: 1.35;
  margin-top: auto;
  padding-top: 6px;
  border-top: 1px dashed #ffffff1a;
}
</style>
