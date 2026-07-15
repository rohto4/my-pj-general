import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


class KnowledgeVaultTransportTests(unittest.TestCase):
    def test_windows_transport_uses_a_real_python_executable_not_the_store_alias(self):
        script = (ROOT / "infra" / "intake" / "import-knowledge-vault.ps1").read_text(encoding="utf-8")

        self.assertIn("Get-Command python.exe -CommandType Application", script)
        self.assertLess(script.index("$bundled ="), script.index("Get-Command python.exe -CommandType Application"))
        self.assertNotIn("Get-Command python -ErrorAction", script)

    def test_windows_transport_allows_a_bounded_llm_timeout_override(self):
        script = (ROOT / "infra" / "intake" / "import-knowledge-vault.ps1").read_text(encoding="utf-8")

        self.assertIn("[int]$LlmTimeout = 60", script)
        self.assertIn("'--llm-timeout', [string]$LlmTimeout", script)

    def test_windows_transport_uses_dedicated_key_hash_and_batch_mode(self):
        script = (ROOT / "infra" / "intake" / "import-knowledge-vault.ps1").read_text(encoding="utf-8")
        self.assertIn("IdentitiesOnly=yes", script)
        self.assertIn("BatchMode=yes", script)
        self.assertIn("Get-FileHash", script)
        self.assertIn("collect-vault-batch", script)
        self.assertNotIn("p0.sqlite", script)

    def test_remote_import_verifies_hash_and_writes_through_db_tool(self):
        script = (ROOT / "infra" / "intake" / "import-knowledge-vault-remote.sh").read_text(encoding="utf-8")
        self.assertIn("sha256sum", script)
        self.assertIn("docker exec -i pj-general python3 /app/db_tool.py import-vault-batch", script)
        self.assertNotIn("docker volume rm", script)
        self.assertNotIn("rm -rf", script)


if __name__ == "__main__":
    unittest.main()
