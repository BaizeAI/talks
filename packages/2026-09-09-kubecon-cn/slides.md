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

<!--
【0:00 – 0:30】

大家好。今天这场分享的题目是 —— Why Your TTFT Lies，为什么你的 TTFT 在说谎。

副标题是：在 PD 分离的推理架构下，怎么用一小组跨层指标做诊断。

我们两位来自 DaoCloud 的推理加速团队。今天讲的每一个坑，都是我们自己在生产环境里踩过的。

〔不要念标题，直接翻页〕
-->

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

<!--
【0:30 – 0:50】

简单介绍一下。我是 Nicole，在推理加速团队。这位是 Kebe，高级软件工程师。

我们在生产上运维 PD 分离的 LLM 推理集群。今天不讲论文，讲的是我们被叫起来之后学到的东西。

那就从一次真实的告警说起。
-->

---
layout: section
glowSeed: 120
---

# Background

<div text-2xl op-70 mt-3>TTFT sent us into a maze</div>

<!--
【0:50 – 0:55】

第一部分，背景 —— TTFT 是怎么把我们带进迷宫的。

〔5 秒带过，不要停留〕
-->

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

<!--
【0:55 – 1:55】

上午十一点，TTFT 的 P95 告警红了。

告警阈值是 800 毫秒。而那天的峰值，P95 冲到了 41 分钟，P99 是 42 分钟。影响窗口从十一点一直持续到下午一点零五分。

〔指右边的生产面板〕

现在请看左下角这句话：**均值面板此刻读数是 681 毫秒，是绿的。**

这次事故，在均值那条线上，从头到尾就没有出现过。

这就是「TTFT 说谎」的第一层意思 —— 不是这个数字算错了，而是**你看的那个聚合口径，根本没有记录这件事**。

〔口径提醒：说「均值面板此刻是绿的」，不要说成「事故期间均值是绿的」，两者量纲不同，会被追问〕

好，告警响了。第一反应当然是打开面板。然后呢？
-->

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

<!--
【1:55 – 2:55】

然后就是这一页。

所有人都会问同一个问题：到底哪儿坏了？是网关，是 Prefill？是 KV 用满了，还是 KV 传输？是 GPU，还是网络？

还是说 —— TTFT 在骗我们？

右边这十二块，是我们当时真实的面板清单。每一块都在采数据，每一块的数字都是对的。

**但是没有任何一块告诉你：下一步该看哪儿。**

这就是今天这场要解决的问题。我们不缺指标，我们缺的是「下一步」。

〔停两秒，让问号沉一下〕

那为什么 PD 分离会让这件事变得更难？
-->

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

<!--
【2:55 – 3:55】

因为 TTFT 根本不是一个测量值，**它是一个和**。

它等于：网关的时间，加上 Prefill 的时间，加上 KV 传输的时间，再加上第一个 decode token 的时间。

四项里任何一项炸了，这个和都会涨。但是**这个和永远不会告诉你是哪一项**。

中间这一段，KV Transfer，我要特别强调。

在单体引擎里，这一项**根本不存在**。它是 PD 分离新增出来的一个边界 —— 而且这个边界，两边都不完全拥有它。缓存没命中、对端慢、网络路径走错，全都会落在这里。

右下这句话是全场的题眼：每一层都在测，但每一层测的是**自己那一段**。**没有人测层与层之间的间隙** —— 而分钟级的时间，就消失在那些间隙里。

那回到刚才那次告警，我们是怎么定位的？
-->

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

<!--
【3:55 – 5:10】

我们没有继续盯着 TTFT 看，而是**沿着请求路径走了一遍**。五行，从上往下：

业务网关，延迟稳定 —— 健康，排除。

PD 路由，队列很低 —— 健康，排除。

Prefill，等待请求数从 1 冲到 150 —— **第一个异常边界，就是它。**

Decode，等待是 0，在跑的只有 0 到 10 个 —— 说明下游没有饿着，问题在它前面。

KV 缓存，驱逐每秒 689 次 —— 可疑，先记下来。

四次读，我们就从「TTFT 高」收敛到了「Prefill」。

〔用词要准，这里是全场诚实度的关键〕

请注意我的用词：这里得到的是**第一个异常边界**，**不是根因**。路径告诉了我们在哪儿，还没告诉我们为什么。

〔最后这句讲慢一点〕

TTFT 告诉我们用户**什么时候**在等。路径告诉我们**在哪儿**等。至于**为什么** —— 后面的案例那一段才会揭晓，而且答案有点出乎意料。

问题是：这一次我们是走运。要想每次都这样，就得把它变成方法。
-->

---
layout: section
glowSeed: 175
---

# Method

<div text-2xl op-70 mt-3>Organize for decisions, reveal detail only when needed</div>

<!--
【5:10 – 5:15】

第二部分，方法。一句话概括：**按决策来组织，需要的时候才展开细节。**

〔5 秒带过〕
-->

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

<!--
【5:15 – 6:30】1.25 分钟

先承认一件事：我们不是没有可观测性，**我们有太多了**。

〔指左边那个抱头的小人〕

V1，组件视图。每一层都有人负责，每一块面板都是对的 —— 但**每一块都只是「局部正确」，没有一块是「第一块该打开的」**。
端到端的请求路径，不在任何人的视图里。这就是那句：**遥测数据到处都是，就是没有第一步。**

V2，我们把它们串成一条链：网关 → Prefill → KV 交接 → Decode。到这一步终于能说清「在哪儿」，但还是说不出「该做什么」。

V3 就是右边那张图 —— **信号 → 证据 → 一个可回滚的动作**，末尾带一道验证门。
图里那四个角色（Model Ops、Engine、SRE、Business）说明同一条路径上，不同的人负责不同的一段。

〔底部这句必须说，否则听众会觉得我们前后矛盾〕

**我们一块面板都没有删。** V1 那些面板全都还在。V3 做的事情只有一件 ——
**决定你打开它们的顺序。**

那八个入口信号是什么？
-->

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

<!--
【6:30 – 7:45】

四组，八个。

第一组，**健康**：还能不能接住流量。可用端点数，错误和超时率。

第二组，**负载**：进来了多少活。请求速率，输入和输出的 token 速率。

第三组，**用户 SLO**：用户等多久。TTFT 和 TPOT 的 p95、p99。

第四组，**PD 阶段**：卡在哪一段。Prefill 等待数，Decode 等待数。

下面这条流程是整套方法的骨架：八个入口常驻屏幕 → 定位到第一个异常边界 → 按需打开一页证据 → 一个可回滚的动作。

〔黄框这条规则一字不差地念〕

**如果一个信号的值，不会改变你的下一步动作，它就不是入口信号。**

其他所有指标不是被删了，是退到了「按需取证」那一层，离你只有一次点击。

〔被问「为什么是 8 不是 10」：四个问题 × 每个两个信号，不是凑数〕

接下来三页，讲这八个信号怎么读。
-->

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

<!--
【7:45 – 8:45】

第一步永远不是「哪个 GPU 慢」，而是 —— **我们还能不能接住流量。**

三个分支：

可用端点掉了，同时 5xx 在涨 → 服务能力问题，去看端点，别碰 GPU。

端点稳定，但 429 在涨 → 准入、配额、容量的问题。

健康指标全都稳定，只有延迟在涨 → 这时候才继续往下走。

〔黄框这句是这一页存在的理由〕

**掉线、被拒、变慢，这三种情况在延迟曲线上长得一模一样。** 但只有第三种值得你去查 GPU。

跳过这一步，就会出现「花一个小时调 batch size，最后发现是一个端点挂了」这种事。这个我们干过。

健康没问题，那就进第二步。
-->

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

<!--
【8:45 – 9:45】

第二步和第三步必须放在一起看，所以我合成了一页。

左边是**流量**：进来了多少活 —— 请求数、输入输出 token 速率、prompt 长度。

右边是**用户感受**：成功率、超时、TTFT、TPOT。

中间这条虚线是重点：**同一个时间窗口。** 分开看这两组数据，你永远建立不了因果关系。

放在一起，就有两条可以直接用的规则：

输入 token 速率或者 prompt 长度在涨，同时 TTFT 在涨 → 下一步看 Prefill。

输出 token 速率或者并发在涨，同时 TPOT 在涨 → 下一步看 Decode。

〔左下这句是个真实的坑，值得讲〕

**这是一个决策视图，不是一个加权健康分。** 很多团队想把这些揉成一个分数，但那恰好抹掉了你最需要的对比 —— **TTFT 涨而 TPOT 平，这个「不一致」本身就是信息。**

〔页脚标了 schematic，是关系示意，一句带过〕

现在我们知道该看 Prefill 还是 Decode 了。第四步，定位到具体边界。
-->

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

<!--
【9:45 – 10:35】

三条规则，很快：

TTFT 涨，加上 Prefill 等待涨 → 去取 Prefill 的证据。

两边队列都平，但传输 p99 涨 → 去验 KV 交接。

TPOT 涨，加上 Decode 等待涨 → 去取 Decode 的证据。

〔但这一页真正要记住的是下面这句〕

**队列不是一起涨的，是有先后的。**

**最先动的那一段，就是边界。** 它下游的全是症状，它上游的已经被排除了。

这也是为什么刚才第七页那次事故，四次读就能收敛 —— 不是我们运气好，是我们只看「谁先动」。

那从信号到证据，这个映射关系是什么？
-->

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

<!--
【10:35 – 11:35】

六行，我挑三行讲，其余你们扫一眼就行。

TTFT 涨 + Prefill 等待涨 → 打开 Prefill / 调度器那一页。

两边队列都平，但传输 p99 涨 → 打开 NIXL / KV 交接。

吞吐降 + 某一张 GPU 利用率偏离 → 打开 GPU / 放置。

〔底部这句有两个点，都要讲〕

**第一，永远是两个信号，不是一个。** 单个指标动是天然有歧义的 —— TTFT 涨可能是任何原因。**是组合，才足够具体到能选出一页。**

**第二，箭头只负责选页，不负责证明根因。** 这句我必须说，它是这套方法诚实的边界。真正的证明，在你打开那一页之后才开始。

〔时间紧张时这一页可以整页跳过，它是最后 Playbook 的子集〕

说了这么多，看一次真实的。
-->

---
layout: section
glowSeed: 260
---

# Demo

<div text-2xl op-70 mt-3>Follow the first broken boundary</div>

<!--
【11:35 – 11:40】

第三部分，Demo。跟着第一个坏掉的边界走一遍。

〔5 秒带过〕
-->

---
layout: default
glowSeed: 300
---

# Follow One Request Until the Owner Changes

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
    poster="/demo-poster.jpg"
    print-poster="/demo-poster.jpg"
    class="demo-vid"
  >
    <source src="/demo.mp4" type="video/mp4">
  </SlidevVideo>
  <div class="demo-cav">
    <div i-carbon:information style="color: #ffa35f; flex: none; margin-top: 2px" />
    <span>Controlled replay on a demo environment · <b>1:24</b> · request-path signals are measured, scenario is scripted</span>
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

<!--
【11:40 – 13:35】视频 1 分 24 秒

先花二十秒说清楚要看什么，否则视频过去了大家抓不住重点。

这段录屏走的就是我们刚才讲的那条路径，四个阶段：

**信号** —— TTFT 尾部在涨，TPOT 稳住。八个入口信号里只有一个动了。

**边界** —— **Prefill 的等待先涨，Decode 一直是有界的。** 边界是自己浮出来的，不是我们猜的。

**动作** —— 一个改动，需求不变：把资源往受约束的那一段挪。

**验证** —— 录屏最后那块叫「Decision checkpoint」，写着**四条护栏全过才保留**：Prefill 等待下降、实测 TTFT 尾部下降、Decode 等待仍然有界、输出 TPM 和完成 RPM 不回退。

〔这一段和第 24 页的验证闭环是同一件事，播完可以点一句：「刚才那四条护栏，就是我们第 24 页说的那道门。」〕

〔画面里的面板文字偏小，需要看细节时点右下角全屏。但**不要指望观众读清面板** —— 靠你的口述带节奏〕

〔诚实口径：页面下方已标注 —— 受控演示环境的回放，请求路径信号是实测的，场景是编排的〕

————————————
放映前检查：
· 文件已在 `public/demo.mp4`（3.1 MB，2160×1350，静音）
· 静音 + autoplay：翻到这页自动播放；离开再回来会从头播
· 若播放失败：跳过这一页，口述上面四个阶段，直接进 Cases 段。**不要在台上调播放器**

【13:35 – 13:45】

第四部分。分钟到底花在哪儿了。

接下来三页，每页一个机制：Prefill、KV 空间、KV 传输。每一个都是 TTFT 上涨的一种原因，而聚合数字看不出来。

Decode 那一层我们放到案例段讲，因为它的**机制就是事故本身**。
-->

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

<!--
【13:45 – 15:00】

Prefill 的 TTFT 被什么撑起来？四件事。**前两件是这个请求自己的活，后两件是别人的活。**

**第一，未缓存的 token 量。** 成本跟着「要算的 token 数」走，**不是跟着请求数走**。复用率一掉，同样的 QPS 就变成好几倍的计算量 —— 而请求速率那块面板，纹丝不动。

**第二，位置。** 每个 token 都要注意到它前面所有的 token，所以**越靠后的 chunk 越贵**。prompt 长度翻倍，工作量涨得比两倍还多。

**第三，队头阻塞** —— 这一条最重要。看这个例子：R2 自己的活只有 0.8 秒，但它的 TTFT 是 9 秒，**其中 91% 是在等 R1 的 prompt。**

**命中率救不了一个排在队里的请求。**

〔下面这行小字要念，它是后面案例的钥匙〕

而且这件事**只有把 request_queue_time 从 request_prefill_time 里拆开才看得见**。聚合的 TTFT 只告诉你「有个请求慢」，拆开了才知道**是谁的错**。

**第四，chunk size** —— 这是唯一一个你能直接调的旋钮。

〔诚实口径：R1/R2 的时间轴和 per-chunk 成本柱是构造示例，说明机制，不是实测；144K / 72.7s / 35.8s 是公开基准，不是我们的数据〕

记住第三条，后面它会变成一个完整的案例。接下来，KV 那一层。
-->

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

<!--
【15:00 – 16:15】

先纠正一个直觉：**KV 空间不是「够不够用」的问题。它是一份被所有请求共享的预算 —— 而 TTFT 在替它买单。**

两条路径。

**第一，满了，准入就停了。** Decode 侧的 KV 到顶，调度器就没法准入新请求。

PD 分离让这一点更尖锐：**Prefill 已经算完了，KV 准备好要交接了 —— 但是没地方放。** 这条请求带着**已经做完的工作**在排队，而 TTFT 还在计时。指标上它表现为 capacity 等待原因，不是某一段变慢。

**第二，取 KV 这个动作，本身要先占住空间。** 加载一段缓存前缀，是**先分配目标 block，再往里填**。长 prompt 就是一大块分配，而且要占住整个取回过程。

所以慢的取回**不只是慢了这一条请求 —— 它把空间从所有人那里拿走了。**

〔指左边两条池子〕

健康的时候空闲还有 32%；压力下空闲塌到 5%，但**塌掉的那部分不是在服务任何人**，是被在途的取回占着的。调度器停止准入，TTFT 涨在那些**根本还没碰到 GPU** 的请求上。

黄框这句是量化落点：**取回的代价是 blocks 乘以时长。** 一次 2 秒的远端读，比 0.15 秒的本地读多占十三倍的时间 —— 同样的空间，十三倍的 block-seconds，而且全程空转。

**第三，预算本身比你以为的小。**

**这一条是我们自己踩的 —— 我们线上跑的就是 MLA 架构的模型。**

MLA 把 K 和 V 压成一个**所有注意力头共享的潜向量**。它省显存的道理就在这儿：不用每个头存一份。

但代价在并行策略上：**张量并行是按头切的，而这里没有头可以切。** 于是这份 KV cache 在**每个 rank 上完整复制一份** —— TP 等于 8，就是八倍的 KV 内存。

**MLA 好不容易省下来的空间，被张量并行原样吐了回去。**

解法是让注意力层走**数据并行**（DP attention），MoE 层走专家并行 —— vLLM 已经支持。

〔如果被问「那你们改了吗、效果如何」：照实答，不要含糊。这一条的价值在于「这个坑真实存在且很少人知道」，不在于我们修得多漂亮〕

另外两格快速带过：max_model_len 是按最坏情况预留的，不是按你的 p99；FP8 KV 能省一半，而且默认是关的。

〔诚实口径：两条池子的占比是机制示意，不是某次事故的实测〕

KV 还要在 P 和 D 之间搬运 —— 那是 PD 分离独有的一层。
-->

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

<!--
【16:15 – 17:15】

这一层是 PD 分离独有的，也是现有的可观测性分享基本没有覆盖的。

三步，**顺序不能乱：先看有没有搬，再看搬得快不快，最后看有没有搬完。**

〔指右边四块面板〕

这就是这一层的陷阱长什么样：

传输 p99 是 0 毫秒，绿的。传输错误 0，绿的。**字节数是一条平线 —— 根本没传。** 而 TTFT 在涨。

**没有传输，自然就没有慢的传输**，所以延迟面板永远是完美的。而 Decode 在默默地重算每一个前缀。这是最阴险的一类故障。

第二步补一句：**延迟必须和 payload 大小一起读。** 尾部高加上包很小，指向的是分片、协议、或者没走 GDR 的路径，**不是带宽不够**。

第三步：**静默过期会表现成 Prefill 队列，永远不会表现成传输错误。** 所以过期计数必须单独看。

在这一层，先查速度是最常见的浪费一小时的做法。

〔时间紧张时这一页压到 40 秒：只讲三步顺序 + 右边四块面板〕

三个机制讲完了。但所有这些证据，最后都要能预测一个变化，否则没有意义。
-->

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

<!--
【17:15 – 18:15】

这一页是整套方法的收口，也是我们和大多数可观测性分享最大的区别 —— **大多数讲到「动作」就停了。**

五步：观察 → 假设 → **一次一个改动** → 观测 → 验证。

〔第三步要重读〕

**一次只改一个，绝不同时改两个。** 同时改两个，你永远不知道是哪个起了作用，下次还得重来。

然后是两道门。

**保留**：队列压平、尾延迟改善，**而且下游没有出现新的压力**。最后半句是关键。

**回滚**：Decode 或者 KV 的压力上升，**或者总吞吐下降 —— 哪怕 TTFT 改善了也要回滚。**

〔黄框这句讲慢一点〕

**TTFT 改善但总吞吐下降，那不是修好了 —— 那是把代价挪到了告警看不见的地方。** 而且回滚条件必须在动手**之前**写下来；事后补的回滚条件，永远会迁就已经做出的改动。

〔重要伏笔，一定要说，它让下一段的第一个案例有戏剧性〕

最后请注意这一页的假设是「长输入导致的 Prefill 容量压力」。**下一段的第一个案例里，这个假设会被这道门否掉。这恰恰是为什么要有门。**
-->

---
layout: section
glowSeed: 168
---

# Cases

<div text-2xl op-70 mt-3>Two incidents, one diagnosis pattern</div>

<div mt-8 text-lg op-60 style="max-width: 700px; line-height: 1.6">
  Observability should not stop at <i>what went wrong</i>. It should tell us <b>what to change</b>.
</div>

<!--
【18:15 – 18:25】

第五部分，案例。两个真实事故，一套诊断模式。

〔这句引言可以念，作为这一段的定调〕

**可观测性不该停在「出了什么问题」，它应该告诉我们「要改什么」。**
-->

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

<!--
【18:25 – 19:40】

第一个案例，就是开场那次告警的下半场。还记得吗 —— Prefill 等待从 1 冲到 150。

左边五行信号。请特别注意**第三行**，这是最反直觉的地方：**前缀命中率没有变化。**

缓存好好的，命中率也没掉。但那些**本该最便宜的请求，恰恰是等得最久的。**

第五行是决定性证据：把 request_queue_time 从 request_prefill_time 里拆出来，**排队时间压倒性地占主导。**

所以结论是：**队头阻塞，不是容量不够。** 几个超长的、未缓存的 prompt 占住了迭代，后面全在等。90% 的复用率，TTFT 还是 9 秒 —— 因为其中 8 秒是别人的 prompt。

〔回收上一页的伏笔，这是全场最有说服力的一段，讲慢一点〕

**回到上一页那道验证门：如果我们当时按「容量压力」的假设去加 Prefill 副本 —— 队列会短一点，但那些命中的请求还是排在长 prompt 后面，总吞吐不会涨，问题不会消失。这个假设，就是被那道门否掉的。**

真正的解法在**路由层**：在引擎前面加一道准入队列。按预期代价分类 —— 前缀命中估计加上 prompt 长度 —— **给命中的那一类单独一条通道，并且给每一类都设队列深度上限。**

长请求照常服务，只是不再让所有人替它排队。

左下两根条是效果：同一个 90% 命中的请求，之前 9 秒里有 8.2 秒在替别人排队，之后回到 1.1 秒。

〔标注：这两个数字沿用第 21 页的算例，不是实测；真实的是信号读法和这个解法〕

验证行的落点请注意：**一张 GPU 都没有加。** 容量从来不是约束，**队列纪律才是。**

第二个案例，另一个反直觉的。
-->

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

<!--
【19:40 – 21:05】

标题就是结论：**卡一张没少，容量没了。**

入口信号是一个「劈叉」：**TPOT 在涨，而 TTFT 是平的。** 首 token 准时，之后每一个 token 都晚。

**这一个对比，就排除了入口、路由、Prefill 和 KV 传输** —— 在我们打开任何引擎页面之前。

左上三行：吞吐从 16K 掉到 10K，TPOT 从 21 毫秒涨到 47 毫秒，**而 GPU 数量一张没变。**

〔指四根柱子，第三根〕

88、91、**34**、89。

然后是这一页最关键的一句：**平均下来是 75%，一个再正常不过的数字。TP 组是以最慢的那个成员的速度在运行的，而平均值恰好把那个成员藏住了。**

因果链一步一步看：一个 rank 慢 → TP 迭代时间涨 → 输出 token 率降 → 请求存活变长 → KV 驻留更久 → 准入下降 → 等待上升。

〔最后半句重读〕

**KV 压力是这条链的最后一环，却是最先告警的那一环。** 如果你只盯着 KV，你会一路去调 KV 参数，而真正的原因在链条的另一头。

定位方法三步，这是最能直接照抄的部分：

**DCGM** 找出那张异常的**卡** → **NCCL 初始化日志**把 rank 映射到 GPU → 然后分支：设备有硬件错误就隔离设备；设备干净但集合通信慢，就**整个 TP 组换位置**。

括号里那句是我们踩过的坑：**rank 是一个软件索引，重启之后可能落在完全不同的物理卡上。** 跳过映射这一步，就会排错节点。

右下这个框是防止误判的护栏：**内存受限在入口信号上长得一模一样。** 各 rank 对称加上 DRAM/HBM 高，那加容量是对的；一个 rank 歪了，加副本只会成本翻倍、延迟照旧。

〔诚实口径：88/91/34/89 是实测；那条因果链是推理，不是逐环测出来的〕

两个案例，一张表。
-->

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

<!--
【21:05 – 22:05】

〔先说这句，然后真的停十秒，不要一边停一边说话〕

**这一页可以拍照，我停十秒。**

〔停十秒〕

六行，每一行都是同一个结构：**信号组合 → 下一步取证 → 候选动作。**

我只挑两行讲。

**P 到 D 那一行**：字节数为 0，或者过期在涨 —— 传输根本没有发生，而所有的延迟面板都是绿的。

**Remote KV 那一行**：命中率涨了**但是** TTFT 也涨了。这一行今天没有单独展开，它是从第 22 页 KV 空间那一条推出来的 —— 取回本身既要占空间、又要花时间，**命中不等于划算**。

〔底部这句是全场方法的一句话总结〕

**每一行都终结于一个可回滚的动作，而不是终结于一个面板。**

〔这是听众唯一带得走的一页，宁可砍掉别的，也要给它留够时间〕
-->

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

<!--
【22:05 – 22:50】

三句话，带走就行。每句十几秒，不要展开 —— 展开的内容前面全讲过了。

**第一，TTFT 告诉你「出事了」，从不告诉你「在哪儿」。** 它是四段之和，而和是不可逆的。用它来**开启**调查，不要用它来**结束**调查。

**第二，更多的面板不等于更多的可见性。** 八个入口信号决定下一页开哪个，其余的全部退到一次点击之外。

**第三，一个诊断必须能预测一个变化。** 一次一个改动，一道验证门，一个回滚条件 —— 而且在动手**之前**就写下来。

〔最后这句念出来，是全场的落点〕

**最好的面板，是你凌晨两点真的会打开的那一个。**
-->

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

<!--
【22:50 – 23:20】

最后说一下社区。这套方法**不需要造任何新轮子**。

vLLM 和 SGLang 已经暴露了每个请求的延迟、队列、token 形态和 trace —— 数据是现成的。

OpenTelemetry 的 GenAI 语义约定在推动跨层的字段统一。但它**还在演进**，所以可以现在就接，**别把告警绑死在字段名上**。

llm-d 和 GAIE 已经把 P/D 角色、队列状态、在途 token 接进了路由和扩缩容的决策。

KV 传输层和外部 KV 缓存层，正在把命中、字节、延迟、失败做成一等公民信号 —— PD 分离独有的那个故障域，终于可以被测量了。

〔底部收口〕

**缺的不是埋点，是「一致」。** 一个请求上下文，跨层共享，最后终结于**一个可度量、可回滚的动作**。

〔时间紧张时压到 20 秒，只念最后这句〕
-->

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

<!--
【23:20 – 结束】

谢谢大家。欢迎提问。

最后一页的二维码指向本次演讲的 Slides 与可复现 Demo 源码。

════════ 高频问题的回答口径 ════════

**Q：这套东西怎么落到我们现有的 Prometheus？**
八个入口信号**没有一个需要新 agent**，全部来自 llm-d EPP、vLLM、DCGM、NIXL 这些已经在跑的 exporter。
对应指标名：llm_d_epp_ready_endpoints、llm_d_epp_request_error_total、vllm:request_success_total、
vllm:time_to_first_token_seconds、vllm:time_per_output_token_seconds、vllm:num_requests_waiting（按 pd_role 拆）、
inference_pool_average_queue_size。证据层再加 agent_xfer_time_us / agent_tx_bytes / agent_errors_total 和 DCGM。

**Q：和 llm-d 自带的面板有什么区别？**
我们不替代它们，它们是数据源。社区已经把数据准备好了，**缺的是从数据到动作的那一跳。**

**Q：为什么是 8 个信号，不是 10 个或 6 个？**
四个问题（能不能接住 / 来了多少活 / 用户等多久 / 卡在哪段）× 每个两个信号。
纳入规则：**值不改变下一步动作的，就不是入口信号。**

**Q：路由侧的准入队列具体怎么分类？**
按**预期代价**分，不是按用户或模型分。两个输入就够：前缀命中估计（EPP 已经在算，用于 KV-aware 路由）和 prompt 长度。
**每一类都要有深度上限** —— 上限保护后端，优先级保护 SLA，两个都要有。

**Q：这不就是限流吗？**
限流是按总量拒绝；这里是**按代价排序 + 分类限深**。长请求不被拒绝，只是不插队。

**Q：取回不是在后台做的吗，为什么会占 GPU 空间？**
加载缓存前缀是先分配目标 KV block、再往里填。分配在取回开始时就发生，一直持有到填完 ——
所以慢的取回等于把空间从其他请求那里拿走。代价是 **blocks × 时长**。

**Q：KV 为什么总是不够用？**
三个隐性浪费：
① **MLA + 张量并行** —— 潜向量所有头共享，TP 按头切但没有头可切，于是每个 rank 完整复制一份，TP=8 就是 8 倍。
解法是注意力层走 DP attention、MoE 层走 EP，vLLM 已支持。**这一条是我们线上的一手经验，我们跑的就是 MLA 架构的模型。**
② max_model_len 按最坏情况预留，不是按实际输入长度的 p99。
③ FP8 KV 能省一半，默认是关的。

**Q：Operator homepage 是生产环境吗？**
不是，是受控演示环境，页面上已标注。生产截图在第 4 页和第 7 页。

**Q：和 KubeCon EU 那场「Redefining SLIs for LLM Inference」有什么不同？**
那场讲的是 SLI/SLO 的定义方法。我们这场：聚焦 **PD 分离**（KV Transfer 是它独有的故障域）；
从指标一路走到**参数级动作 + 回滚条件**；两个案例的第一反应都是「加卡」，而**两次都是错的**。
-->
