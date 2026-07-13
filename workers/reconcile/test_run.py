import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


class ReconcileWorkerTests(unittest.TestCase):
    def test_worker_calls_reconcile_endpoint_and_has_timeout(self):
        script = (ROOT / "workers" / "reconcile" / "run.py").read_text(encoding="utf-8")
        self.assertIn("/api/integrations/vikunja/reconcile", script)
        self.assertIn("urlopen", script)
        self.assertIn("timeout", script)

    def test_systemd_reconcile_timer_is_persistent(self):
        timer = (ROOT / "infra" / "systemd" / "pj-general-reconcile.timer").read_text(encoding="utf-8")
        service = (ROOT / "infra" / "systemd" / "pj-general-reconcile.service").read_text(encoding="utf-8")
        self.assertIn("Persistent=true", timer)
        self.assertIn("OnCalendar=*:0/15", timer)
        self.assertIn("Type=oneshot", service)


if __name__ == "__main__":
    unittest.main()
