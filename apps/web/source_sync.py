"""Source import domain shared by the HTTP boundary and the oneshot worker.

The module owns source-specific scanning and candidate mapping. Persistence is
kept behind ``db_tool`` so the current SQLite contract remains unchanged while
the worker can call the same domain without going through an HTTP handler.
"""

import hashlib
import re
from datetime import datetime
from pathlib import Path

import db_tool
import candidate_proposal


TAG_HINTS = {
    "gantt": ("gantt", "ガント", "timeline", "タイムライン"),
    "tasks": ("task", "todo", "タスク", "作業", "対応"),
    "ui": ("ui", "ux", "画面", "表示", "導線"),
    "schedule": ("schedule", "calendar", "予定", "期限", "日程"),
    "review": ("review", "レビュー", "確認", "受入"),
    "research": ("research", "調査", "検証"),
}


VAULT_TASK_CANDIDATE_PROMPT = """knowledge-vaultから未完了の次アクションだけを候補化する。
見出しやREADME、完了済み記録をタスク化しない。各候補は原文の行動を保ち、
対象・成果・次アクションが分かる一文にする。識別子や英語固有名詞は無理に翻訳しない。"""

ACTION_HEADINGS = {"next actions", "next action", "next steps", "next step", "次にやるべきこと", "次のアクション", "次アクション", "todo"}


def import_source_proposals(conn, payload):
    """Persist accepted proposals from a source collector as pending only."""
    source = str(payload.get("source") or "").strip()
    if source not in candidate_proposal.ALLOWED_SOURCE_KINDS - {"knowledge_vault", "chat"}:
        raise ValueError(f"unsupported AI source import: {source}")
    items = payload.get("items") or []
    allowed_tags = payload.get("allowedTags") or []
    source_label = payload.get("sourceLabel") or source
    run = db_tool.start_source_sync(conn, {"source": source, "cursor_before": payload.get("cursor")})
    imported = 0
    skipped = 0
    held = 0
    candidate_ids = []
    normalized_items = []
    try:
        for item in items:
            source_ref = str(item.get("sourceRef") or "").strip()
            source_body = str(item.get("sourceBody") or "").strip()
            if not source_ref or not source_body:
                skipped += 1
                continue
            normalized = candidate_proposal.normalize_output(
                item.get("output") or {},
                source_body,
                allowed_tags=allowed_tags,
                source_kind=source,
                source_ref=source_ref,
            )
            normalized_items.append({"sourceRef": source_ref, **normalized})
            for proposal in normalized["proposals"]:
                if proposal["validation"]["status"] != "accepted":
                    held += 1
                    continue
                digest = hashlib.sha1(
                    f"{source}:{source_ref}:{proposal['proposal_id']}".encode("utf-8")
                ).hexdigest()[:12]
                prefix = "SL" if source == "slack" else "MK"
                candidate_id = f"{prefix}AI-{digest}"
                if conn.execute("select 1 from candidates where id = ?", (candidate_id,)).fetchone():
                    skipped += 1
                    continue
                evidence = proposal.get("evidence_quotes") or []
                db_tool.insert_candidate(conn, {
                    "id": candidate_id,
                    "status": "pending",
                    "title": proposal["title"],
                    "kind": proposal["kind"],
                    "source": source,
                    "sourceLabel": source_label,
                    "sourcePath": source_ref,
                    "tags": candidate_tags(conn, [source, "ai-proposed"], source_body),
                    "confidence": proposal["confidence"],
                    "missing": proposal["missing"],
                    "occurred": item.get("occurred") or datetime.now().strftime("%Y-%m-%d"),
                    "excerpt": evidence[0] if evidence else proposal["todo"],
                    "summary": proposal["summary"],
                    "todo": proposal["todo"],
                    "schedule": proposal["schedule"],
                    "preview": f"AIProposal/{proposal['proposal_type']}: {proposal['title'][:80]}",
                })
                imported += 1
                candidate_ids.append(candidate_id)
        conn.execute("update sources set last_imported_at = ? where id = ?", (db_tool.now(), source))
        sync_run = db_tool.finish_source_sync(conn, {
            "run_id": run["run_id"],
            "state": "succeeded",
            "cursor_after": payload.get("cursor_after"),
            "scanned": len(items),
            "created": imported,
            "skipped": skipped,
        })
        return {
            "imported": imported,
            "skipped": skipped,
            "held": held,
            "scanned": len(items),
            "ids": candidate_ids,
            "items": normalized_items,
            "syncRun": sync_run,
        }
    except Exception as error:
        db_tool.finish_source_sync(conn, {
            "run_id": run["run_id"],
            "state": "failed",
            "failed": 1,
            "error": type(error).__name__,
        })
        raise


def frontmatter(text):
    if not text.startswith("---"):
        return {}
    closing = text.find("\n---", 3)
    if closing < 0:
        return {}
    fields = {}
    for line in text[3:closing].splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        fields[key.strip().lower()] = value.strip().strip('"\'').lower()
    return fields


def next_actions(text):
    """Return unfinished list items from explicit next-action sections."""
    lines = text.splitlines()
    collecting = False
    actions = []
    for raw in lines:
        stripped = raw.strip()
        if stripped.startswith("#"):
            heading = stripped.lstrip("#").strip().lower()
            collecting = heading in ACTION_HEADINGS
            continue
        if not collecting or not stripped:
            continue
        if re.match(r"^[-*+]\s*\[[xX]\]", stripped):
            continue
        action = re.sub(r"^(?:[-*+]\s+|\d+[.)]\s*)", "", stripped).strip()
        if action:
            actions.append(action.rstrip("。."))
    return actions


def meaningful_lines(text):
    """Return body lines that are useful in a candidate preview, not markdown chrome."""
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    return [line for line in lines if not line.startswith("#") and line not in {"---", "```"}]


def candidate_excerpt(lines, limit=360):
    excerpt = "\n".join(lines)
    return excerpt[:limit].rstrip()


def candidate_summary(source_label, relative, lines, fallback_title):
    body = " ".join(lines).strip()
    detail = (body or fallback_title).replace("\n", " ")[:180].rstrip()
    return f"{source_label} / {relative}: {detail}"


def candidate_tags(conn, source_tags, text):
    """Keep source provenance and select only matching tags already in the master."""
    known = {
        row["name"].strip()
        for row in conn.execute("select name from tags where visible = 1").fetchall()
        if row["name"].strip()
    }
    lowered = text.lower()
    selected = list(source_tags)
    for tag, terms in TAG_HINTS.items():
        if tag in known and any(term in lowered for term in terms):
            selected.append(tag)
    for tag in known:
        normalized = tag.lower().strip()
        if normalized and normalized not in TAG_HINTS and normalized in lowered:
            selected.append(tag)
    return sorted(set(selected))


def import_knowledge_vault(conn, payload):
    run = db_tool.start_source_sync(conn, {"source": "knowledge_vault", "cursor_before": payload.get("cursor")})
    root = Path(payload.get("root") or "G:/knowledge-vault")
    controls = db_tool.load_admin_controls(conn)
    configured_targets = [item["id"] for item in controls["scopes"] if item.get("enabled")]
    targets = payload.get("targets") or configured_targets
    limit = int(payload.get("limit") or 30)
    imported = 0
    skipped = 0
    files = []
    try:
        for target in targets:
            base = root / target
            if not base.exists():
                continue
            files.extend([path for path in base.rglob("*.md") if path.is_file()])
        files = sorted(files, key=lambda path: path.stat().st_mtime, reverse=True)[:limit]
        for path in files:
            try:
                text = path.read_text(encoding="utf-8-sig", errors="ignore").strip()
            except OSError:
                skipped += 1
                continue
            if not text:
                skipped += 1
                continue
            metadata = frontmatter(text)
            if path.name.lower() == "readme.md" or metadata.get("status") in {"completed", "done", "archived"}:
                skipped += 1
                continue
            lines = [line.strip() for line in text.splitlines() if line.strip()]
            heading = next((line.lstrip("# ").strip() for line in lines if line.startswith("#")), "")
            title = heading or path.stem
            body_lines = meaningful_lines(text)
            relative = path.relative_to(root).as_posix() if root in path.parents else path.name
            top = relative.split("/")[0]
            actions = next_actions(text)
            if not actions and top == "inbox":
                actions = [title]
            if not actions:
                skipped += 1
                continue
            for index, action in enumerate(actions, start=1):
                digest = hashlib.sha1(f"{path}:{index}".encode("utf-8")).hexdigest()[:10]
                candidate_id = f"KV-{digest}"
                if conn.execute("select 1 from candidates where id = ?", (candidate_id,)).fetchone():
                    skipped += 1
                    continue
                excerpt = candidate_excerpt([action])
                item = {
                    "id": candidate_id,
                    "status": "pending",
                    "title": action[:120],
                    "kind": "todo",
                    "source": "knowledge_vault",
                    "sourceLabel": top,
                    "sourcePath": str(path).replace("\\", "/"),
                    "tags": candidate_tags(conn, ["knowledge-vault", top, "imported"], text),
                    "confidence": "medium",
                    "missing": ["owner confirm"],
                    "occurred": datetime.fromtimestamp(path.stat().st_mtime).strftime("%Y-%m-%d"),
                    "excerpt": excerpt,
                    "summary": candidate_summary("knowledge-vault", relative, [action], title),
                    "todo": action[:80],
                    "schedule": "候補なし",
                    "preview": f"VaultCandidate: {action[:80]}",
                }
                db_tool.insert_candidate(conn, item)
                imported += 1
        conn.execute(
            "update sources set last_imported_at = ? where id = ?",
            (db_tool.now(), "knowledge_vault"),
        )
        sync_run = db_tool.finish_source_sync(
            conn,
            {
                "run_id": run["run_id"],
                "state": "succeeded",
                "cursor_after": payload.get("cursor_after"),
                "scanned": len(files),
                "created": imported,
                "skipped": skipped,
            },
        )
        return {"imported": imported, "skipped": skipped, "scanned": len(files), "syncRun": sync_run}
    except Exception as error:
        db_tool.finish_source_sync(conn, {"run_id": run["run_id"], "state": "failed", "failed": 1, "error": str(error)})
        raise


def import_slack(conn, payload):
    run = db_tool.start_source_sync(conn, {"source": "slack", "cursor_before": payload.get("cursor")})
    messages = payload.get("messages") or []
    imported = 0
    skipped = 0
    imported_ids = []
    try:
        for message in messages:
            text = (message.get("text") or "").strip()
            if not text or "チャンネルに参加" in text:
                skipped += 1
                continue
            ts = str(message.get("ts") or message.get("time") or db_tool.now())
            digest = hashlib.sha1(f"slack:{ts}:{text}".encode("utf-8")).hexdigest()[:10]
            candidate_id = f"SL-{digest}"
            if conn.execute("select 1 from candidates where id = ?", (candidate_id,)).fetchone():
                skipped += 1
                continue
            lines = meaningful_lines(text)
            title = (lines[0] if lines else text.splitlines()[0]).lstrip("# ")[:100]
            item = {
                "id": candidate_id,
                "status": "pending",
                "title": title,
                "kind": db_tool.classify_text(text),
                "source": "slack",
                "sourceLabel": payload.get("channelName") or "memo-ideas",
                "sourcePath": payload.get("channelUrl") or "https://unibell4-dev.slack.com/archives/C0BG4TCPAUD",
                "tags": candidate_tags(conn, ["slack", "memo-ideas", "imported"], text),
                "confidence": "medium",
                "missing": ["owner confirm"],
                "occurred": payload.get("occurred") or datetime.now().strftime("%Y-%m-%d"),
                "excerpt": candidate_excerpt(lines or [text]),
                "summary": candidate_summary(payload.get("channelName") or "memo-ideas", "Slack", lines, title),
                "todo": title,
                "schedule": "候補なし",
                "preview": f"SlackCandidate: {title}",
            }
            db_tool.insert_candidate(conn, item)
            imported += 1
            imported_ids.append(candidate_id)
        conn.execute(
            "update sources set last_imported_at = ? where id = ?",
            (db_tool.now(), "slack"),
        )
        sync_run = db_tool.finish_source_sync(
            conn,
            {
                "run_id": run["run_id"],
                "state": "succeeded",
                "cursor_after": payload.get("cursor_after"),
                "scanned": len(messages),
                "created": imported,
                "skipped": skipped,
            },
        )
        return {
            "imported": imported,
            "skipped": skipped,
            "scanned": len(messages),
            "ids": imported_ids,
            "syncRun": sync_run,
        }
    except Exception as error:
        db_tool.finish_source_sync(conn, {"run_id": run["run_id"], "state": "failed", "failed": 1, "error": str(error)})
        raise
