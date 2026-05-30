# Agent Architecture Patterns

Common patterns for building AI agents—architectures, workflows, and design approaches.

---

## Agent Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    Agent Architecture Layers                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   USER INTERFACE        ← How users interact                    │
│         ↓                                                       │
│   ORCHESTRATION         ← How agent thinks and decides          │
│         ↓                                                       │
│   CAPABILITIES          ← What agent can do (skills, tools)     │
│         ↓                                                       │
│   KNOWLEDGE             ← What agent knows (RAG, memory)        │
│         ↓                                                       │
│   FOUNDATION            ← Base LLM and infrastructure           │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Reasoning Patterns

### Pattern 1: ReAct (Reasoning + Acting)

Agent interleaves thinking and acting.

```
┌─────────────────────────────────────────┐
│              ReAct Loop                 │
├─────────────────────────────────────────┤
│                                         │
│   Thought: "I need to find X"          │
│      ↓                                  │
│   Action: search_tool(query)           │
│      ↓                                  │
│   Observation: [results]               │
│      ↓                                  │
│   Thought: "Based on this, I should..." │
│      ↓                                  │
│   Action: ...                          │
│      ↓                                  │
│   (Repeat until done)                  │
│                                         │
└─────────────────────────────────────────┘
```

**Use when:**
- Tasks require information gathering
- Steps depend on previous results
- Transparency of reasoning is valuable

**Specification:**
```yaml
reasoning:
  pattern: react
  max_iterations: 10
  
  thought_format: |
    Thought: [reasoning about what to do next]
    Action: [tool_name(params)]
    
  termination:
    - condition: task_complete
    - condition: max_iterations_reached
    - condition: no_progress_detected
```

### Pattern 2: Plan-then-Execute

Agent creates full plan before executing.

```
┌─────────────────────────────────────────┐
│          Plan-then-Execute              │
├─────────────────────────────────────────┤
│                                         │
│   PLANNING PHASE                        │
│   ┌─────────────────────────────────┐   │
│   │ 1. Analyze task                 │   │
│   │ 2. Identify required steps      │   │
│   │ 3. Order steps                  │   │
│   │ 4. Identify dependencies        │   │
│   │ 5. Finalize plan               │   │
│   └─────────────────────────────────┘   │
│                  ↓                      │
│   EXECUTION PHASE                       │
│   ┌─────────────────────────────────┐   │
│   │ Execute step 1                  │   │
│   │ Execute step 2                  │   │
│   │ ...                             │   │
│   │ Handle deviations               │   │
│   └─────────────────────────────────┘   │
│                                         │
└─────────────────────────────────────────┘
```

**Use when:**
- Complex multi-step tasks
- User approval of plan is needed
- Execution is expensive (want to optimize)

**Specification:**
```yaml
reasoning:
  pattern: plan_then_execute
  
  planning:
    max_steps: 20
    require_user_approval: true
    replanning_triggers:
      - step_failure
      - new_information
      
  execution:
    parallel_steps: false
    checkpoint_frequency: every_step
```

### Pattern 3: Tree of Thoughts

Agent explores multiple reasoning paths.

```
┌─────────────────────────────────────────┐
│           Tree of Thoughts              │
├─────────────────────────────────────────┤
│                                         │
│              [Problem]                  │
│                  │                      │
│       ┌─────────┼─────────┐             │
│       ↓         ↓         ↓             │
│   [Path A]  [Path B]  [Path C]          │
│       │         │         │             │
│    [Eval]    [Eval]    [Eval]           │
│       │         │         │             │
│   Continue   Prune    Continue          │
│       │                   │             │
│       ↓                   ↓             │
│    [A.1]               [C.1]            │
│       │                   │             │
│     ...                 ...             │
│                                         │
└─────────────────────────────────────────┘
```

**Use when:**
- Problem requires exploration
- Multiple valid approaches exist
- Optimal solution isn't obvious

**Specification:**
```yaml
reasoning:
  pattern: tree_of_thoughts
  
  branching:
    initial_branches: 3
    evaluation_at_depth: 2
    
  pruning:
    method: score_threshold
    threshold: 0.5
    keep_top_n: 2
    
  selection:
    method: best_final_score
```

### Pattern 4: Reflexion

Agent self-critiques and improves.

```
┌─────────────────────────────────────────┐
│              Reflexion                  │
├─────────────────────────────────────────┤
│                                         │
│   1. Generate initial response          │
│              ↓                          │
│   2. Self-critique response             │
│      "What could be better?"            │
│              ↓                          │
│   3. Generate improved response         │
│              ↓                          │
│   4. Check if good enough               │
│      ├── Yes → Return                   │
│      └── No → Go to step 2              │
│                                         │
└─────────────────────────────────────────┘
```

**Use when:**
- Quality is critical
- First attempt may be insufficient
- Self-improvement is possible

**Specification:**
```yaml
reasoning:
  pattern: reflexion
  
  max_iterations: 3
  
  critique_prompt: |
    Review this response and identify:
    1. What is good
    2. What could be improved
    3. Specific suggestions
    
  quality_threshold: 0.8
  quality_evaluator: llm_judge
```

---

## Agent Types

### Type 1: Conversational Agent

Chat-focused agent for dialogue.

```yaml
agent_type: conversational

interface:
  modality: text
  turn_taking: alternating
  
conversation:
  max_turns: 100
  memory: session
  context_strategy: sliding_window
  
capabilities:
  - answer_questions
  - hold_dialogue
  - remember_context
  
behavior:
  response_style: conversational
  proactivity: reactive
```

### Type 2: Task Agent

Agent focused on completing specific tasks.

```yaml
agent_type: task

interface:
  modality: text + actions
  
task_handling:
  decomposition: automatic
  execution: tool_based
  reporting: on_completion
  
capabilities:
  - understand_task
  - plan_steps
  - execute_tools
  - report_results
  
behavior:
  response_style: task_focused
  proactivity: goal_driven
```

### Type 3: Autonomous Agent

Agent that operates with minimal supervision.

```yaml
agent_type: autonomous

interface:
  modality: background + notifications
  
autonomy:
  level: high
  human_checkpoints: critical_only
  
capabilities:
  - monitor_conditions
  - make_decisions
  - take_actions
  - report_outcomes
  
behavior:
  proactivity: fully_proactive
  intervention_triggers:
    - high_risk_action
    - uncertainty_threshold
    - scheduled_checkpoint
```

### Type 4: Copilot Agent

Agent that assists human in real-time.

```yaml
agent_type: copilot

interface:
  modality: inline_suggestions
  integration: ide / document / workflow
  
assistance:
  trigger: on_request + proactive_suggestions
  confidence_threshold: 0.7
  
capabilities:
  - suggest_completions
  - answer_questions
  - provide_context
  - automate_routine
  
behavior:
  response_style: concise
  proactivity: suggestive
  user_control: always_optional
```

### Type 5: Multi-Agent System

Multiple agents collaborating.

```yaml
agent_type: multi_agent

agents:
  - name: coordinator
    role: orchestrate_workflow
    
  - name: researcher
    role: gather_information
    
  - name: writer
    role: produce_content
    
  - name: reviewer
    role: quality_check
    
coordination:
  pattern: hierarchical
  communication: message_passing
  conflict_resolution: coordinator_decides
```

---

## Workflow Patterns

### Pattern 1: Sequential Pipeline

Steps execute one after another.

```
Input → Step 1 → Step 2 → Step 3 → Output
```

**Use when:**
- Each step depends on previous
- Order is fixed
- Simple linear process

### Pattern 2: Branching Workflow

Path depends on conditions.

```
                ┌→ Path A → 
Input → Check ──┼→ Path B → ──→ Merge → Output
                └→ Path C →
```

**Use when:**
- Different scenarios need different handling
- Routing based on input type or content

### Pattern 3: Parallel Workflow

Steps execute simultaneously.

```
        ┌→ Step A ─┐
Input ──┼→ Step B ─┼──→ Combine → Output
        └→ Step C ─┘
```

**Use when:**
- Steps are independent
- Latency reduction is important
- Aggregating multiple sources

### Pattern 4: Iterative Workflow

Loop until condition met.

```
Input → Process → Check ──→ Done? ──→ Output
            ↑                 │
            └──── No ─────────┘
```

**Use when:**
- Quality iteration needed
- Convergence to solution
- Refinement process

### Pattern 5: Human-in-the-Loop

Human approval at checkpoints.

```
Auto → Auto → [Human Check] → Auto → [Human Check] → Output
```

**Use when:**
- Critical decisions
- High-risk actions
- Compliance requirements

---

## Orchestration Patterns

### Pattern 1: Router

Route to specialized handlers.

```yaml
orchestration:
  pattern: router
  
  routes:
    - condition: "intent == 'search'"
      handler: search_agent
      
    - condition: "intent == 'create'"
      handler: creation_agent
      
    - condition: "default"
      handler: general_agent
```

### Pattern 2: Chain

Pass through sequence of processors.

```yaml
orchestration:
  pattern: chain
  
  steps:
    - name: understand
      processor: intent_classifier
      
    - name: enrich
      processor: context_enhancer
      
    - name: execute
      processor: task_executor
      
    - name: format
      processor: response_formatter
```

### Pattern 3: Supervisor

Manager agent coordinates workers.

```yaml
orchestration:
  pattern: supervisor
  
  supervisor:
    role: coordinate_and_decide
    
  workers:
    - name: researcher
      specialty: information_gathering
      
    - name: analyst
      specialty: data_analysis
      
    - name: writer
      specialty: content_creation
      
  delegation:
    method: supervisor_assigns
```

### Pattern 4: Consensus

Multiple agents must agree.

```yaml
orchestration:
  pattern: consensus
  
  agents:
    - agent_a
    - agent_b
    - agent_c
    
  consensus:
    method: majority_vote
    minimum_agreement: 2/3
    tiebreaker: agent_a
```

---

## Integration Patterns

### Pattern 1: API-First

Agent exposes API for integration.

```yaml
integration:
  pattern: api
  
  endpoints:
    - path: /chat
      method: POST
      streaming: true
      
    - path: /task
      method: POST
      async: true
```

### Pattern 2: Event-Driven

Agent responds to events.

```yaml
integration:
  pattern: event_driven
  
  event_sources:
    - type: webhook
      events: [order_created, user_registered]
      
    - type: queue
      source: task_queue
      
  event_handling:
    processing: async
    acknowledgment: after_processing
```

### Pattern 3: Embedded

Agent embedded in application.

```yaml
integration:
  pattern: embedded
  
  host_application: ide
  
  integration_points:
    - trigger: text_selection
      action: offer_suggestions
      
    - trigger: command
      action: execute_task
```

---

## Choosing the Right Pattern

| Requirement | Recommended Pattern |
|-------------|---------------------|
| Simple Q&A | Conversational + ReAct |
| Complex tasks | Task Agent + Plan-then-Execute |
| Real-time assistance | Copilot + Suggestions |
| High-stakes decisions | Human-in-the-Loop |
| Information synthesis | Multi-Agent + Parallel |
| Quality-critical output | Reflexion |
| Exploratory problems | Tree of Thoughts |

### Decision Framework

```
Is real-time interaction needed?
├── Yes → Copilot or Conversational
└── No → Is task well-defined?
          ├── Yes → Task Agent
          └── No → Is exploration needed?
                    ├── Yes → Tree of Thoughts
                    └── No → Is quality critical?
                              ├── Yes → Reflexion
                              └── No → ReAct
```
