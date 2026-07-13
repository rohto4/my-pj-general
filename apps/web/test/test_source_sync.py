import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import db_tool
import source_sync


class SourceSyncDomainTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="pj-general-source-sync-")
        self.root = Path(self.temp.name)
        self.database = self.root / "p0.sqlite"
        self.vault = self.root / "vault"
        (self.vault / "inbox").mkdir(parents=True)
        self.connection = sqlite3.connect(self.database)
        self.connection.row_factory = sqlite3.Row
        db_tool.execute_schema(self.connection)
        db_tool.seed(self.connection)

    def tearDown(self):
        self.connection.close()
        self.temp.cleanup()

    def test_source_sync_domain_is_shared_by_web_wrapper_and_worker(self):
        (self.vault / "inbox" / "idea.md").write_text("# 分離テスト\nやることを確認する", encoding="utf-8")
        payload = {"root": str(self.vault), "targets": ["inbox"], "limit": 30}

        direct = source_sync.import_knowledge_vault(self.connection, payload)
        self.assertEqual(direct["imported"], 1)
        self.assertEqual(direct["syncRun"]["source"], "knowledge_vault")

        # db_tool remains a compatibility boundary for the HTTP handler.
        delegated = db_tool.import_knowledge_vault(self.connection, payload)
        self.assertEqual(delegated["imported"], 0)
        self.assertEqual(delegated["skipped"], 1)

    def test_slack_adapter_uses_same_run_contract(self):
        result = source_sync.import_slack(
            self.connection,
            {"channelName": "memo-ideas", "messages": [{"ts": "1", "text": "source domain"}]},
        )
        self.assertEqual(result["imported"], 1)
        self.assertEqual(result["syncRun"]["source"], "slack")
        self.assertEqual(
            self.connection.execute("select count(*) from source_sync_runs where state = 'succeeded'").fetchone()[0],
            1,
        )

    def test_knowledge_vault_candidate_uses_meaningful_excerpt_summary_and_existing_tags(self):
        for tag in ("knowledge-vault", "inbox", "imported", "gantt", "tasks", "ui"):
            db_tool.create_tag(self.connection, {"name": tag})
        (self.vault / "inbox" / "gantt.md").write_text(
            "# ガント初期表示を直す\n\n"
            "初回遷移で時間軸が崩れるため、ResizeObserverで再計測する。\n"
            "タスクの担当と進捗が読み取れることを確認する。\n",
            encoding="utf-8",
        )

        source_sync.import_knowledge_vault(self.connection, {"root": str(self.vault), "targets": ["inbox"]})
        candidate = db_tool.rows_to_candidates(self.connection)[0]

        self.assertEqual(candidate["excerpt"], "初回遷移で時間軸が崩れるため、ResizeObserverで再計測する。\nタスクの担当と進捗が読み取れることを確認する。")
        self.assertIn("初回遷移で時間軸が崩れる", candidate["summary"])
        self.assertNotIn("取り込んだ確認候補", candidate["summary"])
        self.assertEqual(candidate["todo"], "ガント初期表示を直す")
        self.assertEqual(candidate["tags"], ["gantt", "imported", "inbox", "knowledge-vault", "tasks", "ui"])


if __name__ == "__main__":
    unittest.main()
