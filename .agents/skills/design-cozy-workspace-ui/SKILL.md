---
name: design-cozy-workspace-ui
description: Design or revise information-dense dashboards, hubs, task systems, knowledge tools, and internal apps as calm, rich, lived-in workspaces. Use when a UI should feel like a library, studio, lounge, sunroom, or personal study; when generic SaaS cards and excessive rounded corners must be removed; or when multiple bold visual directions must preserve the same real data and interactions across narrow and wide viewports.
---

# Design Cozy Workspace UI

Create an inhabitable information workspace, not a pile of cards.

Read [references/cozy-ui-system.md](references/cozy-ui-system.md) before designing or reviewing a theme.

## Workflow

1. Inventory every required datum, state, and action before styling.
2. Record the target viewports, including the user's real narrow working width.
3. Define a distinct room metaphor and material palette for each option.
4. Write visual acceptance tests before implementation.
5. Preserve one DOM, one interaction layer, and one data source across theme options.
6. Separate regions with shelves, rules, color fields, spacing, and typography before adding containers.
7. Add patterns and room motifs only in decorative layers that cannot obscure content.
8. Render every option at narrow and wide widths. Check alignment, overflow, density, and action clarity from screenshots.
9. Reject any option that reads as the same dashboard with recolored cards.

## Non-negotiable constraints

- Default `border-radius` to `0`; allow `1px` or `2px` for optical correction.
- Reserve circles and organic curves for status dots, plant leaves, lamps, and other decorative motifs.
- Do not apply rounded rectangles to every panel, row, filter, button, badge, or drawer.
- Do not remove information to create whitespace.
- Do not place text over busy imagery.
- Do not create mock data when the product has real data or API routes.
- Do not clone one reference site; combine independent patterns into an original system.
- Do not shrink the desktop layout uniformly for narrow viewports. Recompose it.

## Required evidence

- Screenshot at the user's narrow viewport.
- Screenshot at the product's wide desktop viewport.
- No horizontal document overflow at either width.
- Repeated summary columns have equal block height and aligned baselines.
- Main controls still work with the real backend.
- A radius audit proves structural surfaces are square or near-square.

## Review language

Describe the room metaphor, reading rhythm, material cues, and information hierarchy. Avoid calling a theme modern merely because it uses whitespace, shadows, or rounded cards.
