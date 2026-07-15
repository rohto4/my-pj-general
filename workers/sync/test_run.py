import json
import os
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
WORKER = ROOT / "workers" / "sync" / "run.py"
sys.path.insert(0, str(ROOT / "workers" / "sync"))
import run as sync_run


class SyncWorkerTests(unittest.TestCase):
    def test_external_sources_are_explicit_and_dry_run_by_default(self):
        args = sync_run.parse_args(["--sources", "slack,misskey"])

        self.assertEqual(args.sources, "slack,misskey")
        self.assertFalse(args.commit)

    def test_systemd_timer_is_persistent_and_six_hourly(self):
        timer = (ROOT / "infra" / "systemd" / "pj-general-sync.timer").read_text(encoding="utf-8")
        service = (ROOT / "infra" / "systemd" / "pj-general-sync.service").read_text(encoding="utf-8")
        self.assertIn("OnCalendar=*-*-* 00,06,12,18:00:00", timer)
        self.assertIn("Persistent=true", timer)
        self.assertIn("Type=oneshot", service)
        self.assertIn("--lock-file /run/pj-general-sync/sync.lock", service)
        self.assertIn("--sources slack,misskey", service)
        self.assertNotIn("--commit", service)
        env_example = (ROOT / "infra" / "systemd" / "sync.env.example").read_text(encoding="utf-8")
        self.assertIn("SLACK_BOT_TOKEN=", env_example)
        self.assertIn("MISSKEY_OWNER_USER_ID=", env_example)

    def run_worker(self, database, vault, slack_payload, lock_file):
        result = subprocess.run(
            [
                sys.executable,
                str(WORKER),
                "--db",
                str(database),
                "--knowledge-vault-root",
                str(vault),
                "--slack-payload",
                str(slack_payload),
                "--lock-file",
                str(lock_file),
                "--commit",
            ],
            cwd=ROOT,
            capture_output=True,
            text=True,
            env={**os.environ, "PYTHONUTF8": "1", "PYTHONIOENCODING": "utf-8"},
        )
        payload = json.loads(result.stdout)
        return result, payload

    def test_two_runs_are_idempotent_and_preserve_source_results(self):
        with tempfile.TemporaryDirectory(prefix="pj-general-worker-") as temp:
            base = Path(temp)
            database = base / "p0.sqlite"
            vault = base / "vault"
            (vault / "inbox").mkdir(parents=True)
            (vault / "inbox" / "idea.md").write_text("# Worker test\nやることを確認する", encoding="utf-8")
            slack_payload = base / "slack.json"
            slack_payload.write_text(
                json.dumps({"channelName": "memo-ideas", "messages": [{"ts": "100", "text": "Slack worker test"}]}, ensure_ascii=False),
                encoding="utf-8",
            )
            lock_file = base / "sync.lock"

            first_result, first = self.run_worker(database, vault, slack_payload, lock_file)
            self.assertEqual(first_result.returncode, 0, first_result.stderr)
            self.assertEqual(first["state"], "succeeded")
            self.assertEqual(first["sources"]["knowledge_vault"]["created"], 1)
            self.assertEqual(first["sources"]["slack"]["created"], 1)

            second_result, second = self.run_worker(database, vault, slack_payload, lock_file)
            self.assertEqual(second_result.returncode, 0, second_result.stderr)
            self.assertEqual(second["state"], "succeeded")
            self.assertEqual(second["sources"]["knowledge_vault"]["created"], 0)
            self.assertEqual(second["sources"]["knowledge_vault"]["skipped"], 1)
            self.assertEqual(second["sources"]["slack"]["created"], 0)
            self.assertEqual(second["sources"]["slack"]["skipped"], 1)

            connection = sqlite3.connect(database)
            try:
                self.assertEqual(connection.execute("select count(*) from candidates").fetchone()[0], 2)
                self.assertEqual(connection.execute("select count(*) from source_sync_runs").fetchone()[0], 4)
                self.assertEqual(connection.execute("select count(*) from source_sync_runs where state = 'succeeded'").fetchone()[0], 4)
            finally:
                connection.close()

    def test_lock_is_exclusive(self):
        with tempfile.TemporaryDirectory(prefix="pj-general-worker-lock-") as temp:
            base = Path(temp)
            database = base / "p0.sqlite"
            vault = base / "vault"
            vault.mkdir()
            slack_payload = base / "slack.json"
            slack_payload.write_text(json.dumps({"messages": []}), encoding="utf-8")
            lock_file = base / "sync.lock"
            lock_file.write_text("another-run", encoding="utf-8")

            result, payload = self.run_worker(database, vault, slack_payload, lock_file)
            self.assertEqual(result.returncode, 2)
            self.assertEqual(payload["state"], "locked")

    def test_source_failure_does_not_stop_other_adapters(self):
        with tempfile.TemporaryDirectory(prefix="pj-general-worker-failure-") as temp:
            base = Path(temp)
            database = base / "p0.sqlite"
            vault = base / "vault"
            (vault / "inbox").mkdir(parents=True)
            (vault / "inbox" / "ok.md").write_text("# Keep syncing\nsource failure isolation", encoding="utf-8")
            slack_payload = base / "slack-invalid.json"
            slack_payload.write_text("{invalid", encoding="utf-8")
            lock_file = base / "sync.lock"

            result, payload = self.run_worker(database, vault, slack_payload, lock_file)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(payload["state"], "partial")
            self.assertEqual(payload["sources"]["knowledge_vault"]["state"], "succeeded")
            self.assertEqual(payload["sources"]["slack"]["state"], "failed")

            connection = sqlite3.connect(database)
            try:
                self.assertEqual(connection.execute("select count(*) from candidates").fetchone()[0], 1)
                self.assertEqual(connection.execute("select count(*) from source_sync_runs where source = 'slack' and state = 'failed'").fetchone()[0], 1)
            finally:
                connection.close()


if __name__ == "__main__":
    unittest.main()
