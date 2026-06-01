# Claude Code Skills for Litho/DeepWiki-RS

This directory contains reusable Claude Code skills for documentation generation and codebase analysis.

## What are Claude Code Skills?

Skills are instructions that extend Claude Code's capabilities. They act as specialized agents that can be invoked by name or automatically triggered based on user requests.

## Available Skills

### 1. Smart Docs (`smart-docs/`)

**Purpose**: Generate comprehensive technical documentation for any codebase

**Features**:
- 📋 Project overview & getting started guides
- 🏗️ C4 architecture diagrams (Context, Container, Component)
- 🔄 Workflow sequence diagrams
- 📊 Mermaid diagrams (flowcharts, state diagrams, ERDs)
- 🔍 Deep dive module documentation

**Installation**:
```bash
./skills/smart-docs/install.sh
```

**Usage**:
```
Generate comprehensive documentation for this codebase
```

**Output**: `./docs/` directory with 1,500-3,000 lines of markdown + 10-20 diagrams

**Cost**: $0 (uses Claude Code subscription)

---

## Installation Guide

### Quick Install (All Skills)

Install all skills at once:

```bash
# From deepwiki-rs root
for skill in skills/*/; do
    if [ -f "$skill/install.sh" ]; then
        echo "Installing $(basename $skill)..."
        bash "$skill/install.sh"
    fi
done
```

### Individual Install

Install specific skill:

```bash
# Example: Install smart-docs
cd deepwiki-rs
./skills/smart-docs/install.sh
```

### Manual Install

```bash
# Copy skill directory to Claude config
cp -r skills/smart-docs ~/.claude/skills/
```

---

## Deployment to New Machine

When setting up on a new development machine:

```bash
# 1. Clone repo
git clone https://github.com/sopaco/deepwiki-rs.git
cd deepwiki-rs

# 2. Install skills
./skills/smart-docs/install.sh

# 3. Verify installation
ls -la ~/.claude/skills/
```

---

## Creating New Skills

Want to create your own skill?

### Structure

```
skills/
└── your-skill-name/
    ├── SKILL.md           # Required: Skill definition
    ├── README.md          # Recommended: Documentation
    ├── install.sh         # Recommended: Install script
    └── examples.md        # Optional: Usage examples
```

### SKILL.md Format

```yaml
---
name: your-skill-name
description: "What your skill does"
allowed-tools:
  - "Read"
  - "Write"
  - "Glob"
  - "Bash(tree:*)"
---

# Your Skill Instructions

[Detailed instructions for Claude on how to execute this skill]
```

### Install Script Template

```bash
#!/bin/bash
SKILL_NAME="your-skill-name"
SKILL_DIR="$HOME/.claude/skills/$SKILL_NAME"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

mkdir -p "$SKILL_DIR"
cp "$SCRIPT_DIR/SKILL.md" "$SKILL_DIR/"
echo "✅ $SKILL_NAME installed!"
```

---

## Skill Development Workflow

1. **Create**: Add new skill in `skills/your-skill/`
2. **Test**: Install locally and test with Claude Code
3. **Iterate**: Refine skill instructions based on output
4. **Document**: Write README and examples
5. **Share**: Commit to repo, others can install

---

## Best Practices

### 1. Version Control Skills

Store skills in repo for:
- ✅ Portability across machines
- ✅ Team collaboration
- ✅ Version history
- ✅ Easy updates

### 2. Use Install Scripts

Benefits:
- ✅ Automated deployment
- ✅ Consistent setup
- ✅ Error handling
- ✅ User-friendly

### 3. Document Thoroughly

Include:
- ✅ Purpose and features
- ✅ Installation steps
- ✅ Usage examples
- ✅ Expected output
- ✅ Troubleshooting

### 4. Test on Multiple Projects

Validate skill works on:
- Different languages
- Different architectures
- Different project sizes

---

## Skill Management Commands

### List Installed Skills

```bash
ls -la ~/.claude/skills/
```

### Remove Skill

```bash
rm -rf ~/.claude/skills/smart-docs
```

### Update Skill

```bash
cd deepwiki-rs
git pull
./skills/smart-docs/install.sh  # Overwrite existing
```

### Backup Skills

```bash
tar -czf claude-skills-backup.tar.gz ~/.claude/skills/
```

---

## Comparison: Skills vs Litho Binary

| Aspect | Skills | Litho Binary |
|--------|--------|--------------|
| **Purpose** | General documentation via Claude | Specialized C4 docs with algorithms |
| **Cost** | $0 (subscription) | $2-5 per run (API costs) |
| **Setup** | Copy 1 directory | Build Rust binary |
| **Dependencies** | None | Rust, API keys, config |
| **Portability** | Instant (copy files) | Per-machine compilation |
| **Quality** | ~85-90% | 100% (reference) |
| **Customization** | Edit text (easy) | Edit Rust code (complex) |
| **Speed** | 10-30 min | 5-15 min |
| **Use Case** | General projects | Standardized docs |

**Recommendation**: Start with skills for most projects. Use Litho binary when exact format or specialized algorithms are required.

---

## Future Skills (Ideas)

Potential skills to add:

- **api-docs**: Generate OpenAPI/Swagger specs from code
- **test-generator**: Create unit tests for untested code
- **refactor-advisor**: Suggest refactoring opportunities
- **security-audit**: Identify common vulnerabilities
- **performance-analyzer**: Find performance bottlenecks
- **migration-guide**: Generate migration guides for upgrades
- **onboarding-docs**: Create developer onboarding guides

Want to contribute? Submit a PR!

---

## Support

- **Documentation**: See individual skill READMEs
- **Issues**: Open issue in deepwiki-rs repo
- **Questions**: Ask in team chat or documentation channel

---

## Credits

**Maintainer**: vovanduc
**Project**: Litho (deepwiki-rs)
**License**: Same as parent project

---

**Last Updated**: 2025-11-11
**Skills Version**: 1.0
