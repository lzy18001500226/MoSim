#!/usr/bin/env bash
set -euo pipefail

# generate_agent_prd_skeleton.sh - Generate AI Agent PRD document structure
# Usage: generate_agent_prd_skeleton.sh [--force] <output_dir> <agent_name>

usage() {
  cat <<'EOF'
Usage:
  generate_agent_prd_skeleton.sh [--force] <output_dir> <agent_name>

Generates a complete AI Agent PRD document structure with templates.

Example:
  generate_agent_prd_skeleton.sh ./docs/agent-prd "Customer Support Agent"
  generate_agent_prd_skeleton.sh --force ./docs/agent-prd "Customer Support Agent"
EOF
}

force_overwrite=0
if [[ "${1:-}" == "--force" ]]; then
  force_overwrite=1
  shift
fi

if [[ $# -lt 2 ]]; then
  usage
  exit 1
fi

output_dir="$1"
agent_name="$2"
date_now=$(date +"%Y-%m-%d")

if [[ -d "$output_dir" && $force_overwrite -eq 0 ]]; then
  if find "$output_dir" -mindepth 1 -maxdepth 1 -print -quit | grep -q .; then
    echo "Error: output directory is not empty: $output_dir" >&2
    echo "Refusing to overwrite existing files. Use --force to overwrite." >&2
    exit 2
  fi
fi

mkdir -p "$output_dir"

echo "Creating AI Agent PRD structure for: $agent_name"
echo "Output directory: $output_dir"

# Main PRD document
cat > "$output_dir/AGENT_PRD.md" << ENDPRD
# AI Agent PRD: $agent_name

| Field | Value |
|-------|-------|
| **Agent Name** | $agent_name |
| **Author** | [Your Name] |
| **Status** | Draft |
| **Version** | 0.1 |
| **Created** | $date_now |
| **Last Updated** | $date_now |

---

## 1. Executive Summary

### 1.1 Agent Mission

**One Sentence:** [Why does this agent exist?]

### 1.2 Value Proposition

| For | Who | The Agent | Unlike | Our Agent |
|-----|-----|-----------|--------|-----------|
| [Target user] | [User need] | [Is a solution that] | [Alternative] | [Differentiator] |

### 1.3 Success Metrics

| Metric | Definition | Target | Timeline |
|--------|------------|--------|----------|
| [Primary] | [Definition] | [Target] | [When] |
| [Secondary] | [Definition] | [Target] | [When] |

---

## 2. Agent Identity

See: [IDENTITY.md](./IDENTITY.md)

---

## 3. Users & Use Cases

See: [USE_CASES.md](./USE_CASES.md)

---

## 4. Capability Architecture

### 4.1 Skills

See: [SKILLS.md](./SKILLS.md)

### 4.2 Tools

See: [TOOLS.md](./TOOLS.md)

### 4.3 Memory

See: [MEMORY.md](./MEMORY.md)

### 4.4 Knowledge (RAG)

See: [KNOWLEDGE.md](./KNOWLEDGE.md)

### 4.5 Workflows

See: [WORKFLOWS.md](./WORKFLOWS.md)

---

## 5. Behavior Specification

See: [BEHAVIOR.md](./BEHAVIOR.md)

---

## 6. Safety & Guardrails

See: [SAFETY.md](./SAFETY.md)

---

## 7. Evaluation Framework

See: [EVALUATION.md](./EVALUATION.md)

---

## 8. Operational Model

### 8.1 Cost Model

| Component | Unit Cost | Avg Usage | Per-Interaction |
|-----------|-----------|-----------|-----------------|
| LLM (input) | \$[X]/1K | [X] tokens | \$[X] |
| LLM (output) | \$[X]/1K | [X] tokens | \$[X] |
| **Total** | | | **\$[X]** |

### 8.2 Scaling Strategy

[Define scaling approach]

---

## 9. Timeline & Milestones

| Milestone | Date | Deliverables |
|-----------|------|--------------|
| Alpha | [Date] | [What] |
| Beta | [Date] | [What] |
| Launch | [Date] | [What] |

---

## 10. Risks & Open Questions

### Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| [Risk] | H/M/L | H/M/L | [Strategy] |

### Open Questions

| Question | Owner | Due | Status |
|----------|-------|-----|--------|
| [Question] | [Name] | [Date] | Open |

---

## Appendix

### A. Glossary

| Term | Definition |
|------|------------|
| [Term] | [Definition] |

### B. System Prompt (Draft)

\`\`\`
[Draft system prompt for the agent]
\`\`\`

### C. Example Conversations

See: [EXAMPLES.md](./EXAMPLES.md)
ENDPRD

# Identity document
cat > "$output_dir/IDENTITY.md" << 'ENDIDENTITY'
# Agent Identity

## Persona

| Attribute | Specification |
|-----------|---------------|
| **Name** | [Agent name] |
| **Role** | [What role does it play?] |
| **Personality** | [3-5 traits] |
| **Communication Style** | [How it communicates] |
| **Expertise Domain** | [Area of expertise] |

## Identity Boundaries

| What It IS | What It Is NOT |
|------------|----------------|
| [Positive definition] | [Negative definition] |

## User Relationship

**Primary Model:** [ ] Copilot [ ] Autopilot [ ] Peer [ ] Expert [ ] Executor

**Relationship Dynamics:**

| Situation | Mode | Behavior |
|-----------|------|----------|
| [Situation] | [Mode] | [Behavior] |
ENDIDENTITY

# Use cases document
cat > "$output_dir/USE_CASES.md" << 'ENDUSECASES'
# Users & Use Cases

## User Personas

### Primary Persona: [Name]

| Attribute | Description |
|-----------|-------------|
| **Role** | [Job/function] |
| **Goal** | [What they want] |
| **Pain Points** | [Frustrations] |
| **Technical Level** | [Level] |
| **Trust Level** | [Autonomy given] |

---

## Use Cases

### UC-001: [Use Case Name]

| Attribute | Specification |
|-----------|---------------|
| **User** | [Persona] |
| **Goal** | [Objective] |
| **Trigger** | [How initiated] |
| **Happy Path** | [Ideal flow] |
| **Success Criteria** | [How measured] |
| **Frequency** | [How often] |

[Repeat for each use case]
ENDUSECASES

# Skills document
cat > "$output_dir/SKILLS.md" << 'ENDSKILLS'
# Skills Specification

## Skills Inventory

| Skill | Purpose | Priority | Dependencies |
|-------|---------|----------|--------------|
| [Skill] | [Purpose] | P0/P1/P2 | [Dependencies] |

---

## Skill: [Name]

### Purpose
[What this skill enables]

### Trigger
- Intent: [patterns]
- Context: [conditions]

### Input
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| [param] | [type] | [Y/N] | [description] |

### Process
```
1. [Step]
2. [Step]
```

### Output
| Field | Type | Description |
|-------|------|-------------|
| [field] | [type] | [description] |

### Examples
| Input | Output |
|-------|--------|
| [example] | [result] |

### Boundaries
- Cannot: [limitations]

[Repeat for each skill]
ENDSKILLS

# Tools document
cat > "$output_dir/TOOLS.md" << 'ENDTOOLS'
# Tools Specification

## Tools Inventory

| Tool | Purpose | Type | Risk |
|------|---------|------|------|
| [Tool] | [Purpose] | [Read/Write] | [Low/Med/High] |

---

## Tool: [Name]

### Overview
- **Name:** `[tool_name]`
- **Category:** [Read/Write/Execute]
- **Risk Level:** [Low/Medium/High]

### Interface
```json
{
  "name": "[tool_name]",
  "description": "[Description for LLM]",
  "parameters": {
    "type": "object",
    "properties": {
      "[param]": {
        "type": "[type]",
        "description": "[description]"
      }
    }
  }
}
```

### Execution
| Attribute | Value |
|-----------|-------|
| Endpoint | [URL] |
| Timeout | [seconds] |
| Rate Limit | [limit] |

### Response Handling
| Status | Interpretation | Action |
|--------|----------------|--------|
| 200 | Success | [action] |
| 4xx | Error | [recovery] |

### Safety
| Check | Specification |
|-------|---------------|
| Confirmation Required | [when] |
| Audit | [what to log] |

[Repeat for each tool]
ENDTOOLS

# Memory document
cat > "$output_dir/MEMORY.md" << 'ENDMEMORY'
# Memory Architecture

## Memory Types

### Working Memory
| Attribute | Specification |
|-----------|---------------|
| Capacity | [tokens] |
| Priority | [what to keep] |
| Truncation | [strategy] |

### Session Memory
| Attribute | Specification |
|-----------|---------------|
| Duration | [time] |
| Contents | [what's stored] |
| Reset | [triggers] |

### Long-term Memory
| Attribute | Specification |
|-----------|---------------|
| Contents | [what's persisted] |
| Retention | [duration] |
| User Control | [options] |

## Memory Schema

```json
{
  "profile": {
    "preferences": {},
    "settings": {}
  },
  "facts": [],
  "history": []
}
```

## Retrieval Strategy

| Trigger | Method | Top-K |
|---------|--------|-------|
| [trigger] | [method] | [k] |
ENDMEMORY

# Knowledge document
cat > "$output_dir/KNOWLEDGE.md" << 'ENDKNOWLEDGE'
# Knowledge Architecture (RAG)

## Knowledge Sources

| Source | Content | Update Frequency |
|--------|---------|------------------|
| [Source] | [Content type] | [Frequency] |

## Retrieval Configuration

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| Embedding Model | [model] | [why] |
| Chunk Size | [tokens] | [why] |
| Top-K | [number] | [why] |
| Threshold | [score] | [why] |

## Knowledge Gaps

| Scenario | Detection | Response |
|----------|-----------|----------|
| No results | [method] | [response] |
| Low confidence | [method] | [response] |

## Citation
- Style: [how cited]
- Display confidence: [yes/no]
ENDKNOWLEDGE

# Workflows document
cat > "$output_dir/WORKFLOWS.md" << 'ENDWORKFLOWS'
# Workflow Specifications

## Workflow: [Name]

### Purpose
[What this workflow accomplishes]

### Trigger
[How initiated]

### Flow Diagram
```
Step 1 → Step 2 → Decision
                    ├→ Path A
                    └→ Path B
```

### Steps

| Step | Actor | Action | Success | Failure |
|------|-------|--------|---------|---------|
| 1 | [Who] | [What] | [Criteria] | [Recovery] |

### Human Checkpoints

| Checkpoint | Trigger | Timeout |
|------------|---------|---------|
| [Name] | [When] | [Default action] |

[Repeat for each workflow]
ENDWORKFLOWS

# Behavior document
cat > "$output_dir/BEHAVIOR.md" << 'ENDBEHAVIOR'
# Behavior Specification

## Reasoning Strategy

**Primary:** [ ] ReAct [ ] Plan-then-Execute [ ] Tree of Thought [ ] Reflexion

### Process
1. Perceive: [how it understands]
2. Think: [how it reasons]
3. Plan: [how it plans]
4. Act: [how it executes]
5. Reflect: [how it evaluates]

## Decision Framework

### Priority Order
1. [Highest priority]
2. [Second priority]
3. [Third priority]

### Decision Rules

| Situation | Decision |
|-----------|----------|
| [Situation] | [Rule] |

## Conversation Design

### Voice & Tone

| Attribute | Specification |
|-----------|---------------|
| Persona | [style] |
| Formality | [level] |
| Verbosity | [level] |

### Response Patterns

| Scenario | Pattern |
|----------|---------|
| Simple question | [pattern] |
| Complex task | [pattern] |
| Error | [pattern] |
| Out of scope | [pattern] |
ENDBEHAVIOR

# System prompt spec document
cat > "$output_dir/SYSTEM_PROMPT_SPEC.md" << 'ENDSYSPROMPT'
# System Prompt Design Specification

This document specifies the **design intent** for the agent's system prompt (not necessarily the final prompt text).

Reference: `references/system-prompt-design.md`

---

## 1) Identity Declaration

- Role / persona: [who the agent is]
- Domain expertise: [what it is expert in]
- Voice & tone: [how it speaks]

## 2) Capability Declaration

List available capabilities and when to use them.

### Skills
| Skill | When to use | Inputs | Outputs | Boundaries |
|------|-------------|--------|---------|------------|
| [skill] | [trigger] | [inputs] | [outputs] | [limits] |

### Tools
| Tool | When to use | Risk | Confirmation required? | Logging |
|------|-------------|------|------------------------|---------|
| [tool] | [trigger] | Low/Med/High | Yes/No | [what] |

## 3) Behavioral Instructions

- Reasoning strategy: [ReAct / Plan-then-Execute / ...]
- Ask vs act: [when to ask clarifying questions]
- Default output formats: [bullets/tables/json/etc.]
- Uncertainty handling: [how to express confidence]

## 4) Constraint Boundaries

- Must never do: [prohibited actions]
- Must ask before doing: [confirmation-required actions]
- Always disclose: [limitations / assumptions / data freshness]

## 5) Escalation Rules

| Trigger | Action | Handoff target | What to include |
|--------|--------|----------------|-----------------|
| [trigger] | escalate | [human/team] | [context] |

## 6) Safety & Compliance Hooks

- Prompt injection defenses: [detection + response]
- PII handling: [rules]
- High-risk domains: [medical/legal/finance/etc.]
ENDSYSPROMPT

# Golden conversations document
cat > "$output_dir/CONVERSATIONS.md" << 'ENDCONV'
# Golden Conversations

Golden conversations are the **most precise behavioral specification** for an agent:
- Acceptance criteria (does it behave like this?)
- Few-shot candidates (optional)
- Evaluation dataset seeds

Reference: `references/conversation-design.md`

---

## Conversation: [Scenario Name]
**Type:** [happy-path | edge-case | safety | multi-turn | error]
**Tests:** [Which capabilities/rules this validates]

### Dialogue
User: [input]
Agent: [expected response]
// Annotation: [Why this is correct. What rules apply.]

User: [follow-up]
Agent: [expected response]
// Annotation: [Key behavior being demonstrated]

### Unacceptable Alternatives
- Agent should NOT: [bad behavior]
- Agent should NOT: [bad behavior]

### Evaluation Criteria
- [ ] [Checkable criterion 1]
- [ ] [Checkable criterion 2]

---

## Coverage Checklist

- [ ] Happy path (2–3 per core use case)
- [ ] Edge cases (1–2 per use case)
- [ ] Safety boundaries (3–5 total)
- [ ] Multi-turn complex (2–3 total)
- [ ] Context switching (1–2 total)
- [ ] Error recovery (2–3 total)
- [ ] Out-of-scope (2–3 total)
ENDCONV

# Safety document
cat > "$output_dir/SAFETY.md" << 'ENDSAFETY'
# Safety & Guardrails

## Capability Boundaries

### Authorized Actions
| Category | Actions | Conditions |
|----------|---------|------------|
| [Category] | [Actions] | [When] |

### Prohibited Actions
| Action | Reason | Response |
|--------|--------|----------|
| [Action] | [Why] | [What to say] |

## Human Oversight

### Approval Required
| Trigger | Approver | Timeout | Default |
|---------|----------|---------|---------|
| [Trigger] | [Who] | [Time] | [Action] |

## Input Guardrails

| Check | Method | Response |
|-------|--------|----------|
| Prompt injection | [method] | [response] |
| Harmful request | [method] | [response] |

## Output Guardrails

| Check | Method | Response |
|-------|--------|----------|
| Harmful content | [method] | [response] |
| PII leakage | [method] | [response] |

## Error Handling

| Error | Detection | Message | Recovery |
|-------|-----------|---------|----------|
| [Type] | [How] | [Message] | [Action] |
ENDSAFETY

# Evaluation document
cat > "$output_dir/EVALUATION.md" << 'ENDEVAL'
# Evaluation Framework

## Core Metrics

| Metric | Definition | Target | Measurement |
|--------|------------|--------|-------------|
| Task Success | [definition] | >X% | [how] |
| Quality | [definition] | >X | [how] |
| Safety | [definition] | 100% | [how] |
| Latency | [definition] | <Xs | [how] |
| CSAT | [definition] | >X | [how] |

## Evaluation Methods

### Automated
- [ ] Task completion testing
- [ ] Safety classifier
- [ ] Regression testing

### Human Evaluation
- Frequency: [how often]
- Sample: [size]
- Rubric: [link]

### Red Team
- Scope: [what]
- Frequency: [when]

## Benchmarks

| Benchmark | Purpose | Pass Criteria |
|-----------|---------|---------------|
| [Name] | [Tests] | [Criteria] |
ENDEVAL

# Examples document
cat > "$output_dir/EXAMPLES.md" << 'ENDEXAMPLES'
# Example Conversations

## Example 1: [Scenario Name]

**Context:** [Setup/background]

**Conversation:**
```
User: [message]
Agent: [response]
User: [message]
Agent: [response]
```

**Notes:** [Key behaviors demonstrated]

---

## Example 2: [Error Handling]

**Context:** [Error scenario]

**Conversation:**
```
User: [message]
Agent: [response showing error handling]
```

**Notes:** [How error was handled]

---

## Example 3: [Edge Case]

**Context:** [Edge case scenario]

**Conversation:**
```
User: [message]
Agent: [response]
```

**Notes:** [How edge case was handled]
ENDEXAMPLES

# Checklist document
cat > "$output_dir/CHECKLIST.md" << 'ENDCHECK'
# Agent PRD Completion Checklist

## Identity & Purpose
- [ ] Agent mission defined
- [ ] Persona specified
- [ ] Boundaries clear (is/is not)
- [ ] User relationship model defined

## Users & Use Cases
- [ ] User personas documented
- [ ] Use cases prioritized
- [ ] Success criteria defined

## Capabilities
- [ ] Skills inventory complete
- [ ] Each skill specified (trigger, I/O, examples)
- [ ] Tools inventory complete
- [ ] Each tool specified (interface, safety)
- [ ] Memory architecture defined
- [ ] Knowledge/RAG configured
- [ ] Workflows documented

## Behavior
- [ ] Reasoning strategy chosen
- [ ] Decision framework defined
- [ ] Conversation patterns specified

## Safety
- [ ] Capability boundaries set
- [ ] Human oversight defined
- [ ] Input guardrails specified
- [ ] Output guardrails specified
- [ ] Error handling complete

## Evaluation
- [ ] Metrics defined with targets
- [ ] Evaluation methods specified
- [ ] Benchmarks created

## Operational
- [ ] Cost model estimated
- [ ] Scaling approach defined
- [ ] Timeline set

## Review
- [ ] Stakeholders reviewed
- [ ] Engineering reviewed
- [ ] Example conversations created
ENDCHECK

echo ""
echo "AI Agent PRD structure created successfully!"
echo ""
echo "Files created:"
echo "  $output_dir/AGENT_PRD.md     - Main PRD document"
echo "  $output_dir/IDENTITY.md      - Agent identity"
echo "  $output_dir/USE_CASES.md     - Users and use cases"
echo "  $output_dir/SKILLS.md        - Skills specification"
echo "  $output_dir/TOOLS.md         - Tools specification"
echo "  $output_dir/MEMORY.md        - Memory architecture"
echo "  $output_dir/KNOWLEDGE.md     - RAG configuration"
echo "  $output_dir/WORKFLOWS.md     - Workflow definitions"
echo "  $output_dir/BEHAVIOR.md      - Behavior specification"
echo "  $output_dir/SYSTEM_PROMPT_SPEC.md - System prompt design specification"
echo "  $output_dir/CONVERSATIONS.md - Golden conversations"
echo "  $output_dir/SAFETY.md        - Safety guardrails"
echo "  $output_dir/EVALUATION.md    - Evaluation framework"
echo "  $output_dir/EXAMPLES.md      - Example conversations"
echo "  $output_dir/CHECKLIST.md     - Completion checklist"
echo ""
echo "Next steps:"
echo "  1. Start with AGENT_PRD.md - fill in executive summary"
echo "  2. Define identity in IDENTITY.md"
echo "  3. Document users and use cases"
echo "  4. Specify capabilities (skills, tools, memory, knowledge)"
echo "  5. Define behavior and safety"
echo "  6. Create evaluation plan"
echo "  7. Use CHECKLIST.md before handoff"
