#!/usr/bin/env bash
# visual-score.sh — Start a harness project's dev server, capture screenshots via
# Chrome DevTools MCP, and have Claude score the UX.
#
# Usage:
#   ./visual-score.sh <project-dir> <harness-id> <output-dir>
#
# Example:
#   ./visual-score.sh /tmp/oma-bench/projects/vanilla vanilla /tmp/oma-bench/scoring/vanilla
#
# ─── INVESTIGATION FINDINGS ──────────────────────────────────────────────────
#
# 1. Chrome DevTools MCP package
#    Package: chrome-devtools-mcp (Apache-2.0, published by ChromeDevTools team)
#    Latest:  0.21.0 (published ~2025-04-04)
#    npm URL: https://registry.npmjs.org/chrome-devtools-mcp
#    Command: npx -y chrome-devtools-mcp@latest  ← confirmed valid
#
# 2. claude -p --output-format json output structure
#    Top-level keys (observed via `claude -p "say hi" --output-format json`):
#      .type             "result"
#      .subtype          "success"
#      .is_error         false
#      .result           <string>  ← THIS is the model's actual text output
#      .stop_reason      "end_turn"
#      .session_id       "..."
#      .total_cost_usd   0.107
#      .usage            { input_tokens, output_tokens, ... }
#      .duration_ms      3799
#    Extraction: jq -r '.result' on the raw JSON file gives the text response.
#    The score-prompt.md instructs the model to emit a JSON object as its sole
#    stdout, so .result will contain that JSON string.
#
# 3. --mcp-config flag behavior
#    Accepts one or more file paths (space-separated) or inline JSON strings.
#    Usage: --mcp-config /path/to/config.json
#    The flag does NOT require --strict-mcp-config; existing MCP servers from
#    .mcp.json are merged unless --strict-mcp-config is also passed.
#    We add --strict-mcp-config here to ensure only chrome-devtools-mcp is
#    active during scoring (avoids accidental tool use from project-local MCP
#    config).
#
# ─────────────────────────────────────────────────────────────────────────────

set -uo pipefail

# ── argument validation ───────────────────────────────────────────────────────
if [[ $# -ne 3 ]]; then
  echo "Usage: $0 <project-dir> <harness-id> <output-dir>" >&2
  exit 1
fi

PROJECT_DIR="$1"
HARNESS="$2"
OUTPUT_DIR="$3"

if [[ ! -d "$PROJECT_DIR" ]]; then
  echo "ERROR: project-dir does not exist: $PROJECT_DIR" >&2
  exit 1
fi

# ── dependency checks ─────────────────────────────────────────────────────────
for cmd in claude jq npx; do
  if ! command -v "$cmd" &>/dev/null; then
    echo "ERROR: required command not found in PATH: $cmd" >&2
    exit 1
  fi
done

# ── setup ─────────────────────────────────────────────────────────────────────
mkdir -p "$OUTPUT_DIR/screenshots"

SCORE_PROMPT_FILE="$(cd "$(dirname "$0")" && pwd)/score-prompt.md"
if [[ ! -f "$SCORE_PROMPT_FILE" ]]; then
  echo "ERROR: score-prompt.md not found at: $SCORE_PROMPT_FILE" >&2
  exit 1
fi

# Temp file for MCP config — cleaned up on exit
MCP_CONFIG="$(mktemp -t chrome-mcp-XXXXXX.json)"
trap 'rm -f "$MCP_CONFIG"' EXIT

# ── MCP config ────────────────────────────────────────────────────────────────
# chrome-devtools-mcp v0.21.0 — official ChromeDevTools team package.
# npx -y downloads it on first use; no global install required.
cat > "$MCP_CONFIG" <<'EOF'
{
  "mcpServers": {
    "chrome-devtools": {
      "command": "npx",
      "args": ["-y", "chrome-devtools-mcp@latest"]
    }
  }
}
EOF

# ── build the prompt (inject harness id) ──────────────────────────────────────
# The score-prompt.md uses "<harness id>" as a placeholder in its output spec;
# we prepend a one-line instruction so the model fills it with the real value.
PROMPT="Your harness ID for this run is: ${HARNESS}

$(cat "$SCORE_PROMPT_FILE")"

# ── run claude -p with retries ───────────────────────────────────────────────
# Timeout: 300 s (5 min) per attempt — generous for install + dev-server boot
#   + 4 screenshots.
# --strict-mcp-config: use only the chrome-devtools MCP, ignore any .mcp.json
#   present in the project directory.
# --add-dir: grants file-system access to the project tree.
# --no-session-persistence: each scoring run is isolated.
#
# Retry policy: up to MAX_ATTEMPTS times if the model returns an empty
# response or an unparseable JSON. Empty responses have been observed when
# the dev server fails to boot in time or the MCP server isn't ready;
# a fresh attempt usually succeeds.
echo "Starting visual scoring for harness '${HARNESS}' in ${PROJECT_DIR} ..." >&2

MAX_ATTEMPTS=3
ATTEMPT=0
SCORE_OK=false

# Helper: report whether the raw JSON contains a non-empty result body that
# parses to either valid JSON or non-trivial text.
result_is_valid() {
  local raw="$1"
  [[ -s "$raw" ]] || return 1
  local result
  result="$(jq -r '.result // empty' "$raw" 2>/dev/null)"
  # Strip whitespace
  result="${result#"${result%%[![:space:]]*}"}"
  result="${result%"${result##*[![:space:]]}"}"
  [[ -n "$result" ]] || return 1
  # If the prompt asked for JSON, prefer valid JSON; otherwise any non-empty
  # text counts. We try JSON first.
  if echo "$result" | jq -e . >/dev/null 2>&1; then
    return 0
  fi
  # Non-JSON but non-trivial (>100 chars suggests model produced something)
  [[ ${#result} -gt 100 ]]
}

while (( ATTEMPT < MAX_ATTEMPTS )); do
  ATTEMPT=$(( ATTEMPT + 1 ))
  echo "  attempt ${ATTEMPT}/${MAX_ATTEMPTS}..." >&2

  (
    cd "$PROJECT_DIR"
    timeout 300 claude -p "$PROMPT" \
      --dangerously-skip-permissions \
      --model claude-opus-4-6 \
      --effort max \
      --output-format json \
      --max-budget-usd 5 \
      --no-session-persistence \
      --mcp-config "$MCP_CONFIG" \
      --strict-mcp-config \
      --add-dir "$PROJECT_DIR"
  ) > "$OUTPUT_DIR/visual-score-raw.json" \
    2>> "$OUTPUT_DIR/visual-score.stderr"

  EXIT_CODE=$?

  if [[ $EXIT_CODE -ne 0 ]]; then
    echo "  attempt ${ATTEMPT}: claude exited ${EXIT_CODE}" >&2
    continue
  fi

  if result_is_valid "$OUTPUT_DIR/visual-score-raw.json"; then
    SCORE_OK=true
    break
  fi

  echo "  attempt ${ATTEMPT}: empty/invalid result; retrying..." >&2
  # Preserve the failed raw for debugging
  cp "$OUTPUT_DIR/visual-score-raw.json" "$OUTPUT_DIR/visual-score-raw.attempt${ATTEMPT}.json" 2>/dev/null || true
done

# ── move screenshots captured inside the project dir ─────────────────────────
# score-prompt.md asks Claude to save to screenshots/ inside PROJECT_DIR.
if [[ -d "${PROJECT_DIR}/screenshots" ]]; then
  mv "${PROJECT_DIR}/screenshots"/*.png "$OUTPUT_DIR/screenshots/" 2>/dev/null || true
fi

# ── extract the inner result JSON ─────────────────────────────────────────────
if [[ "$SCORE_OK" == true ]]; then
  jq -r '.result' "$OUTPUT_DIR/visual-score-raw.json" > "$OUTPUT_DIR/visual-score.json"
  echo "Scores written to: ${OUTPUT_DIR}/visual-score.json (after ${ATTEMPT} attempt(s))" >&2
else
  echo "WARNING: visual-score gave up after ${MAX_ATTEMPTS} attempts. Raw JSON files preserved in ${OUTPUT_DIR}/" >&2
  # Write a minimal stub so downstream collect.sh doesn't choke on truly empty file
  echo '{"harness":"'"$HARNESS"'","error":"visual-score returned empty after '"$MAX_ATTEMPTS"' retries"}' \
    > "$OUTPUT_DIR/visual-score.json"
fi
