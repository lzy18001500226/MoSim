#!/usr/bin/env bash
# journey-judge.sh — drive a running dev server through 5 user journeys via
# chrome-devtools MCP, capture screenshots, and emit per-journey scores.
#
# Usage:
#   ./journey-judge.sh <project-dir> <harness-id> <output-dir> <dev-url>
#
# Output (stdout): JSON object mapping journey ids to {score, max, evidence}.
# Side effects: writes screenshots to <output-dir>/screenshots/

set -uo pipefail

if [[ $# -ne 4 ]]; then
  echo "Usage: $0 <project-dir> <harness-id> <output-dir> <dev-url>" >&2
  exit 1
fi

PROJECT_DIR="$1"
HARNESS="$2"
OUTPUT_DIR="$3"
DEV_URL="$4"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

mkdir -p "$OUTPUT_DIR/screenshots"

MCP_CONFIG="$(mktemp -t chrome-mcp-XXXXXX.json)"
trap 'rm -f "$MCP_CONFIG"' EXIT
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

PROMPT="You are evaluating a children's 3D world-building web app at ${DEV_URL}.
Use the chrome-devtools MCP tools to drive Chrome and verify these 5 user journeys.
Save one screenshot per journey to ${OUTPUT_DIR}/screenshots/ as PNG.

For each journey, decide a score 0-N where N is the listed max:

1. journey-onboard (max 3): Navigate to /. Is there a clear 'Start Creating' /
   onboarding entry visible without scrolling? PASS=3 if yes; 1.5 if hidden but
   reachable; 0 if absent. Save screenshots/01-landing.png.

2. journey-builder (max 4): Navigate to the world builder route (try /create,
   /builder, or click the start button). Does a Three.js Canvas render with
   floor/grid? Are there object/shape pickers in a sidebar? PASS=4 if Canvas
   renders + pickers visible; 2 if Canvas renders but no pickers; 0 if neither.
   Save screenshots/02-builder.png.

3. journey-ai (max 3): Find the AI panel/buddy (sidebar or floating). Type
   something like 'help me' and submit. Does it return a non-empty response?
   PASS=3 if response appears; 1.5 if input visible but no response; 0 if no AI
   panel found. Save screenshots/03-ai-panel.png.

4. journey-save (max 3): If a save/save-world button exists, click it. Reload
   the page. Does the previously-saved state remain (e.g., world name or
   objects)? PASS=3 if state persists; 1.5 if save UI exists but reload loses
   state; 0 if no save mechanism. Save screenshots/04-save-after-reload.png.

5. journey-gallery (max 2): Navigate to /gallery (or whatever the gallery route
   is). Does a grid/list of saved worlds appear (even empty-state cards count)?
   PASS=2 if gallery UI renders; 1 if route exists but blank; 0 if route 404.
   Save screenshots/05-gallery.png.

Return STRICT JSON only (no prose). Schema:
{
  \"journey-onboard\":  {\"score\": 0-3, \"max\": 3, \"evidence\": \"<one sentence>\"},
  \"journey-builder\":  {\"score\": 0-4, \"max\": 4, \"evidence\": \"<one sentence>\"},
  \"journey-ai\":       {\"score\": 0-3, \"max\": 3, \"evidence\": \"<one sentence>\"},
  \"journey-save\":     {\"score\": 0-3, \"max\": 3, \"evidence\": \"<one sentence>\"},
  \"journey-gallery\":  {\"score\": 0-2, \"max\": 2, \"evidence\": \"<one sentence>\"}
}

EMIT JSON ONLY."

RAW="$OUTPUT_DIR/journey-raw-claude.json"
( cd "$OUTPUT_DIR" && timeout 360 claude -p "$PROMPT" \
    --dangerously-skip-permissions \
    --model claude-opus-4-6 \
    --effort high \
    --output-format json \
    --max-budget-usd 3 \
    --no-session-persistence \
    --setting-sources project,local \
    --mcp-config "$MCP_CONFIG" \
    --strict-mcp-config \
    --add-dir "$OUTPUT_DIR" ) > "$RAW" 2>>"$OUTPUT_DIR/multiaxis.log"

# Extract inner JSON
inner="$(jq -r '.result // "{}"' "$RAW" 2>/dev/null)"
echo "$inner"
