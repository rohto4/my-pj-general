import sqlite3
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "infra" / "vikunja" / "backup-and-verify.py"


class BackupRestoreDrillTests(unittest.TestCase):
    def create_db(self, path, schema, rows):
        connection = sqlite3.connect(path)
        try:
            connection.executescript(schema)
            for statement, values in rows:
                connection.execute(statement, values)
            connection.commit()
        finally:
            connection.close()

    def test_both_databases_restore_and_report_counts(self):
        with tempfile.TemporaryDirectory(prefix="pj-general-restore-drill-") as temp:
            base = Path(temp)
            pj_db = base / "pj.sqlite"
            vikunja_db = base / "vikunja.sqlite"
            backup_root = base / "backups"
            self.create_db(
                pj_db,
                "create table candidates(id text); create table execution_links(candidate_id text);",
                [("insert into candidates values (?)", ("C-1",)), ("insert into execution_links values (?)", ("C-1",))],
            )
            self.create_db(
                vikunja_db,
                "create table tasks(id integer, title text);",
                [("insert into tasks values (?, ?)", (77, "restore drill"))],
            )

            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--pj-db",
                    str(pj_db),
                    "--vikunja-db",
                    str(vikunja_db),
                    "--backup-root",
                    str(backup_root),
                ],
                capture_output=True,
                text=True,
                cwd=ROOT,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("pj-general backup=ok restore=ok candidates=1", result.stdout)
            self.assertIn("vikunja backup=ok restore=ok tasks=1", result.stdout)
            self.assertIn("execution_links=1", result.stdout)
            generation = next(backup_root.iterdir())
            self.assertTrue((generation / "pj-general.restore-test.sqlite").exists())
            self.assertTrue((generation / "vikunja.restore-test.sqlite").exists())


if __name__ == "__main__":
    unittest.main()
