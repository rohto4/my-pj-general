---
name: maintain-design-documentation
description: Keep pj-general canonical design documents synchronized after a requirement decision, implementation change, verification result, deployment change, or handoff. Use when a completed change could leave product/spec/data/arch/ops docs, coverage assessment, task state, or reading guidance out of sync.
---

# Maintain Design Documentation

Synchronize documents at every change boundary without copying rules into every file.

## Start from the change

Read `docs/guide/docs-management-rules.md`, then classify the trigger as a requirement decision, implementation/verification progress, user-only operation, deployment/recovery procedure, or handoff/compression.

Read the affected coverage row and the role-specific set in `docs/guide/implementation-context-reading-guide.md`.

## Update in order

1. Update the one canonical product/spec/data/arch/ops document first.
2. Update direct entry points only when navigation changed: `docs/README.md`, folder README, or reading guide.
3. Update progress in `imp-tasks.md`, user-only work in `user-tasks.md` or `user-judge.md`, and completion facts in `imp-comp.md`.
4. Update the coverage HTML with evidence, score, and implementation boundary.
5. Write a diary only when the next session needs a reconstruction checkpoint.

Keep `PROJECT.md` free of task history and `docs/imp/*` free of long-lived design prose.

## Recheck the map

- Represent a changed UI rule in product or spec, not only CSS or an acceptance comment.
- Represent a changed field/state in both data and API/spec coverage.
- Represent a changed external dependency in architecture plus runbook/operations coverage.
- Link a new canonical document from its reader entry.
- Keep incomplete verification yellow/red; never upgrade merely because source changed.

## Finish safely

Run focused static/regression checks, verify local links, and run `git diff --check`. Evaluate knowledge-vault recording by the policy before writing there. Never expose secrets or make real-data/deployment changes merely to synchronize documentation.
