#!/usr/bin/env bash
set -euo pipefail

REPO="DeepExperience/MMSkills"
SKILL_PATH="agent_integrations/mmskills-agent-adapter"
CODEX_HOME="${CODEX_HOME:-$HOME/.codex}"
DEST="$CODEX_HOME/skills/mmskills-agent-adapter"
INSTALLER="$CODEX_HOME/skills/.system/skill-installer/scripts/install-skill-from-github.py"

if [ -e "$DEST" ]; then
  echo "MMSkills Agent Adapter already exists at $DEST"
  echo "Remove it first if you want to reinstall."
  exit 0
fi

if [ -f "$INSTALLER" ]; then
  python3 "$INSTALLER" --repo "$REPO" --path "$SKILL_PATH"
else
  if ! command -v git >/dev/null 2>&1; then
    echo "git is required when the Codex skill installer is not available." >&2
    exit 1
  fi
  TMPDIR="$(mktemp -d)"
  trap 'rm -rf "$TMPDIR"' EXIT
  git clone --depth 1 --filter=blob:none --sparse "https://github.com/$REPO" "$TMPDIR/repo"
  git -C "$TMPDIR/repo" sparse-checkout set "$SKILL_PATH"
  mkdir -p "$CODEX_HOME/skills"
  cp -R "$TMPDIR/repo/$SKILL_PATH" "$DEST"
fi

echo "Installed MMSkills Agent Adapter at $DEST"
echo 'Restart Codex, then invoke $mmskills when a GUI-agent task can use MMSkills.'
