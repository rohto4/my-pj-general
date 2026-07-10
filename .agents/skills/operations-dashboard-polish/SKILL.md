---
name: operations-dashboard-polish
description: Polish SaaS or operations dashboard UI for dense, work-focused scanning, queue handling, task summaries, and admin surfaces. Use when a frontend prototype needs stronger information hierarchy, less generic styling, better Japanese labels, or more useful dashboard metrics.
---

# Operations Dashboard Polish

Treat operational UI as a repeated-use tool, not a landing page.

## Priorities

1. Put the user's main work order first: overview, plan, review queue, worker summary, admin.
2. Use metrics only when they help decisions: queue count, blocked count, missing fields, high-confidence candidates, scheduled load, aging, source mix, action rate.
3. Keep panels compact. A panel should either answer a question or create an action.
4. Prefer clear section bands and restrained panels. Avoid decorative cards inside cards.
5. Use Japanese labels for product-facing sample data unless a technical identifier is intentional.
6. Keep command buttons short and stable: `GO`, `編集`, `不要`, `アーカイブ`.
7. Preserve stable dimensions for tables, timelines, toolbars, and detail panes.

## UI Heuristics

- Dashboard: show bottlenecks, trend-like summaries, source distribution, and top attention items.
- Gantt: make date scale visible; show owner, progress, dependency, and task name without visual clutter.
- Queue: table plus right detail pane; selected row must be obvious; action buttons must not wrap.
- Worker view: show what to do next and the prompt/context needed to start.
- Admin: show only settings needed to reason about P0 scope.

## Style Direction

Use a restrained neutral base, one primary action color, and semantic warning/danger/success accents. Avoid a one-note palette, oversized hero treatment, purple gradients, and generic marketing composition.
