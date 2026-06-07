#!/bin/bash
# Combines all project documentation into a single file for LLM context.
# Usage: ./scripts/bundle-docs.sh [output_file]

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
OUTPUT="${1:-$REPO_ROOT/CONTEXT.md}"

{
  echo "# Spacebot — Full Documentation Bundle"
  echo ""
  echo "Generated: $(date -u '+%Y-%m-%d %H:%M UTC')"
  echo ""

  # Root docs first
  for file in README.md AGENTS.md RUST_STYLE_GUIDE.md; do
    if [ -f "$REPO_ROOT/$file" ]; then
      echo "---"
      echo ""
      echo "# $file"
      echo ""
      cat "$REPO_ROOT/$file"
      echo ""
    fi
  done

  # All docs/
  for file in "$REPO_ROOT"/docs/*.md; do
    [ -f "$file" ] || continue
    [[ "$file" == *.md ]] || continue
    name="$(basename "$file")"
    echo "---"
    echo ""
    echo "# docs/$name"
    echo ""
    cat "$file"
    echo ""
  done

  # System prompts
  for file in "$REPO_ROOT"/prompts/*.md; do
    [ -f "$file" ] || continue
    [[ "$file" == *.md ]] || continue
    name="$(basename "$file")"
    echo "---"
    echo ""
    echo "# prompts/$name"
    echo ""
    cat "$file"
    echo ""
  done

} > "$OUTPUT"

echo "Bundled to $OUTPUT ($(wc -c < "$OUTPUT" | tr -d ' ') bytes)"
