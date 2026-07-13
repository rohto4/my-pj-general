import json
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "workers" / "poc" / "calendar_dry_run.py"


class CalendarDryRunTests(unittest.TestCase):
    def test_approved_schedule_generates_idempotent_proposal_without_external_call(self):
        with tempfile.TemporaryDirectory(prefix="pj-general-calendar-") as temp:
            database = Path(temp) / "p0.sqlite"
            connection = sqlite3.connect(database)
            try:
                connection.execute(
                    "create table candidates(id text, status text, title text, summary text, schedule text)"
                )
                connection.execute(
                    "insert into candidates values (?, ?, ?, ?, ?)",
                    ("C-1", "approved", "週次レビュー", "レビューを行う", "2026-07-15 / 45 min"),
                )
                connection.commit()
            finally:
                connection.close()
            result = subprocess.run(
                [sys.executable, str(SCRIPT), "--db", str(database)],
                cwd=ROOT,
                capture_output=True,
                text=True,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertTrue(payload["dryRun"])
            self.assertEqual(payload["wouldCreate"], 1)
            self.assertEqual(payload["externalCalls"], 0)
            self.assertTrue(payload["proposals"][0]["idempotencyKey"].startswith("gcal-"))


if __name__ == "__main__":
    unittest.main()
