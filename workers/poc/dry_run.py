#!/usr/bin/env python3
"""Non-mutating P1 PoC helpers for similarity and partial auto-confirmation."""

import argparse
import itertools
import json
import re
import sqlite3
from pathlib import Path


TOKEN_RE = re.compile(r"[A-Za-z0-9_]+|[ぁ-んァ-ン一-龥]+")


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description="Run a non-mutating P1 PoC")
    parser.add_argument("--db", default="apps/web/data/p0.sqlite")
    parser.add_argument("--mode", choices=["similarity", "partial-auto-confirm"], required=True)
    parser.add_argument("--threshold", type=float, default=0.35)
    return parser.parse_args(argv)


def text_ngrams(value, size=2):
    text = re.sub(r"\s+", "", str(value or "").lower())
    if not text:
        return set()
    if len(text) <= size:
        return {text}
    return {text[index : index + size] for index in range(len(text) - size + 1)}


def similarity(left, right):
    left_grams = text_ngrams(left)
    right_grams = text_ngrams(right)
    if not left_grams or not right_grams:
        return 0.0
    return len(left_grams & right_grams) / len(left_grams | right_grams)


def load_candidates(connection):
    rows = connection.execute(
        "select id, status, title, kind, confidence, missing_json, source_id from candidates "
        "where status not in ('rejected', 'archived') order by id"
    ).fetchall()
    return [dict(row) for row in rows]


def similarity_dry_run(connection, threshold):
    candidates = load_candidates(connection)
    pairs = []
    for left, right in itertools.combinations(candidates, 2):
        score = similarity(left["title"], right["title"])
        if score < threshold:
            continue
        pairs.append(
            {
                "left": left["id"],
                "right": right["id"],
                "score": round(score, 4),
                "reason": "title character-bigram overlap; proposal only",
            }
        )
    pairs.sort(key=lambda item: (-item["score"], item["left"], item["right"]))
    return {"mode": "similarity", "dryRun": True, "threshold": threshold, "pairs": pairs}


def has_table(connection, name):
    return connection.execute(
        "select 1 from sqlite_master where type = 'table' and name = ?", (name,)
    ).fetchone() is not None


def partial_auto_confirm_dry_run(connection):
    candidates = load_candidates(connection)
    linked = set()
    if has_table(connection, "execution_links"):
        linked = {row[0] for row in connection.execute("select candidate_id from execution_links")}
    eligible = []
    blocked = []
    for candidate in candidates:
        try:
            missing = json.loads(candidate.get("missing_json") or "[]")
        except json.JSONDecodeError:
            missing = ["invalid missing_json"]
        reasons = []
        if candidate["status"] != "pending":
            reasons.append("status is not pending")
        if candidate["confidence"] != "high":
            reasons.append("confidence is not high")
        if missing:
            reasons.append("missing fields remain")
        if candidate["id"] in linked:
            reasons.append("execution link already exists")
        if reasons:
            blocked.append({"id": candidate["id"], "reasons": reasons})
        else:
            eligible.append({"id": candidate["id"], "action": "would-approve", "reason": "dry-run only"})
    return {
        "mode": "partial-auto-confirm",
        "dryRun": True,
        "eligible": eligible,
        "blocked": blocked,
        "wouldUpdate": len(eligible),
    }


def main(argv=None):
    args = parse_args(argv)
    database = Path(args.db)
    with sqlite3.connect(database) as connection:
        connection.row_factory = sqlite3.Row
        result = similarity_dry_run(connection, args.threshold) if args.mode == "similarity" else partial_auto_confirm_dry_run(connection)
    print(json.dumps(result, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
