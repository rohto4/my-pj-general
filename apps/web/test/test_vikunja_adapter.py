import hashlib
import hmac
import json
import unittest

from vikunja_adapter import (
    build_create_task_request,
    make_webhook_dedupe_key,
    verify_webhook_signature,
)


class VikunjaAdapterTest(unittest.TestCase):
    def test_stable_create_task_contract(self):
        request = build_create_task_request(
            base_url="http://vikunja:3456/",
            api_base_path="/api/v1",
            project_id="42",
            candidate={
                "id": "KV-001",
                "title": "設計を確認する",
                "summary": "安定版契約を確認する",
                "todo": "Vikunja実機で確認する",
            },
        )
        self.assertEqual(request["method"], "PUT")
        self.assertEqual(request["url"], "http://vikunja:3456/api/v1/projects/42/tasks")
        self.assertEqual(request["body"]["title"], "設計を確認する")
        self.assertIn("candidate: KV-001", request["body"]["description"])

    def test_webhook_signature_uses_raw_body(self):
        raw_body = b'{"event_name":"task.updated","data":{"task":{"id":1}}}'
        secret = "test-only-secret"
        signature = hmac.new(secret.encode(), raw_body, hashlib.sha256).hexdigest()
        self.assertTrue(verify_webhook_signature(raw_body, signature, secret))
        self.assertFalse(verify_webhook_signature(raw_body + b" ", signature, secret))

    def test_dedupe_key_prefers_external_id_and_falls_back_to_payload_hash(self):
        raw_body = json.dumps({"event_name": "task.updated", "data": {"task": {"id": 1}}}).encode()
        self.assertEqual(make_webhook_dedupe_key(raw_body, "evt-1"), "vikunja:event:evt-1")
        self.assertEqual(
            make_webhook_dedupe_key(raw_body),
            f"vikunja:payload:{hashlib.sha256(raw_body).hexdigest()}",
        )


if __name__ == "__main__":
    unittest.main()
