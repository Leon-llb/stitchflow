<p align="center">
  <img src="icon.png" alt="Stitchflow" width="128" height="128">
</p>

<h1 align="center">Stitchflow</h1>
<p align="center"><strong>AI UI 设计，但真的懂你的项目 — 不是千篇一律的 AI 味</strong></p>

<p align="center">
  <a href="README.md">🇺🇸 English</a>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/platform-macOS%20%7C%20Windows%20%7C%20Linux-lightgrey" alt="Platform">
  <img src="https://img.shields.io/badge/python-3.8%2B-blue" alt="Python">
  <img src="https://img.shields.io/badge/agentskills.io-compliant-green" alt="Agent Skills Standard">
  <img src="https://img.shields.io/badge/license-MIT-green" alt="License">
  <img src="https://img.shields.io/badge/compatible-Claude%20Code%20%7C%20Codex%20%7C%20OpenClaw%20%7C%20Hermes%20%7C%20Cursor-orange" alt="Compatible">
</p>

---

## 演示

<p align="center">
  <a href="demo.mp4?raw=true">
    <img src="preview.gif" alt="Stitchflow 演示" width="800">
  </a>
</p>
<p align="center"><em>点击 GIF 观看完整演示视频 →</em></p>

---

## 问题

你让任何一个 AI 编程助手「帮我设计一个看板」，它会给你一版。但看起来跟所有 AI 生成的 UI 一模一样 —— 千篇一律的布局、差不多的配色、浓浓的「AI 味」。它不认识你的品牌，不了解你的业务，没读过你的产品参数。

结果就是：乍一看还行，一用就发现空洞、没有灵魂。

## Stitchflow 怎么做

Stitchflow 不是把你的需求直接丢给大模型然后吐出代码。它跑一条**六阶段流水线**，从理解你的项目开始，到产出可用的前端代码结束：

1. **读懂项目** — 读取 CLAUDE.md、品牌数据、产品参数、现有 UI，了解你到底在做什么
2. **写定制 prompt** — 不是填空题模板，而是根据你的行业、品牌色、用户画像、功能需求现写的提示词
3. **操控 Google Stitch** — 通过 CDP 连接你已登录的 Chrome 浏览器，自动选「网页」平台、切最强模型、输入 prompt、启动生成
4. **截取结果** — 全页截图给你确认
5. **导出 HTML/CSS** — 从 Stitch 提取渲染好的设计稿
6. **转成实际代码** — AI 按你的技术栈（React / Vue / 静态页面）和项目规范写成生产级代码

输出不是「一个 AI 看板」，而是**你的**看板，**你的**品牌，**你的**数据。

## 安装

```bash
# 1. 安装依赖
pip install playwright && playwright install chromium

# 2. 在 Chrome 浏览器里登录 Google 账号，然后打开 https://stitch.withgoogle.com/ 一次授权

# 3. 安装到你的 AI 编程助手
# Claude Code:
cp -r stitchflow ~/.claude/skills/

# Codex CLI:
cp -r stitchflow ~/.agents/skills/

# OpenClaw:
openclaw skill install --path ./stitchflow

# Cursor / Hermes / Gemini CLI:
cp -r stitchflow ~/.cursor/skills/     # Cursor
cp -r stitchflow ~/.hermes/skills/     # Hermes
cp -r stitchflow .agents/skills/       # Gemini CLI
```

## 怎么用

### 在你的 AI 助手里用（推荐）

安装后直接说：

> 「帮我设计一个电商运营数据看板，深色主题」

AI 会自动跑完整条流水线 — 从读项目到出截图。你确认方向后，导出代码。

### 命令行

```bash
# 首次使用：启动 CDP 模式的 Chrome（会关闭现有 Chrome 窗口）
python3 stitch.py --launch-chrome

# 生成设计
python3 stitch.py "你的完整设计提示词" --output dashboard.png

# 完整流程（启动 + 生成 + 导出）
python3 stitch.py "你的提示词" --launch-chrome --output dashboard.png --export .stitch/designs/
```

## 六阶段流水线

```
项目上下文 → 定制提示词 → Stitch 生成 → 截图确认 → 导出 HTML → AI 写代码
```

| 阶段 | 谁在做 | 做什么 |
|------|--------|--------|
| 1. 读懂项目 | AI | 读取 CLAUDE.md、产品数据、品牌素材、现有 UI |
| 2. 写提示词 | AI | 根据项目实际撰写 Stitch 提示词，含品牌色、用户画像、页面结构、功能需求 |
| 3. 启动浏览器 | 脚本 | 关闭现有 Chrome → 克隆 profile 保留登录态 → 以 CDP 模式重启 |
| 4. 自动生成 | 脚本 | 连接 CDP → 打开 Stitch 首页 → 选「網頁」→ 自动切最强模型 → 输入 prompt → 按 Enter → 轮询等待 |
| 5. 截图确认 | AI | 截图展示给用户，确认或修改 |
| 6. 交付代码 | 脚本+AI | 导出 HTML/CSS → AI 读取 → 转成 React/Vue/静态页面 |

## 跨平台

| | macOS | Windows | Linux |
|--|-------|---------|-------|
| Chrome 路径 | `/Applications/Google Chrome.app/...` | `%PROGRAMFILES%\Google\Chrome\...` | `google-chrome` (PATH) |
| Profile 路径 | `~/Library/Application Support/Google/Chrome` | `%LOCALAPPDATA%\Google\Chrome\User Data` | `~/.config/google-chrome` |
| 特殊要求 | 无 | Chrome 136+ 需额外参数 | 无 |

## 跨 AI 助手兼容

一份 SKILL.md，兼容以下所有平台（遵循 [agentskills.io](https://agentskills.io) 开放标准）：

| 助手 | 安装路径 | 调用方式 |
|------|---------|---------|
| Claude Code | `~/.claude/skills/` | `/stitchflow` |
| Codex CLI | `~/.agents/skills/` | `$stitchflow` |
| OpenClaw | `openclaw skill install` | `stitchflow` |
| Hermes | `~/.hermes/skills/` | 自动检测 |
| Cursor | `~/.cursor/skills/` | 自动检测 |
| Gemini CLI | `.agents/skills/` | 自动检测 |

## 模型选择

Stitch 默认用标准模型。脚本会**自动切换到当前最强模型**（模型列表随 Google 发布新模型而更新）。打开模型下拉菜单，按版本号 + Pro/Thinking 标签评分，自动选最强的。

更强模型 → 更深设计推理 → 更细致、更有创意的设计稿。代价：约 60-120s vs 30-60s 生成时间。

## 零 API Key

不需要 API Key，不需要填 token，不需要任何配置。Stitchflow 通过 CDP 复用了你 Chrome 浏览器里已有的 Google 登录态 —— 跟你手动打开 Stitch 一模一样。

## 文件结构

```
stitchflow/
├── SKILL.md          # 英文版技能定义（给 AI 看的执行指南）
├── SKILL.zh-CN.md    # 中文版技能定义
├── stitch.py         # 核心脚本：CDP 启动 + Stitch 自动化 + 导出
├── icon.png          # 技能图标 (1024×1024)
├── demo.mp4          # 完整演示视频
├── preview.gif       # README 动图预览
├── README.md         # 英文版 README
├── README.zh-CN.md   # 本文件（中文版 README）
└── LICENSE           # MIT
```

## 常见问题

| 问题 | 原因 | 解决办法 |
|------|------|---------|
| 「未检测到 Stitch iframe」 | 浏览器没登录 Google 或没访问过 Stitch | 在 Chrome 里登录 Google 账号，打开 stitch.withgoogle.com 一次 |
| 「CDP 连接失败」 | Chrome 没以 CDP 模式启动 | 先运行 `python3 stitch.py --launch-chrome` |
| 「生成按钮找不到」 | Stitch 界面改版 | **已修复**：首页流程 — 输入 prompt 按 Enter 自动创建项目 |
| 「生成太快（几秒就完成）」 | 提示词没正确注入，或检测过早误判 | **已修复**：键盘逐字输入 + 改进完成检测 |
| 「设计看起来是手机端」 | 平台选择器默认选了 App 模式 | **已修复**：脚本自动点击「網頁」并验证 `aria-checked` |

## License

MIT © 2026 Leon

---

<p align="center">
  <sub>Built for the Agent Skills ecosystem — one file, 27+ platforms</sub>
</p>
