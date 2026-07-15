#!/usr/bin/env bash
set -u

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
STAMP="$(date +%Y%m%d_%H%M%S)"
OUT_DIR="${1:-${ROOT_DIR}/Results/sunray_ros1/falcon_local_nlopt_271_${STAMP}}"
SRC_DIR="${OUT_DIR}/src"
BUILD_DIR="${OUT_DIR}/build"
PREFIX="${OUT_DIR}/prefix"
LOG_FILE="${OUT_DIR}/build.log"
mkdir -p "${OUT_DIR}" "${PREFIX}"

status="failed"
exit_code=0

{
  echo "OUT_DIR=${OUT_DIR}"
  echo "PREFIX=${PREFIX}"
  echo "CMAKE=$(cmake --version 2>/dev/null | head -n 1 || true)"
  echo "GIT=$(git --version 2>/dev/null || true)"
} > "${OUT_DIR}/CONTEXT.txt"

if [ ! -d "${SRC_DIR}/.git" ]; then
  timeout 120s git clone --depth 1 --branch v2.7.1 https://github.com/stevengj/nlopt.git "${SRC_DIR}" > "${LOG_FILE}" 2>&1 || exit_code=$?
fi

if [ "${exit_code}" = "0" ]; then
  mkdir -p "${BUILD_DIR}"
  (
    cd "${BUILD_DIR}"
    timeout 300s cmake "${SRC_DIR}" \
      -DCMAKE_BUILD_TYPE=Release \
      -DCMAKE_INSTALL_PREFIX="${PREFIX}" \
      -DBUILD_SHARED_LIBS=ON \
      -DNLOPT_PYTHON=OFF \
      -DNLOPT_OCTAVE=OFF \
      -DNLOPT_MATLAB=OFF \
      -DNLOPT_GUILE=OFF \
      -DNLOPT_SWIG=OFF \
      && timeout 300s make -j4 \
      && timeout 120s make install
  ) >> "${LOG_FILE}" 2>&1 || exit_code=$?
fi

if [ "${exit_code}" = "0" ] && [ -f "${PREFIX}/include/nlopt.hpp" ]; then
  status="passed"
elif [ "${exit_code}" = "124" ]; then
  status="timeout"
else
  status="failed"
fi

python3 - "$OUT_DIR" "$PREFIX" "$status" "$exit_code" <<'PY'
import json
import sys
from pathlib import Path

out = Path(sys.argv[1])
prefix = Path(sys.argv[2])
status = sys.argv[3]
exit_code = int(sys.argv[4])
payload = {
    "status": status,
    "exit_code": exit_code,
    "out_dir": str(out),
    "prefix": str(prefix),
    "key_files": {
        "nlopt_hpp": str(prefix / "include" / "nlopt.hpp"),
        "nlopt_config_dir": str(prefix / "lib" / "cmake" / "nlopt"),
        "nlopt_lib": [str(p) for p in prefix.rglob("libnlopt.so*")],
    },
}
(out / "FALCON_LOCAL_NLOPT_271.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
(out / "SUMMARY.md").write_text(
    "# FALCON Local NLopt 2.7.1\n\n"
    f"Status: `{status}`\n\n"
    "This packet builds NLopt v2.7.1 into a project-local Results prefix.\n"
    "It does not install system packages.\n\n"
    f"Prefix: `{prefix}`\n\n"
    "Machine-readable file: `FALCON_LOCAL_NLOPT_271.json`\n",
    encoding="utf-8",
)
print(json.dumps({"status": status, "exit_code": exit_code, "out_dir": str(out), "prefix": str(prefix)}, ensure_ascii=False))
PY
