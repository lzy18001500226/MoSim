#!/usr/bin/env bash
set -euo pipefail

# Start the project-owned Unreal renderer in game mode and stream a short
# MWORKS-derived replay packet sequence for manual S0/S1 visual review.

PROJECT_ROOT="/mnt/c/Users/HP/Desktop/MoSim"
RAW_CSV="${1:-${PROJECT_ROOT}/Results/planning/single_obstacle_astar_awff/sunray150_planning_open_blocks_linear_mpc_sysblock/raw/sunray150_planning_open_blocks_linear_mpc_height_profile_0p2_sensor_20hz.csv}"
UNREAL_HOST="${UNREAL_HOST:-$(ip route | awk '/^default/ {print $3; exit}')}"
SCENE_ID="${SCENE_ID:-renderer_framework_manual_review}"
MAP_ID="${MAP_ID:-renderer_framework}"

cd "${PROJECT_ROOT}"

bash Scripts/UE5/open_unreal_renderer.sh game

echo "Waiting for MworksUnrealRenderer game UDP endpoint on Windows port 5005..."
for _ in $(seq 1 90); do
  if powershell.exe -NoProfile -Command \
    "\$game = Get-CimInstance Win32_Process -Filter \"name = 'UnrealEditor.exe'\" | Where-Object { \$_.CommandLine -like '*MworksUnrealRenderer.uproject*' -and \$_.CommandLine -like '* -game*' } | Select-Object -First 1; if (-not \$game) { exit 1 }; \$udp = Get-NetUDPEndpoint -LocalPort 5005 -ErrorAction SilentlyContinue | Where-Object { \$_.OwningProcess -eq \$game.ProcessId } | Select-Object -First 1; if (\$udp) { exit 0 } else { exit 1 }" >/dev/null 2>&1; then
    break
  fi
  sleep 1
done
powershell.exe -NoProfile -Command \
  "\$game = Get-CimInstance Win32_Process -Filter \"name = 'UnrealEditor.exe'\" | Where-Object { \$_.CommandLine -like '*MworksUnrealRenderer.uproject*' -and \$_.CommandLine -like '* -game*' } | Select-Object -First 1; if (-not \$game) { Write-Error 'MworksUnrealRenderer -game process not found'; exit 1 }; \$udp = Get-NetUDPEndpoint -LocalPort 5005 -ErrorAction SilentlyContinue | Where-Object { \$_.OwningProcess -eq \$game.ProcessId } | Select-Object -First 1; if (-not \$udp) { Write-Error 'UDP 5005 endpoint not found for MworksUnrealRenderer -game process'; exit 1 }; \$game | Select-Object ProcessId,CommandLine; \$udp | Select-Object LocalAddress,LocalPort,OwningProcess"

python3 Scripts/UE5/stream_unreal_udp.py "${RAW_CSV}" \
  --host "${UNREAL_HOST}" \
  --port 5005 \
  --scene-id "${SCENE_ID}" \
  --map-id "${MAP_ID}" \
  --fps 20 \
  --replay-speed 1.0 \
  --print-every 100
