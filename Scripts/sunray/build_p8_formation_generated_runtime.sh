#!/usr/bin/env bash
set -euo pipefail
PROJECT_ROOT="${PROJECT_ROOT:-/mnt/c/Users/HP/Desktop/MoSim}"
MODEL="MoSim_P8_FormationControl_CFunction_Sysblock"
GEN_DIR="${PROJECT_ROOT}/Results/control_platform/p8_formation_mworks_20260717/generated_c/${MODEL}"
OUT_DIR="${PROJECT_ROOT}/Results/control_platform/p8_formation_generated_runtime_20260717"
mkdir -p "${OUT_DIR}"
gcc -std=c11 -O2 -fPIC -shared -Wall -Wextra -Werror \
  "${GEN_DIR}/${MODEL}.c" "${GEN_DIR}/${MODEL}_data.c" \
  "${GEN_DIR}/extern_inc/momodel_extern_ince1.c" \
  "${PROJECT_ROOT}/Scripts/sunray/p8_formation_generated_runtime_wrapper.c" \
  -I"${GEN_DIR}" -I"${GEN_DIR}/extern_inc" -lm \
  -o "${OUT_DIR}/libmosim_p8_formation_generated.so"
sha256sum "${OUT_DIR}/libmosim_p8_formation_generated.so" > "${OUT_DIR}/SHA256SUMS"
printf '%s\n' "${OUT_DIR}/libmosim_p8_formation_generated.so"
