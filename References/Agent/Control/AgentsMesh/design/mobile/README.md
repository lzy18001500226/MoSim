# Mobile Design System

iOS-specific design language for AgentsMesh. Borrows from Apple HIG iOS 26
(Liquid Glass material, floating tab bar, large radii) and Lark's mobile
multi-workspace drawer pattern. Visual language stays aligned with the web
client (same `lucide-react`-flavored icons, same accent #0969DA).

## Source of truth

`.pastel` files in this directory are SSOT. PNGs under `../out/` are rendered
artifacts (gitignored). Update tokens / components first, then pages.

## Layout

```
mobile/
├── tokens/
│   ├── typography.pastel    # iOS HIG type ramp (large title 34 / body 17 / footnote 13)
│   ├── layout.pastel        # device + chrome + list metrics
│   ├── material.pastel      # Liquid Glass surfaces, shadows, page bg
│   └── radius.pastel        # iOS 26 radius ladder (4 / 8 / 12 / 16 / 22 / 28 / 999)
├── assets/
│   └── lucide-png/          # PNG icons rendered from real lucide SVGs (see Icons below)
├── scripts/
│   └── gen-icons.sh         # SVG → PNG generator (requires rsvg-convert)
├── components/
│   ├── status-bar.pastel    # Dynamic Island 59pt + notch 47pt + dark variant
│   ├── nav-bar.pastel       # avatar (drawer entry) + title + actions · 4 variants
│   ├── tab-bar.pastel       # floating capsule 361×56 · default / unread / dark
│   ├── icon.pastel          # 5 tab icons × outline+filled + 5 nav action icons (PNG)
│   ├── list-cell.pastel     # 6 cell types · inset-grouped · soft separators
│   ├── section-header.pastel# 32pt · 13pt uppercase #6D6D72
│   ├── segment.pastel       # 2 / 3 / 4-way · 32pt outer
│   ├── avatar.pastel        # circle (people) / rounded-square (org/pod/agent) × 5 size
│   ├── chip.pastel          # role / status / mode pills · radius 4pt · 11pt
│   ├── cta-button.pastel    # primary / secondary / destructive · 52pt · radius 12
│   └── sheet-header.pastel  # grabber + Cancel + title + Save
├── ia/
│   └── ios-sitemap.pastel   # 5-tab IA + per-tab Stack + cuts
└── pages/
    ├── ios-shell-tabbar.pastel  # container template (status + nav + tabs)
    ├── ios-pods-grid.pastel     # Chrome tab-switcher style Pod grid (default Pods view)
    ├── ios-pods-list.pastel     # Alternative list view for Pods
    ├── ios-pod-terminal.pastel  # full-screen push, dark surface
    ├── ios-channels-list.pastel · ios-channel-detail.pastel
    ├── ios-tickets-board.pastel · ios-ticket-detail.pastel
    ├── ios-blocks-list.pastel   · ios-block-detail.pastel
    ├── ios-more.pastel
    ├── ios-create-pod-sheet.pastel
    └── ios-org-drawer.pastel    # Lark-style drawer
```

## Design principles

1. **iOS 26 native** — Liquid Glass surfaces (`#FFFFFFE6`), floating tab bar (capsule, 16pt above safe-bottom), generous radii (12 / 16 / 22 / 28), filled active icons.
2. **Lark-style drawer for orgs** — top-left avatar opens a left drawer with an org rail (60pt) + account menu (280pt). Replaces the previous bottom-sheet org switcher.
3. **lucide visual parity with web/desktop** — tab icons drawn in pastel mimic `lucide-react` shapes used by `clients/web` (Terminal / MessageSquare / Ticket / Blocks / Ellipsis). No emoji in icon roles.
4. **Pods, not Workspace** — concept rename. Tab label, route, and SwiftUI feature names use "Pods" (was "Workspace"). The 5 tabs are Pods / Channels / Tickets / Blocks / More.
5. **Pods list = browser-tab metaphor** — `ios-pods-grid` borrows Chrome iOS Tab Switcher (2-column card grid; each card = pod with terminal preview thumbnail + close button).

## Render commands

Output goes to `design/out/mobile/` (kept separate from `design/out/desktop/`).

```bash
# Single file (live preview)
pastel serve design/mobile/pages/ios-pods-grid.pastel

# Batch (all mobile)
for f in design/mobile/{components,pages,ia}/*.pastel; do
  pastel build "$f" -o "design/out/mobile/$(basename ${f%.pastel}).png"
done
```

## Icons (PNG asset pipeline)

`shape { type = path }` is unreliable when nested in layout frames — pastel's
layout system gives the shape a `0×0` rect and the path collapses to invisible.
The fix: render lucide SVG paths to PNG with `rsvg-convert` and load via `asset
image(...)` + `image asset_name { width, height }`.

Source SVG paths live in `scripts/gen-icons.sh` (copied verbatim from
[lucide.dev](https://lucide.dev)). Re-run the script to regenerate
`assets/lucide-png/<name>-<colorHex>.png` after path edits.

```bash
brew install librsvg          # one-time; provides rsvg-convert
bash design/mobile/scripts/gen-icons.sh
```

In a `.pastel` file:

```pastel
asset terminal_blue = image("../assets/lucide-png/terminal-0969DA.png")

frame swatch {
    width = 44, height = 44, layout = horizontal, justify = center, align = center
    image terminal_blue { width = 24, height = 24 }
}
```

Naming convention: `<icon>-<6char hex color>.png`. For `_filled` variants
(active tab state), name as `<icon>-filled-<color>.png`.

## Token reference quick links

- Color: `design/tokens/colors.pastel` (shared across desktop+mobile)
- Type: `tokens/typography.pastel` — iOS HIG ramp
- Radius: `tokens/radius.pastel` — concentric rule (child = parent − inset)
- Material: `tokens/material.pastel` — glass alpha + elevation shadows
- Layout: `tokens/layout.pastel` — chrome heights, list metrics, touch targets

## Animation (note for SwiftUI implementation)

Not drawn in pastel. Defaults:
- Drawer slide: `spring(response: 0.35, damping: 0.8)`
- Sheet present: `interactiveSpring(response: 0.4, damping: 0.85)`
- Tab switch: `easeOut 0.2`
- Pod card open (terminal push): `spring(response: 0.45, damping: 0.75)`
