# Decision 005: Plan 025 Breaking Changes - Complete Analysis

**Date**: 2025-12-11
**Status**: Documented
**Context**: Plan 025 (Lazy Tool Activation Architecture) breaking changes for SwarmSDK 2.7 / SwarmMemory 2.3

## Executive Summary

Plan 025 introduces **2 user-facing breaking changes** for SwarmSDK 2.7 / SwarmMemory 2.3. This document catalogs ALL interface changes, their impact on users, plugins, and migration paths.

**Test Results**: All changes validated with 100% test pass rate (4240/4240 tests passing).

**Version Bumps**: SwarmSDK 2.6 → 2.7, SwarmMemory 2.2 → 2.3 (minor bumps with breaking changes documented)

## Breaking Changes by Category

### 1. Chat API Changes (Internal - Low Impact)

#### REMOVED: `chat.mark_tools_immutable(*tool_names)`
**Before**:
```ruby
chat.mark_tools_immutable("Think", "Clock", "MemoryRead")
```

**After**: Tools declare removability themselves
```ruby
class Think < SwarmSDK::Tools::Base
  removable false  # Declared in tool class
end
```

**Impact**:
- ✅ Plugins: Must update if they call `mark_tools_immutable`
- ✅ Users: No impact (internal API)
- ✅ Migration: Remove calls, update tool classes to inherit from Base

**Affected Code**:
- SwarmMemory plugin (already updated)
- Any custom plugins calling this method

---

#### REMOVED: `chat.remove_mutable_tools()`
**Before**:
```ruby
chat.remove_mutable_tools  # Removes all tools except immutable ones
```

**After**: Use skill system or clear_skill
```ruby
chat.clear_skill()  # Returns to all tools
# Or load skill with tools: []
skill_state = SkillState.new(file_path: "skill/test.md", tools: [])
chat.load_skill_state(skill_state)
```

**Impact**:
- ✅ Plugins: Must update if they call `remove_mutable_tools`
- ✅ Users: No impact (internal API)
- ✅ Migration: Use skill system instead

**Affected Code**:
- LoadSkill tool (already updated to use skill_state)

---

#### CHANGED: `chat.active_skill_path` (getter only, no setter)
**Before**:
```ruby
chat.active_skill_path = "skill/test.md"  # Direct setter
path = chat.active_skill_path  # Getter
```

**After**: Set via load_skill_state, getter remains
```ruby
skill_state = SkillState.new(file_path: "skill/test.md", ...)
chat.load_skill_state(skill_state)
path = chat.active_skill_path  # Getter still works (delegates to skill_state)
```

**Impact**:
- ✅ Plugins: No impact if only reading active_skill_path
- ⚠️  Snapshot/Restore: attr_writer added back for compatibility
- ✅ Migration: Use load_skill_state instead of direct assignment

**Compatibility**: `attr_writer :active_skill_path` preserved for snapshot restoration.

---

#### NEW: `chat.tool_registry` (public accessor)
```ruby
registry = chat.tool_registry
registry.has_tool?("Read")  # => true
registry.tool_names  # => ["Read", "Write", ...]
```

**Impact**: ✅ New capability, no breaking changes

---

#### NEW: `chat.skill_state` (public accessor)
```ruby
state = chat.skill_state
state.file_path if state  # => "skill/test.md"
state.restricts_tools?  # => true/false
```

**Impact**: ✅ New capability, no breaking changes

---

#### NEW: `chat.activate_tools_for_prompt()` (public method)
```ruby
chat.activate_tools_for_prompt  # Activates tools from registry based on skill state
```

**Impact**: ✅ New capability, called automatically

---

#### NEW: `chat.load_skill_state(skill_state)` (public method)
```ruby
skill_state = SwarmSDK::Agent::SkillState.new(...)
chat.load_skill_state(skill_state)
```

**Impact**: ✅ New capability, replaces mark_skill_loaded

---

#### CHANGED: `chat.tools` return type
**Before**: Returns `@llm_chat.tools` (Hash with string keys)
```ruby
chat.tools["Read"]   # Works
chat.tools[:Read]    # Doesn't work
```

**After**: Returns SymbolKeyHash wrapper (supports both)
```ruby
chat.tools["Read"]   # Works
chat.tools[:Read]    # Works!
```

**Impact**: ✅ Enhancement, no breaking changes (adds symbol key support)

---

### 2. Memory Configuration Changes (User-Facing - Medium Impact)

#### REMOVED: `memory { loadskill_preserve_delegation }`
**Before**:
```yaml
# YAML
memory:
  directory: .swarm/memory
  loadskill_preserve_delegation: true
```

```ruby
# DSL
memory do
  directory ".swarm/memory"
  loadskill_preserve_delegation true
end
```

**After**: Delegation tools must be listed explicitly in skills
```yaml
# Skill frontmatter
---
type: skill
tools: [Read, Edit, WorkWithBackend]  # List delegation explicitly
---
```

**Impact**:
- ⚠️  Users: Must update YAML configs (remove this key)
- ⚠️  Skills: Must explicitly list delegation tools
- ✅ Migration: Remove `loadskill_preserve_delegation` from configs

**Migration Path**:
1. Remove `loadskill_preserve_delegation` from all YAML configs
2. Update skills to explicitly list delegation tools in `tools:` array

---

### 3. Skill Behavior Changes (User-Facing - High Impact)

#### NO CHANGE: `tools: []` meaning (Backward Compatible)
**Before**: Empty array means "keep all current tools"
**After**: Empty array means "keep all current tools" (**SAME**)

```yaml
---
type: skill
tools: []  # Keeps all tools unchanged
---
```

**Impact**: ✅ **NO BREAKING CHANGE** - Behavior unchanged

**Comparison**:
| Skill Config | Behavior |
|--------------|----------|
| `tools: nil` or missing | Keep all tools (no swap) |
| `tools: []` | Keep all tools (no swap) |
| `tools: [Read]` | Swap to Read + non-removable |

**Note**: This was originally planned as a breaking change but changed to preserve backward compatibility.

---

#### NEW: Skills can list delegation tools
**New Capability**:
```yaml
---
type: skill
tools: [Read, Edit, WorkWithBackend, WorkWithDatabase]
---
```

**Impact**: ✅ New feature, no breaking changes

---

#### NEW: Skills can list MCP tools
**New Capability**:
```yaml
---
type: skill
tools: [Read, SearchCode, GetIssue]  # MCP tools work!
---
```

**Impact**: ✅ New feature, no breaking changes

---

### 4. Tool Class Changes (Plugin Authors - Medium Impact)

#### CHANGED: All tools must inherit from `SwarmSDK::Tools::Base`
**Before**:
```ruby
class MyTool < RubyLLM::Tool
  # ...
end
```

**After**:
```ruby
class MyTool < SwarmSDK::Tools::Base
  # Optional: declare removability
  removable false  # Or true (default)

  # ...
end
```

**Impact**:
- ⚠️  Plugin authors: Must update custom tools to inherit from Base
- ✅ Built-in tools: Already updated
- ✅ Memory tools: Already updated
- ✅ Migration: Change parent class to `SwarmSDK::Tools::Base`

**Benefits**:
- Tools can declare `removable false` to be always available
- Consistent base class for all SwarmSDK tools
- Future: Additional tool capabilities can be added to Base

---

### 5. MCP Configuration Changes (User-Facing - Low Impact)

#### NEW: `mcp_server` DSL supports `tools:` parameter
**Before**:
```ruby
mcp_server :codebase, type: :stdio, command: "mcp-server"
# Always calls tools/list (300-500ms)
```

**After** (optional optimization):
```ruby
mcp_server :codebase, type: :stdio, command: "mcp-server", tools: [:search_code, :list_files]
# Skips tools/list (instant boot, lazy schema)
```

**Impact**:
- ✅ Users: Optional enhancement (backward compatible)
- ✅ Migration: Not required (add tools: for faster boot)

**Performance**:
- With `tools:` specified: Boot instant, schema loads on first use (~100ms one-time)
- Without `tools:`: Calls tools/list at boot (~300-500ms per server)

---

### 6. Plugin Interface Changes (Plugin Authors - Medium Impact)

#### NEW: `on_agent_initialized` receives tool_registry
**Before**: Plugins called `agent.add_tool(tool)` and `agent.mark_tools_immutable(...)`

**After**: Plugins register in registry and tools declare removability
```ruby
def on_agent_initialized(agent_name:, agent:, context:)
  tool = create_my_tool(...)

  # Register in registry instead of add_tool
  agent.tool_registry.register(
    tool,
    source: :plugin,
    metadata: { plugin_name: :my_plugin }
  )

  # No need to mark immutable - tool declares it
end
```

**Impact**:
- ⚠️  Plugin authors: Must update to use tool_registry.register
- ✅ Built-in plugins: Already updated (SwarmMemory)
- ✅ Migration: Replace `add_tool` with `tool_registry.register`

**Example Migration**:
```ruby
# OLD
def on_agent_initialized(agent_name:, agent:, context:)
  my_tool = MyTool.new(...)
  agent.add_tool(my_tool)
  agent.mark_tools_immutable("MyTool")
end

# NEW
def on_agent_initialized(agent_name:, agent:, context:)
  my_tool = MyTool.new(...)  # Must inherit from SwarmSDK::Tools::Base
  agent.tool_registry.register(
    my_tool,
    source: :plugin,
    metadata: { plugin_name: :my_plugin }
  )
  # No mark_tools_immutable - tool declares removable false itself
end
```

---

### 7. Internal Architecture Changes (Low User Impact)

#### NEW: 6-Pass Agent Initialization
**Before**: 5-pass initialization
**After**: 6-pass initialization (added Pass 6: activate_tools)

**Impact**: ✅ Internal change, no user impact

---

#### CHANGED: Tools stored with symbol keys in @llm_chat.tools
**Before**: String keys
**After**: Symbol keys (RubyLLM requirement)

**Impact**: ✅ Internal change, no user impact (SymbolKeyHash wrapper supports both)

---

### 8. Delegation Tool Naming (User-Facing - Enhancement)

#### IMPROVED: PascalCase for multi-word agent names
**Before**:
```ruby
slack_agent → WorkWithSlack_agent  # Inconsistent
```

**After**:
```ruby
slack_agent → WorkWithSlackAgent  # Proper PascalCase
web_scraper → WorkWithWebScraper
memory_agent → WorkWithMemoryAgent
```

**Impact**:
- ⚠️  Users: Tool names changed for underscore-containing agent names
- ⚠️  Skills: Must update tool names in frontmatter
- ✅ Migration: Update skill tool lists with new names

**Migration**:
```yaml
# OLD skill
tools: [Read, WorkWithSlack_agent]

# NEW skill
tools: [Read, WorkWithSlackAgent]
```

---

## Complete Breaking Changes Summary

### USER-FACING BREAKING CHANGES (2 total)
1. ⚠️  **`loadskill_preserve_delegation` removed** - Must list delegation tools explicitly
2. ⚠️  **Delegation tool names changed** - PascalCase for underscored names

### MEDIUM IMPACT (Plugin Authors)
4. ⚠️  **Tools must inherit from `SwarmSDK::Tools::Base`** - Not `RubyLLM::Tool`
5. ⚠️  **`mark_tools_immutable()` removed** - Use `removable false` in tool class
6. ⚠️  **`agent.add_tool()` replaced** - Use `agent.tool_registry.register()` in plugins

### LOW IMPACT (Internal/Advanced)
7. ✅ **`remove_mutable_tools()` removed** - Use `clear_skill()` instead
8. ✅ **`active_skill_path=` removed** - Use `load_skill_state()` (setter preserved for compatibility)
9. ✅ **6-pass initialization** - Internal change

### ENHANCEMENTS (Non-Breaking)
10. ✅ **`mcp_server tools:` parameter** - Optional optimization
11. ✅ **Symbol/string key support** - chat.tools supports both
12. ✅ **New public APIs** - tool_registry, skill_state, activate_tools_for_prompt

---

## Plugin Migration Guide

### For Plugin Authors

#### Step 1: Update Tool Classes
```ruby
# OLD
class MyTool < RubyLLM::Tool
  # ...
end

# NEW
class MyTool < SwarmSDK::Tools::Base
  removable false  # If tool should always be available
  # ...
end
```

#### Step 2: Update on_agent_initialized
```ruby
# OLD
def on_agent_initialized(agent_name:, agent:, context:)
  my_tool = MyTool.new(...)
  agent.add_tool(my_tool)
  agent.mark_tools_immutable("MyTool")
end

# NEW
def on_agent_initialized(agent_name:, agent:, context:)
  my_tool = MyTool.new(...)
  agent.tool_registry.register(
    my_tool,
    source: :plugin,
    metadata: { plugin_name: :my_plugin }
  )
  # No mark_tools_immutable - tool declares removable false
end
```

#### Step 3: Test Your Plugin
```ruby
# Verify tool is in registry
agent.tool_registry.has_tool?("MyTool")

# Verify tool is non-removable
entry = agent.tool_registry.get("MyTool")
refute entry.removable

# Verify tool is activated
assert agent.tools["MyTool"]
```

---

## User Migration Guide

### For SwarmSDK Users

#### Migration Checklist

- [ ] Remove `loadskill_preserve_delegation` from all YAML configs
- [ ] Update skills with `tools: []` to remove the `tools:` key
- [ ] Update skills that use delegation tools to list them explicitly
- [ ] Update skill tool names for underscored agent names (snake_case → PascalCase)
- [ ] Test all skills to ensure they load correctly

#### Example: YAML Config Migration
```yaml
# BEFORE (SwarmSDK 2.x)
agents:
  researcher:
    memory:
      directory: .swarm/memory
      loadskill_preserve_delegation: true  # ← REMOVE THIS

# AFTER (SwarmSDK 3.0)
agents:
  researcher:
    memory:
      directory: .swarm/memory
      # loadskill_preserve_delegation removed
```

#### Example: Skill Migration (tools: [])
```yaml
# BEFORE (SwarmSDK 2.x)
---
type: skill
tools: []  # Meant "keep all tools"
---

# AFTER (SwarmSDK 3.0)
---
type: skill
# tools: []  ← REMOVE THIS LINE (or omit tools: key entirely)
---
# Result: All tools available (same as old behavior)
```

#### Example: Skill Migration (delegation tools)
```yaml
# BEFORE (SwarmSDK 2.x)
---
type: skill
tools: [Read, Edit]  # Delegation auto-preserved
---

# AFTER (SwarmSDK 3.0)
---
type: skill
tools: [Read, Edit, WorkWithBackend]  # ← List delegation explicitly
---
```

#### Example: Delegation Tool Name Migration
```yaml
# BEFORE
agents:
  lead:
    delegates_to: [slack_agent]
# Skill would use: WorkWithSlack_agent

# AFTER (same config, but tool name changed)
# Skill must use: WorkWithSlackAgent

# Skill migration:
# OLD
tools: [Read, WorkWithSlack_agent]

# NEW
tools: [Read, WorkWithSlackAgent]
```

---

## Backward Compatibility

### What Still Works (No Changes Needed)

✅ **Basic agent configuration** - No changes
✅ **Tool permissions** - Still works the same way
✅ **Delegation configuration** - `delegates_to:` unchanged
✅ **MCP servers without tools:** parameter - Still works (discovery mode)
✅ **Skills without tools:** key - Still works (all tools available)
✅ **Memory tools** - All work identically
✅ **Custom tools** - Just need to inherit from Base

### What Breaks

❌ **Configs with `loadskill_preserve_delegation`** - Key removed
❌ **Delegation tool names with underscores** - Now PascalCase
❌ **Plugins calling `mark_tools_immutable()`** - Method removed (internal API)
❌ **Direct `active_skill_path =` assignment** - Use load_skill_state (internal API)

### What Still Works (Backward Compatible)

✅ **Skills with `tools: []`** - Still means keep all tools (NO CHANGE)
✅ **Skills with `tools: nil`** - Still means keep all tools (NO CHANGE)

---

## Testing Recommendations

### For Plugin Authors
```ruby
# Test tool registration
def test_my_plugin_registers_tools
  # Create swarm with plugin enabled
  swarm = SwarmSDK.build do
    agent :test do
      my_plugin { directory: "." }
    end
  end

  agent = swarm.agent(:test)

  # Verify in registry
  assert agent.tool_registry.has_tool?("MyTool")

  # Verify removability
  entry = agent.tool_registry.get("MyTool")
  refute entry.removable  # If tool is non-removable

  # Verify activation
  assert agent.tools["MyTool"]
end
```

### For Users
1. Load each skill and verify tools are correct
2. Test delegation tool usage
3. Test MCP tool usage in skills
4. Verify `tools: []` gives minimal toolset

---

## Rollback Plan

If issues arise, rollback is possible but lossy:

**Option A**: Revert to SwarmSDK 2.x
- Lose: Delegation/MCP tools in skills, lazy activation benefits
- Keep: All existing configs and skills work

**Option B**: Partial revert (not recommended)
- Complex, not feasible given architectural changes

**Recommendation**: Forward migration only. Plan 025 is too fundamental to partially revert.

---

## Version Bumping

**SwarmSDK**: 2.x → 3.0 (major version bump required)
**SwarmMemory**: 2.x → 3.0 (follows SDK version)
**SwarmCLI**: 2.x → 3.0 (follows SDK version)

All three gems must be updated together due to interface dependencies.

---

## Documentation Updates Needed

1. **README.md** - Update examples for SwarmSDK 3.0
2. **Skill authoring guide** - Document new `tools:` behavior and delegation/MCP support
3. **MCP configuration guide** - Document `tools:` parameter optimization
4. **Migration guide** - Create MIGRATION_2x_to_3x.md
5. **CHANGELOG.md** - Document all breaking changes
6. **Plugin development guide** - Update for new tool registration pattern

---

## Known Compatible Plugins

### SwarmMemory ✅
- **Status**: Fully updated and tested
- **Changes**: Tool classes inherit from Base, use registry.register
- **Tests**: 254/254 passing

### Future Custom Plugins
- **Required**: Inherit from SwarmSDK::Tools::Base
- **Required**: Use tool_registry.register in on_agent_initialized
- **Optional**: Declare removable false for essential tools

---

## Conclusion

Plan 025 introduces **significant breaking changes** that require:
1. YAML config updates (remove loadskill_preserve_delegation)
2. Skill updates (tools: [] meaning, delegation tool names)
3. Plugin updates (inherit from Base, use registry.register)

All changes are **well-tested** (100% pass rate) and provide **substantial benefits**:
- Skills can control delegation/MCP tools
- Faster MCP boot times
- Cleaner architecture
- Better safety (declarative, immutable)

**Recommendation**: Proceed with SwarmSDK 3.0 release with comprehensive migration guide.
