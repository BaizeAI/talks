---
layout: center
highlighter: shiki
css: unocss
colorSchema: dark
transition: fade-out
title: Why Your TTFT Lies
exportFilename: KubeCon China 2026.09 - Why Your TTFT Lies
lineNumbers: false
drawings:
  persist: false
mdc: true
clicks: 0
preload: false
glowSeed: 311
routerMode: hash
footer: false
fonts:
  sans: DM Sans, Noto Sans SC
---

<div translate-x--10>

<div text-sm tracking-widest op-60 mb-4 font-mono>#KubeCon #CloudNativeCon China 2026</div>

<h1 style="line-height: 1.15">
  Why Your TTFT Lies
</h1>

<div text-xl op-80 mt-3 mb-8 style="max-width: 800px; line-height: 1.5">
  Diagnosing PD-Disaggregated LLM Inference with Minimal Cross-Layer Metrics
</div>

<div text-lg op-90>Nicole Li &nbsp;·&nbsp; Kebe Liu &nbsp;—&nbsp; DaoCloud</div>

</div>

<div w-full absolute bottom-0 left-0 flex items-center transform="translate-x--10 translate-y--12">
  <div w-full flex items-center justify-end gap-4>
    <img src="/kubecon-logo.svg" style="height: 46px; opacity: 0.92">
  </div>
</div>

<div absolute bottom-0 left-0 w-full style="height: 46%; z-index: -1; overflow: hidden; mask-image: linear-gradient(to top, black 30%, transparent)">
  <img src="/skyline-wide.png" style="opacity: 0.18; object-fit: cover; object-position: bottom; width: 100%; height: 100%">
</div>
---
layout: intro
class: px-24
glowSeed: 205
footer: false
---

<div flex items-start justify-center gap-24>
  <div flex flex-col items-center>
    <img src="/person/nicole.jpg" w-44 h-44 rounded-full object-cover mb-5>
    <span font-semibold text-3xl>Nicole Li</span>
    <div text-center mt-2>
      <div op-70>Inference Acceleration Team, DaoCloud</div>
      <div text-sm flex items-center justify-center gap-2 mt-3>
        <div i-ri:github-fill /><span underline decoration-dashed font-mono decoration-zinc-500>nicole-lihui</span>
      </div>
    </div>
  </div>
  <div flex flex-col items-center>
    <img src="/person/kebe.jpeg" w-44 h-44 rounded-full object-cover mb-5>
    <span font-semibold text-3xl>Kebe Liu</span>
    <div text-center mt-2>
      <div op-70>Senior Software Engineer, DaoCloud</div>
      <div text-sm flex items-center justify-center gap-2 mt-3>
        <div i-ri:github-fill /><span underline decoration-dashed font-mono decoration-zinc-500>kebe7jun</span>
      </div>
    </div>
  </div>
</div>

<div mt-12 text-center text-lg op-75>
  We run PD-disaggregated LLM inference in production — every trap in this talk is one we walked into
</div>
---
layout: section
glowSeed: 120
---

# Background

<div text-2xl op-70 mt-3>TTFT sent us into a maze</div>
---
layout: default
glowSeed: 88
---

# At 11 AM, TTFT P95 Went Red

<div text-lg op-70 mt-1 mb-4>A familiar scene in every LLM inference team</div>

<div flex gap-6 items-start>

<div style="flex: 0.82">
  <div class="alert">
    <div class="alert-h">
      <div i-carbon:warning-alt-filled />ALERT FIRED
    </div>
    <div class="alert-b">
      <div class="alert-r"><span>metric</span><b>TTFT P95</b></div>
      <div class="alert-r"><span>threshold</span><b>&gt; 800 ms</b></div>
      <div class="alert-r hot"><span>peak P95</span><b>41.1 min</b></div>
      <div class="alert-r hot"><span>peak P99</span><b>42.3 min</b></div>
      <div class="alert-r"><span>window</span><b>11:00 – 13:05</b></div>
    </div>
  </div>

  <div class="alert-mean">
    <div i-carbon:idea style="color: #2ee59d; flex: none; margin-top: 3px" />
    <div>Mean TTFT reads <b style="color:#2ee59d">681 ms</b> and is green right now. The mean panel never showed this incident at all.</div>
  </div>
</div>

<div style="flex: 1.18">
  <div text-sm op-60 mb-2>Production dashboard · TTFT mean vs. percentile peaks</div>
  <img src="/shots/ttft-incident.png" class="shot">
</div>

</div>

<style>
.alert {
  border: 1px solid #ff6b6b45;
  border-radius: 12px;
  background: #ff6b6b0b;
  overflow: hidden;
}
.alert-h {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 9px 15px;
  background: #ff6b6b18;
  border-bottom: 1px solid #ff6b6b2e;
  color: #ff8f8f;
  font-size: 13.5px;
  font-weight: 700;
  letter-spacing: 0.06em;
}
.alert-b { padding: 11px 15px; display: flex; flex-direction: column; gap: 6px; }
.alert-r {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  font-size: 14px;
}
.alert-r span { opacity: 0.55; font-size: 12.5px; }
.alert-r b { font-family: ui-monospace, SFMono-Regular, Menlo, monospace; font-size: 13.5px; }
.alert-r.hot b { color: #ff6b6b; font-size: 15px; }
.alert-mean {
  display: flex;
  gap: 9px;
  margin-top: 13px;
  padding: 12px 15px;
  border: 1px solid #2ee59d33;
  border-radius: 11px;
  background: #2ee59d0a;
  font-size: 13.5px;
  line-height: 1.55;
}
</style>
---
layout: default
glowSeed: 142
---

# Dashboards Everywhere. Answers Nowhere.

<div text-lg op-70 mt-1 mb-4>Every panel is correct in isolation; none provides a first move</div>

<div flex gap-7 items-center>

<div style="flex: 0.82">
  <div class="q-box">
    <div class="q-h">What broke?</div>
    <div class="q-list">
      <div class="q-i"><span>?</span>Gateway &nbsp;·&nbsp; Prefill</div>
      <div class="q-i"><span>?</span>KV usage &nbsp;·&nbsp; KV transfer</div>
      <div class="q-i"><span>?</span>GPU &nbsp;·&nbsp; Network</div>
      <div class="q-i hot"><span>!</span>Or is TTFT just lying to us?</div>
    </div>
  </div>
</div>

<div style="flex: 1.18">
  <img src="/shots/sprawl-real.png" class="shot">
  <div text-center text-sm op-55 mt-3 style="line-height: 1.5">
    Dashboards everywhere. Answers nowhere.<br><b>The request path must give us a first move.</b>
  </div>
</div>

</div>

<style>
.q-box {
  padding: 14px 17px;
  border: 1px solid #ffffff20;
  border-radius: 13px;
  background: #ffffff07;
}
.q-h { font-size: 22px; font-weight: 700; margin-bottom: 10px; }
.q-list { display: flex; flex-direction: column; gap: 9px; }
.q-i {
  display: flex;
  align-items: center;
  gap: 11px;
  font-size: 15.5px;
  opacity: 0.85;
}
.q-i span {
  flex: none;
  width: 23px;
  height: 23px;
  line-height: 23px;
  text-align: center;
  border-radius: 50%;
  background: #ffffff14;
  font-size: 13px;
  font-weight: 700;
}
.q-i.hot { color: #ffc217; opacity: 1; font-weight: 600; }
.q-i.hot span { background: #ffc21726; color: #ffc217; }
.maze-layout { display: grid; grid-template-columns: 1.2fr 0.8fr; gap: 22px; align-items: stretch; }
.maze-shot { display: flex; flex-direction: column; justify-content: center; min-width: 0; }
.maze-shot img { width: 100%; height: 252px; object-fit: contain; border-radius: 11px; background: #fff; }
.maze-shot span { margin-top: 8px; text-align: center; font-size: 12.5px; opacity: 0.58; }
.maze-question { position: relative; overflow: hidden; min-height: 286px; border-radius: 12px; border: 1px solid #ffffff1c; }
.maze-question > img { position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; opacity: 0.33; }
.maze-question .q-box { position: relative; z-index: 1; margin: 18px; background: #06222ddf; backdrop-filter: blur(2px); }
.maze-close { margin-top: 15px; padding: 11px 16px; border-left: 3px solid #ffc217; background: #ffc2170b; color: #ffc217; font-size: 15px; }
</style>
---
layout: default
glowSeed: 210
---

# Why TTFT Lies: The PD-Disaggregated Lifecycle

<div text-lg op-70 mt-1 mb-2>TTFT is a sum. Any term can blow up — and the sum never says which.</div>

<img src="/shots/pd-lifecycle.png" class="illus" style="max-height: 208px; object-fit: contain">

<div class="eq">
  <span class="eq-l">TTFT</span>
  <span class="eq-o">=</span>
  <span class="eq-t">Gateway</span><span class="eq-o">+</span>
  <span class="eq-t">Prefill</span><span class="eq-o">+</span>
  <span class="eq-t">KV Transfer</span><span class="eq-o">+</span>
  <span class="eq-t">first Decode token</span>
</div>

<div flex gap-5 mt-3>
  <div class="why-c">
    <div class="why-h"><div i-carbon:warning style="color: #ffa35f" />KV Transfer is new</div>
    <div class="why-d">In a monolithic engine this term does not exist. PD disaggregation adds a boundary that <b>neither side owns alone</b>.</div>
  </div>
  <div class="why-c">
    <div class="why-h"><div i-carbon:chart-line style="color: #b0ddff" />The sum hides the terms</div>
    <div class="why-d">Each layer measures <b>its own span</b>. Nobody measures the gaps between them — and the gaps are where the minutes go.</div>
  </div>
</div>

<style>
.pd-figure {
  height: 155px;
  padding: 9px 14px;
  border: 1px solid #ffffff1d;
  border-radius: 12px;
  background: #031a23;
}
.pd-figure img { width: 100%; height: 100%; object-fit: contain; }
.eq {
  display: flex;
  align-items: center;
  justify-content: center;
  flex-wrap: wrap;
  gap: 9px;
  margin-top: 11px;
  padding: 10px 18px;
  border: 1px solid #ffffff1e;
  border-radius: 12px;
  background: #ffffff07;
}
.eq-l { font-size: 21px; font-weight: 700; color: #ffc217; }
.eq-o { font-size: 17px; opacity: 0.5; }
.eq-t {
  padding: 3px 13px;
  border-radius: 999px;
  border: 1px solid #ffffff22;
  background: #ffffff0b;
  font-size: 14.5px;
}
.why-c {
  flex: 1;
  padding: 10px 14px;
  border: 1px solid #ffffff1e;
  border-radius: 12px;
  background: #ffffff07;
}
.why-h { display: flex; align-items: center; gap: 7px; font-size: 15.5px; font-weight: 600; margin-bottom: 6px; }
.why-d { font-size: 12.5px; line-height: 1.55; opacity: 0.85; }
</style>
---
layout: default
glowSeed: 268
---

# Four Reads Narrowed the Request Path

<div text-lg op-70 mt-1 mb-4>Same incident. Walk the path instead of staring at the tail.</div>

<div flex gap-6 items-start>

<div style="flex: 1.1">
  <div class="rp">
    <div class="rp-row ok">
      <div class="rp-stage"><div i-carbon:gateway />Business Gateway</div>
      <div class="rp-obs">latency stable</div>
      <div class="rp-tag">healthy</div>
    </div>
    <div class="rp-row ok">
      <div class="rp-stage"><div i-carbon:router />PD Router / EPP</div>
      <div class="rp-obs">queue low</div>
      <div class="rp-tag">healthy</div>
    </div>
    <div class="rp-row bad">
      <div class="rp-stage"><div i-carbon:model-alt />Prefill</div>
      <div class="rp-obs">waiting <b>1 → 150</b></div>
      <div class="rp-tag">first abnormal</div>
    </div>
    <div class="rp-row ok">
      <div class="rp-stage"><div i-carbon:chat-bot />Decode</div>
      <div class="rp-obs">waiting 0 · running 0–10</div>
      <div class="rp-tag">not starved</div>
    </div>
    <div class="rp-row warn">
      <div class="rp-stage"><div i-carbon:data-base />KV Cache</div>
      <div class="rp-obs">evictions <b>689 ops/s</b></div>
      <div class="rp-tag">suspect</div>
    </div>
  </div>

  <div class="rp-out">
    <div class="rp-out-i">
      <span class="rp-k">Conclusion</span>
      First abnormal boundary — <b style="color:#ffc217">Prefill</b>. Not entry, not Decode.
    </div>
    <div class="rp-out-i">
      <span class="rp-k">Next proof</span>
      prefix hit · computed Prefill tokens · P queue slope · eviction records
    </div>
  </div>
</div>

<div style="flex: 0.95">
  <div class="rp-tail">
    <span class="rp-tail-l">TTFT tail</span>
    <span class="rp-tail-a">856 ms</span>
    <div i-carbon:arrow-right style="color: #ff6b6b" />
    <span class="rp-tail-b">41 min</span>
  </div>
  <img src="/shots/kv-eviction.png" class="shot mt-3">
  <div text-sm op-55 mt-2 style="line-height: 1.5">
TTFT told us <b>when</b> users were waiting. The path told us <b>where</b>. It still did not tell us <b>why</b> — that took a method, and a case we will come back to.
  </div>
</div>

</div>

<style>
.rp { display: flex; flex-direction: column; gap: 6px; }
.rp-row {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 13px;
  border: 1px solid #ffffff18;
  border-radius: 9px;
  background: #ffffff07;
  font-size: 13.5px;
}
.rp-stage {
  flex: 0 0 178px;
  display: flex;
  align-items: center;
  gap: 7px;
  font-weight: 600;
  color: #ffffffe6;
}
.rp-obs { flex: 1; opacity: 0.8; font-size: 13px; }
.rp-obs b { font-family: ui-monospace, SFMono-Regular, Menlo, monospace; }
.rp-tag {
  flex: none;
  padding: 1px 10px;
  border-radius: 999px;
  font-size: 11px;
  border: 1px solid #ffffff20;
  background: #ffffff0b;
  opacity: 0.7;
}
.rp-row.ok { opacity: 0.62; }
.rp-row.bad {
  border-color: #ff6b6b55;
  background: #ff6b6b12;
  box-shadow: 0 0 18px #ff6b6b26;
}
.rp-row.bad .rp-tag { border-color: #ff6b6b66; background: #ff6b6b1e; color: #ff8f8f; opacity: 1; }
.rp-row.bad .rp-obs b { color: #ff6b6b; font-size: 14.5px; }
.rp-row.warn { border-color: #ffc21745; background: #ffc21710; }
.rp-row.warn .rp-tag { border-color: #ffc21766; background: #ffc2171e; color: #ffc217; opacity: 1; }
.rp-row.warn .rp-obs b { color: #ffc217; }
.rp-out {
  margin-top: 13px;
  padding: 11px 15px;
  border: 1px solid #ffc21735;
  border-radius: 11px;
  background: #ffc2170a;
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.rp-out-i { font-size: 13px; line-height: 1.5; }
.rp-k {
  display: inline-block;
  width: 78px;
  margin-right: 9px;
  padding: 1px 7px;
  border-radius: 5px;
  background: #ffffff14;
  font-size: 11px;
  text-align: center;
}
.rp-tail {
  display: flex;
  align-items: baseline;
  gap: 10px;
  padding: 12px 16px;
  border: 1px solid #ff6b6b3a;
  border-radius: 11px;
  background: #ff6b6b0b;
}
.rp-tail-l { font-size: 13px; opacity: 0.7; }
.rp-tail-a { font-family: ui-monospace, SFMono-Regular, Menlo, monospace; font-size: 19px; opacity: 0.75; }
.rp-tail-b { font-family: ui-monospace, SFMono-Regular, Menlo, monospace; font-size: 27px; font-weight: 700; color: #ff6b6b; }
</style>
---
layout: section
glowSeed: 175
---

# Method

<div text-2xl op-70 mt-3>Organize for decisions, reveal detail only when needed</div>
---
layout: default
glowSeed: 148
---

# From Dashboard Sprawl to an Action Path

<div text-lg op-70 mt-1 mb-3>Keep the telemetry. Change the decision path.</div>

<img src="/shots/action-path.png" class="illus" style="max-height: 224px; object-fit: contain">

<div flex gap-4 mt-4>
  <div class="iv">
    <div class="iv-t">V1 · Component views</div>
    <div class="iv-d">Each layer was <b>locally correct</b>; the end-to-end request path was missing.</div>
  </div>
  <div class="iv">
    <div class="iv-t">V2 · PD request path</div>
    <div class="iv-d">Gateway → P → KV handoff → D. We could finally say <b>where</b> — but not what to do.</div>
  </div>
  <div class="iv hot">
    <div class="iv-t">V3 · Action path</div>
    <div class="iv-d"><b>Signal → proof → one reversible action</b>, with a validation gate at the end.</div>
  </div>
</div>

<div class="iv-foot">
  <div i-carbon:idea style="color: #ffc217; flex: none; margin-top: 3px" />
  <div><b>Telemetry everywhere. No first move.</b> The V1 dashboards are all still there — V3 did not replace them, it decided <b>the order in which you open them</b>.</div>
</div>

<style>
.iv {
  flex: 1;
  padding: 11px 14px;
  border: 1px solid #ffffff1e;
  border-radius: 11px;
  background: #ffffff07;
}
.iv.hot { border-color: #2ee59d4a; background: #2ee59d0c; }
.iv-t { font-size: 14.5px; font-weight: 600; margin-bottom: 4px; }
.iv.hot .iv-t { color: #2ee59d; }
.iv-d { font-size: 12px; line-height: 1.55; opacity: 0.85; }
.iv-foot {
  display: flex;
  gap: 10px;
  margin-top: 12px;
  padding: 11px 16px;
  border: 1px solid #ffc21735;
  border-radius: 11px;
  background: #ffc2170a;
  font-size: 13.5px;
  line-height: 1.55;
}
</style>
---
layout: default
glowSeed: 205
---

# Minimal = Eight Signals. One Next Proof.

<div text-lg op-70 mt-1 mb-4>Not the metrics we have — the ones that decide which page opens next</div>

<EntrySignals />

<div class="min-flow">
  <div class="mf-step"><b>8 entries</b><span>always on screen</span></div>
  <div i-carbon:chevron-right class="mf-a" />
  <div class="mf-step"><b>first abnormal boundary</b><span>which stage owns it</span></div>
  <div i-carbon:chevron-right class="mf-a" />
  <div class="mf-step"><b>one proof view</b><span>opened on demand</span></div>
  <div i-carbon:chevron-right class="mf-a" />
  <div class="mf-step hot"><b>one reversible action</b><span>with a validation gate</span></div>
</div>

<div class="min-rule">
  <div i-carbon:filter style="color: #ffc217; flex: none; margin-top: 3px" />
  <div>The inclusion rule: <b>if the value of a signal never changes what you do next, it is not an entry signal.</b> The homepage gives direction; expert evidence stays <b>one click away</b>.</div>
</div>

<style>
.min-flow {
  display: flex;
  align-items: stretch;
  gap: 3px;
  margin-top: 16px;
}
.mf-step {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 1px;
  padding: 9px 13px;
  border: 1px solid #ffffff1e;
  border-radius: 10px;
  background: #ffffff07;
}
.mf-step b { font-size: 13.5px; }
.mf-step span { font-size: 11px; opacity: 0.55; }
.mf-step.hot { border-color: #2ee59d4a; background: #2ee59d0e; }
.mf-step.hot b { color: #2ee59d; }
.mf-a { display: flex; align-items: center; color: #ffffff40; font-size: 15px; flex: none; }
.min-rule {
  display: flex;
  gap: 10px;
  margin-top: 14px;
  padding: 12px 16px;
  border: 1px solid #ffc21735;
  border-radius: 11px;
  background: #ffc2170a;
  font-size: 14px;
  line-height: 1.55;
}
</style>
---
layout: default
glowSeed: 62
---

# Step 1 — Can We Accept Traffic at All?

<div text-lg op-70 mt-1 mb-4>Same slow request, three different first actions. Triage first, root cause later.</div>

<div flex gap-6 items-start>

<div style="flex: 0.72">
  <EntrySignals :vertical="true" :highlight="['ready', 'err']" />
</div>

<div style="flex: 1.28">
  <div class="s1-branch">
    <div class="s1-row">
      <div class="s1-cond"><b>Ready ↓</b> + <b>5xx ↑</b></div>
      <div i-carbon:arrow-right class="s1-ar" />
      <div class="s1-act">endpoint / serving capacity</div>
      <div class="s1-lab down">DOWN</div>
    </div>
    <div class="s1-row">
      <div class="s1-cond"><b>Ready stable</b> + <b>429 ↑</b></div>
      <div i-carbon:arrow-right class="s1-ar" />
      <div class="s1-act">admission · quota · capacity</div>
      <div class="s1-lab rej">REJECTED</div>
    </div>
    <div class="s1-row hot">
      <div class="s1-cond"><b>Health stable</b> + <b>latency ↑</b></div>
      <div i-carbon:arrow-right class="s1-ar" />
      <div class="s1-act">continue to traffic + user SLO</div>
      <div class="s1-lab slow">SLOW</div>
    </div>
  </div>

  <div class="s1-note">
    <div i-carbon:warning style="color: #ffc217; flex: none; margin-top: 3px" />
    <div><b>Down, rejected, or slow?</b> These three look identical from a latency chart alone — and only the third one is worth a GPU investigation. Skipping this step is how teams spend an hour tuning batch size on an incident that was a dead endpoint.</div>
  </div>
</div>

</div>

<style>
.s1-branch { display: flex; flex-direction: column; gap: 9px; }
.s1-row {
  display: flex;
  align-items: center;
  gap: 11px;
  padding: 12px 15px;
  border: 1px solid #ffffff1e;
  border-radius: 11px;
  background: #ffffff07;
}
.s1-cond { flex: 0 0 215px; font-size: 13.5px; }
.s1-cond b { color: #ffffffee; }
.s1-ar { color: #ffffff45; flex: none; }
.s1-act { flex: 1; font-size: 13.5px; opacity: 0.85; }
.s1-lab {
  flex: none;
  padding: 2px 10px;
  border-radius: 999px;
  font-size: 10.5px;
  font-weight: 700;
  letter-spacing: 0.05em;
}
.s1-lab.down { background: #ff6b6b22; color: #ff8f8f; }
.s1-lab.rej { background: #ffa35f22; color: #ffa35f; }
.s1-lab.slow { background: #2ee59d22; color: #2ee59d; }
.s1-row.hot { border-color: #2ee59d4a; background: #2ee59d0c; }
.s1-note {
  display: flex;
  gap: 10px;
  margin-top: 14px;
  padding: 12px 16px;
  border: 1px solid #ffc21735;
  border-radius: 11px;
  background: #ffc2170a;
  font-size: 13.5px;
  line-height: 1.6;
}
</style>
---
layout: default
glowSeed: 118
---

# Step 2–3 — Traffic and User SLO on One Timeline

<div text-lg op-70 mt-1 mb-4>RPS tells you how many. Tokens tell you how much work.</div>

<div flex gap-6 items-start>

<div style="flex: 0.72">
  <EntrySignals :vertical="true" :highlight="['rps', 'tpm', 'ttft', 'tpot']" />
  <div class="s2-warn">
    <div i-carbon:warning-alt style="color: #ffa35f; flex: none; margin-top: 2px" />
    <div>One decision view — <b>not one weighted score</b>. A single health number destroys the contrast you need.</div>
  </div>
</div>

<div style="flex: 1.28">
  <div class="s2-pair">
    <div class="s2-card">
      <div class="s2-h" style="color: #2ee59d">TRAFFIC — how much work arrived</div>
      <div class="s2-l"><span>requests/s</span><span>input tok/s</span><span>output tok/s</span><span>prompt length</span></div>
    </div>
    <div class="s2-card">
      <div class="s2-h" style="color: #ffc217">USER — what they felt</div>
      <div class="s2-l"><span>success · timeout</span><span>TTFT p95 / p99</span><span>TPOT p95 / p99</span></div>
    </div>
  </div>

  <div class="s2-win">SAME TIME WINDOW · read them together</div>

  <div class="s2-rule">
    <div class="s2-r">
      <div class="s2-rc"><b>input TPM / prompt length ↑</b> &nbsp;+&nbsp; <b>TTFT ↑</b></div>
      <div i-carbon:arrow-right style="color: #2ee59d; flex: none" />
      <div class="s2-rt">inspect <b>PREFILL</b> next</div>
    </div>
    <div class="s2-r">
      <div class="s2-rc"><b>output TPM / concurrency ↑</b> &nbsp;+&nbsp; <b>TPOT ↑</b></div>
      <div i-carbon:arrow-right style="color: #b0ddff; flex: none" />
      <div class="s2-rt">inspect <b>DECODE</b> next</div>
    </div>
  </div>

  <div text-xs op-45 mt-3>schematic relationship · no invented values</div>
</div>

</div>

<style>
.s2-pair { display: flex; gap: 11px; }
.s2-card {
  flex: 1;
  padding: 12px 14px;
  border: 1px solid #ffffff1e;
  border-radius: 11px;
  background: #ffffff07;
}
.s2-h { font-size: 13px; font-weight: 700; letter-spacing: 0.03em; margin-bottom: 8px; }
.s2-l { display: flex; flex-wrap: wrap; gap: 5px; }
.s2-l span {
  padding: 2px 9px;
  border-radius: 999px;
  border: 1px solid #ffffff20;
  background: #ffffff0b;
  font-size: 11.5px;
  font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
}
.s2-win {
  margin: 11px 0;
  padding: 5px 0;
  text-align: center;
  border-top: 1px dashed #ffffff26;
  border-bottom: 1px dashed #ffffff26;
  font-size: 11.5px;
  letter-spacing: 0.1em;
  opacity: 0.6;
}
.s2-rule { display: flex; flex-direction: column; gap: 9px; }
.s2-r {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 11px 15px;
  border: 1px solid #ffffff1e;
  border-radius: 11px;
  background: #ffffff07;
  font-size: 13.5px;
}
.s2-rc { flex: 1; opacity: 0.9; }
.s2-rt { flex: 0 0 178px; opacity: 0.9; }
.s2-warn {
  display: flex;
  gap: 9px;
  margin-top: 10px;
  padding: 11px 14px;
  border: 1px solid #ffa35f33;
  border-radius: 11px;
  background: #ffa35f0a;
  font-size: 12.5px;
  line-height: 1.55;
}
</style>
---
layout: default
glowSeed: 232
---

# Step 4 — Prefill, Handoff, or Decode?

<div text-lg op-70 mt-1 mb-4>The first queue that rises owns the incident</div>

<StageFlow
  :stages="[
    { id: 'e', name: 'Entry / EPP', sub: 'ready · queue', icon: 'i-carbon:gateway' },
    { id: 'p', name: 'Prefill', sub: 'waiting', icon: 'i-carbon:model-alt' },
    { id: 'kv', name: 'KV Handoff', sub: 'transfer p99', icon: 'i-carbon:data-share' },
    { id: 'd', name: 'Decode', sub: 'waiting · running', icon: 'i-carbon:chat-bot' },
  ]"
  :highlight="['p']"
/>

<div flex gap-5 mt-5>
  <div class="s4-r">
    <div class="s4-c"><b>TTFT ↑</b> + <b>P waiting ↑</b></div>
    <div i-carbon:arrow-right style="color: #ffc217" />
    <div class="s4-t" style="color: #ffc217">Prefill evidence</div>
  </div>
  <div class="s4-r">
    <div class="s4-c">queues flat + <b>transfer p99 ↑</b></div>
    <div i-carbon:arrow-right style="color: #ffa35f" />
    <div class="s4-t" style="color: #ffa35f">Handoff proof</div>
  </div>
  <div class="s4-r">
    <div class="s4-c"><b>TPOT ↑</b> + <b>D waiting ↑</b></div>
    <div i-carbon:arrow-right style="color: #b0ddff" />
    <div class="s4-t" style="color: #b0ddff">Decode proof</div>
  </div>
</div>

<div class="s4-key">
  <div i-carbon:idea style="color: #ffc217; flex: none; margin-top: 3px" />
  <div>Queues do not rise together — they rise <b>in order</b>. The stage whose queue moved <b>first</b> is the boundary; everything downstream of it is a symptom, and everything upstream is already ruled out.</div>
</div>

<div text-xs op-45 mt-3>schematic example · first rise selects the next page</div>

<style>
.s4-r {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 15px;
  border: 1px solid #ffffff1e;
  border-radius: 11px;
  background: #ffffff07;
  font-size: 13px;
}
.s4-c { flex: 1; opacity: 0.88; }
.s4-t { flex: none; font-weight: 600; font-size: 13.5px; }
.s4-key {
  display: flex;
  gap: 10px;
  margin-top: 16px;
  padding: 13px 17px;
  border: 1px solid #ffc21735;
  border-radius: 11px;
  background: #ffc2170a;
  font-size: 14px;
  line-height: 1.6;
}
</style>
---
layout: default
glowSeed: 84
---

# Two Signals Should Buy You One Next Page

<div text-lg op-70 mt-1 mb-4>The arrow selects the next proof view — it does not prove root cause</div>

<div class="tsg">
  <div class="ts-row">
    <div class="ts-sig"><b>ready ↓</b> + <b>5xx ↑</b></div>
    <div i-carbon:arrow-right class="ts-a" />
    <div class="ts-dst" style="--c: #ff6b6b">SERVING / ENDPOINT</div>
  </div>
  <div class="ts-row">
    <div class="ts-sig"><b>RPS ↑</b> + <b>RPM / TPM ↑</b></div>
    <div i-carbon:arrow-right class="ts-a" />
    <div class="ts-dst" style="--c: #ffa35f">ADMISSION / CAPACITY</div>
  </div>
  <div class="ts-row">
    <div class="ts-sig"><b>TTFT ↑</b> + <b>P waiting ↑</b></div>
    <div i-carbon:arrow-right class="ts-a" />
    <div class="ts-dst" style="--c: #ffc217">PREFILL / SCHEDULER</div>
  </div>
  <div class="ts-row">
    <div class="ts-sig"><b>TPOT ↑</b> + <b>D waiting ↑</b></div>
    <div i-carbon:arrow-right class="ts-a" />
    <div class="ts-dst" style="--c: #b0ddff">DECODE / HBM</div>
  </div>
  <div class="ts-row">
    <div class="ts-sig">queues flat + <b>transfer p99 ↑</b></div>
    <div i-carbon:arrow-right class="ts-a" />
    <div class="ts-dst" style="--c: #ffa35f">NIXL / KV HANDOFF</div>
  </div>
  <div class="ts-row">
    <div class="ts-sig"><b>tok/s ↓</b> + <b>rank skew ↑</b></div>
    <div i-carbon:arrow-right class="ts-a" />
    <div class="ts-dst" style="--c: #2ee59d">GPU / PLACEMENT</div>
  </div>
</div>

<div class="ts-foot">
  <div i-carbon:warning style="color: #ffc217; flex: none; margin-top: 3px" />
  <div>Two signals, never one. A single metric moving is <b>ambiguous by construction</b> — it is the <b>combination</b> that is specific enough to pick a page. And the arrow only picks the page; the proof happens after you open it.</div>
</div>

<style>
.tsg { display: grid; grid-template-columns: 1fr 1fr; gap: 9px 18px; }
.ts-row {
  display: flex;
  align-items: center;
  gap: 11px;
  padding: 11px 15px;
  border: 1px solid #ffffff1e;
  border-radius: 11px;
  background: #ffffff07;
}
.ts-sig { flex: 1; font-size: 13px; opacity: 0.9; }
.ts-sig b { color: #ffffffee; }
.ts-a { color: #ffffff40; flex: none; }
.ts-dst {
  flex: none;
  padding: 3px 11px;
  border-radius: 7px;
  border: 1px solid color-mix(in srgb, var(--c) 45%, transparent);
  background: color-mix(in srgb, var(--c) 12%, transparent);
  color: var(--c);
  font-size: 11.5px;
  font-weight: 700;
  letter-spacing: 0.03em;
}
.ts-foot {
  display: flex;
  gap: 10px;
  margin-top: 16px;
  padding: 13px 17px;
  border: 1px solid #ffc21735;
  border-radius: 11px;
  background: #ffc2170a;
  font-size: 14px;
  line-height: 1.6;
}
</style>
---
layout: section
glowSeed: 260
---

# Demo

<div text-2xl op-70 mt-3>Follow the first broken boundary</div>
---
layout: default
glowSeed: 300
---

# Follow One Request Until the Owner Changes

<script setup>
const demoPoster = `${import.meta.env.BASE_URL}demo-poster.jpg`
</script>

<div text-lg op-70 mt-1 mb-4>Signal → boundary → action → validation, in one continuous view</div>

<div flex gap-6 items-start>

<div style="flex: 0 0 300px">
  <div class="dm">
    <div class="dm-h"><span class="dm-n">1</span><span class="dm-t">Signal</span></div>
    <div class="dm-d">TTFT tail rises, TPOT holds. Eight entry signals, one of them moves.</div>
  </div>
  <div class="dm hot">
    <div class="dm-h"><span class="dm-n">2</span><span class="dm-t">Boundary</span></div>
    <div class="dm-d">Prefill waiting rises <b>first</b>; Decode stays bounded. The boundary picks itself.</div>
  </div>
  <div class="dm">
    <div class="dm-h"><span class="dm-n">3</span><span class="dm-t">Action</span></div>
    <div class="dm-d">One change, same demand. Rebalance toward the constrained stage.</div>
  </div>
  <div class="dm">
    <div class="dm-h"><span class="dm-n">4</span><span class="dm-t">Validation</span></div>
    <div class="dm-d">Keep it only if <b>all four guardrails</b> pass — otherwise roll back.</div>
  </div>
</div>

<div style="flex: 1; min-width: 0">
  <SlidevVideo
    autoplay
    controls
    muted
    autoreset="slide"
    :poster="demoPoster"
    :print-poster="demoPoster"
    class="demo-vid"
  >
    <source src="/demo.mp4" type="video/mp4">
  </SlidevVideo>
  <div class="demo-cav">
    <div i-carbon:information style="color: #ffa35f; flex: none; margin-top: 2px" />
    <span>Controlled replay on a demo environment · <b>3:35</b> · request-path signals are measured, scenario is scripted</span>
  </div>
</div>

</div>

<style>
.dm {
  padding: 9px 13px;
  border: 1px solid #ffffff1e;
  border-radius: 11px;
  background: #ffffff07;
  margin-bottom: 8px;
}
.dm:last-child { margin-bottom: 0; }
.dm.hot { border-color: #ffc21750; background: #ffc21710; }
.dm-h { display: flex; align-items: center; gap: 9px; }
.dm-n {
  flex: none;
  width: 21px;
  height: 21px;
  line-height: 21px;
  text-align: center;
  border-radius: 50%;
  background: #ffffff14;
  font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
  font-size: 11px;
  font-weight: 700;
}
.dm.hot .dm-n { background: #ffc21728; color: #ffc217; }
.dm-t { font-size: 15px; font-weight: 600; }
.dm-d { font-size: 11.5px; line-height: 1.45; opacity: 0.75; margin-top: 4px; }
.demo-vid {
  width: 100%;
  height: auto;
  max-height: 352px;
  object-fit: contain;
  border-radius: 12px;
  border: 1px solid #ffffff26;
  background: #000;
  box-shadow: 0 8px 34px #0006;
}
.demo-cav {
  display: flex;
  gap: 8px;
  margin-top: 8px;
  font-size: 11.5px;
  line-height: 1.5;
  opacity: 0.62;
}
</style>
---
layout: section
glowSeed: 168
---

# Inside the engine

<div text-2xl op-70 mt-3>Proof must change the action</div>
---
layout: default
glowSeed: 134
---

# Four Things Inflate a Prefill TTFT

<div text-lg op-70 mt-1 mb-3>Two are the request's own work. Two belong to somebody else.</div>

<div flex gap-5 items-start>

<div style="flex: 1.02">
  <div class="pf-h"><span class="pf-n own">OWN WORK</span>What this request must compute</div>

  <div class="pf-card">
    <div class="pf-t"><span class="pf-i">1</span>Uncached token volume</div>
    <div class="pf-d">Cost tracks <b>computed tokens</b>, not request count. A reuse drop turns the same RPS into several times the work — and the request-rate panel never moves.</div>
  </div>

  <div class="pf-card">
    <div class="pf-t"><span class="pf-i">2</span>Position — later tokens cost more</div>
    <div class="pf-chunks">
      <div v-for="k in 14" :key="k" class="pf-bar" :style="{ height: `${13 + k * 4.4}px` }" />
    </div>
    <div class="pf-axis"><span>chunk 1</span><span>chunk 14</span></div>
    <div class="pf-d">Every token attends to all tokens before it, so cost per chunk <b>grows with position</b>. Doubling a prompt more than doubles the work.</div>
    <div class="pf-cav">schematic · attention term only</div>
  </div>
</div>

<div style="flex: 1.18">
  <div class="pf-h"><span class="pf-n other">SOMEBODY ELSE'S</span>What this request waits behind</div>

  <div class="pf-card hot">
    <div class="pf-t"><span class="pf-i">3</span>Head-of-line blocking</div>
    <CostBars
      :max="10.4"
      unit=" s"
      :rows="[
        { name: 'R1 · uncached', sub: '32K prompt, 0% reuse',
          segs: [
            { label: '', value: 0.2, color: '#ffffff26' },
            { label: 'prefill compute', value: 8.0, color: '#ffa35f' },
          ] },
        { name: 'R2 · 90% cached', sub: 'needs only 1/10 the compute', bad: true,
          segs: [
            { label: 'waiting behind R1', value: 8.2, color: '#ffffff26' },
            { label: '', value: 0.8, color: '#2ee59d' },
          ] },
      ]"
    />
    <div class="pf-punch">
      R2's <b>own</b> work is 0.8 s. Its TTFT is <b style="color:#ff8f8f">9.0 s</b> —
      <b>91% of it is R1's prompt</b>. A cache hit cannot save a request that is stuck in line.
    </div>
    <div class="pf-sig">
      <div i-carbon:search style="color: #b0ddff; flex: none; margin-top: 2px" />
      <div>Visible only if <code>request_queue_time</code> is split from <code>request_prefill_time</code> — aggregate TTFT shows a slow request, the split shows <b>whose fault it was</b>.</div>
    </div>
  </div>
  <div class="pf-knob">
    <div class="pf-kt"><span class="pf-i">4</span>Chunk size — the knob that trades ③ against ①②</div>
    <div class="pf-kd">
      <b>Small</b> — long prompts interleave, R2 served sooner, more per-iteration overhead.
      <b>Large</b> — higher throughput, but one prompt owns the iteration.
      <br>
      Same 144K prompt: <b style="color:#ff8f8f">72.7 s</b> at chunk 512 vs <b style="color:#2ee59d">35.8 s</b> at 8192 —
      <b style="color:#ffc217">2× from one parameter.</b>
    </div>
  </div>
</div>

</div>

<style>
.pf-h {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 12.5px;
  opacity: 0.72;
  margin-bottom: 6px;
}
.pf-n {
  padding: 2px 10px;
  border-radius: 999px;
  font-size: 10.5px;
  font-weight: 700;
  letter-spacing: 0.06em;
}
.pf-n.own { background: #ffa35f22; color: #ffa35f; }
.pf-n.other { background: #ff6b6b22; color: #ff8f8f; }
.pf-card {
  padding: 10px 13px;
  border: 1px solid #ffffff1e;
  border-radius: 11px;
  background: #ffffff07;
  margin-bottom: 9px;
}
.pf-card:last-child { margin-bottom: 0; }
.pf-card + .pf-card { margin-bottom: 0; }
.pf-card.hot { border-color: #ff6b6b33; background: #ff6b6b08; }
.pf-t {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14.5px;
  font-weight: 600;
  margin-bottom: 6px;
}
.pf-i {
  flex: none;
  width: 20px;
  height: 20px;
  line-height: 20px;
  text-align: center;
  border-radius: 50%;
  background: #ffc21726;
  color: #ffc217;
  font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
  font-size: 11px;
  font-weight: 700;
}
.pf-d { font-size: 12px; line-height: 1.5; opacity: 0.86; }
.pf-chunks {
  display: flex;
  align-items: flex-end;
  gap: 4px;
  height: 58px;
  margin: 3px 0 2px;
}
.pf-bar {
  flex: 1;
  border-radius: 3px 3px 0 0;
  background: linear-gradient(180deg, #ffa35fcc, #ffa35f33);
  border-top: 2px solid #ffa35f;
}
.pf-axis {
  display: flex;
  justify-content: space-between;
  font-size: 10px;
  opacity: 0.45;
  margin-bottom: 6px;
}
.pf-cav { font-size: 10px; opacity: 0.4; margin-top: 4px; }
.pf-punch {
  margin-top: 8px;
  padding: 9px 12px;
  border-radius: 9px;
  background: #ffffff0b;
  font-size: 12.5px;
  line-height: 1.5;
}
.pf-sig {
  display: flex;
  gap: 8px;
  margin-top: 8px;
  padding-top: 8px;
  border-top: 1px dashed #ffffff1f;
  font-size: 11.5px;
  line-height: 1.5;
  opacity: 0.85;
}
.pf-sig code {
  font-size: 10.5px;
  padding: 1px 4px;
  border-radius: 4px;
  background: #ffffff14;
}
.pf-knob {
  margin-top: 9px;
  padding: 9px 13px;
  border: 1px solid #ffc21735;
  border-radius: 11px;
  background: #ffc2170a;
}
.pf-kt {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  font-weight: 600;
  margin-bottom: 6px;
}
.pf-kd { font-size: 12px; line-height: 1.6; opacity: 0.9; }
</style>
---
layout: default
glowSeed: 204
---

# KV Space Is a Shared Budget

<div text-lg op-70 mt-1 mb-3>Full blocks admission · a fetch reserves before it receives · the budget shrinks silently</div>

<div flex gap-6 items-start>

<div style="flex: 1.06">
  <div text-sm op-60 mb-2>The same GPU KV pool, two states</div>

  <div class="pool">
    <div class="pool-h"><span class="pool-tag ok">healthy</span>admission has headroom</div>
    <div class="pool-bar">
      <div class="seg serve" style="width: 62%"><span>serving</span></div>
      <div class="seg fetch" style="width: 6%" />
      <div class="seg free" style="width: 32%"><span>free</span></div>
    </div>
  </div>

  <div class="pool">
    <div class="pool-h"><span class="pool-tag bad">under pressure</span>same pool, nothing crashed</div>
    <div class="pool-bar">
      <div class="seg serve" style="width: 55%"><span>serving</span></div>
      <div class="seg fetch" style="width: 40%"><span>in-flight fetches</span></div>
      <div class="seg free" style="width: 5%" />
    </div>
  </div>

  <div class="pool-key">
    <div i-carbon:idea style="color: #ffc217; flex: none; margin-top: 3px" />
    <div>
      Free space collapsed to <b>5%</b> — and <b>none of it is serving anyone</b>. The scheduler stops admitting; TTFT climbs on requests that never reached a GPU.
      <br>
      A fetch costs <b>blocks × duration</b>: a 2 s remote read holds the allocation <b>~13× longer</b> than a 0.15 s local one — 13× the <b>block-seconds</b>, all idle.
    </div>
  </div>
</div>

<div style="flex: 0.94">
  <div class="way">
    <div class="way-h"><span class="way-n">1</span>Full → admission stalls → TTFT</div>
    <div class="way-d">
      Decode-side KV at capacity means the scheduler <b>cannot admit</b>. PD sharpens this: Prefill has finished, the KV is ready to hand off — and there is <b>nowhere to put it</b>. The request waits with <b>its work already done</b> while TTFT counts. Signal: <code>capacity</code> wait, not a slow stage.
    </div>
  </div>

  <div class="way hot">
    <div class="way-h"><span class="way-n">2</span>A fetch reserves before it receives</div>
    <div class="way-d">
      Loading a cached prefix <b>allocates the destination blocks first</b>, then fills them — for a long prompt, a large allocation held for the whole fetch. So a slow fetch is not just slow for <b>that</b> request: it <b>takes space from everyone else</b>.
    </div>
  </div>
</div>

</div>

<div class="budget">
  <div class="budget-h"><span class="way-n">3</span>And the budget itself<br>is smaller than you think</div>
  <div class="budget-row">
    <div class="bd hot">
      <b>MLA under tensor parallel</b>
      <span>Latent KV is shared across heads — <b>nothing to split</b>, so it is <b>replicated on every rank</b>. TP=8 → 8×. Fix: DP attention.</span>
    </div>
    <div class="bd">
      <b>max_model_len</b>
      <span>Reserved against the <b>worst case</b>, not your real p99 input length.</span>
    </div>
    <div class="bd">
      <b>FP16 KV</b>
      <span>FP8 halves it — same GPU, twice the concurrency. Off by default.</span>
    </div>
  </div>
</div>

<style>
.pool { margin-bottom: 9px; }
.pool-h { display: flex; align-items: center; gap: 9px; font-size: 12.5px; opacity: 0.8; margin-bottom: 5px; }
.pool-tag { padding: 1px 9px; border-radius: 999px; font-size: 10.5px; font-weight: 700; }
.pool-tag.ok { background: #2ee59d1e; color: #2ee59d; }
.pool-tag.bad { background: #ff6b6b1e; color: #ff8f8f; }
.pool-bar {
  display: flex;
  height: 32px;
  border-radius: 9px;
  border: 1px solid #ffffff1c;
  overflow: hidden;
}
.seg { display: flex; align-items: center; justify-content: center; overflow: hidden; }
.seg span { font-size: 11.5px; font-weight: 600; white-space: nowrap; }
.seg.serve { background: #2ee59d3a; }
.seg.serve span { color: #b8ffe4; }
.seg.fetch {
  background: repeating-linear-gradient(45deg, #ffa35f55, #ffa35f55 6px, #ffa35f22 6px, #ffa35f22 12px);
  border-left: 1px solid #ffa35f88;
  border-right: 1px solid #ffa35f88;
}
.seg.fetch span { color: #ffd9bb; }
.seg.free { background: #ffffff0d; }
.seg.free span { color: #ffffff88; }
.pool-note {
  margin-top: 6px;
  padding: 8px 12px;
  border: 1px solid #ff6b6b30;
  border-radius: 10px;
  background: #ff6b6b08;
  font-size: 12.5px;
  line-height: 1.55;
}
.pool-key {
  display: flex;
  gap: 9px;
  margin-top: 7px;
  padding: 8px 12px;
  border: 1px solid #ffc21735;
  border-radius: 10px;
  background: #ffc2170a;
  font-size: 12px;
  line-height: 1.5;
}
.way {
  padding: 9px 13px;
  border: 1px solid #ffffff1e;
  border-radius: 11px;
  background: #ffffff07;
  margin-bottom: 10px;
}
.way.hot { border-color: #ffa35f38; background: #ffa35f09; margin-bottom: 0; }
.way-h { margin-bottom: 5px; }
.way-h { display: flex; align-items: center; gap: 8px; font-size: 14.5px; font-weight: 600; margin-bottom: 6px; }
.way-n {
  flex: none;
  width: 21px;
  height: 21px;
  line-height: 21px;
  text-align: center;
  border-radius: 50%;
  background: #ffc21726;
  color: #ffc217;
  font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
  font-size: 11px;
  font-weight: 700;
}
.way-d { font-size: 11.5px; line-height: 1.5; opacity: 0.88; }
.way-d code { font-size: 11.5px; padding: 1px 5px; border-radius: 4px; background: #ffffff14; }
.budget {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-top: 9px;
  padding: 9px 13px;
  border: 1px solid #ffc21735;
  border-radius: 11px;
  background: #ffc2170a;
}
.budget-h {
  flex: 0 0 168px;
  display: flex;
  align-items: flex-start;
  gap: 8px;
  font-size: 13px;
  font-weight: 600;
  line-height: 1.35;
}
.budget-row { flex: 1; display: flex; gap: 9px; min-width: 0; }
.bd {
  flex: 1;
  min-width: 0;
  padding: 7px 11px;
  border-radius: 9px;
  border: 1px solid #ffffff18;
  background: #ffffff08;
  font-size: 11px;
  line-height: 1.45;
}
.bd.hot { border-color: #ffa35f45; background: #ffa35f10; }
.bd > b { display: block; font-size: 12px; margin-bottom: 2px; }
.bd.hot > b { color: #ffa35f; }
.bd span { opacity: 0.86; }
</style>
---
layout: default
glowSeed: 30
---

# KV Transfer — Zero Bytes Looks Like a Fast Transfer

<div text-lg op-70 mt-1 mb-3>The only stage that exists because of PD disaggregation — and the one nobody owns alone</div>

<StageFlow
  compact
  :stages="[
    { id: 'p', name: 'Prefill', sub: 'produces KV', icon: 'i-carbon:model-alt' },
    { id: 'kv', name: 'KV Handoff', sub: 'ready → transfer → admitted', icon: 'i-carbon:data-share' },
    { id: 'd', name: 'Decode', sub: 'consumes KV', icon: 'i-carbon:chat-bot' },
  ]"
  :highlight="['kv']"
/>

<div flex gap-5 mt-4 items-stretch>

<div style="flex: 1.25">
  <div class="tx-steps">
    <div class="tx-s">
      <div class="tx-n">1</div>
      <div class="tx-b">
        <b>Did bytes move at all?</b>
        <span><code>agent_tx_bytes</code> · descriptors · P/D role</span>
        <em>Zero bytes with an expected handoff → connector, lease, or routing. Every latency panel stays green.</em>
      </div>
    </div>
    <div class="tx-s">
      <div class="tx-n">2</div>
      <div class="tx-b">
        <b>How fast, at what payload size?</b>
        <span><code>agent_xfer_time_us</code> p99 · bytes per transfer</span>
        <em>High tail + small payloads → fragmentation, protocol, or a non-GDR path. Not bandwidth.</em>
      </div>
    </div>
    <div class="tx-s">
      <div class="tx-n">3</div>
      <div class="tx-b">
        <b>Did it complete?</b>
        <span><code>agent_errors_total</code> · expired requests</span>
        <em>Silent expiry shows up as a Prefill queue — never as a transfer error.</em>
      </div>
    </div>
  </div>
</div>

<div style="flex: 0.85">
  <div class="tx-trap">
    <div class="tx-th"><div i-carbon:warning-alt-filled style="color: #ffc217" />What the trap looks like</div>
    <div class="tx-tiles">
      <div class="tx-tile"><span>KV transfer p99</span><b style="color:#2ee59d">0 ms</b><i>green</i></div>
      <div class="tx-tile"><span>transfer errors</span><b style="color:#2ee59d">0</b><i>green</i></div>
      <div class="tx-tile bad"><span>bytes transferred</span><b style="color:#ff6b6b">0</b><i>flat</i></div>
      <div class="tx-tile bad"><span>TTFT p95</span><b style="color:#ff6b6b">↑↑</b><i>red</i></div>
    </div>
    <div class="tx-td">Two green panels, one flat line. Nothing was transferred, so nothing was slow — and Decode recomputed every prefix.</div>
  </div>
</div>

</div>

<div class="tx-foot">
  <div i-carbon:arrow-right style="color: #ffa35f; flex: none; margin-top: 3px" />
  <div>Order matters: <b>bytes → transfer time → failures / expiry</b>. Checking speed before movement is the most common wasted hour here. Checklist in Backup B2.</div>
</div>

<style>
.tx-steps { display: flex; flex-direction: column; gap: 7px; }
.tx-s {
  display: flex;
  gap: 10px;
  padding: 7px 12px;
  border: 1px solid #ffa35f30;
  border-radius: 11px;
  background: #ffa35f08;
}
.tx-n {
  flex: none;
  width: 22px;
  height: 22px;
  line-height: 22px;
  text-align: center;
  border-radius: 50%;
  background: #ffa35f22;
  color: #ffa35f;
  font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
  font-size: 11.5px;
  font-weight: 700;
}
.tx-b { display: flex; flex-direction: column; gap: 1px; font-size: 12.5px; }
.tx-b b { font-size: 13px; }
.tx-b span { font-size: 11px; opacity: 0.6; font-family: ui-monospace, SFMono-Regular, Menlo, monospace; }
.tx-b code { font-size: 11px; }
.tx-b em { font-style: normal; font-size: 11.5px; line-height: 1.45; opacity: 0.85; margin-top: 1px; }
.tx-trap {
  height: 100%;
  padding: 11px 14px;
  border: 1px solid #ffc21735;
  border-radius: 11px;
  background: #ffc2170a;
}
.tx-th { display: flex; align-items: center; gap: 7px; font-size: 14.5px; font-weight: 600; margin-bottom: 9px; }
.tx-tiles { display: grid; grid-template-columns: 1fr 1fr; gap: 7px; }
.tx-tile {
  display: flex;
  flex-direction: column;
  padding: 6px 10px;
  border-radius: 8px;
  border: 1px solid #ffffff1c;
  background: #ffffff09;
}
.tx-tile.bad { border-color: #ff6b6b3a; background: #ff6b6b0c; }
.tx-tile span { font-size: 10.5px; opacity: 0.6; }
.tx-tile b { font-family: ui-monospace, SFMono-Regular, Menlo, monospace; font-size: 16px; line-height: 1.2; }
.tx-tile i { font-style: normal; font-size: 10px; opacity: 0.5; }
.tx-td { margin-top: 9px; font-size: 12px; line-height: 1.5; opacity: 0.88; }
.tx-foot {
  display: flex;
  gap: 10px;
  margin-top: 9px;
  padding: 9px 15px;
  border: 1px solid #ffa35f35;
  border-radius: 11px;
  background: #ffa35f0a;
  font-size: 13.5px;
  line-height: 1.55;
}
</style>
---
layout: default
glowSeed: 122
---

# A Diagnosis Is Useful Only If It Predicts a Change

<div text-lg op-70 mt-1 mb-5>Same workload · one change · one keep-or-rollback gate</div>

<LoopDiagram
  :steps="[
    { no: '1', name: 'Observe', detail: 'TTFT ↑ · P waiting ↑<br>D waiting low' },
    { no: '2', name: 'Hypothesis', detail: 'long-input Prefill<br>capacity pressure' },
    { no: '3', name: 'One change', detail: 'add P <b>or</b> scheduler A/B<br><b>never both</b>' },
    { no: '4', name: 'Watch', detail: 'P queue · TTFT tail<br>D wait · tok/s · KV' },
    { no: '5', name: 'Validate', detail: 'queue slope ↓<br>tail improves' },
  ]"
  keep-if="P queue flattens · TTFT tail improves · <b>and no new pressure appears downstream</b>"
  rollback-if="Decode / KV pressure rises · <b>or</b> total tok/s falls — even if TTFT improved"
/>

<div class="vg">
  <div i-carbon:idea style="color: #ffc217; flex: none; margin-top: 3px" />
  <div>The rollback condition is the part teams skip. <b>A change that improves TTFT while total throughput falls is not a fix</b> — it moved the cost somewhere the alert does not look. Write the rollback condition down <b>before</b> you make the change, not after.</div>
</div>

<style>
.vg {
  display: flex;
  gap: 10px;
  margin-top: 16px;
  padding: 13px 17px;
  border: 1px solid #ffc21735;
  border-radius: 11px;
  background: #ffc2170a;
  font-size: 14px;
  line-height: 1.6;
}
</style>
---
layout: section
glowSeed: 168
---

# Cases

<div text-2xl op-70 mt-3>Two incidents, one diagnosis pattern</div>

<div mt-8 text-lg op-60 style="max-width: 700px; line-height: 1.6">
  Observability should not stop at <i>what went wrong</i>. It should tell us <b>what to change</b>.
</div>
---
layout: default
glowSeed: 214
---

# Case 1 — A Long Prompt Blocked the Cached Ones

<div text-lg op-70 mt-1 mb-3>The requests that needed the least work waited the longest</div>

<div flex gap-6 items-start>

<div style="flex: 0.96">
  <div class="sg">
    <div class="sg-r"><div class="sg-l">Health</div><div class="sg-v">ready · errors · routing</div><div class="sg-s ok">stable</div></div>
    <div class="sg-r hot"><div class="sg-l">User</div><div class="sg-v">TTFT p95 ↑ · TPOT p95 flat</div><div class="sg-s bad">split</div></div>
    <div class="sg-r hot"><div class="sg-l">Cache</div><div class="sg-v">prefix hit rate <b>unchanged</b></div><div class="sg-s key">odd</div></div>
    <div class="sg-r hot"><div class="sg-l">Engine</div><div class="sg-v">Prefill waiting <b>1 → 150</b></div><div class="sg-s bad">rising</div></div>
    <div class="sg-r hot"><div class="sg-l">Split</div><div class="sg-v"><code>queue_time</code> ≫ <code>prefill_time</code></div><div class="sg-s key">decisive</div></div>
  </div>

  <div text-sm op-60 mt-4 mb-2>A 90%-cached request, before and after the fix</div>
  <CostBars
    :max="9.4"
    unit=" s"
    :rows="[
      { name: 'Before', sub: '90% reuse — 0.8 s of its own work', bad: true,
        segs: [
          { label: 'behind a long prompt', value: 8.2, color: '#ff6b6b' },
          { label: '', value: 0.8, color: '#2ee59d' },
        ] },
      { name: 'After', sub: 'own lane at the router · bounded depth',
        segs: [
          { label: '', value: 0.3, color: '#ff6b6b55' },
          { label: '', value: 0.8, color: '#2ee59d' },
        ] },
    ]"
  />
  <div text-xs op-45 mt-1>same worked example as the mechanism page · illustrative</div>
</div>

<div style="flex: 1.04">
  <CaseStory
    saw="TTFT p95 spiked, TPOT flat. Prefix hit rate <b>unchanged</b> — the <b>cheapest</b> requests were the ones waiting. Splitting <code>queue_time</code> from <code>prefill_time</code> showed queue time dominating."
    meant="<b>Head-of-line blocking</b>, not capacity. A few very long uncached prompts owned the iteration. <b>A cache hit cannot save a request stuck in line</b>: 90% reuse, 9 s TTFT — 8 s of it somebody else's prompt."
    changed="An <b>admission queue at the router</b>, in front of the engine: classify by expected cost (prefix-hit estimate + prompt length), give the <b>cached class its own lane</b>, <b>bound every class's depth</b>. Chunked prefill second."
    verified="Cached-class TTFT back to ~<b>its own work time</b> · depth bounded · <b>no GPUs added</b>"
    rollback="uncached class starves or total tok/s falls → rebalance weights"
  />
</div>

</div>

<style>
.sg { display: flex; flex-direction: column; gap: 5px; }
.sg-r {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 6px 12px;
  border: 1px solid #ffffff18;
  border-radius: 9px;
  background: #ffffff07;
  font-size: 12.5px;
}
.sg-r.hot { border-color: #ffc21745; background: #ffc21710; }
.sg-l { flex: 0 0 62px; opacity: 0.6; font-size: 11.5px; }
.sg-v { flex: 1; font-weight: 600; color: #ffffffe0; }
.sg-v code { font-size: 11px; padding: 1px 5px; border-radius: 4px; background: #ffffff16; font-weight: 400; }
.sg-s { flex: none; padding: 1px 9px; border-radius: 999px; font-size: 10.5px; font-weight: 600; }
.sg-s.ok { background: #2ee59d1e; color: #2ee59d; }
.sg-s.bad { background: #ff6b6b1e; color: #ff8f8f; }
.sg-s.key { background: #ffc2172a; color: #ffc217; }
</style>
---
layout: default
glowSeed: 146
---

# Case 2 — The GPUs Are Present. Capacity Is Not.

<div text-lg op-70 mt-1 mb-3>TPOT rose while TTFT stayed flat. One rank had fallen behind its peers.</div>

<div flex gap-6 items-start>

<div style="flex: 0.9">
  <div class="c3-d">
    <div class="c3-r"><span>Output tok/s</span><b>16K</b><div i-carbon:arrow-right class="c3-a" /><b class="bad">10K</b></div>
    <div class="c3-r"><span>TPOT</span><b>21 ms</b><div i-carbon:arrow-right class="c3-a" /><b class="bad">47 ms</b></div>
    <div class="c3-r flat"><span>GPU count</span><b>unchanged — not a capacity incident</b></div>
  </div>
  <div text-sm op-60 mt-2 mb-2>Per-rank GPU utilization · same TP group, same window</div>
  <RankBars
    :height="92"
    :ranks="[
      { name: 'Rank 0', value: 88 },
      { name: 'Rank 1', value: 91 },
      { name: 'Rank 2', value: 34, sub: 'straggler', bad: true },
      { name: 'Rank 3', value: 89 },
    ]"
  />
  <div class="c3-agg">Aggregate reads <b>75%</b> — a perfectly ordinary number. The average hides the slow member.</div>

  <div class="c3-fork">
    <div i-carbon:warning style="color: #ffc217; flex: none; margin-top: 2px" />
    <div><b>Memory-bound looks identical at the entry.</b> Symmetric ranks + high DRAM/HBM → add capacity. One skewed rank → replicas <b>just cost more</b>.</div>
  </div>
</div>

<div style="flex: 1.1">
  <CaseStory
    saw="<b>TPOT rose while TTFT stayed flat</b> — first token on time, every token after it late. KV pressure and waiting rising."
    meant="One rank at <b>34%</b> against 88–91%. A TP group runs at its <b>slowest member</b>: iteration ↑ → token rate ↓ → requests live longer → KV stays resident → admission ↓ → waiting ↑. <b>KV pressure was the last link — and the first thing that alerted.</b>"
    changed="<b>DCGM</b> found the outlier GPU → <b>NCCL init log</b> mapped rank ↔ GPU (a software index — it moves after restarts) → hardware fault: <b>isolate the device</b>; topology fault: <b>re-place the whole TP group</b>"
    verified="rank skew narrowed · TPOT and tok/s recovered · waiting fell <b>with no capacity added</b>"
    rollback="all ranks wait <b>together</b> → never a straggler; escalate back to scheduler / transfer"
  />
</div>

</div>

<style>
.c3-d { display: flex; flex-direction: column; gap: 6px; }
.c3-r {
  display: flex;
  align-items: center;
  gap: 9px;
  padding: 7px 13px;
  border: 1px solid #ffffff1e;
  border-radius: 10px;
  background: #ffffff07;
  font-size: 12.5px;
}
.c3-r > span { opacity: 0.55; font-size: 11.5px; flex: 0 0 92px; }
.c3-r b { font-family: ui-monospace, SFMono-Regular, Menlo, monospace; font-size: 14.5px; }
.c3-r b.bad { color: #ff6b6b; }
.c3-a { color: #ffffff45; flex: none; font-size: 13px; }
.c3-r.flat b { font-family: inherit; font-size: 12.5px; opacity: 0.8; font-weight: 500; }
.c3-agg {
  margin-top: 8px;
  padding: 8px 12px;
  border: 1px solid #ffc21735;
  border-radius: 10px;
  background: #ffc2170a;
  font-size: 12.5px;
  line-height: 1.55;
}
.c3-fork {
  display: flex;
  gap: 9px;
  margin-top: 8px;
  padding: 8px 12px;
  border: 1px solid #ffc21735;
  border-radius: 10px;
  background: #ffc2170a;
  font-size: 12.5px;
  line-height: 1.55;
}
</style>
---
layout: default
glowSeed: 238
---

# Signals → Proof → One Reversible Action

<div text-lg op-70 mt-1 mb-4>The whole method on one page. Photograph this one.</div>

<div class="pb">
  <div class="pb-head">
    <div>Layer</div><div>Signal combination</div><div>Prove next</div><div>Candidate action</div>
  </div>
  <div class="pb-row">
    <div class="pb-l" style="--c: #ff6b6b">Entry</div>
    <div class="pb-s">ready ↓ + 5xx / timeout ↑</div>
    <div class="pb-p">endpoint · route · upstream log</div>
    <div class="pb-a">restore route / endpoint<br><i>skip GPU tuning entirely</i></div>
  </div>
  <div class="pb-row">
    <div class="pb-l" style="--c: #ffc217">Prefill</div>
    <div class="pb-s">TTFT ↑ + P wait ↑<br><i>long prompts · P KV high</i></div>
    <div class="pb-p">capacity reason · P token service rate</div>
    <div class="pb-a">add P capacity / retune P:D<br><i>then benchmark scheduler</i></div>
  </div>
  <div class="pb-row">
    <div class="pb-l" style="--c: #2ee59d">Decode</div>
    <div class="pb-s">TPOT ↑ + D wait ↑<br><i>preemption · D KV high</i></div>
    <div class="pb-p">output shape · D service · HBM</div>
    <div class="pb-a">add D capacity<br><i>cap context / concurrency</i></div>
  </div>
  <div class="pb-row">
    <div class="pb-l" style="--c: #b0ddff">Remote KV</div>
    <div class="pb-s">hit ↑ <b>but</b> TTFT ↑</div>
    <div class="pb-p">retrieve + to-GPU vs recompute</div>
    <div class="pb-a">selective remote reuse<br><i>hot tier / recompute fallback</i></div>
  </div>
  <div class="pb-row">
    <div class="pb-l" style="--c: #ffa35f">P → D</div>
    <div class="pb-s">expected handoff<br><i>bytes = 0 or expiry ↑</i></div>
    <div class="pb-p">connector · role · lease · routing</div>
    <div class="pb-a">fix connector / lease<br><i>or routing</i></div>
  </div>
  <div class="pb-row">
    <div class="pb-l" style="--c: #c9a7ff">Rank / fabric</div>
    <div class="pb-s">tok/s ↓ + one GPU skew<br><i>XID / ECC or collective tail ↑</i></div>
    <div class="pb-p">rank map · DCGM · NCCL topology</div>
    <div class="pb-a">isolate bad GPU / node<br><i>or repair placement</i></div>
  </div>
</div>

<div class="pb-foot">
  Every row ends at a <b>reversible</b> action with a rollback condition — never at a dashboard.
</div>

<style>
.pb { border: 1px solid #ffffff1e; border-radius: 12px; overflow: hidden; }
.pb-head, .pb-row {
  display: grid;
  grid-template-columns: 118px 1.15fr 1fr 1.1fr;
  gap: 12px;
  padding: 6px 15px;
  align-items: center;
}
.pb-head {
  background: #ffffff0e;
  font-size: 11.5px;
  font-weight: 700;
  letter-spacing: 0.06em;
  opacity: 0.7;
  text-transform: uppercase;
}
.pb-row { border-top: 1px solid #ffffff12; font-size: 12.5px; line-height: 1.4; }
.pb-row:nth-child(even) { background: #ffffff05; }
.pb-l {
  padding: 2px 10px;
  border-radius: 6px;
  border: 1px solid color-mix(in srgb, var(--c) 45%, transparent);
  background: color-mix(in srgb, var(--c) 13%, transparent);
  color: var(--c);
  font-size: 12px;
  font-weight: 700;
  text-align: center;
}
.pb-s b { color: #ffc217; }
.pb-s i, .pb-a i { font-style: normal; opacity: 0.6; font-size: 11.5px; }
.pb-p { opacity: 0.82; }
.pb-foot {
  margin-top: 10px;
  padding: 9px 16px;
  border-left: 3px solid #2ee59d;
  background: #2ee59d0a;
  font-size: 14px;
}
</style>
---
layout: default
glowSeed: 108
---

# Key Takeaways

<div text-lg op-70 mt-1 mb-4>“The best dashboard is the one you actually use.” — so you never have to stare at it at 2 AM</div>

<div flex gap-6 items-start>

<div style="flex: 1">
  <div class="kt">
    <div class="kt-c">
      <div class="kt-n">1</div>
      <div class="kt-b">
        <div class="kt-t">TTFT tells you <span style="color:#ffc217">that</span> — never <span style="color:#ffc217">where</span></div>
        <div class="kt-d">It is the sum of four stages. Use it to <b>open</b> an investigation, never to <b>close</b> one.</div>
      </div>
    </div>
    <div class="kt-c">
      <div class="kt-n">2</div>
      <div class="kt-b">
        <div class="kt-t">More dashboards ≠ more visibility</div>
        <div class="kt-d">Eight entry signals decide which page opens next. Everything else stays <b>one click away</b>.</div>
      </div>
    </div>
    <div class="kt-c">
      <div class="kt-n">3</div>
      <div class="kt-b">
        <div class="kt-t">A diagnosis must predict a change</div>
        <div class="kt-d">One change, one validation gate, one rollback condition — <b>written before</b> touching anything.</div>
      </div>
    </div>
  </div>
</div>

<div style="flex: 0 0 226px" flex flex-col items-center>
  <img src="/overtime.gif" class="kt-gif">
  <div class="kt-cap">so nobody gets paged at 2 AM</div>
</div>

</div>

<style>
.kt { display: flex; flex-direction: column; gap: 12px; }
.kt-c {
  display: flex;
  gap: 13px;
  padding: 14px 17px;
  border: 1px solid #ffffff1e;
  border-radius: 13px;
  background: #ffffff07;
}
.kt-n {
  flex: none;
  width: 32px;
  height: 32px;
  line-height: 32px;
  text-align: center;
  border-radius: 9px;
  background: #ffc21720;
  color: #ffc217;
  font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
  font-size: 16px;
  font-weight: 700;
}
.kt-t { font-size: 17.5px; font-weight: 600; line-height: 1.3; }
.kt-d { font-size: 13px; line-height: 1.6; opacity: 0.82; margin-top: 5px; }
.kt-gif {
  width: 200px;
  border-radius: 14px;
  border: 1px solid #ffffff1f;
}
.kt-cap { font-size: 11.5px; opacity: 0.5; margin-top: 9px; text-align: center; }
</style>
---
layout: default
glowSeed: 156
---

# Community Outlook

<div text-lg op-70 mt-1 mb-5>None of this needs a new agent — it needs the existing layers to agree</div>

<div class="co">
  <div class="co-c">
    <div class="co-h"><div i-carbon:model-alt style="color: #2ee59d" />Request context</div>
    <div class="co-p">vLLM · SGLang</div>
    <div class="co-d">Per-request latency, queue, token shape, and traces <b>already exist</b>.</div>
  </div>
  <div class="co-c">
    <div class="co-h"><div i-carbon:connect style="color: #b0ddff" />Portable semantics</div>
    <div class="co-p">OpenTelemetry GenAI</div>
    <div class="co-d">Shared field names are <b>still evolving</b>; instrument now without hard-coding alerts to them.</div>
  </div>
  <div class="co-c">
    <div class="co-h"><div i-carbon:router style="color: #ffc217" />Role-aware control</div>
    <div class="co-p">llm-d · GAIE</div>
    <div class="co-d">P/D roles, queue state, and in-flight tokens <b>already drive</b> routing and autoscaling.</div>
  </div>
  <div class="co-c">
    <div class="co-h"><div i-carbon:data-share style="color: #ffa35f" />KV movement</div>
    <div class="co-p">NIXL · external KV tiers</div>
    <div class="co-d">Hit, bytes, latency, and failure make the <b>PD-only boundary measurable</b>.</div>
  </div>
</div>

<div class="co-foot">
  <div i-carbon:idea style="color: #ffc217; flex: none; margin-top: 3px" />
  <div>The gap is not instrumentation — it is <b>agreement</b>. One request context, shared across layers, ending in one measurable, reversible action.</div>
</div>

<style>
.co { display: grid; grid-template-columns: 1fr 1fr; gap: 13px; }
.co-c {
  padding: 14px 17px;
  border: 1px solid #ffffff1e;
  border-radius: 12px;
  background: #ffffff07;
}
.co-h { display: flex; align-items: center; gap: 8px; font-size: 16px; font-weight: 600; }
.co-p {
  display: inline-block;
  margin: 7px 0;
  padding: 1px 10px;
  border-radius: 999px;
  background: #ffffff12;
  font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
  font-size: 11.5px;
  opacity: 0.85;
}
.co-d { font-size: 12.5px; line-height: 1.6; opacity: 0.85; }
.co-foot {
  display: flex;
  gap: 10px;
  margin-top: 15px;
  padding: 13px 17px;
  border: 1px solid #ffc21735;
  border-radius: 11px;
  background: #ffc2170a;
  font-size: 14px;
  line-height: 1.6;
}
</style>
---
layout: intro
class: px-24
glowSeed: 292
footer: false
---

<div flex flex-col items-center>

<h1 style="font-size: 62px">Q &amp; A</h1>

<div text-xl op-75 mt-2 mb-8>Thank you for your attention</div>

<div flex items-start justify-center gap-16>
  <div flex flex-col items-center>
    <img src="/person/nicole.jpg" w-28 h-28 rounded-full object-cover mb-4>
    <span font-semibold text-xl>Nicole Li</span>
    <div text-sm flex items-center justify-center gap-2 mt-2 op-75>
      <div i-ri:github-fill /><span font-mono>nicole-lihui</span>
    </div>
  </div>
  <div flex flex-col items-center>
    <img src="/person/kebe.jpeg" w-28 h-28 rounded-full object-cover mb-4>
    <span font-semibold text-xl>Kebe Liu</span>
    <div text-sm flex items-center justify-center gap-2 mt-2 op-75>
      <div i-ri:github-fill /><span font-mono>kebe7jun</span>
    </div>
  </div>
  <div flex flex-col items-center>
    <div bg-white p-2 rounded-xl shadow-lg>
      <img src="/kubecon-2026-repo-qr.png" w-28 h-28 alt="Slides and demo repository QR code">
    </div>
    <span font-semibold text-xl mt-4>Slides &amp; Demo</span>
    <div text-sm flex items-center justify-center gap-2 mt-2 op-75>
      <div i-ri:github-fill /><span font-mono>BaizeAI/talks</span>
    </div>
  </div>
</div>

<div mt-9 text-base op-60>DaoCloud &nbsp;·&nbsp; Inference Acceleration Team</div>

<img src="/kubecon-logo.svg" mt-8 style="height: 30px; opacity: 0.5">

</div>
