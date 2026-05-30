#!/usr/bin/env bash
set -euo pipefail

# verify_coverage.sh - Check spec completeness against codebase
# Usage: verify_coverage.sh <project_root> <spec_root>

usage() {
  cat <<'EOF'
Usage:
  verify_coverage.sh <project_root> <spec_root>

Performs bidirectional verification:
  1. Forward: Are all code elements documented in the spec?
  2. Spec → Code: Do all spec elements have corresponding code?

Outputs a coverage report with gaps identified.
EOF
}

if [[ $# -lt 2 ]]; then
  usage
  exit 1
fi

project_root="$1"
spec_root="$2"

if [[ ! -d "$project_root" ]]; then
  echo "Error: Project directory not found: $project_root" >&2
  exit 1
fi

if [[ ! -d "$spec_root" ]]; then
  echo "Error: Spec directory not found: $spec_root" >&2
  exit 1
fi

project_root="$(cd "$project_root" && pwd)"
spec_root="$(cd "$spec_root" && pwd)"

echo "# Spec Coverage Verification Report"
echo "project: $project_root"
echo "spec: $spec_root"
echo "generated: $(date -u +"%Y-%m-%dT%H:%M:%SZ")"
echo ""

# Ignores
ignores="node_modules|\.git|__pycache__|\.next|dist|build|coverage|\.cache|vendor|venv|\.venv"

# Count functions/methods in code
echo "## Code Analysis"
echo ""

count_code_elements() {
  local pattern="$1"
  local desc="$2"
  local count
  count=$(grep -r -E "$pattern" "$project_root" --include="*.ts" --include="*.js" --include="*.py" --include="*.go" 2>/dev/null | grep -v -E "$ignores" | wc -l | tr -d ' ')
  echo "- $desc: $count"
}

echo "### Detected Code Elements"
count_code_elements "^(export )?(async )?function " "Functions (JS/TS)"
count_code_elements "^\s*(async )?def " "Functions (Python)"
count_code_elements "^func " "Functions (Go)"
count_code_elements "class [A-Z]" "Classes"
count_code_elements "@(Get|Post|Put|Delete|Patch|Controller|Injectable|Service)" "Decorators (NestJS/etc)"
count_code_elements "(app|router)\.(get|post|put|delete|patch)\(" "Route handlers"
echo ""

# Count spec elements
echo "## Spec Analysis"
echo ""

count_spec_elements() {
  local pattern="$1"
  local desc="$2"
  local count
  count=$(grep -r -E "$pattern" "$spec_root" --include="*.md" 2>/dev/null | wc -l | tr -d ' ')
  echo "- $desc: $count"
}

echo "### Documented Spec Elements"
count_spec_elements "^## (Entity|Function|Endpoint|Component|Rule|Workflow):" "Named elements"
count_spec_elements "^### (Purpose|Interface|Logic|Constraints)" "Detailed sections"
count_spec_elements "\| .+ \| .+ \|" "Table rows (fields/params/etc)"
count_spec_elements "^```" "Code blocks"
echo ""

# Check for common gaps
echo "## Gap Detection"
echo ""

echo "### Potential Undocumented Code"
echo ""
echo "Files with business logic patterns but no obvious spec reference:"
echo ""

# Find files that look important but might not be documented
find "$project_root" -type f \( -name "*.ts" -o -name "*.js" -o -name "*.py" -o -name "*.go" \) 2>/dev/null | \
  grep -v -E "$ignores" | \
  while read -r file; do
    basename_file=$(basename "$file" | sed 's/\.[^.]*$//')
    # Check if this file is mentioned in any spec
    if ! grep -r -q -i "$basename_file" "$spec_root" --include="*.md" 2>/dev/null; then
      # Only show files that look important (contain functions/classes)
      if grep -q -E "(function|class|def |func )" "$file" 2>/dev/null; then
        echo "- ${file#$project_root/}"
      fi
    fi
  done | head -30

echo ""
echo "(showing first 30 potentially undocumented files)"
echo ""

echo "### Spec Sections That May Need Verification"
echo ""
echo "Spec files with TODO/TBD/FIXME markers:"
echo ""
grep -r -l -E "(TODO|TBD|FIXME|\[.*\])" "$spec_root" --include="*.md" 2>/dev/null | \
  sed "s|^$spec_root/|- |" | head -20
echo ""

echo "### Completeness Checklist"
echo ""
echo "Verify these critical areas have coverage:"
echo ""

check_section() {
  local pattern="$1"
  local desc="$2"
  if grep -r -q -i "$pattern" "$spec_root" --include="*.md" 2>/dev/null; then
    echo "- [x] $desc"
  else
    echo "- [ ] $desc (NOT FOUND)"
  fi
}

check_section "environment" "Environment configuration"
check_section "entity\|model\|schema" "Data models"
check_section "endpoint\|api\|route" "API endpoints"
check_section "business rule\|rule:" "Business rules"
check_section "error\|exception" "Error handling"
check_section "test\|spec" "Test specifications"
check_section "authentication\|auth" "Authentication"
check_section "authorization\|permission" "Authorization"
echo ""

echo "## Summary"
echo ""
echo "This report identifies potential gaps between code and spec."
echo "Review each gap and either:"
echo "1. Add missing documentation to the spec"
echo "2. Confirm the code element is intentionally undocumented (and note why)"
echo ""
echo "Run this script periodically to maintain spec-code alignment."
