---
name: agent-skill-source-review
description: Research external Agent Skills or Claude/Codex skill examples, evaluate whether they are useful, and import only safe project-local derivatives with source notes. Use when the user asks to copy, adapt, compare, or install skills from public repositories or current web sources.
---

# Agent Skill Source Review

Prefer project-local derivative skills over blind copying.

## Workflow

1. Search current public sources when freshness matters.
2. Record source name, URL, date checked, relevant skill names, and why each is useful.
3. Check license and repository guidance before copying any file verbatim.
4. If license or provenance is unclear, write a derivative skill that captures the workflow pattern without copying text.
5. Keep `SKILL.md` concise. Put long examples or source notes in `docs/candi-ref/*`, not inside the skill.
6. Validate each new skill with the skill validation script when available.

## Useful Source Patterns

- `frontend-design`: visual direction and avoidance of generic AI-looking UI.
- `webapp-testing`: rendered browser testing, screenshots, and DOM inspection.
- `web-artifacts-builder`: shadcn/Tailwind/React artifact patterns.
- `theme-factory`: reusable theme palette and font-pairing concepts.

## Local Placement

For this PJ, project-specific skills go under `.agents/skills/`. External source research goes under `docs/candi-ref/`. Do not place transient task progress in `PROJECT.md`.
