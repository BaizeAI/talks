<script setup lang="ts">
interface Dim {
  no: string
  name: string
  ask?: string
  signals: string[]
  note: string
}
withDefaults(defineProps<{
  dims: Dim[]
  accent?: string
  /** one-line conclusion strip under the three cards */
  bottom?: string
}>(), { accent: '#2ee59d' })
</script>

<template>
  <div class="pt">
    <div class="pt-row">
      <div
        v-for="d in dims" :key="d.no" class="pt-card"
        :style="{ borderColor: `${accent}33` }"
      >
        <div class="pt-head">
          <span class="pt-no" :style="{ background: `${accent}1f`, color: accent }">{{ d.no }}</span>
          <div class="pt-titles">
            <span class="pt-name">{{ d.name }}</span>
            <span v-if="d.ask" class="pt-ask">{{ d.ask }}</span>
          </div>
        </div>
        <div class="pt-sigs">
          <span v-for="s in d.signals" :key="s" class="pt-sig">{{ s }}</span>
        </div>
        <div class="pt-note" v-html="d.note" />
      </div>
    </div>
    <div v-if="bottom" class="pt-bottom" :style="{ borderColor: `${accent}3a`, background: `${accent}0d` }">
      <div i-carbon:arrow-right :style="{ color: accent, flex: 'none' }" />
      <span v-html="bottom" />
    </div>
  </div>
</template>

<style scoped>
.pt { width: 100%; }
.pt-row { display: flex; gap: 13px; align-items: stretch; }
.pt-card {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  padding: 13px 15px;
  border: 1px solid;
  border-radius: 12px;
  background: #ffffff07;
}
.pt-head { display: flex; align-items: flex-start; gap: 9px; }
.pt-no {
  flex: none;
  width: 25px;
  height: 25px;
  line-height: 25px;
  text-align: center;
  border-radius: 7px;
  font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
  font-size: 12px;
  font-weight: 700;
}
.pt-titles { display: flex; flex-direction: column; gap: 1px; min-width: 0; }
.pt-name { font-size: 15.5px; font-weight: 600; color: #fffffff0; line-height: 1.25; }
.pt-ask { font-size: 12px; opacity: 0.58; }
.pt-sigs { display: flex; flex-wrap: wrap; gap: 5px; margin-top: 10px; }
.pt-sig {
  padding: 2px 9px;
  border-radius: 999px;
  border: 1px solid #ffffff20;
  background: #ffffff0b;
  font-size: 11.5px;
  font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
  color: #ffffffcc;
  white-space: nowrap;
}
.pt-note {
  margin-top: 10px;
  padding-top: 9px;
  border-top: 1px dashed #ffffff1c;
  font-size: 12.5px;
  line-height: 1.55;
  opacity: 0.85;
}
.pt-bottom {
  display: flex;
  align-items: flex-start;
  gap: 9px;
  margin-top: 13px;
  padding: 11px 16px;
  border: 1px solid;
  border-radius: 11px;
  font-size: 14px;
  line-height: 1.5;
}
</style>
