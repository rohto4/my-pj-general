"""Collect owner notes from Misskey while preserving the original CW and text."""

from __future__ import annotations

from slack_collector import CollectionResult


class MisskeyCollector:
    def __init__(self, http, base_url, owner_user_id, access_token=""):
        self.http = http
        self.base_url = base_url.rstrip("/")
        self.owner_user_id = owner_user_id
        self.access_token = access_token

    def collect(self, cursor_after=None):
        until_id = None
        events = []
        scanned = 0
        skipped = 0
        newest_id = None
        while True:
            body = {
                "userId": self.owner_user_id,
                "limit": 100,
                "withRenotes": False,
                "withReplies": True,
                "withChannelNotes": True,
            }
            if cursor_after:
                body["sinceId"] = cursor_after
            if until_id:
                body["untilId"] = until_id
            if self.access_token:
                body["i"] = self.access_token
            page = self.http.post_json(f"{self.base_url}/api/users/notes", body)
            if not isinstance(page, list):
                raise ValueError("misskey_api")
            if not page:
                break
            if newest_id is None:
                newest_id = str(page[0].get("id") or "").strip() or None
            for note in page:
                scanned += 1
                note_id = str(note.get("id") or "").strip()
                cw = str(note.get("cw") or "").strip()
                text = str(note.get("text") or "").strip()
                if not note_id or note.get("renoteId") or note.get("deletedAt") or not (cw or text):
                    skipped += 1
                    continue
                events.append({
                    "sourceRef": note_id,
                    "sourceBody": "\n".join(part for part in (cw, text) if part),
                    "occurred": str(note.get("createdAt") or "")[:10] or None,
                })
            until_id = str(page[-1].get("id") or "").strip()
            if not until_id:
                raise ValueError("misskey_pagination")
        return CollectionResult(events=events, cursor_after=newest_id or cursor_after, scanned=scanned, skipped=skipped)
