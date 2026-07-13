#!/usr/bin/env bash
set -Eeuo pipefail

VIKUNJA_SOURCE_DIR="${VIKUNJA_SOURCE_DIR:-/srv/pj-general/build/vikunja-listening-lounge}"
IMAGE="${VIKUNJA_IMAGE:-rohto4/vikunja:2.3.0-pj-general-listening-lounge}"
RELEASE_VERSION="${RELEASE_VERSION:-2.3.0-pj-general-listening-lounge}"

if [ ! -f "$VIKUNJA_SOURCE_DIR/Dockerfile" ]; then
  echo "Vikunja source directory is missing Dockerfile: $VIKUNJA_SOURCE_DIR" >&2
  exit 2
fi

docker build \
  --build-arg RELEASE_VERSION="$RELEASE_VERSION" \
  -t "$IMAGE" \
  "$VIKUNJA_SOURCE_DIR"

docker image inspect "$IMAGE" --format 'image={{.RepoTags}} id={{.Id}} created={{.Created}}'
