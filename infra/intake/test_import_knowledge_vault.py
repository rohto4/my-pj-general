import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


class KnowledgeVaultTransportTests(unittest.TestCase):
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
