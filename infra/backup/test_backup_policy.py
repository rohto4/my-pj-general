import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


class BackupPolicyTests(unittest.TestCase):
    def test_rotation_script_keeps_generations_and_mirrors_verified_artifacts(self):
        script = (ROOT / "infra" / "backup" / "rotate-and-mirror.sh").read_text(encoding="utf-8")
        self.assertIn("KEEP_GENERATIONS", script)
        self.assertIn("MIRROR_ROOT", script)
        self.assertIn("sha256sum", script)
        self.assertIn("vikunja-files.tar.gz", script)
        self.assertIn("manifest.sha256", script)
        self.assertIn("rm -rf --", script)
        self.assertIn("P0_BACKUP_DIR", script)
        self.assertIn("p0-", script)

    def test_systemd_backup_is_daily_and_persistent(self):
        timer = (ROOT / "infra" / "systemd" / "pj-general-backup.timer").read_text(encoding="utf-8")
        service = (ROOT / "infra" / "systemd" / "pj-general-backup.service").read_text(encoding="utf-8")
        env = (ROOT / "infra" / "systemd" / "backup.env.example").read_text(encoding="utf-8")
        self.assertIn("OnCalendar=*-*-* 03:30:00", timer)
        self.assertIn("Persistent=true", timer)
        self.assertIn("Type=oneshot", service)
        self.assertIn("rotate-and-mirror.sh", service)
        self.assertIn("KEEP_GENERATIONS=7", env)
        self.assertIn("P0_BACKUP_DIR", env)


if __name__ == "__main__":
    unittest.main()
