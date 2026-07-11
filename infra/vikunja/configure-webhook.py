#!/usr/bin/env python3
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path


def load_env(path):
    values = {}
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key] = value
    return values


def request_json(method, url, token, payload=None):
    body = None if payload is None else json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        url,
        data=body,
        method=method,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=15) as response:
            return json.load(response)
    except urllib.error.HTTPError as error:
        detail = error.read().decode("utf-8", errors="replace")[:1000]
        raise RuntimeError(f"Vikunja API {error.code}: {detail}") from error


def main():
    env_path = os.environ.get(
        "PJ_GENERAL_ENV_FILE",
        str(Path.home() / ".config" / "pj-general" / "pj-general.env"),
    )
    config = load_env(env_path)
    for key in list(config):
        if os.environ.get(key):
            config[key] = os.environ[key]
    required = [
        "VIKUNJA_BASE_URL",
        "VIKUNJA_API_BASE_PATH",
        "VIKUNJA_PROJECT_ID",
        "VIKUNJA_API_TOKEN",
        "VIKUNJA_WEBHOOK_SECRET",
    ]
    missing = [key for key in required if not config.get(key)]
    if missing:
        raise RuntimeError(f"missing settings: {', '.join(missing)}")

    api = config["VIKUNJA_BASE_URL"].rstrip("/") + "/" + config["VIKUNJA_API_BASE_PATH"].strip("/")
    token = config["VIKUNJA_API_TOKEN"]
    project_id = config["VIKUNJA_PROJECT_ID"]
    target_url = config.get(
        "PJ_GENERAL_WEBHOOK_URL",
        "http://pj-general:4173/api/integrations/vikunja/webhook",
    )
    available = request_json("GET", f"{api}/webhooks/events", token)
    desired = [name for name in ("task.created", "task.updated", "task.deleted") if name in available]
    if "task.updated" not in desired:
        raise RuntimeError(f"task.updated is not available; task events={sorted(name for name in available if name.startswith('task.'))}")

    existing = request_json("GET", f"{api}/projects/{project_id}/webhooks?per_page=50", token)
    for webhook in existing:
        if webhook.get("target_url") == target_url:
            print(f"webhook-ready id={webhook['id']} existing=true events={','.join(webhook.get('events') or [])}")
            return 0

    created = request_json(
        "PUT",
        f"{api}/projects/{project_id}/webhooks",
        token,
        {
            "target_url": target_url,
            "events": desired,
            "secret": config["VIKUNJA_WEBHOOK_SECRET"],
        },
    )
    print(f"webhook-ready id={created['id']} existing=false events={','.join(created.get('events') or [])}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as error:
        print(str(error), file=sys.stderr)
        raise SystemExit(1)
