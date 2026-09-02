<script setup lang="ts">
import { computed } from 'vue'

interface Series {
  name: string
  color: string
  points: number[]
  /** value range used to normalise this series; defaults to its own min/max */
  min?: number
  max?: number
  dashed?: boolean
  /** optional right-side value label */
  unit?: string
}

const props = withDefaults(defineProps<{
  series: Series[]
  /** index (in points) where the change was applied; draws a vertical marker */
  markerAt?: number
  markerLabel?: string
  beforeLabel?: string
  afterLabel?: string
  height?: number
  xLabels?: string[]
}>(), { height: 210 })

const W = 900
const PAD_L = 8
const PAD_R = 8
const PAD_T = 14
const PAD_B = 26

const H = computed(() => props.height)

function pathFor(s: Series) {
  const n = s.points.length
  const lo = s.min ?? Math.min(...s.points)
  const hi = s.max ?? Math.max(...s.points)
  const span = hi - lo || 1
  const innerW = W - PAD_L - PAD_R
  const innerH = H.value - PAD_T - PAD_B
  return s.points.map((v, i) => {
    const x = PAD_L + (innerW * i) / (n - 1 || 1)
    const y = PAD_T + innerH * (1 - (v - lo) / span)
    return `${i === 0 ? 'M' : 'L'}${x.toFixed(1)},${y.toFixed(1)}`
  }).join(' ')
}

const markerX = computed(() => {
  if (props.markerAt == null)
    return null
  const n = props.series[0]?.points.length ?? 2
  const innerW = W - PAD_L - PAD_R
  return PAD_L + (innerW * props.markerAt) / (n - 1 || 1)
})
</script>

<template>
  <div class="tc">
    <div class="tc-legend">
      <div v-for="s in series" :key="s.name" class="tc-leg">
        <span
          class="tc-line"
          :style="{ background: s.color, opacity: s.dashed ? 0.7 : 1 }"
          :class="{ dashed: s.dashed }"
        />
        <span :style="{ color: s.color }">{{ s.name }}</span>
      </div>
    </div>

    <svg :viewBox="`0 0 ${W} ${H}`" class="tc-svg" preserveAspectRatio="none">
      <!-- horizontal grid -->
      <line
        v-for="i in 3" :key="`g${i}`"
        :x1="PAD_L" :x2="W - PAD_R"
        :y1="PAD_T + ((H - PAD_T - PAD_B) * i) / 4"
        :y2="PAD_T + ((H - PAD_T - PAD_B) * i) / 4"
        stroke="#ffffff14" stroke-width="1"
      />
      <line
        :x1="PAD_L" :x2="W - PAD_R" :y1="H - PAD_B" :y2="H - PAD_B"
        stroke="#ffffff30" stroke-width="1"
      />

      <!-- change marker -->
      <template v-if="markerX != null">
        <rect
          :x="markerX" :y="PAD_T" :width="W - PAD_R - markerX" :height="H - PAD_T - PAD_B"
          fill="#2ee59d" opacity="0.06"
        />
        <line
          :x1="markerX" :x2="markerX" :y1="PAD_T - 4" :y2="H - PAD_B"
          stroke="#2ee59d" stroke-width="2" stroke-dasharray="5 4"
        />
      </template>

      <path
        v-for="s in series" :key="s.name"
        :d="pathFor(s)"
        fill="none"
        :stroke="s.color"
        stroke-width="2.5"
        stroke-linejoin="round"
        stroke-linecap="round"
        :stroke-dasharray="s.dashed ? '6 5' : undefined"
        vector-effect="non-scaling-stroke"
      />
    </svg>

    <div class="tc-axis">
      <span v-if="beforeLabel" class="tc-before">{{ beforeLabel }}</span>
      <span v-if="markerLabel" class="tc-marker">
        <div i-carbon:arrow-down style="font-size: 12px" />{{ markerLabel }}
      </span>
      <span v-if="afterLabel" class="tc-after">{{ afterLabel }}</span>
    </div>
  </div>
</template>

<style scoped>
.tc {
  width: 100%;
  display: flex;
  flex-direction: column;
  gap: 5px;
}
.tc-legend {
  display: flex;
  gap: 16px;
  font-size: 13px;
  flex-wrap: wrap;
}
.tc-leg {
  display: flex;
  align-items: center;
  gap: 6px;
}
.tc-line {
  display: inline-block;
  width: 18px;
  height: 3px;
  border-radius: 2px;
}
.tc-line.dashed {
  background-image: linear-gradient(90deg, currentColor 60%, transparent 0);
}
.tc-svg {
  width: 100%;
  height: auto;
  display: block;
}
.tc-axis {
  display: flex;
  align-items: center;
  font-size: 13px;
  padding: 0 4px;
}
.tc-before {
  flex: 1;
  text-align: left;
  opacity: 0.6;
}
.tc-after {
  flex: 1;
  text-align: right;
  opacity: 0.6;
}
.tc-marker {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  color: #2ee59d;
  font-weight: 600;
  white-space: nowrap;
}
</style>
