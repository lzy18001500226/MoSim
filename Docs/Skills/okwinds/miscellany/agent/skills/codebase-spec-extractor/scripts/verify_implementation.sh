#!/usr/bin/env bash
set -euo pipefail

# verify_implementation.sh - Validate that spec elements map to code via Source anchors
# Usage: verify_implementation.sh <spec_root> <project_root>
#
# This script is intentionally conservative:
# - It verifies that referenced files exist.
# - Optionally verifies a symbol exists (heuristic text match) if you use #Symbol.
# - Optionally verifies a line exists if you use :<line>.
#
# Recommended Source formats inside Markdown spec files:
#   Source: path/to/file.ts
#   Source: path/to/file.ts#MyFunction
#   Source: path/to/file.py:123
#   Source: path/to/file.go#TypeName.Method
#
# Notes:
# - This is NOT a semantic parser. Symbol checks are best-effort.
# - Paths are resolved relative to <project_root> unless absolute.

usage() {
  cat <<'EOF'
Usage:
  verify_implementation.sh <spec_root> <project_root>

Finds "Source:" anchors in spec Markdown and validates they point to existing code.

Anchor formats supported:
  Source: relative/or/absolute/path.ext
  Source: path.ext#SymbolName          (best-effort text match in file)
  Source: path.ext:123                (checks file has at least 123 lines)
  Source: path.ext:123#SymbolName     (does both checks)

Exit codes:
  0 - all anchors validated
  1 - one or more anchors invalid/missing
  2 - usage error
EOF
}

if [[ $# -lt 2 ]]; then
  usage
  exit 2
fi

spec_root="$1"
project_root="$2"

if [[ ! -d "$spec_root" ]]; then
  echo "Error: Spec directory not found: $spec_root" >&2
  exit 2
fi

if [[ ! -d "$project_root" ]]; then
  echo "Error: Project directory not found: $project_root" >&2
  exit 2
fi

spec_root="$(cd "$spec_root" && pwd)"
project_root="$(cd "$project_root" && pwd)"

extract_sources() {
  local md_file="$1"

  # Match:
  #   Source: ...
  #   - Source: ...
  # Accept optional backticks around the value.
  #
  # shellcheck disable=SC2016
  sed -n -E 's/^[[:space:]]*(-[[:space:]]*)?Source:[[:space:]]*`?([^`]+)`?[[:space:]]*$/\2/p' "$md_file" \
    | sed -e 's/[[:space:]]*$//' -e 's/^[[:space:]]*//'
}

escape_rg_literal() {
  # Escape for ripgrep regex literal matching.
  # We only need to escape regex metacharacters.
  printf "%s" "$1" | sed -e 's/[.[\*^$()+?{|\\]/\\&/g'
}

resolve_path() {
  local raw_path="$1"
  if [[ "$raw_path" = /* ]]; then
    echo "$raw_path"
  else
    echo "$project_root/$raw_path"
  fi
}

echo "# Spec → Code Assist Report (Source Anchors)"
echo ""
echo "Note: This is a heuristic helper to find broken links and likely gaps."
echo "It does not prove completeness or behavioral equivalence."
echo "spec: $spec_root"
echo "project: $project_root"
echo "generated: $(date -u +"%Y-%m-%dT%H:%M:%SZ")"
echo ""

had_fail=0
total=0
ok=0

while IFS= read -r md; do
  while IFS= read -r src; do
    [[ -z "$src" ]] && continue
    total=$((total + 1))

    raw="$src"

    # Split on #symbol (optional)
    file_and_line="${raw%%#*}"
    symbol=""
    if [[ "$raw" == *"#"* ]]; then
      symbol="${raw#*#}"
    fi

    # Split optional :<line> at end of file portion
    file_part="$file_and_line"
    line_part=""
    if [[ "$file_and_line" =~ ^(.+):([0-9]+)$ ]]; then
      file_part="${BASH_REMATCH[1]}"
      line_part="${BASH_REMATCH[2]}"
    fi

    abs_file="$(resolve_path "$file_part")"

    echo "## Anchor"
    echo "- Source: \`$raw\`"
    echo "- Resolved file: \`$abs_file\`"

    anchor_ok=1

    if [[ ! -f "$abs_file" ]]; then
      echo "- Status: FAIL (file not found)"
      echo ""
      had_fail=1
      continue
    fi

    if [[ -n "$line_part" ]]; then
      line_text="$(sed -n "${line_part}p" "$abs_file" || true)"
      if [[ -z "$line_text" ]]; then
        echo "- Line check: FAIL (no such line: $line_part)"
        had_fail=1
        anchor_ok=0
      else
        echo "- Line check: OK ($line_part)"
      fi
    fi

    if [[ -n "$symbol" ]]; then
      if command -v rg >/dev/null 2>&1; then
        symbol_pat="$(escape_rg_literal "$symbol")"
        if rg -n -S --no-messages "$symbol_pat" "$abs_file" >/dev/null 2>&1; then
          echo "- Symbol check: OK (\`$symbol\` found)"
        else
          echo "- Symbol check: FAIL (\`$symbol\` not found; heuristic text match)"
          had_fail=1
          anchor_ok=0
        fi
      else
        if grep -n -F "$symbol" "$abs_file" >/dev/null 2>&1; then
          echo "- Symbol check: OK (\`$symbol\` found)"
        else
          echo "- Symbol check: FAIL (\`$symbol\` not found; heuristic text match)"
          had_fail=1
          anchor_ok=0
        fi
      fi
    fi

    if [[ $anchor_ok -eq 1 ]]; then
      echo "- Status: OK"
      ok=$((ok + 1))
    else
      echo "- Status: FAIL (one or more checks failed)"
    fi
    echo ""
  done < <(extract_sources "$md")
done < <(find "$spec_root" -type f -name "*.md" 2>/dev/null | sort)

echo "## Summary"
echo "- Anchors found: $total"
echo "- Anchors validated: $ok"

if [[ $had_fail -ne 0 ]]; then
  echo "- Result: FAIL (one or more anchors invalid)"
  exit 1
fi

echo "- Result: OK"
