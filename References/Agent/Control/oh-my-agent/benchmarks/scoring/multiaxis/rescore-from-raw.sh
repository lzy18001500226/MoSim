#!/usr/bin/env bash
# rescore-from-raw.sh — re-aggregate multiaxis-score.json from already-saved
# raw judge outputs (spec-raw.json, visual-judge-raw.json, journey-raw-claude.json).
# Useful when the judge ran successfully but parsing failed.
#
# Usage:
#   ./rescore-from-raw.sh <multiaxis-output-dir> <project-dir> <run-result-json> <harness-id>

set -uo pipefail

[[ $# -eq 4 ]] || { echo "Usage: $0 <multiaxis-dir> <project-dir> <run-json> <harness>" >&2; exit 1; }

OUTPUT_DIR="$1"
PROJECT_DIR="$2"
RUN_JSON="$3"
HARNESS_ID="$4"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RUBRIC="$SCRIPT_DIR/rubric.json"

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

# Re-extract judges
[[ -f "$OUTPUT_DIR/spec-raw.json" ]] && \
  jq -r '.result // ""' "$OUTPUT_DIR/spec-raw.json" | extract_json > "$OUTPUT_DIR/spec-judge.json"
[[ -f "$OUTPUT_DIR/visual-judge-raw.json" ]] && \
  jq -r '.result // ""' "$OUTPUT_DIR/visual-judge-raw.json" | extract_json > "$OUTPUT_DIR/visual-judge.json"
[[ -f "$OUTPUT_DIR/journey-raw-claude.json" ]] && \
  jq -r '.result // ""' "$OUTPUT_DIR/journey-raw-claude.json" | extract_json > "$OUTPUT_DIR/journey-raw.json"

# Read existing multiaxis-score.json (if any) to preserve auto-axis values,
# then patch in the freshly-extracted judge results.
EXISTING="$OUTPUT_DIR/multiaxis-score.json"
[[ -f "$EXISTING" ]] || { echo "ERROR: $EXISTING not found, can't rescore" >&2; exit 1; }

functional_json="$(jq '.axes.functional.items' "$EXISTING")"
spec_json="$(jq '.axes.spec.items' "$EXISTING")"
visual_json="$(jq '.axes.visual.items' "$EXISTING")"
eng_json="$(jq '.axes.engineering.items' "$EXISTING")"
eff_json="$(jq '.axes.efficiency.items' "$EXISTING")"

# --- patch journeys into functional_json ---
if jq -e '."journey-onboard"' "$OUTPUT_DIR/journey-raw.json" >/dev/null 2>&1; then
  for id in journey-onboard journey-builder journey-ai journey-save journey-gallery; do
    max=$(jq -r --arg id "$id" '.axes.functional.items[] | select(.id==$id) | .max' "$RUBRIC")
    score=$(jq -r --arg id "$id" '.[$id].score // 0' "$OUTPUT_DIR/journey-raw.json")
    evidence=$(jq -r --arg id "$id" '.[$id].evidence // ""' "$OUTPUT_DIR/journey-raw.json")
    pass=$(awk -v s="$score" -v m="$max" 'BEGIN{print (s>=m/2)?1:0}')
    functional_json="$(echo "$functional_json" | jq --arg id "$id" --argjson m "$max" --argjson s "$score" --arg e "$evidence" --argjson p "$pass" '. + {($id): {pass:$p, score:$s, max:$m, evidence:$e}}')"
  done
fi

# --- patch spec axis ---
if jq -e '.items["spec-product-concept"]' "$OUTPUT_DIR/spec-judge.json" >/dev/null 2>&1; then
  inner="$(cat "$OUTPUT_DIR/spec-judge.json")"
  for id in spec-product-concept spec-personas spec-journeys spec-feature-list spec-ia spec-ui-direction spec-tech-arch spec-db-schema spec-ai-prompts spec-safety spec-impl-plan spec-starter-code spec-priority-screens; do
    max=1
    pass=$(echo "$inner" | jq -r --arg id "$id" '.items[$id].pass // 0')
    evidence=$(echo "$inner" | jq -r --arg id "$id" '.items[$id].evidence // ""')
    [[ "$pass" == "1" ]] && score=1 || { pass=0; score=0; }
    spec_json="$(echo "$spec_json" | jq --arg id "$id" --argjson m "$max" --argjson p "$pass" --argjson s "$score" --arg e "$evidence" '. + {($id): {pass:$p, score:$s, max:$m, evidence:$e}}')"
  done
fi
# spec-real-api-bonus already in spec_json from previous run

# --- patch visual axis ---
if jq -e '.items["visual-anti-patterns"].score' "$OUTPUT_DIR/visual-judge.json" >/dev/null 2>&1; then
  inner="$(cat "$OUTPUT_DIR/visual-judge.json")"
  for id in visual-anti-patterns visual-child-friendly visual-consistency visual-accessibility; do
    max=5
    score=$(echo "$inner" | jq -r --arg id "$id" '.items[$id].score // 0')
    notes=$(echo "$inner" | jq -r --arg id "$id" '.items[$id].notes // ""')
    pass=$(awk -v s="$score" 'BEGIN{print (s>=3)?1:0}')
    visual_json="$(echo "$visual_json" | jq --arg id "$id" --argjson m "$max" --argjson s "$score" --arg e "$notes" --argjson p "$pass" '. + {($id): {pass:$p, score:$s, max:$m, evidence:$e}}')"
  done
fi

# --- aggregate ---
sum_axis() { echo "$1" | jq '[.[].score | tonumber] | add // 0'; }
max_axis() { echo "$1" | jq '[.[].max | tonumber] | add // 0'; }

func_total=$(sum_axis "$functional_json"); func_max=$(max_axis "$functional_json")
spec_total=$(sum_axis "$spec_json"); spec_max=$(max_axis "$spec_json")
visual_total=$(sum_axis "$visual_json"); visual_max=$(max_axis "$visual_json")
eng_total=$(sum_axis "$eng_json"); eng_max=$(max_axis "$eng_json")
eff_total=$(sum_axis "$eff_json"); eff_max=$(max_axis "$eff_json")

grand_total=$(awk -v a="$func_total" -v b="$spec_total" -v c="$visual_total" -v d="$eng_total" -v e="$eff_total" 'BEGIN{printf "%.1f", a+b+c+d+e}')
grand_max=$(awk -v a="$func_max" -v b="$spec_max" -v c="$visual_max" -v d="$eng_max" -v e="$eff_max" 'BEGIN{printf "%.1f", a+b+c+d+e}')

PM=$(jq -r '.package_manager' "$EXISTING")

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
    harness: $harness, package_manager: $pm,
    axes: {
      functional:  { items: $functional,  total: $func_total,   max: $func_max },
      spec:        { items: $spec,        total: $spec_total,   max: $spec_max },
      visual:      { items: $visual,      total: $visual_total, max: $visual_max },
      engineering: { items: $engineering, total: $eng_total,    max: $eng_max },
      efficiency:  { items: $efficiency,  total: $eff_total,    max: $eff_max }
    },
    total: $grand_total, max: $grand_max
  }' > "$OUTPUT_DIR/multiaxis-score.json"

jq '{harness, package_manager, total, max, by_axis: {functional: .axes.functional.total, spec: .axes.spec.total, visual: .axes.visual.total, engineering: .axes.engineering.total, efficiency: .axes.efficiency.total}}' \
  "$OUTPUT_DIR/multiaxis-score.json" > "$OUTPUT_DIR/multiaxis-summary.json"

cat "$OUTPUT_DIR/multiaxis-summary.json"
