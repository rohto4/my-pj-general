---
name: audit-design-documentation-coverage
description: Audit feature-level coverage between implemented behavior, canonical product/spec/data/arch/ops documentation, tests, and operations evidence. Use when pj-general needs a documentation coverage scorecard, a post-compression reading boundary, or an evidence-based decision about whether implementation must be read.
---

# Audit Design Documentation Coverage

Audit documentation before reading implementation broadly.

## Read first

1. Read `AGENTS.md`, `PROJECT.md`, `tech-stack.md`, and `docs/guide/docs-management-rules.md`.
2. Read `docs/guide/implementation-context-reading-guide.md`.
3. Read `docs/imp/design-documentation-coverage-assessment-2026-07-13.html` and the target task in `docs/imp/imp-tasks.md`.

Do not treat a diary, a task note, or source code as a canonical design document.

## Audit one feature row

Collect exactly these evidence classes: product/user flow; screen/state/API contract; data model/invariants; architecture or external boundary; operations/recovery; tests/acceptance; a narrow implementation boundary.

Score the coverage HTML using its five-point rule.

- `5`: canonical document, synchronization target, implementation boundary, and verification are clear.
- `3-4`: a canonical source exists but the latest operation, UI state, or evidence needs confirmation.
- `1-2`: the fact exists only in implementation, `docs/imp`, or an unverified diary.

Keep delivery completion separate from documentation coverage. An unimplemented P1 design may score 5 when its documentation is complete.

## Read code only when necessary

Read only the exact source/test/runbook file named by the row when the canonical documents cannot answer a required state, action, field, integration rule, or recovery behavior. Record that missing fact before creating a document. Do not search the whole source tree first.

## Synchronize

1. Keep the coverage HTML interactive, five-point, and distinct from the P0/P1 scorecard.
2. Link each row to canonical docs, acceptance evidence, and the smallest implementation boundary.
3. Put implementation work in `docs/imp/imp-tasks.md`; put user-only checks in `user-tasks.md` or `user-judge.md`.
4. Update `imp-comp.md` on resolution and a diary only for a handoff.
5. Update `docs/README.md` and the reading guide when canonical entry paths change.

## Verify

- Run `apps/web/test/design-documentation-coverage.test.mjs`.
- Check every local link exists.
- Require yellow/red rows to name a specific missing document or verification.
- Run `git diff --check`.

Do not deploy, change real data, reveal secrets, or re-import data during this audit.
