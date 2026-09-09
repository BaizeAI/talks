import { access, readFile } from 'node:fs/promises'
import { resolve } from 'node:path'

const root = resolve(import.meta.dirname, '..')
const slides = await readFile(resolve(root, 'slides.md'), 'utf8')

const orderedMarkers = [
  'Why Your TTFT Lies',
  'Nicole Li',
  '# Background',
  '# At 11 AM, TTFT P95 Went Red',
  '# Dashboards Everywhere. Answers Nowhere.',
  '# Why TTFT Lies: The PD-Disaggregated Lifecycle',
  '# Four Reads Narrowed the Request Path',
  '# Method',
  '# From Dashboard Sprawl to an Action Path',
  '# Minimal = Eight Signals. One Next Proof.',
  '# Step 1 — Can We Accept Traffic at All?',
  '# Step 2–3 — Traffic and User SLO on One Timeline',
  '# Step 4 — Prefill, Handoff, or Decode?',
  '# Diagnosis Playbook',
  '# Demo',
  '# Follow One Request Until the Owner Changes',
  '# Inside the engine',
  '# Three Things Inflate a Prefill TTFT',
  '# KV Space Is a Shared Budget',
  '# KV Transfer — Zero Bytes Looks Like a Fast Transfer',
]

const slideCount = (slides.match(/^---$/gm) ?? []).length / 2
if (slideCount !== 27)
  throw new Error(`Expected 27 slides after merging the playbook into slide 14, found ${slideCount}`)

let cursor = -1
for (const marker of orderedMarkers) {
  const next = slides.indexOf(marker, cursor + 1)
  if (next === -1)
    throw new Error(`Missing or out-of-order slide marker: ${marker}`)
  cursor = next
}

for (const asset of [
  'public/shots/ttft-incident.png',
  'public/shots/sprawl-real.png',
  'public/shots/pd-lifecycle.png',
  'public/shots/action-path.png',
  'public/demo-poster.jpg',
]) {
  await access(resolve(root, asset))
}

console.log('Current first-20 slide order, 27-slide count, and source visuals are valid.')
