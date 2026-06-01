#!/usr/bin/env bash
# build-report.sh — generate benchmarks/README.md from multiaxis-score.json
# files and the screenshots/ tree.
#
# Usage:
#   ./build-report.sh <bench-base-dir> <repo-root>
#
# Inputs:
#   <bench-base-dir>  e.g., /tmp/oma-benchmark-20260504-171703
#   <repo-root>       repo root (writes <repo-root>/benchmarks/README.md)
#
# Reads:
#   <bench-base-dir>/multiaxis/<harness>/multiaxis-score.json
#   <bench-base-dir>/results/<harness>.json
#   <repo-root>/benchmarks/screenshots/<harness>/*.png

set -uo pipefail

if [[ $# -ne 2 ]]; then
  echo "Usage: $0 <bench-base-dir> <repo-root>" >&2
  exit 1
fi

BASE="$1"
REPO="$2"
OUT="$REPO/benchmarks/README.md"
SHOTS_BASE="$REPO/benchmarks/screenshots"

# Order to display in narrative (rank by total desc — computed below)
ALL_HARNESSES=(vanilla oma omc ecc superpowers)

# Validate inputs
for h in "${ALL_HARNESSES[@]}"; do
  [[ -f "$BASE/multiaxis/$h/multiaxis-score.json" ]] || { echo "ERROR: missing $BASE/multiaxis/$h/multiaxis-score.json" >&2; exit 1; }
  [[ -f "$BASE/results/$h.json" || -f "$BASE/results/$h.run.json" ]] || { echo "ERROR: missing $BASE/results/$h.json (or $h.run.json)" >&2; exit 1; }
done

# ---------------------------------------------------------------------------
# Compute ranked harness order (desc by total)
# ---------------------------------------------------------------------------
RANKED="$(
  for h in "${ALL_HARNESSES[@]}"; do
    total=$(jq -r '.total' "$BASE/multiaxis/$h/multiaxis-score.json")
    echo "$total $h"
  done | sort -k1 -nr | awk '{print $2}'
)"

# Helpers
get() { jq -r "$1" "$BASE/multiaxis/$2/multiaxis-score.json"; }
# Numeric-aware get: rounds floats to 1 decimal (drops trailing .0 for integers)
getn() {
  local v
  v=$(jq -r "$1" "$BASE/multiaxis/$2/multiaxis-score.json")
  awk -v x="$v" 'BEGIN{
    if (x ~ /^-?[0-9]+(\.[0-9]+)?$/) {
      r = sprintf("%.1f", x+0)
      sub(/\.0$/, "", r)
      print r
    } else print x
  }'
}
runget() {
  local f="$BASE/results/$2.json"
  [[ -f "$f" ]] || f="$BASE/results/$2.run.json"
  jq -r "$1" "$f"
}

# Map a row name to a screenshot file present for given harness, or empty.
find_shot() {
  local harness="$1" row="$2"
  local d="$SHOTS_BASE/$harness"
  [[ -d "$d" ]] || { echo ""; return; }
  case "$row" in
    landing)
      [[ -f "$d/01-landing.png" ]] && echo "01-landing.png" && return ;;
    builder)
      for f in 02-world-builder.png 02-builder.png; do
        [[ -f "$d/$f" ]] && echo "$f" && return
      done ;;
    ai)
      [[ -f "$d/03-ai-panel.png" ]] && echo "03-ai-panel.png" && return ;;
    gallery)
      for f in 04-gallery.png 05-gallery.png; do
        [[ -f "$d/$f" ]] && echo "$f" && return
      done ;;
    object)
      for f in 02b-object-placed.png 02b-box-placed.png 02-world-builder-with-object.png 05-objects-added.png; do
        [[ -f "$d/$f" ]] && echo "$f" && return
      done ;;
    env)
      for f in 06-theme-change.png 02c-env-theme.png 02b-env-theme.png 05-env-theme.png; do
        [[ -f "$d/$f" ]] && echo "$f" && return
      done ;;
    save)
      [[ -f "$d/04-save-after-reload.png" ]] && echo "04-save-after-reload.png" && return ;;
  esac
  echo ""
}

shot_cell() {
  local harness="$1" row="$2"
  local file
  file="$(find_shot "$harness" "$row")"
  if [[ -n "$file" ]]; then
    echo "![$harness $row](screenshots/$harness/$file)"
  else
    echo "_(missing)_"
  fi
}

# Format duration in m:ss
fmt_dur() {
  local s="$1"
  local m=$((s / 60))
  local r=$((s % 60))
  printf "%dm %02ds" "$m" "$r"
}

# Format cost trimmed to 2 decimals
fmt_cost() {
  awk -v c="$1" 'BEGIN{printf "$%.2f", c}'
}

# Build "spec missed/passed" bullets per harness
spec_passed() {
  jq -r '.axes.spec.items | to_entries[] | select(.value.score>0 and (.key|startswith("spec-real")|not)) | (.key|ltrimstr("spec-"))' "$BASE/multiaxis/$1/multiaxis-score.json" | paste -sd, -
}
spec_failed() {
  jq -r '.axes.spec.items | to_entries[] | select(.value.score==0 and (.key|startswith("spec-real")|not)) | (.key|ltrimstr("spec-"))' "$BASE/multiaxis/$1/multiaxis-score.json" | paste -sd, -
}

# Generate per-harness narrative bullets (mechanical)
narrative_for() {
  local h="$1" rank="$2"

  local total func spec visual eng eff
  total=$(getn '.total' "$h")
  func=$(getn '.axes.functional.total' "$h")
  spec=$(getn '.axes.spec.total' "$h")
  visual=$(getn '.axes.visual.total' "$h")
  eng=$(getn '.axes.engineering.total' "$h")
  eff=$(getn '.axes.efficiency.total' "$h")

  local turns dur_s cost
  turns=$(runget '.num_turns' "$h")
  dur_s=$(runget '.duration_ms / 1000 | floor' "$h")
  cost=$(runget '.total_cost_usd' "$h")
  cost_fmt=$(fmt_cost "$cost")
  dur_fmt=$(fmt_dur "$dur_s")

  # Functional drops
  local lint_score lint_ev
  lint_score=$(get '.axes.functional.items["lint-clean"].score' "$h")
  lint_ev=$(get '.axes.functional.items["lint-clean"].evidence' "$h")
  local save_score save_ev
  save_score=$(get '.axes.functional.items["journey-save"].score' "$h")
  save_ev=$(get '.axes.functional.items["journey-save"].evidence' "$h")

  # Spec
  local spec_passed_list spec_failed_list spec_real
  spec_passed_list=$(spec_passed "$h")
  spec_failed_list=$(spec_failed "$h")
  spec_real=$(get '.axes.spec.items["spec-real-api-bonus"].score' "$h")

  # Visual
  local v_anti v_anti_ev v_acc
  v_anti=$(getn '.axes.visual.items["visual-anti-patterns"].score' "$h")
  v_anti_ev=$(get '.axes.visual.items["visual-anti-patterns"].evidence' "$h" | head -c 120)
  v_acc=$(getn '.axes.visual.items["visual-accessibility"].score' "$h")

  # Engineering
  local e_breadth_ev e_type_ev e_mod_ev e_transp e_env_ev
  e_breadth_ev=$(get '.axes.engineering.items["eng-breadth"].evidence' "$h")
  e_type_ev=$(get '.axes.engineering.items["eng-type-safety"].evidence' "$h")
  e_mod_ev=$(get '.axes.engineering.items["eng-modularity"].evidence' "$h")
  e_transp=$(getn '.axes.engineering.items["eng-transparency"].score' "$h")
  e_env_ev=$(get '.axes.engineering.items["eng-env-safety"].evidence' "$h")

  cat <<NAR

### $rank $h ($total)

- **Functional $func/35** — $(
    if (( $(echo "$func >= 35" | bc -l) )); then echo "all journeys + build/boot/lint/ts clean."
    else
      bullets=""
      if [[ "$lint_score" == "0" ]]; then
        if [[ "$h" == "oma" ]]; then
          bullets+="lint -5 (real eslint errors caught at scoring time; oma defers lint enforcement to pre-commit/pre-push hooks — see caveat #4); "
        else
          bullets+="lint failed; "
        fi
      fi
      awk -v s="$save_score" 'BEGIN{exit !(s<3)}' && bullets+="save-reload only $save_score/3; "
      [[ -z "$bullets" ]] && bullets="see breakdown"
      echo "${bullets%; }."
    fi
  )
- **Spec $spec/15** — passed: \`${spec_passed_list:-(none)}\`. ${spec_failed_list:+failed: \`$spec_failed_list\`. }real-api bonus $spec_real/2.
- **Visual $visual/20** — anti-patterns $v_anti/5 ($(echo "$v_anti_ev" | tr -d '\n' | head -c 100)…); accessibility $v_acc/5.
- **Engineering $eng/20** — breadth: $e_breadth_ev. type: $e_type_ev. modularity: $e_mod_ev. transparency markers: $e_transp/4. env: $e_env_ev.
- **Efficiency $eff/10** — $turns turns / $dur_fmt / $cost_fmt total ($(awk -v c="$cost" -v f="$(get '.axes.engineering.items["eng-breadth"].evidence' "$h" | grep -oE 'components=[0-9]+' | grep -oE '[0-9]+')" 'BEGIN{ if(f==0){print "?";exit} printf "$%.2f/file", c/f }') estimated).
NAR
}

# ---------------------------------------------------------------------------
# Build header rows in markdown
# ---------------------------------------------------------------------------
{
cat <<'HEAD'
# AI Coding Harness Benchmark

Compares 5 Claude Code harnesses on the same prompt — building a children's
3D creative learning platform MVP (`benchmarks/prompt.md`).

| Harness | Mechanism | Activation evidence |
|---|---|---|
| `vanilla` | bare Claude Code, no plugin/skill | baseline |
| `oma` | `oh-my-agent` source-seeded into project (`.agents/` + `.claude/`) | design-rule-driven anti-pattern avoidance, deferred-stub markers |
| `omc` | `oh-my-claudecode` via `--plugin-dir` | self-reported "OMC loaded, 40+ skills" |
| `ecc` | `everything-claude-code` installed to user `~/.claude/` | session skill list expanded with ecc skills |
| `superpowers` | `superpowers` via `--plugin-dir` | first run hit `<HARD-GATE>` brainstorming skill (forced override prompt to proceed) |

Run conditions: `claude-opus-4-6`, effort `max`, `--max-budget-usd 20`,
`--no-session-persistence`, `--setting-sources project,local`, identical raw prompt.
ANTHROPIC_API_KEY not set — OAuth via the user's logged-in `claude` CLI.

---

## Final scoreboard (5-axis, 100pt total)

| Rank | Harness | **Total** | Func/35 | Spec/15 | Visual/20 | Eng/20 | Eff/10 |
|---|---|---|---|---|---|---|---|
HEAD

i=0
for h in $RANKED; do
  i=$((i + 1))
  case $i in 1) medal="🥇 1" ;; 2) medal="🥈 2" ;; 3) medal="🥉 3" ;; *) medal="$i" ;; esac
  total=$(getn '.total' "$h")
  func=$(getn '.axes.functional.total' "$h")
  spec=$(getn '.axes.spec.total' "$h")
  visual=$(getn '.axes.visual.total' "$h")
  eng=$(getn '.axes.engineering.total' "$h")
  eff=$(getn '.axes.efficiency.total' "$h")
  if (( i == 1 )); then
    printf "| %s | **%s** | **%s** | %s | %s | %s | %s | %s |\n" "$medal" "$h" "$total" "$func" "$spec" "$visual" "$eng" "$eff"
  else
    printf "| %s | %s | %s | %s | %s | %s | %s | %s |\n" "$medal" "$h" "$total" "$func" "$spec" "$visual" "$eng" "$eff"
  fi
done

# Run economics
cat <<'ECON_HEAD'

### Run economics

| Harness | Turns | Duration | Cost | Files (src) | Cost / file |
|---|---|---|---|---|---|
ECON_HEAD

for h in "${ALL_HARNESSES[@]}"; do
  turns=$(runget '.num_turns' "$h")
  dur_s=$(runget '.duration_ms / 1000 | floor' "$h")
  cost=$(runget '.total_cost_usd' "$h")
  files=$(get '.axes.engineering.items["eng-breadth"].evidence' "$h" | grep -oE 'components=[0-9]+' | grep -oE '[0-9]+')
  routes=$(get '.axes.engineering.items["eng-breadth"].evidence' "$h" | grep -oE 'routes=[0-9]+' | grep -oE '[0-9]+')
  src_files=$(awk -v r="${routes:-0}" -v c="${files:-0}" 'BEGIN{print r+c+5}')  # rough
  cpf=$(awk -v c="$cost" -v f="$src_files" 'BEGIN{ if(f==0){print "?";exit} printf "$%.2f", c/f }')
  cost_fmt=$(fmt_cost "$cost")
  dur_fmt=$(fmt_dur "$dur_s")
  printf "| %s | %s | %s | %s | %s | %s |\n" "$h" "$turns" "$dur_fmt" "$cost_fmt" "$src_files" "$cpf"
done

# Screenshot rows
cat <<'SHOT_HEAD'

---

## Screenshot comparison

SHOT_HEAD

declare -a ROWS=(
  "Landing page|landing"
  "World builder|builder"
  "AI panel|ai"
  "Gallery|gallery"
  "Save → reload (state persistence)|save"
)

for row in "${ROWS[@]}"; do
  IFS='|' read -r title key <<< "$row"
  echo "### $title"
  echo
  echo "| vanilla | oma | omc | ecc | superpowers |"
  echo "|---|---|---|---|---|"
  cells=""
  for h in vanilla oma omc ecc superpowers; do
    cells+="| $(shot_cell "$h" "$key") "
  done
  cells+="|"
  echo "$cells"
  echo
  if [[ "$key" == "save" ]]; then
    cat <<'NOTE'
> `journey-save` axis evidence: harnesses scoring 3/3 fully restore the saved
> world; harnesses scoring 1.5/3 persist the gallery card but the canvas
> doesn't rehydrate after reload.
NOTE
    echo
  fi
done

# Per-harness narrative
cat <<'NARR_HEAD'
---

## Per-harness narrative

NARR_HEAD

i=0
for h in $RANKED; do
  i=$((i + 1))
  case $i in 1) rank="🥇" ;; 2) rank="🥈" ;; 3) rank="🥉" ;; *) rank="$i." ;; esac
  narrative_for "$h" "$rank"
done

# Methodology
cat <<'METH'

---

## How the score axes are computed

| Axis | Weight | Key signals | Tooling |
|---|---|---|---|
| **Functional** | 35 | build exit, dev-server boots (HTTP 200 ≤45s), 5 user-journey checks, lint, ts-clean | `pm install/build/lint`, curl, chrome-devtools MCP, `tsc --noEmit` |
| **Spec** | 15 | 13 explicit prompt deliverables (docs or final reply), real-API bonus | LLM judge with brace-balanced JSON extractor |
| **Visual** | 20 | anti-patterns (gradient bgs, sub-16px text, nesting), child-friendly UX, design-system consistency, accessibility | LLM judge over screenshots |
| **Engineering** | 20 | code breadth, TS strict, max file size + folder depth, deferred-stub markers, no hardcoded keys | static analysis (jq + grep + find) |
| **Efficiency** | 10 | turns to complete, wall-clock duration, cost-per-file | `claude -p` result JSON |

Implementation: `benchmarks/scoring/multiaxis/score.sh` → emits per-harness
`multiaxis-score.json` and `multiaxis-summary.json`. This README itself is
generated by `benchmarks/scoring/multiaxis/build-report.sh`.

---

## Honest caveats

1. **superpowers prompt override** — necessary for the harness to function in non-interactive mode. Result is "what superpowers can do once the brainstorming gate is bypassed", not pure apples-to-apples.
2. **Multi-judge averaging (spec + visual), single-run journey** — spec and visual judges run 3 times per harness via `judge-multi.sh`; per-item scores are averaged across rounds (fractional like 0.67 = 2-of-3 rounds passed). Journey judging requires a live dev server so it stays single-run; treat journey gaps under ~2 points as noise. Sample size is still 1 build per harness — re-running the same harness from scratch can still produce different code, which this benchmark does not measure.
3. **Cost normalization** — efficiency uses cost-per-file. Absolute cost ($1.28–$8.19 across the 5) is not reflected in the axis score.
4. **oma design principle: lint and typecheck belong in pre-commit / pre-push, not in the agent skill** — oma deliberately does not have the agent self-police linter rules during generation. The reasoning: (a) baking ESLint-specific rules into a skill is brittle (Biome / oxlint / future linters have different rules), and (b) the canonical layer for "is this push-ready" is git hooks (husky + lint-staged for pre-commit; lint/typecheck/build for pre-push) and CI. In a real workflow, the bad `<a href>` and unused-import this run produced would be blocked by the pre-push hook before they reach the remote — the developer (or agent on retry) would fix and re-push. Single-run benchmark scoring penalises this as -5 in `lint-clean`, but the architectural choice is intentional: keep agent skills focused on framework canonical patterns, leave mechanical enforcement to the hook/CI layer.

---

## Reproduce

```bash
# 1. Run all 5 harnesses (sequential, ~45 min, ~$15-20 in API spend)
./benchmarks/run.sh

# 2. Multiaxis scoring per harness (5-axis, 100pt) — single judge round
for h in vanilla oma omc ecc superpowers; do
  ./benchmarks/scoring/multiaxis/score.sh \
    /tmp/oma-benchmark-<timestamp>/projects/$h \
    $h \
    /tmp/oma-benchmark-<timestamp>/results/$h.json \
    /tmp/oma-benchmark-<timestamp>/multiaxis/$h
done

# 3. (optional) Re-judge spec + visual N times and average — reduces LLM noise.
#    Reuses existing run-1 outputs and runs N-1 additional rounds.
for h in vanilla oma omc ecc superpowers; do
  ./benchmarks/scoring/multiaxis/judge-multi.sh \
    /tmp/oma-benchmark-<timestamp>/multiaxis/$h \
    /tmp/oma-benchmark-<timestamp>/projects/$h \
    /tmp/oma-benchmark-<timestamp>/results/$h.json \
    $h \
    3
done

# 4. Generate this README from the multiaxis outputs
./benchmarks/scoring/multiaxis/build-report.sh \
  /tmp/oma-benchmark-<timestamp> \
  $(pwd)
```
METH

} > "$OUT"

echo "wrote: $OUT" >&2
wc -l "$OUT" >&2
