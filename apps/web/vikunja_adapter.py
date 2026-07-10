import hashlib
import hmac


def build_create_task_request(base_url, api_base_path, project_id, candidate):
    base = base_url.rstrip("/")
    api = "/" + api_base_path.strip("/")
    description_parts = [
        candidate.get("summary", "").strip(),
        candidate.get("todo", "").strip(),
        f"candidate: {candidate['id']}",
    ]
    return {
        "method": "PUT",
        "url": f"{base}{api}/projects/{project_id}/tasks",
        "body": {
            "title": candidate["title"].strip(),
            "description": "\n\n".join(part for part in description_parts if part),
        },
    }


def verify_webhook_signature(raw_body, signature, secret):
    if not signature or not secret:
        return False
    expected = hmac.new(secret.encode("utf-8"), raw_body, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature)


def make_webhook_dedupe_key(raw_body, external_event_id=None):
    if external_event_id:
        return f"vikunja:event:{external_event_id}"
    payload_hash = hashlib.sha256(raw_body).hexdigest()
    return f"vikunja:payload:{payload_hash}"
