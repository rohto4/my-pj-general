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

    def test_common_ai_intake_creates_action_and_aspiration_as_pending_candidates(self):
        payload = {
            "source": "slack",
            "sourceLabel": "memo-ideas",
            "allowedTags": [],
            "items": [
                {
                    "sourceRef": "slack://memo-ideas/1",
                    "sourceBody": "監査APIの同期結果を確認し、失敗runを再実行する。",
                    "output": {
                        "document_summary": "監査APIの再実行が必要。",
                        "candidate_proposals": [{
                            "proposal_type": "action",
                            "title": "監査APIの失敗runを再実行する",
                            "summary": "同期結果を確認して失敗runを再実行する。",
                            "todo": "監査APIの同期結果を確認し、失敗runを再実行する",
                            "kind": "todo",
                            "schedule": "候補なし",
                            "confidence": "high",
                            "missing": [],
                            "tags": [],
                            "evidence_quotes": ["監査APIの同期結果を確認し、失敗runを再実行する。"],
                        }],
                    },
                },
                {
                    "sourceRef": "slack://memo-ideas/2",
                    "sourceBody": "なんとなく、いつか自宅の本を横断検索できるようにしたい。",
                    "output": {
                        "document_summary": "自宅の本を横断検索したいという希望。",
                        "candidate_proposals": [{
                            "proposal_type": "aspiration",
                            "title": "自宅の本を横断検索したい",
                            "summary": "自宅の本を横断検索できるようにしたい。",
                            "todo": "なんとなく、いつか自宅の本を横断検索できるようにしたい。",
                            "kind": "idea",
                            "schedule": "候補なし",
                            "confidence": "medium",
                            "missing": [],
                            "tags": [],
                            "evidence_quotes": ["なんとなく、いつか自宅の本を横断検索できるようにしたい。"],
                        }],
                    },
                },
            ],
        }

        result = source_sync.import_source_proposals(self.connection, payload)
        candidates = db_tool.rows_to_candidates(self.connection)

        self.assertEqual(result["imported"], 2)
        self.assertEqual(result["held"], 0)
        self.assertEqual(result["syncRun"]["source"], "slack")
        self.assertEqual({item["kind"] for item in candidates}, {"todo", "idea"})
        self.assertTrue(all(item["status"] == "pending" for item in candidates))
        self.assertEqual(self.connection.execute("select count(*) from execution_links").fetchone()[0], 0)

    def test_common_ai_intake_holds_invented_misskey_aspiration_and_is_idempotent(self):
        wish = "ローカルLLMで写真を整理できたらいいな。"
        payload = {
            "source": "misskey",
            "sourceLabel": "Misskey",
            "allowedTags": [],
            "items": [{
                "sourceRef": "misskey://note/1",
                "sourceBody": wish,
                "output": {
                    "document_summary": "写真整理への希望。",
                    "candidate_proposals": [{
                        "proposal_type": "aspiration",
                        "title": "写真整理を自動化したい",
                        "summary": "ローカルLLMで写真を整理したい。",
                        "todo": "今週中にPythonで写真分類workerを実装する",
                        "kind": "idea",
                        "schedule": "候補なし",
                        "confidence": "high",
                        "missing": [],
                        "tags": [],
                        "evidence_quotes": [wish],
                    }],
                },
            }],
        }

        first = source_sync.import_source_proposals(self.connection, payload)
        self.assertEqual(first["imported"], 0)
        self.assertEqual(first["held"], 1)
        self.assertEqual(self.connection.execute("select count(*) from candidates").fetchone()[0], 0)

        payload["items"][0]["output"]["candidate_proposals"][0]["todo"] = wish
        second = source_sync.import_source_proposals(self.connection, payload)
        third = source_sync.import_source_proposals(self.connection, payload)
        self.assertEqual(second["imported"], 1)
        self.assertEqual(third["imported"], 0)
        self.assertEqual(third["skipped"], 1)
        candidate = db_tool.rows_to_candidates(self.connection)[0]
        self.assertEqual(candidate["source"], "misskey")
        self.assertEqual(candidate["kind"], "idea")

    def test_knowledge_vault_candidate_uses_meaningful_excerpt_summary_and_existing_tags(self):
        for tag in ("knowledge-vault", "inbox", "imported", "gantt", "tasks", "ui"):
            db_tool.create_tag(self.connection, {"name": tag})
        (self.vault / "inbox" / "gantt.md").write_text(
            "# ガント初期表示を直す\n\n"
            "初回遷移で時間軸が崩れるため、ResizeObserverで再計測する。\n"
            "タスクの担当と進捗が読み取れることを確認する。\n\n"
            "## Next Actions\n\n"
            "- ガント初期表示を直す\n",
            encoding="utf-8",
        )

        source_sync.import_knowledge_vault(self.connection, {"root": str(self.vault), "targets": ["inbox"]})
        candidate = db_tool.rows_to_candidates(self.connection)[0]

        self.assertEqual(candidate["excerpt"], "ガント初期表示を直す")
        self.assertIn("ガント初期表示を直す", candidate["summary"])
        self.assertNotIn("取り込んだ確認候補", candidate["summary"])
        self.assertEqual(candidate["todo"], "ガント初期表示を直す")
        self.assertEqual(candidate["tags"], ["gantt", "imported", "inbox", "knowledge-vault", "tasks", "ui"])

    def test_knowledge_vault_extracts_only_open_next_actions_without_heading_translation(self):
        (self.vault / "tasks").mkdir(parents=True)
        (self.vault / "tasks" / "active.md").write_text(
            "---\nstatus: active\n---\n\n# Vault Bootstrap\n\n"
            "## Next Actions\n\n"
            "1. Obsidianで Local REST API plugin を有効化し、疎通確認する。\n"
            "2. records/ に移行要約を作る。\n",
            encoding="utf-8",
        )
        (self.vault / "tasks" / "completed.md").write_text(
            "---\nstatus: completed\n---\n\n# 完了済み\n\n## Next Actions\n\n- 再実行しない。\n",
            encoding="utf-8",
        )
        (self.vault / "tasks" / "README.md").write_text("# Tasks\n", encoding="utf-8")

        result = source_sync.import_knowledge_vault(self.connection, {"root": str(self.vault), "targets": ["tasks"]})
        candidates = db_tool.rows_to_candidates(self.connection)

        self.assertEqual(result["imported"], 2)
        self.assertEqual(result["skipped"], 2)
        self.assertEqual(sorted(item["title"] for item in candidates), sorted([
            "Obsidianで Local REST API plugin を有効化し、疎通確認する",
            "records/ に移行要約を作る",
        ]))
        self.assertEqual(sorted(item["todo"] for item in candidates), sorted([
            "Obsidianで Local REST API plugin を有効化し、疎通確認する",
            "records/ に移行要約を作る",
        ]))


if __name__ == "__main__":
    unittest.main()
