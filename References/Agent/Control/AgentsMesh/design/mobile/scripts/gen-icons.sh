#!/bin/bash
# Generate lucide-style PNG icons for the mobile design system.
# Source SVG paths copied from lucide.dev (24x24 viewBox).
# Output: design/mobile/assets/lucide-png/<name>-<color>.png at 48×48 px (2×).

set -e
cd "$(dirname "$0")/.."
OUT="assets/lucide-png"
mkdir -p "$OUT"

# Render an icon with a given name, color (hex w/o #), and SVG inner content.
render() {
    local name="$1"
    local color="$2"
    local stroke_width="${3:-2}"
    local fill="${4:-none}"
    local inner="$5"

    local svg="$OUT/${name}-${color}.svg"
    cat > "$svg" <<EOF
<svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="$fill" stroke="#$color" stroke-width="$stroke_width" stroke-linecap="round" stroke-linejoin="round">$inner</svg>
EOF
    rsvg-convert "$svg" -o "$OUT/${name}-${color}.png"
}

# === Tab icons (outline) ===
TERMINAL='<polyline points="4 17 10 11 4 5"/><line x1="12" y1="19" x2="20" y2="19"/>'
MESSAGE='<path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>'
TICKET='<path d="M2 9a3 3 0 0 1 0 6v2a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2v-2a3 3 0 0 1 0-6V7a2 2 0 0 0-2-2H4a2 2 0 0 0-2 2Z"/><path d="M13 5v2"/><path d="M13 11v2"/><path d="M13 17v2"/>'
BLOCKS='<rect width="7" height="7" x="14" y="3" rx="1"/><path d="M10 21V8a1 1 0 0 0-1-1H4a1 1 0 0 0-1 1v12a1 1 0 0 0 1 1h12a1 1 0 0 0 1-1v-5a1 1 0 0 0-1-1H3"/>'
ELLIPSIS='<circle cx="12" cy="12" r="1"/><circle cx="19" cy="12" r="1"/><circle cx="5" cy="12" r="1"/>'

# Outline colors: active blue + inactive gray + dark inactive
for spec in \
    "terminal:0969DA:2:none:$TERMINAL" \
    "terminal:8E8E93:2:none:$TERMINAL" \
    "terminal:6E7681:2:none:$TERMINAL" \
    "message:0969DA:2:none:$MESSAGE" \
    "message:8E8E93:2:none:$MESSAGE" \
    "message:6E7681:2:none:$MESSAGE" \
    "ticket:0969DA:2:none:$TICKET" \
    "ticket:8E8E93:2:none:$TICKET" \
    "ticket:6E7681:2:none:$TICKET" \
    "blocks:0969DA:2:none:$BLOCKS" \
    "blocks:8E8E93:2:none:$BLOCKS" \
    "blocks:6E7681:2:none:$BLOCKS" \
    "ellipsis:0969DA:2:0969DA:$ELLIPSIS" \
    "ellipsis:8E8E93:2:8E8E93:$ELLIPSIS" \
    "ellipsis:6E7681:2:6E7681:$ELLIPSIS" \
; do
    IFS=":" read -r name color sw fill inner <<<"$spec"
    render "$name" "$color" "$sw" "$fill" "$inner"
done

# === Tab icons (filled, active) — solid blue with white interior strokes/fills ===
# terminal_filled: thicker stroke
render "terminal-filled" "0969DA" "3" "none" "$TERMINAL"
# Closed shapes filled
render "message-filled" "0969DA" "2" "#0969DA" "$MESSAGE"
render "ticket-filled" "0969DA" "2" "#0969DA" "$TICKET"
render "blocks-filled" "0969DA" "2" "#0969DA" "$BLOCKS"
# ellipsis already filled

# === Nav action icons ===
SEARCH='<circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/>'
PLUS='<path d="M5 12h14"/><path d="M12 5v14"/>'
CHEVRON_LEFT='<path d="m15 18-6-6 6-6"/>'
COG='<path d="M12.22 2h-.44a2 2 0 0 0-2 2v.18a2 2 0 0 1-1 1.73l-.43.25a2 2 0 0 1-2 0l-.15-.08a2 2 0 0 0-2.73.73l-.22.38a2 2 0 0 0 .73 2.73l.15.1a2 2 0 0 1 1 1.72v.51a2 2 0 0 1-1 1.74l-.15.09a2 2 0 0 0-.73 2.73l.22.38a2 2 0 0 0 2.73.73l.15-.08a2 2 0 0 1 2 0l.43.25a2 2 0 0 1 1 1.73V20a2 2 0 0 0 2 2h.44a2 2 0 0 0 2-2v-.18a2 2 0 0 1 1-1.73l.43-.25a2 2 0 0 1 2 0l.15.08a2 2 0 0 0 2.73-.73l.22-.39a2 2 0 0 0-.73-2.73l-.15-.08a2 2 0 0 1-1-1.74v-.5a2 2 0 0 1 1-1.74l.15-.09a2 2 0 0 0 .73-2.73l-.22-.38a2 2 0 0 0-2.73-.73l-.15.08a2 2 0 0 1-2 0l-.43-.25a2 2 0 0 1-1-1.73V4a2 2 0 0 0-2-2z"/><circle cx="12" cy="12" r="3"/>'
CLOSE='<path d="M18 6 6 18"/><path d="m6 6 12 12"/>'

for spec in \
    "search:0969DA:2:none:$SEARCH" \
    "plus:0969DA:2.5:none:$PLUS" \
    "back:0969DA:2.5:none:$CHEVRON_LEFT" \
    "back:58A6FF:2.5:none:$CHEVRON_LEFT" \
    "cog:0969DA:2:none:$COG" \
    "cog:8B949E:2:none:$COG" \
    "close:8E8E93:2.5:none:$CLOSE" \
    "close:C9D1D9:2.5:none:$CLOSE" \
; do
    IFS=":" read -r name color sw fill inner <<<"$spec"
    render "$name" "$color" "$sw" "$fill" "$inner"
done

# Cleanup .svg intermediates (keep only .png)
rm -f "$OUT"/*.svg

echo "Generated $(ls "$OUT" | wc -l | tr -d ' ') PNG icons in $OUT"
