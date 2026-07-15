#!/usr/bin/env bash
set -u

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
STAMP="$(date +%Y%m%d_%H%M%S)"
OUT_DIR="${1:-${ROOT_DIR}/Results/sunray_ros1/falcon_local_apt_deps_${STAMP}}"
APT_DIR="${OUT_DIR}/apt"
PREFIX="${OUT_DIR}/prefix"
mkdir -p "${APT_DIR}" "${PREFIX}"

packages=(
  libnlopt0
  libnlopt-dev
  libgoogle-glog0v5
  libgoogle-glog-dev
  libgflags2.2
  libgflags-dev
  libdw1
  libdw-dev
  libelf1
  libelf-dev
  libdwarf1
  libdwarf-dev
  libc++1-10
  libc++-10-dev
  libc++abi1-10
  libc++abi-10-dev
)

status="prepared"
missing=()

(
  cd "${APT_DIR}"
  for pkg in "${packages[@]}"; do
    if ! apt download "${pkg}" >> "${OUT_DIR}/apt_download.log" 2>&1; then
      missing+=("${pkg}")
    fi
  done
)

for deb in "${APT_DIR}"/*.deb; do
  [ -e "${deb}" ] || continue
  dpkg-deb -x "${deb}" "${PREFIX}"
done

if [ "${#missing[@]}" -gt 0 ]; then
  status="prepared_with_missing_packages"
fi

python3 - "$OUT_DIR" "$PREFIX" "$status" "${missing[@]}" <<'PY'
import json
import sys
from pathlib import Path

out = Path(sys.argv[1])
prefix = Path(sys.argv[2])
status = sys.argv[3]
missing = sys.argv[4:]

def found(pattern):
    return sorted(str(p.relative_to(prefix)) for p in prefix.rglob(pattern))[:50]

payload = {
    "status": status,
    "out_dir": str(out),
    "prefix": str(prefix),
    "missing_packages": missing,
    "key_files": {
        "nlopt_config": found("NLoptConfig.cmake"),
        "nlopt_libs": found("libnlopt.so*"),
        "glog_headers": found("logging.h"),
        "glog_libs": found("libglog.so*"),
        "dw_libs": found("libdw.so*"),
        "elf_headers": found("gelf.h") + found("libelf.h"),
        "dwarf_libs": found("libdwarf.so*"),
    },
}
(out / "FALCON_LOCAL_APT_DEPS.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
(out / "SUMMARY.md").write_text(
    "# FALCON Local Apt Dependency Prefix\n\n"
    f"Status: `{status}`\n\n"
    "This packet downloads Ubuntu packages into a project-local Results prefix.\n"
    "It does not install system packages with sudo or dpkg -i.\n\n"
    f"Prefix: `{prefix}`\n\n"
    "Machine-readable file: `FALCON_LOCAL_APT_DEPS.json`\n",
    encoding="utf-8",
)
print(json.dumps({"status": status, "out_dir": str(out), "prefix": str(prefix)}, ensure_ascii=False))
PY
