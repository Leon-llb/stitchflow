<p align="center">
  <img src="icon.png" alt="Stitchflow" width="128" height="128">
</p>

<h1 align="center">Stitchflow</h1>
<p align="center"><strong>AI-Powered UI Design Workflow — One Skill, 27+ Agent Platforms</strong></p>

<p align="center">
  <img src="https://img.shields.io/badge/platform-macOS%20%7C%20Windows%20%7C%20Linux-lightgrey" alt="Platform">
  <img src="https://img.shields.io/badge/python-3.8%2B-blue" alt="Python">
  <img src="https://img.shields.io/badge/agentskills.io-compliant-green" alt="Agent Skills Standard">
  <img src="https://img.shields.io/badge/license-MIT-green" alt="License">
  <img src="https://img.shields.io/badge/compatible-Claude%20Code%20%7C%20Codex%20%7C%20OpenClaw%20%7C%20Hermes%20%7C%20Cursor-orange" alt="Compatible">
</p>

---

Automates the full **UI design pipeline** for AI coding agents: understand your project → craft tailored design prompts → generate in [Google Stitch](https://stitch.withgoogle.com/) → capture results. No API keys needed — connects to your already-logged-in Chrome browser via CDP.

**Unlike Google's [stitch-skills](https://github.com/google-labs-code/stitch-skills) (MCP server approach), Stitchflow uses direct browser CDP automation — no MCP setup required.**

### Why Stitchflow?

- **Project-aware prompts** — reads your CLAUDE.md, brand data, and product specs before writing prompts. No generic AI aesthetics
- **No API billing** — uses your existing Google Stitch access through your logged-in browser
- **Cross-platform** — macOS, Windows, and Linux all supported
- **Cross-agent** — one SKILL.md works on Claude Code, Codex, OpenClaw, Hermes, Cursor, and 22+ others
- **agentskills.io certified** — follows the open Agent Skills standard

---

## Quick Start

```bash
# 1. Install dependencies
pip install playwright && playwright install chromium

# 2. Log into Google Stitch in your Chrome browser
#    → Open https://stitch.withgoogle.com/ once

# 3. Launch Chrome in CDP mode
python3 stitch.py --launch-chrome

# 4. Generate your first design
python3 stitch.py "Design a modern SaaS analytics dashboard, dark theme, blue+green" --output dashboard.png
```

## Agent Platform Installation

| Platform | Install Command | Invocation |
|----------|----------------|------------|
| **Claude Code** | `cp -r stitchflow ~/.claude/skills/` | `/stitchflow` |
| **Codex CLI** | `cp -r stitchflow ~/.agents/skills/` | `$stitchflow` |
| **OpenClaw** | `openclaw skill install --path ./stitchflow` | `stitchflow` |
| **Hermes** | `cp -r stitchflow ~/.hermes/skills/` | auto-detected |
| **Cursor** | `cp -r stitchflow ~/.cursor/skills/` | auto-detected |
| **Gemini CLI** | `cp -r stitchflow .agents/skills/` | auto-detected |

> All platforms share the same `SKILL.md` — `agentskills.io` open standard ensures Write Once, Run Anywhere.

## How It Works

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐     ┌──────────┐
│  Project      │ →   │  Tailored     │ →   │  Google       │ →   │  Design   │
│  Context      │     │  Prompt       │     │  Stitch       │     │  Screenshot│
│  (CLAUDE.md,  │     │  Engineering  │     │  Generation   │     │  (PNG)    │
│   products)   │     │               │     │               │     │           │
└──────────────┘     └──────────────┘     └──────────────┘     └──────────┘
```

1. **Phase 1 — Read**: Agent reads your project's CLAUDE.md, product data, brand assets
2. **Phase 2 — Craft**: Writes a project-specific design prompt (not a generic template)
3. **Phase 3 — Launch**: Starts Chrome in CDP mode with your logged-in profile
4. **Phase 4 — Generate**: Automates Stitch — types prompt, clicks generate, waits
5. **Phase 5 — Capture**: Full-page screenshot saved to your project directory

## Prerequisites

| Requirement | How to Check |
|-------------|--------------|
| Google account logged into Chrome | Open gmail.com — if you see your inbox, you're good |
| Stitch accessed at least once | Open [stitch.withgoogle.com](https://stitch.withgoogle.com/) — if it loads, you're good |
| Python 3.8+ | `python3 --version` |
| Playwright | `pip install playwright && playwright install chromium` |

## Platform-Specific Notes

### macOS
```bash
python3 stitch.py --launch-chrome
# Chrome profile cloned to /tmp to preserve cookies
```

### Windows
```bash
python stitch.py --launch-chrome
# Chrome 136+ requires --disable-features=DevToolsDebuggingRestrictions
```

### Linux
```bash
python3 stitch.py --launch-chrome
# Uses google-chrome from PATH
```

## Skill Structure

```
stitchflow/
├── SKILL.md          # English (agentskills.io compliant)
├── SKILL.zh-CN.md    # Chinese (中文版)
├── stitch.py         # Cross-platform CDP automation script
├── icon.png          # Skill icon (1024×1024)
├── README.md         # This file
└── LICENSE           # MIT
```

## Advanced: Standalone Script

```bash
# Full pipeline
python3 stitch.py "your design prompt" --launch-chrome --output design.png

# Just generate (CDP already running)
python3 stitch.py "your design prompt" --output design.png
```

## Model Selection

For best results, switch Stitch to **Gemini 3.1 Pro** (top-left model selector). 3.1 Pro's deeper reasoning produces more nuanced designs. Manual step for now.

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "No Stitch iframe detected" | Open stitch.withgoogle.com in Chrome once to initialize |
| "CDP connection refused" | Run `python3 stitch.py --launch-chrome` |
| "Generate button not found" | Stitch UI may have changed; update selectors in stitch.py |
| "Profile clone failed" (Windows) | Run as Administrator |

## GitHub Topics

`claude-code` `codex-cli` `openclaw` `hermes-agent` `cursor` `google-stitch` `ui-design` `ai-design` `cdp` `chrome-devtools-protocol` `playwright` `browser-automation` `design-automation` `cross-platform` `agentskills` `agent-skills` `developer-tools`

## License

MIT © 2026 Leon

---

<p align="center">
  <sub>Built for the Agent Skills ecosystem — one file, 27+ platforms</sub>
</p>
