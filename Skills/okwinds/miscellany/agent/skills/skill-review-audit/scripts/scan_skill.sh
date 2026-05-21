#!/usr/bin/env bash
set -euo pipefail

skill_dir="${1:-}"
if [[ -z "${skill_dir}" ]]; then
  echo "usage: scan_skill.sh /path/to/skill-dir" >&2
  exit 2
fi

if [[ ! -d "${skill_dir}" ]]; then
  echo "error: not a directory: ${skill_dir}" >&2
  exit 2
fi

echo "== Skill Directory =="
echo "${skill_dir}"
echo

echo "== Tree (depth 3) =="
find "${skill_dir}" -maxdepth 3 -print | sed 's|^| - |'
echo

echo "== File Sizes (top 30) =="
if command -v gdu >/dev/null 2>&1; then
  gdu -ah "${skill_dir}" | sort -hr | head -30
else
  du -ah "${skill_dir}" | sort -hr | head -30
fi
echo

echo "== Provenance Files (if present) =="
for f in ".openskills.json" "package.json" "pyproject.toml" "requirements.txt" "Pipfile" "Gemfile" "go.mod"; do
  if [[ -f "${skill_dir}/${f}" ]]; then
    echo "-- ${f}"
    sed -n '1,120p' "${skill_dir}/${f}" || true
    echo
  fi
done

echo "== Risky Pattern Scan (heuristic) =="
line_patterns=(
  "rm -rf"
  "mkfs"
  "dd if="
  "sudo "
  "curl .*\\|.*sh"
  "wget .*\\|.*sh"
  "Invoke-WebRequest"
  "powershell"
  "ssh "
  "scp "
  "kubectl"
  "docker"
  "npm install"
  "pnpm add"
  "pip install"
  "brew install"
  "http://"
  "https://"
)

sensitive_patterns=(
  "API_KEY"
  "SECRET"
  "TOKEN"
  "BEGIN PRIVATE KEY"
)

if command -v rg >/dev/null 2>&1; then
  for p in "${line_patterns[@]}"; do
    rg -n --hidden --no-heading -S --color never "${p}" "${skill_dir}" && echo || true
  done

  # For secret-like patterns, avoid printing matching lines (which may contain values).
  for p in "${sensitive_patterns[@]}"; do
    rg -n --hidden --no-heading -S --color never --files-with-matches "${p}" "${skill_dir}" && echo || true
  done
else
  for p in "${line_patterns[@]}"; do
    grep -RIn --exclude-dir=.git -E "${p}" "${skill_dir}" && echo || true
  done

  # For secret-like patterns, avoid printing matching lines (which may contain values).
  for p in "${sensitive_patterns[@]}"; do
    grep -RIl --exclude-dir=.git -E "${p}" "${skill_dir}" && echo || true
  done
fi
