# Why Your TTFT Lies

Diagnosing PD-Disaggregated LLM Inference with Minimal Cross-Layer Metrics

KubeCon + CloudNativeCon China 2026 · 2026-09-09 16:15 · Mandarin Hall II · 30 分钟含 QA
讲者：Nicole Li（[@nicole-lihui](https://github.com/nicole-lihui)）、Kebe Liu（[@kebe7jun](https://github.com/kebe7jun)）— DaoCloud · 演讲语言：中文，上屏英文

## 本地预览

```bash
pnpm --filter 2026-09-09-kubecon-cn dev
```

局域网分享：`npx slidev --remote --port 3033`，同事直接开 `http://<你的内网 IP>:3033/`。
`#/overview/` 是缩略图总览，`#/presenter/` 是演讲者模式（含中文讲法注释，**只自己开**）。

## 结构

正片 28 页（无 Backup）。前 20 页的内容与顺序对齐 Nicole 的 `kubecon2026-ttft-0831.pptx`；图像尽量沿用 PPT 原始素材，信息密集处保留更清晰的 Slidev 卡片表达。第 21 页以后按“机制 → 事故”展开：

| 段落 | 页 | 内容 |
|---|---|---|
| Background | 3–7 | 告警现场 → 面板迷宫 → PD 生命周期 → 沿路径四次读收敛 |
| Method | 8–14 | 从面板泛滥到动作路径 → 8 个入口信号 → 四步走 → 两信号买一页证据 |
| Demo | 15–16 | 录屏 1:24：信号 → 边界 → 动作 → 验证 |
| Inside the engine | 17–21 | 三个机制页 → 验证闭环 |
| Cases | 22–24 | 两个一页式案例 |
| 收尾 | 25–28 | Playbook → takeaways → 社区展望 → Q&A |

结构对齐 `kubecon2026 - Why Your TTFT Lies.pptx`（新版）。

- `slides.md` — 全部幻灯片，**中文讲法写在每页末尾的 HTML 注释里**（演讲者模式可见）
- `speaker-notes.md` — 时间轴、超时预案、诚实口径、Backup 翻页索引、待补素材

## 可复现 Demo

演讲使用的 macOS + kind 故障诊断 Demo 已放在 [`demo/`](./demo/)；需要 Docker Desktop、`kind`、`kubectl`、`python3` 和 `curl`。

```bash
cd packages/2026-09-09-kubecon-cn/demo

make up
make baseline-test
make open-dashboard

make baseline
make incident
make evidence
make recovery
make status
```

完整说明、数据边界和清理命令见 [`demo/README.md`](./demo/README.md)。Python 缓存及其他运行时产物不纳入版本库。

## 组件

| 组件 | 用途 |
|---|---|
| `EntrySignals.vue` | 4 组 8 个入口信号；`vertical` 适配窄列，`highlight` 点亮当前步骤用到的信号 |
| `ProofTriad.vue` | 证据页统一版式（01/02/03 三维度 + 结论条），`accent` 区分域别配色 |
| `LoopDiagram.vue` | 观察 → 假设 → 一次改动 → 观测 → 验证 + keep/rollback 双门 |
| `StageFlow.vue` | PD 阶段流程条，`highlight` 点亮当前边界 |
| `RankBars.vue` | per-rank GPU 利用率柱状，`bad` 标出掉队 rank |
| `CostBars.vue` | 分段成本条，用于远端复用 vs 重算、以及队头阻塞的等待/计算对比 |
| `CaseStory.vue` | 案例页右栏的四行故事：SAW / MEANT / CHANGED / VERIFIED（+ 回滚条件） |
| `LineChart.vue` | 带真实坐标轴的折线图（支持对数轴、标注点、竖参考线） |
| `LatencyLadder.vue` | 多级网关耗时阶梯，自动算逐跳差值 |
| `TrendChart.vue` | before/after 趋势曲线，`markerAt` 标注改动时刻 |

## 素材来源

- 品牌配色、上海天际线、官方 lockup 取自 KubeCon China 2026 官方 PPT 模板
- `public/ppt-align/` 是从原 PPT 提取、用于前 20 页内容对齐的图片素材
- `public/shots/` 下的 Grafana 截图取自生产环境与受控演示环境（第 16 页已在页面上标注哪些不是生产证据）
- 指标名取自 llm-d EPP、vLLM、NIXL、DCGM 的原生 Prometheus 指标
- **不上屏任何部署细节**：量化格式、副本数与 P:D 具体配比、并行度、内部代号、域名、集群 ID、主机名、IP

## 第 19 页的 Demo 录屏（已就位）

视频已从 `kubecon2026-ttft-0831.pptx` 提取并压缩：

| | |
|---|---|
| 源 | `ppt/media/media1.mp4`，85 MB，2880×1800，2 fps，1:24 |
| 现在 | `public/demo.mp4`，**3.1 MB**，2160×1350，10 fps，无音轨 |
| 封面 | `public/demo-poster.jpg`（PDF 导出时代替视频） |

重新压缩的命令：

```bash
ffmpeg -i demo-raw.mp4 -vf "scale=2160:-2" -r 10 -c:v libx264 -preset slow -crf 20 \
  -pix_fmt yuv420p -movflags +faststart -an public/demo.mp4
ffmpeg -i public/demo.mp4 -ss 00:00:02 -vframes 1 -q:v 3 public/demo-poster.jpg
```

`-an` 去音轨 —— 现场由讲者口述，而且**浏览器只允许静音视频自动播放**。

页面上用的是 Slidev 内置的 `<SlidevVideo>`：`autoplay` 翻页即播、`autoreset="slide"` 离开回来从头播、
`muted` 保证 autoplay 不被拦、`controls` 保留进度条、`print-poster` 供 PDF 导出。
