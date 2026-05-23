---
name: stitchflow
description: "AI UI 设计全自动化工作流：先读取项目上下文（CLAUDE.md、品牌数据、产品参数）吃透业务，再撰写针对性设计 prompt（不用千篇一律的模板），通过 Chrome CDP+Playwright 操控已登录 Google Stitch 的浏览器自动出图，截图确认后导出 HTML/CSS，AI 再转成实际前端代码。零 API Key — 用的是你浏览器里已登录的 Google 账号。当用户要求设计 UI、Dashboard、Landing Page 或网页界面时使用。支持 macOS / Windows / Linux。"
compatibility: "需要: python3, playwright, 浏览器已登录 Google 并访问过 stitch.withgoogle.com"
license: MIT
metadata:
  author: Leon
  version: "1.0.0"
---

# Stitchflow — AI UI 设计自动化工作流

通过 CDP 连接用户已登录 Google Stitch 的 Chrome 浏览器，自动化完成从「项目理解 → prompt 撰写 → Stitch 生成 → 截图输出」的完整 UI 设计链路。

> **核心原则：先吃透项目，再写 prompt。不用千篇一律的通用提示词。**

---

## 前置条件（用户须知）

| 条件 | 说明 |
|------|------|
| Google 账号 | 用户的 Chrome 浏览器已登录 Google 账号 |
| Stitch 已访问 | 用该 Google 账号访问过 [stitch.withgoogle.com](https://stitch.withgoogle.com/) |
| Playwright | `pip install playwright && playwright install chromium` |
| Python 3.8+ | 系统已安装 |

> ⚠ **如果用户的浏览器没有登录 Google 或没有访问过 Stitch，脚本会失败。**
> 此时告诉用户：请在你的 Chrome 浏览器中登录 Google 账号，然后打开 stitch.withgoogle.com 授权一次。

---

## 完整工作流（AI 执行步骤）

### 阶段一：吃透项目

在执行 Stitch 设计之前，**必须先读取项目上下文**，理解这个项目是做什么的：

```
必读文件（按优先级）:
1. CLAUDE.md                    → 品牌定位、项目架构、行为规则
2. bridge/knowledge-base/       → 产品参数、SKU 数据
3. platforms/                   → 平台配置（抖音/京东）
4. assets/                      → 品牌素材（如有）
5. dashboard/index.html         → 当前 UI 状态（如果是改版）
```

从项目文件提取以下信息，填入 prompt 模板：
- **品牌名 / 项目代号**
- **行业 / 品类**（电商？SaaS？存储硬件？）
- **品牌色 / 设计 token**（如有 hex 值）
- **目标用户画像**
- **核心功能需求**（KPI 看板？内容管理？数据图表？）
- **当前 UI 痛点**（如果是改版）

### 阶段二：撰写针对性 Prompt

根据项目实际情况撰写 prompt。**禁止用通用模板直接填充** — 每个项目的 prompt 应该因为领域不同而有显著差异。

Prompt 结构（必须包含以下维度）：

```
项目身份：[品牌名 / 代号]，[行业/品类]，[一句话定位]
设计目标：[新增 / 改版 / 探索]，具体要设计什么页面
品牌调性：[3-5个形容词描述风格]，关键视觉元素
配色方案：主色 #XXXXXX，辅色 #XXXXXX，[深色/浅色/混合]
目标用户：[谁在用]，[使用场景]
页面结构：
  - Screen 1: [名称] — [功能描述]
  - Screen 2: [名称] — [功能描述]
  - ...
功能需求：[具体的数据指标、图表类型、交互方式]
语言：所有界面文字使用中文
参考风格：[如有，1-2个设计方向]
```

**示例 — 猫船长电商运营看板：**

```
项目身份：猫船长 CatCaptain（凌云 Lingyun），存储硬件电商，国产高性价比 Micro SD / SSD 品牌
设计目标：重新设计运营数据看板 Dashboard，替代现有纯信息架构页面
品牌调性：专业、科技感、数据驱动，蓝色科技 + 橙色活力点缀
配色方案：深色主题，主色 #1a1f36（深蓝黑），强调色 #FF6B35（猫船长橙），数据绿 #00C897
目标用户：AI 运营官（每天盯盘），品牌创始人（每周看报表）
页面结构：
  - Screen 1 — 主看板：KPI 总览卡片（GMV/订单数/ROI/CTR）+ 趋势折线图 + 平台分布
  - Screen 2 — 内容工厂：短视频素材列表 + 标题 A/B 测试状态 + 内容排期日历
  - Screen 3 — 竞品监控：价格对比表格 + 竞品动态时间线
  - Screen 4 — 日报/周报：自动生成报告预览 + 关键指标变化标注
功能需求：实时数据卡片 + Chart.js 图表 + 可筛选表格 + 左侧导航 + 深色模式
语言：所有界面文字使用中文
参考风格：Vercel Analytics 的简洁数据卡片 + Linear 的深色侧边栏
```

### 阶段三：启动 Chrome CDP

调用 `stitch.py --launch-chrome` 启动 CDP 模式浏览器。

**macOS:**
```bash
killall "Google Chrome" 2>/dev/null; sleep 2
cp -r "$HOME/Library/Application Support/Google/Chrome" "/tmp/chrome-profile-clone"
nohup /Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome \
  --remote-debugging-port=9222 \
  --user-data-dir="/tmp/chrome-profile-clone" \
  > /tmp/chrome-cdp.log 2>&1 &
```

**Windows:**
```bash
taskkill /F /IM chrome.exe /T
xcopy "%LOCALAPPDATA%\Google\Chrome\User Data" "%TEMP%\chrome-profile-clone" /E /I /H /Y
start "" "C:\Program Files\Google\Chrome\Application\chrome.exe" ^
  --remote-debugging-port=9222 ^
  --user-data-dir="%TEMP%\chrome-profile-clone" ^
  --disable-features=DevToolsDebuggingRestrictions
```

> Windows 注意：Chrome 136+ 对默认 profile 路径有安全限制，需要 `--disable-features=DevToolsDebuggingRestrictions`。Mac 使用 `/tmp` 克隆路径天然绕过此限制。

### 阶段四：执行 Stitch 设计

```bash
python3 ~/.claude/skills/stitchflow/stitch.py "<阶段二撰写的完整prompt>" --output <项目目录>/stitch-design-v1.png
```

脚本自动完成：
1. 通过 CDP 连接 Chrome
2. 打开 Stitch 首页（`stitch.withgoogle.com`）
3. 进入 iframe（`app-companion-430619.appspot.com`）
4. **在首页选择「網頁」平台**（平台选择器仅在首页可见，项目页无此选项）
5. 用键盘输入 prompt 到 contenteditable 编辑器
6. 按 Enter 键创建新项目（Stitch 自动开始生成，无需手动点生成按钮）
7. 轮询等待生成完成（检测预览 frame 出现）
8. 全页截图保存

### 阶段五：模型选择

Stitch 默认使用标准模型。**始终切换到当前最强的模型** — 模型列表会随 Google 发布新模型而更新。当前（2026年5月）最强是「Gemini 3.1 Pro」，但每次使用前请检查模型选择器，选最新的那个。

规则：**选版本号最高、或标注 Pro/Ultra/Max 的模型** — 参数越多 → 设计推理越深 → 输出越细致、越有创意。

- 脚本已自动化模型切换：会自动打开模型下拉菜单，选择版本号最高且标注 Pro/Thinking 的模型
- 选顶配模型
- 代价：生成时间稍长（约 60-120s vs 30-60s）

### 阶段六：确认 + 导出 + 交付

用 `Read` 工具读取截图展示给用户。用户确认方向后：

**满意 → 导出设计稿到代码：**

```bash
python3 ~/.claude/skills/stitchflow/stitch.py \
  "<同款prompt>" \
  --export .stitch/designs/
```

`--export` 参数触发 `stitch_export()`，用 4 层回退策略自动导出：
1. 点击 Stitch 界面的「Download / 下载 / Export」按钮
2. 尝试「...」更多菜单 → 找导出选项
3. 直接从 Stitch 预览区提取渲染好的 HTML
4. 捕获浏览器触发的文件下载事件

文件保存到 `.stitch/designs/`（兼容 Google stitch-skills 目录结构）：

```
.stitch/designs/
├── home-dashboard.html     # 导出的 HTML
├── home-dashboard.png      # 设计截图
└── index.html              # 完整页面 HTML（回退提取）
```

**AI 拿到导出文件后，转换为项目代码：**
- 读取 `.stitch/designs/` 中的 HTML/CSS
- 按项目实际框架映射（React / Vue / 静态 HTML）
- 匹配项目的 CSS 变量 / Tailwind 配置
- 遵守项目已有的文件结构和命名规范
- 产出可运行的、生产级别的代码

**不满意 → 根据用户反馈修改 prompt，重新生成。**

完整链路由六阶段闭环：
```
项目上下文 → 针对性 Prompt → Stitch 生成 → 截图确认 → 导出 HTML → AI 写代码
```

---

## IFrame / Stitch 界面参考

- 主内容在 `frames[1]`（iframe 来源 `app-companion-430619.appspot.com`）
- 编辑器是 TipTap/ProseMirror 富文本编辑器，元素为 `[contenteditable="true"]`
- **平台选择器仅在首页可见**：`button[role="radio"]:has-text("網頁")` / `button[role="radio"]:has-text("應用程式")`，选中状态通过 `aria-checked="true"` 判断
- **首页提交方式**：输入 prompt 后按 Enter 键，自动创建项目并开始生成
- 项目页无平台选择器 — 平台在创建项目时锁定，事后无法更改
- 生成中检测：`document.body.innerText` 包含「正在为您设计」「正在开始构建」或「正在生成」
- 生成完成检测：出现第 3 个 frame（预览区）或出现「提示：」文本

---

## 一键命令

```bash
# 完整流程（启动 CDP + 设计 + 截图）
python3 ~/.claude/skills/stitchflow/stitch.py \
  "你的完整设计prompt" \
  --launch-chrome \
  --output ./stitch-design-v1.png

# 如果 CDP 已启动，直接生成
python3 ~/.claude/skills/stitchflow/stitch.py \
  "你的完整设计prompt" \
  --output ./stitch-design-v2.png
```

---

## 关键词

`stitch` `google stitch` `AI 设计` `UI 设计` `dashboard` `设计自动化` `CDP` `Playwright`
