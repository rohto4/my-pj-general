"""Evidence-first knowledge-vault batch collector and SQLite importer.

The collector is intended to run on Windows, where the Vault is readable.  The
importer runs through ``db_tool.py`` inside the Linux Hub container.  Only a
validated proposal can become a pending Hub candidate; this module never GOes
or writes to Vikunja.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import socket
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

import candidate_proposal


SCHEMA_VERSION = "threadline.knowledge-vault.batch.v1"
PROMPT_VERSION = candidate_proposal.PROMPT_VERSION
COLLECTOR_VERSION = "1"
DEFAULT_TARGETS = ("records", "inbox", "tasks", "memory")
ACTION_HEADINGS = {
    "next actions",
    "next action",
    "next steps",
    "next step",
    "次にやるべきこと",
    "次のアクション",
    "次アクション",
    "todo",
}
TERMINAL_STATUSES = {"completed", "done", "archived", "rejected"}
GENERIC_ACTIONS = {"確認する", "整理する", "対応する", "検討する", "調査する", "修正する"}
ALLOWED_KINDS = {"todo", "consideration", "concern", "schedule_candidate"}
ALLOWED_CONFIDENCE = {"high", "medium", "low"}
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
SECRET_LINE_PATTERNS = (
    re.compile(r"-----BEGIN (?:OPENSSH|RSA|EC|DSA|PGP) PRIVATE KEY-----", re.IGNORECASE),
    re.compile(r'''["']?\b(?:api[_-]?key|access[_-]?token|refresh[_-]?token|token|secret|password|passwd|cookie|authorization)\b["']?\s*[:=]\s*\S+''', re.IGNORECASE),
    re.compile(r"\bBearer\s+[A-Za-z0-9._~+/=-]{12,}", re.IGNORECASE),
    re.compile(r"\b(?:ghp|github_pat|sk)-[A-Za-z0-9_-]{12,}", re.IGNORECASE),
)


def utc_now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def sha256_text(value):
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def canonical_json(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def load_prompt():
    return candidate_proposal.load_prompt()


def parse_frontmatter(text):
    if not text.startswith("---"):
        return {}
    end = text.find("\n---", 3)
    if end < 0:
        return {}
    fields = {}
    for line in text[3:end].splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        fields[key.strip().lower()] = value.strip().strip("\"'").lower()
    return fields


def document_heading(text, fallback):
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("#"):
            heading = stripped.lstrip("#").strip()
            if heading:
                return heading
    return fallback


def redact_secret_lines(text):
    """Preserve line numbers while removing likely credential values."""
    redacted = []
    private_key_block = False
    for line in text.splitlines():
        if private_key_block:
            redacted.append("[REDACTED_SECRET_LINE]")
            if re.search(r"-----END .*PRIVATE KEY.*-----", line, re.IGNORECASE):
                private_key_block = False
        elif re.search(r"-----BEGIN .*PRIVATE KEY.*-----", line, re.IGNORECASE):
            private_key_block = True
            redacted.append("[REDACTED_SECRET_LINE]")
        elif any(pattern.search(line) for pattern in SECRET_LINE_PATTERNS):
            redacted.append("[REDACTED_SECRET_LINE]")
        else:
            redacted.append(line)
    return "\n".join(redacted)


def explicit_actions(text):
    """Return open list items only from explicit action sections."""
    collecting = False
    heading = ""
    actions = []
    for number, raw in enumerate(text.splitlines(), start=1):
        stripped = raw.strip()
        if stripped.startswith("#"):
            heading = stripped.lstrip("#").strip()
            collecting = heading.lower() in ACTION_HEADINGS
            continue
        if not collecting or not stripped:
            continue
        if re.match(r"^[-*+]\s*\[[xX]\]", stripped):
            continue
        item = re.sub(r"^(?:[-*+]\s*(?:\[ \]\s*)?|\d+[.)]\s*)", "", stripped).strip()
        if not item:
            continue
        actions.append({"quote": item, "todo": item.rstrip("。."), "heading": heading, "line": number})
    return actions


def safe_error(error):
    """Record the failure class only; provider messages may contain secrets."""
    return type(error).__name__


def parse_llm_json(content):
    if isinstance(content, dict):
        return content
    value = str(content or "").strip()
    if value.startswith("```"):
        value = re.sub(r"^```(?:json)?\s*", "", value, flags=re.IGNORECASE)
        value = re.sub(r"\s*```$", "", value)
    return json.loads(value)


def build_llm_request(relative_path, source_body, allowed_tags):
    request = candidate_proposal.build_request(
        source_kind="knowledge_vault",
        source_ref=relative_path,
        source_body=source_body,
        allowed_tags=allowed_tags,
    )
    request["relative_path"] = relative_path
    return request


def openai_compatible_client(base_url, model, timeout=60, api_key=""):
    base = base_url.rstrip("/")
    if base.endswith("/chat/completions"):
        endpoint = base
    elif base.endswith("/v1"):
        endpoint = f"{base}/chat/completions"
    else:
        endpoint = f"{base}/v1/chat/completions"

    def invoke(request):
        headers = {"content-type": "application/json"}
        if api_key:
            headers["authorization"] = f"Bearer {api_key}"
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": request["system_prompt"]},
                {"role": "user", "content": request["user_prompt"]},
            ],
            "temperature": 0,
            "max_tokens": 3000,
            "stream": False,
        }
        http_request = urllib.request.Request(
            endpoint,
            data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
            headers=headers,
            method="POST",
        )
        with urllib.request.urlopen(http_request, timeout=timeout) as response:
            result = json.loads(response.read().decode("utf-8"))
        content = result.get("choices", [{}])[0].get("message", {}).get("content")
        if not content:
            raise ValueError("provider returned no message content")
        return parse_llm_json(content)

    return invoke


def line_for_quote(text, quote):
    offset = text.find(quote)
    if offset < 0:
        return None
    return text.count("\n", 0, offset) + 1


def heading_before_line(text, line_number):
    heading = ""
    for index, raw in enumerate(text.splitlines(), start=1):
        if index > line_number:
            break
        stripped = raw.strip()
        if stripped.startswith("#"):
            heading = stripped.lstrip("#").strip()
    return heading


def source_line(text, line_number):
    lines = text.splitlines()
    return lines[line_number - 1].strip() if 0 < line_number <= len(lines) else ""


def normalize_llm_output(output, source_text, allowed_tags, document_id):
    return candidate_proposal.normalize_output(
        output,
        source_text,
        allowed_tags=allowed_tags,
        source_kind="knowledge_vault",
        source_ref=document_id,
        proposal_id_prefix="KVP",
    )


def fallback_output(source_text, document_id, fallback_title):
    proposals = []
    for action in explicit_actions(source_text):
        identity = sha256_text(canonical_json({
            "document": document_id,
            "title": action["todo"],
            "todo": action["todo"],
            "evidence": [action["quote"]],
        }))[:20]
        proposals.append({
            "proposal_id": f"KVP-{identity}",
            "proposal_type": "action",
            "title": action["todo"][:120],
            "summary": action["todo"][:600],
            "todo": action["todo"][:240],
            "kind": "todo",
            "schedule": "候補なし",
            "confidence": "high",
            "missing": [],
            "tags": [],
            "evidence_quotes": [action["quote"]],
            "validation": {"status": "accepted", "reasons": []},
        })
    return {"summary": fallback_title[:600], "proposals": proposals}


def build_fragments(document_id, source_text, proposals):
    fragments = []
    seen = set()
    for proposal in proposals:
        for quote in proposal.get("evidence_quotes", []):
            if quote in seen or quote not in source_text:
                continue
            seen.add(quote)
            line = line_for_quote(source_text, quote)
            fragment_hash = sha256_text(quote)
            fragments.append({
                "fragment_id": f"KVF-{sha256_text(f'{document_id}\0{fragment_hash}')[:20]}",
                "heading": heading_before_line(source_text, line or 1),
                "line_start": line or 1,
                "line_end": line or 1,
                "excerpt": quote,
                "content_hash": fragment_hash,
                "extraction_method": "llm_evidence" if proposal.get("model_generated") else "explicit_action",
            })
    return fragments


def batch_identity(documents, model):
    return {
        "schema_version": SCHEMA_VERSION,
        "prompt_version": PROMPT_VERSION,
        "model": model,
        "documents": [
            {
                "document_id": item["document_id"],
                "proposal_ids": [proposal["proposal_id"] for proposal in item["proposals"]],
            }
            for item in documents
        ],
    }


def collect_batch(root, targets=None, limit=30, allowed_tags=None, llm=None, model="deterministic"):
    root = Path(root).resolve()
    targets = list(targets or DEFAULT_TARGETS)
    allowed_tags = list(allowed_tags or [])
    files = []
    for target in targets:
        base = root / target
        if base.exists():
            files.extend(path for path in base.rglob("*.md") if path.is_file())
    files = sorted(files, key=lambda path: path.stat().st_mtime_ns, reverse=True)[: int(limit)]
    documents = []
    fallback_count = 0
    for path in files:
        if path.name.lower() == "readme.md":
            continue
        text = path.read_text(encoding="utf-8-sig", errors="replace").strip()
        if not text or parse_frontmatter(text).get("status") in TERMINAL_STATUSES:
            continue
        relative = path.relative_to(root).as_posix()
        scope = relative.split("/", 1)[0]
        content_hash = sha256_text(text)
        document_id = f"KVD-{sha256_text(f'{relative}\0{content_hash}')[:20]}"
        title = document_heading(text, path.stem)
        safe_text = redact_secret_lines(text)
        request = build_llm_request(relative, safe_text, allowed_tags)
        input_hash = sha256_text(request["user_prompt"])
        ai_status = "deterministic"
        ai_error = None
        if llm is None:
            normalized = fallback_output(request["source_body"], document_id, title)
        else:
            try:
                raw_output = llm(request)
                normalized = normalize_llm_output(raw_output, request["source_body"], allowed_tags, document_id)
                for proposal in normalized["proposals"]:
                    proposal["model_generated"] = True
                ai_status = "succeeded"
            except Exception as error:
                normalized = fallback_output(request["source_body"], document_id, title)
                ai_status = "fallback"
                ai_error = safe_error(error)
                fallback_count += 1
        output_hash = sha256_text(canonical_json(normalized))
        fragments = build_fragments(document_id, request["source_body"], normalized["proposals"])
        for proposal in normalized["proposals"]:
            proposal.pop("model_generated", None)
        run_id = f"KVR-{sha256_text(f'{document_id}\0{input_hash}\0{model}\0{PROMPT_VERSION}')[:20]}"
        documents.append({
            "document_id": document_id,
            "relative_path": relative,
            "scope": scope,
            "content_hash": content_hash,
            "modified_at": datetime.fromtimestamp(path.stat().st_mtime, timezone.utc).isoformat(timespec="seconds"),
            "summary": normalized["summary"],
            "fragments": fragments,
            "proposals": normalized["proposals"],
            "ai_run": {
                "run_id": run_id,
                "provider": "openai-compatible" if llm is not None else "deterministic",
                "model": model,
                "prompt_version": PROMPT_VERSION,
                "input_hash": input_hash,
                "output_hash": output_hash,
                "status": ai_status,
                "error": ai_error,
                "created_at": utc_now(),
            },
        })
    model_info = {"provider": "openai-compatible" if llm is not None else "deterministic", "name": model}
    identity = batch_identity(documents, model_info)
    accepted = sum(p["validation"]["status"] == "accepted" for d in documents for p in d["proposals"])
    held = sum(p["validation"]["status"] != "accepted" for d in documents for p in d["proposals"])
    return {
        "schema_version": SCHEMA_VERSION,
        "batch_id": f"KVB-{sha256_text(canonical_json(identity))[:24]}",
        "created_at": utc_now(),
        "source_type": "knowledge_vault",
        "source_root_label": "knowledge-vault",
        "collector_version": COLLECTOR_VERSION,
        "prompt_version": PROMPT_VERSION,
        "model": model_info,
        "documents": documents,
        "stats": {"documents": len(documents), "accepted": accepted, "held": held, "fallback": fallback_count},
    }


def validate_batch(batch):
    if not isinstance(batch, dict) or batch.get("schema_version") != SCHEMA_VERSION:
        raise ValueError(f"unsupported schema_version: {batch.get('schema_version') if isinstance(batch, dict) else None}")
    if not re.fullmatch(r"KVB-[0-9a-f]{24}", str(batch.get("batch_id") or "")):
        raise ValueError("invalid batch_id")
    expected = f"KVB-{sha256_text(canonical_json(batch_identity(batch.get('documents') or [], batch.get('model') or {})))[:24]}"
    if batch["batch_id"] != expected:
        raise ValueError("batch_id does not match content")
    for document in batch.get("documents") or []:
        if not re.fullmatch(r"KVD-[0-9a-f]{20}", str(document.get("document_id") or "")):
            raise ValueError("invalid document_id")
        path = str(document.get("relative_path") or "")
        if not path or Path(path).is_absolute() or ".." in Path(path).parts or ":" in path:
            raise ValueError("relative_path must stay inside knowledge-vault")
        fragment_text = "\n".join(str(item.get("excerpt") or "") for item in document.get("fragments") or [])
        for proposal in document.get("proposals") or []:
            if not re.fullmatch(r"KVP-[0-9a-f]{20}", str(proposal.get("proposal_id") or "")):
                raise ValueError("invalid proposal_id")
            for quote in proposal.get("evidence_quotes") or []:
                if proposal.get("validation", {}).get("status") == "accepted" and quote not in fragment_text:
                    raise ValueError("proposal evidence is missing from stored fragments")


def import_batch(conn, batch, manifest_sha256=None):
    validate_batch(batch)
    batch_id = batch["batch_id"]
    existing = conn.execute("select batch_id, stats_json from intake_batches where batch_id = ?", (batch_id,)).fetchone()
    if existing:
        stats = json.loads(existing["stats_json"])
        return {"batchId": batch_id, "created": stats.get("created", 0), "held": stats.get("held", 0), "duplicate": True}

    import db_tool

    run = db_tool.start_source_sync(conn, {"source": "knowledge_vault_batch"})
    created = 0
    held = 0
    conn.execute(
        """insert into intake_batches(
             batch_id, schema_version, source_type, source_root_label, created_at, imported_at,
             manifest_sha256, prompt_version, model_json, state, stats_json
           ) values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            batch_id,
            batch["schema_version"],
            batch.get("source_type", "knowledge_vault"),
            batch.get("source_root_label", "knowledge-vault"),
            batch.get("created_at") or utc_now(),
            utc_now(),
            manifest_sha256,
            batch.get("prompt_version", PROMPT_VERSION),
            canonical_json(batch.get("model") or {}),
            "importing",
            "{}",
        ),
    )
    for document in batch.get("documents") or []:
        conn.execute(
            """insert or ignore into source_documents(
                 document_id, source_type, source_ref, scope, content_hash, modified_at,
                 collected_at, summary, metadata_json
               ) values (?, 'knowledge_vault', ?, ?, ?, ?, ?, ?, ?)""",
            (
                document["document_id"], document["relative_path"], document.get("scope", ""),
                document["content_hash"], document.get("modified_at"), batch.get("created_at") or utc_now(),
                document.get("summary", ""), canonical_json({"batch_id": batch_id}),
            ),
        )
        for fragment in document.get("fragments") or []:
            conn.execute(
                """insert or ignore into source_fragments(
                     fragment_id, document_id, heading, line_start, line_end, excerpt, content_hash, extraction_method
                   ) values (?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    fragment["fragment_id"], document["document_id"], fragment.get("heading", ""),
                    fragment.get("line_start"), fragment.get("line_end"), fragment["excerpt"],
                    fragment["content_hash"], fragment.get("extraction_method", "unknown"),
                ),
            )
        ai_run = document["ai_run"]
        conn.execute(
            """insert or ignore into ai_runs(
                 run_id, batch_id, document_id, provider, model, prompt_version, input_hash,
                 output_hash, status, error, created_at
               ) values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                ai_run["run_id"], batch_id, document["document_id"], ai_run.get("provider", "unknown"),
                ai_run.get("model", "unknown"), ai_run.get("prompt_version", PROMPT_VERSION),
                ai_run["input_hash"], ai_run["output_hash"], ai_run["status"], ai_run.get("error"),
                ai_run.get("created_at") or utc_now(),
            ),
        )
        for proposal in document.get("proposals") or []:
            status = proposal.get("validation", {}).get("status", "held")
            candidate_id = None
            if status == "accepted":
                candidate_id = f"KVAI-{proposal['proposal_id'].removeprefix('KVP-')}"
                evidence = proposal.get("evidence_quotes") or []
                db_tool.insert_candidate(conn, {
                    "id": candidate_id,
                    "status": "pending",
                    "title": proposal["title"],
                    "kind": proposal.get("kind", "todo"),
                    "source": "knowledge_vault",
                    "sourceLabel": document.get("scope") or "knowledge-vault",
                    "sourcePath": document["relative_path"],
                    "tags": sorted(set(["knowledge-vault", document.get("scope", ""), "ai-proposed"] + proposal.get("tags", [])) - {""}),
                    "confidence": proposal.get("confidence", "medium"),
                    "missing": proposal.get("missing", []),
                    "occurred": (document.get("modified_at") or utc_now())[:10],
                    "excerpt": evidence[0] if evidence else proposal["todo"],
                    "summary": proposal["summary"],
                    "todo": proposal["todo"],
                    "schedule": proposal.get("schedule", "候補なし"),
                    "preview": f"VaultAIProposal: {proposal['todo'][:80]}",
                })
                status = "candidate_pending"
                created += 1
            else:
                held += 1
            conn.execute(
                """insert or ignore into candidate_proposals(
                     proposal_id, batch_id, document_id, status, title, summary, todo, kind,
                     schedule, confidence, missing_json, tags_json, evidence_json, validation_json,
                     candidate_id, created_at, updated_at
                   ) values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    proposal["proposal_id"], batch_id, document["document_id"], status,
                    proposal["title"], proposal["summary"], proposal["todo"], proposal.get("kind", "todo"),
                    proposal.get("schedule", "候補なし"), proposal.get("confidence", "low"),
                    canonical_json(proposal.get("missing", [])), canonical_json(proposal.get("tags", [])),
                    canonical_json(proposal.get("evidence_quotes", [])), canonical_json(proposal.get("validation", {})),
                    candidate_id, utc_now(), utc_now(),
                ),
            )
    stats = {"created": created, "held": held, "documents": len(batch.get("documents") or [])}
    conn.execute("update intake_batches set state = 'succeeded', stats_json = ? where batch_id = ?", (canonical_json(stats), batch_id))
    conn.execute("update sources set last_imported_at = ? where id = 'knowledge_vault'", (db_tool.now(),))
    db_tool.finish_source_sync(conn, {
        "run_id": run["run_id"], "state": "succeeded", "scanned": stats["documents"],
        "created": created, "skipped": held,
    })
    return {"batchId": batch_id, "created": created, "held": held, "duplicate": False}


def write_batch(batch, output_path, manifest_path):
    output_path = Path(output_path)
    manifest_path = Path(manifest_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    encoded = (json.dumps(batch, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    output_path.write_bytes(encoded)
    digest = hashlib.sha256(encoded).hexdigest()
    manifest = {"schema_version": "threadline.batch-manifest.v1", "batch_id": batch["batch_id"], "batch_file": output_path.name, "sha256": digest}
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return manifest


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description="Thread Line knowledge-vault intake")
    subparsers = parser.add_subparsers(dest="command", required=True)
    collect = subparsers.add_parser("collect-vault-batch")
    collect.add_argument("--root", required=True)
    collect.add_argument("--output", required=True)
    collect.add_argument("--manifest", required=True)
    collect.add_argument("--targets", default=",".join(DEFAULT_TARGETS))
    collect.add_argument("--limit", type=int, default=30)
    collect.add_argument("--allowed-tags", default="")
    collect.add_argument("--llm-base-url", default=os.environ.get("LOCAL_LLM_BASE_URL") or os.environ.get("OLLAMA_BASE_URL") or "")
    collect.add_argument("--llm-model", default=os.environ.get("LOCAL_LLM_MODEL", "local-unverified"))
    collect.add_argument("--llm-timeout", type=int, default=60)
    collect.add_argument("--no-llm", action="store_true")
    collect.add_argument("--require-llm", action="store_true")
    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)
    if args.command == "collect-vault-batch":
        use_llm = not args.no_llm and bool(args.llm_base_url)
        if args.require_llm and not use_llm:
            raise ValueError("--require-llm needs --llm-base-url")
        client = None
        if use_llm:
            client = openai_compatible_client(
                args.llm_base_url,
                args.llm_model,
                timeout=args.llm_timeout,
                api_key=os.environ.get("LOCAL_LLM_API_KEY", ""),
            )
        batch = collect_batch(
            args.root,
            targets=[item.strip() for item in args.targets.split(",") if item.strip()],
            limit=args.limit,
            allowed_tags=[item.strip() for item in args.allowed_tags.split(",") if item.strip()],
            llm=client,
            model=args.llm_model if use_llm else "deterministic",
        )
        if args.require_llm and batch["stats"]["fallback"]:
            raise RuntimeError("one or more LLM calls fell back")
        manifest = write_batch(batch, args.output, args.manifest)
        print(json.dumps({
            "batchId": batch["batch_id"],
            "documents": batch["stats"]["documents"],
            "accepted": batch["stats"]["accepted"],
            "held": batch["stats"]["held"],
            "fallback": batch["stats"]["fallback"],
            "sha256": manifest["sha256"],
        }, ensure_ascii=False))
        return 0
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
