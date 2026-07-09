---
name: mermaid-diagram-style
description: Create or revise Mermaid diagrams with consistent pastel colors, concise Japanese node text, and clear layout rules. Use for technical concept diagrams, business workflow diagrams, sequence diagrams, feature flowcharts, architecture sketches, and documentation diagrams where readability and visual consistency matter.
---

# Mermaid Diagram Style

## Core Rule

Create diagrams that are easy to scan before they are exhaustive.

Prefer:
- box-to-box arrows for high-level concept diagrams
- consistent pastel color classes
- stable left-to-right or top-to-bottom reading order
- short Japanese titles with optional supporting lines

Avoid:
- strict implementation arrows in concept diagrams
- many unlabeled crossing arrows
- unstyled default Mermaid output
- mixed label formats in the same diagram

## Text Rules

- Use Japanese titles.
- Use at most 3 lines per node by default.
- Allow 4 lines only when the extra line preserves necessary information.
- Format node text as `Title<br/>support<br/>support`.
- Keep the first line as the semantic name.
- Put implementation names, examples, or constraints on later lines.
- Separate main information from supporting information visually.
- Mermaid cannot reliably style individual lines inside one node, so use node class, font size, font weight, and placement to distinguish primary flow nodes from supporting notes.

## Color Rules

Use pastel colors. Assign color by semantic role, not by arbitrary node order.

Default palette:

```mermaid
classDef input fill:#e3f2fd,stroke:#64a6d9,color:#17324d,stroke-width:1.5px
classDef app fill:#fff4c2,stroke:#d8b545,color:#3b3100,stroke-width:1.5px
classDef api fill:#e8f5e9,stroke:#73b77a,color:#183d1f,stroke-width:1.5px
classDef async fill:#f3e8ff,stroke:#a986d8,color:#302044,stroke-width:1.5px
classDef data fill:#dff3ff,stroke:#5aa4c8,color:#173746,stroke-width:1.5px
classDef external fill:#ffe8d6,stroke:#d9965c,color:#4a2a10,stroke-width:1.5px
classDef decision fill:#fff0f0,stroke:#d87878,color:#4a1515,stroke-width:1.5px
classDef note fill:#f5f7fa,stroke:#aab4c0,color:#26313f,stroke-width:1.5px
```

Theme tendencies:
- DB / data flow: blue family
- business workflow: orange family
- web UI / visible screens: yellow family
- async / AI / job: soft purple
- external services: peach
- decisions / user GO: soft red

## Diagram Type Rules

### Technical Concept Diagram

Use when explaining architecture at a high level.

Rules:
- Use `flowchart LR`.
- Use 4 to 7 main boxes.
- Connect boxes, not individual functions.
- Keep arrows broad: `入口 -> アプリ/API -> Queue/Workers -> DB/外部API`.
- Put detailed endpoints in later specs, not this diagram.

### Business Workflow Diagram

Use when explaining user-facing flow.

Rules:
- Use `flowchart TD`.
- Show business state transitions, not packages.
- Use orange and decision colors more than technical colors.
- Keep decision nodes few.
- If the diagram becomes too tall, switch to `flowchart LR` and keep the main path horizontal.
- Keep the main path to 5 to 7 nodes for FullHD readability.
- Put detail branches under or beside the main path as lighter note or output nodes.

### Sequence Diagram

Use when order and actor responsibility matter.

Rules:
- Use `sequenceDiagram`.
- Keep actors to 3 to 5.
- Show only meaningful calls.
- Add notes only when they change interpretation.

### Feature Flowchart

Use when designing one feature in detail.

Rules:
- Use `flowchart TD`.
- One main path plus exception branches.
- Color user actions, system processing, data persistence, and external calls separately.

### Data Flow Diagram

Use when source, transformation, and persistence matter.

Rules:
- Use blue family as the dominant color.
- Separate source events, normalized events, domain objects, and lineage.
- Avoid UI nodes unless they are required for review or correction.
- Prefer `flowchart LR`.
- Keep the main data path to 5 to 7 nodes.
- Use side branches only for lineage, external APIs, or review points.

## Layout Rules

- Prefer `LR` for architecture and data movement.
- Prefer `TD` for user workflows and state progression.
- Keep subgraphs only when they reduce cognitive load.
- Avoid more than 2 nested visual levels.
- If a diagram needs many details, split it into overview and detail diagrams.
- Optimize overview diagrams to fit on a FullHD screen without tiny text.
- Avoid extreme vertical or horizontal diagrams.
- Use 5 to 9 total boxes for overview diagrams.
- Prefer one main path and a few side notes over many equally weighted branches.
- Use `font-size` and `font-weight` in class definitions to distinguish primary nodes from supporting nodes.

Suggested emphasis classes:

```mermaid
classDef main font-size:16px,font-weight:bold
classDef support font-size:13px,font-weight:normal
classDef muted font-size:12px,font-weight:normal
```

## Review Checklist

Before finalizing a Mermaid diagram:
- Are colors assigned by semantic role?
- Is the first line of every node a clear title?
- Are high-level concept diagrams free of noisy implementation arrows?
- Are there fewer than 8 primary boxes in overview diagrams?
- Does the reading direction match the story?
- Can the user understand the diagram without reading the surrounding text first?
- Does the diagram fit a FullHD screen without tiny text?
- Are primary flow nodes visually stronger than supporting notes?
