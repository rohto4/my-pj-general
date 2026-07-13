#!/usr/bin/env python3
"""Run the P1 source sync adapters once and exit.

The worker intentionally reuses the Hub's SQLite/domain boundary. It does not
create Vikunja tasks and it isolates source failures so one broken adapter does
not hide successful imports from the other source.
"""

import argparse
import json
import os
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
WEB_ROOT = ROOT / "apps" / "web"
sys.path.insert(0, str(WEB_ROOT))
import db_tool  # noqa: E402
import source_sync  # noqa: E402


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description="Run pj-general source sync once")
    parser.add_argument("--db", default=os.environ.get("P0_DB_PATH", str(WEB_ROOT / "data" / "p0.sqlite")))
    parser.add_argument(
        "--knowledge-vault-root",
        default=os.environ.get("KNOWLEDGE_VAULT_ROOT", "G:/knowledge-vault"),
    )
    parser.add_argument("--targets", default=os.environ.get("SYNC_TARGETS", ""))
    parser.add_argument("--limit", type=int, default=int(os.environ.get("SYNC_LIMIT", "30")))
    parser.add_argument("--slack-payload", default=os.environ.get("SLACK_PAYLOAD_FILE", ""))
    parser.add_argument(
        "--lock-file",
        default=os.environ.get("SYNC_LOCK_FILE", str(Path(os.environ.get("TMPDIR", "/tmp")) / "pj-general-sync.lock")),
    )
    return parser.parse_args(argv)


class SyncLock:
    def __init__(self, path):
        self.path = Path(path)
        self.fd = None

    def acquire(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.fd = os.open(self.path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        os.write(self.fd, f"pid={os.getpid()}\n".encode("ascii"))

    def release(self):
        if self.fd is not None:
            os.close(self.fd)
            self.fd = None
        self.path.unlink(missing_ok=True)

    def __enter__(self):
        self.acquire()
        return self

    def __exit__(self, exc_type, exc, traceback):
        self.release()


def open_database(path):
    db_tool.DB_PATH = Path(path)
    connection = db_tool.connect()
    db_tool.execute_schema(connection)
    db_tool.seed(connection)
    return connection


def latest_cursor(connection, source):
    row = connection.execute(
        "select cursor_after from source_sync_runs where source = ? and state in ('succeeded', 'partial') "
        "and cursor_after is not null order by id desc limit 1",
        (source,),
    ).fetchone()
    return row[0] if row else None


def vault_cursor(root, targets):
    root = Path(root)
    timestamps = []
    for target in targets:
        base = root / target
        if not base.exists():
            continue
        timestamps.extend(path.stat().st_mtime_ns for path in base.rglob("*.md") if path.is_file())
    return str(max(timestamps)) if timestamps else None


def slack_cursor(messages):
    values = [str(message.get("ts") or message.get("time") or "") for message in messages if isinstance(message, dict)]
    return max(values) if values else None


def normalize_run(source, run):
    return {
        "source": source,
        "runId": run.get("run_id"),
        "state": run.get("state", "succeeded"),
        "cursorBefore": run.get("cursor_before"),
        "cursorAfter": run.get("cursor_after"),
        "scanned": int(run.get("scanned", 0) or 0),
        "created": int(run.get("created", 0) or 0),
        "skipped": int(run.get("skipped", 0) or 0),
        "failed": int(run.get("failed", 0) or 0),
    }


def normalize_result(source, result):
    run = result.get("syncRun") or {}
    normalized = normalize_run(source, run)
    normalized["created"] = int(result.get("imported", normalized["created"]) or 0)
    normalized["skipped"] = int(result.get("skipped", normalized["skipped"]) or 0)
    normalized["scanned"] = int(result.get("scanned", normalized["scanned"]) or 0)
    return normalized


def failed_result(connection, source, error, existing_run=None):
    if existing_run is not None:
        normalized = normalize_run(source, existing_run)
        normalized["error"] = existing_run.get("error") or str(error)
        return normalized
    run = db_tool.start_source_sync(connection, {"source": source})
    completed = db_tool.finish_source_sync(
        connection,
        {"run_id": run["run_id"], "state": "failed", "failed": 1, "error": str(error)},
    )
    normalized = normalize_run(source, completed)
    normalized["error"] = completed.get("error")
    return normalized


def run_count(connection, source):
    return connection.execute("select count(*) from source_sync_runs where source = ?", (source,)).fetchone()[0]


def latest_run(connection, source):
    row = connection.execute("select * from source_sync_runs where source = ? order by id desc limit 1", (source,)).fetchone()
    return dict(row) if row else None


def run_once(args):
    targets = [item.strip() for item in args.targets.split(",") if item.strip()]
    if not targets:
        targets = [item["id"] for item in db_tool.ADMIN_CONTROL_DEFAULTS["scopes"] if item.get("enabled")]
    results = {}
    connection = open_database(args.db)
    try:
        try:
            vault_run_count = run_count(connection, "knowledge_vault")
            vault_payload = {
                "root": args.knowledge_vault_root,
                "targets": targets,
                "limit": args.limit,
                "cursor": latest_cursor(connection, "knowledge_vault"),
                "cursor_after": vault_cursor(args.knowledge_vault_root, targets),
            }
            results["knowledge_vault"] = normalize_result(
                "knowledge_vault", source_sync.import_knowledge_vault(connection, vault_payload)
            )
        except Exception as error:  # isolate source failure
            existing_run = latest_run(connection, "knowledge_vault") if run_count(connection, "knowledge_vault") > vault_run_count else None
            results["knowledge_vault"] = failed_result(connection, "knowledge_vault", error, existing_run)

        if args.slack_payload:
            try:
                slack_run_count = run_count(connection, "slack")
                payload = json.loads(Path(args.slack_payload).read_text(encoding="utf-8"))
                payload["cursor"] = latest_cursor(connection, "slack")
                payload["cursor_after"] = slack_cursor(payload.get("messages") or [])
                results["slack"] = normalize_result("slack", source_sync.import_slack(connection, payload))
            except Exception as error:  # isolate source failure
                existing_run = latest_run(connection, "slack") if run_count(connection, "slack") > slack_run_count else None
                results["slack"] = failed_result(connection, "slack", error, existing_run)

        connection.commit()
    finally:
        connection.close()
    states = [item["state"] for item in results.values()]
    if not states:
        return {"state": "succeeded", "sources": {}}
    if all(state == "succeeded" for state in states):
        state = "succeeded"
    elif all(state == "failed" for state in states):
        state = "failed"
    else:
        state = "partial"
    return {"state": state, "sources": results}


def main(argv=None):
    args = parse_args(argv)
    try:
        with SyncLock(args.lock_file):
            output = run_once(args)
    except FileExistsError:
        output = {"state": "locked", "lockFile": str(Path(args.lock_file))}
        print(json.dumps(output, ensure_ascii=False))
        return 2
    except Exception as error:
        output = {"state": "failed", "error": str(error)}
        print(json.dumps(output, ensure_ascii=False))
        return 1
    print(json.dumps(output, ensure_ascii=False))
    return 0 if output["state"] in {"succeeded", "partial"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
