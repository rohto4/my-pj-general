import json
import os
import re
import sqlite3
import sys
import hashlib
import uuid
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parent
DB_PATH = Path(os.environ.get("P0_DB_PATH", ROOT / "data" / "p0.sqlite"))
BACKUP_DIR = Path(os.environ.get("P0_BACKUP_DIR", ROOT.parent.parent / "tmp" / "backup" / "hub"))


DATE_PATTERN = re.compile(r"(?<!\d)(\d{4}-\d{2}-\d{2})(?!\d)")
OPERATION_ID_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]{2,95}$")


def connect():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def now():
    return datetime.now().isoformat(timespec="seconds")


def decision_operation_id(note):
    if not note or not note.startswith("operation:"):
        return None
    operation_id = note.split(" ", 1)[0].removeprefix("operation:")
    return operation_id if OPERATION_ID_PATTERN.fullmatch(operation_id) else None


def decision_note(operation_id, summary):
    if operation_id is None:
        return summary
    if not OPERATION_ID_PATTERN.fullmatch(str(operation_id)):
        raise ValueError("operation_id must be 3-96 characters of letters, numbers, _ or -")
    return f"operation:{operation_id} {summary}"


def insert_decision(conn, candidate_id, action, summary, operation_id=None, timestamp=None):
    created_at = timestamp or now()
    cursor = conn.execute(
        "insert into decisions(candidate_id, action, note, created_at) values (?, ?, ?, ?)",
        (candidate_id, action, decision_note(operation_id, summary), created_at),
    )
    return {
        "id": cursor.lastrowid,
        "candidateId": candidate_id,
        "action": action,
        "operationId": operation_id,
        "createdAt": created_at,
    }


def extract_date(value):
    if not value:
        return None
    match = DATE_PATTERN.search(str(value))
    if not match:
        return None
    try:
        datetime.strptime(match.group(1), "%Y-%m-%d")
    except ValueError:
        return None
    return match.group(1)


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
        create table if not exists execution_links (
          candidate_id text primary key,
          provider text not null,
          external_project_id text not null,
          external_task_id text not null unique,
          external_url text not null,
          sync_state text not null default 'not_requested',
          last_synced_at text,
          created_at text not null,
          updated_at text not null
        );
        create table if not exists execution_task_state (
          candidate_id text primary key,
          title text not null,
          done integer not null default 0,
          due_date text,
          priority integer,
          assignees_json text not null default '[]',
          percent_done integer,
          external_updated_at text,
          mirrored_at text not null
        );
        create table if not exists sync_events (
          id integer primary key autoincrement,
          dedupe_key text not null unique,
          external_event_id text,
          provider text not null,
          event_type text not null,
          payload_hash text not null,
          payload_json text not null,
          received_at text not null,
          processed_at text,
          processing_state text not null default 'received',
          error text
        );
        create table if not exists sync_attempts (
          id integer primary key autoincrement,
          candidate_id text,
          provider text not null,
          direction text not null,
          operation text not null,
          idempotency_key text not null unique,
          state text not null,
          error text,
          attempted_at text not null
        );
        create table if not exists source_sync_runs (
          id integer primary key autoincrement,
          run_id text not null unique,
          source text not null,
          state text not null,
          started_at text not null,
          finished_at text,
          cursor_before text,
          cursor_after text,
          scanned integer not null default 0,
          created integer not null default 0,
          skipped integer not null default 0,
          failed integer not null default 0,
          error text
        );
        create table if not exists intake_batches (
          batch_id text primary key,
          schema_version text not null,
          source_type text not null,
          source_root_label text not null,
          created_at text not null,
          imported_at text not null,
          manifest_sha256 text,
          prompt_version text not null,
          model_json text not null,
          state text not null,
          stats_json text not null
        );
        create table if not exists source_documents (
          document_id text primary key,
          source_type text not null,
          source_ref text not null,
          scope text not null,
          content_hash text not null,
          modified_at text,
          collected_at text not null,
          summary text not null,
          metadata_json text not null,
          unique(source_type, source_ref, content_hash)
        );
        create table if not exists source_fragments (
          fragment_id text primary key,
          document_id text not null,
          heading text not null,
          line_start integer,
          line_end integer,
          excerpt text not null,
          content_hash text not null,
          extraction_method text not null
        );
        create table if not exists ai_runs (
          run_id text primary key,
          batch_id text not null,
          document_id text not null,
          provider text not null,
          model text not null,
          prompt_version text not null,
          input_hash text not null,
          output_hash text not null,
          status text not null,
          error text,
          created_at text not null
        );
        create table if not exists candidate_proposals (
          proposal_id text primary key,
          batch_id text not null,
          document_id text not null,
          status text not null,
          title text not null,
          summary text not null,
          todo text not null,
          kind text not null,
          schedule text not null,
          confidence text not null,
          missing_json text not null,
          tags_json text not null,
          evidence_json text not null,
          validation_json text not null,
          candidate_id text,
          created_at text not null,
          updated_at text not null
        );
        create table if not exists chat_threads (
          id text primary key,
          title text not null,
          provider text not null,
          model text not null,
          status text not null default 'active',
          created_at text not null,
          updated_at text not null
        );
        create table if not exists chat_messages (
          id integer primary key autoincrement,
          thread_id text not null,
          role text not null,
          content text not null,
          metadata_json text not null default '{}',
          created_at text not null
        );
        create table if not exists chat_task_suggestions (
          id text primary key,
          thread_id text not null,
          message_id integer not null,
          title text not null,
          summary text not null,
          todo text not null,
          kind text not null,
          schedule text not null,
          confidence text not null,
          missing_json text not null default '[]',
          status text not null default 'proposed',
          candidate_id text,
          created_at text not null,
          updated_at text not null
        );
        """
    )


def schema_info(conn):
    tables = [
        row["name"]
        for row in conn.execute(
            "select name from sqlite_master where type = 'table' order by name"
        ).fetchall()
    ]
    unique_indexes = {}
    for table in tables:
        columns = []
        for index in conn.execute(f'pragma index_list("{table}")').fetchall():
            if not index["unique"]:
                continue
            columns.extend(
                row["name"]
                for row in conn.execute(
                    f'pragma index_info("{index["name"]}")'
                ).fetchall()
            )
        unique_indexes[table] = columns
    return {"tables": tables, "uniqueIndexes": unique_indexes}


HEALTH_COUNT_TABLES = (
    "sources",
    "candidates",
    "decisions",
    "execution_links",
    "execution_task_state",
    "sync_events",
    "sync_attempts",
    "source_sync_runs",
    "intake_batches",
    "source_documents",
    "source_fragments",
    "ai_runs",
    "candidate_proposals",
    "chat_threads",
    "chat_messages",
    "chat_task_suggestions",
)


def database_health(conn):
    return database_health_for_path(conn, DB_PATH)


def file_sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def backup_database(conn):
    conn.commit()
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S-%f")
    destination = BACKUP_DIR / f"p0-{stamp}.sqlite"
    with sqlite3.connect(destination) as backup_conn:
        conn.backup(backup_conn)
    with sqlite3.connect(f"file:{destination.as_posix()}?mode=ro", uri=True) as verify_conn:
        verify_conn.row_factory = sqlite3.Row
        verification = database_health_for_path(verify_conn, destination)
    if verification["integrity"] != "ok":
        destination.unlink(missing_ok=True)
        raise ValueError("backup integrity check failed")
    return {
        "path": str(destination.resolve()),
        "createdAt": now(),
        "sizeBytes": destination.stat().st_size,
        "sha256": file_sha256(destination),
        "integrity": verification["integrity"],
        "counts": verification["counts"],
    }


def database_health_for_path(conn, path):
    integrity_rows = conn.execute("pragma quick_check").fetchall()
    integrity = "ok" if len(integrity_rows) == 1 and integrity_rows[0][0] == "ok" else "failed"
    tables = {
        row[0]
        for row in conn.execute("select name from sqlite_master where type = 'table'").fetchall()
    }
    counts = {
        table: conn.execute(f'select count(*) from "{table}"').fetchone()[0]
        for table in HEALTH_COUNT_TABLES
        if table in tables
    }
    return {
        "status": "ok" if integrity == "ok" else "error",
        "integrity": integrity,
        "counts": counts,
        "sizeBytes": path.stat().st_size if path.exists() else 0,
    }


def source_sync_run(conn, run_id):
    row = conn.execute("select * from source_sync_runs where run_id = ?", (run_id,)).fetchone()
    if row is None:
        raise ValueError(f"source sync run not found: {run_id}")
    return dict(row)


def start_source_sync(conn, payload):
    source = str(payload.get("source") or "unknown")[:120]
    timestamp = now()
    run_id = f"{source}:{uuid.uuid4().hex}"
    conn.execute(
        """
        insert into source_sync_runs(
          run_id, source, state, started_at, cursor_before
        ) values (?, ?, 'running', ?, ?)
        """,
        (run_id, source, timestamp, payload.get("cursor_before")),
    )
    return source_sync_run(conn, run_id)


def finish_source_sync(conn, payload):
    run_id = str(payload.get("run_id") or "")
    if not run_id:
        raise ValueError("source sync run_id is required")
    state = str(payload.get("state") or "succeeded")
    if state not in {"succeeded", "failed", "partial"}:
        raise ValueError(f"invalid source sync state: {state}")
    row = source_sync_run(conn, run_id)
    conn.execute(
        """
        update source_sync_runs
        set state = ?, finished_at = ?, cursor_after = ?, scanned = ?, created = ?,
            skipped = ?, failed = ?, error = ?
        where run_id = ?
        """,
        (
            state,
            now(),
            payload.get("cursor_after"),
            max(int(payload.get("scanned") or 0), 0),
            max(int(payload.get("created") or 0), 0),
            max(int(payload.get("skipped") or 0), 0),
            max(int(payload.get("failed") or 0), 0),
            str(payload.get("error") or "")[:1000] or None,
            run_id,
        ),
    )
    return source_sync_run(conn, run_id)


def list_source_sync_runs(conn, limit=30):
    rows = conn.execute(
        "select * from source_sync_runs order by id desc limit ?",
        (max(min(int(limit), 100), 1),),
    ).fetchall()
    return [dict(row) for row in rows]


def latest_backup_observability(limit=10):
    if not BACKUP_DIR.exists():
        return []
    result = []
    for path in sorted(BACKUP_DIR.glob("p0-*.sqlite"), key=lambda item: item.stat().st_mtime, reverse=True)[:limit]:
        try:
            with sqlite3.connect(str(path)) as verify_conn:
                verify_conn.row_factory = sqlite3.Row
                verification = database_health_for_path(verify_conn, path)
            result.append(
                {
                    "name": path.name,
                    "createdAt": datetime.fromtimestamp(path.stat().st_mtime).isoformat(timespec="seconds"),
                    "sizeBytes": path.stat().st_size,
                    "sha256": file_sha256(path),
                    "integrity": verification["integrity"],
                    "counts": verification["counts"],
                }
            )
        except (OSError, sqlite3.Error):
            result.append({"name": path.name, "integrity": "unavailable"})
    return result


def observability(conn):
    runs = list_source_sync_runs(conn)
    latest_by_source = {}
    for run in runs:
        latest_by_source.setdefault(run["source"], run)
    return {
        "sourceSyncRuns": runs,
        "latestBySource": latest_by_source,
        "latestBackups": latest_backup_observability(),
        "operations": operational_metrics(conn),
    }


def count_by(conn, column, table="candidates"):
    allowed = {"status", "source_id", "kind", "confidence", "action"}
    if column not in allowed:
        raise ValueError(f"unsupported metrics column: {column}")
    rows = conn.execute(f'select "{column}", count(*) as total from "{table}" group by "{column}"').fetchall()
    return {str(row[0] or "unknown"): row[1] for row in rows}


def operational_metrics(conn):
    candidate_counts = count_by(conn, "status")
    candidate_counts["total"] = conn.execute("select count(*) from candidates").fetchone()[0]
    source_counts = count_by(conn, "source_id")
    kind_counts = count_by(conn, "kind")
    confidence_counts = count_by(conn, "confidence")
    decision_counts = count_by(conn, "action", "decisions")
    missing_count = 0
    for row in conn.execute("select missing_json from candidates").fetchall():
        try:
            missing_count += 1 if json.loads(row[0] or "[]") else 0
        except json.JSONDecodeError:
            missing_count += 1
    linked = conn.execute("select count(*) from execution_links").fetchone()[0]
    completed = conn.execute("select count(*) from execution_task_state where done = 1").fetchone()[0]
    approved = decision_counts.get("approved", 0)
    decision_total = sum(decision_counts.values())
    return {
        "candidateCounts": candidate_counts,
        "sourceCounts": source_counts,
        "kindCounts": kind_counts,
        "confidenceCounts": confidence_counts,
        "missingCandidates": missing_count,
        "decisionCounts": decision_counts,
        "goRate": round(approved / decision_total * 100, 2) if decision_total else None,
        "executionCounts": {"linked": linked, "completed": completed},
    }


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
        ("chat", "AI相談", "chat://local-llm", 1, "local_agent"),
    ]
    conn.executemany("insert or ignore into sources(id, label, path, enabled, source_kind) values (?, ?, ?, ?, ?)", sources)
    conn.execute(
        "update sources set label = ?, path = ?, source_kind = ? where id = ?",
        ("Misskey (未接続)", "misskey://not-connected", "connector", "misskey"),
    )
    conn.execute(
        "update sources set label = ?, path = ?, source_kind = ? where id = ?",
        (
            "knowledge-vault AI batch",
            "infra/intake/import-knowledge-vault.ps1",
            "windows_ssh_batch",
            "knowledge_vault",
        ),
    )
    static_gantt_marker = conn.execute("select 1 from settings where key = ?", ("migration.remove-static-gantt.v1",)).fetchone()
    if static_gantt_marker is None:
        conn.execute("delete from gantt_tasks where id in ('GT-001', 'GT-002', 'GT-003', 'GT-004')")
        ensure_setting(conn, "migration.remove-static-gantt.v1", {"appliedAt": now()})
    ensure_setting(conn, "automation.mode", {"label": "P0確認方針", "value": "all_pending_first"})
    ensure_setting(conn, "slack.memo_ideas", {"channel": "C0BG4TCPAUD", "mode": "connector_payload_import"})
    load_admin_controls(conn)
    templates = [
        ("codex-start", "Codex起動支援", "candidate", "AGENTS.md と PROJECT.md を読み、選択候補を実装タスクとして開始する。", 1),
        ("candidate-triage", "候補整理", "intake", "入口データを TODO / 検討 / 気になる事 / 予定候補に分類する。", 1),
        ("go-promotion", "GO後作成", "decision", "GOした候補をタスク、予定候補、判断記録へ展開する。", 1),
    ]
    conn.executemany("insert or ignore into prompt_templates(id, name, target, body, enabled) values (?, ?, ?, ?, ?)", templates)
    candidate_prompt_marker = conn.execute("select 1 from settings where key = ?", ("migration.candidate-triage.v2",)).fetchone()
    if candidate_prompt_marker is None:
        conn.execute(
            "update prompt_templates set body = ? where id = ?",
            (
                "knowledge-vaultから未完了の次アクションだけを候補化する。README、完了記録、単なる見出しは除外する。原文の行動を保ち、対象・成果・次アクションが分かる一文にする。固有名詞や英語識別子は無理に翻訳せず、定型の『〜を確認する』を付与しない。候補は確認待ちとし、自動GOしない。",
                "candidate-triage",
            ),
        )
        ensure_setting(conn, "migration.candidate-triage.v2", {"appliedAt": now()})
    candidate_prompt_v3 = conn.execute("select 1 from settings where key = ?", ("migration.candidate-triage.v3",)).fetchone()
    if candidate_prompt_v3 is None:
        conn.execute(
            "update prompt_templates set body = ? where id = ?",
            (
                "knowledge-vault / Slack / Misskey / AI相談の本人本文から、明示actionはTODO、まだ曖昧な『やりたいこと』はaspirationとして原文根拠付きで候補化する。aspirationを架空の具体作業へ変換せず、全件を確認待ちにして自動GOしない。runtime正本はthreadline-candidate-proposal-v2。",
                "candidate-triage",
            ),
        )
        ensure_setting(conn, "migration.candidate-triage.v3", {"appliedAt": now()})
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


def display_assignee(assignees):
    if not isinstance(assignees, list) or not assignees:
        return "未設定"
    first = assignees[0]
    if isinstance(first, dict):
        for key in ("username", "name", "email"):
            value = first.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()
        return "未設定"
    if isinstance(first, str) and first.strip():
        return first.strip()
    return "未設定"


def gantt_rows(conn):
    rows = conn.execute(
        """
        select
          c.id as candidate_id,
          c.title,
          c.todo,
          c.kind,
          c.source_label,
          c.schedule,
          c.missing_json,
          ets.done,
          ets.due_date,
          ets.percent_done,
          ets.assignees_json
        from candidates c
        left join execution_task_state ets on ets.candidate_id = c.id
        where c.status not in ('rejected', 'archived')
        order by c.updated_at desc, c.id asc
        """
    ).fetchall()
    result = []
    for row in rows:
        schedule_date = extract_date(row["schedule"])
        due_date = extract_date(row["due_date"])
        start_date = schedule_date or due_date
        end_date = due_date or schedule_date
        if not start_date:
            continue
        if end_date < start_date:
            end_date = start_date
        try:
            missing = json.loads(row["missing_json"] or "[]")
        except json.JSONDecodeError:
            missing = []
        try:
            assignees = json.loads(row["assignees_json"] or "[]") if row["assignees_json"] else []
        except json.JSONDecodeError:
            assignees = []
        progress = 100 if row["done"] else int(row["percent_done"] or 0)
        result.append(
            {
                "id": row["candidate_id"],
                "candidateId": row["candidate_id"],
                "title": row["todo"] or row["title"],
                "owner": display_assignee(assignees),
                "progress": max(0, min(progress, 100)),
                "state": "done" if row["done"] else "active",
                "dependency": " / ".join(str(item) for item in missing) if missing else "なし",
                "source": row["source_label"],
                "schedule": row["schedule"],
                "startDate": start_date,
                "endDate": end_date,
            }
        )
    return result


def bootstrap(conn):
    candidates = rows_to_candidates(conn)
    log = [
        {
            "id": row["id"],
            "action": row["action"],
            "title": row["todo"] or row["title"],
            "time": row["created_at"],
            "operationId": decision_operation_id(row["note"]),
        }
        for row in conn.execute(
            """
            select d.id, d.action, d.note, c.title, c.todo, d.created_at
            from decisions d join candidates c on c.id = d.candidate_id
            order by d.id desc limit 20
            """
        ).fetchall()
    ]
    sources = [dict(row) for row in conn.execute("select * from sources order by id").fetchall()]
    tags = [dict(row) for row in conn.execute("select * from tags order by name").fetchall()]
    gantt = gantt_rows(conn)
    templates = [dict(row) for row in conn.execute("select * from prompt_templates order by id").fetchall()]
    execution_links = [dict(row) for row in conn.execute("select * from execution_links order by created_at").fetchall()]
    execution_task_states = [dict(row) for row in conn.execute("select * from execution_task_state order by candidate_id").fetchall()]
    sync_events = [
        dict(row)
        for row in conn.execute(
            "select id, dedupe_key, external_event_id, provider, event_type, received_at, processed_at, processing_state, error from sync_events order by id"
        ).fetchall()
    ]
    return {
        "candidates": candidates,
        "log": log,
        "sources": sources,
        "tags": tags,
        "ganttTasks": gantt,
        "promptTemplates": templates,
        "adminControls": load_admin_controls(conn),
        "executionLinks": execution_links,
        "executionTaskStates": execution_task_states,
        "syncEvents": sync_events,
        "dbPath": str(DB_PATH),
    }


def ensure_chat_thread(conn, thread_id=None):
    thread_id = thread_id or "chat-default"
    row = conn.execute("select * from chat_threads where id = ?", (thread_id,)).fetchone()
    if row is None:
        timestamp = now()
        conn.execute(
            "insert into chat_threads(id, title, provider, model, created_at, updated_at) values (?, ?, ?, ?, ?, ?)",
            (thread_id, "AI相談", "openai-compatible", os.environ.get("LOCAL_LLM_MODEL", "gemma4:latest"), timestamp, timestamp),
        )
        row = conn.execute("select * from chat_threads where id = ?", (thread_id,)).fetchone()
    return dict(row)


def chat_messages(conn, thread_id, limit=40):
    rows = conn.execute(
        "select id, thread_id, role, content, metadata_json, created_at from chat_messages where thread_id = ? order by id desc limit ?",
        (thread_id, limit),
    ).fetchall()
    result = []
    for row in reversed(rows):
        item = dict(row)
        item["metadata"] = json.loads(item.pop("metadata_json") or "{}")
        result.append(item)
    return result


def chat_suggestions(conn, thread_id):
    rows = conn.execute(
        "select * from chat_task_suggestions where thread_id = ? order by created_at desc",
        (thread_id,),
    ).fetchall()
    result = []
    for row in rows:
        item = dict(row)
        item["missing"] = json.loads(item.pop("missing_json") or "[]")
        result.append(item)
    return result


def chat_bootstrap(conn, payload):
    thread = ensure_chat_thread(conn, payload.get("thread_id"))
    return {
        "thread": thread,
        "messages": chat_messages(conn, thread["id"]),
        "suggestions": chat_suggestions(conn, thread["id"]),
    }


def save_chat_message(conn, payload):
    thread = ensure_chat_thread(conn, payload.get("thread_id"))
    role = payload.get("role") or "user"
    if role not in {"user", "assistant", "system", "tool"}:
        raise ValueError("unsupported chat role")
    content = str(payload.get("content") or "").strip()
    if not content:
        raise ValueError("chat message is empty")
    timestamp = now()
    cursor = conn.execute(
        "insert into chat_messages(thread_id, role, content, metadata_json, created_at) values (?, ?, ?, ?, ?)",
        (thread["id"], role, content, json.dumps(payload.get("metadata") or {}, ensure_ascii=False), timestamp),
    )
    conn.execute("update chat_threads set updated_at = ? where id = ?", (timestamp, thread["id"]))
    row = conn.execute(
        "select id, thread_id, role, content, metadata_json, created_at from chat_messages where id = ?",
        (cursor.lastrowid,),
    ).fetchone()
    item = dict(row)
    item["metadata"] = json.loads(item.pop("metadata_json") or "{}")
    return item


def create_chat_suggestions(conn, payload):
    thread = ensure_chat_thread(conn, payload.get("thread_id"))
    message_id = int(payload["message_id"])
    result = []
    for suggestion in payload.get("suggestions") or []:
        suggestion_id = f"chat-suggestion-{uuid.uuid4().hex}"
        timestamp = now()
        conn.execute(
            """
            insert into chat_task_suggestions(
              id, thread_id, message_id, title, summary, todo, kind, schedule,
              confidence, missing_json, status, created_at, updated_at
            ) values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'proposed', ?, ?)
            """,
            (
                suggestion_id,
                thread["id"],
                message_id,
                suggestion.get("title") or "無題のタスク候補",
                suggestion.get("summary") or suggestion.get("title") or "",
                suggestion.get("todo") or suggestion.get("title") or "",
                suggestion.get("kind") or "todo",
                suggestion.get("schedule") or "候補なし",
                suggestion.get("confidence") or "medium",
                json.dumps(suggestion.get("missing") or [], ensure_ascii=False),
                timestamp,
                timestamp,
            ),
        )
        row = conn.execute("select * from chat_task_suggestions where id = ?", (suggestion_id,)).fetchone()
        item = dict(row)
        item["missing"] = json.loads(item.pop("missing_json") or "[]")
        result.append(item)
    return result


def chat_context(conn):
    candidates = conn.execute(
        """
        select id, title, status, kind, source_label, confidence, missing_json, schedule
        from candidates
        where status not in ('rejected', 'archived')
        order by updated_at desc
        limit 20
        """
    ).fetchall()
    candidate_items = []
    for row in candidates:
        item = dict(row)
        item["missing"] = json.loads(item.pop("missing_json") or "[]")
        candidate_items.append(item)
    execution = [
        dict(row)
        for row in conn.execute(
            "select candidate_id, title, done, due_date, percent_done, assignees_json from execution_task_state order by mirrored_at desc limit 20"
        ).fetchall()
    ]
    return {
        "hub": {
            "candidate_count": conn.execute("select count(*) from candidates").fetchone()[0],
            "pending_count": conn.execute("select count(*) from candidates where status = 'pending'").fetchone()[0],
            "candidates": candidate_items,
        },
        "execution_state": execution,
    }


def accept_chat_suggestion(conn, suggestion_id):
    suggestion = conn.execute("select * from chat_task_suggestions where id = ?", (suggestion_id,)).fetchone()
    if suggestion is None:
        raise ValueError(f"chat suggestion not found: {suggestion_id}")
    if suggestion["candidate_id"]:
        candidate = conn.execute("select * from candidates where id = ?", (suggestion["candidate_id"],)).fetchone()
        return {"suggestion": dict(suggestion), "candidate": dict(candidate) if candidate else None}
    item = create_candidate(
        conn,
        {
            "title": suggestion["title"],
            "body": suggestion["summary"],
            "summary": suggestion["summary"],
            "todo": suggestion["todo"],
            "schedule": suggestion["schedule"],
            "kind": suggestion["kind"],
            "source": "chat",
            "sourceLabel": "AI相談",
            "sourcePath": f"chat://thread/{suggestion['thread_id']}",
            "tags": ["chat", "ai-suggested"],
            "confidence": suggestion["confidence"],
            "missing": json.loads(suggestion["missing_json"] or "[]"),
        },
    )
    timestamp = now()
    conn.execute(
        "update chat_task_suggestions set status = 'candidate_pending', candidate_id = ?, updated_at = ? where id = ?",
        (item["id"], timestamp, suggestion_id),
    )
    return {
        "suggestion": dict(conn.execute("select * from chat_task_suggestions where id = ?", (suggestion_id,)).fetchone()),
        "candidate": item,
    }


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
    title = payload.get("title") or "Untitled intake"
    body = payload.get("body") or payload.get("summary") or title
    item = {
        "id": next_candidate_id(conn),
        "status": "pending",
        "title": title,
        "kind": payload.get("kind") or "idea",
        "source": payload.get("source") or "web",
        "sourceLabel": payload.get("sourceLabel") or "manual",
        "sourcePath": payload.get("sourcePath") or payload.get("url") or "web://manual",
        "tags": payload.get("tags") or ["manual"],
        "confidence": payload.get("confidence") or "medium",
        "missing": payload.get("missing") or (["schedule decision"] if payload.get("schedule") == "none" else []),
        "occurred": datetime.now().strftime("%Y-%m-%d"),
        "excerpt": payload.get("excerpt") or body,
        "summary": payload.get("summary") or body[:140],
        "todo": payload.get("todo") or f"{title} を整理する",
        "schedule": payload.get("schedule") or "候補なし",
        "preview": payload.get("preview") or f"{payload.get('kind') or 'idea'}: {title}",
    }
    insert_candidate(conn, item)
    conn.execute("insert into decisions(candidate_id, action, note, created_at) values (?, ?, ?, ?)", (item["id"], "created", "manual intake", now()))
    return item


def update_status(conn, candidate_id, status, operation_id=None):
    row = conn.execute("select id from candidates where id = ?", (candidate_id,)).fetchone()
    if not row:
        raise ValueError(f"candidate not found: {candidate_id}")
    conn.execute("update candidates set status = ?, updated_at = ? where id = ?", (status, now(), candidate_id))
    decision = insert_decision(conn, candidate_id, status, "queue action", operation_id)
    return {"id": candidate_id, "status": status, "decision": decision}


def prepare_execution(conn, candidate_id, operation_id=None):
    candidate = conn.execute("select * from candidates where id = ?", (candidate_id,)).fetchone()
    if candidate is None:
        raise ValueError(f"candidate not found: {candidate_id}")
    existing = conn.execute("select * from execution_links where candidate_id = ?", (candidate_id,)).fetchone()
    if existing is not None:
        return {"existing": True, "link": dict(existing), "operation_id": operation_id}

    timestamp = now()
    if candidate["status"] != "approved":
        conn.execute("update candidates set status = 'approved', updated_at = ? where id = ?", (timestamp, candidate_id))
        decision = insert_decision(conn, candidate_id, "approved", "Vikunja execution requested", operation_id, timestamp)
    else:
        decision = None
    attempt_key = f"vikunja:{candidate_id}:create:{datetime.now().isoformat(timespec='microseconds')}"
    cursor = conn.execute(
        """
        insert into sync_attempts(candidate_id, provider, direction, operation, idempotency_key, state, attempted_at)
        values (?, 'vikunja', 'outbound', 'create_task', ?, 'pending', ?)
        """,
        (candidate_id, attempt_key, timestamp),
    )
    return {"existing": False, "attempt_id": cursor.lastrowid, "candidate": dict(candidate), "decision": decision, "operation_id": operation_id}


def complete_execution(conn, payload):
    candidate_id = payload["candidate_id"]
    task = payload["task"]
    timestamp = now()
    external_task_id = str(task["id"])
    conn.execute(
        """
        insert into execution_links(
          candidate_id, provider, external_project_id, external_task_id, external_url,
          sync_state, last_synced_at, created_at, updated_at
        ) values (?, 'vikunja', ?, ?, ?, 'synced', ?, ?, ?)
        on conflict(candidate_id) do update set
          external_task_id=excluded.external_task_id,
          external_url=excluded.external_url,
          sync_state='synced',
          last_synced_at=excluded.last_synced_at,
          updated_at=excluded.updated_at
        """,
        (
            candidate_id,
            str(payload["project_id"]),
            external_task_id,
            payload["external_url"],
            timestamp,
            timestamp,
            timestamp,
        ),
    )
    conn.execute(
        """
        insert into execution_task_state(
          candidate_id, title, done, due_date, priority, assignees_json,
          percent_done, external_updated_at, mirrored_at
        ) values (?, ?, ?, ?, ?, ?, ?, ?, ?)
        on conflict(candidate_id) do update set
          title=excluded.title, done=excluded.done, due_date=excluded.due_date,
          priority=excluded.priority, assignees_json=excluded.assignees_json,
          percent_done=excluded.percent_done, external_updated_at=excluded.external_updated_at,
          mirrored_at=excluded.mirrored_at
        """,
        (
            candidate_id,
            task.get("title", ""),
            1 if task.get("done") else 0,
            task.get("due_date"),
            task.get("priority"),
            json.dumps(task.get("assignees") or [], ensure_ascii=False),
            task.get("percent_done"),
            task.get("updated"),
            timestamp,
        ),
    )
    conn.execute("update sync_attempts set state = 'succeeded', error = null where id = ?", (payload["attempt_id"],))
    result = dict(conn.execute("select * from execution_links where candidate_id = ?", (candidate_id,)).fetchone())
    if payload.get("operation_id"):
        result["operation_id"] = payload["operation_id"]
    return result


def fail_execution(conn, payload):
    conn.execute(
        "update sync_attempts set state = 'failed', error = ? where id = ?",
        (str(payload.get("error", "external API failed"))[:1000], payload["attempt_id"]),
    )
    return {"candidate_id": payload["candidate_id"], "sync_state": "failed"}


def list_execution_links(conn):
    return [dict(row) for row in conn.execute("select * from execution_links order by candidate_id").fetchall()]


def record_reconcile_result(conn, payload):
    candidate_id = payload["candidate_id"]
    result = payload["result"]
    timestamp = now()
    attempt_key = f"vikunja:{candidate_id}:reconcile:{datetime.now().isoformat(timespec='microseconds')}"
    state = "succeeded" if result in ("updated", "detached") else "failed"
    conn.execute(
        """
        insert into sync_attempts(candidate_id, provider, direction, operation, idempotency_key, state, error, attempted_at)
        values (?, 'vikunja', 'inbound', 'reconcile_task', ?, ?, ?, ?)
        """,
        (candidate_id, attempt_key, state, payload.get("error"), timestamp),
    )
    if result == "detached":
        conn.execute(
            "update execution_links set sync_state = 'detached', updated_at = ? where candidate_id = ?",
            (timestamp, candidate_id),
        )
    elif result == "updated":
        link = conn.execute("select * from execution_links where candidate_id = ?", (candidate_id,)).fetchone()
        complete_execution(
            conn,
            {
                "candidate_id": candidate_id,
                "project_id": link["external_project_id"],
                "external_url": link["external_url"],
                "attempt_id": None,
                "task": payload["task"],
            },
        )
    return {"candidate_id": candidate_id, "result": result}


def process_vikunja_webhook(conn, payload):
    raw_body = payload["raw_body"]
    event = json.loads(raw_body)
    payload_hash = hashlib.sha256(raw_body.encode("utf-8")).hexdigest()
    external_event_id = payload.get("external_event_id")
    dedupe_key = f"vikunja:event:{external_event_id}" if external_event_id else f"vikunja:payload:{payload_hash}"
    timestamp = now()
    cursor = conn.execute(
        """
        insert or ignore into sync_events(
          dedupe_key, external_event_id, provider, event_type, payload_hash,
          payload_json, received_at, processing_state
        ) values (?, ?, 'vikunja', ?, ?, ?, ?, 'received')
        """,
        (dedupe_key, external_event_id, event.get("event_name", "unknown"), payload_hash, raw_body, timestamp),
    )
    if cursor.rowcount == 0:
        return {"duplicate": True, "dedupe_key": dedupe_key}

    task = (event.get("data") or {}).get("task") or {}
    task_id = str(task.get("id", ""))
    link = conn.execute("select * from execution_links where external_task_id = ?", (task_id,)).fetchone()
    if link is None:
        conn.execute(
            "update sync_events set processed_at = ?, processing_state = 'orphan' where dedupe_key = ?",
            (timestamp, dedupe_key),
        )
        return {"duplicate": False, "orphan": True, "dedupe_key": dedupe_key}

    complete_execution(
        conn,
        {
            "candidate_id": link["candidate_id"],
            "project_id": link["external_project_id"],
            "external_url": link["external_url"],
            "attempt_id": None,
            "task": task,
        },
    )
    conn.execute(
        "update sync_events set processed_at = ?, processing_state = 'processed' where dedupe_key = ?",
        (timestamp, dedupe_key),
    )
    return {"duplicate": False, "orphan": False, "dedupe_key": dedupe_key}


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
    decision = insert_decision(conn, candidate_id, fields["status"], "edited candidate", payload.get("operation_id"))
    result = next(item for item in rows_to_candidates(conn) if item["id"] == candidate_id)
    result["decision"] = decision
    return result


def delete_candidate(conn, candidate_id):
    conn.execute("delete from candidate_tags where candidate_id = ?", (candidate_id,))
    conn.execute("delete from decisions where candidate_id = ?", (candidate_id,))
    conn.execute("delete from candidates where id = ?", (candidate_id,))
    return {"id": candidate_id, "deleted": True}


def reset_operational_data(conn):
    """Clear the derived queue and every audit row that refers to it.

    Configuration, tags, prompt templates, and chat history are intentionally
    retained: they are not execution history for the rebuilt vault queue.
    """
    tables = [
        "candidate_proposals",
        "ai_runs",
        "source_fragments",
        "source_documents",
        "intake_batches",
        "candidate_tags",
        "decisions",
        "execution_task_state",
        "execution_links",
        "sync_attempts",
        "sync_events",
        "source_sync_runs",
        "candidates",
    ]
    counts = {table: conn.execute(f"select count(*) from {table}").fetchone()[0] for table in tables}
    for table in tables:
        conn.execute(f"delete from {table}")
    conn.execute("update sources set last_imported_at = null")
    return {
        "candidates": counts["candidates"],
        "decisions": counts["decisions"],
        "execution_links": counts["execution_links"],
        "execution_task_state": counts["execution_task_state"],
        "sync_attempts": counts["sync_attempts"],
        "sync_events": counts["sync_events"],
        "source_sync_runs": counts["source_sync_runs"],
        "intake_batches": counts["intake_batches"],
        "source_documents": counts["source_documents"],
        "source_fragments": counts["source_fragments"],
        "ai_runs": counts["ai_runs"],
        "candidate_proposals": counts["candidate_proposals"],
    }


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
    from source_sync import import_knowledge_vault as import_domain

    return import_domain(conn, payload)


def import_vault_batch(conn, payload):
    from vault_intake import import_batch

    manifest_sha256 = payload.pop("_manifest_sha256", None) if isinstance(payload, dict) else None
    return import_batch(conn, payload, manifest_sha256=manifest_sha256)


def import_slack(conn, payload):
    from source_sync import import_slack as import_domain

    return import_domain(conn, payload)


def candidate_proposal_config(conn):
    from candidate_proposal import PROMPT_VERSION

    return {
        "promptVersion": PROMPT_VERSION,
        "allowedTags": [
            row["name"]
            for row in conn.execute("select name from tags where visible = 1 order by name").fetchall()
        ],
        "sources": {
            row["id"]: bool(row["enabled"])
            for row in conn.execute("select id, enabled from sources order by id").fetchall()
        },
    }


def normalize_source_proposals(payload):
    from candidate_proposal import normalize_output

    return normalize_output(
        payload.get("output") or {},
        str(payload.get("sourceBody") or ""),
        allowed_tags=payload.get("allowedTags") or [],
        source_kind=str(payload.get("source") or ""),
        source_ref=str(payload.get("sourceRef") or ""),
    )


def import_source_proposals(conn, payload):
    from source_sync import import_source_proposals as import_domain

    return import_domain(conn, payload)


def update_source(conn, source_id, payload):
    enabled = 1 if payload.get("enabled") else 0
    conn.execute("update sources set enabled = ? where id = ?", (enabled, source_id))
    return dict(conn.execute("select * from sources where id = ?", (source_id,)).fetchone())


def update_prompt_template(conn, template_id, payload):
    existing = conn.execute("select * from prompt_templates where id = ?", (template_id,)).fetchone()
    if existing is None:
        raise ValueError(f"prompt template not found: {template_id}")
    enabled = 1 if payload.get("enabled", bool(existing["enabled"])) else 0
    body = payload.get("body", existing["body"])
    if not isinstance(body, str) or not body.strip():
        raise ValueError("prompt template body is required")
    if len(body) > 4000:
        raise ValueError("prompt template body must be 4000 characters or fewer")
    conn.execute("update prompt_templates set enabled = ?, body = ? where id = ?", (enabled, body.strip(), template_id))
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
        elif command == "chat-bootstrap":
            output = chat_bootstrap(conn, payload)
        elif command == "chat-context":
            output = chat_context(conn)
        elif command == "chat-save-message":
            output = save_chat_message(conn, payload)
        elif command == "chat-create-suggestions":
            output = create_chat_suggestions(conn, payload)
        elif command == "chat-accept-suggestion":
            output = accept_chat_suggestion(conn, payload["id"])
        elif command == "create-candidate":
            output = create_candidate(conn, payload)
        elif command == "update-status":
            output = update_status(conn, payload["id"], payload["status"], payload.get("operation_id"))
        elif command == "prepare-execution":
            output = prepare_execution(conn, payload["id"], payload.get("operation_id"))
        elif command == "complete-execution":
            output = complete_execution(conn, payload)
        elif command == "fail-execution":
            output = fail_execution(conn, payload)
        elif command == "list-execution-links":
            output = list_execution_links(conn)
        elif command == "record-reconcile-result":
            output = record_reconcile_result(conn, payload)
        elif command == "start-source-sync":
            output = start_source_sync(conn, payload)
        elif command == "finish-source-sync":
            output = finish_source_sync(conn, payload)
        elif command == "observability":
            output = observability(conn)
        elif command == "process-vikunja-webhook":
            output = process_vikunja_webhook(conn, payload)
        elif command == "update-candidate":
            output = update_candidate(conn, payload["id"], payload)
        elif command == "delete-candidate":
            output = delete_candidate(conn, payload["id"])
        elif command == "reset-operational-data":
            output = reset_operational_data(conn)
        elif command == "import-knowledge-vault":
            output = import_knowledge_vault(conn, payload)
        elif command == "import-vault-batch":
            output = import_vault_batch(conn, payload)
        elif command == "import-slack":
            output = import_slack(conn, payload)
        elif command == "candidate-proposal-config":
            output = candidate_proposal_config(conn)
        elif command == "normalize-source-proposals":
            output = normalize_source_proposals(payload)
        elif command == "import-source-proposals":
            output = import_source_proposals(conn, payload)
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
        elif command == "schema-info":
            output = schema_info(conn)
        elif command == "database-health":
            output = database_health(conn)
        elif command == "backup-database":
            output = backup_database(conn)
        else:
            raise ValueError(f"unknown command: {command}")
        conn.commit()
    print(json.dumps(output, ensure_ascii=False))


if __name__ == "__main__":
    main()
