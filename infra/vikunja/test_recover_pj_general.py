import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


class RecoverPjGeneralTests(unittest.TestCase):
    def test_recovery_script_has_safe_branches_and_no_data_deletion(self):
        script = (ROOT / "infra" / "vikunja" / "recover-pj-general.sh").read_text(encoding="utf-8")

        self.assertIn("--status", script)
        self.assertIn("--redeploy-hub", script)
        self.assertIn("--restart-all", script)
        self.assertIn("--vikunja-image", script)
        self.assertIn("--dry-run", script)
        self.assertIn("com.docker.compose.project.config_files", script)
        self.assertIn("/api/bootstrap", script)
        self.assertIn("docker compose", script)
        self.assertIn("rohto4/vikunja:2.3.0-pj-general-listening-lounge", script)
        self.assertNotIn("docker compose down", script)
        self.assertNotIn("docker volume rm", script)
        self.assertNotIn("docker system prune", script)
        self.assertNotIn("re-import", script.lower())

    def test_unified_start_uses_listening_lounge_by_default(self):
        compose = (ROOT / "infra" / "deploy" / "compose.yaml").read_text(encoding="utf-8")
        script = (ROOT / "infra" / "deploy" / "start-pj-general.sh").read_text(encoding="utf-8")

        self.assertIn("pj-general", compose)
        self.assertIn("vikunja", compose)
        self.assertIn("rohto4/vikunja:2.3.0-pj-general-listening-lounge", compose)
        self.assertIn("VIKUNJA_SERVICE_PUBLICURL", compose)
        self.assertIn("http://${SERVER_LAN_IP:?set SERVER_LAN_IP in .env}:3456/", compose)
        self.assertIn("--dry-run", script)
        self.assertIn("--status", script)
        self.assertIn("--adopt-existing", script)
        self.assertIn("vikunja-listening-lounge-working-tree.tgz", script)
        self.assertIn("docker rm -f", script)
        self.assertNotIn("docker compose down", script)
        self.assertNotIn("docker volume rm", script)


if __name__ == "__main__":
    unittest.main()
