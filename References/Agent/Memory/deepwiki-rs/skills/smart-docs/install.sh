#!/bin/bash

# Smart Docs Skill Installer
# Automatically installs the smart-docs skill to Claude Code

set -e  # Exit on error

SKILL_NAME="smart-docs"
SKILL_DIR="$HOME/.claude/skills/$SKILL_NAME"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "🚀 Installing $SKILL_NAME skill for Claude Code..."

# Check if Claude skills directory exists
if [ ! -d "$HOME/.claude" ]; then
    echo "⚠️  Claude Code config directory not found at ~/.claude"
    echo "   Creating directory..."
    mkdir -p "$HOME/.claude/skills"
fi

# Check if skill already exists
if [ -d "$SKILL_DIR" ]; then
    echo "⚠️  Skill already exists at $SKILL_DIR"
    read -p "   Overwrite? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "❌ Installation cancelled"
        exit 1
    fi
    rm -rf "$SKILL_DIR"
fi

# Create skill directory
mkdir -p "$SKILL_DIR"

# Copy skill files
echo "📦 Copying skill files..."
if [ ! -f "$SCRIPT_DIR/SKILL.md" ] || [ ! -f "$SCRIPT_DIR/QUICKSTART.md" ]; then
    echo "❌ Required skill files not found in $SCRIPT_DIR"
    exit 1
fi
cp "$SCRIPT_DIR/SKILL.md" "$SKILL_DIR/"
cp "$SCRIPT_DIR/QUICKSTART.md" "$SKILL_DIR/"

# Verify installation
if [ -f "$SKILL_DIR/SKILL.md" ]; then
    echo "✅ Smart Docs skill installed successfully!"
    echo ""
    echo "📍 Location: $SKILL_DIR"
    echo ""
    echo "🎯 Usage:"
    echo "   Open Claude Code and say:"
    echo "   'Generate comprehensive documentation for this codebase'"
    echo ""
    echo "📖 Quick Start Guide:"
    echo "   cat ~/.claude/skills/smart-docs/QUICKSTART.md"
    echo ""
    echo "🔥 Happy documenting!"
else
    echo "❌ Installation failed"
    exit 1
fi
