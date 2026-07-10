---
name: wqhd-ui-screenshot-loop
description: Capture WQHD browser screenshots and iteratively improve web UI layout, density, text fit, and interaction states. Use when Codex is asked to polish visual styling, verify a local web app by screenshot, or repeat inspect-edit-screenshot loops for desktop UI quality.
---

# WQHD UI Screenshot Loop

Use a real rendered browser state before trusting CSS or layout edits.

## Workflow

1. Confirm the app URL and server state. If no server is running, start the repo-standard dev server.
2. Capture a 2560x1440 screenshot for the default route and each important state.
3. Inspect the screenshots visually. Check text fit, whitespace, information density, button wrapping, sticky panes, scrollbars, and whether the page communicates the primary workflow.
4. Patch the smallest set of HTML/CSS/JS needed.
5. Run the repo checks.
6. Capture again with the same viewport and compare against the prior pass.
7. Repeat until no obvious WQHD layout issue remains or until the remaining issues need user judgment.

## Screenshot Targets

For P0 web prototypes, capture at least:

- `http://127.0.0.1:4173/`
- `http://127.0.0.1:4173/#gantt`
- `http://127.0.0.1:4173/#queue`
- `http://127.0.0.1:4173/#intake` when the app supports drawer-open deep links

## Chrome Command Pattern

Use installed Chrome when available:

```powershell
& 'C:\Program Files\Google\Chrome\Application\chrome.exe' --headless=new --disable-gpu --force-device-scale-factor=1 --window-size=2560,1440 --screenshot=G:\devwork\pj-general\tmp\p0-wqhd-pass-N.png http://127.0.0.1:4173
```

Use `view_image` on the screenshot before editing.

## Visual Checks

- Navigation labels should match the user's language and should not feel like default sample scaffolding.
- Main sections should be scannable at WQHD without becoming low-density empty panels.
- Operational dashboards should prioritize state, bottlenecks, queue pressure, and next actions.
- Detail panes should be wide enough for action buttons without wrapping.
- Drawers and overlays should be testable by URL or deterministic interaction.
- Colors should distinguish semantic roles without becoming a one-hue theme.
