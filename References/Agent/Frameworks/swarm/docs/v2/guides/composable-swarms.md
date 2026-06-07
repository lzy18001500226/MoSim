# Composable Swarms Guide

Build reusable AI agent teams that can be composed together like building blocks.

---

## Overview

Composable swarms enable you to:
- **Build once, use anywhere**: Create specialized swarm teams and reuse them
- **Hierarchical composition**: Swarms can contain other swarms, unlimited nesting
- **Transparent delegation**: Delegate to swarms just like agents
- **No configuration merging**: Each swarm maintains isolated scope
- **Multiple sources**: Load from files, YAML strings, or define inline

**Key principle:** **A swarm IS an agent** - delegating to a child swarm is identical to delegating to an agent. The child swarm's lead agent serves as its public interface.

---

## Quick Start

### Ruby DSL

```ruby
# Define a reusable code review swarm (in ./swarms/code_review.rb)
SwarmSDK.build do
  id "code_review_team"
  name "Code Review Team"
  lead :lead_reviewer

  agent :lead_reviewer do
    model "claude-3-5-sonnet"
    description "Lead code reviewer"
    system "Coordinate security, style, and performance reviews"
    delegates_to "security", "style", "performance"
  end

  agent :security do
    model "gpt-4o"
    system "Security expert - analyze for vulnerabilities"
  end

  agent :style do
    model "gpt-4o-mini"
    system "Code style expert - enforce best practices"
  end

  agent :performance do
    model "gpt-4o"
    system "Performance expert - optimize code efficiency"
  end
end

# Use it in your main swarm
SwarmSDK.build do
  id "development_team"
  name "Development Team"
  lead :lead_dev

  swarms do
    register "code_review", file: "./swarms/code_review.rb"
  end

  agent :lead_dev do
    system "Lead developer coordinating the team"
    delegates_to "backend", "code_review"  # Delegate to swarm!
  end

  agent :backend do
    system "Backend developer"
  end
end

# Execute
swarm.execute("Review the authentication module")
# lead_dev → code_review swarm → lead_reviewer → security/style/performance
```

### YAML

```yaml
# File: config.yml
version: 2
swarm:
  id: development_team
  name: "Development Team"
  lead: lead_dev

  swarms:
    code_review:
      file: "./swarms/code_review.yml"
      keep_context: true

  agents:
    lead_dev:
      description: "Lead developer"
      system: "Coordinate the team"
      delegates_to:
        - backend
        - code_review  # Delegate to swarm!

    backend:
      description: "Backend developer"
      system: "Build APIs"
```

---

## Registration Methods

Composable swarms support three ways to register sub-swarms:

### 1. File Path

Load swarms from .rb (Ruby DSL) or .yml (YAML) files.

**When to use:**
- Swarm is complex and deserves its own file
- Swarm is reused across multiple parent swarms
- Team collaboration on swarm definition
- Version control separate swarm components

**Ruby DSL:**
```ruby
swarms do
  register "code_review", file: "./swarms/code_review.rb"
  register "testing", file: "./swarms/testing.yml", keep_context: false
end
```

**YAML:**
```yaml
swarms:
  code_review:
    file: "./swarms/code_review.rb"
    keep_context: true
  testing:
    file: "./swarms/testing.yml"
    keep_context: false
```

### 2. YAML String

Pass YAML content directly as a string.

**When to use:**
- Loading swarms from APIs or databases
- Dynamic swarm selection based on runtime conditions
- Configuration management systems
- Remote swarm repositories

**Ruby DSL:**
```ruby
# Fetch from API
yaml_content = HTTP.get("https://api.example.com/swarms/testing.yml").body

# Or from database
yaml_content = SwarmConfig.find_by(name: "testing").yaml_content

# Or from environment variable
yaml_content = ENV["TESTING_SWARM_CONFIG"]

swarms do
  register "testing", yaml: yaml_content, keep_context: false
end
```

**YAML:**
Not supported in YAML format (use inline definition instead).

### 3. Inline Block (DSL Only)

Define swarms inline without separate files.

**When to use:**
- Simple, single-use sub-swarms
- Testing and development
- Self-contained gems (no external files)
- Dynamically generated swarms from templates
- Co-locating swarm with usage makes sense

**Ruby DSL:**
```ruby
swarms do
  register "testing", keep_context: false do
    id "testing_team"
    name "Testing Team"
    lead :tester

    agent :tester do
      model "gpt-4o-mini"
      description "Test specialist"
      system "You write and run comprehensive tests"
      tools :Think, :Bash
    end

    agent :qa do
      model "gpt-4o"
      description "QA specialist"
      system "You validate quality and user experience"
    end
  end
end
```

### 4. Inline Definition (YAML Only)

Define swarms inline within YAML configuration.

**When to use:**
- Want everything in one YAML file
- Simple sub-swarms that don't need separate files
- Deployment simplicity (single config file)

**YAML:**
```yaml
swarms:
  testing:
    keep_context: false
    swarm:  # Inline swarm definition
      id: testing_team
      name: "Testing Team"
      lead: tester
      agents:
        tester:
          description: "Test specialist"
          model: gpt-4o-mini
          system: "You write tests"
          tools:
            - Think
            - Bash
```

---

## Hierarchical Swarm IDs

Sub-swarms automatically get hierarchical IDs based on parent ID and registration name.

**Pattern:** `"#{parent_swarm_id}/#{registration_name}"`

```ruby
SwarmSDK.build do
  id "main_app"  # Parent swarm ID

  swarms do
    register "code_review", file: "./swarms/code_review.rb"
    # Loaded swarm gets: swarm_id = "main_app/code_review"

    register "testing", file: "./swarms/testing.rb"
    # Loaded swarm gets: swarm_id = "main_app/testing"
  end
end
```

**Hierarchy example:**
```
main_app                           (root swarm)
├── main_app/code_review          (sub-swarm)
│   └── main_app/code_review/security  (nested sub-swarm)
├── main_app/testing              (sub-swarm)
└── main_app/deployment           (sub-swarm)
```

**Event tracking:**
All events include `swarm_id` and `parent_swarm_id` for complete hierarchy tracking:

```ruby
{
  type: "agent_delegation",
  swarm_id: "main_app",
  parent_swarm_id: nil,
  agent: "lead_dev",
  delegate_to: "code_review"
}

{
  type: "agent_step",
  swarm_id: "main_app/code_review",
  parent_swarm_id: "main_app",
  agent: "lead_reviewer"
}
```

---

## Context Control

Control whether sub-swarms maintain conversation history between delegations.

### keep_context: true (default)

Swarm maintains conversation history across delegations.

**Use cases:**
- Iterative work (multiple rounds of refinement)
- Stateful processes (building up knowledge)
- Collaborative sessions (back-and-forth discussion)

**Example:**
```ruby
swarms do
  register "code_review", file: "./swarms/code_review.rb", keep_context: true
end

# First delegation
swarm.agent(:backend).ask("Review the auth module")
# code_review swarm: conversation history = [user: "Review auth module", assistant: "Found 3 issues..."]

# Second delegation
swarm.agent(:backend).ask("Fix the issues you found")
# code_review swarm: remembers previous review, can reference "the 3 issues"
```

### keep_context: false

Swarm context is reset after each delegation completes.

**Use cases:**
- Stateless operations (each task independent)
- Preventing context pollution
- Enforcing fresh starts
- Memory management for long-running swarms

**Example:**
```ruby
swarms do
  register "testing", file: "./swarms/testing.rb", keep_context: false
end

# First delegation
swarm.agent(:backend).ask("Test the login endpoint")
# testing swarm: conversation history = [user: "Test login endpoint", assistant: "Tests passed"]

# After delegation completes, context is reset

# Second delegation
swarm.agent(:backend).ask("Test the signup endpoint")
# testing swarm: conversation history = [user: "Test signup endpoint", ...] (no memory of login test)
```

---

## Transparent Delegation

Delegating to a swarm is identical to delegating to an agent. The swarm's lead agent serves as the entry point.

```ruby
agent :backend do
  # Mix local agents and registered swarms in delegates_to
  delegates_to "database",      # Local agent
               "code_review",   # Registered swarm
               "testing"        # Registered swarm
end
```

**Resolution order:**
When delegating to target "code_review":
1. Check local agents (`@swarm.agents["code_review"]`)
2. Check delegation instances (`@swarm.delegation_instances["code_review@backend"]`)
3. Check registered swarms (`@swarm.swarm_registry.registered?("code_review")`)
4. Raise error if not found

**This means:**
- Local agents take precedence over swarms with same name
- Clear error messages when target not found
- No ambiguity in delegation resolution

---

## Circular Dependency Detection

Runtime detection prevents infinite delegation loops.

### Within Swarm

Detects circular delegation within a single swarm:

```ruby
SwarmSDK.build do
  id "team"

  agent :agent_a do
    delegates_to "agent_b"
  end

  agent :agent_b do
    delegates_to "agent_a"  # Circular!
  end
end

# Execution: agent_a → agent_b → agent_a (BLOCKED)
# Event emitted: delegation_circular_dependency
# LLM receives: "Error: Circular delegation detected: agent_a -> agent_b -> agent_a"
```

### Across Swarms

Each swarm has an isolated call stack, so false positives are avoided:

```ruby
# Parent swarm
SwarmSDK.build do
  id "main"

  swarms do
    register "child_swarm" do
      id "child"
      agent :agent_a do
        delegates_to "agent_b"  # This is ALLOWED
      end
    end
  end

  agent :agent_a do
    delegates_to "child_swarm"
  end
end

# Execution: main.agent_a → child_swarm → child.agent_a
# NOT circular because they're in different swarms (isolated contexts)
```

---

## Deep Nesting

Swarms can be nested unlimited levels deep.

```ruby
# File: ./swarms/security/scanner.rb
SwarmSDK.build do
  id "vulnerability_scanner"
  # ...
end

# File: ./swarms/security/audit.rb
SwarmSDK.build do
  id "security_audit"

  swarms do
    register "scanner", file: "./scanner.rb"
  end

  agent :auditor do
    delegates_to "scanner"
  end
end

# File: ./swarms/code_review.rb
SwarmSDK.build do
  id "code_review_team"

  swarms do
    register "security", file: "./security/audit.rb"
  end

  agent :reviewer do
    delegates_to "security"
  end
end

# File: main.rb
SwarmSDK.build do
  id "main"

  swarms do
    register "code_review", file: "./swarms/code_review.rb"
  end

  agent :lead do
    delegates_to "code_review"
  end
end

# Hierarchy:
# main
#   └── main/code_review
#         └── main/code_review/security
#               └── main/code_review/security/scanner
```

All events properly tagged at each level with hierarchical swarm_id!

---

## Use Cases

### 1. Specialized Teams

Create expert teams for specific domains:

```ruby
swarms do
  # Each team is a self-contained swarm
  register "security_team" do
    id "security"
    name "Security Team"
    lead :security_lead

    agent :security_lead do
      delegates_to "owasp_expert", "crypto_expert", "auth_expert"
    end

    agent :owasp_expert { system "OWASP Top 10 specialist" }
    agent :crypto_expert { system "Cryptography specialist" }
    agent :auth_expert { system "Authentication specialist" }
  end

  register "performance_team" do
    id "performance"
    name "Performance Team"
    lead :perf_lead

    agent :perf_lead do
      delegates_to "profiling", "optimization", "caching"
    end

    agent :profiling { system "Profiling specialist" }
    agent :optimization { system "Code optimization specialist" }
    agent :caching { system "Caching strategies specialist" }
  end
end
```

### 2. Dynamic Swarm Loading

Load swarms from different sources based on runtime conditions:

```ruby
# Environment-specific configurations
testing_config = case ENV["RAILS_ENV"]
when "production"
  # Load strict production testing from API
  yaml: fetch_swarm_from_api("production_testing")
when "staging"
  # Load from file
  file: "./swarms/staging_testing.yml"
else
  # Define inline for dev
  proc do
    id "dev_testing"
    name "Dev Testing"
    lead :quick_tester
    agent :quick_tester do
      model "gpt-4o-mini"
      system "Quick smoke tests only"
    end
  end
end

SwarmSDK.build do
  id "app_#{ENV['RAILS_ENV']}"

  swarms do
    if testing_config[:yaml]
      register "testing", yaml: testing_config[:yaml]
    elsif testing_config[:file]
      register "testing", file: testing_config[:file]
    else
      register "testing", &testing_config
    end
  end
end
```

### 3. Embedded Swarms in Gems

Create gems with embedded swarm teams (no external files needed):

```ruby
# In your gem
module MyGem
  def self.create_analyzer
    SwarmSDK.build do
      id "code_analyzer"
      name "Code Analyzer"
      lead :coordinator

      swarms do
        # Embed all sub-swarms in gem code
        register "security_audit" do
          id "security"
          name "Security Auditor"
          lead :security_expert

          agent :security_expert do
            model "claude-3-5-sonnet"
            system <<~PROMPT
              You are a security expert specializing in vulnerability detection.
              Analyze code for OWASP Top 10 vulnerabilities, authentication issues,
              and data validation problems.
            PROMPT
            tools :Read, :Grep, :Bash
          end
        end

        register "code_quality" do
          id "quality"
          name "Quality Checker"
          lead :quality_expert

          agent :quality_expert do
            model "gpt-4o"
            system "Analyze code quality, maintainability, and best practices"
            tools :Read, :Grep
          end
        end

        register "performance" do
          id "performance"
          name "Performance Analyzer"
          lead :perf_expert

          agent :perf_expert do
            model "gpt-4o"
            system "Analyze performance bottlenecks and optimization opportunities"
            tools :Read, :Bash
          end
        end
      end

      agent :coordinator do
        model "claude-3-5-sonnet"
        system "Coordinate comprehensive code analysis across security, quality, and performance"
        delegates_to "security_audit", "code_quality", "performance"
      end
    end
  end
end

# Users of your gem
require "my_gem"

analyzer = MyGem.create_analyzer
result = analyzer.execute("Analyze this codebase for issues")
```

### 4. Template-Based Swarm Generation

Generate swarms programmatically from templates:

```ruby
# Template function
def specialist_swarm(domain:, model:, expertise:)
  proc do
    id "#{domain}_specialist"
    name "#{domain.capitalize} Specialist"
    lead :expert

    agent :expert do
      model model
      description "#{domain} expert"
      system expertise
      tools :Read, :Write, :Bash
    end
  end
end

# Use template to generate swarms
SwarmSDK.build do
  id "multi_domain_team"
  name "Multi-Domain Team"
  lead :coordinator

  swarms do
    # Generate swarms from template
    register "security", &specialist_swarm(
      domain: "security",
      model: "claude-3-5-sonnet",
      expertise: "You are a security expert specializing in vulnerability detection..."
    )

    register "performance", &specialist_swarm(
      domain: "performance",
      model: "gpt-4o",
      expertise: "You are a performance expert specializing in optimization..."
    )

    register "accessibility", &specialist_swarm(
      domain: "accessibility",
      model: "gpt-4o",
      expertise: "You are an accessibility expert ensuring WCAG compliance..."
    )
  end

  agent :coordinator do
    model "claude-3-5-sonnet"
    system "Coordinate analysis across all specialist domains"
    delegates_to "security", "performance", "accessibility"
  end
end
```

### 5. Testing with Inline Swarms

Create test swarms without managing files:

```ruby
# In your test suite
def create_test_swarm
  SwarmSDK.build do
    id "test_main"
    name "Test Main"
    lead :main

    swarms do
      # Mock service swarm - inline definition
      register "mock_api" do
        id "mock"
        name "Mock API Service"
        lead :mocker

        agent :mocker do
          model "gpt-4o-mini"
          system "Return mock API responses: { status: 'ok', data: [...] }"
          tools :Think
        end
      end

      # Mock database swarm - inline definition
      register "mock_db" do
        id "mock_db"
        name "Mock Database"
        lead :db

        agent :db do
          model "gpt-4o-mini"
          system "Return mock database query results"
          tools :Think
        end
      end
    end

    agent :main do
      system "Main agent under test"
      delegates_to "mock_api", "mock_db"
    end
  end
end

# Test with mocked dependencies
swarm = create_test_swarm
result = swarm.execute("Fetch user data from API and save to DB")
```

---

## Best Practices

### 1. ID Naming Conventions

Use descriptive, hierarchical IDs:

```ruby
# Good
id "main_application"
id "code_review_team_v2"
id "security_audit_strict"

# Avoid
id "team"
id "cr"
id "x"
```

### 2. Swarm Granularity

**Too granular:**
```ruby
swarms do
  register "read_files" do  # Too simple - should be an agent
    agent :reader do
      system "Read files"
    end
  end
end
```

**Too coarse:**
```ruby
swarms do
  register "entire_application" do  # Too large - hard to reuse
    # 20+ agents doing everything
  end
end
```

**Just right:**
```ruby
swarms do
  register "code_review" do  # Focused, reusable team
    agent :lead_reviewer do
      delegates_to "security", "style", "performance"
    end
    # 3-5 specialized agents
  end
end
```

### 3. keep_context Guidelines

**Use `keep_context: true` (default) when:**
- Sub-swarm performs iterative work
- Multiple delegations build on previous work
- Conversation context improves results

**Use `keep_context: false` when:**
- Each delegation is independent
- Want fresh perspective each time
- Preventing context pollution matters
- Managing memory in long-running swarms

```ruby
swarms do
  # Stateful - remembers previous reviews
  register "code_review", file: "./code_review.rb", keep_context: true

  # Stateless - fresh tests each time
  register "testing", file: "./testing.rb", keep_context: false
end
```

### 4. Mixing Local Agents and Swarms

```ruby
agent :backend do
  # Best practice: List local agents first, then swarms
  delegates_to "database",      # Local agent (fast, same swarm)
               "cache",          # Local agent
               "code_review",   # External swarm (more expensive)
               "deployment"     # External swarm
end
```

---

## Advanced Patterns

### Pattern 1: Swarm Pipeline

Chain swarms for multi-stage processing:

```ruby
SwarmSDK.build do
  id "pipeline"

  swarms do
    register "analysis", file: "./swarms/analysis.rb"
    register "refactoring", file: "./swarms/refactoring.rb"
    register "testing", file: "./swarms/testing.rb"
  end

  agent :coordinator do
    system <<~PROMPT
      Process code through pipeline:
      1. Delegate to analysis for code review
      2. Based on analysis, delegate to refactoring if needed
      3. After changes, delegate to testing for validation
    PROMPT
    delegates_to "analysis", "refactoring", "testing"
  end
end
```

### Pattern 2: Conditional Swarm Loading

Load different swarms based on project type:

```ruby
# Detect project type
project_type = detect_project_type  # => :rails, :nodejs, :python

swarms do
  case project_type
  when :rails
    register "testing", file: "./swarms/rails_testing.rb"
    register "deployment", file: "./swarms/rails_deployment.rb"
  when :nodejs
    register "testing", file: "./swarms/nodejs_testing.rb"
    register "deployment", file: "./swarms/nodejs_deployment.rb"
  when :python
    register "testing", file: "./swarms/python_testing.rb"
    register "deployment", file: "./swarms/python_deployment.rb"
  end
end
```

### Pattern 3: Feature Flags for Swarms

Enable/disable swarms based on configuration:

```ruby
swarms do
  # Always available
  register "code_review", file: "./swarms/code_review.rb"

  # Optional features
  if ENV["ENABLE_SECURITY_AUDIT"]
    register "security", file: "./swarms/security_audit.rb"
  end

  if ENV["ENABLE_PERFORMANCE_ANALYSIS"]
    register "performance", file: "./swarms/performance.rb"
  end
end

agent :lead do
  delegates = ["code_review"]
  delegates << "security" if ENV["ENABLE_SECURITY_AUDIT"]
  delegates << "performance" if ENV["ENABLE_PERFORMANCE_ANALYSIS"]

  delegates_to(*delegates)
end
```

---

## Troubleshooting

### Error: "Swarm id must be set using id(...) when using composable swarms"

**Cause:** Using `swarms {}` block without setting swarm ID.

**Solution:**
```ruby
SwarmSDK.build do
  id "main_app"  # Add this!

  swarms do
    register "team", file: "./team.rb"
  end
end
```

### Error: "register 'name' requires either file:, yaml:, or a block"

**Cause:** Calling `register` without providing a source.

**Solution:**
```ruby
# Wrong
register "team"

# Right - pick one
register "team", file: "./team.rb"
register "team", yaml: yaml_string
register "team" do
  # ...
end
```

### Error: "register 'name' accepts only one of: file:, yaml:, or block (got 2)"

**Cause:** Providing multiple sources to `register`.

**Solution:**
```ruby
# Wrong
register "team", file: "./team.rb" do
  # ...
end

# Right - pick one
register "team", file: "./team.rb"
# OR
register "team" do
  # ...
end
```

### Error: "Circular delegation detected: agent_a -> agent_b -> agent_a"

**Cause:** Agents delegating in a circle, creating infinite loop.

**Solution:**
Restructure delegation to avoid cycles:
```ruby
# Wrong
agent :a do
  delegates_to "b"
end

agent :b do
  delegates_to "a"  # Circular!
end

# Right - use intermediary or rethink architecture
agent :coordinator do
  delegates_to "a", "b"
end

agent :a do
  # No delegation to b
end

agent :b do
  # No delegation to a
end
```

### Error: "Agent 'backend' delegates to unknown target 'code_review'"

**Cause:** Referencing a swarm that isn't registered.

**Solution:**
```ruby
swarms do
  register "code_review", file: "./swarms/code_review.rb"  # Add this!
end

agent :backend do
  delegates_to "code_review"
end
```

---

## Performance Considerations

### Lazy Loading

Sub-swarms are only loaded when first accessed:

```ruby
swarms do
  register "heavy_swarm", file: "./heavy.rb"  # Not loaded yet
end

# First delegation triggers load
swarm.agent(:main).ask("Use heavy_swarm")  # Loads now

# Subsequent delegations use cached instance
swarm.agent(:main).ask("Use heavy_swarm again")  # Uses cache
```

### Memory Management

```ruby
swarms do
  # Stateless swarms reset after each use (better memory)
  register "testing", file: "./testing.rb", keep_context: false

  # Stateful swarms accumulate conversation (uses more memory)
  register "code_review", file: "./code_review.rb", keep_context: true
end
```

### Cleanup

All sub-swarms are automatically cleaned up when parent swarm completes:

```ruby
swarm = SwarmSDK.build do
  swarms do
    register "child", file: "./child.rb"
  end
end

swarm.execute("Task")
# After execution:
# - swarm.cleanup is called
# - Cascades to child swarm
# - All MCP clients stopped
# - Resources released
```

---

## API Reference

Quick reference for composable swarms methods.

### Ruby DSL

```ruby
# Swarm-level
id "swarm_id"                    # Set swarm ID
swarms { }                       # Register sub-swarms

# Inside swarms {}
register "name", file: "path"                           # From file
register "name", yaml: "yaml_string", keep_context: false  # From YAML
register "name", keep_context: false do ... end         # Inline block
```

### YAML

```yaml
swarm:
  id: swarm_id
  swarms:
    name:
      file: "./path/to/swarm.rb"
      keep_context: true
    name2:
      swarm:  # Inline definition
        id: team_id
        # ... full swarm config
```

### Events

All events include:
- `swarm_id`: Current swarm ID
- `parent_swarm_id`: Parent swarm ID (null for root)

New event:
- `delegation_circular_dependency`: Emitted when circular delegation detected

---

## Migration Guide

### From Monolithic to Composable

**Before:**
```ruby
SwarmSDK.build do
  name "Development Team"
  lead :lead_dev

  # Everything in one swarm
  agent :lead_dev { delegates_to "backend", "security", "style", "performance" }
  agent :backend { }
  agent :security { }
  agent :style { }
  agent :performance { }
end
```

**After:**
```ruby
# Extract specialized teams
# File: ./swarms/code_review.rb
SwarmSDK.build do
  id "code_review_team"
  name "Code Review Team"
  lead :reviewer
  agent :reviewer { delegates_to "security", "style", "performance" }
  agent :security { }
  agent :style { }
  agent :performance { }
end

# Main swarm
SwarmSDK.build do
  id "development_team"
  name "Development Team"
  lead :lead_dev

  swarms do
    register "code_review", file: "./swarms/code_review.rb"
  end

  agent :lead_dev { delegates_to "backend", "code_review" }
  agent :backend { }
end
```

**Benefits:**
- Code review team is now reusable
- Cleaner main swarm configuration
- Easier to test and maintain
- Can be shared across projects

---

## See Also

- [Ruby DSL Reference - swarms](../reference/ruby-dsl.md#swarms)
- [Ruby DSL Reference - swarms.register](../reference/ruby-dsl.md#swarmsregister)
- [YAML Reference - swarms](../reference/yaml.md#swarms)
- [Event Payloads - delegation_circular_dependency](../reference/event_payload_structures.md#12a-delegation_circular_dependency)

---

*Guide last updated: 2025-11-02*
