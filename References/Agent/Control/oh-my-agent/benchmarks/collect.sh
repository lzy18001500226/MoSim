#!/usr/bin/env bash
# =============================================================================
# benchmarks/collect.sh — AI Harness Benchmark Aggregator
# =============================================================================
#
# Reads outputs produced by run.sh (and optionally auto-score.sh /
# visual-score.sh) for a completed benchmark run, then:
#   1. Runs auto-score.sh and visual-score.sh per harness (idempotent).
#   2. Aggregates raw scores into $BASE/results/scores.json.
#   3. Writes a human-readable $BASE/results/report.md.
#   4. Copies generated code, screenshots, and reports to the repo tree.
#
# Usage:
#   ./benchmarks/collect.sh <BASE_DIR>
#
# Example:
#   ./benchmarks/collect.sh /tmp/oma-benchmark-20260411-120000
#
# Prerequisites:
#   - jq    in PATH
#   - rsync in PATH (falls back to cp + find -delete)
#   - auto-score.sh and visual-score.sh alongside this script in scoring/
# =============================================================================

set -uo pipefail

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly SCRIPT_DIR
readonly SCORING_DIR="${SCRIPT_DIR}/scoring"
readonly AUTO_SCORE_SH="${SCORING_DIR}/auto-score.sh"
readonly VISUAL_SCORE_SH="${SCORING_DIR}/visual-score.sh"
readonly CHECKLIST_JSON="${SCORING_DIR}/checklist.json"
readonly REPO_ROOT="${SCRIPT_DIR}"
readonly REPO_RUNS_DIR="${REPO_ROOT}/runs"
readonly REPO_SCREENSHOTS_DIR="${REPO_ROOT}/screenshots"
readonly REPO_RESULTS_DIR="${REPO_ROOT}/results"

# ---------------------------------------------------------------------------
# Argument validation
# ---------------------------------------------------------------------------
if [[ $# -ne 1 ]]; then
  echo "Usage: $0 <BASE_DIR>" >&2
  exit 1
fi

BASE="$(cd "$1" 2>/dev/null && pwd)" || {
  echo "ERROR: BASE_DIR does not exist or is not accessible: $1" >&2
  exit 1
}

RUN_MANIFEST="${BASE}/results/run-manifest.json"

if [[ ! -f "$RUN_MANIFEST" ]]; then
  echo "ERROR: run-manifest.json not found at ${RUN_MANIFEST}" >&2
  echo "  Make sure run.sh has completed for this BASE directory." >&2
  exit 1
fi

# ---------------------------------------------------------------------------
# Preflight: required binaries and scoring scripts
# ---------------------------------------------------------------------------
preflight_check() {
  local missing=0

  if ! command -v jq &>/dev/null; then
    echo "ERROR: 'jq' not found in PATH" >&2
    missing=1
  fi

  if [[ ! -x "$AUTO_SCORE_SH" ]]; then
    echo "ERROR: auto-score.sh not found or not executable: ${AUTO_SCORE_SH}" >&2
    missing=1
  fi

  if [[ ! -x "$VISUAL_SCORE_SH" ]]; then
    echo "ERROR: visual-score.sh not found or not executable: ${VISUAL_SCORE_SH}" >&2
    missing=1
  fi

  if [[ ! -f "$CHECKLIST_JSON" ]]; then
    echo "ERROR: checklist.json not found: ${CHECKLIST_JSON}" >&2
    missing=1
  fi

  if [[ "$missing" -ne 0 ]]; then
    exit 1
  fi

  # rsync is optional (we fall back to cp)
  if command -v rsync &>/dev/null; then
    HAS_RSYNC=true
  else
    HAS_RSYNC=false
  fi
}

# ---------------------------------------------------------------------------
# Logging helpers
# ---------------------------------------------------------------------------
log()  { echo "[$(date +%H:%M:%S)] $*"; }
info() { echo "[$(date +%H:%M:%S)] INFO  $*"; }
warn() { echo "[$(date +%H:%M:%S)] WARN  $*" >&2; }
err()  { echo "[$(date +%H:%M:%S)] ERROR $*" >&2; }

# ---------------------------------------------------------------------------
# rsync or cp -r fallback for copying project trees
# Excludes: node_modules, .next, .git
# ---------------------------------------------------------------------------
sync_tree() {
  local src="$1"
  local dst="$2"

  mkdir -p "$dst"

  if [[ "$HAS_RSYNC" == true ]]; then
    rsync -a \
      --exclude=node_modules \
      --exclude=.next \
      --exclude=.git \
      "${src}/" "${dst}/"
  else
    cp -r "${src}/." "${dst}/"
    find "$dst" \( \
      -name "node_modules" \
      -o -name ".next" \
      -o -name ".git" \
    \) -exec rm -rf {} + 2>/dev/null || true
  fi
}

# ---------------------------------------------------------------------------
# Safe copy of screenshots directory
# ---------------------------------------------------------------------------
sync_screenshots() {
  local src="$1"   # $BASE/scoring/$h/screenshots
  local dst="$2"   # $REPO_SCREENSHOTS_DIR/$h

  if [[ ! -d "$src" ]]; then
    warn "  Screenshots directory not found, skipping: ${src}"
    return 0
  fi

  mkdir -p "$dst"

  if [[ "$HAS_RSYNC" == true ]]; then
    rsync -a "${src}/" "${dst}/"
  else
    cp -r "${src}/." "${dst}/"
  fi
}

# ---------------------------------------------------------------------------
# Read harness list from run-manifest.json
# ---------------------------------------------------------------------------
read_harnesses() {
  jq -r '.harnesses[]' "$RUN_MANIFEST"
}

# ---------------------------------------------------------------------------
# Read model from run-manifest.json
# ---------------------------------------------------------------------------
read_model() {
  jq -r '.model // "unknown"' "$RUN_MANIFEST"
}

# ---------------------------------------------------------------------------
# Run auto-score.sh for a harness (idempotent: always re-runs)
# ---------------------------------------------------------------------------
run_auto_score() {
  local harness="$1"
  local project_dir="${BASE}/projects/${harness}"
  local out_file="${BASE}/results/${harness}.auto-score.json"

  if [[ ! -d "$project_dir" ]]; then
    warn "[${harness}] project dir missing — auto-score skipped: ${project_dir}"
    return 1
  fi

  info "[${harness}] Running auto-score.sh..."
  if "$AUTO_SCORE_SH" "$project_dir" "$harness" > "$out_file" 2>"${BASE}/results/${harness}.auto-score.stderr"; then
    info "[${harness}] auto-score complete."
    return 0
  else
    warn "[${harness}] auto-score.sh exited non-zero. Partial results may exist."
    return 1
  fi
}

# ---------------------------------------------------------------------------
# Run visual-score.sh for a harness (idempotent: always re-runs)
# ---------------------------------------------------------------------------
run_visual_score() {
  local harness="$1"
  local project_dir="${BASE}/projects/${harness}"
  local scoring_dir="${BASE}/scoring/${harness}"

  if [[ ! -d "$project_dir" ]]; then
    warn "[${harness}] project dir missing — visual-score skipped: ${project_dir}"
    return 1
  fi

  mkdir -p "$scoring_dir"

  info "[${harness}] Running visual-score.sh..."
  if "$VISUAL_SCORE_SH" "$project_dir" "$harness" "$scoring_dir" \
       2>"${scoring_dir}/visual-score-collect.stderr"; then
    info "[${harness}] visual-score complete."
    return 0
  else
    warn "[${harness}] visual-score.sh exited non-zero."
    return 1
  fi
}

# ---------------------------------------------------------------------------
# Score aggregation
#
# checklist.json categories have a `weight` (max points for that category)
# and items with individual `max` values. The item maxes within a category
# do NOT always sum to the category weight (e.g. world-builder: items sum to
# 30 but weight is 20). We therefore use normalized scoring:
#
#   item.normalized  = item.score / item.max           (0..1)
#   category.score   = sum(item.normalized * item.max) * (weight / items_sum)
#   total_score      = sum(category.score)             (max == sum(weights) == 100)
#
# Sources per item:
#   auto   → $BASE/results/$h.auto-score.json  .checks.<id>
#   visual → $BASE/scoring/$h/visual-score.json .scores.<id>   (0-5 integer)
#   manual → pending; score=0, pending_human_review=true
#
# Visual items carry a raw 0-5 from the model. We convert to item-weighted
# score via:
#   visual_score = raw_0_to_5 * (item.max / 5)
# ---------------------------------------------------------------------------

# Emit a JSON score record for a single harness.
# Reads: harness manifest, auto-score json, visual-score json, claude output json.
# Returns: JSON object (printed to stdout)
aggregate_harness() {
  local harness="$1"

  local manifest_file="${BASE}/results/${harness}.manifest.json"
  local auto_score_file="${BASE}/results/${harness}.auto-score.json"
  local visual_score_file="${BASE}/scoring/${harness}/visual-score.json"
  local claude_output_file="${BASE}/results/${harness}.json"
  local scoring_dir="${BASE}/scoring/${harness}"

  # ---- manifest fields -------------------------------------------------------
  local install_status run_status duration_seconds
  if [[ -f "$manifest_file" ]]; then
    install_status="$(jq -r '.install_status // "unknown"' "$manifest_file")"
    run_status="$(jq -r '.run_status // "unknown"' "$manifest_file")"
    duration_seconds="$(jq -r '.duration_seconds // 0' "$manifest_file")"
  else
    install_status="unknown"
    run_status="unknown"
    duration_seconds=0
    warn "[${harness}] manifest file missing: ${manifest_file}"
  fi

  # ---- claude output metrics -------------------------------------------------
  local input_tokens output_tokens cost_usd claude_duration_ms
  if [[ -f "$claude_output_file" ]] && jq -e '.usage' "$claude_output_file" &>/dev/null; then
    input_tokens="$(jq -r '.usage.input_tokens // 0' "$claude_output_file")"
    output_tokens="$(jq -r '.usage.output_tokens // 0' "$claude_output_file")"
    cost_usd="$(jq -r '.total_cost_usd // 0' "$claude_output_file")"
    claude_duration_ms="$(jq -r '.duration_ms // 0' "$claude_output_file")"
  else
    input_tokens=0
    output_tokens=0
    cost_usd=0
    claude_duration_ms=0
  fi

  # ---- screenshots -----------------------------------------------------------
  local screenshots_json="[]"
  if [[ -d "${scoring_dir}/screenshots" ]]; then
    screenshots_json="$(
      find "${scoring_dir}/screenshots" -name "*.png" -type f | sort | \
      sed "s|${BASE}/||" | jq -R . | jq -s .
    )"
  fi

  # ---- build items and categories via jq + checklist -------------------------
  # We pass the auto-score and visual-score blobs into jq for safe computation.

  local auto_score_blob="{}"
  if [[ -f "$auto_score_file" ]]; then
    auto_score_blob="$(jq '.checks // {}' "$auto_score_file")"
  fi

  local visual_score_blob="{}"
  if [[ -f "$visual_score_file" ]] && jq -e '.scores' "$visual_score_file" &>/dev/null; then
    visual_score_blob="$(jq '.scores // {}' "$visual_score_file")"
  fi

  # Use jq to compute items, categories, pending_manual list
  jq -n \
    --arg harness              "$harness" \
    --arg install_status       "$install_status" \
    --arg run_status           "$run_status" \
    --argjson duration_seconds "$duration_seconds" \
    --argjson input_tokens     "$input_tokens" \
    --argjson output_tokens    "$output_tokens" \
    --argjson cost_usd         "$cost_usd" \
    --argjson claude_duration_ms "$claude_duration_ms" \
    --argjson auto_checks      "$auto_score_blob" \
    --argjson visual_scores    "$visual_score_blob" \
    --argjson screenshots      "$screenshots_json" \
    --slurpfile checklist      "$CHECKLIST_JSON" \
    '
    # ----------------------------------------------------------------
    # helpers
    # ----------------------------------------------------------------
    def clamp01(v; mx): if mx == 0 then 0 else (v / mx) | if . > 1 then 1 elif . < 0 then 0 else . end end;

    # ----------------------------------------------------------------
    # build items map  { item_id: { score, max, source, ... } }
    # ----------------------------------------------------------------
    ($checklist[0].categories) as $cats |

    # flatten all items from checklist into a single array
    [ $cats[].items[] ] as $all_items |

    # build items map
    (
      $all_items | map(
        . as $item |
        ($item.id) as $id |
        (
          if $item.auto then
            # auto-scored item
            (($auto_checks[$id] // {score:0, max:$item.max}) | .score) as $raw_score |
            (($auto_checks[$id] // {score:0, max:$item.max}) | .evidence // "") as $ev |
            {
              ($id): {
                score:  $raw_score,
                max:    $item.max,
                source: "auto",
                evidence: $ev
              }
            }
          elif ($visual_scores | has($id)) then
            # visual-scored item: raw 0-5 converted to item weight
            (($visual_scores[$id].score // 0) | tonumber) as $raw_0_5 |
            (($visual_scores[$id].note  // "")           ) as $note |
            ($raw_0_5 * ($item.max / 5)) as $weighted_score |
            {
              ($id): {
                score:  $weighted_score,
                max:    $item.max,
                source: "visual",
                note:   $note
              }
            }
          elif ($item.id == "test-meaningful") then
            # manual item — always pending
            {
              ($id): {
                score:  0,
                max:    $item.max,
                source: "manual",
                pending_human_review: true
              }
            }
          else
            # visual item for which no visual-score exists yet
            {
              ($id): {
                score:  0,
                max:    $item.max,
                source: "visual",
                pending_human_review: true
              }
            }
          end
        )
      ) | add // {}
    ) as $items |

    # ----------------------------------------------------------------
    # build categories map
    #   category.score = sum(item.score) * (weight / items_sum)
    #   where items_sum = sum(item.max) for items in that category
    # ----------------------------------------------------------------
    (
      $cats | map(
        . as $cat |
        ($cat.items | map(.max) | add) as $items_sum |
        ($cat.items | map(.id) |
          map($items[.].score // 0) | add
        ) as $raw_sum |
        ($raw_sum * ($cat.weight / $items_sum)) as $cat_score |
        {
          ($cat.id): {
            score: ($cat_score | (. * 100 | round) / 100),
            max:   $cat.weight
          }
        }
      ) | add // {}
    ) as $categories |

    # ----------------------------------------------------------------
    # total score
    # ----------------------------------------------------------------
    ([ $categories[].score ] | add // 0) as $total_score |
    ([ $categories[].max   ] | add // 0) as $total_max |

    # ----------------------------------------------------------------
    # pending manual items
    # ----------------------------------------------------------------
    (
      [ $items | to_entries[] | select(.value.pending_human_review == true) | .key ]
    ) as $pending_manual |

    # ----------------------------------------------------------------
    # output
    # ----------------------------------------------------------------
    {
      install_status:   $install_status,
      run_status:       $run_status,
      duration_seconds: $duration_seconds,
      tokens: {
        input:  $input_tokens,
        output: $output_tokens
      },
      cost_usd:         $cost_usd,
      claude_duration_ms: $claude_duration_ms,
      categories:       $categories,
      items:            $items,
      total_score:      ($total_score | (. * 100 | round) / 100),
      total_max:        $total_max,
      screenshots:      $screenshots,
      pending_manual:   $pending_manual
    }
    '
}

# ---------------------------------------------------------------------------
# Build scores.json
# ---------------------------------------------------------------------------
build_scores_json() {
  local harnesses=("$@")
  local model
  model="$(read_model)"
  local generated_at
  generated_at="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  local checklist_version
  checklist_version="$(jq -r '.meta.version // "1.0"' "$CHECKLIST_JSON")"

  # Aggregate each harness
  local harnesses_obj="{}"
  for h in "${harnesses[@]}"; do
    info "Aggregating scores for harness: ${h}"
    local harness_json
    harness_json="$(aggregate_harness "$h")"
    harnesses_obj="$(echo "$harnesses_obj" | jq --arg k "$h" --argjson v "$harness_json" '. + {($k): $v}')"
  done

  # Build ranking array sorted descending by total_score
  local ranking_json
  ranking_json="$(
    echo "$harnesses_obj" | jq '[to_entries[] | {harness: .key, score: .value.total_score}] | sort_by(-.score)'
  )"

  jq -n \
    --arg base_dir              "$BASE" \
    --arg model                 "$model" \
    --arg generated_at          "$generated_at" \
    --arg checklist_version     "$checklist_version" \
    --argjson harnesses         "$harnesses_obj" \
    --argjson ranking           "$ranking_json" \
    '{
      meta: {
        base_dir:           $base_dir,
        model:              $model,
        generated_at:       $generated_at,
        checklist_version:  $checklist_version
      },
      harnesses: $harnesses,
      ranking:   $ranking
    }'
}

# ---------------------------------------------------------------------------
# Build report.md  (bash + jq, no Python)
# ---------------------------------------------------------------------------
build_report_md() {
  local scores_json_file="$1"
  local harnesses_arg=("${@:2}")

  local model
  model="$(jq -r '.meta.model' "$scores_json_file")"
  local generated_at
  generated_at="$(jq -r '.meta.generated_at' "$scores_json_file")"
  local date_only="${generated_at%%T*}"

  # Determine prompt path relative to repo root
  local prompt_display="benchmarks/prompt.md"

  # ---------------------------------------------------------------------------
  # Header
  # ---------------------------------------------------------------------------
  cat <<HEADER
# AI Harness Benchmark Report

> Prompt: 3D Creative Learning Platform MVP (${prompt_display})
> Model: ${model} (effort: max, 1M context)
> Date: ${date_only}
> Condition: identical raw prompt, \$HOME isolation, empty git-init project, --dangerously-skip-permissions

HEADER

  # ---------------------------------------------------------------------------
  # Summary table
  # ---------------------------------------------------------------------------
  echo "## Summary"
  echo ""
  echo "| Rank | Harness | Score | Build | Install | Time | Cost | Tokens (in/out) |"
  echo "|---|---|---|---|---|---|---|---|"

  local rank=1
  while IFS= read -r entry; do
    local h score
    h="$(echo "$entry" | jq -r '.harness')"
    score="$(echo "$entry" | jq -r '.score')"

    local install_status run_status duration_seconds input_tokens output_tokens cost_usd
    install_status="$(jq -r --arg h "$h" '.harnesses[$h].install_status' "$scores_json_file")"
    run_status="$(jq -r --arg h "$h" '.harnesses[$h].run_status' "$scores_json_file")"
    duration_seconds="$(jq -r --arg h "$h" '.harnesses[$h].duration_seconds' "$scores_json_file")"
    input_tokens="$(jq -r --arg h "$h" '.harnesses[$h].tokens.input' "$scores_json_file")"
    output_tokens="$(jq -r --arg h "$h" '.harnesses[$h].tokens.output' "$scores_json_file")"
    cost_usd="$(jq -r --arg h "$h" '.harnesses[$h].cost_usd' "$scores_json_file")"

    local total_max
    total_max="$(jq -r --arg h "$h" '.harnesses[$h].total_max' "$scores_json_file")"

    # Build status emoji
    local build_icon install_icon
    case "$run_status" in
      success) build_icon="ok" ;;
      timeout) build_icon="timeout" ;;
      skipped) build_icon="skipped" ;;
      *)       build_icon="fail" ;;
    esac
    case "$install_status" in
      success) install_icon="ok" ;;
      failed)  install_icon="fail" ;;
      *)       install_icon="${install_status}" ;;
    esac

    # Format time (seconds -> Xm Ys)
    local time_fmt
    if [[ "$duration_seconds" -gt 0 ]]; then
      local mins secs
      mins=$(( duration_seconds / 60 ))
      secs=$(( duration_seconds % 60 ))
      time_fmt="${mins}m${secs}s"
    else
      time_fmt="n/a"
    fi

    # Format tokens
    local tok_in_k tok_out_k
    tok_in_k="$(echo "$input_tokens" | awk '{printf "%dk", $1/1000}')"
    tok_out_k="$(echo "$output_tokens" | awk '{printf "%dk", $1/1000}')"

    # Format cost
    local cost_fmt
    if [[ "$cost_usd" != "0" && "$cost_usd" != "null" ]]; then
      cost_fmt="$(printf '$%.2f' "$cost_usd")"
    else
      cost_fmt="n/a"
    fi

    printf "| %d | %s | %.1f/%s | %s | %s | %s | %s | %s/%s |\n" \
      "$rank" "$h" "$score" "$total_max" \
      "$build_icon" "$install_icon" \
      "$time_fmt" "$cost_fmt" \
      "$tok_in_k" "$tok_out_k"

    rank=$(( rank + 1 ))
  done < <(jq -c '.ranking[]' "$scores_json_file")

  echo ""

  # ---------------------------------------------------------------------------
  # Screenshot comparison table
  # ---------------------------------------------------------------------------
  echo "## Screenshot Comparison"
  echo ""

  # Column headers
  local header_row="| |"
  local sep_row="|---|"
  for h in "${harnesses_arg[@]}"; do
    header_row+=" ${h} |"
    sep_row+="---|"
  done
  echo "$header_row"
  echo "$sep_row"

  local screenshot_labels=(
    "Landing|01-landing.png"
    "World Builder|02-world-builder.png"
    "AI Panel|03-ai-panel.png"
    "Gallery|04-gallery.png"
  )

  for label_file in "${screenshot_labels[@]}"; do
    local label="${label_file%%|*}"
    local fname="${label_file##*|}"
    local row="| ${label} |"
    for h in "${harnesses_arg[@]}"; do
      local img_path="screenshots/${h}/${fname}"
      row+=" ![]($img_path) |"
    done
    echo "$row"
  done

  echo ""

  # ---------------------------------------------------------------------------
  # Category breakdown tables
  # ---------------------------------------------------------------------------
  echo "## Category Breakdown"
  echo ""

  while IFS= read -r cat_entry; do
    local cat_id cat_name cat_weight
    cat_id="$(echo "$cat_entry" | jq -r '.id')"
    cat_name="$(echo "$cat_entry" | jq -r '.name')"
    cat_weight="$(echo "$cat_entry" | jq -r '.weight')"

    echo "### ${cat_name} (${cat_weight}pts)"
    echo ""

    # Table header
    local cat_header="| Item |"
    local cat_sep="|---|"
    for h in "${harnesses_arg[@]}"; do
      cat_header+=" ${h} |"
      cat_sep+="---|"
    done
    echo "$cat_header"
    echo "$cat_sep"

    # Items in this category
    while IFS= read -r item_entry; do
      local item_id item_desc item_max
      item_id="$(echo "$item_entry" | jq -r '.id')"
      item_desc="$(echo "$item_entry" | jq -r '.desc')"
      item_max="$(echo "$item_entry" | jq -r '.max')"
      local item_row="| ${item_desc} (/${item_max}) |"
      for h in "${harnesses_arg[@]}"; do
        local item_score
        item_score="$(jq -r --arg h "$h" --arg id "$item_id" \
          '.harnesses[$h].items[$id].score // 0' "$scores_json_file")"
        item_row+=" ${item_score} |"
      done
      echo "$item_row"
    done < <(echo "$cat_entry" | jq -c '.items[]')

    # Category total row
    local total_row="| **Category Total** |"
    for h in "${harnesses_arg[@]}"; do
      local cat_score
      cat_score="$(jq -r --arg h "$h" --arg cid "$cat_id" \
        '.harnesses[$h].categories[$cid].score // 0' "$scores_json_file")"
      total_row+=" **${cat_score}** |"
    done
    echo "$total_row"
    echo ""

  done < <(jq -c '.categories[]' "$CHECKLIST_JSON")

  # ---------------------------------------------------------------------------
  # Meta metrics table
  # ---------------------------------------------------------------------------
  echo "## Meta Metrics"
  echo ""
  local meta_header="| |"
  local meta_sep="|---|"
  for h in "${harnesses_arg[@]}"; do
    meta_header+=" ${h} |"
    meta_sep+="---|"
  done
  echo "$meta_header"
  echo "$meta_sep"

  # Wall Clock Time
  local time_row="| Wall Clock Time |"
  for h in "${harnesses_arg[@]}"; do
    local ds
    ds="$(jq -r --arg h "$h" '.harnesses[$h].duration_seconds' "$scores_json_file")"
    if [[ "$ds" -gt 0 ]]; then
      time_row+=" $(( ds / 60 ))m$(( ds % 60 ))s |"
    else
      time_row+=" n/a |"
    fi
  done
  echo "$time_row"

  # Total Tokens
  local tok_row="| Total Tokens |"
  for h in "${harnesses_arg[@]}"; do
    local tin tout total_tok
    tin="$(jq -r --arg h "$h" '.harnesses[$h].tokens.input' "$scores_json_file")"
    tout="$(jq -r --arg h "$h" '.harnesses[$h].tokens.output' "$scores_json_file")"
    total_tok=$(( tin + tout ))
    if [[ "$total_tok" -gt 0 ]]; then
      tok_row+=" $(echo "$total_tok" | awk '{printf "%dk", $1/1000}') |"
    else
      tok_row+=" n/a |"
    fi
  done
  echo "$tok_row"

  # Cost
  local cost_row="| Cost (USD) |"
  for h in "${harnesses_arg[@]}"; do
    local cu
    cu="$(jq -r --arg h "$h" '.harnesses[$h].cost_usd' "$scores_json_file")"
    if [[ "$cu" != "0" && "$cu" != "null" ]]; then
      cost_row+=" $(printf '$%.2f' "$cu") |"
    else
      cost_row+=" n/a |"
    fi
  done
  echo "$cost_row"

  # Install Status
  local inst_row="| Install Status |"
  for h in "${harnesses_arg[@]}"; do
    local is
    is="$(jq -r --arg h "$h" '.harnesses[$h].install_status' "$scores_json_file")"
    inst_row+=" ${is} |"
  done
  echo "$inst_row"

  # Run Status
  local run_row="| Run Status |"
  for h in "${harnesses_arg[@]}"; do
    local rs
    rs="$(jq -r --arg h "$h" '.harnesses[$h].run_status' "$scores_json_file")"
    run_row+=" ${rs} |"
  done
  echo "$run_row"

  echo ""

  # ---------------------------------------------------------------------------
  # Methodology
  # ---------------------------------------------------------------------------
  cat <<METHODOLOGY
## Methodology

- Isolation: \$HOME override per harness
- Initial state: empty directory + git init
- Prompt: identical raw prompt, no harness workflow
- Permissions: --dangerously-skip-permissions
- Model: ${model} with --effort max
- Budget cap: \$20 per run
- Time limit: 60 minutes per run
- Reproduction: see benchmarks/run.sh

METHODOLOGY

  # ---------------------------------------------------------------------------
  # Per-harness notes
  # ---------------------------------------------------------------------------
  echo "## Per-harness Notes"
  echo ""

  for h in "${harnesses_arg[@]}"; do
    local install_status run_status pending_manual_json
    install_status="$(jq -r --arg h "$h" '.harnesses[$h].install_status' "$scores_json_file")"
    run_status="$(jq -r --arg h "$h" '.harnesses[$h].run_status' "$scores_json_file")"
    pending_manual_json="$(jq -r --arg h "$h" '[.harnesses[$h].pending_manual[]?] | join(", ")' "$scores_json_file")"

    echo "### ${h}"
    echo ""
    echo "- Install: ${install_status}"
    echo "- Run: ${run_status}"
    if [[ -n "$pending_manual_json" ]]; then
      echo "- Pending manual review: ${pending_manual_json}"
    fi

    # Install log excerpt (last 10 lines if present)
    local install_log_file="${BASE}/results/${h}.install.log"
    if [[ -f "$install_log_file" ]]; then
      echo "- Install log (tail):"
      echo '  ```'
      tail -n 10 "$install_log_file" | sed 's/^/  /'
      echo '  ```'
    fi

    # auto-score errors
    local auto_errors_json
    auto_errors_json="$(jq -r --arg h "$h" \
      'if (.harnesses[$h].items | to_entries | map(select(.value.source == "auto" and .value.score == 0)) | length) > 0
       then .harnesses[$h].items | to_entries | map(select(.value.source == "auto" and .value.score == 0)) | map(.key) | join(", ")
       else ""
       end' "$scores_json_file" 2>/dev/null || true)"
    if [[ -n "$auto_errors_json" ]]; then
      echo "- Auto-score failures: ${auto_errors_json}"
    fi

    echo ""
  done
}

# ---------------------------------------------------------------------------
# Copy artifacts to the repo tree
# ---------------------------------------------------------------------------
copy_artifacts() {
  local harnesses=("$@")

  mkdir -p "$REPO_RUNS_DIR" "$REPO_SCREENSHOTS_DIR" "$REPO_RESULTS_DIR"

  for h in "${harnesses[@]}"; do
    local project_src="${BASE}/projects/${h}"
    local project_dst="${REPO_RUNS_DIR}/${h}"
    local screenshots_src="${BASE}/scoring/${h}/screenshots"
    local screenshots_dst="${REPO_SCREENSHOTS_DIR}/${h}"

    info "Copying project code: ${h} -> ${project_dst}"
    if [[ -d "$project_src" ]]; then
      sync_tree "$project_src" "$project_dst"
    else
      warn "  Project dir not found, skipping: ${project_src}"
    fi

    info "Copying screenshots: ${h} -> ${screenshots_dst}"
    sync_screenshots "$screenshots_src" "$screenshots_dst"
  done

  info "Copying final reports to ${REPO_RESULTS_DIR}"
  cp -f "${BASE}/results/scores.json" "${REPO_RESULTS_DIR}/scores.json"
  cp -f "${BASE}/results/report.md"   "${REPO_RESULTS_DIR}/report.md"
}

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
main() {
  preflight_check

  info "collect.sh starting"
  info "BASE: ${BASE}"

  # Read harness list from run manifest
  local harnesses=()
  while IFS= read -r h; do
    harnesses+=("$h")
  done < <(read_harnesses)

  if [[ "${#harnesses[@]}" -eq 0 ]]; then
    err "No harnesses found in ${RUN_MANIFEST}"
    exit 1
  fi

  info "Harnesses: ${harnesses[*]}"

  # ---- Phase 1: scoring scripts ---------------------------------------------
  for h in "${harnesses[@]}"; do
    run_auto_score   "$h" || warn "[${h}] auto-score had errors, continuing"
    run_visual_score "$h" || warn "[${h}] visual-score had errors, continuing"
  done

  # ---- Phase 2: aggregate scores.json ---------------------------------------
  info "Building scores.json..."
  local scores_json_file="${BASE}/results/scores.json"
  build_scores_json "${harnesses[@]}" > "$scores_json_file"
  info "scores.json written: ${scores_json_file}"

  # ---- Phase 3: report.md ---------------------------------------------------
  info "Building report.md..."
  local report_md_file="${BASE}/results/report.md"
  build_report_md "$scores_json_file" "${harnesses[@]}" > "$report_md_file"
  info "report.md written: ${report_md_file}"

  # ---- Phase 4: copy artifacts to repo tree ---------------------------------
  info "Copying artifacts to repo tree..."
  copy_artifacts "${harnesses[@]}"

  info "collect.sh complete."
  info "  scores.json : ${scores_json_file}"
  info "  report.md   : ${report_md_file}"
  echo "$scores_json_file"
}

main "$@"
