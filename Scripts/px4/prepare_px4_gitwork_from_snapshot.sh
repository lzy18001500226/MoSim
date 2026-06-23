#!/usr/bin/env bash
# Prepare a buildable PX4 git worktree from the project-local source snapshot.
#
# The checked-in PX4 reference snapshot may not contain its own .git metadata.
# PX4's Makefile refuses to build without .git. This script creates a separate
# hardlink copy under Results/tmp and initializes git metadata there, leaving
# References/PX4/PX4 unchanged.
set -euo pipefail

PROJECT_ROOT="${PROJECT_ROOT:-/mnt/c/Users/HP/Desktop/MoSim}"
SOURCE_PX4_DIR="${SOURCE_PX4_DIR:-${PROJECT_ROOT}/References/PX4/PX4}"
PX4_GITWORK_DIR="${PX4_GITWORK_DIR:-${PROJECT_ROOT}/Results/tmp/px4_gitwork/PX4}"
RESULT_JSON="${RESULT_JSON:-${PROJECT_ROOT}/Results/px4_gazebo/px4_gitwork_prepare_$(date +%Y%m%d_%H%M%S).json}"

mkdir -p "$(dirname "${PX4_GITWORK_DIR}")" "$(dirname "${RESULT_JSON}")"

status="unknown"
message=""

if [[ ! -d "${SOURCE_PX4_DIR}" ]]; then
  status="blocked_missing_source_snapshot"
  message="SOURCE_PX4_DIR does not exist"
elif [[ -e "${PX4_GITWORK_DIR}" && ! -d "${PX4_GITWORK_DIR}/.git" ]]; then
  status="blocked_existing_non_gitwork"
  message="PX4_GITWORK_DIR exists but has no .git; not deleting or overwriting"
elif [[ -d "${PX4_GITWORK_DIR}/.git" ]]; then
  status="ready_existing"
  message="existing gitwork reused"
else
  cp -al "${SOURCE_PX4_DIR}" "${PX4_GITWORK_DIR}"
  git -C "${PX4_GITWORK_DIR}" init
  git -C "${PX4_GITWORK_DIR}" config user.email "mosim-local@example.invalid"
  git -C "${PX4_GITWORK_DIR}" config user.name "MoSim Local Gitwork"
  status="ready_created"
  message="hardlink gitwork created from source snapshot"
fi

if [[ "${status}" == ready_* ]]; then
  git -C "${PX4_GITWORK_DIR}" status --short > "$(dirname "${RESULT_JSON}")/px4_gitwork_status.txt" 2>&1 || true
fi

python3 - "${RESULT_JSON}" "${status}" "${message}" "${SOURCE_PX4_DIR}" "${PX4_GITWORK_DIR}" <<'PY'
import json
import pathlib
import sys
from datetime import datetime, timezone

result_json = pathlib.Path(sys.argv[1])
source = pathlib.Path(sys.argv[4])
gitwork = pathlib.Path(sys.argv[5])

required = {
    "Makefile": gitwork / "Makefile",
    "gz_models_cmake": gitwork / "Tools/simulation/gz/CMakeLists.txt",
    "micro_xrce_client_cmake": gitwork / "src/modules/uxrce_dds_client/Micro-XRCE-DDS-Client/CMakeLists.txt",
    "mavlink_common_xml": gitwork / "src/modules/mavlink/mavlink/message_definitions/v1.0/common.xml",
    "dds_topics_yaml": gitwork / "src/modules/uxrce_dds_client/dds_topics.yaml",
}

payload = {
    "schema": "mosim.px4_gitwork_prepare.v1",
    "timestamp_utc": datetime.now(timezone.utc).isoformat(),
    "status": sys.argv[2],
    "message": sys.argv[3],
    "semantic_boundary": "prepare_only_no_build_no_runtime",
    "source_px4_dir": str(source),
    "px4_gitwork_dir": str(gitwork),
    "source_has_git": (source / ".git").exists(),
    "gitwork_has_git": (gitwork / ".git").exists(),
    "required_files": {name: {"path": str(path), "exists": path.exists()} for name, path in required.items()},
}
result_json.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps(payload, ensure_ascii=False, indent=2))
PY

case "${status}" in
  ready_created|ready_existing) exit 0 ;;
  *) exit 2 ;;
esac
