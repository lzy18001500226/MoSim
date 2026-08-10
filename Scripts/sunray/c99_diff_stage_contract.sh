#!/usr/bin/env bash
# Shared helpers for the staged C99/Diff-Swarm entrypoints.

if [[ "${BASH_SOURCE[0]}" == "$0" ]]; then
  printf '%s\n' "This file is a source-only helper for the C99/Diff-Swarm staged entrypoints." >&2
  exit 2
fi

c99_diff_stage_die() {
  printf 'BLOCKER %s\n' "$*" >&2
  exit 2
}

c99_diff_load_contract() {
  local contract_file="$1"
  local key value

  [[ -f "${contract_file}" ]] || c99_diff_stage_die "contract file is missing: ${contract_file}"
  while IFS='=' read -r key value || [[ -n "${key}" ]]; do
    key="${key%$'\r'}"
    value="${value%$'\r'}"
    [[ -z "${key}" || "${key}" == \#* ]] && continue
    [[ "${key}" =~ ^[A-Z_][A-Z0-9_]*$ ]] \
      || c99_diff_stage_die "invalid contract key in ${contract_file}: ${key}"
    case "${key}" in
      BASH_ENV|BASHOPTS|BASH_XTRACEFD|CDPATH|ENV|IFS|PATH|SHELLOPTS)
        c99_diff_stage_die "unsafe contract key in ${contract_file}: ${key}"
        ;;
    esac
    export "${key}=${value}"
  done < "${contract_file}"
}

c99_diff_require_json_status() {
  local json_file="$1"
  local expected_status="$2"

  python3 - "${json_file}" "${expected_status}" <<'PY'
import json
import sys
from pathlib import Path

path = Path(sys.argv[1])
expected = sys.argv[2]
if not path.is_file():
    raise SystemExit(f"required status file is missing: {path}")
try:
    payload = json.loads(path.read_text(encoding="utf-8"))
except (OSError, json.JSONDecodeError) as error:
    raise SystemExit(f"unable to read status file {path}: {error}") from error
if payload.get("status") != expected:
    raise SystemExit(
        f"status file {path} has status={payload.get('status')!r}; expected {expected!r}"
    )
PY
}
