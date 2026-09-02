<script setup lang="ts">
defineProps<{
  saw?: string
  meant?: string
  changed: string
  verified: string
  /** optional rollback / escalate condition, shown under 'verified' */
  rollback?: string
}>()
</script>

<template>
  <div class="cs">
    <div v-if="saw" class="cs-row">
      <div class="cs-k" style="--c: #b0ddff">SAW</div>
      <div class="cs-v" v-html="saw" />
    </div>
    <div v-if="meant" class="cs-row">
      <div class="cs-k" style="--c: #ffc217">MEANT</div>
      <div class="cs-v" v-html="meant" />
    </div>
    <div class="cs-row">
      <div class="cs-k" style="--c: #2ee59d">CHANGED</div>
      <div class="cs-v" v-html="changed" />
    </div>
    <div class="cs-row">
      <div class="cs-k" style="--c: #ffa35f">VERIFIED</div>
      <div class="cs-v">
        <span v-html="verified" />
        <div v-if="rollback" class="cs-rb">
          <div i-carbon:undo style="color: #ff6b6b; flex: none; margin-top: 2px" />
          <span v-html="rollback" />
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.cs { display: flex; flex-direction: column; gap: 6px; }
.cs-row {
  display: flex;
  gap: 11px;
  padding: 8px 13px;
  border: 1px solid #ffffff1c;
  border-radius: 11px;
  background: #ffffff07;
}
.cs-k {
  flex: 0 0 78px;
  align-self: flex-start;
  padding: 3px 0;
  border-radius: 6px;
  text-align: center;
  border: 1px solid color-mix(in srgb, var(--c) 45%, transparent);
  background: color-mix(in srgb, var(--c) 13%, transparent);
  color: var(--c);
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.06em;
}
.cs-v { flex: 1; font-size: 13px; line-height: 1.5; opacity: 0.92; }
.cs-v :deep(code) { font-size: 12px; padding: 1px 5px; border-radius: 4px; background: #ffffff14; }
.cs-rb {
  display: flex;
  gap: 7px;
  margin-top: 6px;
  padding-top: 6px;
  border-top: 1px dashed #ffffff1f;
  font-size: 12px;
  color: #ffb3b3;
}
</style>
