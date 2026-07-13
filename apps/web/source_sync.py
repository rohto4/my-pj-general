"""Source import domain shared by the HTTP boundary and the oneshot worker.

The module owns source-specific scanning and candidate mapping. Persistence is
kept behind ``db_tool`` so the current SQLite contract remains unchanged while
the worker can call the same domain without going through an HTTP handler.
"""

import hashlib
from datetime import datetime
from pathlib import Path

import db_tool


TAG_HINTS = {
    "gantt": ("gantt", "ガント", "timeline", "タイムライン"),
    "tasks": ("task", "todo", "タスク", "作業", "対応"),
    "ui": ("ui", "ux", "画面", "表示", "導線"),
    "schedule": ("schedule", "calendar", "予定", "期限", "日程"),
    "review": ("review", "レビュー", "確認", "受入"),
    "research": ("research", "調査", "検証"),
}


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
            digest = hashlib.sha1(str(path).encode("utf-8")).hexdigest()[:10]
            candidate_id = f"KV-{digest}"
            if conn.execute("select 1 from candidates where id = ?", (candidate_id,)).fetchone():
                skipped += 1
                continue
            lines = [line.strip() for line in text.splitlines() if line.strip()]
            heading = next((line.lstrip("# ").strip() for line in lines if line.startswith("#")), "")
            title = heading or path.stem
            body_lines = meaningful_lines(text)
            excerpt = candidate_excerpt(body_lines)
            relative = path.relative_to(root).as_posix() if root in path.parents else path.name
            top = relative.split("/")[0]
            item = {
                "id": candidate_id,
                "status": "pending",
                "title": title[:120],
                "kind": db_tool.classify_text(text),
                "source": "knowledge_vault",
                "sourceLabel": top,
                "sourcePath": str(path).replace("\\", "/"),
                "tags": candidate_tags(conn, ["knowledge-vault", top, "imported"], text),
                "confidence": "medium",
                "missing": ["owner confirm"],
                "occurred": datetime.fromtimestamp(path.stat().st_mtime).strftime("%Y-%m-%d"),
                "excerpt": excerpt,
                "summary": candidate_summary("knowledge-vault", relative, body_lines, title),
                "todo": title[:80],
                "schedule": "候補なし",
                "preview": f"VaultCandidate: {title[:80]}",
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
