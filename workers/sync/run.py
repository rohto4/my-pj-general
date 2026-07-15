#!/usr/bin/env python3
"""Run legacy snapshot imports or explicit external-source collection once.

External Slack/Misskey collection is dry-run by default.  ``--commit`` is the
only switch that can create pending candidates or advance a source cursor.
"""

import argparse
import json
import os
import sqlite3
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
WEB_ROOT = ROOT / "apps" / "web"
sys.path.insert(0, str(WEB_ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import db_tool  # noqa: E402
import source_sync  # noqa: E402
from http_client import HttpClient  # noqa: E402
from llm_client import CandidateProposalLlm  # noqa: E402
from misskey_collector import MisskeyCollector  # noqa: E402
from proposal_pipeline import ProposalPipeline  # noqa: E402
from slack_collector import SlackCollector  # noqa: E402


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description="Run pj-general source sync once")
    parser.add_argument("--db", default=os.environ.get("P0_DB_PATH", str(WEB_ROOT / "data" / "p0.sqlite")))
    parser.add_argument("--sources", default=os.environ.get("SYNC_SOURCES", ""), help="comma-separated: slack,misskey")
    parser.add_argument("--commit", action="store_true", help="persist candidates and source cursors")
    # Legacy snapshot-only inputs remain available for regression compatibility.
    parser.add_argument("--knowledge-vault-root", default=os.environ.get("KNOWLEDGE_VAULT_ROOT", "G:/knowledge-vault"))
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


def open_readonly_database(path):
    database = Path(path).resolve()
    if not database.exists():
        raise RuntimeError("database_unavailable")
    connection = sqlite3.connect(f"{database.as_uri()}?mode=ro", uri=True)
    connection.row_factory = sqlite3.Row
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
        if base.exists():
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


def failed_result(connection, source, cursor_before=None):
    run = db_tool.start_source_sync(connection, {"source": source, "cursor_before": cursor_before})
    completed = db_tool.finish_source_sync(
        connection,
        {"run_id": run["run_id"], "state": "failed", "failed": 1, "error": "source_error"},
    )
    normalized = normalize_run(source, completed)
    normalized["error"] = "source_error"
    return normalized


def legacy_run(connection, args):
    targets = [item.strip() for item in args.targets.split(",") if item.strip()]
    if not targets:
        targets = [item["id"] for item in db_tool.ADMIN_CONTROL_DEFAULTS["scopes"] if item.get("enabled")]
    results = {}
    try:
        payload = {
            "root": args.knowledge_vault_root,
            "targets": targets,
            "limit": args.limit,
            "cursor": latest_cursor(connection, "knowledge_vault"),
            "cursor_after": vault_cursor(args.knowledge_vault_root, targets),
        }
        results["knowledge_vault"] = normalize_result("knowledge_vault", source_sync.import_knowledge_vault(connection, payload))
    except Exception:
        results["knowledge_vault"] = failed_result(connection, "knowledge_vault")
    if args.slack_payload:
        try:
            payload = json.loads(Path(args.slack_payload).read_text(encoding="utf-8"))
            payload["cursor"] = latest_cursor(connection, "slack")
            payload["cursor_after"] = slack_cursor(payload.get("messages") or [])
            results["slack"] = normalize_result("slack", source_sync.import_slack(connection, payload))
        except Exception:
            results["slack"] = failed_result(connection, "slack")
    return results


def external_collector(source, http):
    if source == "slack":
        channel_id = os.environ.get("SLACK_CHANNEL_ID", "")
        owner_id = os.environ.get("SLACK_OWNER_USER_ID", "")
        token = os.environ.get("SLACK_BOT_TOKEN", "")
        if not (channel_id and owner_id and token):
            raise RuntimeError("slack_config")
        return SlackCollector(
            http,
            channel_id=channel_id,
            owner_user_id=owner_id,
            bot_token=token,
            initial_oldest_ts=os.environ.get("SLACK_INITIAL_OLDEST_TS", ""),
            api_base_url=os.environ.get("SLACK_API_BASE_URL", "https://slack.com/api"),
        ), "memo-ideas"
    if source == "misskey":
        base_url = os.environ.get("MISSKEY_BASE_URL", "")
        owner_id = os.environ.get("MISSKEY_OWNER_USER_ID", "")
        if not (base_url and owner_id):
            raise RuntimeError("misskey_config")
        return MisskeyCollector(http, base_url, owner_id, os.environ.get("MISSKEY_ACCESS_TOKEN", "")), "Misskey"
    raise RuntimeError("unsupported_source")


def external_run(connection, args, source):
    cursor_before = latest_cursor(connection, source)
    try:
        timeout_seconds = max(int(os.environ.get("LOCAL_LLM_TIMEOUT_MS", "60000")) / 1000, 5)
        http = HttpClient(timeout_seconds=timeout_seconds)
        collector, source_label = external_collector(source, http)
        collected = collector.collect(cursor_before)
        pipeline = ProposalPipeline(CandidateProposalLlm(http))
        result = pipeline.process(connection, source, source_label, collected, cursor_before, commit=args.commit)
        return {"source": source, **result}
    except Exception:
        if args.commit:
            return failed_result(connection, source, cursor_before)
        return {
            "source": source,
            "state": "failed",
            "cursorBefore": cursor_before,
            "cursorAfter": cursor_before,
            "scanned": 0,
            "created": 0,
            "skipped": 0,
            "failed": 1,
            "error": "source_error",
        }


def overall_state(results):
    states = [item["state"] for item in results.values()]
    if not states or all(state == "succeeded" for state in states):
        return "succeeded"
    if all(state == "failed" for state in states):
        return "failed"
    return "partial"


def run_once(args):
    selected = [item.strip() for item in args.sources.split(",") if item.strip()]
    if any(item not in {"slack", "misskey"} for item in selected):
        raise RuntimeError("unsupported_source")
    if not args.commit and not selected:
        return {"state": "succeeded", "mode": "dry-run", "sources": {}}
    connection = open_database(args.db) if args.commit else open_readonly_database(args.db)
    try:
        results = {source: external_run(connection, args, source) for source in selected} if selected else legacy_run(connection, args)
        if args.commit:
            connection.commit()
    finally:
        connection.close()
    return {"state": overall_state(results), "mode": "commit" if args.commit else "dry-run", "sources": results}


def main(argv=None):
    args = parse_args(argv)
    try:
        with SyncLock(args.lock_file):
            output = run_once(args)
    except FileExistsError:
        output = {"state": "locked", "lockFile": str(Path(args.lock_file))}
        print(json.dumps(output, ensure_ascii=False))
        return 2
    except Exception:
        output = {"state": "failed", "error": "worker_error"}
        print(json.dumps(output, ensure_ascii=False))
        return 1
    print(json.dumps(output, ensure_ascii=False))
    return 0 if output["state"] in {"succeeded", "partial"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
