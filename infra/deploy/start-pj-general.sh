#!/usr/bin/env bash
# Start the Hub and Listening Lounge Vikunja image from one canonical Compose file.
# It never removes volumes, restores data, or prints env-file contents.
set -Eeuo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEPLOY_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
COMPOSE_FILE="$SCRIPT_DIR/compose.yaml"
ENV_FILE="$SCRIPT_DIR/.env"
FORK_DIR="$DEPLOY_ROOT/build/vikunja-listening-lounge"
FORK_BUNDLE="/tmp/vikunja-listening-lounge-working-tree.tgz"
DEFAULT_IMAGE="rohto4/vikunja:2.3.0-pj-general-listening-lounge"
MODE="start"
DRY_RUN=0
ADOPT_EXISTING=0
REBUILD_VIKUNJA=0
COMPOSE_PROJECT="pj-general-deploy"

usage() {
  cat <<'EOF'
Usage: start-pj-general.sh [--status | --start] [--adopt-existing] [--dry-run]

--start    Ensure the Listening Lounge image exists, then start Hub and Vikunja (default).
--status   Show container and health state without changes.
--adopt-existing
           Replace same-name containers created by the former split Compose setup.
           This removes containers only; it never removes volumes, bind-mounted data,
           restores data, or displays environment-file contents.
--rebuild-vikunja
           Rebuild the existing Listening Lounge image from deploy-root/build/
           vikunja-listening-lounge before starting. It never touches volumes or data.
--dry-run  Print the mutating commands without running them.

The script uses infra/deploy/.env for non-secret paths and the LAN address.
It does not remove volumes, import data, or display environment-file contents.
EOF
}

fail() { echo "error: $*" >&2; exit 2; }

run() {
  if [ "$DRY_RUN" -eq 1 ]; then
    printf '+ '; printf '%q ' "$@"; printf '\n'
  else
    "$@"
  fi
}

require_env() {
  [ -f "$ENV_FILE" ] || fail "missing $ENV_FILE; copy .env.example and set only the required paths"
  SERVER_LAN_IP="$(sed -n 's/^SERVER_LAN_IP=//p' "$ENV_FILE" | tail -n 1)"
  [ -n "$SERVER_LAN_IP" ] || fail "SERVER_LAN_IP is missing in $ENV_FILE"
}

ensure_fork_image() {
	if [ "$REBUILD_VIKUNJA" -ne 1 ] && docker image inspect "$DEFAULT_IMAGE" >/dev/null 2>&1; then
    return
  fi
  if [ ! -f "$FORK_DIR/Dockerfile" ]; then
    [ -f "$FORK_BUNDLE" ] || fail "missing fork source and bundle: $FORK_BUNDLE"
    run install -d -m 0755 "$FORK_DIR"
    run tar -xzf "$FORK_BUNDLE" -C "$FORK_DIR"
  fi
  run docker build --build-arg RELEASE_VERSION=2.3.0-pj-general-listening-lounge -t "$DEFAULT_IMAGE" "$FORK_DIR"
}

adopt_or_refuse_existing() {
  local container project
  for container in pj-general vikunja; do
    if ! docker container inspect "$container" >/dev/null 2>&1; then
      continue
    fi
    project="$(docker inspect --format '{{ index .Config.Labels "com.docker.compose.project" }}' "$container")"
    if [ "$project" = "$COMPOSE_PROJECT" ]; then
      continue
    fi
    if [ "$ADOPT_EXISTING" -ne 1 ]; then
      fail "$container is owned by the former Compose project '$project'. Review with --dry-run, then rerun with --adopt-existing to replace containers without deleting data."
    fi
    run docker rm -f "$container"
  done
}

status() {
  require_env
  docker compose --env-file "$ENV_FILE" -f "$COMPOSE_FILE" ps
  curl -fsS "http://$SERVER_LAN_IP:4173/api/health"
  curl -fsS "http://$SERVER_LAN_IP:3456/api/v1/info"
}

wait_for_services() {
  local i
  for i in $(seq 1 30); do
    if curl -fsS "http://$SERVER_LAN_IP:4173/api/health" >/dev/null \
      && curl -fsS "http://$SERVER_LAN_IP:3456/api/v1/info" >/dev/null; then
      return 0
    fi
    sleep 2
  done
  echo "error: Hub or Tasks did not become ready within 60 seconds" >&2
  return 1
}

start() {
  require_env
  ensure_fork_image
  adopt_or_refuse_existing
  run docker compose --env-file "$ENV_FILE" -f "$COMPOSE_FILE" up -d --build --force-recreate
  if [ "$DRY_RUN" -eq 0 ]; then
    wait_for_services
    status
  fi
}

while [ "$#" -gt 0 ]; do
  case "$1" in
    --status) MODE="status" ;;
    --start) MODE="start" ;;
    --adopt-existing) ADOPT_EXISTING=1 ;;
	--rebuild-vikunja) REBUILD_VIKUNJA=1 ;;
    --dry-run) DRY_RUN=1 ;;
    --help|-h) usage; exit 0 ;;
    *) fail "unknown argument: $1" ;;
  esac
  shift
done

case "$MODE" in
  status) status ;;
  start) start ;;
esac
