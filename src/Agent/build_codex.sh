#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CODEX_RS_DIR="$SCRIPT_DIR/codex-main/codex-rs"
MANIFEST_PATH="$CODEX_RS_DIR/Cargo.toml"
LOCK_PATH="$CODEX_RS_DIR/Cargo.lock"
CODEX_BIN="$CODEX_RS_DIR/target/release/codex"

if ! command -v cargo >/dev/null 2>&1; then
    echo "Cargo was not found. Install the Rust stable toolchain, reopen the shell, then rerun this script." >&2
    exit 1
fi

if ! command -v rustc >/dev/null 2>&1; then
    echo "rustc was not found. Install the Rust stable toolchain, reopen the shell, then rerun this script." >&2
    exit 1
fi

if [[ ! -f "$MANIFEST_PATH" || ! -f "$LOCK_PATH" ]]; then
    echo "The vendored Codex Cargo workspace or Cargo.lock is missing: $CODEX_RS_DIR" >&2
    exit 1
fi

echo "Building vendored Codex CLI with the locked dependency graph..."
echo "Cargo: $(cargo --version)"
echo "Rustc: $(rustc --version)"

cd "$CODEX_RS_DIR"
cargo build --locked --release --bin codex

if [[ ! -x "$CODEX_BIN" ]]; then
    echo "Cargo completed without producing the expected executable: $CODEX_BIN" >&2
    exit 1
fi

echo "Build complete: $CODEX_BIN"
"$CODEX_BIN" --version
