<script setup lang="ts">
interface Rank { name: string, value: number, sub?: string, bad?: boolean }
withDefaults(defineProps<{ ranks: Rank[], unit?: string, height?: number }>(), { unit: '%', height: 150 })
</script>

<template>
  <div class="rb">
    <div class="rb-plot" :style="{ height: `${height}px` }">
      <div v-for="r in ranks" :key="r.name" class="rb-col">
        <div class="rb-val" :class="{ bad: r.bad }">
          {{ r.value }}{{ unit }}
        </div>
        <div class="rb-track">
          <div class="rb-bar" :class="{ bad: r.bad }" :style="{ height: `${r.value}%` }" />
        </div>
        <div class="rb-name" :class="{ bad: r.bad }">
          {{ r.name }}
        </div>
        <div v-if="r.sub" class="rb-sub">
          {{ r.sub }}
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.rb { width: 100%; }
.rb-plot { display: flex; gap: 14px; align-items: flex-end; }
.rb-col { flex: 1; display: flex; flex-direction: column; height: 100%; }
.rb-val {
  font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
  font-size: 14px;
  font-weight: 700;
  color: #ffffffdd;
  text-align: center;
  margin-bottom: 4px;
}
.rb-val.bad { color: #ff6b6b; font-size: 17px; }
.rb-track {
  flex: 1;
  display: flex;
  align-items: flex-end;
  border-radius: 8px;
  background: #ffffff0a;
  border: 1px solid #ffffff14;
  overflow: hidden;
}
.rb-bar {
  width: 100%;
  border-radius: 7px 7px 0 0;
  background: linear-gradient(180deg, #2ee59d88, #2ee59d33);
  border-top: 2px solid #2ee59d;
  transition: height 400ms ease;
}
.rb-bar.bad {
  background: linear-gradient(180deg, #ff6b6bcc, #ff6b6b55);
  border-top-color: #ff6b6b;
  box-shadow: 0 0 18px #ff6b6b44;
}
.rb-name {
  text-align: center;
  margin-top: 7px;
  font-size: 13px;
  font-weight: 600;
  color: #ffffffcc;
}
.rb-name.bad { color: #ff6b6b; }
.rb-sub { text-align: center; font-size: 10.5px; opacity: 0.5; margin-top: 1px; }
</style>
