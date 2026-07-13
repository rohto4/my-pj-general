import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent


class RedeployP0FrontendTests(unittest.TestCase):
    def test_script_keeps_passwords_out_of_arguments_and_validates_bundles(self):
        script = (ROOT / "redeploy-p0-frontend.ps1").read_text(encoding="utf-8")

        self.assertIn("Get-FileHash", script)
        self.assertIn("scp", script)
        self.assertIn("ssh", script)
        self.assertIn("-tt", script)
        self.assertIn("--rebuild-vikunja", script)
        helper = (ROOT / "redeploy-p0-frontend-remote.sh").read_text(encoding="utf-8")
        self.assertIn("/api/bootstrap", helper)
        self.assertIn("/api/v1/info", helper)
        self.assertNotIn("-Password", script)
        self.assertNotIn("P0_DB_PATH", script)
        self.assertNotIn("docker volume", script.lower())

    def test_script_has_dry_run_and_hash_mismatch_stop(self):
        script = (ROOT / "redeploy-p0-frontend.ps1").read_text(encoding="utf-8")
        helper = (ROOT / "redeploy-p0-frontend-remote.sh").read_text(encoding="utf-8")

        self.assertIn("[switch]$DryRun", script)
        self.assertIn("hash mismatch", helper)
        self.assertIn("ExpectedHubHash", script)
        self.assertIn("ExpectedTasksHash", script)
        self.assertIn('redeploy-p0-frontend-remote.sh', script)
        self.assertIn('pj-general-p0-redeploy-hashes.txt', script)
        self.assertIn('ssh -tt $remote', script)
        self.assertIn('pj-general-p0-redeploy-hashes.txt', helper)
        self.assertIn('HUB_EXPECTED=', helper)
        self.assertIn('TASKS_EXPECTED=', helper)
        self.assertIn('hub bundle hash mismatch', helper)
        self.assertIn('expected hub SHA-256:', helper)
        self.assertIn('actual hub SHA-256:', helper)
        self.assertIn("tr '[:upper:]' '[:lower:]'", helper)
        self.assertIn("tr -d '\\r\\n'", helper)

    def test_script_repackages_current_hub_and_tasks_sources_before_hashing(self):
        script = (ROOT / "redeploy-p0-frontend.ps1").read_text(encoding="utf-8")

        self.assertIn("New-CurrentBundles", script)
        self.assertIn("tar.exe", script)
        self.assertIn("apps/web", script)
        self.assertIn("vikunja-listening-lounge", script)
        self.assertIn("--exclude=frontend/node_modules", script)
        self.assertIn("--exclude=apps/web/test/__pycache__", script)
        self.assertIn("New-CurrentBundles", script[script.index("Require-File"):])

    def test_start_script_waits_for_both_http_services_after_recreate(self):
        start_script = (ROOT / "start-pj-general.sh").read_text(encoding="utf-8")

        self.assertIn("wait_for_services", start_script)
        self.assertIn("for i in $(seq 1 30)", start_script)
        self.assertIn('wait_for_services', start_script[start_script.index('start() {'):])
        self.assertIn('status', start_script[start_script.index('wait_for_services', start_script.index('start() {')):])


if __name__ == "__main__":
    unittest.main()
