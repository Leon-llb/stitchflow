---
name: stitchflow
description: "AI-powered UI design workflow via Google Stitch + Chrome CDP + Playwright. Reads your project context first, then crafts tailored prompts — no generic AI aesthetics. Use when the user asks to design a UI, dashboard, landing page, or web app interface. Cross-platform: macOS / Windows / Linux."
compatibility: "requires: python3, playwright, google-chrome-logged-into-stitch"
license: MIT
metadata:
  author: Leon
  version: "1.0.0"
---

# Stitchflow — AI UI Design Automation

Automates the full UI design pipeline: **project understanding → prompt engineering → Stitch generation → result capture**. Connects to your already-logged-in Chrome browser via CDP, so no API keys needed.

> **Core principle: Understand the project first, then write the prompt. No generic one-size-fits-all prompts.**

---

## Prerequisites (User Must Do)

| Requirement | Details |
|-------------|---------|
| Google Account | Chrome browser must be logged into a Google account |
| Stitch Access | Must have visited [stitch.withgoogle.com](https://stitch.withgoogle.com/) at least once with that account |
| Playwright | `pip install playwright && playwright install chromium` |
| Python 3.8+ | Installed on the system |

> ⚠ **If the browser isn't logged into Google or hasn't visited Stitch, the script will fail.**
> Tell the user: "Please log into your Google account in Chrome, then open stitch.withgoogle.com once to authorize."

---

## Full Workflow (AI Execution Steps)

### Phase 1: Understand the Project

Before touching Stitch, **read the project's context files** to understand what this project actually is:

```
Priority order:
1. CLAUDE.md                    → Brand identity, project architecture, behavior rules
2. Product data / knowledge base → SKU data, feature specs
3. Platform configs             → Deployment platforms (e.g., Shopify, JD, Douyin)
4. Brand assets                 → Logos, colors, design tokens (if available)
5. Current UI code              → Existing dashboard/index.html (if redesign)
```

Extract these dimensions for the prompt:
- **Brand name / Project codename**
- **Industry / Vertical** (e-commerce? SaaS? hardware?)
- **Brand colors / Design tokens** (hex values if available)
- **Target user persona**
- **Core functional needs** (KPI dashboard? Content management? Charts?)
- **Current UI pain points** (if redesign)

### Phase 2: Craft a Tailored Prompt

Write the prompt based on actual project data. **Never use a generic template** — every project's prompt should differ significantly because domains differ.

Prompt structure (must cover all dimensions):

```
Project Identity: [Brand/Codename], [Industry/Vertical], [one-line positioning]
Design Goal: [New / Redesign / Exploration], what page to design
Brand Tone: [3-5 adjectives], key visual elements
Color Scheme: Primary #XXXXXX, Accent #XXXXXX, [Dark/Light/Mixed]
Target User: [Who uses it], [Usage scenario]
Page Structure:
  - Screen 1: [Name] — [Function]
  - Screen 2: [Name] — [Function]
  - ...
Functional Requirements: [Specific metrics, chart types, interactions]
Language: All UI text in [Chinese/English/Japanese/etc.]
Style Reference: [Optional, 1-2 design directions]
```

**Example — E-commerce Operations Dashboard:**

```
Project Identity: CatCaptain (Lingyun), storage hardware e-commerce, high-value Micro SD / SSD brand
Design Goal: Redesign the AI operations dashboard for daily KPI monitoring + content management
Brand Tone: Professional, tech-driven, data-first, dark theme with vibrant orange accents
Color Scheme: Dark theme, Primary #1a1f36 (deep navy), Accent #FF6B35 (brand orange), Data Green #00C897
Target User: AI operations agent (daily monitoring) + Brand founder (weekly reports)
Page Structure:
  - Screen 1 — Main Dashboard: KPI cards (GMV/Orders/ROI/CTR) + trend charts + platform breakdown
  - Screen 2 — Content Factory: Video asset list + A/B test status + content calendar
  - Screen 3 — Competitor Watch: Price comparison table + competitor activity timeline
  - Screen 4 — Auto Reports: Daily/weekly report preview + key metric change highlights
Functional Requirements: Real-time data cards + Chart.js line/bar charts + filterable tables + left sidebar nav + dark mode
Language: All UI text in Chinese
Style Reference: Vercel Analytics data cards + Linear dark sidebar
```

### Phase 3: Launch Chrome CDP

Call `stitch.py --launch-chrome` to start Chrome in CDP mode.

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

> Windows note: Chrome 136+ (March 2025) silently ignores `--remote-debugging-port` on default profile paths. The `--disable-features=DevToolsDebuggingRestrictions` flag is required. macOS/Linux naturally bypass this by using `/tmp` cloned profiles.

**Linux:**
```bash
pkill -9 chrome 2>/dev/null; sleep 2
cp -r ~/.config/google-chrome /tmp/chrome-profile-clone
nohup google-chrome \
  --remote-debugging-port=9222 \
  --user-data-dir="/tmp/chrome-profile-clone" \
  > /tmp/chrome-cdp.log 2>&1 &
```

### Phase 4: Run Stitch Design

```bash
python3 ~/.claude/skills/stitchflow/stitch.py "<prompt from Phase 2>" --output <project-dir>/stitch-design-v1.png
```

The script automatically:
1. Connects to Chrome via CDP
2. Opens/reuses the Stitch page
3. Enters the Stitch iframe (`app-companion-430619.appspot.com`)
4. Selects the "Web" platform
5. Types the prompt into the contenteditable editor
6. Clicks the generate button
7. Polls until generation completes
8. Saves a full-page screenshot

### Phase 5: Model Selection

Stitch defaults to a standard model. **Switch to Gemini 3.1 Pro** in the Stitch UI for deeper design reasoning:

- Click the model selector in the top-left corner of Stitch
- Select **Gemini 3.1 Pro**
- 3.1 Pro's reasoning depth produces more nuanced, creative designs
- Trade-off: longer generation time (~60-120s vs 30-60s)

> Manual step — the script can't automate the model dropdown yet (requires UI interaction within the iframe).

### Phase 6: Review + Iterate

Use the `Read` tool to show the screenshot to the user. Once direction is confirmed:
- Approved → Move to code implementation
- Needs revision → Refine prompt based on feedback, regenerate

---

## IFrame / Stitch Interface Reference

- Main content is in `frames[1]` (iframe origin: `app-companion-430619.appspot.com`)
- Editor: TipTap/ProseMirror rich text editor, element `[contenteditable="true"]`
- Generate button: `button[placeholder="生成設計"]` / `button:has-text("生成")` / `button:has-text("Generate")`
- Generation detection: `document.body.innerText` contains "正在生成" or "Generating"
- Platform selector: `button:has-text("網頁")` (Web) / `button:has-text("應用程式")` (App)

---

## One-Liner Commands

```bash
# Full pipeline (launch CDP + design + screenshot)
python3 ~/.claude/skills/stitchflow/stitch.py \
  "your full design prompt" \
  --launch-chrome \
  --output ./stitch-design-v1.png

# If CDP is already running, just generate
python3 ~/.claude/skills/stitchflow/stitch.py \
  "your full design prompt" \
  --output ./stitch-design-v2.png
```

---

## Cross-Platform Summary

| | macOS | Windows | Linux |
|--|-------|---------|-------|
| Chrome Path | `/Applications/Google Chrome.app/...` | `%PROGRAMFILES%\Google\Chrome\...` | `google-chrome` (PATH) |
| Profile Path | `~/Library/Application Support/Google/Chrome` | `%LOCALAPPDATA%\Google\Chrome\User Data` | `~/.config/google-chrome` |
| Kill Process | `killall "Google Chrome"` | `taskkill /F /IM chrome.exe /T` | `pkill -9 chrome` |
| Special Flags | None | `--disable-features=DevToolsDebuggingRestrictions` | None |

---

## Keywords

`stitch` `google stitch` `AI design` `UI design` `dashboard` `design automation` `CDP` `Playwright` `claude-code` `skill`
