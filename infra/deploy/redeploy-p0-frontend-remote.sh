#!/usr/bin/env bash
# Runs inside the user's interactive SSH shell. It never removes data, volumes, or files.
set -Eeuo pipefail

hash_manifest='/tmp/pj-general-p0-redeploy-hashes.txt'
test -f "$hash_manifest" || { echo 'deployment hash manifest is missing' >&2; exit 40; }
hub_expected="$(sed -n 's/^HUB_EXPECTED=//p' "$hash_manifest" | tail -n 1)"
tasks_expected="$(sed -n 's/^TASKS_EXPECTED=//p' "$hash_manifest" | tail -n 1)"
test -n "$hub_expected" || { echo 'HUB_EXPECTED is missing from deployment hash manifest' >&2; exit 40; }
test -n "$tasks_expected" || { echo 'TASKS_EXPECTED is missing from deployment hash manifest' >&2; exit 40; }
hub_expected="$(printf '%s' "$hub_expected" | tr -d '\r\n' | tr '[:upper:]' '[:lower:]')"
tasks_expected="$(printf '%s' "$tasks_expected" | tr -d '\r\n' | tr '[:upper:]' '[:lower:]')"

hub_actual="$(sha256sum /tmp/pj-general-web-working-tree.tgz | awk '{print $1}')"
tasks_actual="$(sha256sum /tmp/vikunja-listening-lounge-working-tree.tgz | awk '{print $1}')"

if [ "$hub_actual" != "$hub_expected" ]; then
  echo 'hub bundle hash mismatch' >&2
  echo "expected hub SHA-256: $hub_expected" >&2
  echo "actual hub SHA-256:   $hub_actual" >&2
  exit 41
fi

if [ "$tasks_actual" != "$tasks_expected" ]; then
  echo 'tasks bundle hash mismatch' >&2
  echo "expected tasks SHA-256: $tasks_expected" >&2
  echo "actual tasks SHA-256:   $tasks_actual" >&2
  exit 42
fi

cd ~/pj-general-deploy
sudo tar -xzf /tmp/pj-general-web-working-tree.tgz -C ~/pj-general-deploy
sudo install -d -m 0755 ~/pj-general-deploy/build/vikunja-listening-lounge
sudo tar -xzf /tmp/vikunja-listening-lounge-working-tree.tgz -C ~/pj-general-deploy/build/vikunja-listening-lounge
sudo install -m 0755 /tmp/start-pj-general.sh ~/pj-general-deploy/infra/deploy/start-pj-general.sh

cd ~/pj-general-deploy/infra/deploy
grep -q -- '--rebuild-vikunja' start-pj-general.sh
./start-pj-general.sh --start --rebuild-vikunja

for i in $(seq 1 30); do
  if curl -fsS http://192.168.0.200:4173/api/health >/dev/null && curl -fsS http://192.168.0.200:3456/api/v1/info >/dev/null; then
    break
  fi
  sleep 2
done

test "$(curl -fsS -o /dev/null -w '%{http_code}' http://192.168.0.200:4173/api/bootstrap)" = '200'
test "$(curl -fsS -o /dev/null -w '%{http_code}' http://192.168.0.200:3456/api/v1/info)" = '200'
echo 'P0 frontend redeploy complete: Hub /api/bootstrap=200, Tasks /api/v1/info=200'
