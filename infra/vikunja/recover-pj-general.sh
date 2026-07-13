#!/usr/bin/env bash
# Safe recovery helper for the deployed pj-general Hub and Vikunja containers.
# It never removes volumes, imports data, prints environment files, or prints secrets.
set -Eeuo pipefail

MODE="status"
DRY_RUN=0
BUNDLE="/tmp/pj-general-web-working-tree.tgz"
VIKUNJA_IMAGE="rohto4/vikunja:2.3.0-pj-general-listening-lounge"

usage() {
  cat <<'EOF'
Usage:
  recover-pj-general.sh [--status | --redeploy-hub | --restart-all] [--bundle PATH] [--vikunja-image IMAGE] [--dry-run]

Modes:
  --status         Show the Hub Compose location and health/count summary (default).
  --redeploy-hub   Expand the Hub bundle into its detected deploy root, rebuild, recreate, verify.
  --restart-all    Recreate Hub and Vikunja without rebuilding. Vikunja defaults to the Listening Lounge image.

Safety:
  This script does not remove volumes, stop the Compose project wholesale, import data again,
  display environment-file contents, or print secrets. Use --dry-run before an unfamiliar run.
EOF
}

fail() { echo "error: $*" >&2; exit 2; }

run() {
  if [ "$DRY_RUN" -eq 1 ]; then
    printf '+ '
    printf '%q ' "$@"
    printf '\n'
  else
    "$@"
  fi
}

container_label() {
  local container="$1" label="$2"
  sudo docker inspect "$container" --format "{{ index .Config.Labels \"$label\" }}"
}

discover_compose() {
  local container="$1"
  CONTAINER="$container"
  COMPOSE_DIR="$(container_label "$container" 'com.docker.compose.project.working_dir')"
  COMPOSE_FILES="$(container_label "$container" 'com.docker.compose.project.config_files')"
  SERVICE="$(container_label "$container" 'com.docker.compose.service')"
  COMPOSE_FILE="${COMPOSE_FILES%%,*}"

  [ -n "$COMPOSE_DIR" ] || fail "Compose workdir was not found for container: $container"
  [ -n "$COMPOSE_FILE" ] || fail "Compose file was not found for container: $container"
  [ -n "$SERVICE" ] || fail "Compose service was not found for container: $container"
  [ -d "$COMPOSE_DIR" ] || fail "Compose workdir does not exist: $COMPOSE_DIR"
  [ -f "$COMPOSE_FILE" ] || fail "Compose file does not exist: $COMPOSE_FILE"
}

compose_for_current() {
  sudo docker compose --project-directory "$COMPOSE_DIR" -f "$COMPOSE_FILE" "$@"
}

hub_url() {
  local binding
  binding="$(sudo docker port pj-general 4173/tcp | head -n 1 || true)"
  [ -n "$binding" ] || fail "Hub port 4173 is not published by pj-general"
  printf 'http://%s' "$binding"
}

verify_hub() {
  local url
  url="$(hub_url)"
  if [ "$DRY_RUN" -eq 1 ]; then
    echo "+ curl -fsS $url/api/health"
    echo "+ curl -fsS $url/api/bootstrap (counts only)"
    return
  fi
  curl -fsS "$url/api/health"
  curl -fsS "$url/api/bootstrap" | python3 -c '
import json, sys
d = json.load(sys.stdin)
print({"candidates": len(d.get("candidates", [])), "decisions": len(d.get("log", [])), "executionLinks": len(d.get("executionLinks", [])), "executionTaskStates": len(d.get("executionTaskStates", []))})
'
}

status() {
  discover_compose pj-general
  printf 'container=%s\ncompose_dir=%s\ncompose_file=%s\nservice=%s\n' "$CONTAINER" "$COMPOSE_DIR" "$COMPOSE_FILE" "$SERVICE"
  if [ "$DRY_RUN" -eq 1 ]; then
    echo "+ sudo docker ps --format ..."
  else
    sudo docker ps --format 'table {{.Names}}\t{{.Image}}\t{{.Status}}\t{{.Ports}}'
  fi
  verify_hub
}

redeploy_hub() {
  discover_compose pj-general
  [ -f "$BUNDLE" ] || fail "Hub bundle does not exist: $BUNDLE"
  tar -tzf "$BUNDLE" | grep -qx 'apps/web/Dockerfile' || fail "Hub bundle does not contain apps/web/Dockerfile: $BUNDLE"

  DEPLOY_ROOT="$(cd "$COMPOSE_DIR/../.." && pwd)"
  [ -d "$DEPLOY_ROOT/apps/web" ] || fail "Refusing to expand outside a pj-general deploy root: $DEPLOY_ROOT"

  printf 'deploy_root=%s\ncompose_file=%s\nservice=%s\n' "$DEPLOY_ROOT" "$COMPOSE_FILE" "$SERVICE"
  run sudo tar -xzf "$BUNDLE" -C "$DEPLOY_ROOT"
  run sudo docker compose --project-directory "$COMPOSE_DIR" -f "$COMPOSE_FILE" build --no-cache "$SERVICE"
  run sudo docker compose --project-directory "$COMPOSE_DIR" -f "$COMPOSE_FILE" up -d --force-recreate --no-deps "$SERVICE"
  verify_hub
}

restart_container() {
  local container="$1"
  discover_compose "$container"
  printf 'restart_container=%s compose_file=%s service=%s\n' "$CONTAINER" "$COMPOSE_FILE" "$SERVICE"
  if [ "$container" = "vikunja" ]; then
    printf 'vikunja_image=%s\n' "$VIKUNJA_IMAGE"
    run sudo env "VIKUNJA_IMAGE=$VIKUNJA_IMAGE" docker compose --project-directory "$COMPOSE_DIR" -f "$COMPOSE_FILE" up -d --force-recreate --no-deps "$SERVICE"
  else
    run sudo docker compose --project-directory "$COMPOSE_DIR" -f "$COMPOSE_FILE" up -d --force-recreate --no-deps "$SERVICE"
  fi
}

restart_all() {
  restart_container pj-general
  if sudo docker inspect vikunja >/dev/null 2>&1; then
    restart_container vikunja
  else
    echo 'vikunja container is not present; Hub only was restarted.' >&2
  fi
  discover_compose pj-general
  verify_hub
}

while [ "$#" -gt 0 ]; do
  case "$1" in
    --status) MODE="status" ;;
    --redeploy-hub) MODE="redeploy_hub" ;;
    --restart-all) MODE="restart_all" ;;
    --bundle) shift; [ "$#" -gt 0 ] || fail '--bundle requires a path'; BUNDLE="$1" ;;
    --vikunja-image) shift; [ "$#" -gt 0 ] || fail '--vikunja-image requires an image name'; VIKUNJA_IMAGE="$1" ;;
    --dry-run) DRY_RUN=1 ;;
    --help|-h) usage; exit 0 ;;
    *) fail "unknown argument: $1" ;;
  esac
  shift
done

case "$MODE" in
  status) status ;;
  redeploy_hub) redeploy_hub ;;
  restart_all) restart_all ;;
esac
