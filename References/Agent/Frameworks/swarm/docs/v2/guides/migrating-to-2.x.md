# Migrating SwarmSDK 2.x

This guide covers all breaking changes and migration steps for upgrading between SwarmSDK 2.x versions.

---

## Migrating to v2.6.0

### Overview

SwarmSDK v2.6.0 introduces execution timeouts with external enforcement via Async, and renames the `timeout` configuration to `request_timeout` for clarity.

### Breaking Changes

#### 1. `timeout` Configuration Renamed to `request_timeout`

**What Changed:**
- Agent-level `timeout` configuration renamed to `request_timeout`
- Clarifies that it controls only the LLM HTTP request timeout (Faraday level), not the entire agent turn
- Two new timeout configurations added: `execution_timeout` (swarm-level) and `turn_timeout` (agent-level)

**Why:** The old `timeout` name was ambiguous - it only controlled HTTP request timeout, not the entire agent execution. The new names make the scope explicit.

**Before (v2.5.x):**
```ruby
# Ruby DSL
agent :backend do
  timeout 300
end

all_agents do
  timeout 180
end
```

```yaml
# YAML
all_agents:
  timeout: 300

agents:
  backend:
    timeout: 600
```

**After (v2.6.0):**
```ruby
# Ruby DSL
agent :backend do
  request_timeout 300   # HTTP request timeout (Faraday level)
  turn_timeout 900      # NEW: Entire agent turn timeout
end

all_agents do
  request_timeout 180
  turn_timeout 900
end

# NEW: Swarm-level execution timeout
execution_timeout 3600  # Max time for entire swarm.execute()
```

```yaml
# YAML
swarm:
  execution_timeout: 3600  # NEW: Swarm-level timeout

  all_agents:
    request_timeout: 300
    turn_timeout: 900      # NEW: Agent turn timeout

  agents:
    backend:
      request_timeout: 600
      turn_timeout: 1200
```

**Migration Steps:**

1. **Search and replace in Ruby DSL:**
   - Replace `timeout(` with `request_timeout(`
   - Replace `timeout ` with `request_timeout `

2. **Search and replace in YAML:**
   - Replace `timeout:` with `request_timeout:`

3. **Add new timeouts (optional):**
   - Add `execution_timeout` at swarm level if you want to cap total execution time
   - Add `turn_timeout` at agent level if you want to cap agent turns separately from HTTP requests

4. **Update tests:**
   - Replace `definition.timeout` with `definition.request_timeout`
   - Replace `timeout_set?` with `request_timeout_set?`

**Note:** The global config `SwarmSDK.config.agent_request_timeout` already used the correct name and does NOT need to be changed.

#### 2. New Timeout Configurations

**Added:**
- `execution_timeout` (swarm-level): Maximum wall-clock time for entire `swarm.execute()` call
- `turn_timeout` (agent-level): Maximum time for single `agent.ask()` call including all tool executions

**Defaults:**
- Both new timeouts default to `1800` seconds (30 minutes)
- Set to `nil` to disable timeout enforcement
- Zero and negative values are validated and rejected

**Global Configuration:**
```ruby
SwarmSDK.configure do |config|
  config.default_execution_timeout = 3600  # 1 hour
  config.default_turn_timeout = 900        # 15 minutes
  # Or set to nil to disable
  config.default_execution_timeout = nil
end
```

**Behavior:**
- **Execution timeout**: Uses Async's `task.with_timeout()` to wrap entire swarm execution
- **Turn timeout**: Wraps each `agent.ask()` call with external timeout enforcement
- **Cleanup guaranteed**: `ensure` blocks always run after timeout
- **New events**: `execution_timeout` and `turn_timeout` events emitted for monitoring

---

## Migrating to v2.4.0

### Overview

SwarmSDK v2.4.0 introduces a centralized configuration system that replaces the previous `SwarmSDK.settings` approach.

### Breaking Changes

#### 1. Configuration API Change

**What Changed:**
- `SwarmSDK.settings` replaced with `SwarmSDK.config` singleton
- New `SwarmSDK.configure` block syntax for setting values
- Lazy ENV loading with thread-safe initialization
- Auto-proxying of API keys to RubyLLM

**Before (v2.3.x):**
```ruby
# Direct property access
SwarmSDK.settings.openai_api_key = "sk-..."
SwarmSDK.settings.default_model = "gpt-5"
SwarmSDK.settings.allow_filesystem_tools = false

# Reading values
model = SwarmSDK.settings.default_model
```

**After (v2.4.0):**
```ruby
# Block-based configuration
SwarmSDK.configure do |config|
  config.openai_api_key = "sk-..."
  config.default_model = "gpt-5"
  config.allow_filesystem_tools = false
end

# Reading values
model = SwarmSDK.config.default_model
```

**Migration Steps:**

1. **Replace all `SwarmSDK.settings` with `SwarmSDK.config`:**
```ruby
# Before
timeout = SwarmSDK.settings.agent_request_timeout

# After
timeout = SwarmSDK.config.agent_request_timeout
```

2. **Use configure block for setting multiple values:**
```ruby
# Before
SwarmSDK.settings.openai_api_key = ENV["OPENAI_API_KEY"]
SwarmSDK.settings.default_model = "claude-sonnet-4"
SwarmSDK.settings.agent_request_timeout = 600

# After
SwarmSDK.configure do |config|
  config.openai_api_key = ENV["OPENAI_API_KEY"]
  config.default_model = "claude-sonnet-4"
  config.agent_request_timeout = 600
end
```

3. **Update test setup/teardown:**
```ruby
# Before
def setup
  @original = SwarmSDK.settings.default_model
  SwarmSDK.settings.default_model = "test-model"
end

def teardown
  SwarmSDK.settings.default_model = @original
end

# After
def setup
  SwarmSDK.reset_config!
  SwarmSDK.configure do |config|
    config.default_model = "test-model"
  end
end

def teardown
  SwarmSDK.reset_config!
end
```

#### 2. API Key Auto-Proxying

**What Changed:**
- API keys set via `SwarmSDK.configure` are automatically proxied to `RubyLLM.config`
- No need to configure both SwarmSDK and RubyLLM separately

**Before (v2.3.x):**
```ruby
# Had to configure both
SwarmSDK.settings.openai_api_key = "sk-..."
RubyLLM.config.openai_api_key = "sk-..."
```

**After (v2.4.0):**
```ruby
# Only configure SwarmSDK - auto-proxied to RubyLLM
SwarmSDK.configure do |config|
  config.openai_api_key = "sk-..."
end
# RubyLLM.config.openai_api_key is now also set
```

#### 3. Configuration Priority

Values are resolved in this order:
1. **Explicit value** (set via `SwarmSDK.configure`)
2. **Environment variable** (e.g., `SWARM_SDK_DEFAULT_MODEL`)
3. **Default value** (from `SwarmSDK::Defaults` module)

```ruby
# ENV has SWARM_SDK_DEFAULT_MODEL=gpt-4o

# Without explicit config - uses ENV
SwarmSDK.config.default_model  # => "gpt-4o"

# With explicit config - overrides ENV
SwarmSDK.configure do |config|
  config.default_model = "claude-sonnet-4"
end
SwarmSDK.config.default_model  # => "claude-sonnet-4"
```

### New Features

#### Configuration Reference

See [Configuration Reference](../reference/configuration_reference.md) for all 45+ configuration options including:
- API keys for all providers
- Timeouts and limits
- WebFetch LLM processing
- Security settings

#### New Helper Methods

```ruby
# Check if WebFetch LLM processing is enabled
SwarmSDK.config.webfetch_llm_enabled?

# Reset config for testing
SwarmSDK.reset_config!
```

### Testing Your Migration

```ruby
describe "v2.4.0 Migration" do
  def setup
    SwarmSDK.reset_config!
  end

  def teardown
    SwarmSDK.reset_config!
  end

  it "uses new config API" do
    SwarmSDK.configure do |config|
      config.default_model = "test-model"
    end

    assert_equal "test-model", SwarmSDK.config.default_model
  end

  it "auto-proxies API keys to RubyLLM" do
    SwarmSDK.configure do |config|
      config.openai_api_key = "test-key"
    end

    assert_equal "test-key", RubyLLM.config.openai_api_key
  end
end
```

---

## Migrating to v2.3.0

### Overview

SwarmSDK v2.3.0 introduces significant architectural improvements:

- **Swarm/Workflow API Separation** - Clear distinction between single-swarm and multi-stage workflows
- **Delegation Tool Rebranding** - `WorkWith*` instead of `DelegateTaskTo*`
- **Agent::Chat Abstraction Layer** - Improved encapsulation of RubyLLM internals
- **Snapshot Version 2.1.0** - Plugin state support and metadata restructuring
- **Observer Module** - Event-driven parallel agent execution (new feature)
- **Context Management DSL** - Custom context warning handlers (new feature)
- **Non-blocking Execution** - Async execution with cancellation support (new feature)

---

## Priority: Critical Breaking Changes

### 1. Delegation Tool Rebranding

**What Changed:**
- Tool names: `DelegateTaskTo*` → `WorkWith*`
- Parameter: `task:` → `message:`
- Description emphasizes collaboration over task delegation

**Before (v2.2.x):**
```ruby
# Tool call
DelegateTaskToBackend(task: "Build the authentication API")

# In agent conversations
"I'll delegate this to Backend using DelegateTaskToBackend"
```

**After (v2.3.0):**
```ruby
# Tool call
WorkWithBackend(message: "Build the authentication API")

# In agent conversations
"I'll work with Backend using WorkWithBackend"
```

**Migration Steps:**

1. **Update tool references in your code:**
```ruby
# Before
expect(agent.has_tool?(:DelegateTaskToBackend)).to be true

# After
expect(agent.has_tool?(:WorkWithBackend)).to be true
```

2. **Update parameter names:**
```ruby
# Before
result = DelegateTaskToBackend(task: "Build API")

# After
result = WorkWithBackend(message: "Build API")
```

3. **Update documentation and prompts:**
```ruby
# Before - in system prompts
"Use DelegateTaskToBackend when you need help with APIs"

# After
"Use WorkWithBackend when you need to collaborate on APIs"
```

4. **Canonical tool name generation:**
```ruby
# Use the canonical method
tool_name = SwarmSDK::Tools::Delegate.tool_name_for(:backend)
# Returns "WorkWithBackend"
```

---

### 2. Agent::Chat Abstraction Layer

**What Changed:**
- Chat no longer inherits from RubyLLM::Chat (composition over inheritance)
- Direct access to `.tools`, `.messages`, `.model` removed
- New abstraction methods provide controlled access

**Before (v2.2.x):**
```ruby
agent = swarm.agent(:backend)

# Direct access to RubyLLM internals
agent.tools.key?(:Read)        # Check tool existence
agent.tools.keys               # List all tools
agent.model.id                 # Get model ID
agent.model.provider           # Get provider
agent.messages.count           # Count messages
agent.messages                 # Access messages array
```

**After (v2.3.0):**
```ruby
agent = swarm.agent(:backend)

# SwarmSDK abstraction API
agent.has_tool?(:Read)         # Check tool existence
agent.tool_names               # List all tools
agent.model_id                 # Get model ID
agent.model_provider           # Get provider
agent.message_count            # Count messages
agent.messages                 # Safe copy of messages
```

**Migration Table:**

| Old API (v2.2.x) | New API (v2.3.0) |
|------------------|------------------|
| `chat.tools.key?(:Read)` | `chat.has_tool?(:Read)` |
| `chat.tools.keys` | `chat.tool_names` |
| `chat.tools.count` | `chat.tool_count` |
| `chat.tools[:Read]` | Not available (use `has_tool?`) |
| `chat.model.id` | `chat.model_id` |
| `chat.model.provider` | `chat.model_provider` |
| `chat.model.context_window` | `chat.model_context_window` |
| `chat.messages.count` | `chat.message_count` |
| `chat.messages.any? { \|m\| m.role == :user }` | `chat.has_user_message?` |
| `chat.messages.last` | `chat.last_assistant_message` |

**For Plugin/Internal Code:**

If you're writing plugins or internal modules that need direct access:

```ruby
# Use internal access methods (not for public API consumption)
agent.internal_messages  # Direct array of RubyLLM messages
agent.internal_tools     # Direct hash of tool instances
agent.internal_model     # Direct RubyLLM model object
```

**Why This Change:**
- Better encapsulation of LLM library internals
- Easier future migrations if RubyLLM API changes
- More consistent and predictable API
- Prevents accidental mutation of internal state

---

### 3. Swarm vs Workflow API Separation

**What Changed:**
- `SwarmSDK.build` now **ONLY** returns `Swarm`
- New `SwarmSDK.workflow` method for multi-stage workflows
- YAML uses explicit `swarm:` or `workflow:` root keys
- `NodeOrchestrator` class renamed to `Workflow`

**Before (v2.2.x):**
```ruby
# Single method returned either Swarm or NodeOrchestrator
result = SwarmSDK.build do
  # If you used nodes, got NodeOrchestrator
  # If not, got Swarm
end
```

**After (v2.3.0):**
```ruby
# Explicit methods for each type
swarm = SwarmSDK.build do
  name "Development Team"
  lead :backend
  # Cannot use nodes here - raises ConfigurationError
end

workflow = SwarmSDK.workflow do
  name "CI Pipeline"
  start_node :planning
  # Must define nodes here
end
```

**Migration for DSL Users:**

```ruby
# Before - building a workflow
SwarmSDK.build do
  name "Pipeline"
  agent(:planner) { ... }
  node(:planning) { ... }
  start_node :planning
end

# After
SwarmSDK.workflow do
  name "Pipeline"
  agent(:planner) { ... }
  node(:planning) { ... }
  start_node :planning
end
```

**Migration for YAML Users:**

```yaml
# Before - workflow config
version: 2
swarm:
  name: "Pipeline"
  start_node: planning
  agents: { ... }
  nodes: { ... }

# After - explicit workflow key
version: 2
workflow:
  name: "Pipeline"
  start_node: planning
  agents: { ... }
  nodes: { ... }
```

**For Vanilla Swarm Users:**
No changes needed! Your code continues to work:

```ruby
# This still works exactly the same
swarm = SwarmSDK.build do
  name "Team"
  lead :backend
  agent(:backend) { ... }
end
```

```yaml
# This still works exactly the same
version: 2
swarm:
  name: "Team"
  lead: backend
  agents: { ... }
```

---

### 4. Snapshot Version 2.1.0

**What Changed:**
- Version bumped from 1.0.0 to 2.1.0
- New `plugin_states` field for plugin-specific state
- `swarm:` metadata key renamed to `metadata:`
- Type field now lowercase: `"swarm"` or `"workflow"`

**Old Snapshot Format (v1.0.0):**
```json
{
  "version": "1.0.0",
  "type": "swarm",
  "swarm": {
    "id": "main",
    "parent_id": null,
    "first_message_sent": true
  },
  "agents": { ... },
  "delegation_instances": { ... },
  "read_tracking": { ... },
  "memory_read_tracking": { ... }
}
```

**New Snapshot Format (v2.1.0):**
```json
{
  "version": "2.1.0",
  "type": "swarm",
  "snapshot_at": "2025-11-17T10:30:00Z",
  "swarm_sdk_version": "2.3.0",
  "metadata": {
    "id": "main",
    "parent_id": null,
    "name": "Development Team",
    "first_message_sent": true
  },
  "agents": { ... },
  "delegation_instances": { ... },
  "scratchpad": { ... },
  "read_tracking": { ... },
  "plugin_states": {
    "backend": { "read_entries": [...] }
  }
}
```

**Migration Steps:**

1. **Cannot restore old snapshots directly** - Create new snapshots after upgrading
2. **Manual conversion (if absolutely needed):**
```ruby
def convert_snapshot_1_to_2(old_data)
  {
    version: "2.1.0",
    type: old_data[:type] || "swarm",
    snapshot_at: Time.now.utc.iso8601,
    swarm_sdk_version: SwarmSDK::VERSION,
    metadata: old_data[:swarm] || old_data[:orchestrator],
    agents: old_data[:agents],
    delegation_instances: old_data[:delegation_instances],
    scratchpad: old_data[:scratchpad] || {},
    read_tracking: old_data[:read_tracking],
    plugin_states: convert_memory_tracking(old_data[:memory_read_tracking])
  }
end

def convert_memory_tracking(memory_tracking)
  return {} unless memory_tracking
  memory_tracking.transform_values do |entries|
    { read_entries: entries }
  end
end
```

3. **Event-sourced sessions** - Use `SnapshotFromEvents.reconstruct(events)` which automatically generates v2.1.0 snapshots

---

## Important: Plugin Lifecycle Changes

### Plugin State Persistence

**What Changed:**
- Plugins now have `snapshot_agent_state` and `restore_agent_state` methods
- SDK no longer has direct knowledge of plugin internals
- `memory_read_tracking` field replaced by generic `plugin_states`

**If You Have Custom Plugins:**

```ruby
class MyPlugin < SwarmSDK::Plugin
  # NEW - Snapshot your plugin's state
  def snapshot_agent_state(agent_name)
    {
      custom_data: @storage[agent_name]&.to_h || {}
    }
  end

  # NEW - Restore your plugin's state
  def restore_agent_state(agent_name, state)
    @storage[agent_name]&.restore(state[:custom_data])
  end

  # NEW - Get digest for change detection hooks
  def get_tool_result_digest(agent_name:, tool_name:, path:)
    return nil unless tool_name == :MyCustomRead
    @storage[agent_name]&.digest_for(path)
  end
end
```

### Plugin Configuration Decoupling

**What Changed:**
- SDK no longer knows about specific plugin configs
- Plugin configs stored in generic `@plugin_configs` hash
- Plugins handle their own YAML translation

**Agent::Definition Changes:**

```ruby
# Accessing plugin configuration
definition.plugin_config(:memory)  # Returns memory plugin config
definition.plugin_config(:custom)  # Returns custom plugin config

# Generic storage for non-SDK keys
definition.plugin_configs  # Hash of all plugin configs
```

---

## New Features (No Migration Required)

These are additions that don't break existing code:

### Observer Module

```ruby
swarm = SwarmSDK.build do
  agent :backend { ... }
  agent :security_monitor { ... }

  # NEW - Parallel agent execution
  observer :security_monitor do
    on :tool_call do |event|
      next unless event[:tool_name] == "Bash"
      "Check security of: #{event[:arguments][:command]}"
    end
    timeout 30
  end
end
```

### Context Management DSL

```ruby
agent :backend do
  # NEW - Custom context warning handlers
  context_management do
    on :warning_60 do |ctx|
      ctx.compress_tool_results(keep_recent: 15)
    end

    on :warning_80 do |ctx|
      ctx.prune_old_messages(keep_recent: 20)
    end
  end
end
```

### Non-blocking Execution

```ruby
# NEW - Async execution with cancellation
Sync do
  task = swarm.execute("Build feature", wait: false)

  # Cancel if needed
  task.stop

  # Wait for result
  result = task.wait  # Returns nil if cancelled
end
```

### Filtered Event Subscriptions

```ruby
# NEW - Subscribe to specific events
LogCollector.subscribe(filter: { type: "tool_call", agent: :backend }) do |event|
  puts "Backend called tool: #{event[:tool_name]}"
end
```

---

## Testing Your Migration

### 1. Check for Deprecated APIs

```ruby
# Run this in your test suite
describe "Migration compatibility" do
  it "uses new Chat API" do
    agent = swarm.agent(:backend)

    # These should work
    expect(agent).to respond_to(:has_tool?)
    expect(agent).to respond_to(:tool_names)
    expect(agent).to respond_to(:model_id)

    # These are gone (don't test for them)
    # agent.tools.key? - removed
    # agent.model.id - removed
  end

  it "uses new delegation names" do
    expect(agent.has_tool?(:WorkWithDatabase)).to be true
    expect(agent.has_tool?(:DelegateTaskToDatabase)).to be false
  end
end
```

### 2. Verify Workflow Separation

```ruby
describe "Workflow API" do
  it "uses separate methods" do
    # This should work
    workflow = SwarmSDK.workflow do
      node(:planning) { ... }
      start_node :planning
    end
    expect(workflow).to be_a(SwarmSDK::Workflow)

    # This should raise
    expect {
      SwarmSDK.build do
        node(:planning) { ... }  # ERROR!
      end
    }.to raise_error(SwarmSDK::ConfigurationError)
  end
end
```

### 3. Test Snapshot Compatibility

```ruby
describe "Snapshot format" do
  it "generates v2.1.0 snapshots" do
    snapshot = swarm.snapshot
    expect(snapshot.version).to eq("2.1.0")
    expect(snapshot.data[:metadata]).to be_present
    expect(snapshot.data[:swarm]).to be_nil  # Old key removed
  end
end
```

---

## Deprecation Timeline

- **v2.3.0**
  - Swarm/Workflow API separation
  - Delegation tool rebranding
  - Agent::Chat abstraction layer
  - Snapshot format v2.1.0

- **v2.4.0** (Current Release)
  - `SwarmSDK.settings` → `SwarmSDK.config`
  - Centralized configuration system
  - API key auto-proxying to RubyLLM

- **v2.5.0** (Future)
  - No breaking changes planned
  - Focus on new features

---

## Getting Help

If you encounter issues during migration:

1. **Check the CHANGELOG**: `docs/v2/CHANGELOG.swarm_sdk.md` has detailed explanations
2. **Run tests**: `bundle exec rake swarm_sdk:test` to catch compatibility issues
3. **Review examples**: `test/swarm_sdk/` contains comprehensive usage examples
4. **Report issues**: https://github.com/parruda/claude-swarm/issues

---

## Summary Checklist

### v2.4.0 Migration
- [ ] Replace `SwarmSDK.settings` with `SwarmSDK.config`
- [ ] Use `SwarmSDK.configure` block for setting values
- [ ] Update test setup/teardown to use `SwarmSDK.reset_config!`
- [ ] Remove duplicate RubyLLM API key configuration (auto-proxied now)

### v2.3.0 Migration
- [ ] Update delegation tool calls: `DelegateTaskTo*` → `WorkWith*`
- [ ] Update delegation parameters: `task:` → `message:`
- [ ] Update Chat API usage: `tools.key?` → `has_tool?`, etc.
- [ ] Separate workflows: `SwarmSDK.build` → `SwarmSDK.workflow` for node-based configs
- [ ] Update YAML: `swarm:` key for swarms, `workflow:` key for workflows
- [ ] Regenerate snapshots (v1.0.0 → v2.1.0)
- [ ] Update custom plugins with new lifecycle methods

### Final Step
- [ ] Test all changes with `bundle exec rake swarm_sdk:test`
