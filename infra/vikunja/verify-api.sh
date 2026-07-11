#!/usr/bin/env sh
set -eu

ENV_FILE="${PJ_GENERAL_ENV_FILE:-$HOME/.config/pj-general/pj-general.env}"
if [ ! -r "$ENV_FILE" ]; then
  echo "pj-general env is not readable: $ENV_FILE" >&2
  exit 2
fi

set -a
. "$ENV_FILE"
set +a

for name in VIKUNJA_BASE_URL VIKUNJA_API_BASE_PATH VIKUNJA_PROJECT_ID VIKUNJA_API_TOKEN; do
  eval "value=\${$name:-}"
  if [ -z "$value" ]; then
    echo "missing required setting: $name" >&2
    exit 2
  fi
done

response="$(
  curl -fsS \
    -H "Authorization: Bearer ${VIKUNJA_API_TOKEN}" \
    "${VIKUNJA_BASE_URL}${VIKUNJA_API_BASE_PATH}/projects/${VIKUNJA_PROJECT_ID}"
)"

printf '%s' "$response" | python3 -c '
import json
import sys

project = json.load(sys.stdin)
print("api-ready project_id={} title={}".format(project["id"], project["title"]))
'
