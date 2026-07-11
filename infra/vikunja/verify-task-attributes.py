#!/usr/bin/env python3
import json
import os
import urllib.error
import urllib.request
from pathlib import Path


def load_env(path):
    values = {}
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        if line and not line.startswith("#") and "=" in line:
            key, value = line.split("=", 1)
            values[key] = value
    return values


def request_json(method, url, token, payload=None):
    request = urllib.request.Request(
        url,
        data=None if payload is None else json.dumps(payload).encode("utf-8"),
        method=method,
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
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
    base_url = os.environ.get("VIKUNJA_BASE_URL", config["VIKUNJA_BASE_URL"]).rstrip("/")
    api = base_url + "/" + config["VIKUNJA_API_BASE_PATH"].strip("/")
    token = config["VIKUNJA_API_TOKEN"]
    task_id = os.environ.get("VIKUNJA_TEST_TASK_ID", "1")
    user_id = int(os.environ.get("VIKUNJA_TEST_USER_ID", "1"))

    task = request_json("GET", f"{api}/tasks/{task_id}", token)
    mutable_fields = (
        "title",
        "description",
        "done",
        "due_date",
        "priority",
        "start_date",
        "end_date",
        "repeat_after",
        "repeat_mode",
        "percent_done",
        "hex_color",
        "is_favorite",
    )
    update = {key: task.get(key) for key in mutable_fields}
    update.update(
        {
            "description": (
                "knowledge-vault/memory/l1-triggers.md から取り込んだ確認候補。\n\n"
                "L1 Triggers を確認する\n\n"
                "candidate: KV-e378384856"
            ),
            "done": True,
            "priority": 3,
            "due_date": "2026-07-20T12:00:00Z",
        }
    )
    request_json("POST", f"{api}/tasks/{task_id}", token, update)
    task = request_json("GET", f"{api}/tasks/{task_id}", token)
    if not any(assignee.get("id") == user_id for assignee in task.get("assignees") or []):
        request_json("PUT", f"{api}/tasks/{task_id}/assignees", token, {"user_id": user_id})
    task = request_json("GET", f"{api}/tasks/{task_id}", token)
    assignee_ids = [assignee["id"] for assignee in task.get("assignees") or []]
    print(
        "task-attributes-ready "
        f"id={task['id']} priority={task['priority']} due_date={task['due_date']} "
        f"assignees={','.join(map(str, assignee_ids))}"
    )


if __name__ == "__main__":
    main()
