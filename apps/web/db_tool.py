import json
import os
import sqlite3
import sys
import hashlib
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parent
DB_PATH = Path(os.environ.get("P0_DB_PATH", ROOT / "data" / "p0.sqlite"))


GANTT_TASKS = [
    {"id": "GT-001", "title": "P0画面構成を固める", "owner": "Codex", "progress": 65, "start": 4, "span": 22, "state": "active", "dependency": "UI参考資料"},
    {"id": "GT-002", "title": "確認待ちキューを調整する", "owner": "Codex", "progress": 78, "start": 15, "span": 28, "state": "active", "dependency": "AI候補モデル"},
    {"id": "GT-003", "title": "読み取り専用ガントを作る", "owner": "Codex", "progress": 42, "start": 36, "span": 24, "state": "late", "dependency": "TODO予定候補"},
    {"id": "GT-004", "title": "ユーザーが画面を触って確認する", "owner": "ユーザー", "progress": 10, "start": 62, "span": 26, "state": "active", "dependency": "P0薄い画面"},
]


def connect():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def now():
    return datetime.now().isoformat(timespec="seconds")


def execute_schema(conn):
    conn.executescript(
        """
        create table if not exists sources (
          id text primary key,
          label text not null,
          path text not null,
          enabled integer not null default 1,
          source_kind text not null,
          last_imported_at text
        );
        create table if not exists tags (
          id integer primary key autoincrement,
          name text not null unique,
          category text not null default 'general',
          color text not null default 'blue',
          visible integer not null default 1
        );
        create table if not exists candidates (
          id text primary key,
          status text not null,
          title text not null,
          kind text not null,
          source_id text not null,
          source_label text not null,
          source_path text not null,
          confidence text not null,
          missing_json text not null,
          occurred text not null,
          excerpt text not null,
          summary text not null,
          todo text not null,
          schedule text not null,
          preview text not null,
          created_at text not null,
          updated_at text not null
        );
        create table if not exists candidate_tags (
          candidate_id text not null,
          tag_id integer not null,
          primary key (candidate_id, tag_id)
        );
        create table if not exists decisions (
          id integer primary key autoincrement,
          candidate_id text not null,
          action text not null,
          note text,
          created_at text not null
        );
        create table if not exists settings (
          key text primary key,
          value_json text not null
        );
        create table if not exists prompt_templates (
          id text primary key,
          name text not null,
          target text not null,
          body text not null,
          enabled integer not null default 1
        );
        create table if not exists gantt_tasks (
          id text primary key,
          title text not null,
          owner text not null,
          progress integer not null,
          start integer not null,
          span integer not null,
          state text not null,
          dependency text not null
        );
        """
    )


def ensure_tag(conn, name):
    conn.execute("insert or ignore into tags(name) values (?)", (name,))
    return conn.execute("select id from tags where name = ?", (name,)).fetchone()["id"]


ADMIN_CONTROL_DEFAULTS = {
    "roles": [
        {"id": "owner", "name": "Owner", "enabled": True, "detail": "全画面閲覧、GO / 編集 / 不要 / アーカイブ可", "meta": "full control"},
        {"id": "collaborator", "name": "外部協力者", "enabled": True, "detail": "スケジュール中心表示、詳細タスクは制限", "meta": "schedule centered"},
    ],
    "automation": [
        {"id": "all-pending", "name": "P0確認方針", "enabled": True, "detail": "AI候補は全件確認待ち。P0完了後に部分自動確定へ移行", "meta": "all pending first"},
        {"id": "high-confidence", "name": "高信頼TODO", "enabled": False, "detail": "高信頼かつ不足なし候補のみ自動GO候補", "meta": "after P0"},
    ],
    "scopes": [
        {"id": "records", "name": "knowledge-vault/records", "enabled": True, "detail": "日次記録と復元価値のある作業記録", "meta": "real scan"},
        {"id": "inbox", "name": "knowledge-vault/inbox", "enabled": True, "detail": "検討や知見の種を回収対象に含める", "meta": "real scan"},
        {"id": "tasks", "name": "knowledge-vault/tasks", "enabled": True, "detail": "実行候補と実施予定を回収対象に含める", "meta": "real scan"},
        {"id": "memory", "name": "knowledge-vault/memory L1-L2", "enabled": True, "detail": "記憶層のうちP0判定に必要な範囲", "meta": "real scan"},
    ],
}


def ensure_setting(conn, key, value):
    row = conn.execute("select value_json from settings where key = ?", (key,)).fetchone()
    if row is None:
        conn.execute("insert into settings(key, value_json) values (?, ?)", (key, json.dumps(value, ensure_ascii=False)))


def load_admin_controls(conn):
    result = {}
    for key, defaults in ADMIN_CONTROL_DEFAULTS.items():
        setting_key = f"admin.{key}"
        ensure_setting(conn, setting_key, defaults)
        row = conn.execute("select value_json from settings where key = ?", (setting_key,)).fetchone()
        result[key] = json.loads(row["value_json"])
    return result


def insert_candidate(conn, item):
    ts = now()
    conn.execute(
        """
        insert or replace into candidates(
          id, status, title, kind, source_id, source_label, source_path, confidence,
          missing_json, occurred, excerpt, summary, todo, schedule, preview, created_at, updated_at
        ) values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, coalesce((select created_at from candidates where id = ?), ?), ?)
        """,
        (
            item["id"],
            item.get("status", "pending"),
            item["title"],
            item["kind"],
            item["source"],
            item.get("sourceLabel", item["source"]),
            item.get("sourcePath", ""),
            item.get("confidence", "medium"),
            json.dumps(item.get("missing", []), ensure_ascii=False),
            item.get("occurred", datetime.now().strftime("%Y-%m-%d")),
            item.get("excerpt", item["title"]),
            item.get("summary", item["title"]),
            item.get("todo", f"{item['title']} を整理する"),
            item.get("schedule", "候補なし"),
            item.get("preview", item["title"]),
            item["id"],
            ts,
            ts,
        ),
    )
    conn.execute("delete from candidate_tags where candidate_id = ?", (item["id"],))
    for tag in item.get("tags", []):
        tag_id = ensure_tag(conn, tag)
        conn.execute("insert or ignore into candidate_tags(candidate_id, tag_id) values (?, ?)", (item["id"], tag_id))


def seed(conn):
    sources = [
        ("web", "Web手入力", "web://manual", 1, "manual"),
        ("slack", "Slack memo-ideas", "https://unibell4-dev.slack.com/archives/C0BG4TCPAUD", 1, "connector"),
        ("knowledge_vault", "knowledge-vault", "G:/knowledge-vault", 1, "local_scan"),
        ("misskey", "Misskey (未接続)", "misskey://not-connected", 0, "connector"),
    ]
    conn.executemany("insert or ignore into sources(id, label, path, enabled, source_kind) values (?, ?, ?, ?, ?)", sources)
    conn.execute(
        "update sources set label = ?, path = ?, source_kind = ? where id = ?",
        ("Misskey (未接続)", "misskey://not-connected", "connector", "misskey"),
    )
    for task in GANTT_TASKS:
        conn.execute(
            "insert or ignore into gantt_tasks(id, title, owner, progress, start, span, state, dependency) values (?, ?, ?, ?, ?, ?, ?, ?)",
            (task["id"], task["title"], task["owner"], task["progress"], task["start"], task["span"], task["state"], task["dependency"]),
        )
    ensure_setting(conn, "automation.mode", {"label": "P0確認方針", "value": "all_pending_first"})
    ensure_setting(conn, "slack.memo_ideas", {"channel": "C0BG4TCPAUD", "mode": "connector_payload_import"})
    load_admin_controls(conn)
    templates = [
        ("codex-start", "Codex起動支援", "candidate", "AGENTS.md と PROJECT.md を読み、選択候補を実装タスクとして開始する。", 1),
        ("candidate-triage", "候補整理", "intake", "入口データを TODO / 検討 / 気になる事 / 予定候補に分類する。", 1),
        ("go-promotion", "GO後作成", "decision", "GOした候補をタスク、予定候補、判断記録へ展開する。", 1),
    ]
    conn.executemany("insert or ignore into prompt_templates(id, name, target, body, enabled) values (?, ?, ?, ?, ?)", templates)
    marker = conn.execute("select 1 from settings where key = ?", ("migration.remove-initial-candidates.v1",)).fetchone()
    if marker is None:
        conn.execute("delete from decisions where candidate_id in ('AI-001', 'AI-002', 'AI-003', 'AI-004', 'AI-005', 'AI-006')")
        conn.execute("delete from candidate_tags where candidate_id in ('AI-001', 'AI-002', 'AI-003', 'AI-004', 'AI-005', 'AI-006')")
        conn.execute("delete from candidates where id in ('AI-001', 'AI-002', 'AI-003', 'AI-004', 'AI-005', 'AI-006')")
        ensure_setting(conn, "migration.remove-initial-candidates.v1", {"appliedAt": now()})


def rows_to_candidates(conn):
    rows = conn.execute("select * from candidates order by occurred desc, id asc").fetchall()
    result = []
    for row in rows:
        tags = conn.execute(
            """
            select t.name from tags t
            join candidate_tags ct on ct.tag_id = t.id
            where ct.candidate_id = ?
            order by t.name
            """,
            (row["id"],),
        ).fetchall()
        result.append(
            {
                "id": row["id"],
                "status": row["status"],
                "title": row["title"],
                "kind": row["kind"],
                "source": row["source_id"],
                "sourceLabel": row["source_label"],
                "sourcePath": row["source_path"],
                "tags": [tag["name"] for tag in tags],
                "confidence": row["confidence"],
                "missing": json.loads(row["missing_json"]),
                "occurred": row["occurred"],
                "excerpt": row["excerpt"],
                "summary": row["summary"],
                "todo": row["todo"],
                "schedule": row["schedule"],
                "preview": row["preview"],
            }
        )
    return result


def bootstrap(conn):
    candidates = rows_to_candidates(conn)
    log = [
        {"action": row["action"], "title": row["title"], "time": row["created_at"]}
        for row in conn.execute(
            """
            select d.action, c.title, d.created_at
            from decisions d join candidates c on c.id = d.candidate_id
            order by d.id desc limit 20
            """
        ).fetchall()
    ]
    sources = [dict(row) for row in conn.execute("select * from sources order by id").fetchall()]
    tags = [dict(row) for row in conn.execute("select * from tags order by name").fetchall()]
    gantt = [dict(row) for row in conn.execute("select * from gantt_tasks order by id").fetchall()]
    templates = [dict(row) for row in conn.execute("select * from prompt_templates order by id").fetchall()]
    return {"candidates": candidates, "log": log, "sources": sources, "tags": tags, "ganttTasks": gantt, "promptTemplates": templates, "adminControls": load_admin_controls(conn), "dbPath": str(DB_PATH)}


def next_candidate_id(conn):
    rows = conn.execute("select id from candidates where id like 'AI-%'").fetchall()
    max_id = 0
    for row in rows:
        try:
            max_id = max(max_id, int(row["id"].split("-")[1]))
        except (IndexError, ValueError):
            continue
    return f"AI-{max_id + 1:03d}"


def create_candidate(conn, payload):
    item = {
        "id": next_candidate_id(conn),
        "status": "pending",
        "title": payload.get("title") or "Untitled intake",
        "kind": payload.get("kind") or "idea",
        "source": payload.get("source") or "web",
        "sourceLabel": payload.get("sourceLabel") or "manual",
        "sourcePath": payload.get("url") or "web://manual",
        "tags": payload.get("tags") or ["manual"],
        "confidence": payload.get("confidence") or "medium",
        "missing": ["schedule decision"] if payload.get("schedule") == "none" else [],
        "occurred": datetime.now().strftime("%Y-%m-%d"),
        "excerpt": payload.get("body") or payload.get("title") or "Untitled intake",
        "summary": (payload.get("body") or payload.get("title") or "Untitled intake")[:140],
        "todo": f"{payload.get('title') or 'Untitled intake'} を整理する",
        "schedule": "候補なし" if payload.get("schedule") == "none" else "2026-07-10 / 30 min",
        "preview": f"{payload.get('kind') or 'idea'}: {payload.get('title') or 'Untitled intake'}",
    }
    insert_candidate(conn, item)
    conn.execute("insert into decisions(candidate_id, action, note, created_at) values (?, ?, ?, ?)", (item["id"], "created", "manual intake", now()))
    return item


def update_status(conn, candidate_id, status):
    row = conn.execute("select id from candidates where id = ?", (candidate_id,)).fetchone()
    if not row:
        raise ValueError(f"candidate not found: {candidate_id}")
    conn.execute("update candidates set status = ?, updated_at = ? where id = ?", (status, now(), candidate_id))
    conn.execute("insert into decisions(candidate_id, action, note, created_at) values (?, ?, ?, ?)", (candidate_id, status, "queue action", now()))
    return {"id": candidate_id, "status": status}


def update_candidate(conn, candidate_id, payload):
    row = conn.execute("select * from candidates where id = ?", (candidate_id,)).fetchone()
    if not row:
        raise ValueError(f"candidate not found: {candidate_id}")
    tags = payload.get("tags")
    if isinstance(tags, str):
        tags = [tag.strip() for tag in tags.split(",") if tag.strip()]
    fields = {
        "title": payload.get("title", row["title"]),
        "summary": payload.get("summary", row["summary"]),
        "excerpt": payload.get("excerpt", row["excerpt"]),
        "todo": payload.get("todo", row["todo"]),
        "schedule": payload.get("schedule", row["schedule"]),
        "preview": payload.get("preview", row["preview"]),
        "kind": payload.get("kind", row["kind"]),
        "confidence": payload.get("confidence", row["confidence"]),
        "status": payload.get("status", "edited"),
    }
    conn.execute(
        """
        update candidates
        set title = ?, summary = ?, excerpt = ?, todo = ?, schedule = ?, preview = ?,
            kind = ?, confidence = ?, status = ?, updated_at = ?
        where id = ?
        """,
        (
            fields["title"],
            fields["summary"],
            fields["excerpt"],
            fields["todo"],
            fields["schedule"],
            fields["preview"],
            fields["kind"],
            fields["confidence"],
            fields["status"],
            now(),
            candidate_id,
        ),
    )
    if tags is not None:
        conn.execute("delete from candidate_tags where candidate_id = ?", (candidate_id,))
        for tag in tags:
            tag_id = ensure_tag(conn, tag)
            conn.execute("insert or ignore into candidate_tags(candidate_id, tag_id) values (?, ?)", (candidate_id, tag_id))
    conn.execute("insert into decisions(candidate_id, action, note, created_at) values (?, ?, ?, ?)", (candidate_id, fields["status"], "edited candidate", now()))
    return next(item for item in rows_to_candidates(conn) if item["id"] == candidate_id)


def delete_candidate(conn, candidate_id):
    conn.execute("delete from candidate_tags where candidate_id = ?", (candidate_id,))
    conn.execute("delete from decisions where candidate_id = ?", (candidate_id,))
    conn.execute("delete from candidates where id = ?", (candidate_id,))
    return {"id": candidate_id, "deleted": True}


def classify_text(text):
    lowered = text.lower()
    if "todo" in lowered or "task" in lowered or "やる" in text or "対応" in text:
        return "todo"
    if "予定" in text or "schedule" in lowered or "calendar" in lowered:
        return "schedule_candidate"
    if "懸念" in text or "concern" in lowered or "困" in text:
        return "concern"
    return "consideration"


def import_knowledge_vault(conn, payload):
    root = Path(payload.get("root") or "G:/knowledge-vault")
    controls = load_admin_controls(conn)
    configured_targets = [item["id"] for item in controls["scopes"] if item.get("enabled")]
    targets = payload.get("targets") or configured_targets
    limit = int(payload.get("limit") or 30)
    imported = 0
    skipped = 0
    files = []
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
        excerpt = "\n".join(lines[:4])[:360]
        relative = path.relative_to(root).as_posix() if root in path.parents else path.name
        top = relative.split("/")[0]
        item = {
            "id": candidate_id,
            "status": "pending",
            "title": title[:120],
            "kind": classify_text(text),
            "source": "knowledge_vault",
            "sourceLabel": top,
            "sourcePath": str(path).replace("\\", "/"),
            "tags": ["knowledge-vault", top, "imported"],
            "confidence": "medium",
            "missing": ["owner confirm"],
            "occurred": datetime.fromtimestamp(path.stat().st_mtime).strftime("%Y-%m-%d"),
            "excerpt": excerpt,
            "summary": f"knowledge-vault/{relative} から取り込んだ確認候補。",
            "todo": f"{title[:80]} を確認する",
            "schedule": "候補なし",
            "preview": f"VaultCandidate: {title[:80]}",
        }
        insert_candidate(conn, item)
        imported += 1
    conn.execute(
        "update sources set last_imported_at = ? where id = ?",
        (now(), "knowledge_vault"),
    )
    return {"imported": imported, "skipped": skipped, "scanned": len(files)}


def import_slack(conn, payload):
    messages = payload.get("messages") or []
    imported = 0
    skipped = 0
    imported_ids = []
    for message in messages:
        text = (message.get("text") or "").strip()
        if not text or "チャンネルに参加" in text:
            skipped += 1
            continue
        ts = str(message.get("ts") or message.get("time") or now())
        digest = hashlib.sha1(f"slack:{ts}:{text}".encode("utf-8")).hexdigest()[:10]
        candidate_id = f"SL-{digest}"
        if conn.execute("select 1 from candidates where id = ?", (candidate_id,)).fetchone():
            skipped += 1
            continue
        title = text.splitlines()[0][:100]
        item = {
            "id": candidate_id,
            "status": "pending",
            "title": title,
            "kind": classify_text(text),
            "source": "slack",
            "sourceLabel": payload.get("channelName") or "memo-ideas",
            "sourcePath": payload.get("channelUrl") or "https://unibell4-dev.slack.com/archives/C0BG4TCPAUD",
            "tags": ["slack", "memo-ideas", "imported"],
            "confidence": "medium",
            "missing": ["owner confirm"],
            "occurred": payload.get("occurred") or datetime.now().strftime("%Y-%m-%d"),
            "excerpt": text[:360],
            "summary": "Slack memo-ideas から取り込んだ確認候補。",
            "todo": f"{title} を確認する",
            "schedule": "候補なし",
            "preview": f"SlackCandidate: {title}",
        }
        insert_candidate(conn, item)
        imported += 1
        imported_ids.append(candidate_id)
    conn.execute(
        "update sources set last_imported_at = ? where id = ?",
        (now(), "slack"),
    )
    return {"imported": imported, "skipped": skipped, "scanned": len(messages), "ids": imported_ids}


def update_source(conn, source_id, payload):
    enabled = 1 if payload.get("enabled") else 0
    conn.execute("update sources set enabled = ? where id = ?", (enabled, source_id))
    return dict(conn.execute("select * from sources where id = ?", (source_id,)).fetchone())


def update_prompt_template(conn, template_id, payload):
    enabled = 1 if payload.get("enabled") else 0
    conn.execute("update prompt_templates set enabled = ? where id = ?", (enabled, template_id))
    return dict(conn.execute("select * from prompt_templates where id = ?", (template_id,)).fetchone())


def update_admin_control(conn, group, item_id, payload):
    if group not in ADMIN_CONTROL_DEFAULTS:
        raise ValueError(f"unknown admin control group: {group}")
    controls = load_admin_controls(conn)
    items = controls[group]
    item = next((item for item in items if item["id"] == item_id), None)
    if item is None:
        raise ValueError(f"admin control not found: {group}/{item_id}")
    item["enabled"] = bool(payload.get("enabled"))
    conn.execute(
        "update settings set value_json = ? where key = ?",
        (json.dumps(items, ensure_ascii=False), f"admin.{group}"),
    )
    return item


def create_tag(conn, payload):
    name = (payload.get("name") or "").strip()
    if not name:
        raise ValueError("tag name is required")
    existing = conn.execute("select * from tags where name = ?", (name,)).fetchone()
    if existing:
        return dict(existing)
    conn.execute(
        "insert into tags(name, category, color, visible) values (?, ?, ?, ?)",
        (name, payload.get("category") or "general", payload.get("color") or "blue", 1),
    )
    return dict(conn.execute("select * from tags where name = ?", (name,)).fetchone())


def update_tag(conn, tag_id, payload):
    row = conn.execute("select * from tags where id = ?", (tag_id,)).fetchone()
    if row is None:
        raise ValueError(f"tag not found: {tag_id}")
    visible = 1 if payload.get("visible") else 0
    conn.execute("update tags set visible = ? where id = ?", (visible, tag_id))
    return dict(conn.execute("select * from tags where id = ?", (tag_id,)).fetchone())


def main():
    command = sys.argv[1] if len(sys.argv) > 1 else "bootstrap"
    payload = json.loads(sys.stdin.read() or "{}")
    with connect() as conn:
        execute_schema(conn)
        seed(conn)
        if command == "bootstrap":
            output = bootstrap(conn)
        elif command == "create-candidate":
            output = create_candidate(conn, payload)
        elif command == "update-status":
            output = update_status(conn, payload["id"], payload["status"])
        elif command == "update-candidate":
            output = update_candidate(conn, payload["id"], payload)
        elif command == "delete-candidate":
            output = delete_candidate(conn, payload["id"])
        elif command == "import-knowledge-vault":
            output = import_knowledge_vault(conn, payload)
        elif command == "import-slack":
            output = import_slack(conn, payload)
        elif command == "update-source":
            output = update_source(conn, payload["id"], payload)
        elif command == "update-prompt-template":
            output = update_prompt_template(conn, payload["id"], payload)
        elif command == "update-admin-control":
            output = update_admin_control(conn, payload["group"], payload["id"], payload)
        elif command == "create-tag":
            output = create_tag(conn, payload)
        elif command == "update-tag":
            output = update_tag(conn, payload["id"], payload)
        else:
            raise ValueError(f"unknown command: {command}")
        conn.commit()
    print(json.dumps(output, ensure_ascii=False))


if __name__ == "__main__":
    main()
