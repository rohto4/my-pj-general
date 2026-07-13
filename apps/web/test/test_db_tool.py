import sys
import unittest
from pathlib import Path


WEB_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(WEB_ROOT))

from db_tool import display_assignee


class GanttAssigneeDisplayTests(unittest.TestCase):
    def test_uses_vikunja_user_name_for_object_assignee(self):
        self.assertEqual(display_assignee([{"username": "unibell4", "name": "Unibell"}]), "unibell4")

    def test_falls_back_for_empty_or_unknown_assignee(self):
        self.assertEqual(display_assignee([]), "未設定")
        self.assertEqual(display_assignee([{}]), "未設定")


if __name__ == "__main__":
    unittest.main()
