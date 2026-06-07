#!/bin/bash

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"

if ! git -C "$REPO_ROOT" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo "Not inside a git repository: $REPO_ROOT" >&2
  exit 1
fi

git -C "$REPO_ROOT" config core.hooksPath .githooks

echo "Git hooks configured to use .githooks"
echo "pre-commit now runs cargo fmt --all for staged Rust files"
