#!/usr/bin/env bash
# Run the G9.5/G9.6 paper-grade controller candidates through the existing
# px4ctrl Sunray/Gazebo gate without duplicating mission logic.

set -uo pipefail

PROJECT_ROOT="${PROJECT_ROOT:-/mnt/c/Users/HP/Desktop/MoSim}"
RUN_STAMP="${RUN_STAMP:-$(date +%Y%m%d_%H%M%S)}"
RUN_ROOT="${RUN_ROOT:-${PROJECT_ROOT}/Results/sunray_ros1/g95_g96_controller_ab_${RUN_STAMP}}"
MISSIONS="${MISSIONS:-takeoff_hover_land figure8}"
CONTROLLERS="${CONTROLLERS:-dfbc_high_order dfbc_smooth_robust}"
BASIC_GATE="${BASIC_GATE:-${PROJECT_ROOT}/Scripts/sunray/run_px4ctrl_basic_gate.sh}"
DEFAULT_TRAJECTORY_MISSION_ARGS="${DEFAULT_TRAJECTORY_MISSION_ARGS:---force-disarm-after-land --force-disarm-timeout-s 18}"
PX4CTRL_USE_BODYRATE_CTRL="${PX4CTRL_USE_BODYRATE_CTRL:-false}"
if [[ "${PX4CTRL_USE_BODYRATE_CTRL}" == "true" ]]; then
  COMMAND_INTERFACE="BODYRATE_THRUST"
  CLAIM_BOUNDARY="ROS1/Sunray/Gazebo/PX4/MAVROS/px4ctrl BODYRATE_THRUST release-smoke runtime. The run verifies the existing px4ctrl use_bodyrate_ctrl path; snap/body-acceleration command release, MWORKS generated-code acceptance, and PX4-native deployment remain forbidden claims."
else
  COMMAND_INTERFACE="ATTITUDE_THRUST"
  CLAIM_BOUNDARY="ROS1/Sunray/Gazebo/PX4/MAVROS/px4ctrl ATTITUDE_THRUST runtime only. Body-rate/thrust release, MWORKS generated-code acceptance, and PX4-native deployment remain forbidden claims."
fi

mkdir -p "${RUN_ROOT}"

SUMMARY_TSV="${RUN_ROOT}/summary.tsv"
MANIFEST_JSONL="${RUN_ROOT}/runs.jsonl"

printf 'controller\tmission\tcommand_interface\tstatus\tresult_dir\n' > "${SUMMARY_TSV}"
: > "${MANIFEST_JSONL}"

overall_status=0

for controller in ${CONTROLLERS}; do
  case "${controller}" in
    dfbc_high_order)
      goal="G9.5"
      ;;
    dfbc_smooth_robust)
      goal="G9.6"
      ;;
    *)
      echo "Unsupported controller in CONTROLLERS=${controller}" >&2
      overall_status=2
      continue
      ;;
  esac

  for mission in ${MISSIONS}; do
    run_id="$(printf '%s_%s_%s_%s' "${goal}" "${controller}" "${mission}" "${RUN_STAMP}" | tr '[:upper:]' '[:lower:]' | tr '.' '_')"
    result_dir="${RUN_ROOT}/${run_id}"
    mkdir -p "${result_dir}"

    mission_extra_args="${PX4CTRL_MISSION_EXTRA_ARGS:-}"
    if [[ -z "${mission_extra_args}" && "${mission}" != "takeoff_hover_land" ]]; then
      mission_extra_args="${DEFAULT_TRAJECTORY_MISSION_ARGS}"
    fi

    echo "== ${goal} ${controller} ${mission} =="
    set +e
      PX4CTRL_CORE_PROFILE="${controller}" \
      PX4CTRL_KP_XY="${PX4CTRL_KP_XY:-12}" \
      PX4CTRL_KP_Z="${PX4CTRL_KP_Z:-5}" \
      PX4CTRL_USE_BODYRATE_CTRL="${PX4CTRL_USE_BODYRATE_CTRL}" \
      PX4CTRL_MISSION_EXTRA_ARGS="${mission_extra_args}" \
      RUN_ID="${run_id}" \
      RESULT_DIR="${result_dir}" \
      PROJECT_ROOT="${PROJECT_ROOT}" \
      bash "${BASIC_GATE}" "${mission}" \
      > "${result_dir}/ab_runner.log" 2>&1
    exit_code=$?
    set -e

    if [[ "${exit_code}" -eq 0 ]]; then
      status="passed"
    else
      status="failed:${exit_code}"
      overall_status="${exit_code}"
    fi

    printf '%s\t%s\t%s\t%s\t%s\n' "${controller}" "${mission}" "${COMMAND_INTERFACE}" "${status}" "${result_dir}" >> "${SUMMARY_TSV}"
    python3 - <<PY >> "${MANIFEST_JSONL}"
import json
print(json.dumps({
    "goal": "${goal}",
    "controller": "${controller}",
    "mission": "${mission}",
    "command_interface": "${COMMAND_INTERFACE}",
    "px4ctrl_use_bodyrate_ctrl": "${PX4CTRL_USE_BODYRATE_CTRL}" == "true",
    "status": "${status}",
    "exit_code": ${exit_code},
    "result_dir": "${result_dir}",
}, sort_keys=True))
PY
  done
done

cat > "${RUN_ROOT}/README.md" <<EOF
# G9.5/G9.6 Controller A/B Gate

- run_root: \`${RUN_ROOT}\`
- missions: \`${MISSIONS}\`
- controllers: \`${CONTROLLERS}\`
- backend: existing \`Scripts/sunray/run_px4ctrl_basic_gate.sh\`
- command_interface: \`${COMMAND_INTERFACE}\`
- PX4CTRL_USE_BODYRATE_CTRL: \`${PX4CTRL_USE_BODYRATE_CTRL}\`
- claim_boundary: ${CLAIM_BOUNDARY}

This packet is runtime evidence only after each child result directory contains
the normal px4ctrl gate artifacts and metrics. Use \`CONTROLLERS=<one>\` and
\`MISSIONS=<one>\` for bounded single-case execution; ordinary live runs should
not use one long blocking batch.

See \`summary.tsv\` and \`runs.jsonl\` for child run status.
EOF

echo "${RUN_ROOT}"
exit "${overall_status}"
