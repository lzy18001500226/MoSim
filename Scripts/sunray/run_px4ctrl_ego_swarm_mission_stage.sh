#!/usr/bin/env bash
# Run only the C99/Diff-Swarm mission against a retained components stage.

set -euo pipefail

require_value() {
  local name="$1"
  [[ -n "${!name:-}" ]] || {
    printf 'BLOCKER required component-contract value is missing: %s\n' "${name}" >&2
    exit 2
  }
}

for required in \
  PROJECT_ROOT RESULT_DIR UAV_NUM PLANNER_VARIANT \
  START1_X START1_Y START2_X START2_Y START3_X START3_Y \
  TARGET1_X TARGET1_Y TARGET1_Z TARGET2_X TARGET2_Y TARGET2_Z TARGET3_X TARGET3_Y TARGET3_Z \
  PLANNER_TARGET_MODE PLANNER_GOAL_TOPIC_TEMPLATE TOTAL_TIMEOUT_S; do
  require_value "${required}"
done

[[ "${PLANNER_VARIANT}" == "diff_planner" ]] || {
  printf 'BLOCKER mission stage supports PLANNER_VARIANT=diff_planner only\n' >&2
  exit 2
}

set +e
timeout --kill-after=15s "${TOTAL_TIMEOUT_S}s" python3 "${PROJECT_ROOT}/Scripts/sunray/px4ctrl_ego_swarm_mission_node.py" \
  --result-dir "${RESULT_DIR}" \
  --uav-num "${UAV_NUM}" \
  --start1-x "${START1_X}" --start1-y "${START1_Y}" \
  --start2-x "${START2_X}" --start2-y "${START2_Y}" \
  --start3-x "${START3_X}" --start3-y "${START3_Y}" \
  --target1-x "${TARGET1_X}" --target1-y "${TARGET1_Y}" --target1-z "${TARGET1_Z}" \
  --target2-x "${TARGET2_X}" --target2-y "${TARGET2_Y}" --target2-z "${TARGET2_Z}" \
  --target3-x "${TARGET3_X}" --target3-y "${TARGET3_Y}" --target3-z "${TARGET3_Z}" \
  --target1-chain-file "${TARGET1_CHAIN_FILE}" \
  --target2-chain-file "${TARGET2_CHAIN_FILE}" \
  --target3-chain-file "${TARGET3_CHAIN_FILE}" \
  --formation-center-chain-file "${FORMATION_CENTER_CHAIN_FILE}" \
  --target-chain-max-goals "${TARGET_CHAIN_MAX_GOALS}" \
  --target-chain-goal-timeout-s "${TARGET_CHAIN_GOAL_TIMEOUT_S}" \
  --target-chain-goal-wall-timeout-s "${TARGET_CHAIN_GOAL_WALL_TIMEOUT_S}" \
  --takeoff-height "${EGO_GATE_TAKEOFF_HEIGHT}" \
  --planner-target-mode "${PLANNER_TARGET_MODE}" \
  --goal-topic-template "${PLANNER_GOAL_TOPIC_TEMPLATE}" \
  --goal-publish-stagger-s "${GOAL_PUBLISH_STAGGER_S}" \
  --formation-target-recovery-max-attempts "${EGO_GATE_FORMATION_TARGET_RECOVERY_MAX_ATTEMPTS}" \
  --formation-target-recovery-stall-s "${EGO_GATE_FORMATION_TARGET_RECOVERY_STALL_S}" \
  --formation-target-recovery-wall-stall-s "${EGO_GATE_FORMATION_TARGET_RECOVERY_WALL_STALL_S}" \
  --formation-target-recovery-min-improvement-m "${EGO_GATE_FORMATION_TARGET_RECOVERY_MIN_IMPROVEMENT_M}" \
  --raw-position-cmd-topic-template "/uav{uid}/planner_position_cmd_raw" \
  --adapted-position-cmd-topic-template "/uav{uid}/position_cmd" \
  --world-cloud-topic-template "/uav{uid}/livox_world" \
  --cmd-adapter-enable-topic-template "/uav{uid}/mosim/position_cmd_adapter_enable" \
  --bspline-topic-template "" \
  --bspline-msg-package traj_utils \
  --polytraj-topic-template "/drone_{drone_id}_planning/trajectory" \
  --occupancy-topic-template "/drone_{drone_id}_ego_planner_node/grid_map/occupancy_inflate" \
  --cmd-safety-diagnostics-template "${RESULT_DIR}/uav{uid}_position_cmd_safety_adapter.json" \
  --min-raw-planner-z-warn-m "${EGO_CMD_SAFETY_MIN_Z}" \
  --min-adapted-cmd-z-m "${EGO_CMD_SAFETY_MIN_Z}" \
  --max-position-cmd-jump-m "${EGO_CMD_SAFETY_MAX_POSITION_JUMP_M}" \
  --max-position-cmd-speed-mps "${EGO_CMD_SAFETY_MAX_POSITION_JUMP_SPEED_MPS}" \
  --min-inter-uav-distance "${EGO_GATE_MIN_INTER_UAV_DISTANCE}" \
  $(if [[ "${EGO_GATE_INTER_UAV_EMERGENCY_HOLD_ENABLE}" == "true" ]]; then echo "--inter-uav-emergency-hold-enabled"; fi) \
  --inter-uav-emergency-deceleration-mps2 "${EGO_GATE_INTER_UAV_EMERGENCY_DECELERATION_MPS2}" \
  --inter-uav-emergency-margin-m "${EGO_GATE_INTER_UAV_EMERGENCY_MARGIN_M}" \
  --inter-uav-emergency-min-closing-speed-mps "${EGO_GATE_INTER_UAV_EMERGENCY_MIN_CLOSING_SPEED_MPS}" \
  --inter-uav-emergency-odom-timeout-s "${EGO_GATE_INTER_UAV_EMERGENCY_ODOM_TIMEOUT_S}" \
  $(if [[ "${EGO_GATE_BLOCK_ON_RAW_CMD_DISCONTINUITY}" == "true" ]]; then echo "--block-on-raw-position-cmd-discontinuity"; else echo "--warn-on-raw-position-cmd-discontinuity"; fi) \
  --ready-timeout-s "${EGO_GATE_READY_TIMEOUT_S}" \
  --mavros-ready-min-state-samples "${MAVROS_READY_MIN_STATE_SAMPLES}" \
  --mavros-ready-stable-wall-s "${MAVROS_READY_STABLE_WALL_S}" \
  --takeoff-timeout-s "${EGO_GATE_TAKEOFF_TIMEOUT_S}" \
  --takeoff-wall-timeout-s "${EGO_GATE_TAKEOFF_WALL_TIMEOUT_S}" \
  --ego-takeover-timeout-s "${EGO_GATE_EGO_TAKEOVER_TIMEOUT_S}" \
  --execute-timeout-s "${EGO_GATE_EXECUTE_TIMEOUT_S}" \
  --execute-wall-timeout-s "${EGO_GATE_EXECUTE_WALL_TIMEOUT_S}" \
  --land-timeout-s "${EGO_GATE_LAND_TIMEOUT_S}" \
  --land-wall-timeout-s "${EGO_GATE_LAND_WALL_TIMEOUT_S}" \
  --pre-land-hover-s "${EGO_GATE_PRE_LAND_HOVER_S}" \
  --pre-land-no-cmd-s "${EGO_GATE_PRE_LAND_NO_CMD_S}" \
  --pre-land-no-cmd-wall-timeout-s "${EGO_GATE_PRE_LAND_NO_CMD_WALL_TIMEOUT_S}" \
  --landed-z-max "${EGO_GATE_LANDED_Z_MAX}" \
  --landed-z-tolerance-m "${EGO_GATE_LANDED_Z_TOLERANCE_M}" \
  --pre-takeoff-settle-s "${EGO_GATE_PRE_TAKEOFF_SETTLE_S}" \
  --pre-takeoff-settle-timeout-s "${EGO_GATE_PRE_TAKEOFF_SETTLE_TIMEOUT_S}" \
  --pre-takeoff-odom-timeout-s "${EGO_GATE_PRE_TAKEOFF_ODOM_TIMEOUT_S}" \
  --pre-takeoff-truth-timeout-s "${EGO_GATE_PRE_TAKEOFF_TRUTH_TIMEOUT_S}" \
  --pre-takeoff-max-speed-mps "${EGO_GATE_PRE_TAKEOFF_MAX_SPEED_MPS}" \
  --pre-takeoff-max-vz-mps "${EGO_GATE_PRE_TAKEOFF_MAX_VZ_MPS}" \
  --pre-takeoff-max-roll-pitch-deg "${EGO_GATE_PRE_TAKEOFF_MAX_ROLL_PITCH_DEG}" \
  --pre-takeoff-min-target-attitude-count "${EGO_GATE_PRE_TAKEOFF_MIN_TARGET_ATTITUDE_COUNT}" \
  --pre-takeoff-min-debug-count "${EGO_GATE_PRE_TAKEOFF_MIN_DEBUG_COUNT}" \
  --takeoff-uav-stagger-s "${EGO_GATE_TAKEOFF_UAV_STAGGER_S}" \
  --takeoff-retry-interval-s "${EGO_GATE_TAKEOFF_RETRY_INTERVAL_S}" \
  --takeoff-retry-repeats "${EGO_GATE_TAKEOFF_RETRY_REPEATS}" \
  --takeoff-retry-max "${EGO_GATE_TAKEOFF_RETRY_MAX}" \
  --takeoff-rise-detect-m "${EGO_GATE_TAKEOFF_RISE_DETECT_M}" \
  --pre-planner-stable-s "${EGO_GATE_PRE_STABLE_S}" \
  --pre-planner-max-xy-error-m "${EGO_GATE_PRE_MAX_XY_ERROR_M}" \
  --pre-planner-max-z-error-m "${EGO_GATE_PRE_MAX_Z_ERROR_M}" \
  --pre-planner-max-speed-mps "${EGO_GATE_PRE_MAX_SPEED_MPS}" \
  --pre-planner-max-vz-mps "${EGO_GATE_PRE_MAX_VZ_MPS}" \
  --pre-planner-max-roll-pitch-deg "${EGO_GATE_PRE_MAX_ROLL_PITCH_DEG}" \
  --target-hold-s "${EGO_GATE_TARGET_HOLD_S}" \
  --target-hold-max-speed-mps "${EGO_GATE_TARGET_HOLD_MAX_SPEED_MPS}" \
  --target-reached-radius "${EGO_GATE_TARGET_REACHED_RADIUS_M}" \
  --target-hold-max-vz-mps "${EGO_GATE_TARGET_HOLD_MAX_VZ_MPS}" \
  --target-stable-skip-radius-m "${EGO_GATE_TARGET_STABLE_SKIP_RADIUS_M}" \
  --target-stable-skip-s "${EGO_GATE_TARGET_STABLE_SKIP_S}" \
  --target-stable-skip-max-speed-mps "${EGO_GATE_TARGET_STABLE_SKIP_MAX_SPEED_MPS}" \
  --target-stable-skip-max-vz-mps "${EGO_GATE_TARGET_STABLE_SKIP_MAX_VZ_MPS}" \
  --min-occupancy-count "${EGO_GATE_MIN_OCCUPANCY_COUNT}" \
  --min-occupancy-points "${EGO_GATE_MIN_OCCUPANCY_POINTS}" \
  $(if [[ "${EGO_GATE_PUBLISH_HOVER_DURING_TAKEOFF}" == "true" ]]; then echo "--publish-hover-during-takeoff"; fi) \
  > "${RESULT_DIR}/px4ctrl_ego_swarm_mission.log" 2>&1
mission_exit_code=$?
set -e

exit "${mission_exit_code}"
