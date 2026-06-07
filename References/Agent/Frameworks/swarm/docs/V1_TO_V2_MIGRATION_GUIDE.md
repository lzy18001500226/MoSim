# Migration Guide: Claude Swarm v1 → SwarmSDK v2

A comprehensive guide for migrating from Claude Swarm (v1) to SwarmSDK (v2).

---

## 📖 Table of Contents

- [TL;DR: Quick Migration Summary](#tldr-quick-migration-summary)
- [Understanding the Changes](#understanding-the-changes)
- [Step-by-Step Migration](#step-by-step-migration)
- [Configuration Changes Reference](#configuration-changes-reference)
- [Migration Examples](#migration-examples)
- [Swarm Organization Best Practices](#swarm-organization-best-practices)
- [Common Migration Scenarios](#common-migration-scenarios)
- [Troubleshooting](#troubleshooting)

---

## TL;DR: Quick Migration Summary

### What Changed?

SwarmSDK v2 is a **complete redesign** that's not backward compatible with Claude Swarm v1:

**Architecture:**
- ❌ **No more Claude Code dependency** - Decoupled from Claude Code entirely
- ✅ **Single process** - All agents run in one Ruby process using [RubyLLM](https://github.com/parruda/ruby_llm)
- ✅ **Direct method calls** - No more MCP inter-process communication overhead
- ✅ **More efficient** - Better performance and lower resource usage

**Configuration:**
- Change `version: 1` → `version: 2`
- Rename `instances` → `agents`
- Rename `connections` → `delegates_to`
- Rename `mcps` → `mcp_servers`
- Rename `allowed_tools` → `tools`
- Rename `prompt` → `system_prompt`

**New Features:**
- 🎯 Node workflows for multi-stage pipelines
- 🔧 Comprehensive hooks system (12 events, 6 action types)
- 🧠 SwarmMemory for persistent agent knowledge
- 🔌 Plugin system for extensibility
- 📊 Structured logging and cost tracking
- 🎮 Interactive REPL
- 🌐 Multiple LLM providers (Claude, OpenAI, Gemini, DeepSeek, etc.)

### Migration Effort

1. Update YAML field names
2. Test and verify behavior
3. Optional: Add new v2 features

---

## Understanding the Changes

### Why SwarmSDK v2?

Claude Swarm v1 had architectural limitations:

**v1 Architecture (Multi-Process):**
```
Main Claude Code Process
  ├── MCP Server (Instance 1 - Claude Code)
  ├── MCP Server (Instance 2 - Claude Code)
  └── MCP Server (Instance 3 - Claude Code)
```

**Problems:**
- Heavy resource usage (multiple Claude Code processes)
- MCP communication overhead (JSON serialization/deserialization)
- Complex state management across processes
- Limited control over agent behavior
- Tied to Claude Code's release cycle

**v2 Architecture (Single Process):**
```
Single Ruby Process
  ├── Agent 1 (RubyLLM)
  ├── Agent 2 (RubyLLM)
  └── Agent 3 (RubyLLM)
```

**Benefits:**
- ✅ Lightweight - Single Ruby process
- ✅ Fast - Direct method calls
- ✅ Flexible - Any LLM provider
- ✅ Feature-rich - Hooks, workflows, memory
- ✅ Better DX - Ruby DSL, structured logging

---

## Step-by-Step Migration

### Step 1: Install SwarmSDK

```bash
# Install the CLI (includes swarm_sdk)
gem install swarm_cli

# Or add to your Gemfile
gem 'swarm_sdk', '~> 2.2'
gem 'swarm_cli', '~> 2.1'
```

### Step 2: Update Configuration Version

Change the version field:

```yaml
# Before (v1)
version: 1

# After (v2)
version: 2
```

### Step 3: Update Field Names

Apply these systematic changes to your YAML:

| v1 Field | v2 Field | Notes |
|----------|----------|-------|
| `instances` | `agents` | Renamed for clarity |
| `connections` | `delegates_to` | More descriptive |
| `mcps` | `mcp_servers` | Consistent naming |
| `allowed_tools` | `tools` | Simplified |
| `prompt` | `system_prompt` | Explicit purpose |

### Step 4: Update Tool Names

No changes needed! All tools use the same names.

### Step 5: Test Your Swarm

```bash
# Interactive mode - test behavior
swarm run your_swarm.yml

# One-shot mode - automation
swarm run your_swarm.yml -p "Your test prompt"
```

### Step 6: Optional Enhancements

Consider adding v2-specific features:

**Hooks:**
```yaml
agents:
  backend:
    hooks:
      pre_tool_use:
        - matcher: "Write|Edit"
          type: command
          command: "rubocop --auto-correct"
```

**Permissions:**
```yaml
agents:
  backend:
    permissions:
      Bash:
        allowed_commands: ["^bundle", "^rake"]
      Write:
        allowed_paths: ["app/**/*", "lib/**/*"]
```

**Memory:**
```yaml
agents:
  backend:
    memory:
      enabled: true
      directory: ".swarm/memory"
```

---

## Configuration Changes Reference

### Complete Side-by-Side Comparison

#### v1 Configuration (Claude Swarm)

```yaml
version: 1
swarm:
  name: "Development Team"
  main: lead
  instances:
    lead:
      description: "Lead developer"
      directory: .
      model: opus
      connections: [frontend, backend]
      prompt: "You are the lead developer"
      allowed_tools: [Read, Edit, Bash]
      mcps:
        - name: "headless_browser"
          type: "stdio"
          command: "bundle"
          args: ["exec", "hbt", "stdio"]
      hooks:
        PreToolUse:
          - matcher: "Write|Edit"
            hooks:
              - type: "command"
                command: "rubocop --auto-correct"

    frontend:
      description: "Frontend developer"
      directory: .
      model: sonnet
      connections: []
      prompt: "You specialize in frontend"
      allowed_tools: [Read, Write, Edit]
```

#### v2 Configuration (SwarmSDK)

```yaml
version: 2
swarm:
  name: "Development Team"
  lead: lead
  agents:
    lead:
      description: "Lead developer"
      directory: .
      model: claude-opus-4-1
      provider: anthropic
      delegates_to: [frontend, backend]
      system_prompt: "You are the lead developer"
      tools: [Read, Edit, Bash]
      mcp_servers:
        - name: "headless_browser"
          type: "stdio"
          command: "bundle"
          args: ["exec", "hbt", "stdio"]
      hooks:
        pre_tool_use:
          - matcher: "Write|Edit"
            type: command
            command: "rubocop --auto-correct"

    frontend:
      description: "Frontend developer"
      directory: .
      model: sonnet
      delegates_to: []
      system_prompt: "You specialize in frontend"
      tools: [Read, Write, Edit]
```

### Key Differences

1. **Top-level structure unchanged** - Still uses `swarm:` key
2. **`main` → `lead`** - More intuitive naming
3. **`instances` → `agents`** - Clearer terminology
4. **`connections` → `delegates_to`** - More descriptive
5. **`prompt` → `system_prompt`** - Explicit purpose
6. **`allowed_tools` → `tools`** - Simplified
7. **`mcps` → `mcp_servers`** - Consistent naming
8. **Hook event names** - lowercase with underscores:
   - `PreToolUse` → `pre_tool_use`
   - `PostToolUse` → `post_tool_use`
   - `UserPromptSubmit` → `user_prompt_submit`

---

## Migration Examples

### Example 1: Simple Two-Agent Swarm

**Before (v1):**
```yaml
version: 1
swarm:
  name: "Code Review"
  main: reviewer
  instances:
    reviewer:
      description: "Code reviewer"
      model: opus
      connections: [implementer]
      prompt: "Review code and provide feedback"
      allowed_tools: [Read, Bash]

    implementer:
      description: "Code implementer"
      model: sonnet
      connections: []
      prompt: "Implement requested changes"
      allowed_tools: [Read, Write, Edit]
```

**After (v2):**
```yaml
version: 2
swarm:
  name: "Code Review"
  lead: reviewer
  agents:
    reviewer:
      description: "Code reviewer"
      model: claude-opus-4-1
      provider: anthropic
      delegates_to: [implementer]
      system_prompt: "Review code and provide feedback"
      tools: [Read, Bash]

    implementer:
      description: "Code implementer"
      model: sonnet
      system_prompt: "Implement requested changes"
      tools: [Read, Write, Edit]
```

**Changes Made:**
- `version: 1` → `version: 2`
- `main` → `lead`
- `instances` → `agents`
- `connections` → `delegates_to`
- `prompt` → `system_prompt`
- `allowed_tools` → `tools`
- Removed `connections: []` (empty arrays can be omitted)

### Example 2: Complex Multi-Agent Swarm

**Before (v1):**
```yaml
version: 1
swarm:
  name: "Full-Stack Team"
  main: architect
  instances:
    architect:
      description: "Lead architect"
      directory: .
      model: opus
      connections: [frontend, backend, qa]
      prompt: "Coordinate the development team"
      allowed_tools: [Read, Edit]

    frontend:
      description: "Frontend specialist"
      directory: ./frontend
      model: sonnet
      connections: [qa]
      prompt: "Build React components"
      allowed_tools: [Read, Write, Edit, Bash]

    backend:
      description: "Backend specialist"
      directory: ./backend
      model: sonnet
      connections: [qa]
      prompt: "Build REST APIs"
      allowed_tools: [Read, Write, Edit, Bash]

    qa:
      description: "QA engineer"
      directory: .
      model: sonnet
      connections: []
      prompt: "Test and review code"
      allowed_tools: [Read, Bash]
```

**After (v2):**
```yaml
version: 2
swarm:
  name: "Full-Stack Team"
  lead: architect
  agents:
    architect:
      description: "Lead architect"
      directory: .
      model: claude-opus-4-1
      provider: anthropic
      delegates_to: [frontend, backend, qa]
      system_prompt: "Coordinate the development team"
      tools: [Read, Edit]

    frontend:
      description: "Frontend specialist"
      directory: ./frontend
      model: claude-sonnet-4-5
      provider: anthropic
      delegates_to: [qa]
      system_prompt: "Build React components"
      tools: [Read, Write, Edit, Bash]

    backend:
      description: "Backend specialist"
      directory: ./backend
      model: claude-sonnet-4-5
      provider: anthropic
      delegates_to: [qa]
      system_prompt: "Build REST APIs"
      tools: [Read, Write, Edit, Bash]

    qa:
      description: "QA engineer"
      directory: .
      model: claude-sonnet-4-5
      provider: anthropic
      system_prompt: "Test and review code"
      tools: [Read, Bash]
```

### Example 3: With Hooks

**Before (v1):**
```yaml
version: 1
swarm:
  name: "Rails Team"
  main: lead
  instances:
    lead:
      description: "Rails developer"
      hooks:
        PreToolUse:
          - matcher: "Write|Edit"
            hooks:
              - type: "command"
                command: "rubocop --auto-correct"
        PostToolUse:
          - matcher: "Bash"
            hooks:
              - type: "command"
                command: "echo 'Command executed' >> /tmp/log"
```

**After (v2):**
```yaml
version: 2
swarm:
  name: "Rails Team"
  lead: lead
  agents:
    lead:
      description: "Rails developer"
      hooks:
        pre_tool_use:
          - matcher: "Write|Edit"
            type: command
            command: "rubocop --auto-correct"
        post_tool_use:
          - matcher: "Bash"
            type: command
            command: "echo 'Command executed' >> /tmp/log"
```

**Changes:**
- Hook event names: `PreToolUse` → `pre_tool_use`
- Hook structure: Flattened (removed nested `hooks:` array)
- Hook type: Moved `type:` to top level of hook definition

---

## Swarm Organization Best Practices

### Finding the Sweet Spot

The key to effective swarm organization is **clear separation of concerns** with **appropriate delegation**.

### Organizational Patterns

#### Pattern 1: Hierarchical Leadership

**When to use:** Complex projects with multiple domains

```yaml
version: 2
swarm:
  name: "E-Commerce Platform"
  lead: cto
  agents:
    cto:
      description: "CTO coordinating all teams"
      delegates_to: [frontend_lead, backend_lead, data_lead]
      tools: [Read]

    frontend_lead:
      description: "Frontend team lead"
      delegates_to: [react_dev, ui_designer]
      tools: [Read, Edit]

    backend_lead:
      description: "Backend team lead"
      delegates_to: [api_dev, db_engineer]
      tools: [Read, Edit]
```

**Pros:**
- Clear chain of command
- Scales well with team size
- Easy to understand responsibilities

**Cons:**
- More delegation overhead
- Can be slower for simple tasks

#### Pattern 2: Flat Collaboration

**When to use:** Small teams, simple projects

```yaml
version: 2
swarm:
  name: "Microservice Team"
  lead: coordinator
  agents:
    coordinator:
      description: "Coordinates peer developers"
      delegates_to: [dev1, dev2, dev3]
      tools: [Read]

    dev1:
      description: "Full-stack developer"
      tools: [Read, Write, Edit, Bash]

    dev2:
      description: "Full-stack developer"
      tools: [Read, Write, Edit, Bash]
```

**Pros:**
- Simple structure
- Fast execution
- Low overhead

**Cons:**
- Doesn't scale well
- Can be confusing with many agents

#### Pattern 3: Specialized Roles

**When to use:** Projects requiring distinct expertise

```yaml
version: 2
swarm:
  name: "Development Lifecycle"
  lead: product_manager
  agents:
    product_manager:
      description: "Translates requirements"
      delegates_to: [architect, developer, qa, devops]
      tools: [Read, Write]

    architect:
      description: "Designs system architecture"
      tools: [Read, Write]

    developer:
      description: "Implements features"
      delegates_to: [qa]
      tools: [Read, Write, Edit, Bash]

    qa:
      description: "Tests implementation"
      tools: [Read, Bash]

    devops:
      description: "Handles deployment"
      tools: [Read, Bash]
```

**Pros:**
- Clear expertise boundaries
- High-quality specialized output
- Easy to add/remove roles

**Cons:**
- More complex delegation
- Requires clear handoffs

### Responsibility Ownership Guidelines

#### 1. Lead Agent Responsibilities

The lead agent should:
- ✅ Understand the overall goal
- ✅ Break down complex tasks
- ✅ Delegate to specialists
- ✅ Synthesize results
- ❌ NOT implement everything themselves

**Example Lead System Prompt:**
```yaml
lead:
  system_prompt: |
    You coordinate a development team with these specialists:
    - frontend_dev: React, UI/UX, styling
    - backend_dev: APIs, databases, business logic
    - qa_engineer: Testing, code review

    Your responsibilities:
    1. Understand the user's request
    2. Break it into frontend/backend/qa tasks
    3. Delegate to appropriate specialists
    4. Review and integrate their work
    5. Ensure requirements are met

    DON'T write code yourself - delegate to specialists.
```

#### 2. Specialist Agent Responsibilities

Specialist agents should:
- ✅ Focus on their domain
- ✅ Have necessary tools for their work
- ✅ Delegate to other specialists when needed
- ❌ NOT work outside their expertise

**Example Specialist:**
```yaml
backend_dev:
  system_prompt: |
    You are a backend specialist focusing on:
    - REST APIs and GraphQL
    - Database design and queries
    - Business logic and services
    - Authentication and authorization

    You can delegate to:
    - qa_engineer: For testing your work

    Stay in your lane - don't touch frontend code.
```

#### 3. Delegation Patterns

**Cross-cutting delegation:**
```yaml
# Good: Frontend and backend can both delegate to QA
frontend_dev:
  delegates_to: [qa_engineer]

backend_dev:
  delegates_to: [qa_engineer]
```

**Sequential delegation:**
```yaml
# Good: Clear pipeline
developer:
  delegates_to: [code_reviewer]

code_reviewer:
  delegates_to: [qa_engineer]
```

**Avoid circular delegation:**
```yaml
# ❌ BAD: Circular dependency
agent_a:
  delegates_to: [agent_b]

agent_b:
  delegates_to: [agent_a]  # Error!
```

### Tool Distribution Strategy

#### Strategy 1: Least Privilege

Give agents only the tools they need:

```yaml
architect:
  tools: [Read]  # Only reads code

developer:
  tools: [Read, Write, Edit, Bash]  # Full development tools

qa:
  tools: [Read, Bash]  # Read and test
```

#### Strategy 2: Shared Core + Specialized

```yaml
all_agents:
  tools: [Read, Think]  # Everyone gets these

agents:
  developer:
    tools: [Write, Edit, Bash]  # Additional tools

  qa:
    tools: [Bash]  # Additional tools
```

#### Strategy 3: Progressive Access

```yaml
junior_dev:
  tools: [Read, Write]
  permissions:
    Write:
      allowed_paths: ["src/components/**/*"]

senior_dev:
  tools: [Read, Write, Edit, Bash]
  # Full access
```

### Real-World Examples

#### Example 1: Rails Development Team

```yaml
version: 2
swarm:
  name: "Rails Expert Team"
  lead: senior_rails_dev
  agents:
    senior_rails_dev:
      description: "Senior Rails developer coordinating team"
      system_prompt: |
        You coordinate a Rails team with:
        - backend_dev: Models, controllers, services, jobs, APIs
        - frontend_dev: Views, Stimulus/Turbo, assets, CSS/JS
        - test_engineer: Minitest, fixtures, system tests

        Delegate Rails work appropriately and ensure quality.
      tools: [Read, Edit, Bash]
      delegates_to: [backend_dev, frontend_dev, test_engineer]

    backend_dev:
      description: "Backend Rails specialist"
      system_prompt: |
        You focus on Rails backend:
        - ActiveRecord models and migrations
        - Controllers and services
        - ActiveJob background jobs
        - REST APIs and JSON responses

        Always delegate to test_engineer for test coverage.
      tools: [Read, Write, Edit, Bash]
      delegates_to: [test_engineer]

    frontend_dev:
      description: "Frontend Rails specialist"
      system_prompt: |
        You focus on Rails frontend:
        - ERB views and partials
        - Stimulus controllers
        - Turbo Frames/Streams
        - Asset pipeline and JavaScript

        Always delegate to test_engineer for system tests.
      tools: [Read, Write, Edit]
      delegates_to: [test_engineer]

    test_engineer:
      description: "Rails testing specialist"
      system_prompt: |
        You write comprehensive Rails tests:
        - Unit tests for models
        - Controller tests
        - System tests with Capybara
        - Fixtures and factories

        Ensure high test coverage and quality.
      tools: [Read, Write, Edit, Bash]
```

**Why this works:**
- Clear role separation
- Backend/frontend don't overlap
- Both delegate to testing
- Senior dev coordinates but doesn't implement

#### Example 2: Microservices Platform

```yaml
version: 2
swarm:
  name: "Microservices Platform"
  lead: platform_architect
  agents:
    platform_architect:
      description: "Platform architect"
      system_prompt: |
        You design microservices architecture and coordinate:
        - auth_service_dev: Authentication microservice
        - api_gateway_dev: API gateway
        - core_service_dev: Core business logic service
        - shared_lib_dev: Shared libraries

        Focus on system design, not implementation.
      tools: [Read, Write]
      delegates_to: [auth_service_dev, api_gateway_dev, core_service_dev]

    auth_service_dev:
      description: "Auth service developer"
      system_prompt: |
        You develop the authentication microservice:
        - OAuth2 and JWT
        - User management
        - Session handling

        Directory: backend/auth-service/
      directory: backend/auth-service
      tools: [Read, Write, Edit, Bash]
      delegates_to: [shared_lib_dev]

    api_gateway_dev:
      description: "API gateway developer"
      system_prompt: |
        You develop the API gateway:
        - Request routing
        - Rate limiting
        - Request transformation

        Directory: backend/api-gateway/
      directory: backend/api-gateway
      tools: [Read, Write, Edit, Bash]
      delegates_to: [shared_lib_dev]

    core_service_dev:
      description: "Core service developer"
      system_prompt: |
        You develop the core business logic service:
        - Main application features
        - Business rules
        - Data processing

        Directory: backend/core-service/
      directory: backend/core-service
      tools: [Read, Write, Edit, Bash]
      delegates_to: [shared_lib_dev]

    shared_lib_dev:
      description: "Shared libraries developer"
      system_prompt: |
        You maintain shared code used across services:
        - Common utilities
        - Shared types/interfaces
        - Reusable components

        Directory: shared-libs/
      directory: shared-libs
      tools: [Read, Write, Edit, Bash]
```

**Why this works:**
- Each service has dedicated developer
- Directory isolation prevents conflicts
- Shared lib developer prevents duplication
- Architect designs without implementing

#### Example 3: Data Platform Team

```yaml
version: 2
swarm:
  name: "Data Platform"
  lead: data_lead
  agents:
    data_lead:
      description: "Data team lead"
      system_prompt: |
        You lead the data team:
        - data_engineer: ETL pipelines, data warehouse
        - ml_engineer: ML models, training, deployment
        - analytics_dev: Dashboards, reports, BI

        Coordinate data initiatives and architecture.
      tools: [Read, Edit]
      delegates_to: [data_engineer, ml_engineer, analytics_dev]

    data_engineer:
      description: "Data engineer"
      system_prompt: |
        You build data infrastructure:
        - ETL/ELT pipelines
        - Data warehouse design
        - Streaming data (Kafka, etc.)
        - Data quality checks

        Directory: data-platform/pipelines/
      directory: data-platform/pipelines
      tools: [Read, Write, Edit, Bash]

    ml_engineer:
      description: "ML engineer"
      system_prompt: |
        You develop ML models:
        - Model training and tuning
        - Feature engineering
        - Model deployment
        - A/B testing

        Directory: data-platform/ml-models/
      directory: data-platform/ml-models
      tools: [Read, Write, Edit, Bash]

    analytics_dev:
      description: "Analytics developer"
      system_prompt: |
        You create analytics and BI:
        - SQL queries and views
        - Dashboards and visualizations
        - Business intelligence reports
        - Data storytelling

        Directory: data-platform/analytics/
      directory: data-platform/analytics
      tools: [Read, Write, Edit, Bash]
```

**Why this works:**
- Distinct data disciplines
- Clear data flow: engineer → ML/analytics
- No overlap in responsibilities
- Lead focuses on coordination

---

## Common Migration Scenarios

### Scenario 1: Basic Configuration Only

**If you only have:**
- Agent definitions
- Basic tool assignments
- Simple connections

**Migration time: 5-10 minutes**

Just update field names and test.

### Scenario 2: With MCP Servers

**If you have:**
- External MCP server integrations

**Changes needed:**
- `mcps` → `mcp_servers`
- Structure remains the same

**Migration time: 10-15 minutes**

### Scenario 3: With Hooks

**If you have:**
- Shell hooks for validation
- Pre/post tool use hooks

**Changes needed:**
- Event names: `PreToolUse` → `pre_tool_use`
- Flatten hook structure
- Move `type` to top level

**Migration time: 15-20 minutes**

### Scenario 4: Complex Multi-Directory Setup

**If you have:**
- Multiple agents in different directories
- Worktree configurations

**Good news:**
- Directory configurations work the same
- Worktrees not needed in v2 (single process)

**Migration time: 10-15 minutes**

### Scenario 5: Custom Provider (OpenAI)

**If you have:**
- OpenAI provider configurations
- Custom API parameters

**Changes needed:**
- None! Provider configs transfer directly

**Migration time: 5 minutes**

---

## Troubleshooting

### Error: "SwarmSDK requires version: 2"

**Problem:** You forgot to update the version field.

**Solution:**
```yaml
# Change this
version: 1

# To this
version: 2
```

### Error: "Missing 'agents' field in swarm configuration"

**Problem:** You didn't rename `instances` to `agents`.

**Solution:**
```yaml
# Change this
swarm:
  instances:
    ...

# To this
swarm:
  agents:
    ...
```

### Error: "Agent 'X' missing required 'description' field"

**Problem:** Description is now required in v2.

**Solution:**
Add a description to every agent:
```yaml
agents:
  backend:
    description: "Backend developer specializing in APIs"
    ...
```

### Error: Unknown field 'connections'

**Problem:** Field renamed to `delegates_to`.

**Solution:**
```yaml
# Change this
agents:
  lead:
    connections: [backend, frontend]

# To this
agents:
  lead:
    delegates_to: [backend, frontend]
```

### Error: Unknown field 'allowed_tools'

**Problem:** Field renamed to `tools`.

**Solution:**
```yaml
# Change this
agents:
  dev:
    allowed_tools: [Read, Write]

# To this
agents:
  dev:
    tools: [Read, Write]
```

### Migration Checklist

Use this checklist to ensure complete migration:

- [ ] Updated `version: 1` to `version: 2`
- [ ] Renamed `main` to `lead`
- [ ] Renamed `instances` to `agents`
- [ ] Renamed `connections` to `delegates_to`
- [ ] Renamed `allowed_tools` to `tools`
- [ ] Renamed `prompt` to `system_prompt`
- [ ] Renamed `mcps` to `mcp_servers` (if used)
- [ ] Updated hook event names to lowercase (if used)
- [ ] Added `description` to all agents
- [ ] Added the `provider` key to all agents
- [ ] Tested configuration with `swarm run`
- [ ] Verified agent delegation works
- [ ] Confirmed tools execute correctly

---

## Need Help?

### Resources

- **[SwarmSDK Documentation](docs/v2/README.md)** - Complete v2 documentation
- **[Complete Tutorial](docs/v2/guides/complete-tutorial.md)** - In-depth feature guide
- **[YAML Reference](docs/v2/reference/yaml.md)** - Full configuration reference
- **[CLI Reference](docs/v2/reference/cli.md)** - Command-line usage

### Support

- **GitHub Issues**: [Report issues](https://github.com/parruda/claude-swarm/issues)
- **Examples**: Check `examples/v2/` directory for working configurations

---

## Next Steps

After migration, explore v2 features:

1. **[Node Workflows](docs/v2/guides/complete-tutorial.md#part-5-node-workflows)** - Multi-stage pipelines
2. **[Hooks System](docs/v2/guides/complete-tutorial.md#part-4-hooks-system)** - Custom lifecycle logic
3. **[SwarmMemory](docs/v2/guides/swarm-memory.md)** - Persistent agent knowledge
4. **[Composable Swarms](docs/v2/guides/composable-swarms.md)** - Reusable team components
5. **[Permissions](docs/v2/guides/complete-tutorial.md#permissions-system)** - Fine-grained control

---

**Happy Migrating! 🚀**
