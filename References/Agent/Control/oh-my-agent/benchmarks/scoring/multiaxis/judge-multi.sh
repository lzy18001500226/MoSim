#!/usr/bin/env bash
# judge-multi.sh — re-run spec + visual judges N times and average,
# patch multiaxis-score.json with the averaged values.
#
# Journey judge is NOT re-run (requires live dev server). Functional/
# engineering/efficiency axes are kept as-is (deterministic).
#
# Usage:
#   ./judge-multi.sh <multiaxis-dir> <project-dir> <run-json> <harness-id> <N>
#
#   <multiaxis-dir>  Existing multiaxis output dir (must contain
#                    multiaxis-score.json; existing spec-raw.json and
#                    visual-judge-raw.json are reused as run-1).
#   <project-dir>    Project source root (passed to spec judge as --add-dir).
#   <run-json>       claude -p result JSON (used to extract final_message).
#   <harness-id>     Short id for substitution in prompts.
#   <N>              Total judge runs (existing counts as #1; runs 2..N are new).

set -uo pipefail

[[ $# -eq 5 ]] || { echo "Usage: $0 <multiaxis-dir> <project-dir> <run-json> <harness> <N>" >&2; exit 1; }

OUTPUT_DIR="$(cd "$1" && pwd)"
PROJECT_DIR="$(cd "$2" && pwd)"
RUN_JSON="$3"
HARNESS_ID="$4"
N="$5"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RUBRIC="$SCRIPT_DIR/rubric.json"
JUDGE_SPEC="$SCRIPT_DIR/judge-spec-prompt.md"
JUDGE_VISUAL="$SCRIPT_DIR/judge-visual-prompt.md"

[[ -f "$OUTPUT_DIR/multiaxis-score.json" ]] || { echo "ERROR: $OUTPUT_DIR/multiaxis-score.json not found" >&2; exit 1; }
[[ -f "$RUN_JSON" ]] || { echo "ERROR: $RUN_JSON not found" >&2; exit 1; }
[[ "$N" =~ ^[0-9]+$ ]] && (( N >= 1 )) || { echo "ERROR: N must be positive int" >&2; exit 1; }

RAW="$OUTPUT_DIR/raw"
LOG="$OUTPUT_DIR/judge-multi.log"
mkdir -p "$RAW"
: > "$LOG"

log() { echo "[$(date +%H:%M:%S)] $*" | tee -a "$LOG" >&2; }

extract_json() {
  node -e '
    (() => {
      const s = require("fs").readFileSync(0, "utf-8");
      try { JSON.parse(s); process.stdout.write(s.trim()); return; } catch(e){}
      const m = s.match(/```(?:json)?\s*\n?([\s\S]*?)\n?```/);
      if (m) { try { JSON.parse(m[1]); process.stdout.write(m[1].trim()); return; } catch(e){} }
      let depth=0,start=-1,inStr=false,esc=false;
      for (let i=0;i<s.length;i++){
        const c=s[i];
        if(esc){esc=false;continue;}
        if(c==="\\"){esc=true;continue;}
        if(c==="\""){inStr=!inStr;continue;}
        if(inStr)continue;
        if(c==="{"){if(start<0)start=i;depth++;}
        else if(c==="}"){depth--;if(depth===0&&start>=0){const cand=s.slice(start,i+1);try{JSON.parse(cand);process.stdout.write(cand);return;}catch(e){start=-1;}}}
      }
      process.exit(1);
    })();
  ' 2>/dev/null
}

# Seed run-1 from existing single-run outputs
[[ -f "$OUTPUT_DIR/spec-raw.json"        && ! -f "$RAW/spec-1.json"   ]] && cp "$OUTPUT_DIR/spec-raw.json"        "$RAW/spec-1.json"
[[ -f "$OUTPUT_DIR/visual-judge-raw.json" && ! -f "$RAW/visual-1.json" ]] && cp "$OUTPUT_DIR/visual-judge-raw.json" "$RAW/visual-1.json"

# Build prompts (mirror score.sh)
final_msg="$(jq -r '.result // ""' "$RUN_JSON")"
trunc="$(echo "$final_msg" | head -c 8000)"
SPEC_PROMPT="$(cat "$JUDGE_SPEC")"
SPEC_PROMPT="${SPEC_PROMPT//<harness_id>/$HARNESS_ID}"
SPEC_PROMPT="${SPEC_PROMPT//<project_dir>/$PROJECT_DIR}"
SPEC_PROMPT="${SPEC_PROMPT/<final_message>/$trunc}"

VISUAL_PROMPT="$(cat "$JUDGE_VISUAL")"
VISUAL_PROMPT="${VISUAL_PROMPT//<harness_id>/$HARNESS_ID}"
VISUAL_PROMPT="${VISUAL_PROMPT//<screenshots_glob>/$OUTPUT_DIR/screenshots/*.png}"

run_spec() {
  local out="$1"
  ( cd "$PROJECT_DIR" && timeout 240 claude -p "$SPEC_PROMPT" \
      --dangerously-skip-permissions \
      --model claude-opus-4-6 \
      --effort high \
      --output-format json \
      --max-budget-usd 2 \
      --no-session-persistence \
      --setting-sources project,local \
      --add-dir "$PROJECT_DIR" ) > "$out" 2>>"$LOG"
}

run_visual() {
  local out="$1"
  ( cd "$OUTPUT_DIR" && timeout 240 claude -p "$VISUAL_PROMPT" \
      --dangerously-skip-permissions \
      --model claude-opus-4-6 \
      --effort high \
      --output-format json \
      --max-budget-usd 2 \
      --no-session-persistence \
      --setting-sources project,local \
      --add-dir "$OUTPUT_DIR" ) > "$out" 2>>"$LOG"
}

# Make sure screenshots are visible to the visual judge
if [[ ! -d "$OUTPUT_DIR/screenshots" ]] || ! ls "$OUTPUT_DIR/screenshots"/*.png >/dev/null 2>&1; then
  ALT="$(dirname "$(dirname "$OUTPUT_DIR")")/screenshots/$HARNESS_ID"
  if [[ -d "$ALT" ]] && ls "$ALT"/*.png >/dev/null 2>&1; then
    mkdir -p "$OUTPUT_DIR/screenshots"
    cp "$ALT"/*.png "$OUTPUT_DIR/screenshots/" || true
    log "copied screenshots from $ALT"
  fi
fi

for i in $(seq 1 "$N"); do
  if [[ ! -s "$RAW/spec-$i.json" ]]; then
    log "spec round $i/$N..."
    run_spec "$RAW/spec-$i.json"
  else
    log "spec round $i/$N — reusing existing"
  fi
  if [[ ! -s "$RAW/visual-$i.json" ]]; then
    log "visual round $i/$N..."
    run_visual "$RAW/visual-$i.json"
  else
    log "visual round $i/$N — reusing existing"
  fi
done

# Parse each round
for i in $(seq 1 "$N"); do
  jq -r '.result // ""' "$RAW/spec-$i.json"   2>/dev/null | extract_json > "$RAW/spec-$i.parsed.json"   2>/dev/null || echo '{}' > "$RAW/spec-$i.parsed.json"
  jq -r '.result // ""' "$RAW/visual-$i.json" 2>/dev/null | extract_json > "$RAW/visual-$i.parsed.json" 2>/dev/null || echo '{}' > "$RAW/visual-$i.parsed.json"
  [[ -s "$RAW/spec-$i.parsed.json"   ]] || echo '{}' > "$RAW/spec-$i.parsed.json"
  [[ -s "$RAW/visual-$i.parsed.json" ]] || echo '{}' > "$RAW/visual-$i.parsed.json"
done

# Aggregate spec: per item, mean of pass (0/1) across N runs → fractional score in [0,1]
EXISTING="$OUTPUT_DIR/multiaxis-score.json"
spec_existing=$(jq '.axes.spec.items' "$EXISTING")
spec_avg="$spec_existing"
for id in spec-product-concept spec-personas spec-journeys spec-feature-list spec-ia spec-ui-direction spec-tech-arch spec-db-schema spec-ai-prompts spec-safety spec-impl-plan spec-starter-code spec-priority-screens; do
  total=0
  votes_str=""
  for i in $(seq 1 "$N"); do
    v=$(jq -r --arg id "$id" '.items[$id].pass // 0' "$RAW/spec-$i.parsed.json" 2>/dev/null)
    [[ "$v" =~ ^[01]$ ]] || v=0
    total=$((total + v))
    votes_str+="$v"
  done
  mean=$(awk -v t="$total" -v n="$N" 'BEGIN{printf "%.2f", t/n}')
  pass_flag=$(awk -v m="$mean" 'BEGIN{print (m>=0.5)?1:0}')
  evidence="pass_votes=$votes_str ($total/$N rounds)"
  spec_avg=$(echo "$spec_avg" | jq --arg id "$id" --argjson m 1 --argjson s "$mean" --arg e "$evidence" --argjson p "$pass_flag" \
    '. + {($id): {pass:$p, score:$s, max:$m, evidence:$e}}')
done

# Aggregate visual: per item, mean of score (0..5) across N runs
visual_existing=$(jq '.axes.visual.items' "$EXISTING")
visual_avg="$visual_existing"
for id in visual-anti-patterns visual-child-friendly visual-consistency visual-accessibility; do
  scores_str=""
  total_f="0"
  for i in $(seq 1 "$N"); do
    v=$(jq -r --arg id "$id" '.items[$id].score // 0' "$RAW/visual-$i.parsed.json" 2>/dev/null)
    [[ "$v" =~ ^[0-9]+(\.[0-9]+)?$ ]] || v=0
    scores_str+="$v "
    total_f=$(awk -v a="$total_f" -v b="$v" 'BEGIN{printf "%.4f", a+b}')
  done
  mean=$(awk -v t="$total_f" -v n="$N" 'BEGIN{printf "%.1f", t/n}')
  pass_flag=$(awk -v m="$mean" 'BEGIN{print (m>=3)?1:0}')
  evidence="scores=[ ${scores_str}] mean=$mean (over $N rounds)"
  visual_avg=$(echo "$visual_avg" | jq --arg id "$id" --argjson m 5 --argjson s "$mean" --arg e "$evidence" --argjson p "$pass_flag" \
    '. + {($id): {pass:$p, score:$s, max:$m, evidence:$e}}')
done

# Re-aggregate (mirror score.sh)
sum_axis() { echo "$1" | jq '[.[].score | tonumber] | add // 0'; }
max_axis() { echo "$1" | jq '[.[].max  | tonumber] | add // 0'; }

functional_json=$(jq '.axes.functional.items'  "$EXISTING")
eng_json=$(       jq '.axes.engineering.items' "$EXISTING")
eff_json=$(       jq '.axes.efficiency.items'  "$EXISTING")

func_total=$(sum_axis "$functional_json"); func_max=$(max_axis "$functional_json")
spec_total=$(sum_axis "$spec_avg");        spec_max=$(max_axis "$spec_avg")
visual_total=$(sum_axis "$visual_avg");    visual_max=$(max_axis "$visual_avg")
eng_total=$(sum_axis "$eng_json");         eng_max=$(max_axis "$eng_json")
eff_total=$(sum_axis "$eff_json");         eff_max=$(max_axis "$eff_json")

grand_total=$(awk -v a="$func_total" -v b="$spec_total" -v c="$visual_total" -v d="$eng_total" -v e="$eff_total" 'BEGIN{printf "%.1f", a+b+c+d+e}')
grand_max=$(awk -v a="$func_max" -v b="$spec_max" -v c="$visual_max" -v d="$eng_max" -v e="$eff_max" 'BEGIN{printf "%.1f", a+b+c+d+e}')

PM=$(jq -r '.package_manager' "$EXISTING")

jq -n \
  --arg harness "$HARNESS_ID" \
  --arg pm "$PM" \
  --argjson functional "$functional_json" \
  --argjson spec "$spec_avg" \
  --argjson visual "$visual_avg" \
  --argjson engineering "$eng_json" \
  --argjson efficiency "$eff_json" \
  --argjson func_total "$func_total"   --argjson func_max "$func_max" \
  --argjson spec_total "$spec_total"   --argjson spec_max "$spec_max" \
  --argjson visual_total "$visual_total" --argjson visual_max "$visual_max" \
  --argjson eng_total "$eng_total"     --argjson eng_max "$eng_max" \
  --argjson eff_total "$eff_total"     --argjson eff_max "$eff_max" \
  --argjson grand_total "$grand_total" --argjson grand_max "$grand_max" \
  --argjson judge_runs "$N" \
  '{
    harness: $harness, package_manager: $pm,
    judge_runs_spec_visual: $judge_runs,
    axes: {
      functional:  { items: $functional,  total: $func_total,   max: $func_max },
      spec:        { items: $spec,        total: $spec_total,   max: $spec_max },
      visual:      { items: $visual,      total: $visual_total, max: $visual_max },
      engineering: { items: $engineering, total: $eng_total,    max: $eng_max },
      efficiency:  { items: $efficiency,  total: $eff_total,    max: $eff_max }
    },
    total: $grand_total, max: $grand_max
  }' > "$EXISTING"

jq '{harness, package_manager, judge_runs_spec_visual, total, max,
     by_axis: {functional: .axes.functional.total, spec: .axes.spec.total,
               visual: .axes.visual.total, engineering: .axes.engineering.total,
               efficiency: .axes.efficiency.total}}' \
  "$EXISTING" > "$OUTPUT_DIR/multiaxis-summary.json"

log "DONE — judge_runs=$N total=$grand_total/$grand_max"
cat "$OUTPUT_DIR/multiaxis-summary.json"
