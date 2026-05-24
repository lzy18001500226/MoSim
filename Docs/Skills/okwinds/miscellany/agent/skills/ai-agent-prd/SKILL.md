---
name: ai-agent-prd
version: 0.1.1
description: "Write comprehensive PRDs for AI Agent products—covering agent identity, capability architecture (skills, tools, memory, RAG, workflows), behavior specifications, safety guardrails, and evaluation frameworks. Use when: designing conversational agents, autonomous agents, copilots, multi-agent systems, or any LLM-powered agentic application. Triggers: 'AI agent PRD', 'agent product requirements', 'design AI agent', 'agent capability spec', 'LLM agent requirements', '智能体PRD', '智能体需求文档', '对话机器人PRD', '多智能体系统需求'. Anti-triggers: '传统PRD（非智能体）', '只润色提示词/只写Prompt', '只写用户故事/验收标准但不涉及工具调用、记忆或RAG'."
license: MIT
compatibility: "Works with any agent framework. Skeleton generator requires bash (macOS/Linux); Windows via WSL/Git Bash."
metadata:
  author: "肆〇柒/ForOhZen"
  version: 0.1.1
  category: product-management
  tags: "prd, ai-agent, llm, skills, tools, rag, workflow, memory"
---

# AI Agent PRD Guide

## Overview

Write PRDs for AI Agent products that define not just **what the agent does**, but **how it thinks, decides, and acts**.

### Relationship with Other Skills

This skill **extends** `prd-writing-guide` for AI Agent products specifically. You should:
- Apply `prd-writing-guide`'s **Seven Lenses** to each agent capability
- Follow `prd-writing-guide`'s **Writing Style Guide** for requirement clarity
- Use `prd-writing-guide`'s **Developer Test** as your quality bar

**Handoff:** The Agent PRD this skill produces feeds into `prd-to-engineering-spec` for technical design. That skill includes an Agent-specific validation branch for converting agent capabilities into engineering specs.

```
Traditional PRD:  Input → Deterministic Logic → Output
Agent PRD:        Goal → Perceive → Think → Decide → Act → Learn
                          ↑                           │
                          └───────── Feedback ────────┘

You're not defining a function. You're defining a cognitive architecture.
```

### Quality Test

Can your engineering team answer these without asking you?
- What is the agent's purpose and identity?
- What capabilities (skills/tools) does it have?
- How does it decide what to do?
- What can it NOT do? (boundaries)
- When should humans intervene?
- How do we know if it's working well?

## Quick Start

1. Generate a document skeleton:

   ```bash
   bash scripts/generate_agent_prd_skeleton.sh ./docs/agent-prd "Customer Support Agent"
   ```

2. Fill in using templates from references
3. Validate completeness with checklist

**Note:** The skeleton generator writes a set of `.md` files into your output directory. Use a new/empty folder to avoid accidental overwrites.

---

## Workflow

```
Phase 1: Agent Identity ──────► Who is the agent? What's its purpose?
         ↓
Phase 2: Capability Architecture ──► Skills, Tools, Memory, RAG, Workflows
         ↓
Phase 3: Behavior & System Prompt ─► How does it think? What's its DNA?
         ↓
Phase 4: Conversation Design ────► Golden conversations, example behaviors
         ↓
Phase 5: Safety & Guardrails ────► What can't it do? Human oversight?
         ↓
Phase 6: Evaluation Framework ───► How do we measure success?
         ↓
Phase 7: Operational Model ──────► Cost, scaling, iteration
```

---

## Phase 1: Agent Identity

**Goal:** Define who the agent is and its relationship with users.

### Key Elements

| Element | Questions to Answer |
|---------|---------------------|
| **Persona** | Name, role, personality, expertise domain |
| **Mission** | Why does this agent exist? |
| **Boundaries** | What it IS vs what it is NOT |
| **User Relationship** | Copilot, Autopilot, Peer, Expert, or Executor? |

### User-Agent Relationship Models

| Model | Description | Example |
|-------|-------------|---------|
| **Copilot** | Human leads, agent assists | Code completion |
| **Autopilot** | Agent leads, human monitors | Customer support |
| **Peer** | Equal collaboration | Brainstorming |
| **Expert** | Agent advises, human decides | Medical advisor |
| **Executor** | Human commands, agent executes | Task automation |

---

## Phase 2: Capability Architecture

**Goal:** Define the building blocks that enable agent capabilities.

### Capability Stack

```
┌─────────────────────────────────────────────────────────────────┐
│   SKILLS          TOOLS           WORKFLOWS                     │
│   (What it        (External       (Multi-step                   │
│    can do)         actions)        processes)                   │
│         └──────────────┼──────────────┘                         │
│                        ↓                                        │
│              AGENT CORE (Reasoning, Planning)                   │
│                        ↓                                        │
│         ┌──────────────┼──────────────┐                         │
│      MEMORY          RAG          CONTEXT                       │
│   (State/History) (Knowledge)  (Awareness)                      │
└─────────────────────────────────────────────────────────────────┘
```

### 2.1 Skills

Reusable capability modules. See [skills-specification.md](references/skills-specification.md).

**Per skill, document:**
- Purpose & trigger conditions
- Input/output specification
- Process logic
- Examples & boundaries

### 2.2 Tools

External actions the agent can invoke. See [tools-specification.md](references/tools-specification.md).

**Per tool, document:**
- Interface definition (JSON schema)
- Execution details (endpoint, auth, timeout)
- Response handling
- Safety requirements (confirmation, audit)

### 2.3 Memory

Stateful, context-aware behavior. See [memory-patterns.md](references/memory-patterns.md).

| Type | Scope | Example |
|------|-------|---------|
| **Working** | Current request | Context window |
| **Session** | Current session | Conversation history |
| **Long-term** | Cross-session | User preferences |

### 2.4 Knowledge (RAG)

Knowledge grounding via retrieval. See [memory-patterns.md](references/memory-patterns.md) for architecture patterns.

**Per knowledge source, document:**

| Attribute | Specify |
|-----------|---------|
| **Source** | What data source? (docs, DB, API, web) |
| **Format** | Document types, data structure |
| **Volume** | How much data? Growth rate? |
| **Freshness** | Update frequency? Acceptable staleness? |
| **Authority** | Is this authoritative? What if conflicting sources? |

**Retrieval configuration:**
- Chunking strategy (semantic, fixed-size, hybrid) and chunk size rationale
- Embedding model and dimension
- Retrieval method (dense, sparse, hybrid) and top-k range
- Re-ranking strategy (if any)
- Quality threshold (minimum similarity score for inclusion)

**Knowledge gap handling:**
- How does the agent detect it doesn't know something?
- Response when knowledge is insufficient (admit? search? escalate?)
- Citation requirements (when must it cite? format? inline or footnote?)

**Knowledge conflict resolution:**
- When multiple sources disagree, which takes priority?
- Should the agent present conflicting views or choose one?

### 2.5 Workflows

Multi-step orchestrated processes. Document:
- Trigger and steps with success criteria
- Human checkpoints
- Timeout and cancellation handling

---

## Phase 3: Behavior & System Prompt

**Goal:** Define how the agent thinks, decides, communicates—and encode it into a System Prompt specification.

### Reasoning Strategies

| Strategy | Description | Use When |
|----------|-------------|----------|
| **ReAct** | Think → Act → Observe → Repeat | Most tasks |
| **Plan-then-Execute** | Full plan upfront → Execute | Complex multi-step |
| **Tree of Thought** | Explore multiple paths | Exploration needed |
| **Reflexion** | Self-critique and improve | Quality-critical |

See [agent-patterns.md](references/agent-patterns.md) for detailed patterns.

### Decision Framework

Define priority order for agent decisions:
1. Safety first
2. User intent
3. Efficiency
4. Quality

### Conversation Design

| Aspect | Define |
|--------|--------|
| **Voice & Tone** | Persona, formality, verbosity |
| **Response Patterns** | By scenario (simple, complex, error, out-of-scope) |
| **Multi-turn** | Context retention, topic switching, reference resolution |

### System Prompt Specification ⭐ Core Deliverable

The System Prompt is the agent's DNA. The PRD must produce a **System Prompt Design Spec** (not the final prompt text, but its design intent). See [system-prompt-design.md](references/system-prompt-design.md).

**Required sections in the System Prompt Spec:**

| Section | Content | Example |
|---------|---------|---------|
| **Identity Declaration** | Who the agent is, role, personality | "You are Aria, a senior financial advisor..." |
| **Capability Declaration** | What tools/skills are available, when to use each | "You have access to: search_docs, calculate..." |
| **Behavioral Instructions** | How to reason, when to ask vs act, output style | "Always explain your reasoning before acting..." |
| **Constraint Boundaries** | What the agent must never do | "Never provide medical diagnoses..." |
| **Output Format Rules** | Response structure, length, formatting | "Use bullet points for lists of 3+..." |
| **Escalation Rules** | When and how to hand off to humans | "If user mentions legal action, transfer to..." |

---

## Phase 4: Example Conversations (Golden Conversations)

**Goal:** Define concrete conversation examples that serve as both behavioral spec and acceptance criteria.

See [conversation-design.md](references/conversation-design.md) for detailed methodology.

### Why Golden Conversations Matter

For Agent products, example conversations are the **most precise behavioral specification**. They are:
- Acceptance criteria (does the agent behave like this example?)
- Training signals (few-shot examples in the system prompt)
- Evaluation dataset (automated quality testing)
- Stakeholder alignment tool (shows exactly what "good" looks like)

### Coverage Requirements

Design golden conversations for each of these scenario types:

| Scenario Type | Count | Purpose |
|---------------|-------|---------|
| **Happy path** | 2-3 per use case | Shows ideal agent behavior |
| **Edge cases** | 1-2 per use case | Shows boundary handling |
| **Safety boundaries** | 3-5 total | Shows refusal/escalation |
| **Multi-turn complex** | 2-3 total | Shows context management |
| **Context switching** | 1-2 total | Shows topic change handling |
| **Error recovery** | 2-3 total | Shows tool failure handling |
| **Out-of-scope** | 2-3 total | Shows graceful boundary enforcement |

### Conversation Annotation Format

Each golden conversation should include:

```markdown
## Conversation: [Scenario Name]
**Type:** [happy-path | edge-case | safety | multi-turn | error]
**Tests:** [Which capabilities/rules this validates]

### Dialogue
User: [input]
Agent: [expected response]
// Annotation: [Why this response is correct. What rules apply.]

User: [follow-up]
Agent: [expected response]
// Annotation: [Key behavior being demonstrated]

### Unacceptable Alternatives
- Agent should NOT: [describe bad behavior]
- Agent should NOT: [describe bad behavior]

### Evaluation Criteria
- [ ] [Checkable criterion 1]
- [ ] [Checkable criterion 2]
```

---

## Phase 5: Safety & Guardrails

**Goal:** Define boundaries, controls, and human oversight.

See [safety-checklist.md](references/safety-checklist.md) for comprehensive checklist.

### 5.1 Capability Boundaries

| Category | Document |
|----------|----------|
| **CAN DO** | Authorized actions with conditions |
| **CANNOT DO** | Prohibited actions with response |
| **MUST ASK** | Actions requiring confirmation |

### 5.2 Human-in-the-Loop

Define when humans must intervene:
- Approval triggers and workflow
- Escalation paths
- Override capabilities

### 5.3 Guardrails

**Input Guardrails:**
- Prompt injection protection
- Harmful request detection
- Input validation

**Output Guardrails:**
- Harmful content filtering
- PII leakage prevention
- Hallucination detection

### 5.4 Error Handling

| Error Type | Document |
|------------|----------|
| Tool failure | Detection, message, recovery |
| Knowledge gap | Detection, message, fallback |
| Reasoning failure | Detection, restart/escalate |

---

## Phase 6: Evaluation Framework

**Goal:** Define how to measure agent quality and success.

See [evaluation-rubrics.md](references/evaluation-rubrics.md) for detailed rubrics.

### Core Metrics

| Dimension | Metrics |
|-----------|---------|
| **Task Success** | Completion rate, first-turn resolution |
| **Quality** | Accuracy, relevance, completeness |
| **Safety** | Harmful response rate, boundary violations |
| **Efficiency** | Latency, token usage, cost |
| **User Experience** | CSAT, NPS, escalation rate |

### Evaluation Methods

| Method | Purpose | Frequency |
|--------|---------|-----------|
| **Automated Testing** | Regression, benchmarks | Every change |
| **Human Evaluation** | Quality assessment | Weekly |
| **LLM-as-Judge** | Scalable quality scoring | Continuous |
| **Red Team Testing** | Adversarial testing | Quarterly |
| **A/B Testing** | Compare variants | As needed |

---

## Phase 7: Operational Model

### 7.1 Cost Model

| Component | Document |
|-----------|----------|
| Per-request costs | LLM tokens, embeddings, tool calls |
| Projected costs | By scale (launch, 6 months, 1 year) |
| Cost controls | Budgets, alerts, throttling |

### 7.2 Scaling & Iteration

- Scaling strategy (horizontal, rate limiting, caching)
- Feedback collection mechanisms
- Continuous improvement cycle
- Version management

---

## Output Structure

```
agent-prd/
├── AGENT_PRD.md          # Main document
├── IDENTITY.md           # Agent persona & boundaries
├── USE_CASES.md          # Users and use cases
├── SKILLS.md             # Skills specification
├── TOOLS.md              # Tools specification
├── MEMORY.md             # Memory architecture
├── KNOWLEDGE.md          # RAG configuration
├── WORKFLOWS.md          # Workflow definitions
├── BEHAVIOR.md           # Reasoning & conversation
├── SYSTEM_PROMPT_SPEC.md # System prompt design specification ⭐
├── CONVERSATIONS.md      # Golden conversations ⭐
├── SAFETY.md             # Guardrails
├── EVALUATION.md         # Metrics & testing
├── EXAMPLES.md           # Additional example interactions
└── CHECKLIST.md          # Completion checklist
```

---

## Resources

**Scripts:**
- `scripts/generate_agent_prd_skeleton.sh` - Generate PRD structure

**Core References:**
- `references/agent-prd-template.md` - Complete PRD template
- `references/skills-specification.md` - Skill definition guide
- `references/tools-specification.md` - Tool definition guide
- `references/memory-patterns.md` - Memory architecture patterns
- `references/agent-patterns.md` - Reasoning & architecture patterns
- `references/conversation-design.md` - Golden conversation methodology ⭐
- `references/worked-example.md` - **End-to-end worked example** (HelpBot agent) ⭐

**Safety & Evaluation:**
- `references/safety-checklist.md` - Safety requirements
- `references/evaluation-rubrics.md` - Evaluation frameworks

**Advanced Topics:**
- `references/multi-agent-design.md` - Multi-agent system design
- `references/system-prompt-design.md` - System prompt engineering
- `references/multimodal-design.md` - Multi-modal agent design
- `references/observability-operations.md` - Monitoring & operations
- `references/protocols-standards.md` - MCP, protocols, standards
- `references/domain-specific-design.md` - Domain-specific guidance

---

## Extensibility & Future-Proofing

This skill is designed to evolve with Agent technology:

| Current | Future-Ready |
|---------|--------------|
| Text I/O | Multimodal (vision, audio, video) |
| Single Agent | Multi-Agent orchestration |
| Custom tools | Protocol standards (MCP, Agent Protocol) |
| Basic metrics | Full observability stack |
| Generic | Domain-specific extensions |

**Adding new capabilities:**
1. Add reference file in `references/`
2. Update SKILL.md Resources section
3. Extend PRD template if needed

---

## Summary: Agent PRD Principles

```
┌─────────────────────────────────────────────────────────────────┐
│  1. DEFINE IDENTITY - Who is this agent? Not just features.    │
│  2. SPECIFY CAPABILITIES - Skills, Tools, Memory, Knowledge.   │
│  3. DESIGN THE PROMPT - System Prompt is the agent's DNA.      │
│  4. SHOW, DON'T TELL - Golden conversations are the spec.      │
│  5. BOUND THE BEHAVIOR - What it CAN'T do matters equally.     │
│  6. EVALUATE CONTINUOUSLY - Define metrics before building.    │
│  7. HUMANS IN THE LOOP - Know when to escalate, always.        │
└─────────────────────────────────────────────────────────────────┘
```

The goal is to **architect cognition**—define how an intelligent system should think, decide, and act within safe boundaries.
