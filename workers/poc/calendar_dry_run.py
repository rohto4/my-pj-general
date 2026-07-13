#!/usr/bin/env python3
"""Build one-way calendar event proposals without calling Google Calendar."""

import argparse
import hashlib
import json
import re
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path


SCHEDULE_RE = re.compile(r"(?P<date>\d{4}-\d{2}-\d{2})(?:\s+|\s*/\s*)(?P<minutes>\d+)\s*min")


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description="Prepare one-way Calendar event proposals")
    parser.add_argument("--db", default="apps/web/data/p0.sqlite")
    return parser.parse_args(argv)


def event_key(candidate_id, start, end):
    raw = f"google_calendar:{candidate_id}:{start}:{end}".encode("utf-8")
    return "gcal-" + hashlib.sha256(raw).hexdigest()[:24]


def build_proposals(connection):
    rows = connection.execute(
        "select id, title, summary, schedule from candidates where status = 'approved' order by id"
    ).fetchall()
    proposals = []
    blocked = []
    for row in rows:
        match = SCHEDULE_RE.search(row["schedule"] or "")
        if not match:
            blocked.append({"id": row["id"], "reason": "schedule date and duration are required"})
            continue
        start = datetime.strptime(match.group("date"), "%Y-%m-%d").replace(hour=9, minute=0)
        end = start + timedelta(minutes=int(match.group("minutes")))
        proposals.append(
            {
                "candidateId": row["id"],
                "title": row["title"],
                "description": row["summary"],
                "startCandidate": start.isoformat(),
                "endCandidate": end.isoformat(),
                "idempotencyKey": event_key(row["id"], start.isoformat(), end.isoformat()),
                "action": "would-create-after-user-go",
            }
        )
    return {
        "mode": "calendar-one-way",
        "dryRun": True,
        "proposals": proposals,
        "blocked": blocked,
        "wouldCreate": len(proposals),
        "externalCalls": 0,
    }


def main(argv=None):
    args = parse_args(argv)
    with sqlite3.connect(Path(args.db)) as connection:
        connection.row_factory = sqlite3.Row
        result = build_proposals(connection)
    print(json.dumps(result, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
