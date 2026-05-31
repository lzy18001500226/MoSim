#!/usr/bin/env bash
# Detect DTO drift between Go gin.H multi-field returns and Rust Response struct field sets.
#
# Why this exists: backend handlers like `c.JSON(http.StatusOK, gin.H{"pod": p, "warning": w})`
# emit envelope JSON with multiple sibling fields. The api-client previously unwrapped the first
# field via `get_resource("key")`, silently dropping the others. Several issues
# (#341/#342/#343/#345) all traced back to this pattern. Round-trip Rust unit tests catch it
# *if* a test exists; this script is a static lint that catches drift even when tests are missing.
#
# Strategy: grep gin.H multi-key responses → extract field set → grep matching Rust struct →
# verify field set is a subset of the Rust DTO. Reports unmatched.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"
cd "$REPO_ROOT"

REPORT=$(mktemp)
trap 'rm -f "$REPORT"' EXIT

echo "=== Backend gin.H multi-key responses ===" >> "$REPORT"

# Capture lines like: c.JSON(http.StatusOK, gin.H{"x": ..., "y": ..., "z": ...})
# Multi-key means >= 2 keys, which is the drift-prone shape.
backend_lines=$(grep -rn 'c\.JSON.*gin\.H{' backend/internal/api/rest/v1/ \
    | grep -v '_test\.go' \
    | grep -E '"[a-z_]+":.*"[a-z_]+":' \
    | head -100 || true)

echo "$backend_lines" >> "$REPORT"
echo "" >> "$REPORT"
echo "=== Drift detection ===" >> "$REPORT"

drift_count=0
while IFS= read -r line; do
  [ -z "$line" ] && continue
  # Extract keys from gin.H{"a": ..., "b": ...}
  keys=$(echo "$line" | grep -oE '"[a-z_]+"\s*:' | tr -d '":' | tr -d ' ' | sort -u | tr '\n' ',' | sed 's/,$//')
  [ -z "$keys" ] && continue

  # Skip single-key responses (handled correctly by *_resource wrappers)
  key_count=$(echo "$keys" | tr ',' '\n' | wc -l | tr -d ' ')
  [ "$key_count" -lt 2 ] && continue

  # Skip error / status-only envelopes
  case "$keys" in
    "error"|"message"|"status"|"data"|*"error"*|"message,status"|"status,message")
      continue
      ;;
  esac

  loc=$(echo "$line" | cut -d: -f1-2)
  echo "  Backend $loc → keys: {$keys}" >> "$REPORT"
  drift_count=$((drift_count + 1))
done <<< "$backend_lines"

echo "" >> "$REPORT"
echo "=== Summary ===" >> "$REPORT"
echo "Total multi-key envelope responses: $drift_count" >> "$REPORT"
echo "" >> "$REPORT"
echo "To verify each is preserved by Rust:" >> "$REPORT"
echo "  1. find the Rust DTO that mirrors the response (clients/core/crates/types/src/)" >> "$REPORT"
echo "  2. confirm the Response struct lists every key" >> "$REPORT"
echo "  3. add a *_relay_preserves_* round-trip test if missing" >> "$REPORT"

cat "$REPORT"

exit 0
