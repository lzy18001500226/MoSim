# UFO³ Configuration Tools

Professional configuration management tools for UFO³ with backward compatibility.

## 🎯 Quick Reference

### Validate Configuration
```bash
# Check UFO configuration
python -m ufo.tools.validate_config ufo

# Check Galaxy configuration
python -m ufo.tools.validate_config galaxy

# Check both + show details
python -m ufo.tools.validate_config all --show-config
```

### Migrate Configuration
```bash
# Preview migration (safe)
python -m ufo.tools.migrate_config --dry-run

# Perform migration (with backup)
python -m ufo.tools.migrate_config

# Force migration (skip confirmation)
python -m ufo.tools.migrate_config --force
```

---

## 📁 Configuration Structure

### Modern (Recommended)
```
config/
├── ufo/          # UFO² configurations
│   ├── agents.yaml
│   ├── system.yaml
│   ├── rag.yaml
│   └── ...
└── galaxy/       # Galaxy configurations
    ├── agent.yaml
    ├── devices.yaml
    └── ...
```

### Legacy (Still Supported)
```
ufo/config/       # Old monolithic config
├── config.yaml
└── config_dev.yaml
```

---

## 🔄 Migration

The system automatically detects and uses legacy configurations with helpful warnings.

### When to Migrate?
- ✅ **Recommended:** When starting new projects
- ✅ **Optional:** For existing projects (backward compatible)
- ✅ **Required:** Before v4.0 (future release)

### Migration Benefits
- ✨ Cleaner separation of concerns
- ✨ Easier to manage and version control
- ✨ Better team collaboration
- ✨ Environment-specific overrides

---

## 📖 Documentation

**Full Guide:** [docs/configuration_guide.md](../docs/configuration_guide.md)

Key Topics:
- Configuration structure and best practices
- Priority chain (new → legacy → env)
- Troubleshooting common issues
- Advanced configuration patterns

---

## 🛠️ Tool Details

### `validate_config` - Configuration Validator

**Purpose:** Validate configuration files and detect issues

**Usage:**
```bash
python -m ufo.tools.validate_config {ufo|galaxy|all} [--show-config]
```

**Features:**
- ✅ Validates required fields
- ✅ Detects placeholder values
- ✅ Checks API configurations
- ✅ Shows configuration hierarchy
- ✅ Provides actionable feedback

**Example Output:**
```
🔍 Validation
======================================================================
Configuration Paths:
  ✓ config/ufo/ (active)
    ├── agents.yaml
    ├── system.yaml
    └── rag.yaml

Warnings (1):
  ⚠ Placeholder value detected: HOST_AGENT.API_KEY = 'YOUR_KEY'
     Please update with actual value

✓ Configuration is valid!
Consider addressing warnings for best practices.
```

---

### `migrate_config` - Configuration Migration Tool

**Purpose:** Migrate legacy config to modern structure

**Usage:**
```bash
python -m ufo.tools.migrate_config [options]
```

**Options:**
- `--dry-run` - Preview changes without modifying files
- `--no-backup` - Skip backup creation (not recommended)
- `--force` - Skip confirmation prompts
- `--legacy-path PATH` - Custom legacy path
- `--new-path PATH` - Custom destination path

**Features:**
- ✅ Automatic backup creation
- ✅ Dry run mode (safe preview)
- ✅ Safety confirmations
- ✅ Detailed migration report
- ✅ Rollback support

**Example Output:**
```
🔧 Config Migration
======================================================================
Legacy: ufo/config/
New:    config/ufo/

Found 5 configuration file(s):
  • config.yaml
  • config_dev.yaml
  • config_prices.yaml
  • agent_mcp.yaml
  • __init__.py

Creating backup: ufo/config.backup_20250103_143022
✓ Backup created successfully

Migrating files...
✓ Copied: config.yaml → config/ufo/config.yaml
✓ Copied: config_dev.yaml → config/ufo/config_dev.yaml
✓ Copied: config_prices.yaml → config/ufo/config_prices.yaml

✨ Success
======================================================================
Migration Complete!

Next Steps:
1. Verify the new configuration files work correctly:
   python -m ufo --task test

2. Once verified, you can remove the legacy config:
   rm -rf ufo/config/*.yaml

3. If needed, rollback using backup:
   cp -r ufo/config.backup_20250103_143022/* ufo/config/

Your UFO³ configuration is now using the modern structure!
```

---

## 🎓 Common Workflows

### New User Setup
```bash
# 1. Copy templates
cp config/ufo/agents.yaml.template config/ufo/agents.yaml

# 2. Edit configuration
notepad config/ufo/agents.yaml

# 3. Validate
python -m ufo.tools.validate_config ufo

# 4. Test
python -m ufo --task test
```

### Existing User Migration
```bash
# 1. Preview migration
python -m ufo.tools.migrate_config --dry-run

# 2. Perform migration (with backup)
python -m ufo.tools.migrate_config

# 3. Validate new config
python -m ufo.tools.validate_config ufo

# 4. Test functionality
python -m ufo --task test

# 5. Remove old config (after verification)
rm -rf ufo/config/*.yaml
```

### Configuration Troubleshooting
```bash
# 1. Validate configuration
python -m ufo.tools.validate_config ufo --show-config

# 2. Check for issues
# - Missing required fields
# - Placeholder values
# - Path conflicts

# 3. Fix issues in YAML files

# 4. Re-validate
python -m ufo.tools.validate_config ufo
```

---

## 🔍 Priority Chain

When both new and legacy configurations exist:

```
Priority: config/ufo/ > ufo/config/ > Environment Variables
```

**Example:**
```yaml
# config/ufo/agents.yaml (NEW - highest priority)
MAX_STEP: 50
API_MODEL: "gpt-4o"

# ufo/config/config.yaml (LEGACY - fallback)
MAX_STEP: 30           # ← Overridden by new config
TIMEOUT: 60            # ← Used (not in new config)
```

**Result:** `MAX_STEP=50, API_MODEL="gpt-4o", TIMEOUT=60`

---

## ⚠️ Important Notes

### Backward Compatibility
- ✅ **Legacy paths still work** - No breaking changes
- ✅ **Automatic fallback** - System detects and uses legacy config
- ✅ **Migration is optional** - Choose when to migrate
- ✅ **Warnings are informational** - Can be safely ignored

### Data Safety
- ✅ **Automatic backups** - Migration tool creates timestamped backups
- ✅ **Dry run mode** - Preview changes before applying
- ✅ **Non-destructive** - Original files preserved until manually deleted
- ✅ **Rollback support** - Easy restoration from backups

### Best Practices
- ✅ **Validate before using** - Run validation tool after changes
- ✅ **Use version control** - Git-track configuration templates
- ✅ **Separate secrets** - Use environment variables for API keys
- ✅ **Test after migration** - Verify functionality before removing old config

---

## 📞 Support

- **Full Documentation:** [docs/configuration_guide.md](../docs/configuration_guide.md)
- **GitHub Issues:** https://github.com/microsoft/UFO/issues
- **Email:** ufo-agent@microsoft.com

---

<sub>© Microsoft 2025 | UFO³ Configuration Tools</sub>
