#!/usr/bin/env bash
set -euo pipefail

MASTER_PORT="${GAZEBO_STEP_PROBE_MASTER_PORT:-11347}"
WORLD="${GAZEBO_STEP_PROBE_WORLD:-/usr/share/gazebo-11/worlds/empty.world}"
export GAZEBO_MASTER_URI="http://127.0.0.1:${MASTER_PORT}"

log_file="$(mktemp /tmp/mosim-gazebo-step-probe.XXXXXX.log)"
stats_file="$(mktemp /tmp/mosim-gazebo-step-stats.XXXXXX.log)"
gzserver --pause "${WORLD}" >"${log_file}" 2>&1 &
server_pid=$!

cleanup() {
  kill "${server_pid}" 2>/dev/null || true
  wait "${server_pid}" 2>/dev/null || true
  rm -f "${log_file}"
  rm -f "${stats_file}"
}
trap cleanup EXIT

ready=false
for _ in $(seq 1 100); do
  if gz world --pause 1 >/dev/null 2>&1; then
    ready=true
    break
  fi
  sleep 0.1
done
if [[ "${ready}" != "true" ]]; then
  cat "${log_file}" >&2
  exit 2
fi

world_stats_topic="$(gz topic -l | grep -E '/world_stats$' | head -n 1)"
if [[ -z "${world_stats_topic}" ]]; then
  gz topic -l >&2
  exit 3
fi
timeout --signal=INT 5 stdbuf -oL gz topic -e "${world_stats_topic}" >"${stats_file}" 2>/dev/null &
stats_pid=$!
sleep 1
gz world --multi-step 5
sleep 0.5
gz world --multi-step 10
sleep 1
kill -INT "${stats_pid}" 2>/dev/null || true
wait "${stats_pid}" 2>/dev/null || true

printf '%s\n' WORLD_STATS
grep -E 'iterations:|sim_time|sec:|nsec:' "${stats_file}" | tail -n 24
