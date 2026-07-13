import json
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "workers" / "poc" / "dry_run.py"


class PocDryRunTests(unittest.TestCase):
    def create_db(self, path):
        connection = sqlite3.connect(path)
        try:
            connection.executescript(
                """
                create table candidates(
                  id text primary key, status text, title text, kind text,
                  confidence text, missing_json text, source_id text
                );
                """
            )
            connection.executemany(
                "insert into candidates values (?, ?, ?, ?, ?, ?, ?)",
                [
                    ("C-1", "pending", "週次レビューの準備", "todo", "medium", "[\"owner confirm\"]", "web"),
                    ("C-2", "pending", "週次レビューの準備を進める", "todo", "medium", "[\"owner confirm\"]", "slack"),
                    ("C-3", "pending", "単独のアイデア", "consideration", "high", "[]", "web"),
                ],
            )
            connection.commit()
        finally:
            connection.close()

    def run_worker(self, database, mode):
        result = subprocess.run(
            [sys.executable, str(SCRIPT), "--db", str(database), "--mode", mode],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        return json.loads(result.stdout)

    def test_similarity_only_proposes_pairs_without_writing(self):
        with tempfile.TemporaryDirectory(prefix="pj-general-poc-") as temp:
            database = Path(temp) / "p0.sqlite"
            self.create_db(database)
            before = database.read_bytes()
            output = self.run_worker(database, "similarity")
            self.assertTrue(output["dryRun"])
            self.assertEqual(output["mode"], "similarity")
            self.assertEqual(output["pairs"][0]["left"], "C-1")
            self.assertEqual(output["pairs"][0]["right"], "C-2")
            self.assertEqual(database.read_bytes(), before)

    def test_partial_auto_confirm_reports_eligible_without_mutating(self):
        with tempfile.TemporaryDirectory(prefix="pj-general-auto-confirm-") as temp:
            database = Path(temp) / "p0.sqlite"
            self.create_db(database)
            output = self.run_worker(database, "partial-auto-confirm")
            self.assertTrue(output["dryRun"])
            self.assertEqual(output["wouldUpdate"], 1)
            self.assertEqual(output["eligible"][0]["id"], "C-3")
            self.assertEqual(output["eligible"][0]["action"], "would-approve")


if __name__ == "__main__":
    unittest.main()
