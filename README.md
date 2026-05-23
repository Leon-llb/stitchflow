<p align="center">
  <img src="icon.png" alt="Stitchflow" width="128" height="128">
</p>

<h1 align="center">Stitchflow</h1>
<p align="center"><strong>Let your AI coding agent design UIs — auto-reads your project, crafts tailored prompts, drives Google Stitch</strong></p>

<p align="center">
  <a href="README.zh-CN.md">🇨🇳 简体中文</a>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/platform-macOS%20%7C%20Windows%20%7C%20Linux-lightgrey" alt="Platform">
  <img src="https://img.shields.io/badge/python-3.8%2B-blue" alt="Python">
  <img src="https://img.shields.io/badge/agentskills.io-compliant-green" alt="Agent Skills Standard">
  <img src="https://img.shields.io/badge/license-MIT-green" alt="License">
  <img src="https://img.shields.io/badge/compatible-Claude%20Code%20%7C%20Codex%20%7C%20OpenClaw%20%7C%20Hermes%20%7C%20Cursor-orange" alt="Compatible">
</p>

---

## Demo

<video src="demo.mp4" controls width="100%"></video>

> Full automation: read project → write prompt → select platform → switch model → generate design → screenshot

## What is this?

When you ask an AI to design a dashboard or landing page, it can only describe it with text or sketch rough code. To see a real, polished design, you'd normally open Figma or manually type prompts into Google Stitch.

Stitchflow automates that entire loop: **your AI agent reads your project's actual context (brand colors, product data, user personas), crafts a prompt tailored to your business, drives Google Stitch through your already-logged-in Chrome browser, and delivers a full-page design screenshot.** Approve it, and the AI exports the HTML/CSS and converts it into real frontend code.

No manual Stitch interaction. No prompt engineering guesswork. No copy-paste.

## How is this different from Google's stitch-skills?

Google's [stitch-skills](https://github.com/google-labs-code/stitch-skills) is an MCP server that gives you API-style access to Stitch. But it doesn't close the loop — it can't read your project context and generate business-specific designs.

Stitchflow takes a different approach: it's not an MCP server. It drives Chrome directly through CDP (Chrome DevTools Protocol), using your already-logged-in browser session. This means:

- **Zero API keys** — uses your existing Google account session
- **Zero configuration** — no tokens, no secrets, no setup wizards
- **Context-aware** — the AI reads your CLAUDE.md, product data, and brand assets before writing any prompt
- **End-to-end pipeline** — understand → prompt → generate → screenshot → export → code

Think of it this way: stitch-skills gives you the toolbox. Stitchflow gives you the fully automated assembly line.

## Installation

```bash
# 1. Install dependencies
pip install playwright && playwright install chromium

# 2. Log into your Google account in Chrome, then visit https://stitch.withgoogle.com/ once

# 3. Install to your AI coding agent
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

## Usage

### Recommended: Talk to your AI agent

After installation, just say:

> "Design a SaaS analytics dashboard with dark theme"

The AI agent will:
1. Read your project's CLAUDE.md, product data, and brand colors
2. Craft a Stitch prompt tailored to your business
3. Launch Chrome in CDP mode
4. Open Stitch → select "Web" platform → auto-switch to the best model → type prompt → press Enter
5. Wait for generation, then show you the screenshot
6. Export HTML/CSS and convert to frontend code once you approve

### CLI mode

```bash
# First time: launch CDP-enabled Chrome (closes existing Chrome windows)
python3 stitch.py --launch-chrome

# Generate a design
python3 stitch.py "your full design prompt" --output dashboard.png

# Full pipeline (launch + generate + export)
python3 stitch.py "your prompt" --launch-chrome --output dashboard.png --export .stitch/designs/
```

## Six-Stage Pipeline

```
Project Context → Tailored Prompt → Stitch Generation → Screenshot Review → Export HTML → AI Writes Code
```

| Stage | Who | What |
|-------|-----|------|
| 1. Understand | AI | Read CLAUDE.md, product data, brand assets, existing UI |
| 2. Prompt | AI | Write a Stitch prompt with brand colors, personas, page structure, feature requirements |
| 3. Launch | Script | Kill existing Chrome → clone profile (preserves login) → restart in CDP mode |
| 4. Generate | Script | Connect CDP → open Stitch home → select "Web" → auto-switch best model → type prompt → press Enter → poll until done |
| 5. Review | AI | Show screenshot to user, get approval or revision feedback |
| 6. Ship | Script+AI | Export HTML/CSS → AI reads → converts to React/Vue/static code |

## Cross-Platform

| | macOS | Windows | Linux |
|--|-------|---------|-------|
| Chrome Path | `/Applications/Google Chrome.app/...` | `%PROGRAMFILES%\Google\Chrome\...` | `google-chrome` (PATH) |
| Profile Path | `~/Library/Application Support/Google/Chrome` | `%LOCALAPPDATA%\Google\Chrome\User Data` | `~/.config/google-chrome` |
| Special Flags | None | `--disable-features=DevToolsDebuggingRestrictions` | None |

## Multi-Agent Compatibility

One SKILL.md, compatible across all major AI coding agents (follows [agentskills.io](https://agentskills.io) open standard):

| Agent | Install Path | Invocation |
|-------|-------------|------------|
| Claude Code | `~/.claude/skills/` | `/stitchflow` |
| Codex CLI | `~/.agents/skills/` | `$stitchflow` |
| OpenClaw | `openclaw skill install` | `stitchflow` |
| Hermes | `~/.hermes/skills/` | Auto-detect |
| Cursor | `~/.cursor/skills/` | Auto-detect |
| Gemini CLI | `.agents/skills/` | Auto-detect |

## Model Selection

Stitch defaults to a standard model. **The script always switches to the most capable model available** (the model list evolves as Google releases new ones). The rule: pick the one with the **highest version number** and/or **Pro/Ultra/Max** label.

Stronger model → deeper design reasoning → more nuanced, creative output. Trade-off: ~60-120s generation time vs 30-60s for standard models.

> Model switching is fully automated: the script opens the model dropdown, scores options by version number + Pro/Thinking labels, and auto-clicks the best one.

## File Structure

```
stitchflow/
├── SKILL.md          # English skill definition (execution guide for AI)
├── SKILL.zh-CN.md    # Chinese skill definition
├── stitch.py         # Core script: CDP launcher + Stitch automation + export
├── icon.png          # Skill icon (1024×1024)
├── demo.mp4          # Demo video
├── README.md         # This file (English)
├── README.zh-CN.md   # Chinese README
└── LICENSE           # MIT
```

## FAQ

| Problem | Cause | Solution |
|---------|-------|----------|
| "Stitch iframe not detected" | Browser not logged into Google or hasn't visited Stitch | Log into Google in Chrome, then open stitch.withgoogle.com once |
| "CDP connection failed" | Chrome not running in CDP mode | Run `python3 stitch.py --launch-chrome` first |
| "Generate button not found" | Stitch UI changed | **Fixed**: new flow doesn't need a generate button — type prompt on home page, press Enter, Stitch auto-creates project and starts generation |
| "Generation finished too fast (a few seconds)" | Prompt didn't inject properly, or false-positive completion detection | **Fixed**: keyboard-based input + improved generation detection. Check CDP connection if issues persist |
| "Design looks like a mobile app" | Platform selector defaulted to "App" mode | **Fixed**: script now auto-clicks the "Web" radio button and verifies `aria-checked="true"` |

## License

MIT © 2026 Leon

---

<p align="center">
  <sub>Built for the Agent Skills ecosystem — one file, 27+ platforms</sub>
</p>
