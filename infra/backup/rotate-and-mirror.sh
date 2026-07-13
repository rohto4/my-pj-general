#!/usr/bin/env bash
set -Eeuo pipefail

# Backup both SQLite stores and the files/config needed to restore Vikunja.
# The script never deletes the live stores. Retention applies only to the
# generated backup generations under BACKUP_ROOT.

PJ_DB_PATH="${PJ_DB_PATH:-/home/unibell4/.local/share/pj-general/p0.sqlite}"
VIKUNJA_DB_PATH="${VIKUNJA_DB_PATH:-/srv/pj-general/data/vikunja/db/vikunja.db}"
VIKUNJA_FILES_PATH="${VIKUNJA_FILES_PATH:-/srv/pj-general/data/vikunja/files}"
VIKUNJA_SECRET_PATH="${VIKUNJA_SECRET_PATH:-/srv/pj-general/secrets/vikunja.env}"
BACKUP_ROOT="${BACKUP_ROOT:-/home/unibell4/.local/share/pj-general/backups}"
P0_BACKUP_DIR="${P0_BACKUP_DIR:-$BACKUP_ROOT/hub}"
MIRROR_ROOT="${MIRROR_ROOT:-}"
KEEP_GENERATIONS="${KEEP_GENERATIONS:-7}"
VERIFY_SCRIPT="${VERIFY_SCRIPT:-/srv/pj-general/infra/vikunja/backup-and-verify.py}"

if ! [[ "$KEEP_GENERATIONS" =~ ^[1-9][0-9]*$ ]]; then
  echo "KEEP_GENERATIONS must be a positive integer" >&2
  exit 2
fi

stamp="$(date -u +%Y%m%d-%H%M%S)"
mkdir -p "$BACKUP_ROOT"

verify_output="$(python3 "$VERIFY_SCRIPT" \
  --pj-db "$PJ_DB_PATH" \
  --vikunja-db "$VIKUNJA_DB_PATH" \
  --backup-root "$BACKUP_ROOT")"
printf '%s\n' "$verify_output"

generation="$(printf '%s\n' "$verify_output" | sed -n 's/^backup-ready path=//p' | tail -n 1)"
if [ -z "$generation" ] || [ ! -d "$generation" ]; then
  echo "backup generation path was not reported" >&2
  exit 1
fi

if [ -d "$VIKUNJA_FILES_PATH" ]; then
  tar -czf "$generation/vikunja-files.tar.gz" -C "$VIKUNJA_FILES_PATH" .
fi
if [ -f "$VIKUNJA_SECRET_PATH" ]; then
  install -m 0600 "$VIKUNJA_SECRET_PATH" "$generation/vikunja.env"
fi

(
  cd "$generation"
  sha256sum -- *.sqlite *.tar.gz vikunja.env 2>/dev/null | sort > manifest.sha256 || true
)
chmod -R go-rwx "$generation"

# The Hub observability endpoint uses the p0-*.sqlite naming contract. Keep a
# verified copy next to the generation so the container-mounted /data path can
# report the same backup that the restore drill just checked.
mkdir -p "$P0_BACKUP_DIR"
hub_backup="$P0_BACKUP_DIR/p0-$stamp.sqlite"
install -m 0600 "$generation/pj-general.sqlite" "$hub_backup"
echo "hub-observability-backup=$hub_backup"

if [ -n "$MIRROR_ROOT" ]; then
  mkdir -p "$MIRROR_ROOT/$stamp"
  cp -a "$generation/." "$MIRROR_ROOT/$stamp/"
  chmod -R go-rwx "$MIRROR_ROOT/$stamp"
  echo "mirror-ready path=$MIRROR_ROOT/$stamp"
fi

mapfile -t generations < <(find "$BACKUP_ROOT" -mindepth 1 -maxdepth 1 -type d -printf '%T@ %p\n' | sort -nr | tail -n +$((KEEP_GENERATIONS + 1)) | cut -d' ' -f2-)
for old_generation in "${generations[@]}"; do
  [ -n "$old_generation" ] && rm -rf -- "$old_generation"
done

echo "backup-complete generation=$generation kept=$KEEP_GENERATIONS"
