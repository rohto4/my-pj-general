#!/usr/bin/env bash
set -Eeuo pipefail

IMAGE="${1:-rohto4/vikunja:2.3.0-pj-general-listening-lounge}"
COMPOSE_DIR="${COMPOSE_DIR:-/srv/pj-general/stack}"

if [ ! -d "$COMPOSE_DIR" ]; then
  echo "Compose directory does not exist: $COMPOSE_DIR" >&2
  exit 2
fi

cd "$COMPOSE_DIR"
VIKUNJA_IMAGE="$IMAGE" docker compose up -d --force-recreate vikunja
docker compose ps vikunja

cat <<EOF
active-image=$IMAGE
rollback-image=vikunja/vikunja:2.3.0
data-volumes=unchanged
EOF
