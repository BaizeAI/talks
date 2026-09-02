<script setup lang="ts">
defineProps<{
  // fingerprint items, e.g. 'TTFT ↑'
  fingerprint: string[]
  cause: string
  actions: string[]
  verify: string
}>()
</script>

<template>
  <div class="dcard">
    <div class="dcard-row">
      <div class="dcard-tag" style="color: #ffc217; border-color: #ffc21766; background: #ffc21714">
        指纹
      </div>
      <div class="dcard-body">
        <span v-for="(f, i) in fingerprint" :key="i" class="dcard-chip">{{ f }}</span>
      </div>
    </div>
    <div class="dcard-row">
      <div class="dcard-tag" style="color: #ff6b6b; border-color: #ff6b6b66; background: #ff6b6b14">
        根因
      </div>
      <div class="dcard-body dcard-cause">
        {{ cause }}
      </div>
    </div>
    <div class="dcard-row">
      <div class="dcard-tag" style="color: #2ee59d; border-color: #2ee59d66; background: #2ee59d14">
        动作
      </div>
      <div class="dcard-body dcard-actions">
        <div v-for="(a, i) in actions" :key="i" class="dcard-action">
          <div i-carbon:arrow-right style="color: #2ee59d; font-size: 12px; flex: none; margin-top: 4px" />
          <span v-html="a" />
        </div>
      </div>
    </div>
    <div class="dcard-row">
      <div class="dcard-tag" style="color: #b0ddff; border-color: #b0ddff66; background: #b0ddff14">
        验证
      </div>
      <div class="dcard-body dcard-verify">
        {{ verify }}
      </div>
    </div>
  </div>
</template>

<style scoped>
.dcard {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 14px;
  border: 1px solid #ffffff1f;
  border-radius: 12px;
  background: #ffffff07;
}
.dcard-row {
  display: flex;
  align-items: flex-start;
  gap: 10px;
}
.dcard-tag {
  flex: 0 0 52px;
  text-align: center;
  padding: 3px 0;
  border: 1px solid;
  border-radius: 6px;
  font-size: 13px;
  font-weight: 600;
}
.dcard-body {
  flex: 1;
  display: flex;
  flex-wrap: wrap;
  gap: 5px;
  font-size: 14.5px;
  line-height: 1.45;
}
.dcard-chip {
  padding: 1px 9px;
  border-radius: 999px;
  border: 1px solid #ffc21744;
  background: #ffc2170f;
  font-size: 13.5px;
  color: #ffe9ad;
  white-space: nowrap;
}
.dcard-cause {
  color: #ffb3b3;
  font-weight: 500;
}
.dcard-actions {
  flex-direction: column;
  gap: 3px;
}
.dcard-action {
  display: flex;
  gap: 6px;
  align-items: flex-start;
  color: #d8f7e9;
}
.dcard-verify {
  color: #cfe7fa;
}
</style>
