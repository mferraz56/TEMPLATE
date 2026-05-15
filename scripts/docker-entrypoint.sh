#!/usr/bin/env bash
# =============================================================================
# Container entrypoint.
#   * Waits for Postgres (when DATABASE_URL points to a TCP host).
#   * Runs Alembic migrations only when RUN_MIGRATIONS=1 (the worker container
#     should set RUN_MIGRATIONS=0 to avoid races during scale-out).
# =============================================================================
set -euo pipefail

log() { printf '[entrypoint] %s\n' "$*"; }

RUN_MIGRATIONS="${RUN_MIGRATIONS:-0}"
POSTGRES_HOST="${POSTGRES_HOST:-db}"
POSTGRES_INTERNAL_PORT="${POSTGRES_INTERNAL_PORT:-5432}"
POSTGRES_USER="${POSTGRES_USER:-postgres}"
POSTGRES_WAIT_TIMEOUT="${POSTGRES_WAIT_TIMEOUT:-60}"

wait_for_postgres() {
  command -v pg_isready >/dev/null 2>&1 || return 0
  log "waiting for Postgres at ${POSTGRES_HOST}:${POSTGRES_INTERNAL_PORT} (timeout ${POSTGRES_WAIT_TIMEOUT}s)"
  local i=0
  while ! pg_isready -h "${POSTGRES_HOST}" -p "${POSTGRES_INTERNAL_PORT}" -U "${POSTGRES_USER}" -q; do
    i=$((i + 1))
    if [ "$i" -ge "${POSTGRES_WAIT_TIMEOUT}" ]; then
      log "Postgres not ready after ${POSTGRES_WAIT_TIMEOUT}s"
      return 1
    fi
    sleep 1
  done
  log "Postgres is ready"
}

run_migrations() {
  if [ "${RUN_MIGRATIONS}" != "1" ]; then
    log "RUN_MIGRATIONS=${RUN_MIGRATIONS}, skipping alembic"
    return 0
  fi
  if ! python -m alembic --version >/dev/null 2>&1; then
    log "python -m alembic not available; cannot run requested migrations"
    return 1
  fi
  log "running python -m alembic upgrade head"
  python -m alembic upgrade head
}

wait_for_postgres
run_migrations

log "exec: $*"
exec "$@"
