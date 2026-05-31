#!/bin/bash
# Install + launch the AgentsMesh .app on a booted iOS Simulator.
#
# Bazel passes the .ipa or .app path as an env var (via the macro).
# We pick the first booted simulator; if none, boot iPhone 17 Pro.
set -euo pipefail

ARTIFACT="${APP_BUNDLE_PATH:-}"
BUNDLE_ID="${APP_BUNDLE_ID:-ai.agentsmesh.ios}"

if [[ -z "$ARTIFACT" ]]; then
    echo "ERROR: APP_BUNDLE_PATH not set" >&2
    exit 1
fi

# Resolve to absolute path — Bazel runfiles paths are relative to CWD.
ARTIFACT="$(cd "$(dirname "$ARTIFACT")" && pwd)/$(basename "$ARTIFACT")"

# Bazel's `ios_application` default output is `.ipa`. Unzip into a temp
# dir to extract the `.app` bundle simctl wants.
APP_PATH="$ARTIFACT"
if [[ "$ARTIFACT" == *.ipa ]]; then
    TMP=$(mktemp -d)
    trap 'rm -rf "$TMP"' EXIT
    unzip -q "$ARTIFACT" -d "$TMP"
    APP_PATH=$(find "$TMP/Payload" -maxdepth 1 -name "*.app" -type d | head -1)
    if [[ -z "$APP_PATH" ]]; then
        echo "ERROR: no .app inside $ARTIFACT" >&2
        exit 1
    fi
fi

if [[ ! -d "$APP_PATH" ]]; then
    echo "ERROR: $APP_PATH is not a directory" >&2
    exit 1
fi

# Pick a booted simulator, or boot iPhone 17 Pro if none.
DEVICE_ID=$(xcrun simctl list devices booted -j | python3 -c "
import json, sys
data = json.load(sys.stdin)
for runtime, devices in data['devices'].items():
    for d in devices:
        if d.get('state') == 'Booted':
            print(d['udid'])
            sys.exit(0)
")

if [[ -z "$DEVICE_ID" ]]; then
    echo "→ No booted simulator. Booting iPhone 17 Pro..." >&2
    xcrun simctl boot "iPhone 17 Pro" 2>&1 || true
    DEVICE_ID=$(xcrun simctl list devices "iPhone 17 Pro" -j | python3 -c "
import json, sys
data = json.load(sys.stdin)
for runtime, devices in data['devices'].items():
    for d in devices:
        if d.get('name') == 'iPhone 17 Pro':
            print(d['udid'])
            sys.exit(0)
")
fi

if [[ -z "$DEVICE_ID" ]]; then
    echo "ERROR: could not find or boot a simulator" >&2
    exit 1
fi

echo "→ Installing $APP_PATH on $DEVICE_ID"
xcrun simctl install "$DEVICE_ID" "$APP_PATH"

echo "→ Launching $BUNDLE_ID"
xcrun simctl launch --console "$DEVICE_ID" "$BUNDLE_ID" || true

# Bring Simulator.app to front so the user sees it.
open -a Simulator
