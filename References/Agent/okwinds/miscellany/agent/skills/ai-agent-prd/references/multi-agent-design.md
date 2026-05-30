# Multi-Agent Systems Design

Multi-Agent System Design Guide — how to design multi-agent collaboration when a single agent is not enough.

---

## Why Multi-Agent?

```
Single Agent Limitations:
┌─────────────────────────────────────────────────────────────────┐
│  • Limited context window, cannot process large volumes at once   │
│  • Single prompt struggles to cover multiple specialized domains  │
│  • Complex tasks require collaboration between different "roles"  │
│  • Long-running tasks require division of labor and parallelism  │
└─────────────────────────────────────────────────────────────────┘

Multi-Agent Solution:
┌─────────────────────────────────────────────────────────────────┐
│  • Specialization: each agent focuses on one domain              │
│  • Capability expansion: combine abilities of multiple agents    │
│  • Parallel processing: multiple agents work simultaneously     │
│  • Quality control: agents cross-check each other               │
└─────────────────────────────────────────────────────────────────┘
```

---

## Multi-Agent Architecture Patterns

### Pattern 1: Manager-Worker

```
                    ┌──────────────┐
                    │   Manager    │
                    │   Agent      │
                    └──────┬───────┘
                           │ Assign tasks
           ┌───────────────┼───────────────┐
           ↓               ↓               ↓
    ┌──────────┐    ┌──────────┐    ┌──────────┐
    │ Worker A │    │ Worker B │    │ Worker C │
    │ (Search) │    │ (Analyze)│    │ (Write)  │
    └──────────┘    └──────────┘    └──────────┘
           │               │               │
           └───────────────┼───────────────┘
                           ↓ Report results
                    ┌──────────────┐
                    │   Manager    │
                    │   Consolidate │
                    └──────────────┘
```

**Use Cases:**
- Complex tasks that need decomposition
- Sub-tasks can run in parallel
- Unified output is required

**PRD Specification:**
```yaml
multi_agent:
  pattern: manager_worker
  
  manager:
    name: task_coordinator
    responsibilities:
      - Understand user request
      - Decompose into sub-tasks
      - Assign to workers
      - Consolidate results
    
  workers:
    - name: research_agent
      specialty: Information retrieval and organization
      tools: [web_search, knowledge_base]
      
    - name: analysis_agent
      specialty: Data analysis and interpretation
      tools: [data_query, chart_generate]
      
    - name: writing_agent
      specialty: Content creation and editing
      tools: [text_generate, format_document]
      
  communication:
    protocol: structured_json
    max_rounds: 5
```

### Pattern 2: Pipeline

```
Input → [Agent A] → [Agent B] → [Agent C] → Output
         (Understand)   (Process)    (Output)
```

**Use Cases:**
- Tasks have clear sequential stages
- Each stage requires specialized processing
- Sequential dependencies exist

**PRD Specification:**
```yaml
multi_agent:
  pattern: pipeline
  
  stages:
    - name: intake
      agent: intent_classifier
      output: structured_intent
      
    - name: process
      agent: task_executor
      input: structured_intent
      output: raw_result
      
    - name: format
      agent: response_formatter
      input: raw_result
      output: final_response
      
  flow_control:
    on_stage_failure: retry_once_then_escalate
    timeout_per_stage: 30s
```

### Pattern 3: Debate/Consensus

```
        ┌──────────┐
        │  Topic   │
        └────┬─────┘
             │
    ┌────────┼────────┐
    ↓        ↓        ↓
┌───────┐┌───────┐┌───────┐
│Agent A││Agent B││Agent C│
│(View 1)││(View 2)││(View 3)│
└───┬───┘└───┬───┘└───┬───┘
    │        │        │
    └────────┼────────┘
             ↓
      ┌──────────────┐
      │  Moderator   │
      │  Build consensus │
      └──────────────┘
```

**Use Cases:**
- Multi-perspective analysis required
- Decisions require trade-off evaluation
- Quality requires cross-validation

**PRD Specification:**
```yaml
multi_agent:
  pattern: debate
  
  debaters:
    - name: optimist_agent
      perspective: Opportunities and benefits
      
    - name: pessimist_agent
      perspective: Risks and costs
      
    - name: pragmatist_agent
      perspective: Feasibility and implementation
      
  moderator:
    name: synthesis_agent
    responsibilities:
      - Collect perspectives from all parties
      - Identify areas of consensus and disagreement
      - Form a balanced conclusion
      
  debate_rules:
    max_rounds: 3
    response_format: structured_argument
    consensus_threshold: 2/3
```

### Pattern 4: Expert Panel

```
                    User Query
                         │
                         ↓
              ┌──────────────────┐
              │     Router       │
              └────────┬─────────┘
                       │ Identify domain
         ┌─────────────┼─────────────┐
         ↓             ↓             ↓
   ┌──────────┐  ┌──────────┐  ┌──────────┐
   │ Expert A │  │ Expert B │  │ Expert C │
   │ (Legal)  │  │(Finance) │  │  (Tech)  │
   └────┬─────┘  └────┬─────┘  └────┬─────┘
        │             │             │
        └─────────────┼─────────────┘
                      ↓
            ┌──────────────────┐
            │   Aggregator     │
            │  Aggregate expert  │
            └──────────────────┘
```

**Use Cases:**
- Problem spans multiple specialized domains
- Deep domain expertise required
- Multi-disciplinary perspectives needed

**PRD Specification:**
```yaml
multi_agent:
  pattern: expert_panel
  
  router:
    name: domain_router
    logic: |
      Based on keywords and intent,
      identify which expert domains to consult
      
  experts:
    - name: legal_expert
      domain: Legal and regulatory
      knowledge_base: legal_documents
      
    - name: financial_expert
      domain: Financial analysis
      knowledge_base: financial_docs
      
    - name: technical_expert
      domain: Technical implementation
      knowledge_base: tech_docs
      
  aggregator:
    name: response_synthesizer
    strategy: weighted_by_relevance
```

### Pattern 5: Swarm (Autonomous Collaboration)

```
┌──────────────────────────────────────────┐
│                                          │
│   Agent A ←──→ Agent B ←──→ Agent C     │
│      ↑            ↑            ↑         │
│      │            │            │         │
│      └────────────┼────────────┘         │
│                   │                      │
│              Shared Memory               │
│                                          │
└──────────────────────────────────────────┘
```

**Use Cases:**
- Highly complex, open-ended tasks
- Dynamic coordination required
- Task structure is uncertain

**PRD Specification:**
```yaml
multi_agent:
  pattern: swarm
  
  agents:
    - name: explorer
      role: Discover new information and opportunities
      
    - name: analyzer
      role: Analyze and evaluate information
      
    - name: executor
      role: Execute specific tasks
      
    - name: validator
      role: Verify and quality-check
      
  coordination:
    shared_memory: true
    message_bus: true
    self_organization: true
    
  governance:
    max_concurrent_agents: 5
    max_total_steps: 50
    human_checkpoint_every: 10_steps
```

---

## Communication Protocol Design

### Inter-Agent Message Format

```json
{
  "message_id": "uuid",
  "from_agent": "agent_name",
  "to_agent": "agent_name | broadcast",
  "message_type": "request | response | notification",
  "timestamp": "ISO8601",
  
  "content": {
    "task": "task_description",
    "context": {},
    "constraints": [],
    "expected_output": "output_spec"
  },
  
  "metadata": {
    "priority": "high | normal | low",
    "timeout": "30s",
    "retry_policy": "once | exponential | none"
  }
}
```

### Shared State Mechanism

```yaml
shared_state:
  storage: distributed_kv
  
  namespaces:
    task_state:
      owner: manager
      readers: all_workers
      
    agent_status:
      owner: each_agent
      readers: manager
      
    intermediate_results:
      owner: producer
      readers: consumers
      
  consistency: eventual
  conflict_resolution: last_write_wins
```

---

## Multi-Agent Specific Requirements

### 1. Agent Discovery and Registration

```yaml
agent_registry:
  discovery:
    method: declarative
    
  registration:
    required_fields:
      - name
      - capabilities
      - input_schema
      - output_schema
      - resource_requirements
      
  health_check:
    interval: 30s
    unhealthy_threshold: 3
```

### 2. Load Balancing

```yaml
load_balancing:
  strategy: round_robin | least_busy | capability_match
  
  agent_pools:
    - pool: general_workers
      min_instances: 2
      max_instances: 10
      scale_trigger: queue_length > 5
```

### 3. Failure Handling

```yaml
fault_tolerance:
  agent_failure:
    detection: heartbeat_timeout
    response: reassign_to_backup
    
  task_failure:
    max_retries: 3
    fallback: escalate_to_human
    
  cascade_prevention:
    circuit_breaker: true
    bulkhead_isolation: true
```

### 4. Debugging and Observability

```yaml
observability:
  tracing:
    enabled: true
    propagation: all_agent_calls
    
  logging:
    level: info
    include_message_content: true
    
  metrics:
    - agent_response_time
    - inter_agent_latency
    - task_completion_rate
    - coordination_overhead
```

---

## When to Use Multi-Agent vs Single Agent

| Factor | Single Agent | Multi-Agent |
|------|----------|----------|
| Task complexity | Simple to moderate | High complexity |
| Domain breadth | Single domain | Multiple domains |
| Processing time | Fast response | Acceptable latency |
| Quality needs | Standard | Cross-validation needed |
| Dev complexity | Low | High |
| Maintenance cost | Low | High |
| Scalability | Limited | High |

### Decision Framework

```
Can a single agent complete the task?
├── Yes → Use single agent
└── No → Does the task have clear stages?
          ├── Yes → Use Pipeline
          └── No → Is multi-perspective analysis needed?
                    ├── Yes → Use Debate/Expert Panel
                    └── No → Is parallel processing needed?
                              ├── Yes → Use Manager-Worker
                              └── No → Use Swarm
```

---

## Multi-Agent PRD Checklist

- [ ] Define each agent's role and responsibilities
- [ ] Define inter-agent communication protocol
- [ ] Define task allocation and coordination mechanism
- [ ] Define shared state management
- [ ] Define failure handling and recovery
- [ ] Define observability and debugging mechanisms
- [ ] Define resource limits and cost controls
- [ ] Define human oversight and intervention points
