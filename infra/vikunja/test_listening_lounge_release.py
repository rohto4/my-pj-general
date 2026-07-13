import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


class ListeningLoungeReleaseTests(unittest.TestCase):
    def test_build_script_pins_release_and_image_tag(self):
        script = (ROOT / "infra" / "vikunja" / "build-listening-lounge.sh").read_text(encoding="utf-8")
        self.assertIn("RELEASE_VERSION", script)
        self.assertIn("VIKUNJA_SOURCE_DIR", script)
        self.assertIn("docker build", script)
        self.assertIn("rohto4/vikunja:2.3.0-pj-general-listening-lounge", script)

    def test_switch_script_only_changes_image_reference(self):
        script = (ROOT / "infra" / "vikunja" / "switch-image.sh").read_text(encoding="utf-8")
        self.assertIn("VIKUNJA_IMAGE", script)
        self.assertIn("--force-recreate", script)
        self.assertIn("vikunja/vikunja:2.3.0", script)
        self.assertNotIn("docker volume rm", script)
        self.assertNotIn("rm -rf", script)


if __name__ == "__main__":
    unittest.main()
