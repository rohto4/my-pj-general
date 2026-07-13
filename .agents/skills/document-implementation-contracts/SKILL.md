---
name: document-implementation-contracts
description: Convert an implemented or partially implemented pj-general feature into concise canonical product, spec, data, architecture, or operations documentation. Use when behavior is known from source, tests, acceptance notes, or runbooks but is missing from the correct design-documentation layer.
---

# Document Implementation Contracts

Turn verified behavior into one canonical document per responsibility.

## Establish the boundary

1. Read `AGENTS.md`, `PROJECT.md`, `docs/guide/docs-management-rules.md`, and the target coverage row.
2. Read all existing canonical documents linked from the row before opening source.
3. Identify the smallest source/test/runbook file that proves the missing fact.
4. Separate verified fact, product decision, and user decision still required.

Never infer an unverified product decision from code. Put an unresolved user choice in `docs/imp/user-judge.md`, not in the new canonical document.

## Select one canonical home

- Experience, navigation, copy, and acceptance perception: `docs/product/*`.
- State, action, validation, endpoint, and error behavior: `docs/spec/*`.
- Entities, fields, events, IDs, source of truth, and invariants: `docs/data/*`.
- Responsibility split, integration direction, idempotency, and failure boundaries: `docs/arch/*`.
- Start, deploy, inspect, backup, restore, rollback, and safe failure: `docs/guide/*` or `docs/ops/*`.

Do not use `docs/imp/*` as long-term specification. Replace duplicated design prose in a task document with canonical links plus implementation sequence, acceptance, and user-confirmation boundaries.

## Write and synchronize

1. State scope and exclusions.
2. State behavior in short tables or ordered flows.
3. State invariants and explicit non-behaviors.
4. Link related canonical documents instead of copying them.
5. State the smallest implementation boundary and verification evidence.
6. Leave next work in `docs/imp/imp-tasks.md`, not the body.
7. Link the new document from `docs/README.md` and a relevant folder README or reading profile.
8. Update the coverage row only after its evidence is actually present.

## Verify

Add or update a focused static/regression test if the new artifact has required structure. Run that test and `git diff --check`. Do not deploy, mutate real data, import data, or copy secrets while documenting behavior.
