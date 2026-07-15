import json
import os
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

WEB_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(WEB_ROOT))

import db_tool
import vault_intake


class VaultIntakePromptTests(unittest.TestCase):
    def test_prompt_is_versioned_and_forbids_common_quality_failures(self):
        prompt = vault_intake.load_prompt()

        self.assertEqual(vault_intake.PROMPT_VERSION, "knowledge-vault-task-proposal-v1")
        for required in (
            "SOURCE_BODYだけを事実根拠",
            "完了事項を再タスク化",
            "固有名詞やpathを雑に翻訳",
            "evidence_quotes",
            "ALLOWED_TAGS",
            "candidateの確定、GO、Vikunja登録はできません",
        ):
            self.assertIn(required, prompt)

    def test_admin_does_not_offer_linux_local_scan_for_windows_vault(self):
        app = (WEB_ROOT / "app.js").read_text(encoding="utf-8")
        db = (WEB_ROOT / "db_tool.py").read_text(encoding="utf-8")

        self.assertNotIn('action: source.id === "knowledge_vault" ? "importKnowledgeVault"', app)
        self.assertIn("windows_ssh_batch", db)
        self.assertIn("infra/intake/import-knowledge-vault.ps1", db)


class VaultIntakeCollectionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="pj-general-vault-intake-")
        self.root = Path(self.temp.name) / "vault"
        (self.root / "records").mkdir(parents=True)
        (self.root / "inbox").mkdir(parents=True)

    def tearDown(self):
        self.temp.cleanup()

    def test_llm_proposal_keeps_lineage_and_never_stores_windows_root(self):
        source = (
            "# 配信修正\n\n"
            "Linux再配信でtarの権限エラーが発生した。\n\n"
            "## Next Actions\n\n"
            "- redeploy-p0-frontend-remote.shで所有者変更を避ける。\n"
        )
        (self.root / "records" / "deploy.md").write_text(source, encoding="utf-8")

        def llm(_request):
            return {
                "document_summary": "Linux再配信時のtar権限エラーと修正作業を記録している。",
                "task_proposals": [{
                    "title": "redeploy-p0-frontend-remote.shの展開処理を修正する",
                    "summary": "Linux再配信のtar権限エラーを避けるため、展開処理を修正する。",
                    "todo": "redeploy-p0-frontend-remote.shで所有者変更を避ける",
                    "kind": "todo",
                    "schedule": "候補なし",
                    "confidence": "high",
                    "missing": [],
                    "tags": ["tasks"],
                    "evidence_quotes": ["redeploy-p0-frontend-remote.shで所有者変更を避ける。"],
                }],
            }

        batch = vault_intake.collect_batch(
            self.root,
            targets=["records"],
            limit=30,
            allowed_tags=["tasks", "review"],
            llm=llm,
            model="local-test",
        )

        self.assertEqual(batch["schema_version"], "threadline.knowledge-vault.batch.v1")
        self.assertEqual(batch["stats"]["documents"], 1)
        document = batch["documents"][0]
        self.assertEqual(document["relative_path"], "records/deploy.md")
        self.assertEqual(document["summary"], "Linux再配信時のtar権限エラーと修正作業を記録している。")
        self.assertEqual(document["proposals"][0]["validation"]["status"], "accepted")
        serialized = json.dumps(batch, ensure_ascii=False)
        self.assertNotIn(str(self.root), serialized)
        self.assertNotIn("G:\\", serialized)

    def test_validator_holds_invented_evidence_unknown_tags_and_generic_title(self):
        output = {
            "document_summary": "入力文書の要約。",
            "task_proposals": [{
                "title": "確認する",
                "summary": "架空の期限を確認する。",
                "todo": "確認する",
                "kind": "todo",
                "schedule": "2026-12-31",
                "confidence": "high",
                "missing": [],
                "tags": ["invented-tag"],
                "evidence_quotes": ["原文に存在しない引用"],
            }],
        }

        normalized = vault_intake.normalize_llm_output(
            output,
            "# 原文\n対象機能はまだ未決定。",
            allowed_tags=["tasks"],
            document_id="KVD-test",
        )

        proposal = normalized["proposals"][0]
        self.assertEqual(proposal["validation"]["status"], "held")
        reasons = " ".join(proposal["validation"]["reasons"])
        self.assertIn("evidence", reasons)
        self.assertIn("tag", reasons)
        self.assertIn("title", reasons)
        self.assertIn("schedule", reasons)

    def test_llm_failure_falls_back_only_to_open_explicit_actions(self):
        (self.root / "inbox" / "memo.md").write_text(
            "# 雑記\n見出しだけではタスクにしない。\n\n"
            "## Next Actions\n"
            "- [x] 完了済みを再登録しない。\n"
            "- Obsidian Local REST APIの疎通を検証する。\n",
            encoding="utf-8",
        )

        def broken_llm(_request):
            raise TimeoutError("provider timeout with secret details")

        batch = vault_intake.collect_batch(
            self.root,
            targets=["inbox"],
            llm=broken_llm,
            model="unverified-local",
        )

        document = batch["documents"][0]
        self.assertEqual(document["ai_run"]["status"], "fallback")
        self.assertEqual(len(document["proposals"]), 1)
        self.assertEqual(document["proposals"][0]["todo"], "Obsidian Local REST APIの疎通を検証する")
        self.assertNotIn("secret details", json.dumps(batch, ensure_ascii=False))

    def test_completed_and_readme_documents_are_excluded(self):
        (self.root / "records" / "README.md").write_text("# index", encoding="utf-8")
        (self.root / "records" / "done.md").write_text(
            "---\nstatus: completed\n---\n# Done\n## Next Actions\n- 再実行する",
            encoding="utf-8",
        )

        batch = vault_intake.collect_batch(self.root, targets=["records"], llm=None)

        self.assertEqual(batch["documents"], [])
        self.assertEqual(batch["stats"]["documents"], 0)

    def test_secret_like_lines_are_redacted_before_llm_and_batch_storage(self):
        (self.root / "records" / "secret.md").write_text(
            "# 接続調査\napi_key: super-secret-value\n"
            '{"token":"json-secret-value"}\n'
            "-----BEGIN OPENSSH PRIVATE KEY-----\nprivate-key-body-value\n-----END OPENSSH PRIVATE KEY-----\n\n"
            "## Next Actions\n- 接続設定の読込境界を検証する。\n",
            encoding="utf-8",
        )
        captured = {}

        def llm(request):
            captured.update(request)
            return {"document_summary": "接続設定の読込境界を検証する記録。", "task_proposals": []}

        batch = vault_intake.collect_batch(self.root, targets=["records"], llm=llm, model="local-test")

        self.assertNotIn("super-secret-value", captured["source_body"])
        self.assertNotIn("json-secret-value", captured["source_body"])
        self.assertNotIn("private-key-body-value", captured["source_body"])
        self.assertIn("[REDACTED_SECRET_LINE]", captured["source_body"])
        self.assertNotIn("super-secret-value", json.dumps(batch, ensure_ascii=False))


class VaultIntakeImportTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="pj-general-vault-import-")
        self.database = Path(self.temp.name) / "p0.sqlite"
        self.connection = sqlite3.connect(self.database)
        self.connection.row_factory = sqlite3.Row
        db_tool.execute_schema(self.connection)
        db_tool.seed(self.connection)

    def tearDown(self):
        self.connection.close()
        self.temp.cleanup()

    def valid_batch(self):
        root = Path(self.temp.name) / "vault"
        (root / "tasks").mkdir(parents=True)
        (root / "tasks" / "active.md").write_text(
            "# Intake\n## Next Actions\n- Vault batch importerの冪等性を検証する。",
            encoding="utf-8",
        )
        return vault_intake.collect_batch(root, targets=["tasks"], llm=None)

    def test_import_persists_lineage_and_creates_one_pending_candidate_idempotently(self):
        batch = self.valid_batch()

        first = vault_intake.import_batch(self.connection, batch, manifest_sha256="a" * 64)
        self.connection.commit()
        second = vault_intake.import_batch(self.connection, batch, manifest_sha256="a" * 64)

        self.assertEqual(first["created"], 1)
        self.assertEqual(first["held"], 0)
        self.assertFalse(first["duplicate"])
        self.assertTrue(second["duplicate"])
        self.assertEqual(self.connection.execute("select count(*) from intake_batches").fetchone()[0], 1)
        self.assertEqual(self.connection.execute("select count(*) from source_documents").fetchone()[0], 1)
        self.assertEqual(self.connection.execute("select count(*) from source_fragments").fetchone()[0], 1)
        self.assertEqual(self.connection.execute("select count(*) from ai_runs").fetchone()[0], 1)
        self.assertEqual(self.connection.execute("select count(*) from candidate_proposals").fetchone()[0], 1)
        candidate = self.connection.execute("select * from candidates").fetchone()
        self.assertEqual(candidate["status"], "pending")
        self.assertEqual(candidate["source_path"], "tasks/active.md")

    def test_unknown_schema_is_rejected_before_any_lineage_write(self):
        batch = self.valid_batch()
        batch["schema_version"] = "unknown.v9"

        with self.assertRaisesRegex(ValueError, "schema_version"):
            vault_intake.import_batch(self.connection, batch)

        self.assertEqual(self.connection.execute("select count(*) from intake_batches").fetchone()[0], 0)
        self.assertEqual(self.connection.execute("select count(*) from candidates").fetchone()[0], 0)

    def test_db_tool_stdin_is_the_linux_import_boundary(self):
        batch = self.valid_batch()
        database = Path(self.temp.name) / "db-tool.sqlite"

        result = subprocess.run(
            [sys.executable, str(WEB_ROOT / "db_tool.py"), "import-vault-batch"],
            input=json.dumps(batch, ensure_ascii=False),
            text=True,
            capture_output=True,
            env={**os.environ, "P0_DB_PATH": str(database), "PYTHONUTF8": "1", "PYTHONIOENCODING": "utf-8"},
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["created"], 1)
        connection = sqlite3.connect(database)
        try:
            self.assertEqual(connection.execute("select count(*) from candidates").fetchone()[0], 1)
            self.assertEqual(connection.execute("select count(*) from candidate_proposals").fetchone()[0], 1)
        finally:
            connection.close()


if __name__ == "__main__":
    unittest.main()
