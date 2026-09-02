<script setup lang="ts">
interface Step { no: string, name: string, detail: string }
defineProps<{ steps: Step[], keepIf: string, rollbackIf: string }>()
</script>

<template>
  <div class="ld">
    <div class="ld-row">
      <template v-for="(s, i) in steps" :key="s.no">
        <div class="ld-step">
          <div class="ld-no">
            {{ s.no }}
          </div>
          <div class="ld-name">
            {{ s.name }}
          </div>
          <div class="ld-detail" v-html="s.detail" />
        </div>
        <div v-if="i < steps.length - 1" class="ld-arrow">
          <div i-carbon:chevron-right />
        </div>
      </template>
    </div>

    <div class="ld-gate">
      <div class="ld-branch ld-keep">
        <div class="ld-bh">
          <div i-carbon:checkmark-filled />KEEP
        </div>
        <span v-html="keepIf" />
      </div>
      <div class="ld-branch ld-roll">
        <div class="ld-bh">
          <div i-carbon:undo />ROLLBACK
        </div>
        <span v-html="rollbackIf" />
      </div>
    </div>
  </div>
</template>

<style scoped>
.ld { width: 100%; }
.ld-row { display: flex; align-items: stretch; gap: 4px; }
.ld-step {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 3px;
  padding: 11px 12px;
  border: 1px solid #ffffff1e;
  border-radius: 11px;
  background: #ffffff07;
}
.ld-no {
  width: 22px;
  height: 22px;
  line-height: 22px;
  text-align: center;
  border-radius: 50%;
  background: #b0ddff22;
  color: #b0ddff;
  font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
  font-size: 11px;
  font-weight: 700;
}
.ld-name { font-size: 14.5px; font-weight: 600; color: #fffffff0; margin-top: 3px; }
.ld-detail { font-size: 11.5px; line-height: 1.5; opacity: 0.72; }
.ld-arrow {
  display: flex;
  align-items: center;
  color: #ffffff45;
  font-size: 17px;
  flex: none;
}
.ld-gate { display: flex; gap: 13px; margin-top: 13px; }
.ld-branch {
  flex: 1;
  padding: 11px 15px;
  border: 1px solid;
  border-radius: 11px;
  font-size: 13px;
  line-height: 1.5;
}
.ld-bh {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  font-weight: 700;
  letter-spacing: 0.05em;
  margin-bottom: 5px;
}
.ld-keep { border-color: #2ee59d3a; background: #2ee59d0c; }
.ld-keep .ld-bh { color: #2ee59d; }
.ld-roll { border-color: #ff6b6b3a; background: #ff6b6b0c; }
.ld-roll .ld-bh { color: #ff6b6b; }
</style>
