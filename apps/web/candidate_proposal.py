"""Source-neutral, evidence-first candidate proposal contract.

Collectors own source access.  This module owns only prompt construction and
deterministic validation.  It never writes a candidate, performs GO, or calls
Vikunja.
"""

from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime
from pathlib import Path


PROMPT_VERSION = "threadline-candidate-proposal-v2"
ALLOWED_SOURCE_KINDS = {"knowledge_vault", "slack", "misskey", "chat"}
ALLOWED_CONFIDENCE = {"high", "medium", "low"}
GENERIC_ACTIONS = {"確認する", "整理する", "対応する", "検討する", "調査する", "修正する"}
ASPIRATION_MARKERS = re.compile(
    r"(?:やりたい|してみたい|試したい|実現したい|できるようにしたい|できたら|"
    r"いいな|欲しい|ほしい|興味|気になる|いつか|なんとなく|would like|want to|interested in)",
    re.IGNORECASE,
)


def canonical_json(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def sha256_text(value):
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def load_prompt():
    path = Path(__file__).resolve().parent / "prompts" / f"{PROMPT_VERSION}.txt"
    return path.read_text(encoding="utf-8")


def build_request(source_kind, source_ref, source_body, allowed_tags):
    source_kind = str(source_kind or "").strip()
    if source_kind not in ALLOWED_SOURCE_KINDS:
        raise ValueError(f"unsupported source_kind: {source_kind}")
    body = str(source_body or "")[:12000]
    reference = str(source_ref or "")[:500]
    tags = sorted(set(str(tag).strip() for tag in (allowed_tags or []) if str(tag).strip()))
    return {
        "system_prompt": load_prompt(),
        "user_prompt": (
            f"SOURCE_KIND: {source_kind}\n"
            f"SOURCE_REF: {reference}\n"
            f"ALLOWED_TAGS: {json.dumps(tags, ensure_ascii=False)}\n"
            "SOURCE_BODY:\n"
            f"{body}"
        ),
        "source_kind": source_kind,
        "source_ref": reference,
        "source_body": body,
        "allowed_tags": tags,
    }


def _line_for_quote(text, quote):
    offset = text.find(quote)
    if offset < 0:
        return None
    return text.count("\n", 0, offset) + 1


def _source_line(text, line_number):
    lines = text.splitlines()
    return lines[line_number - 1].strip() if line_number and 0 < line_number <= len(lines) else ""


def _proposal_identity(source_kind, source_ref, title, todo, evidence):
    return sha256_text(canonical_json({
        "source_kind": source_kind,
        "source_ref": source_ref,
        "title": title,
        "todo": todo,
        "evidence": evidence,
    }))[:20]


def normalize_output(
    output,
    source_text,
    allowed_tags,
    source_kind,
    source_ref,
    proposal_id_prefix="SCP",
):
    """Validate an LLM result without adding facts or changing its intent."""
    if not isinstance(output, dict):
        raise ValueError("LLM output must be a JSON object")
    if source_kind not in ALLOWED_SOURCE_KINDS:
        raise ValueError(f"unsupported source_kind: {source_kind}")
    summary = str(output.get("document_summary") or "").strip()[:600]
    raw_proposals = output.get("candidate_proposals")
    if raw_proposals is None:
        raw_proposals = output.get("task_proposals") or []
    if not isinstance(raw_proposals, list):
        raise ValueError("candidate_proposals must be an array")

    allowed = set(allowed_tags or [])
    by_evidence = {}
    order = []
    for raw in raw_proposals[:20]:
        if not isinstance(raw, dict):
            continue
        proposal_type = str(raw.get("proposal_type") or "action").strip()
        title = str(raw.get("title") or "").strip()[:120]
        todo = str(raw.get("todo") or "").strip()[:240]
        proposal_summary = str(raw.get("summary") or "").strip()[:600]
        kind = str(raw.get("kind") or ("idea" if proposal_type == "aspiration" else "todo")).strip()
        schedule = str(raw.get("schedule") or "候補なし").strip()
        confidence = str(raw.get("confidence") or "low").strip()
        missing = [str(item).strip()[:120] for item in (raw.get("missing") or []) if str(item).strip()][:10]
        tags = [str(item).strip() for item in (raw.get("tags") or []) if str(item).strip()][:12]
        evidence = [str(item).strip() for item in (raw.get("evidence_quotes") or []) if str(item).strip()][:3]
        reasons = []

        if proposal_type not in {"action", "aspiration"}:
            reasons.append("proposal_type is not allowed")
        if not title or len(title) < 4:
            reasons.append("title is missing or too generic")
        if not todo or len(todo) < 4:
            reasons.append("todo is missing or too generic")
        if not proposal_summary:
            reasons.append("summary is required")
        if proposal_type == "action":
            if kind != "todo":
                reasons.append("action kind must be todo")
            if title.rstrip("。. ") in GENERIC_ACTIONS or todo.rstrip("。. ") in GENERIC_ACTIONS:
                reasons.append("title or todo is too generic")
        if proposal_type == "aspiration":
            if kind != "idea":
                reasons.append("aspiration kind must be idea")
            if todo not in evidence:
                reasons.append("aspiration todo must preserve an exact source wish")
            if evidence and not any(ASPIRATION_MARKERS.search(quote) for quote in evidence):
                reasons.append("aspiration evidence has no personal wish marker")
        if confidence not in ALLOWED_CONFIDENCE:
            reasons.append("confidence is not allowed")
        if confidence == "low":
            reasons.append("low confidence proposals stay held")
        if schedule != "候補なし":
            try:
                datetime.strptime(schedule, "%Y-%m-%d")
            except ValueError:
                reasons.append("schedule is not a valid YYYY-MM-DD")
            if schedule not in source_text:
                reasons.append("schedule is not grounded in source")
        unknown_tags = sorted(set(tags) - allowed)
        if unknown_tags:
            reasons.append("tag is not in allowed master")
        if not evidence:
            reasons.append("evidence is required")
        for quote in evidence:
            line = _line_for_quote(source_text, quote)
            if line is None:
                reasons.append("evidence is not an exact source quote")
                continue
            raw_line = _source_line(source_text, line)
            if re.match(r"^[-*+]\s*\[[xX]\]", raw_line):
                reasons.append("evidence points to a completed action")
            if raw_line.startswith(">"):
                reasons.append("evidence is a quoted third-party statement")

        identity = _proposal_identity(source_kind, source_ref, title, todo, evidence)
        proposal = {
            "proposal_id": f"{proposal_id_prefix}-{identity}",
            "proposal_type": proposal_type,
            "title": title,
            "summary": proposal_summary,
            "todo": todo,
            "kind": kind if kind in {"todo", "idea"} else "todo",
            "schedule": schedule,
            "confidence": confidence if confidence in ALLOWED_CONFIDENCE else "low",
            "missing": missing,
            "tags": sorted(set(tags) & allowed),
            "evidence_quotes": evidence,
            "validation": {"status": "accepted" if not reasons else "held", "reasons": sorted(set(reasons))},
        }
        evidence_key = canonical_json(sorted(evidence))
        if evidence_key not in by_evidence:
            by_evidence[evidence_key] = proposal
            order.append(evidence_key)
        elif proposal_type == "action" and by_evidence[evidence_key]["proposal_type"] != "action":
            by_evidence[evidence_key] = proposal

    return {"summary": summary, "proposals": [by_evidence[key] for key in order]}
