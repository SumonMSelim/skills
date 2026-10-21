#!/usr/bin/env sh
# Run a diagram spec with Docker when available; fallback to local Python otherwise.
# Usage:
#   gen.sh <spec.py> <out_dir>
set -eu

SPEC=$(cd "$(dirname "$1")" && pwd)/$(basename "$1")
OUT=$(mkdir -p "$2" && cd "$2" && pwd)
HERE=$(cd "$(dirname "$0")" && pwd)
SKILL_ROOT=$(cd "$HERE/.." && pwd)

run_local() {
  if command -v python3 >/dev/null 2>&1; then
    PYTHONPATH="$SKILL_ROOT/scripts${PYTHONPATH:+:$PYTHONPATH}" python3 "$SPEC" "$OUT"
    return
  fi
  if command -v python >/dev/null 2>&1; then
    PYTHONPATH="$SKILL_ROOT/scripts${PYTHONPATH:+:$PYTHONPATH}" python "$SPEC" "$OUT"
    return
  fi
  echo "error: Docker unavailable and no local python/python3 found." >&2
  exit 1
}

if ! command -v docker >/dev/null 2>&1; then
  run_local
  exit 0
fi

if ! docker info >/dev/null 2>&1; then
  run_local
  exit 0
fi

if [ -n "${AWS_ICONS:-}" ]; then
  docker run --rm \
    -v "$SKILL_ROOT":/skill:ro \
    -v "$AWS_ICONS":/icons:ro \
    -v "$SPEC":/spec.py:ro \
    -v "$OUT":/out \
    -e AWS_ICONS=/icons \
    -e THEME="${THEME:-}" \
    -e PYTHONPATH=/skill/scripts \
    -w /out \
    python:3.12-slim python /spec.py /out
else
  docker run --rm \
    -v "$SKILL_ROOT":/skill:ro \
    -v "$SPEC":/spec.py:ro \
    -v "$OUT":/out \
    -e THEME="${THEME:-}" \
    -e PYTHONPATH=/skill/scripts \
    -w /out \
    python:3.12-slim python /spec.py /out
fi
