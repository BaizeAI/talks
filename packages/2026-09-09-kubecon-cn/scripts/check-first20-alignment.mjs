import { access, readFile } from 'node:fs/promises'
import { resolve } from 'node:path'

const root = resolve(import.meta.dirname, '..')
const slides = await readFile(resolve(root, 'slides.md'), 'utf8')

const orderedMarkers = [
  'Why Your TTFT Lies',
  'Nicole Li',
  '# Background',
  "# It's 11 AM. TTFT P95 Just Went Red.",
  '# Dashboards Everywhere. Answers Nowhere.',
  '# Why TTFT Lies: The PD-Disaggregated Lifecycle',
  '# The Request Path Narrowed It in Four Reads',
  '# Method',
  '# V1 — Locally Correct. No First Move.',
  '<h1 class="iter-title">Three Iterations: From Component Views to Action Path</h1>',
  '# V3 — Eight Entry Signals. Proof on Demand.',
  '# Minimal = 4 Groups, 8 Entry Signals',
  '# Step 1 — Can We Accept Traffic at All?',
  '# Step 2–3 — Traffic and User SLO on One Timeline',
  '# Step 4 — Prefill, Handoff, or Decode?',
  '# The Operator Homepage',
  '# Two Signals Should Buy You One Next Page',
  '# Demo',
  '# Follow One Request Until the Owner Changes',
  '# Inside the engine',
  '# Four Things Inflate a Prefill TTFT',
]

const slideCount = (slides.match(/^---$/gm) ?? []).length / 2
if (slideCount !== 31)
  throw new Error(`Expected 31 slides after restoring PPT slide 11, found ${slideCount}`)

let cursor = -1
for (const marker of orderedMarkers) {
  const next = slides.indexOf(marker, cursor + 1)
  if (next === -1)
    throw new Error(`Missing or out-of-order slide marker: ${marker}`)
  cursor = next
}

for (const asset of [
  'public/ppt-align/dashboard-maze.png',
  'public/ppt-align/pd-lifecycle.png',
  'public/ppt-align/dashboard-sprawl.png',
  'public/ppt-align/iteration-evolution.png',
  'public/ppt-align/v3-entry-signals.png',
]) {
  await access(resolve(root, asset))
}

console.log('PPT alignment markers and source visuals are present.')
