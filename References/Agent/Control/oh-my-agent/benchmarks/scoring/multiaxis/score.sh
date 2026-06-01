#!/usr/bin/env bash
# multiaxis/score.sh — 5-axis benchmark scoring
#
# Usage:
#   ./score.sh <project-dir> <harness-id> <run-result-json> <output-dir>
#
# Inputs:
#   <project-dir>       Path to the harness's built project
#   <harness-id>        Short harness identifier (vanilla|oma|omc|ecc|superpowers)
#   <run-result-json>   The harness's claude -p result JSON (turns, duration, cost)
#   <output-dir>        Where to write multiaxis-score.json + screenshots
#
# Output:
#   <output-dir>/multiaxis-score.json — full per-axis breakdown
#   <output-dir>/multiaxis-summary.json — flat scores per axis
#
# Axes: functional (35) + spec (15) + visual (20) + engineering (20) + efficiency (10) = 100

set -uo pipefail

if [[ $# -ne 4 ]]; then
  echo "Usage: $0 <project-dir> <harness-id> <run-result-json> <output-dir>" >&2
  exit 1
fi

PROJECT_DIR="$(cd "$1" 2>/dev/null && pwd)" || { echo "ERROR: project-dir invalid: $1" >&2; exit 1; }
HARNESS_ID="$2"
RUN_JSON="$3"
OUTPUT_DIR="$4"

[[ -f "$RUN_JSON" ]] || { echo "ERROR: run-result-json not found: $RUN_JSON" >&2; exit 1; }
mkdir -p "$OUTPUT_DIR/screenshots"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RUBRIC="$SCRIPT_DIR/rubric.json"
JUDGE_SPEC="$SCRIPT_DIR/judge-spec-prompt.md"
JUDGE_VISUAL="$SCRIPT_DIR/judge-visual-prompt.md"
LOG="$OUTPUT_DIR/multiaxis.log"
: > "$LOG"

log() { echo "[$(date +%H:%M:%S)] $*" | tee -a "$LOG" >&2; }

require_cmd() { command -v "$1" &>/dev/null || { echo "ERROR: '$1' not in PATH" >&2; exit 1; }; }
for c in claude jq node; do require_cmd "$c"; done

# Robust JSON extractor — handles plain JSON, ```json fences, and prose
# preceding/following a balanced {...} object. Reads from stdin, writes
# the first valid JSON object to stdout. Returns 1 if none found.
extract_json() {
  node -e '
    (() => {
      const s = require("fs").readFileSync(0, "utf-8");
      try { JSON.parse(s); process.stdout.write(s.trim()); return; } catch(e){}
      const m = s.match(/```(?:json)?\s*\n?([\s\S]*?)\n?```/);
      if (m) { try { JSON.parse(m[1]); process.stdout.write(m[1].trim()); return; } catch(e){} }
      let depth = 0, start = -1, inStr = false, esc = false;
      for (let i = 0; i < s.length; i++) {
        const c = s[i];
        if (esc) { esc = false; continue; }
        if (c === "\\") { esc = true; continue; }
        if (c === "\"") { inStr = !inStr; continue; }
        if (inStr) continue;
        if (c === "{") { if (start < 0) start = i; depth++; }
        else if (c === "}") { depth--; if (depth === 0 && start >= 0) {
          const cand = s.slice(start, i+1);
          try { JSON.parse(cand); process.stdout.write(cand); return; } catch(e) { start = -1; }
        }}
      }
      process.exit(1);
    })();
  ' 2>/dev/null
}

# Detect package manager (same logic across axes)
detect_pm() {
  local d="$1"
  if [[ -f "$d/pnpm-lock.yaml" || -f "$d/pnpm-workspace.yaml" ]]; then echo pnpm
  elif [[ -f "$d/yarn.lock" ]]; then echo yarn
  elif [[ -f "$d/bun.lock" || -f "$d/bun.lockb" ]]; then echo bun
  else echo npm
  fi
}
PM="$(detect_pm "$PROJECT_DIR")"
log "PM=$PM, harness=$HARNESS_ID, project=$PROJECT_DIR"

pm_install() {
  case "$PM" in
    pnpm) echo "pnpm install --silent" ;;
    yarn) echo "yarn install --silent" ;;
    bun)  echo "bun install --silent" ;;
    *)    echo "npm install --no-audit --no-fund --loglevel=error" ;;
  esac
}
pm_run() {
  local s="$1"
  case "$PM" in
    pnpm) echo "pnpm run $s" ;;
    yarn) echo "yarn $s" ;;
    bun)  echo "bun run $s" ;;
    *)    echo "npm run $s" ;;
  esac
}

# Find a free TCP port for the dev server
find_free_port() {
  node -e 'const s=require("net").createServer();s.listen(0,()=>{const p=s.address().port;s.close(()=>console.log(p));})'
}

# ---------------------------------------------------------------------------
# AXIS 1 — FUNCTIONAL
# ---------------------------------------------------------------------------
log "=== AXIS 1: functional ==="

functional_json='{}'

# 1a. build-pass — install + run build
log "  build-pass: $(pm_install) && $(pm_run build)"
( cd "$PROJECT_DIR" && eval "$(pm_install) && $(pm_run build)" ) >>"$LOG" 2>&1
build_exit=$?
if [[ $build_exit -eq 0 ]]; then
  functional_json="$(echo "$functional_json" | jq --argjson m 5 '. + {"build-pass": {pass:1, score:$m, max:$m, evidence:"exit 0"}}')"
else
  functional_json="$(echo "$functional_json" | jq --argjson m 5 --arg e "exit $build_exit" '. + {"build-pass": {pass:0, score:0, max:$m, evidence:$e}}')"
fi

# 1b. boot-pass — start dev server, curl localhost
PORT="$(find_free_port)"
log "  boot-pass: starting dev server on port $PORT"
DEV_LOG="$OUTPUT_DIR/devserver.log"
( cd "$PROJECT_DIR" && PORT="$PORT" eval "$(pm_run dev)" > "$DEV_LOG" 2>&1 ) &
DEV_PID=$!

# Wait up to 45s for HTTP 200 on /
boot_ok=false
for i in $(seq 1 45); do
  sleep 1
  if curl -sf -m 2 "http://localhost:$PORT/" -o /dev/null 2>/dev/null; then
    boot_ok=true
    break
  fi
done

if [[ "$boot_ok" == true ]]; then
  functional_json="$(echo "$functional_json" | jq --argjson m 5 '. + {"boot-pass": {pass:1, score:$m, max:$m, evidence:"HTTP 200 within 45s"}}')"
  log "  boot-pass: OK"
else
  functional_json="$(echo "$functional_json" | jq --argjson m 5 '. + {"boot-pass": {pass:0, score:0, max:$m, evidence:"no HTTP 200 within 45s"}}')"
  log "  boot-pass: FAIL"
fi

# 1c. journey checks (delegated to MCP-driven claude judge using existing visual-score.sh as foundation)
# Capture screenshots first; then have a separate judge call score the journeys.
# We reuse the project's running dev server.

if [[ "$boot_ok" == true ]]; then
  log "  journey: invoking visual-score.sh for screenshots + journey eval (port $PORT)"
  # Cooperative reuse: tell visual-score.sh the dev server is already running by setting BENCH_DEV_URL
  BENCH_DEV_URL="http://localhost:$PORT" \
    "$SCRIPT_DIR/journey-judge.sh" "$PROJECT_DIR" "$HARNESS_ID" "$OUTPUT_DIR" "http://localhost:$PORT" \
    > "$OUTPUT_DIR/journey-raw.json" 2>>"$LOG" || true

  # Parse journey results — judge emits JSON like {"journey-onboard":{score,max,evidence}, ...}
  # journey-raw.json contains the .result string; extract balanced JSON from it.
  echo "$(jq -r '.result // ""' "$OUTPUT_DIR/journey-raw-claude.json" 2>/dev/null)" \
    | extract_json > "$OUTPUT_DIR/journey-raw.json.parsed" 2>/dev/null \
    && [[ -s "$OUTPUT_DIR/journey-raw.json.parsed" ]] \
    && mv "$OUTPUT_DIR/journey-raw.json.parsed" "$OUTPUT_DIR/journey-raw.json"
  if jq -e . "$OUTPUT_DIR/journey-raw.json" >/dev/null 2>&1; then
    for id in journey-onboard journey-builder journey-ai journey-save journey-gallery; do
      max=$(jq -r --arg id "$id" '.axes.functional.items[] | select(.id==$id) | .max' "$RUBRIC")
      score=$(jq -r --arg id "$id" '.[$id].score // 0' "$OUTPUT_DIR/journey-raw.json")
      evidence=$(jq -r --arg id "$id" '.[$id].evidence // ""' "$OUTPUT_DIR/journey-raw.json")
      pass=$(awk -v s="$score" -v m="$max" 'BEGIN{print (s>=m/2)?1:0}')
      functional_json="$(echo "$functional_json" | jq --arg id "$id" --argjson m "$max" --argjson s "$score" --arg e "$evidence" --argjson p "$pass" '. + {($id): {pass:$p, score:$s, max:$m, evidence:$e}}')"
    done
  else
    log "  journey: judge output unparseable, all journeys = 0"
    for id in journey-onboard journey-builder journey-ai journey-save journey-gallery; do
      max=$(jq -r --arg id "$id" '.axes.functional.items[] | select(.id==$id) | .max' "$RUBRIC")
      functional_json="$(echo "$functional_json" | jq --arg id "$id" --argjson m "$max" '. + {($id): {pass:0, score:0, max:$m, evidence:"judge failed"}}')"
    done
  fi
else
  log "  journey: skipped (boot failed)"
  for id in journey-onboard journey-builder journey-ai journey-save journey-gallery; do
    max=$(jq -r --arg id "$id" '.axes.functional.items[] | select(.id==$id) | .max' "$RUBRIC")
    functional_json="$(echo "$functional_json" | jq --arg id "$id" --argjson m "$max" '. + {($id): {pass:0, score:0, max:$m, evidence:"boot failed"}}')"
  done
fi

# Kill dev server
log "  killing dev server (pid $DEV_PID)"
kill -TERM "$DEV_PID" 2>/dev/null || true
sleep 2
kill -KILL "$DEV_PID" 2>/dev/null || true
# Also kill any node processes lingering on PORT
lsof -ti tcp:"$PORT" 2>/dev/null | xargs -r kill -KILL 2>/dev/null || true

# 1d. lint-clean — exempt deprecated `next lint` without config
log "  lint-clean"
lint_script=$(jq -r '.scripts.lint // empty' "$PROJECT_DIR/package.json" 2>/dev/null)
lint_handled=false
if [[ "$lint_script" == "next lint" ]]; then
  has_cfg=false
  for f in eslint.config.mjs eslint.config.js eslint.config.cjs eslint.config.ts .eslintrc.json .eslintrc.js .eslintrc.cjs; do
    [[ -f "$PROJECT_DIR/$f" ]] && has_cfg=true && break
  done
  if [[ "$has_cfg" == false ]]; then
    functional_json="$(echo "$functional_json" | jq --argjson m 5 '. + {"lint-clean": {pass:1, score:$m, max:$m, evidence:"n/a (deprecated next lint without config) — credited to avoid penalizing legitimate Next 15 setup"}}')"
    log "    SKIP (deprecated next lint, no config) — credit"
    lint_handled=true
  fi
fi
if [[ "$lint_handled" == false ]]; then
  if [[ -z "$lint_script" ]]; then
    functional_json="$(echo "$functional_json" | jq --argjson m 5 '. + {"lint-clean": {pass:0, score:0, max:$m, evidence:"no lint script"}}')"
  else
    ( cd "$PROJECT_DIR" && eval "$(pm_run lint) < /dev/null" ) >>"$LOG" 2>&1
    le=$?
    if [[ $le -eq 0 ]]; then
      functional_json="$(echo "$functional_json" | jq --argjson m 5 '. + {"lint-clean": {pass:1, score:$m, max:$m, evidence:"exit 0"}}')"
    else
      functional_json="$(echo "$functional_json" | jq --argjson m 5 --arg e "exit $le" '. + {"lint-clean": {pass:0, score:0, max:$m, evidence:$e}}')"
    fi
  fi
fi

# 1e. ts-clean
log "  ts-clean"
if [[ -f "$PROJECT_DIR/tsconfig.json" ]]; then
  case "$PM" in
    bun)  TSC="bunx tsc --noEmit" ;;
    pnpm) TSC="pnpm exec tsc --noEmit" ;;
    yarn) TSC="yarn tsc --noEmit" ;;
    *)    TSC="npx --no-install tsc --noEmit" ;;
  esac
  ( cd "$PROJECT_DIR" && eval "$TSC" ) >>"$LOG" 2>&1
  te=$?
  if [[ $te -eq 0 ]]; then
    functional_json="$(echo "$functional_json" | jq --argjson m 5 '. + {"ts-clean": {pass:1, score:$m, max:$m, evidence:"exit 0"}}')"
  else
    functional_json="$(echo "$functional_json" | jq --argjson m 5 --arg e "exit $te" '. + {"ts-clean": {pass:0, score:0, max:$m, evidence:$e}}')"
  fi
else
  functional_json="$(echo "$functional_json" | jq --argjson m 5 '. + {"ts-clean": {pass:0, score:0, max:$m, evidence:"no tsconfig.json"}}')"
fi

# ---------------------------------------------------------------------------
# AXIS 2 — SPEC (LLM judge against 13 outputs)
# ---------------------------------------------------------------------------
log "=== AXIS 2: spec ==="
spec_json='{}'
final_msg="$(jq -r '.result // ""' "$RUN_JSON")"
SPEC_PROMPT="$(cat "$JUDGE_SPEC")"
SPEC_PROMPT="${SPEC_PROMPT//<harness_id>/$HARNESS_ID}"
SPEC_PROMPT="${SPEC_PROMPT//<project_dir>/$PROJECT_DIR}"
# Replace <final_message> placeholder with actual content (truncated to 8KB to fit)
trunc="$(echo "$final_msg" | head -c 8000)"
SPEC_PROMPT="${SPEC_PROMPT/<final_message>/$trunc}"

log "  invoking spec judge (claude -p)..."
SPEC_RAW="$OUTPUT_DIR/spec-raw.json"
( cd "$PROJECT_DIR" && timeout 180 claude -p "$SPEC_PROMPT" \
    --dangerously-skip-permissions \
    --model claude-opus-4-6 \
    --effort high \
    --output-format json \
    --max-budget-usd 2 \
    --no-session-persistence \
    --setting-sources project,local \
    --add-dir "$PROJECT_DIR" ) > "$SPEC_RAW" 2>>"$LOG"

# Extract result (claude wraps with prose) and pull balanced JSON
spec_text="$(jq -r '.result // ""' "$SPEC_RAW" 2>/dev/null)"
spec_inner="$(echo "$spec_text" | extract_json)"
if [[ -z "$spec_inner" ]]; then spec_inner='{}'; fi
echo "$spec_inner" > "$OUTPUT_DIR/spec-judge.json"

# Score each spec item from judge output
for id in spec-product-concept spec-personas spec-journeys spec-feature-list spec-ia spec-ui-direction spec-tech-arch spec-db-schema spec-ai-prompts spec-safety spec-impl-plan spec-starter-code spec-priority-screens; do
  max=1
  pass=$(echo "$spec_inner" | jq -r --arg id "$id" '.items[$id].pass // 0' 2>/dev/null)
  evidence=$(echo "$spec_inner" | jq -r --arg id "$id" '.items[$id].evidence // ""' 2>/dev/null)
  [[ "$pass" == "1" ]] && score=1 || { pass=0; score=0; }
  spec_json="$(echo "$spec_json" | jq --arg id "$id" --argjson m "$max" --argjson p "$pass" --argjson s "$score" --arg e "$evidence" '. + {($id): {pass:$p, score:$s, max:$m, evidence:$e}}')"
done

# Auto bonus: real API integration (2pt)
SRC_DIR="$PROJECT_DIR/src"
real_api=0
api_evidence="not found"
if [[ -d "$SRC_DIR" ]]; then
  if grep -rE "(from ['\"]openai)|(from ['\"]@anthropic-ai/sdk)|(from ['\"]@google/genai)|(api\.openai\.com)|(api\.anthropic\.com)|(generativelanguage\.googleapis\.com)" \
        "$SRC_DIR" --include="*.ts" --include="*.tsx" --include="*.js" --include="*.jsx" -l 2>/dev/null | head -1 >/dev/null; then
    if grep -rE "(OPENAI_API_KEY)|(ANTHROPIC_API_KEY)|(GEMINI_API_KEY)|(GOOGLE_API_KEY)" \
          "$SRC_DIR" --include="*.ts" --include="*.tsx" --include="*.js" --include="*.jsx" -l 2>/dev/null | head -1 >/dev/null; then
      real_api=2
      api_evidence="real SDK/endpoint + env config"
    else
      real_api=1
      api_evidence="endpoint/SDK present, no env config"
    fi
  fi
fi
spec_json="$(echo "$spec_json" | jq --argjson m 2 --argjson s "$real_api" --arg e "$api_evidence" '. + {"spec-real-api-bonus": {pass: ($s>0|tostring|test("true")), score:$s, max:$m, evidence:$e}}')"

# ---------------------------------------------------------------------------
# AXIS 3 — VISUAL (LLM judge on screenshots)
# ---------------------------------------------------------------------------
log "=== AXIS 3: visual ==="
visual_json='{}'

# Pull screenshots from existing scoring/<harness>/screenshots/ if present
EXISTING_SHOTS_DIR="$(dirname "$OUTPUT_DIR")/$HARNESS_ID/screenshots"
if [[ -d "$EXISTING_SHOTS_DIR" ]] && ls "$EXISTING_SHOTS_DIR"/*.png >/dev/null 2>&1; then
  cp "$EXISTING_SHOTS_DIR"/*.png "$OUTPUT_DIR/screenshots/" 2>/dev/null || true
  log "  copied $(ls "$OUTPUT_DIR/screenshots" | wc -l | tr -d ' ') existing screenshot(s)"
fi

shot_count=$(ls "$OUTPUT_DIR/screenshots"/*.png 2>/dev/null | wc -l | tr -d ' ')
if [[ "$shot_count" -gt 0 ]]; then
  VISUAL_PROMPT="$(cat "$JUDGE_VISUAL")"
  VISUAL_PROMPT="${VISUAL_PROMPT//<harness_id>/$HARNESS_ID}"
  VISUAL_PROMPT="${VISUAL_PROMPT//<screenshots_glob>/$OUTPUT_DIR/screenshots/*.png}"

  VISUAL_RAW="$OUTPUT_DIR/visual-judge-raw.json"
  attempt=0
  visual_ok=false
  while (( attempt < 3 )) && [[ "$visual_ok" == false ]]; do
    attempt=$((attempt + 1))
    log "  visual judge attempt $attempt/3"
    ( cd "$OUTPUT_DIR" && timeout 180 claude -p "$VISUAL_PROMPT" \
        --dangerously-skip-permissions \
        --model claude-opus-4-6 \
        --effort high \
        --output-format json \
        --max-budget-usd 2 \
        --no-session-persistence \
        --setting-sources project,local \
        --add-dir "$OUTPUT_DIR" ) > "$VISUAL_RAW" 2>>"$LOG"
    visual_text="$(jq -r '.result // ""' "$VISUAL_RAW" 2>/dev/null)"
    inner="$(echo "$visual_text" | extract_json)"
    if [[ -n "$inner" ]] && echo "$inner" | jq -e '.items["visual-anti-patterns"].score' >/dev/null 2>&1; then
      visual_ok=true
      echo "$inner" > "$OUTPUT_DIR/visual-judge.json"
    fi
  done
  if [[ "$visual_ok" == true ]]; then
    inner="$(cat "$OUTPUT_DIR/visual-judge.json")"
    for id in visual-anti-patterns visual-child-friendly visual-consistency visual-accessibility; do
      max=5
      score=$(echo "$inner" | jq -r --arg id "$id" '.items[$id].score // 0')
      notes=$(echo "$inner" | jq -r --arg id "$id" '.items[$id].notes // ""')
      pass=$(awk -v s="$score" 'BEGIN{print (s>=3)?1:0}')
      visual_json="$(echo "$visual_json" | jq --arg id "$id" --argjson m "$max" --argjson s "$score" --arg e "$notes" --argjson p "$pass" '. + {($id): {pass:$p, score:$s, max:$m, evidence:$e}}')"
    done
  else
    log "  visual judge: gave up after 3 attempts"
    for id in visual-anti-patterns visual-child-friendly visual-consistency visual-accessibility; do
      visual_json="$(echo "$visual_json" | jq --arg id "$id" --argjson m 5 '. + {($id): {pass:0, score:0, max:$m, evidence:"judge unavailable"}}')"
    done
  fi
else
  log "  visual: no screenshots available, all visual = 0"
  for id in visual-anti-patterns visual-child-friendly visual-consistency visual-accessibility; do
    visual_json="$(echo "$visual_json" | jq --arg id "$id" --argjson m 5 '. + {($id): {pass:0, score:0, max:$m, evidence:"no screenshots"}}')"
  done
fi

# ---------------------------------------------------------------------------
# AXIS 4 — ENGINEERING
# ---------------------------------------------------------------------------
log "=== AXIS 4: engineering ==="
eng_json='{}'

# Exclude auto-generated source (Prisma 7+ emits .ts directly into src/generated)
SRC_FIND_FLAGS=(-type f \( -name '*.ts' -o -name '*.tsx' \) ! -path '*/generated/*' ! -path '*/__generated__/*' ! -path '*/.prisma/*')
count_ts="$(find "$PROJECT_DIR/src" "${SRC_FIND_FLAGS[@]}" 2>/dev/null | wc -l | tr -d ' ')"
count_routes="$(find "$PROJECT_DIR/src/app" -type f -name 'page.tsx' 2>/dev/null | wc -l | tr -d ' ')"
count_components="$(find "$PROJECT_DIR/src" -type d -name 'components' ! -path '*/generated/*' -exec find {} -type f \( -name '*.tsx' -o -name '*.ts' \) ! -path '*/generated/*' \; 2>/dev/null | wc -l | tr -d ' ')"
count_lines="$(find "$PROJECT_DIR/src" "${SRC_FIND_FLAGS[@]}" -exec cat {} + 2>/dev/null | wc -l | tr -d ' ')"

# 4a. eng-breadth — relative to a 6-route, 15-component baseline
breadth_score=$(awk -v r="$count_routes" -v c="$count_components" 'BEGIN{
  rs = (r>=6)?2:(r>=4)?1.5:(r>=2)?1:0
  cs = (c>=15)?2:(c>=10)?1.5:(c>=5)?1:0
  printf "%.1f", rs+cs
}')
eng_json="$(echo "$eng_json" | jq --argjson m 4 --argjson s "$breadth_score" --arg e "routes=$count_routes components=$count_components" '. + {"eng-breadth": {pass: ($s>=2|tostring|test("true")), score:$s, max:$m, evidence:$e}}')"

# 4b. eng-type-safety
strict=$(jq -r '.compilerOptions.strict // false' "$PROJECT_DIR/tsconfig.json" 2>/dev/null)
any_count=$(grep -rE ":\s*any\b|<any>" "$PROJECT_DIR/src" --include="*.ts" --include="*.tsx" --exclude-dir=generated --exclude-dir=__generated__ --exclude-dir=.prisma 2>/dev/null | wc -l | tr -d ' ')
ts_score=$(awk -v st="$strict" -v ac="$any_count" -v lines="$count_lines" 'BEGIN{
  base = (st=="true")?2:0
  if (lines==0){ printf "%.1f", base; exit }
  density = ac / lines * 1000
  bonus = (density<0.5)?2:(density<2)?1:(density<5)?0.5:0
  printf "%.1f", base+bonus
}')
eng_json="$(echo "$eng_json" | jq --argjson m 4 --argjson s "$ts_score" --arg e "strict=$strict any_count=$any_count" '. + {"eng-type-safety": {pass: ($s>=2|tostring|test("true")), score:$s, max:$m, evidence:$e}}')"

# 4c. eng-modularity — folder depth + max file size
max_depth="$(find "$PROJECT_DIR/src" -type d ! -path '*/generated/*' ! -path '*/__generated__/*' ! -path '*/.prisma/*' 2>/dev/null | awk -F/ '{print NF-1}' | sort -n | tail -1)"
max_file_lines="$(find "$PROJECT_DIR/src" "${SRC_FIND_FLAGS[@]}" -exec wc -l {} + 2>/dev/null | sort -n | tail -2 | head -1 | awk '{print $1}')"
mod_score=$(awk -v d="${max_depth:-0}" -v ml="${max_file_lines:-0}" 'BEGIN{
  ds = (d>=5)?2:(d>=3)?1.5:(d>=2)?1:0
  ms = (ml<=200)?2:(ml<=400)?1.5:(ml<=600)?1:0.5
  printf "%.1f", ds+ms
}')
eng_json="$(echo "$eng_json" | jq --argjson m 4 --argjson s "$mod_score" --arg e "max_depth=$max_depth max_file_lines=${max_file_lines:-0}" '. + {"eng-modularity": {pass: ($s>=2|tostring|test("true")), score:$s, max:$m, evidence:$e}}')"

# 4d. eng-transparency — count of deferred markers (TODO / replace with API / mock / MVP)
marker_count=$(grep -rEi -c "(TODO|MVP[: ]|replace.*with.*API|without.*API.*dependency|mock.*OpenAI|mock.*LLM|deferred|stub)" \
   "$PROJECT_DIR/src" --include="*.ts" --include="*.tsx" --exclude-dir=generated --exclude-dir=__generated__ --exclude-dir=.prisma 2>/dev/null | awk -F: '{s+=$2}END{print s+0}')
trans_score=$(awk -v c="$marker_count" 'BEGIN{
  s = (c>=3)?4:(c>=2)?3:(c>=1)?2:0
  printf "%.1f", s
}')
eng_json="$(echo "$eng_json" | jq --argjson m 4 --argjson s "$trans_score" --arg e "deferred_markers=$marker_count" '. + {"eng-transparency": {pass: ($s>=2|tostring|test("true")), score:$s, max:$m, evidence:$e}}')"

# 4e. eng-env-safety — no API key hardcoded, env-var pattern present
hardcode=$(grep -rE "(sk-[a-zA-Z0-9]{20,}|api[_-]?key\s*[:=]\s*['\"][a-zA-Z0-9]{20,})" \
  "$PROJECT_DIR/src" --include="*.ts" --include="*.tsx" --exclude-dir=generated --exclude-dir=__generated__ --exclude-dir=.prisma --include="*.js" --include="*.jsx" -l 2>/dev/null | head -1)
env_ref=$(grep -rE "(process\.env\.[A-Z_]+)" "$PROJECT_DIR/src" --include="*.ts" --include="*.tsx" --exclude-dir=generated --exclude-dir=__generated__ --exclude-dir=.prisma -l 2>/dev/null | head -1)
if [[ -z "$hardcode" && -n "$env_ref" ]]; then
  env_score=4 ; env_evidence="env config present, no hardcoded keys"
elif [[ -z "$hardcode" ]]; then
  env_score=3 ; env_evidence="no hardcoded keys, no env refs either"
else
  env_score=0 ; env_evidence="possible hardcoded key in $hardcode"
fi
eng_json="$(echo "$eng_json" | jq --argjson m 4 --argjson s "$env_score" --arg e "$env_evidence" '. + {"eng-env-safety": {pass: ($s>=3|tostring|test("true")), score:$s, max:$m, evidence:$e}}')"

# ---------------------------------------------------------------------------
# AXIS 5 — EFFICIENCY (extracted from RUN_JSON)
# ---------------------------------------------------------------------------
log "=== AXIS 5: efficiency ==="
eff_json='{}'
turns=$(jq -r '.num_turns // 0' "$RUN_JSON")
duration_s=$(jq -r '.duration_ms / 1000 | floor' "$RUN_JSON")
cost=$(jq -r '.total_cost_usd // 0' "$RUN_JSON")
files=$count_ts

# Turn-efficiency: 4pt if <=20 turns, 3pt if <=40, 2pt <=60, 1pt <=100, 0 else
eff_turns=$(awk -v t="$turns" 'BEGIN{
  s = (t<=20)?4:(t<=40)?3:(t<=60)?2:(t<=100)?1:0
  printf "%d", s
}')
# Time-efficiency: 3pt <=300s, 2pt <=600s, 1pt <=900s, 0 else
eff_time=$(awk -v d="$duration_s" 'BEGIN{
  s = (d<=300)?3:(d<=600)?2:(d<=900)?1:0
  printf "%d", s
}')
# Cost-per-file: lower better
cpf=$(awk -v c="$cost" -v f="$files" 'BEGIN{ if(f==0){print 0;exit} printf "%.3f", c/f }')
eff_cost=$(awk -v cpf="$cpf" 'BEGIN{
  s = (cpf<=0.10)?3:(cpf<=0.20)?2:(cpf<=0.50)?1:0
  printf "%d", s
}')

eff_json="$(echo "$eff_json" | jq --argjson m 4 --argjson s "$eff_turns" --arg e "$turns turns" '. + {"eff-turns": {pass: ($s>=2|tostring|test("true")), score:$s, max:$m, evidence:$e}}')"
eff_json="$(echo "$eff_json" | jq --argjson m 3 --argjson s "$eff_time" --arg e "${duration_s}s" '. + {"eff-time": {pass: ($s>=1|tostring|test("true")), score:$s, max:$m, evidence:$e}}')"
eff_json="$(echo "$eff_json" | jq --argjson m 3 --argjson s "$eff_cost" --arg e "\$$cpf/file ($cost USD / $files files)" '. + {"eff-cost": {pass: ($s>=1|tostring|test("true")), score:$s, max:$m, evidence:$e}}')"

# ---------------------------------------------------------------------------
# Aggregate
# ---------------------------------------------------------------------------
log "=== aggregating ==="
sum_axis() { echo "$1" | jq '[.[].score | tonumber] | add // 0'; }
max_axis() { echo "$1" | jq '[.[].max | tonumber] | add // 0'; }

func_total=$(sum_axis "$functional_json"); func_max=$(max_axis "$functional_json")
spec_total=$(sum_axis "$spec_json"); spec_max=$(max_axis "$spec_json")
visual_total=$(sum_axis "$visual_json"); visual_max=$(max_axis "$visual_json")
eng_total=$(sum_axis "$eng_json"); eng_max=$(max_axis "$eng_json")
eff_total=$(sum_axis "$eff_json"); eff_max=$(max_axis "$eff_json")

grand_total=$(awk -v a="$func_total" -v b="$spec_total" -v c="$visual_total" -v d="$eng_total" -v e="$eff_total" 'BEGIN{printf "%.1f", a+b+c+d+e}')
grand_max=$(awk -v a="$func_max" -v b="$spec_max" -v c="$visual_max" -v d="$eng_max" -v e="$eff_max" 'BEGIN{printf "%.1f", a+b+c+d+e}')

jq -n \
  --arg harness "$HARNESS_ID" \
  --arg pm "$PM" \
  --argjson functional "$functional_json" \
  --argjson spec "$spec_json" \
  --argjson visual "$visual_json" \
  --argjson engineering "$eng_json" \
  --argjson efficiency "$eff_json" \
  --argjson func_total "$func_total" --argjson func_max "$func_max" \
  --argjson spec_total "$spec_total" --argjson spec_max "$spec_max" \
  --argjson visual_total "$visual_total" --argjson visual_max "$visual_max" \
  --argjson eng_total "$eng_total" --argjson eng_max "$eng_max" \
  --argjson eff_total "$eff_total" --argjson eff_max "$eff_max" \
  --argjson grand_total "$grand_total" --argjson grand_max "$grand_max" \
  '{
    harness: $harness,
    package_manager: $pm,
    axes: {
      functional:  { items: $functional,  total: $func_total,   max: $func_max },
      spec:        { items: $spec,        total: $spec_total,   max: $spec_max },
      visual:      { items: $visual,      total: $visual_total, max: $visual_max },
      engineering: { items: $engineering, total: $eng_total,    max: $eng_max },
      efficiency:  { items: $efficiency,  total: $eff_total,    max: $eff_max }
    },
    total: $grand_total,
    max: $grand_max
  }' > "$OUTPUT_DIR/multiaxis-score.json"

# Flat summary
jq '{
  harness, package_manager,
  total, max,
  by_axis: {
    functional:  .axes.functional.total,
    spec:        .axes.spec.total,
    visual:      .axes.visual.total,
    engineering: .axes.engineering.total,
    efficiency:  .axes.efficiency.total
  }
}' "$OUTPUT_DIR/multiaxis-score.json" > "$OUTPUT_DIR/multiaxis-summary.json"

log "DONE — total=$grand_total/$grand_max"
cat "$OUTPUT_DIR/multiaxis-summary.json"
