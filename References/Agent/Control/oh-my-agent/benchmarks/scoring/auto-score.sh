#!/usr/bin/env bash
# auto-score.sh — Automated scoring for AI coding harness benchmark
# Usage: ./auto-score.sh <project-dir> <harness-id> > auto-score-{harness}.json

set -uo pipefail

# ---------------------------------------------------------------------------
# Arguments
# ---------------------------------------------------------------------------
if [[ $# -lt 2 ]]; then
  echo "Usage: $0 <project-dir> <harness-id>" >&2
  exit 1
fi

PROJECT_DIR="$(cd "$1" 2>/dev/null && pwd)" || { echo "ERROR: '$1' is not a valid directory" >&2; exit 1; }
HARNESS_ID="$2"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CHECKLIST="$SCRIPT_DIR/checklist.json"
LOG_FILE="$PROJECT_DIR/auto-score.log"
TIMESTAMP="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"

if [[ ! -f "$CHECKLIST" ]]; then
  echo "ERROR: checklist.json not found at $CHECKLIST" >&2
  exit 1
fi

# ---------------------------------------------------------------------------
# Read max values from checklist.json
# ---------------------------------------------------------------------------
get_max() {
  local id="$1"
  jq -r --arg id "$id" \
    '.categories[].items[] | select(.id == $id) | .max' \
    "$CHECKLIST"
}

MAX_SETUP_NEXTJS="$(get_max setup-nextjs)"
MAX_SETUP_TAILWIND="$(get_max setup-tailwind)"
MAX_SETUP_R3F="$(get_max setup-r3f)"
MAX_SETUP_BUILD="$(get_max setup-build)"
MAX_AI_API="$(get_max ai-api)"
MAX_LINT_CLEAN="$(get_max lint-clean)"
MAX_TS_CLEAN="$(get_max ts-clean)"

# Tests are scored only when the prompt explicitly asked for them. Default off
# so prompts that don't mention tests don't penalize every harness equally.
PROMPT_REQUIRES_TESTS="$(jq -r '.meta["prompt-requires-tests"] // false' "$CHECKLIST")"
MAX_TEST_EXISTS="$(get_max test-exists)"
MAX_TEST_PASS="$(get_max test-pass)"
MAX_TEST_COVERAGE="$(get_max test-coverage)"

# ---------------------------------------------------------------------------
# Package manager detection — picks pnpm/yarn/bun/npm based on lockfile so
# pnpm-workspace projects are not scored against `npm install` failures.
# ---------------------------------------------------------------------------
detect_pm() {
  local dir="$1"
  if [[ -f "$dir/pnpm-lock.yaml" || -f "$dir/pnpm-workspace.yaml" ]]; then
    echo pnpm
  elif [[ -f "$dir/yarn.lock" ]]; then
    echo yarn
  elif [[ -f "$dir/bun.lock" || -f "$dir/bun.lockb" ]]; then
    echo bun
  else
    echo npm
  fi
}

pm_install_cmd() {
  case "$1" in
    pnpm) echo "pnpm install --silent" ;;
    yarn) echo "yarn install --silent" ;;
    bun)  echo "bun install --silent" ;;
    *)    echo "npm install --no-audit --no-fund --loglevel=error" ;;
  esac
}

pm_run_cmd() {
  local pm="$1" script="$2"
  case "$pm" in
    pnpm) echo "pnpm run $script" ;;
    yarn) echo "yarn $script" ;;
    bun)  echo "bun run $script" ;;
    *)    echo "npm run $script" ;;
  esac
}

pm_test_cmd() {
  local pm="$1" extra="$2"
  case "$pm" in
    pnpm) echo "pnpm test -- $extra" ;;
    yarn) echo "yarn test $extra" ;;
    bun)  echo "bun test $extra" ;;
    *)    echo "npm test -- $extra" ;;
  esac
}

# ---------------------------------------------------------------------------
# Logging helpers
# ---------------------------------------------------------------------------
log() {
  echo "[$(date -u +"%H:%M:%S")] $*" >> "$LOG_FILE"
}

# ---------------------------------------------------------------------------
# Result accumulation
# ---------------------------------------------------------------------------
declare -A PASS SCORE MAX EVIDENCE
ERRORS=()

set_result() {
  local id="$1" pass="$2" score="$3" max="$4" evidence="$5"
  PASS[$id]="$pass"
  SCORE[$id]="$score"
  MAX[$id]="$max"
  EVIDENCE[$id]="$evidence"
}

add_error() {
  ERRORS+=("$1")
}

# ---------------------------------------------------------------------------
# Early exit: no package.json
# ---------------------------------------------------------------------------
PKG_JSON="$PROJECT_DIR/package.json"

if [[ ! -f "$PKG_JSON" ]]; then
  log "ERROR: package.json not found in $PROJECT_DIR"
  for id in setup-nextjs setup-tailwind setup-r3f setup-build ai-api lint-clean ts-clean test-exists test-pass test-coverage; do
    max_var="MAX_$(echo "$id" | tr '[:lower:]-' '[:upper:]_')"
    set_result "$id" false 0 "${!max_var}" "package.json not found"
  done
  add_error "package.json not found in $PROJECT_DIR — all auto-checks scored 0"
else

# Detected package manager drives every install/run/test command below.
PM="$(detect_pm "$PROJECT_DIR")"
log "Detected package manager: $PM"

# ---------------------------------------------------------------------------
# CHECK: setup-nextjs
# ---------------------------------------------------------------------------
log "Check: setup-nextjs"
next_version="$(jq -r '(.dependencies // {}) * (.devDependencies // {}) | .["next"] // empty' "$PKG_JSON" 2>>"$LOG_FILE")"
if [[ -n "$next_version" ]]; then
  set_result "setup-nextjs" true "$MAX_SETUP_NEXTJS" "$MAX_SETUP_NEXTJS" "next@${next_version}"
  log "setup-nextjs: PASS (next@${next_version})"
else
  set_result "setup-nextjs" false 0 "$MAX_SETUP_NEXTJS" "not found"
  log "setup-nextjs: FAIL"
fi

# ---------------------------------------------------------------------------
# CHECK: setup-tailwind
# ---------------------------------------------------------------------------
log "Check: setup-tailwind"
tailwind_version="$(jq -r '(.dependencies // {}) * (.devDependencies // {}) | .["tailwindcss"] // empty' "$PKG_JSON" 2>>"$LOG_FILE")"
if [[ -n "$tailwind_version" ]]; then
  set_result "setup-tailwind" true "$MAX_SETUP_TAILWIND" "$MAX_SETUP_TAILWIND" "tailwindcss@${tailwind_version}"
  log "setup-tailwind: PASS (tailwindcss@${tailwind_version})"
else
  set_result "setup-tailwind" false 0 "$MAX_SETUP_TAILWIND" "not found"
  log "setup-tailwind: FAIL"
fi

# ---------------------------------------------------------------------------
# CHECK: setup-r3f
# ---------------------------------------------------------------------------
log "Check: setup-r3f"
r3f_version="$(jq -r '(.dependencies // {}) * (.devDependencies // {}) | .["@react-three/fiber"] // empty' "$PKG_JSON" 2>>"$LOG_FILE")"
drei_version="$(jq -r '(.dependencies // {}) * (.devDependencies // {}) | .["@react-three/drei"] // empty' "$PKG_JSON" 2>>"$LOG_FILE")"
if [[ -n "$r3f_version" && -n "$drei_version" ]]; then
  set_result "setup-r3f" true "$MAX_SETUP_R3F" "$MAX_SETUP_R3F" "@react-three/fiber@${r3f_version} @react-three/drei@${drei_version}"
  log "setup-r3f: PASS"
else
  missing=""
  [[ -z "$r3f_version" ]]  && missing="@react-three/fiber"
  [[ -z "$drei_version" ]] && missing="${missing:+$missing, }@react-three/drei"
  set_result "setup-r3f" false 0 "$MAX_SETUP_R3F" "missing: $missing"
  log "setup-r3f: FAIL (missing: $missing)"
fi

# ---------------------------------------------------------------------------
# CHECK: setup-build
# ---------------------------------------------------------------------------
log "Check: setup-build"
BUILD_START="$(date +%s)"
INSTALL_CMD="$(pm_install_cmd "$PM")"
BUILD_CMD="$(pm_run_cmd "$PM" build)"
log "  install: $INSTALL_CMD"
log "  build:   $BUILD_CMD"
build_output="$(
  timeout 300 bash -c "cd $(printf '%q' "$PROJECT_DIR") && $INSTALL_CMD && $BUILD_CMD" \
    >>"$LOG_FILE" 2>>"$LOG_FILE"
  echo $?
)"
build_exit="${build_output##*$'\n'}"
BUILD_END="$(date +%s)"
BUILD_ELAPSED=$(( BUILD_END - BUILD_START ))

if [[ "$build_exit" == "0" ]]; then
  set_result "setup-build" true "$MAX_SETUP_BUILD" "$MAX_SETUP_BUILD" "exit 0 in ${BUILD_ELAPSED}s"
  log "setup-build: PASS (${BUILD_ELAPSED}s)"
elif [[ "$build_exit" == "124" ]]; then
  set_result "setup-build" false 0 "$MAX_SETUP_BUILD" "timeout after 300s"
  add_error "setup-build: timed out after 300s"
  log "setup-build: TIMEOUT"
else
  set_result "setup-build" false 0 "$MAX_SETUP_BUILD" "exit ${build_exit} in ${BUILD_ELAPSED}s"
  log "setup-build: FAIL (exit $build_exit)"
fi

# ---------------------------------------------------------------------------
# CHECK: ai-api  — three-state evaluation
#   PASS_FULL    (max):     real LLM SDK import + env-var-based config
#   PASS_PARTIAL (max/2):   no SDK, BUT explicit deferred-stub markers
#                           (e.g., "MVP", "TODO", "replace with API",
#                           "without API dependency", "mock") AND a working
#                           local AI substitute (a function generating
#                           non-trivial responses). Rewards graceful
#                           degradation when no API key is provided.
#   FAIL         (0):       neither
# ---------------------------------------------------------------------------
log "Check: ai-api"
SRC_DIR="$PROJECT_DIR/src"
PARTIAL_AI=$(awk -v m="$MAX_AI_API" 'BEGIN{printf "%.2f", m/2}')
if [[ -d "$SRC_DIR" ]]; then
  # Recognize three integration styles:
  #   1. SDK import (`from "openai"`, `@anthropic-ai/sdk`, `@google/genai`)
  #   2. Raw fetch to provider endpoint (`api.openai.com`, `api.anthropic.com`,
  #      `generativelanguage.googleapis.com`)
  #   3. Hosted provider via OpenAI-compatible URL
  ai_full_match="$(timeout 60 grep -rE \
    "(from ['\"]openai)|(from ['\"]@anthropic-ai/sdk)|(from ['\"]@google/genai)|(require\(['\"]openai)|(require\(['\"]@anthropic-ai/sdk)|(api\.openai\.com)|(api\.anthropic\.com)|(generativelanguage\.googleapis\.com)" \
    "$SRC_DIR" --include="*.ts" --include="*.tsx" --include="*.js" --include="*.jsx" -l 2>>"$LOG_FILE" | head -1)"
  has_env_ref="$(timeout 60 grep -rE \
    "(OPENAI_API_KEY)|(ANTHROPIC_API_KEY)|(GEMINI_API_KEY)|(GOOGLE_API_KEY)|(process\.env\.[A-Z_]*API[A-Z_]*KEY)" \
    "$SRC_DIR" --include="*.ts" --include="*.tsx" --include="*.js" --include="*.jsx" -l 2>>"$LOG_FILE" | head -1)"

  if [[ -n "$ai_full_match" && -n "$has_env_ref" ]]; then
    ai_match_rel="${ai_full_match#$PROJECT_DIR/}"
    set_result "ai-api" true "$MAX_AI_API" "$MAX_AI_API" "real SDK + env config in $ai_match_rel"
    log "ai-api: PASS_FULL ($ai_match_rel)"
  elif [[ -n "$ai_full_match" ]]; then
    # SDK imported but no env-var config — likely hardcoded or broken
    ai_match_rel="${ai_full_match#$PROJECT_DIR/}"
    set_result "ai-api" true "$PARTIAL_AI" "$MAX_AI_API" "SDK imported but no API-key env config in $ai_match_rel"
    log "ai-api: PASS_PARTIAL ($ai_match_rel — missing env config)"
  else
    # No SDK — check for a deferred-stub pattern (intentional graceful fallback)
    deferred_marker="$(timeout 60 grep -rE -i \
      "(replace.*with.*API|TODO.*API|MVP[: ].*(local|without|mock)|without.*API.*dependency|mock.*OpenAI|mock.*LLM|integrate.*OpenAI.*later|local.*responses.*without)" \
      "$SRC_DIR" --include="*.ts" --include="*.tsx" --include="*.js" --include="*.jsx" -l 2>>"$LOG_FILE" | head -1)"
    has_substitute="$(timeout 60 grep -rE \
      "(generateResponse|aiResponse|companion|getRandomPrompt|whatif|reflect)" \
      "$SRC_DIR" --include="*.ts" --include="*.tsx" --include="*.js" --include="*.jsx" -l 2>>"$LOG_FILE" | head -1)"

    if [[ -n "$deferred_marker" && -n "$has_substitute" ]]; then
      marker_rel="${deferred_marker#$PROJECT_DIR/}"
      set_result "ai-api" true "$PARTIAL_AI" "$MAX_AI_API" "deferred stub with local substitute ($marker_rel)"
      log "ai-api: PASS_PARTIAL (deferred stub at $marker_rel)"
    else
      set_result "ai-api" false 0 "$MAX_AI_API" "no AI integration or deferred stub"
      log "ai-api: FAIL"
    fi
  fi
else
  set_result "ai-api" false 0 "$MAX_AI_API" "src/ directory not found"
  log "ai-api: FAIL (no src/ directory)"
fi

# ---------------------------------------------------------------------------
# CHECK: lint-clean — `<pm> run lint` exits 0
# ---------------------------------------------------------------------------
log "Check: lint-clean"
has_lint_script="$(jq -r '.scripts.lint // empty' "$PKG_JSON" 2>>"$LOG_FILE")"
if [[ -z "$has_lint_script" ]]; then
  set_result "lint-clean" false 0 "$MAX_LINT_CLEAN" "no lint script in package.json"
  log "lint-clean: SKIP (no script)"
else
  # Detect a deprecated `next lint` setup that prompts interactively in
  # Next.js 16+. We can't reliably score it here without an eslint config,
  # so mark n/a (max=0) instead of penalizing.
  if [[ "$has_lint_script" == "next lint" ]]; then
    has_eslint_cfg=false
    for f in eslint.config.mjs eslint.config.js eslint.config.cjs eslint.config.ts .eslintrc.json .eslintrc.js .eslintrc.cjs; do
      [[ -f "$PROJECT_DIR/$f" ]] && has_eslint_cfg=true && break
    done
    if [[ "$has_eslint_cfg" == false ]]; then
      set_result "lint-clean" true 0 0 "n/a (deprecated 'next lint' without eslint config)"
      log "lint-clean: SKIP (next lint deprecated, no eslint config)"
      LINT_HANDLED=true
    fi
  fi

  if [[ "${LINT_HANDLED:-false}" != true ]]; then
    LINT_CMD="$(pm_run_cmd "$PM" lint)"
    log "  cmd: $LINT_CMD"
    # Close stdin so any prompt in the lint script fails fast instead of hanging
    timeout 120 bash -c "cd $(printf '%q' "$PROJECT_DIR") && $LINT_CMD < /dev/null" \
      >>"$LOG_FILE" 2>>"$LOG_FILE"
    lint_exit=$?
    if [[ $lint_exit -eq 0 ]]; then
      set_result "lint-clean" true "$MAX_LINT_CLEAN" "$MAX_LINT_CLEAN" "exit 0"
      log "lint-clean: PASS"
    elif [[ $lint_exit -eq 124 ]]; then
      set_result "lint-clean" false 0 "$MAX_LINT_CLEAN" "timeout after 120s"
      log "lint-clean: TIMEOUT"
    else
      set_result "lint-clean" false 0 "$MAX_LINT_CLEAN" "exit $lint_exit"
      log "lint-clean: FAIL ($lint_exit)"
    fi
  fi
fi

# ---------------------------------------------------------------------------
# CHECK: ts-clean — `tsc --noEmit` exits 0 (only when tsconfig.json exists)
# ---------------------------------------------------------------------------
log "Check: ts-clean"
if [[ ! -f "$PROJECT_DIR/tsconfig.json" ]]; then
  set_result "ts-clean" false 0 "$MAX_TS_CLEAN" "no tsconfig.json"
  log "ts-clean: SKIP (no tsconfig)"
else
  # Use locally-installed tsc via npx; bun and pnpm both expose it through PATH
  # after install. Falls back to global tsc if local not installed.
  TSC_CMD="npx --no-install tsc --noEmit"
  case "$PM" in
    bun)  TSC_CMD="bunx tsc --noEmit" ;;
    pnpm) TSC_CMD="pnpm exec tsc --noEmit" ;;
    yarn) TSC_CMD="yarn tsc --noEmit" ;;
  esac
  log "  cmd: $TSC_CMD"
  timeout 180 bash -c "cd $(printf '%q' "$PROJECT_DIR") && $TSC_CMD" \
    >>"$LOG_FILE" 2>>"$LOG_FILE"
  tsc_exit=$?
  if [[ $tsc_exit -eq 0 ]]; then
    set_result "ts-clean" true "$MAX_TS_CLEAN" "$MAX_TS_CLEAN" "exit 0"
    log "ts-clean: PASS"
  elif [[ $tsc_exit -eq 124 ]]; then
    set_result "ts-clean" false 0 "$MAX_TS_CLEAN" "timeout after 180s"
    log "ts-clean: TIMEOUT"
  else
    set_result "ts-clean" false 0 "$MAX_TS_CLEAN" "exit $tsc_exit"
    log "ts-clean: FAIL ($tsc_exit)"
  fi
fi

# ---------------------------------------------------------------------------
# Test checks — only scored when the prompt explicitly asked for tests.
# When PROMPT_REQUIRES_TESTS=false, all three are recorded as "n/a (not
# requested)" with score=0 and max=0 so they don't penalize harnesses that
# correctly skipped writing tests for a non-test prompt.
# ---------------------------------------------------------------------------
if [[ "$PROMPT_REQUIRES_TESTS" != "true" ]]; then
  log "Tests: SKIPPED — prompt does not request tests"
  set_result "test-exists"   true 0 0 "n/a (prompt did not request tests)"
  set_result "test-pass"     true 0 0 "n/a (prompt did not request tests)"
  set_result "test-coverage" true 0 0 "n/a (prompt did not request tests)"
else

# ---------------------------------------------------------------------------
# CHECK: test-exists
# ---------------------------------------------------------------------------
log "Check: test-exists"
test_files="$(timeout 300 find "$PROJECT_DIR" \
  \( -name "*.test.*" -o -name "*.spec.*" \) \
  -not -path "*/node_modules/*" \
  2>>"$LOG_FILE")"
find_exit=$?

if [[ $find_exit -eq 124 ]]; then
  set_result "test-exists" false 0 "$MAX_TEST_EXISTS" "timeout after 300s"
  add_error "test-exists: find timed out after 300s"
  log "test-exists: TIMEOUT"
else
  test_count=0
  if [[ -n "$test_files" ]]; then
    test_count="$(echo "$test_files" | wc -l | tr -d ' ')"
  fi
  if [[ "$test_count" -gt 0 ]]; then
    set_result "test-exists" true "$MAX_TEST_EXISTS" "$MAX_TEST_EXISTS" "${test_count} test file(s)"
    log "test-exists: PASS ($test_count files)"
  else
    set_result "test-exists" false 0 "$MAX_TEST_EXISTS" "0 test files found"
    log "test-exists: FAIL"
  fi
fi

# ---------------------------------------------------------------------------
# CHECK: test-pass
# ---------------------------------------------------------------------------
log "Check: test-pass"
TEST_START="$(date +%s)"
TEST_CMD="$(pm_test_cmd "$PM" "--passWithNoTests")"
log "  cmd: $TEST_CMD"
timeout 300 bash -c "cd $(printf '%q' "$PROJECT_DIR") && $TEST_CMD" \
  >>"$LOG_FILE" 2>>"$LOG_FILE"
test_exit=$?
TEST_END="$(date +%s)"
TEST_ELAPSED=$(( TEST_END - TEST_START ))

if [[ $test_exit -eq 124 ]]; then
  set_result "test-pass" false 0 "$MAX_TEST_PASS" "timeout after 300s"
  add_error "test-pass: npm test timed out after 300s"
  log "test-pass: TIMEOUT"
elif [[ $test_exit -eq 0 ]]; then
  set_result "test-pass" true "$MAX_TEST_PASS" "$MAX_TEST_PASS" "exit 0 in ${TEST_ELAPSED}s"
  log "test-pass: PASS (${TEST_ELAPSED}s)"
else
  set_result "test-pass" false 0 "$MAX_TEST_PASS" "exit ${test_exit} in ${TEST_ELAPSED}s"
  log "test-pass: FAIL (exit $test_exit)"
fi

# ---------------------------------------------------------------------------
# CHECK: test-coverage
# ---------------------------------------------------------------------------
log "Check: test-coverage"
COV_START="$(date +%s)"
COV_CMD="$(pm_test_cmd "$PM" "--coverage --passWithNoTests")"
log "  cmd: $COV_CMD"
cov_raw="$(timeout 300 bash -c "cd $(printf '%q' "$PROJECT_DIR") && $COV_CMD" \
  2>>"$LOG_FILE")"
cov_exit=$?
COV_END="$(date +%s)"
COV_ELAPSED=$(( COV_END - COV_START ))
log "coverage raw output length: ${#cov_raw}"

if [[ $cov_exit -eq 124 ]]; then
  set_result "test-coverage" false 0 "$MAX_TEST_COVERAGE" "timeout after 300s"
  add_error "test-coverage: npm test --coverage timed out after 300s"
  log "test-coverage: TIMEOUT"
elif [[ $cov_exit -ne 0 ]]; then
  set_result "test-coverage" false 0 "$MAX_TEST_COVERAGE" "exit ${cov_exit} — coverage run failed"
  log "test-coverage: FAIL (exit $cov_exit)"
else
  # Parse overall coverage percentage from output lines like:
  #   All files  |   67.34 |   50.00 |   80.00 |   67.34 |
  # or from json summary if present
  cov_pct=""

  # Try lcov-style text output first (vitest / jest --text reporter)
  cov_line="$(echo "$cov_raw" | grep -E "^All files\s*\|" | head -1)"
  if [[ -n "$cov_line" ]]; then
    cov_pct="$(echo "$cov_line" | awk -F'|' '{print $2}' | tr -d ' %')"
  fi

  # Fallback: look for "Statements" line from istanbul text table
  if [[ -z "$cov_pct" ]]; then
    cov_pct="$(echo "$cov_raw" | grep -E "Statements\s*:" | head -1 | grep -oE '[0-9]+\.[0-9]+' | head -1)"
  fi

  # Fallback: look for coverage-summary.json
  cov_summary="$PROJECT_DIR/coverage/coverage-summary.json"
  if [[ -z "$cov_pct" && -f "$cov_summary" ]]; then
    cov_pct="$(jq -r '.total.statements.pct // empty' "$cov_summary" 2>>"$LOG_FILE")"
  fi

  if [[ -n "$cov_pct" ]]; then
    # Strip trailing % if present, compare numerically
    cov_num="${cov_pct//%/}"
    cov_int="${cov_num%%.*}"
    if [[ "$cov_int" -gt 0 ]] 2>/dev/null; then
      set_result "test-coverage" true "$MAX_TEST_COVERAGE" "$MAX_TEST_COVERAGE" "${cov_num}%"
      log "test-coverage: PASS (${cov_num}%)"
    else
      set_result "test-coverage" false 0 "$MAX_TEST_COVERAGE" "coverage is 0%"
      log "test-coverage: FAIL (0%)"
    fi
  else
    # Could not parse coverage but command exited 0 — treat as > 0% if test-pass also passed
    if [[ "${PASS[test-pass]:-false}" == "true" ]]; then
      set_result "test-coverage" true "$MAX_TEST_COVERAGE" "$MAX_TEST_COVERAGE" "coverage output unparseable but exit 0"
      log "test-coverage: PASS (unparseable, inferred from exit 0)"
    else
      set_result "test-coverage" false 0 "$MAX_TEST_COVERAGE" "coverage output unparseable"
      log "test-coverage: FAIL (unparseable)"
    fi
  fi
fi

fi  # end of PROMPT_REQUIRES_TESTS block

fi  # end of package.json block

# ---------------------------------------------------------------------------
# Compute totals
# ---------------------------------------------------------------------------
AUTO_TOTAL=0
AUTO_MAX=0

for id in setup-nextjs setup-tailwind setup-r3f setup-build ai-api lint-clean ts-clean test-exists test-pass test-coverage; do
  AUTO_TOTAL="$(echo "$AUTO_TOTAL + ${SCORE[$id]:-0}" | bc)"
  AUTO_MAX="$(echo "$AUTO_MAX + ${MAX[$id]:-0}" | bc)"
done

# ---------------------------------------------------------------------------
# Build JSON output
# ---------------------------------------------------------------------------
build_check_json() {
  local id="$1"
  local pass="${PASS[$id]:-false}"
  local score="${SCORE[$id]:-0}"
  local max="${MAX[$id]:-0}"
  local evidence="${EVIDENCE[$id]:-unknown}"

  jq -n \
    --argjson pass "$pass" \
    --argjson score "$score" \
    --argjson max "$max" \
    --arg evidence "$evidence" \
    '{pass: $pass, score: $score, max: $max, evidence: $evidence}'
}

# Build errors JSON array
errors_json="$(printf '%s\n' "${ERRORS[@]+"${ERRORS[@]}"}" | jq -R . | jq -s .)"

jq -n \
  --arg harness "$HARNESS_ID" \
  --arg project_dir "$PROJECT_DIR" \
  --arg timestamp "$TIMESTAMP" \
  --arg pm "${PM:-unknown}" \
  --arg requires_tests "$PROMPT_REQUIRES_TESTS" \
  --argjson nextjs    "$(build_check_json setup-nextjs)" \
  --argjson tailwind  "$(build_check_json setup-tailwind)" \
  --argjson r3f       "$(build_check_json setup-r3f)" \
  --argjson build     "$(build_check_json setup-build)" \
  --argjson ai_api    "$(build_check_json ai-api)" \
  --argjson lint      "$(build_check_json lint-clean)" \
  --argjson ts        "$(build_check_json ts-clean)" \
  --argjson texists   "$(build_check_json test-exists)" \
  --argjson tpass     "$(build_check_json test-pass)" \
  --argjson tcoverage "$(build_check_json test-coverage)" \
  --argjson total "$AUTO_TOTAL" \
  --argjson max "$AUTO_MAX" \
  --argjson errors "$errors_json" \
  '{
    harness: $harness,
    project_dir: $project_dir,
    timestamp: $timestamp,
    package_manager: $pm,
    prompt_requires_tests: ($requires_tests == "true"),
    checks: {
      "setup-nextjs":   $nextjs,
      "setup-tailwind": $tailwind,
      "setup-r3f":      $r3f,
      "setup-build":    $build,
      "ai-api":         $ai_api,
      "lint-clean":     $lint,
      "ts-clean":       $ts,
      "test-exists":    $texists,
      "test-pass":      $tpass,
      "test-coverage":  $tcoverage
    },
    auto_score_total: $total,
    auto_score_max: $max,
    errors: $errors
  }'
