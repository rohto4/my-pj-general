#!/usr/bin/env bash
# Verify one transferred batch and import it through the Linux Hub's sole SQLite writer.
set -Eeuo pipefail

BATCH="${1:-/tmp/threadline-knowledge-vault-batch.json}"
MANIFEST="${2:-/tmp/threadline-knowledge-vault-manifest.json}"

case "$BATCH" in /tmp/*.json) ;; *) echo "batch must be an absolute /tmp JSON path" >&2; exit 2 ;; esac
case "$MANIFEST" in /tmp/*.json) ;; *) echo "manifest must be an absolute /tmp JSON path" >&2; exit 2 ;; esac
test -f "$BATCH"
test -f "$MANIFEST"

cleanup() {
  rm -f -- "$BATCH" "$MANIFEST" "${BATCH%.json}.verified.json"
}
trap cleanup EXIT

EXPECTED="$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1], encoding="utf-8"))["sha256"])' "$MANIFEST")"
ACTUAL="$(sha256sum "$BATCH" | awk '{print $1}')"
test "$ACTUAL" = "$EXPECTED" || { echo "batch SHA-256 mismatch" >&2; exit 3; }

docker container inspect pj-general >/dev/null 2>&1
VERIFIED="${BATCH%.json}.verified.json"
python3 -c 'import json,sys; p=json.load(open(sys.argv[1], encoding="utf-8")); p["_manifest_sha256"]=sys.argv[3]; json.dump(p, open(sys.argv[2], "w", encoding="utf-8"), ensure_ascii=False)' "$BATCH" "$VERIFIED" "$ACTUAL"
docker exec -i pj-general python3 /app/db_tool.py import-vault-batch < "$VERIFIED"
