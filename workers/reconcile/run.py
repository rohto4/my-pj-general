#!/usr/bin/env python3
"""Run the Hub's Vikunja reconciliation endpoint once."""

import json
import os
import sys
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


def main():
    base_url = os.environ.get("PJ_GENERAL_URL", "http://127.0.0.1:4173").rstrip("/")
    timeout = max(int(os.environ.get("RECONCILE_TIMEOUT_SECONDS", "30")), 1)
    request = Request(
        f"{base_url}/api/integrations/vikunja/reconcile",
        method="POST",
        data=b"{}",
        headers={"content-type": "application/json"},
    )
    try:
        with urlopen(request, timeout=timeout) as response:
            payload = json.loads(response.read().decode("utf-8"))
        print(json.dumps({"state": "succeeded", "result": payload}, ensure_ascii=False))
        return 0
    except HTTPError as error:
        body = error.read().decode("utf-8", errors="replace")
        print(json.dumps({"state": "failed", "status": error.code, "error": body[:500]}, ensure_ascii=False))
        return 1
    except (URLError, TimeoutError, OSError) as error:
        print(json.dumps({"state": "unavailable", "error": str(error)[:500]}, ensure_ascii=False))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
