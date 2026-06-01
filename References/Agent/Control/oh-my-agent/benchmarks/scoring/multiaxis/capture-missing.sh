#!/usr/bin/env bash
# capture-missing.sh — fill specific screenshot gaps for a harness using
# chrome-devtools MCP without re-running full visual scoring.
#
# Usage:
#   ./capture-missing.sh <project-dir> <output-screenshots-dir> <gaps-csv>
#
# gaps-csv example: "env-theme,save-reload,tablet"
# Recognized gap names:
#   env-theme    -> 06-theme-change.png (click an Environment chip)
#   save-reload  -> 04-save-after-reload.png (save world, reload, screenshot)
#   tablet       -> 07-tablet-layout.png (resize to 800x1100, screenshot builder)
#   onboarding   -> 00-onboarding.png (capture /onboarding or first-time UI)

set -uo pipefail

if [[ $# -ne 3 ]]; then
  echo "Usage: $0 <project-dir> <output-screenshots-dir> <gaps-csv>" >&2
  exit 1
fi

PROJECT_DIR="$1"
SHOTS_DIR="$2"
GAPS="$3"
mkdir -p "$SHOTS_DIR"

# Detect package manager
PM=npm
[[ -f "$PROJECT_DIR/pnpm-lock.yaml" || -f "$PROJECT_DIR/pnpm-workspace.yaml" ]] && PM=pnpm
[[ -f "$PROJECT_DIR/yarn.lock" ]] && PM=yarn
[[ -f "$PROJECT_DIR/bun.lock" || -f "$PROJECT_DIR/bun.lockb" ]] && PM=bun

# Find a free port
PORT="$(node -e 'const s=require("net").createServer();s.listen(0,()=>{const p=s.address().port;s.close(()=>console.log(p));})')"

# Start dev server
case "$PM" in
  pnpm) DEV="pnpm dev" ;;
  yarn) DEV="yarn dev" ;;
  bun)  DEV="bun run dev" ;;
  *)    DEV="npm run dev" ;;
esac

echo "Starting dev server (port $PORT) in $PROJECT_DIR ..." >&2
( cd "$PROJECT_DIR" && PORT="$PORT" eval "$DEV" > /tmp/capture-dev.log 2>&1 ) &
DEV_PID=$!

# Wait for boot
for i in $(seq 1 45); do
  sleep 1
  curl -sf -m 2 "http://localhost:$PORT/" -o /dev/null 2>/dev/null && break
done

if ! curl -sf -m 2 "http://localhost:$PORT/" -o /dev/null 2>/dev/null; then
  echo "ERROR: dev server never responded on port $PORT" >&2
  kill -KILL "$DEV_PID" 2>/dev/null
  exit 1
fi
echo "dev server up at http://localhost:$PORT" >&2

# MCP config
MCP_CONFIG="$(mktemp -t cmcp-XXXXXX.json)"
trap 'rm -f "$MCP_CONFIG"; kill -KILL "$DEV_PID" 2>/dev/null; lsof -ti tcp:'"$PORT"' 2>/dev/null | xargs -r kill -KILL 2>/dev/null' EXIT
cat > "$MCP_CONFIG" <<'EOF'
{ "mcpServers": { "chrome-devtools": { "command": "npx", "args": ["-y", "chrome-devtools-mcp@latest"] } } }
EOF

# Build instruction set per gap
INSTRUCTIONS="DEV server is running at http://localhost:$PORT.
Use chrome-devtools MCP to capture the following screenshots into $SHOTS_DIR/.
For each, navigate, perform any required interaction, then screenshot.
"

case ",$GAPS," in *,env-theme,*)
  INSTRUCTIONS+="
- env-theme: navigate to the world-builder route. Find the Environment / theme
  picker (chips or list at the bottom or in the sidebar — labels like 'Sunny
  Meadow', 'Starry Night', 'Underwater', 'Ocean', etc.). Click a different
  theme to change it. Screenshot the page after the theme has changed.
  Save as $SHOTS_DIR/06-theme-change.png.
" ;; esac

case ",$GAPS," in *,save-reload,*)
  INSTRUCTIONS+="
- save-reload: navigate to the world-builder, place at least one object, set a
  world name if asked, then click the Save button. Wait for any confirmation.
  Reload the page (or navigate away and back). Take a screenshot showing the
  saved world is restored or visible (e.g., name in title, object still on
  canvas, or 'My Worlds' card showing this world).
  Save as $SHOTS_DIR/04-save-after-reload.png.
" ;; esac

case ",$GAPS," in *,tablet,*)
  INSTRUCTIONS+="
- tablet: use chrome-devtools to resize the viewport to 800x1100 (tablet
  portrait). Navigate to the world-builder route. Screenshot the responsive
  layout. Save as $SHOTS_DIR/07-tablet-layout.png.
" ;; esac

case ",$GAPS," in *,onboarding,*)
  INSTRUCTIONS+="
- onboarding: try /onboarding or the first-run flow. If /onboarding exists,
  capture it. Otherwise capture whatever 'first-time user' screen the landing
  page transitions into when 'Start' is clicked.
  Save as $SHOTS_DIR/00-onboarding.png.
" ;; esac

INSTRUCTIONS+="
After all captures, reply with a one-line JSON summary:
{\"captured\": [\"<filename1>\", ...], \"skipped\": [\"<id>: <reason>\", ...]}
"

echo "Asking claude+chrome-devtools to capture: $GAPS" >&2

cd "$SHOTS_DIR"
timeout 240 claude -p "$INSTRUCTIONS" \
  --dangerously-skip-permissions \
  --model claude-opus-4-6 \
  --effort high \
  --output-format json \
  --max-budget-usd 2 \
  --no-session-persistence \
  --setting-sources project,local \
  --mcp-config "$MCP_CONFIG" \
  --strict-mcp-config \
  --add-dir "$SHOTS_DIR" \
  > /tmp/capture-result.json 2>&1

echo "result summary:" >&2
jq -r '.result // "no result"' /tmp/capture-result.json 2>&1 | tail -5 >&2

ls "$SHOTS_DIR" | grep -E "(06-theme|04-save|07-tablet|00-onbo)" >&2 || echo "(no targeted files found)" >&2
