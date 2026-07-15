"""Small, injectable JSON HTTP boundary for periodic source collectors."""

from __future__ import annotations

import json
import time
import urllib.error
import urllib.request


class HttpClientError(RuntimeError):
    """A general error code only; response bodies and credentials never escape."""


class UrllibTransport:
    def request(self, method, url, headers=None, json_body=None, timeout=None):
        data = None if json_body is None else json.dumps(json_body, ensure_ascii=False).encode("utf-8")
        request = urllib.request.Request(url, data=data, method=method, headers=headers or {})
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                raw = response.read().decode("utf-8")
                return {"status": response.status, "headers": dict(response.headers.items()), "json": json.loads(raw)}
        except urllib.error.HTTPError as error:
            return {"status": error.code, "headers": dict(error.headers.items()) if error.headers else {}, "json": {}}
        except (urllib.error.URLError, TimeoutError, OSError) as error:
            raise HttpClientError("http_network") from error


class HttpClient:
    def __init__(self, transport=None, timeout_seconds=60, sleep=None):
        self.transport = transport or UrllibTransport()
        self.timeout_seconds = timeout_seconds
        self.sleep = sleep or time.sleep

    def get_json(self, url, headers=None):
        return self.request_json("GET", url, headers=headers)

    def post_json(self, url, json_body, headers=None):
        return self.request_json("POST", url, headers=headers, json_body=json_body)

    def request_json(self, method, url, headers=None, json_body=None):
        retry_delays = (1, 2, 4)
        retried_429 = False
        for attempt, delay in enumerate(retry_delays):
            response = self.transport.request(method, url, headers=headers, json_body=json_body, timeout=self.timeout_seconds)
            status = int(response.get("status") or 0)
            if 200 <= status < 300:
                return response.get("json")
            if status == 429 and not retried_429:
                retried_429 = True
                retry_after = response.get("headers", {}).get("Retry-After", "1")
                try:
                    wait = min(max(int(retry_after), 0), 60)
                except (TypeError, ValueError):
                    wait = 1
                self.sleep(wait)
                continue
            if 500 <= status < 600 and attempt < len(retry_delays) - 1:
                self.sleep(delay)
                continue
            if status == 429:
                raise HttpClientError("http_429")
            if 500 <= status < 600:
                raise HttpClientError("http_5xx")
            raise HttpClientError("http_status")
        raise HttpClientError("http_retry_exhausted")
