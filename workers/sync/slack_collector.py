"""Collect only owner-authored root messages from the configured Slack channel."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from urllib.parse import urlencode

from http_client import HttpClientError


@dataclass
class CollectionResult:
    events: list
    cursor_after: str | None
    scanned: int
    skipped: int


class SlackCollector:
    def __init__(self, http, channel_id, owner_user_id, bot_token, initial_oldest_ts=None, api_base_url="https://slack.com/api"):
        self.http = http
        self.channel_id = channel_id
        self.owner_user_id = owner_user_id
        self.bot_token = bot_token
        self.initial_oldest_ts = initial_oldest_ts
        self.api_base_url = api_base_url.rstrip("/")

    @staticmethod
    def _occurred(timestamp):
        try:
            return datetime.fromtimestamp(float(timestamp), timezone.utc).date().isoformat()
        except (TypeError, ValueError, OverflowError):
            return None

    def collect(self, cursor_after=None):
        oldest = cursor_after or self.initial_oldest_ts
        page_cursor = None
        events = []
        scanned = 0
        skipped = 0
        while True:
            query = {"channel": self.channel_id, "inclusive": "false", "limit": "15"}
            if oldest:
                query["oldest"] = oldest
            if page_cursor:
                query["cursor"] = page_cursor
            payload = self.http.get_json(
                f"{self.api_base_url}/conversations.history?{urlencode(query)}",
                headers={"Authorization": f"Bearer {self.bot_token}"},
            )
            if not payload.get("ok"):
                raise HttpClientError("slack_api")
            for message in payload.get("messages") or []:
                scanned += 1
                text = str(message.get("text") or "").strip()
                timestamp = str(message.get("ts") or "").strip()
                if (
                    not timestamp
                    or not text
                    or message.get("user") != self.owner_user_id
                    or message.get("subtype")
                    or message.get("thread_ts")
                ):
                    skipped += 1
                    continue
                events.append({
                    "sourceRef": f"{self.channel_id}:{timestamp}",
                    "sourceBody": text,
                    "occurred": self._occurred(timestamp),
                })
            page_cursor = str((payload.get("response_metadata") or {}).get("next_cursor") or "").strip() or None
            if not page_cursor:
                break
        latest = max((event["sourceRef"].split(":", 1)[1] for event in events), default=cursor_after)
        return CollectionResult(events=events, cursor_after=latest, scanned=scanned, skipped=skipped)
