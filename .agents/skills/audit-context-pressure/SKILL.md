---
name: audit-context-pressure
description: Analyze Codex session-context pressure and create a safe continuation plan. Use when auto-compaction repeats, a conversation with screenshots, attachments, image generation, long logs, or broad repository reading grows unexpectedly, or when deciding whether to continue or rotate to a new session across implementation-first, documentation-first, or mixed work.
---

# Audit Context Pressure

Diagnose why a task is approaching context limits without exposing session text, images, credentials, cookies, tokens, or environment contents. Separate measured evidence from inference and leave the next session able to resume from a small, explicit packet.

## Outcomes

Produce all of the following:

1. A measured baseline for mandatory initialization and task-local reading.
2. A pressure table separating current input-token occupancy, compactions, images/attachments, tool output, and document granularity.
3. A green/yellow/orange/red continuation decision with a concrete next action.
4. A project-local investigation record and task/completion state.
5. A checkpoint packet when rotation is needed.

Do not use cumulative token usage as current occupancy. Use `last_token_usage.input_tokens / model_context_window` only when both values are present.

## Procedure

1. Read the project's normal initialization files and its documentation-update rules before auditing. Do not add all linked documents to the read set.
2. Preserve an existing worktree before any analysis that will add artifacts: inspect status, then create the requested commit/push only with the user's authority.
3. Pick the evidence route:

   | Situation | Evidence |
   | --- | --- |
   | A local Codex rollout JSONL is available | Run `scripts/summarize-session.mjs` with the explicit file path. |
   | Runtime token-count events are visible but no log file is available | Record the latest input/window ratio and compaction count; do not invent payload sizes. |
   | No session metrics are available | Audit the current task packet, initialization corpus, image/log/tool practices, and document granularity; label the result as an estimate. |

4. For a JSONL, run the script with a known Node runtime:

   ```powershell
   node <skill-dir>/scripts/summarize-session.mjs --session <rollout.jsonl> --top 12
   ```

   In Codex Desktop, use the bundled Node path when `node` is absent from `PATH`. The script streams JSONL and emits only counts, record types, structural sizes, and token metadata.

5. Classify evidence. Do not add size categories because one record can be both an image and a tool record.

   | State | Measured condition | Action |
   | --- | --- | --- |
   | Green | input under 60%, no compaction, few high-cost payloads | Continue the current small unit. |
   | Yellow | 60-74%, one compaction, or new screenshots/logs | Finish and document the small unit; prepare a checkpoint. |
   | Orange | 75-84%, one compaction followed by another image/log-heavy phase, or images remain in replacement history | Do not start broad reading or a new implementation phase; rotate after closing the unit. |
   | Red | 85% or more, two or more compactions, or repeated image/attachment payloads persist after compaction | Close a safe docs/Git checkpoint and start a new session. |

   If a model reports a different context-window size, use that actual window. Treat a missing metric as unknown, not green.

6. Select the task pattern and audit only its relevant boundary:

   - **Implementation-first:** list the changed feature, source boundary, tests, and missing product/spec/data/arch evidence. Add only the missing feature-level documentation.
   - **Documentation-first:** read the role-specific guide, target headings, and target acceptance IDs. Do not follow links recursively or load a whole 500-line document for one feature.
   - **Mixed:** make a six-column feature map: experience, state/API, data, external boundary, operations, regression. Read or add only the missing column.
   - **Visual/log-heavy:** count retained screenshots, generated images, attachments, and oversized command results. Preserve only representative artifacts for the next decision.

7. Write the result to the project's `docs/imp/` area. Put durable operating rules in a concise `docs/guide/` document; do not put a session log into `AGENTS.md` or a broad progress list into `PROJECT.md`.

8. Before rotation, update the implementation task, completion record, and—only if needed—a diary handoff. Commit one verified work unit. Start the new session from the mandatory initialization files plus the smallest task-specific packet.

## Report Format

Use this compact table in the investigation record and user update:

| Factor | Evidence | State | Next action |
| --- | --- | --- | --- |
| Initialization | measured token count or estimated bounded corpus | green/yellow/red | retain or split |
| Task-local docs | target sections vs broad/repeated reads | green/yellow/red | narrow/read missing evidence |
| Images/attachments | count and replacement-history persistence | green/yellow/red | select representative assets/rotate |
| Tool output | large record types and count | green/yellow/red | summarize/filter/file-reference |
| Input occupancy | latest input/window ratio and compactions | green/yellow/red | continue/checkpoint/rotate |

Always state the limitations: raw JSON bytes are not model tokens; categories may overlap; unknown metrics remain unknown.

## Required Safety Rules

- Never print, store, or quote session payload text, image contents, passwords, cookies, tokens, private keys, or environment files.
- Never use a compaction count alone as proof that a project document is too large.
- Never treat a new session as a substitute for recording task state, verification, and the next action.
- Refer to the project's canonical docs-management policy rather than copying it into this skill.
