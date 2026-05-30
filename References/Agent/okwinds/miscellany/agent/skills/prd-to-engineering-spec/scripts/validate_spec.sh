#!/usr/bin/env bash
set -euo pipefail

# validate_spec.sh - Validate engineering spec completeness
# Usage: validate_spec.sh <spec_root>

usage() {
  cat <<'EOF'
Usage:
  validate_spec.sh <spec_root>

Validates engineering specification completeness:
  - Required files and directories present
  - No TODO/TBD placeholders remaining
  - Content depth checks (not just file existence)
  - Cross-references valid
  - Security, operations, and replicability checks

Notes:
  - Designed to work on macOS (BSD userland) and Linux.
  - Avoids GNU-only grep flags (e.g. --include).
EOF
}

if [[ $# -lt 1 ]]; then usage; exit 1; fi
spec_root="$1"
if [[ ! -d "$spec_root" ]]; then echo "Error: Not found: $spec_root" >&2; exit 1; fi
spec_root="$(cd "$spec_root" && pwd)"

echo "# Engineering Spec Validation Report"
echo "spec: $spec_root"
echo "generated: $(date -u +"%Y-%m-%dT%H:%M:%SZ")"
echo ""

errors=0; warnings=0

error() { echo "❌ ERROR: $1"; ((errors++)) || true; }
warning() { echo "⚠️  WARNING: $1"; ((warnings++)) || true; }
ok() { echo "✅ $1"; }
info() { echo "ℹ️  $1"; }

md_files() {
  find "$spec_root" -type f -name "*.md" 2>/dev/null
}

# --- 1. Required Files ---
echo "## 1. Required Files"
echo ""

required_files=(
  "00_Overview/SUMMARY.md"
  "00_Overview/REQUIREMENTS_MATRIX.md"
  "00_Overview/DECISION_LOG.md"
  "00_Overview/TECH_STACK.md"
  "01_Requirements/USER_STORIES.md"
  "01_Requirements/FUNCTIONAL_REQS.md"
  "01_Requirements/NON_FUNCTIONAL_REQS.md"
  "02_Technical_Design/ARCHITECTURE.md"
  "02_Technical_Design/DATA_MODEL.md"
  "02_Technical_Design/API_SPEC.md"
  "03_Security/AUTH_DESIGN.md"
  "04_Operations/DEPLOYMENT.md"
  "04_Operations/CONFIGURATION.md"
  "04_Operations/MONITORING.md"
  "05_Testing/TEST_PLAN.md"
  "06_Implementation/TASK_BREAKDOWN.md"
  "SPEC_INDEX.md"
)

optional_files=(
  "02_Technical_Design/BUSINESS_LOGIC.md"
  "02_Technical_Design/AI_COMPONENTS.md"
  "03_Security/DATA_SECURITY.md"
  "03_Security/AUDIT_SPEC.md"
  "04_Operations/RUNBOOK.md"
  "05_Testing/ACCEPTANCE_TESTS.md"
  "06_Implementation/MILESTONES.md"
  "06_Implementation/RISKS.md"
  "06_Implementation/MIGRATION.md"
)

for file in "${required_files[@]}"; do
  if [[ -f "$spec_root/$file" ]]; then ok "Found: $file"
  else error "Missing required: $file"; fi
done
for file in "${optional_files[@]}"; do
  if [[ -f "$spec_root/$file" ]]; then ok "Found (optional): $file"
  else info "Missing optional: $file"; fi
done
echo ""

# --- 2. Placeholder Check ---
echo "## 2. Placeholder Check"
echo ""

placeholder_patterns='TODO|TBD|FIXME|\[XXX\]|\[TBD\]|\[TODO\]|\[PLACEHOLDER\]|\[INSERT\]|\[FILL\]'
placeholder_files=""

if md_files | head -n 1 | grep -q .; then
  # shellcheck disable=SC2046
  placeholder_files=$(grep -l -E "$placeholder_patterns" $(md_files) 2>/dev/null || true)
fi

if [[ -n "$placeholder_files" ]]; then
  while IFS= read -r file; do
    [[ -z "$file" ]] && continue
    count=$(grep -c -E "$placeholder_patterns" "$file" 2>/dev/null || echo 0)
    warning "${file#$spec_root/} ($count placeholders)"
  done <<< "$placeholder_files"
else
  ok "No placeholders found"
fi
echo ""

# --- 2b. Secret/PII Smell Check (heuristic) ---
echo "## 2b. Secret/PII Smell Check"
echo ""

secret_patterns='-----BEGIN ([A-Z ]+ )?PRIVATE KEY-----|ghp_[A-Za-z0-9]{36}|sk-[A-Za-z0-9]{20,}|AKIA[0-9A-Z]{16}|xox[baprs]-[A-Za-z0-9-]{10,}'
secret_files=""
if md_files | head -n 1 | grep -q .; then
  # shellcheck disable=SC2046
  secret_files=$(grep -l -E "$secret_patterns" $(md_files) 2>/dev/null || true)
fi

if [[ -n "$secret_files" ]]; then
  while IFS= read -r file; do
    [[ -z "$file" ]] && continue
    warning "Potential secret/credential pattern found in: ${file#$spec_root/}"
  done <<< "$secret_files"
else
  ok "No obvious secret patterns found"
fi
echo ""

# --- 3. Content Depth Checks ---
echo "## 3. Content Depth"
echo ""

check_min_lines() {
  local file="$1" min_lines="$2" label="$3"
  if [[ -f "$spec_root/$file" ]]; then
    local lines
    lines=$(wc -l < "$spec_root/$file")
    if [[ $lines -lt $min_lines ]]; then
      warning "$label: Only $lines lines (expected >$min_lines). May lack sufficient detail."
    else
      ok "$label: $lines lines"
    fi
  fi
}

check_min_lines "02_Technical_Design/DATA_MODEL.md" 30 "Data Model"
check_min_lines "02_Technical_Design/API_SPEC.md" 50 "API Spec"
check_min_lines "03_Security/AUTH_DESIGN.md" 20 "Auth Design"
check_min_lines "04_Operations/CONFIGURATION.md" 15 "Configuration"
check_min_lines "04_Operations/MONITORING.md" 15 "Monitoring"
check_min_lines "05_Testing/TEST_PLAN.md" 30 "Test Plan"
check_min_lines "06_Implementation/TASK_BREAKDOWN.md" 20 "Task Breakdown"

# Check data model has field definitions (tables)
if [[ -f "$spec_root/02_Technical_Design/DATA_MODEL.md" ]]; then
  table_count=$(grep -c "|.*|.*|.*|" "$spec_root/02_Technical_Design/DATA_MODEL.md" 2>/dev/null || echo 0)
  if [[ $table_count -lt 5 ]]; then
    warning "Data Model has few table rows ($table_count). May lack field definitions."
  fi
fi

# Check API spec has endpoints
if [[ -f "$spec_root/02_Technical_Design/API_SPEC.md" ]]; then
  endpoint_count=$(grep -c -E "^####? (GET|POST|PUT|PATCH|DELETE) " "$spec_root/02_Technical_Design/API_SPEC.md" 2>/dev/null || echo 0)
  info "API endpoints found: $endpoint_count"
  if [[ $endpoint_count -eq 0 ]]; then
    warning "No API endpoints detected. Check formatting (expected: '### GET /path')."
  fi
fi
echo ""

# --- 4. Security Checks ---
echo "## 4. Security"
echo ""

if [[ -d "$spec_root/03_Security" ]]; then
  ok "Security directory exists"

  if [[ -f "$spec_root/03_Security/AUTH_DESIGN.md" ]]; then
    for keyword in "authentication" "authorization" "token" "permission"; do
      if grep -q -i "$keyword" "$spec_root/03_Security/AUTH_DESIGN.md" 2>/dev/null; then
        ok "Auth design mentions: $keyword"
      else
        warning "Auth design may be missing: $keyword"
      fi
    done
  fi
else
  error "Missing 03_Security/ directory — security architecture not specified"
fi
echo ""

# --- 5. Operations Checks ---
echo "## 5. Operations"
echo ""

if [[ -d "$spec_root/04_Operations" ]]; then
  ok "Operations directory exists"

  # Check configuration has env var table
  if [[ -f "$spec_root/04_Operations/CONFIGURATION.md" ]]; then
    env_vars=$(grep -c -E "^\|.*\|.*\|.*\|" "$spec_root/04_Operations/CONFIGURATION.md" 2>/dev/null || echo 0)
    if [[ $env_vars -lt 3 ]]; then
      warning "Configuration may lack env var definitions (found $env_vars table rows)"
    else
      ok "Configuration has $env_vars table rows"
    fi
  fi

  # Check monitoring has alert definitions
  if [[ -f "$spec_root/04_Operations/MONITORING.md" ]]; then
    if grep -q -i "alert\|threshold" "$spec_root/04_Operations/MONITORING.md" 2>/dev/null; then
      ok "Monitoring includes alert definitions"
    else
      warning "Monitoring may be missing alert thresholds"
    fi
  fi
else
  error "Missing 04_Operations/ directory — deployment/monitoring not specified"
fi
echo ""

# --- 6. Test Traceability ---
echo "## 6. Test Traceability"
echo ""

if [[ -f "$spec_root/00_Overview/REQUIREMENTS_MATRIX.md" ]]; then
  matrix_file="$spec_root/00_Overview/REQUIREMENTS_MATRIX.md"
  if grep -q -i -E "test|UT-|IT-|E2E-" "$matrix_file" 2>/dev/null; then
    ok "Requirements matrix includes test references"
  else
    warning "Requirements matrix may lack test traceability"
  fi

  empty_refs=0
  if grep -q -E "\| *- *\| *- *\|" "$matrix_file" 2>/dev/null; then
    empty_refs=$(grep -c -E "\| *- *\| *- *\|" "$matrix_file" 2>/dev/null || echo 0)
  fi
  if [[ $empty_refs -gt 0 ]]; then
    warning "$empty_refs requirements may have no test coverage"
  fi
else
  error "Missing requirements traceability matrix"
fi
echo ""

# --- 7. Cross-Reference Validation ---
echo "## 7. Cross-References"
echo ""

broken_links=0
while IFS= read -r -d '' file; do
  links=$(grep -o -E '\[.*\]\([^)]+\.md[^)]*\)' "$file" 2>/dev/null | grep -o -E '\([^)]+\)' | tr -d '()' || true)
  for link in $links; do
    dir=$(dirname "$file")
    if [[ ! -f "$dir/$link" ]] && [[ ! -f "$spec_root/$link" ]]; then
      warning "Broken link in ${file#$spec_root/}: $link"
      ((broken_links++)) || true
    fi
  done
done < <(find "$spec_root" -name "*.md" -print0 2>/dev/null)

if [[ $broken_links -eq 0 ]]; then ok "No broken links"; fi
echo ""

# --- 8. Replicability Check ---
echo "## 8. Replicability"
echo ""

replicability_keywords=(
  "version:Tech Stack should pin versions"
  "dependency:Dependencies should be listed"
  "environment:Environment setup should be documented"
  "docker\|container:Container/deployment spec should exist"
)

for entry in "${replicability_keywords[@]}"; do
  keyword="${entry%%:*}"
  desc="${entry##*:}"
  found=""
  if md_files | head -n 1 | grep -q .; then
    # shellcheck disable=SC2046
    found=$(grep -l -i -E "$keyword" $(md_files) 2>/dev/null | head -1 || true)
  fi

  if [[ -n "$found" ]]; then
    ok "$desc (found in ${found#$spec_root/})"
  else
    warning "$desc — keyword '$keyword' not found in any spec file"
  fi
done
echo ""

# --- Summary ---
echo "## Summary"
echo ""
echo "Errors: $errors"
echo "Warnings: $warnings"
echo ""

if [[ $errors -gt 0 ]]; then
  echo "❌ FAILED — fix $errors errors before proceeding"
  exit 1
elif [[ $warnings -gt 5 ]]; then
  echo "⚠️  PASSED with $warnings warnings — significant review needed"
  exit 0
elif [[ $warnings -gt 0 ]]; then
  echo "⚠️  PASSED with $warnings warnings — minor review needed"
  exit 0
else
  echo "✅ PASSED — spec appears complete"
  exit 0
fi
