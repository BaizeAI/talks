<script setup lang="ts">
import { computed } from 'vue'

interface Point { x: number, y: number }
interface Series {
  name: string
  color: string
  points: Point[]
  dashed?: boolean
  /** thicker stroke for the line the audience should read first */
  emphasis?: boolean
}
interface Tick { v: number, label: string }
interface Marker { x: number, y: number, color: string, label: string, dy?: number, anchor?: 'start' | 'middle' | 'end' }
interface VLine { x: number, color: string, label: string }

const props = withDefaults(defineProps<{
  series: Series[]
  xMin: number
  xMax: number
  yMin: number
  yMax: number
  xTicks: Tick[]
  yTicks: Tick[]
  logX?: boolean
  logY?: boolean
  height?: number
  xLabel?: string
  markers?: Marker[]
  vline?: VLine
}>(), { height: 250 })

const W = 900
const PAD_L = 58
const PAD_R = 16
const PAD_T = 14
const PAD_B = 30

const H = computed(() => props.height)

function sx(x: number) {
  const f = props.logX
    ? (Math.log(x) - Math.log(props.xMin)) / (Math.log(props.xMax) - Math.log(props.xMin))
    : (x - props.xMin) / (props.xMax - props.xMin)
  return PAD_L + f * (W - PAD_L - PAD_R)
}
function sy(y: number) {
  const f = props.logY
    ? (Math.log(y) - Math.log(props.yMin)) / (Math.log(props.yMax) - Math.log(props.yMin))
    : (y - props.yMin) / (props.yMax - props.yMin)
  return PAD_T + (1 - f) * (H.value - PAD_T - PAD_B)
}
function path(s: Series) {
  return s.points.map((p, i) => `${i ? 'L' : 'M'}${sx(p.x).toFixed(1)},${sy(p.y).toFixed(1)}`).join(' ')
}
</script>

<template>
  <div class="lc">
    <div class="lc-legend">
      <div v-for="s in series" :key="s.name" class="lc-leg">
        <span class="lc-swatch" :style="{ background: s.color, opacity: s.dashed ? 0.85 : 1 }" />
        <span :style="{ color: s.color }">{{ s.name }}</span>
      </div>
    </div>

    <svg :viewBox="`0 0 ${W} ${H}`" class="lc-svg">
      <!-- y grid + labels -->
      <g v-for="t in yTicks" :key="`y${t.v}`">
        <line
          :x1="PAD_L" :x2="W - PAD_R" :y1="sy(t.v)" :y2="sy(t.v)"
          stroke="#ffffff12" stroke-width="1"
        />
        <text
          :x="PAD_L - 9" :y="sy(t.v) + 4"
          text-anchor="end" fill="#ffffff70" style="font-size: 13px"
        >{{ t.label }}</text>
      </g>

      <!-- x labels -->
      <g v-for="t in xTicks" :key="`x${t.v}`">
        <line
          :x1="sx(t.v)" :x2="sx(t.v)" :y1="PAD_T" :y2="H - PAD_B"
          stroke="#ffffff0c" stroke-width="1"
        />
        <text
          :x="sx(t.v)" :y="H - PAD_B + 19"
          text-anchor="middle" fill="#ffffff70" style="font-size: 13px"
        >{{ t.label }}</text>
      </g>

      <!-- axes -->
      <line :x1="PAD_L" :x2="W - PAD_R" :y1="H - PAD_B" :y2="H - PAD_B" stroke="#ffffff30" stroke-width="1" />
      <line :x1="PAD_L" :x2="PAD_L" :y1="PAD_T" :y2="H - PAD_B" stroke="#ffffff30" stroke-width="1" />

      <!-- vertical reference -->
      <template v-if="vline">
        <line
          :x1="sx(vline.x)" :x2="sx(vline.x)" :y1="PAD_T" :y2="H - PAD_B"
          :stroke="vline.color" stroke-width="2" stroke-dasharray="5 4"
        />
        <text
          :x="sx(vline.x) + 7" :y="PAD_T + 14"
          :fill="vline.color" style="font-size: 12.5px; font-weight: 600"
        >{{ vline.label }}</text>
      </template>

      <!-- series -->
      <path
        v-for="s in series" :key="s.name"
        :d="path(s)"
        fill="none"
        :stroke="s.color"
        :stroke-width="s.emphasis ? 3.4 : 2.4"
        stroke-linejoin="round"
        stroke-linecap="round"
        :stroke-dasharray="s.dashed ? '7 5' : undefined"
      />

      <!-- markers -->
      <g v-for="m in markers" :key="m.label">
        <circle :cx="sx(m.x)" :cy="sy(m.y)" r="6" :fill="m.color" />
        <circle :cx="sx(m.x)" :cy="sy(m.y)" r="11" fill="none" :stroke="m.color" stroke-width="1.5" opacity="0.45" />
        <text
          :x="sx(m.x) + (m.anchor === 'end' ? -16 : 16)" :y="sy(m.y) + (m.dy ?? 5)"
          :text-anchor="m.anchor ?? 'start'"
          :fill="m.color" style="font-size: 13px; font-weight: 600"
        >{{ m.label }}</text>
      </g>

      <text
        v-if="xLabel"
        :x="W - PAD_R" :y="H - 2"
        text-anchor="end" fill="#ffffff55" style="font-size: 12px"
      >{{ xLabel }}</text>
    </svg>
  </div>
</template>

<style scoped>
.lc {
  width: 100%;
  display: flex;
  flex-direction: column;
  gap: 5px;
}
.lc-legend {
  display: flex;
  gap: 15px;
  flex-wrap: wrap;
  font-size: 13px;
}
.lc-leg {
  display: flex;
  align-items: center;
  gap: 6px;
}
.lc-swatch {
  display: inline-block;
  width: 17px;
  height: 3px;
  border-radius: 2px;
}
.lc-svg {
  width: 100%;
  height: auto;
  display: block;
}
</style>
