# Contribution Guidelines

Thank you for contributing to `awesome-opencode`! Add your entries via YAML files—no need to edit README.md directly.

## How to Add an Entry

### Step 1: Fork & Clone

```bash
git clone https://github.com/YOUR-USERNAME/awesome-opencode.git
cd awesome-opencode
```

### Step 2: Create YAML File

Create a YAML file in the appropriate category folder under `data/`:
- `data/plugins/` - OpenCode plugins and extensions
- `data/themes/` - Color schemes and visual themes
- `data/agents/` - AI agents and subagents
- `data/projects/` - Tools, GUIs, integrations, and utilities
- `data/resources/` - Guides, templates, and configurations

**Filename:** kebab-case (e.g., `my-plugin.yaml`)

### Step 3: Add YAML Content

```yaml
name: Your Plugin Name
repo: https://github.com/owner/repo-name
tagline: Short punchy summary (max 120 chars, shown in collapsed view)
description: Longer description explaining what it does and why it's useful.
```

### Step 4: Submit PR

```bash
git checkout -b add-my-plugin
git add data/plugins/my-plugin.yaml
git commit -m "docs: add my-plugin to plugins"
git push origin add-my-plugin
```

Open a Pull Request on GitHub.

## Entry Requirements

- [ ] **Relevant** - Directly related to OpenCode
- [ ] **Public** - Repository is publicly accessible
- [ ] **Maintained** - Active commits within the last 6 months
- [ ] **Unique** - Not a duplicate of existing entry
- [ ] **Complete** - All required fields included

## What Happens After PR?

1. **Validation runs** - Automated checks verify YAML format
2. **Maintainer review** - Content and relevance verified
3. **Merge** - Once approved
4. **README auto-generates** - List updates automatically

No need to edit README.md—it regenerates from YAML files.
