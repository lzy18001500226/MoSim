# Agent Observability & Operations

Monitoring, tracing, debugging, and operational management of agents in production.

---

## Why is Agent Observability Hard?

```
Traditional software:
  Request → Deterministic processing → Response
  (Each step is predictable and traceable)

Agent:
  Request → Understand → Plan → [Tool calls]* → Reflect → [Retry]* → Response
                ↑                           │
                └─────── Dynamic loop ────────┘
  
  (Steps uncertain, paths uncertain, outcomes uncertain)
```

**Unique Challenges of Agent Observability:**
- Non-deterministic behavior (same input may produce different outputs)
- Dynamic execution paths (tool call chains are not fixed)
- Multi-step compound latency
- Unpredictable costs
- Complex failure modes

---

## Three Pillars of Observability

```
┌─────────────────────────────────────────────────────────────────┐
│              Agent Observability: Three Pillars                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   TRACES          METRICS           LOGS                        │
│   Tracing         Metrics           Logs                        │
│                                                                 │
│   "What happened?" "How is it doing?" "What are the details?"   │
│                                                                 │
│   - Request path   - Success rate    - Reasoning process        │
│   - Tool call chain - Latency        - Decision rationale       │
│   - Time distrib.  - Cost            - Error details            │
│   - Causality      - Quality scores  - User feedback            │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Trace Design

### Trace Structure

```
Trace: user_request_123
├── Span: understand_intent (50ms)
│   └── Attributes: intent=search, confidence=0.95
├── Span: plan_execution (30ms)
│   └── Attributes: steps=3, strategy=sequential
├── Span: execute_step_1 (200ms)
│   ├── Span: tool_call_search (180ms)
│   │   └── Attributes: tool=web_search, results=10
│   └── Span: process_results (20ms)
├── Span: execute_step_2 (500ms)
│   ├── Span: tool_call_analyze (450ms)
│   └── Span: synthesize (50ms)
├── Span: generate_response (100ms)
│   └── Attributes: tokens=250, model=gpt-4
└── Span: total (880ms)
    └── Attributes: success=true, cost=$0.015
```

### Trace Data Model

```yaml
trace:
  trace_id: string
  
  # Request info
  request:
    user_id: string
    session_id: string
    input: string
    input_tokens: int
    timestamp: datetime
    
  # Execution path
  spans:
    - span_id: string
      parent_span_id: string
      name: string
      start_time: datetime
      end_time: datetime
      attributes: map
      events: list
      status: success|error
      
  # Agent-specific
  agent_execution:
    reasoning_steps: list
    tool_calls: list
    memory_access: list
    rag_retrievals: list
    
  # Output info
  response:
    output: string
    output_tokens: int
    total_tokens: int
    model: string
    
  # Quality info
  quality:
    user_feedback: thumbs_up|thumbs_down|none
    auto_eval_score: float
    
  # Cost info
  cost:
    llm_cost: float
    tool_cost: float
    total_cost: float
```

---

## Metrics Design

### Core Metrics

| Category | Metric | Calculation | Alert Threshold |
|------|------|----------|----------|
| **Availability** | Success rate | Successful / Total requests | <95% |
| **Latency** | P50/P95/P99 | Response time distribution | P95>5s |
| **Throughput** | QPS | Requests per second | Per capacity |
| **Cost** | Cost per request | Total cost / Request count | >Budget |
| **Quality** | Satisfaction | Positive / Total feedback | <80% |

### Agent-Specific Metrics

| Metric | Definition | Significance |
|------|------|------|
| **Reasoning steps** | Avg steps per request | Efficiency indicator |
| **Tool call count** | Avg tool calls per request | Dependency level |
| **Tool failure rate** | Failed tool calls ratio | Integration health |
| **Retry rate** | Requests needing retry | Stability |
| **Timeout rate** | Timed-out requests ratio | Complexity |
| **Escalation rate** | Requests needing human | Automation level |
| **Token efficiency** | Output quality / Token usage | Cost efficiency |

### Metrics Dashboard

```yaml
dashboard:
  
  real_time:  # Real-time monitoring
    - metric: error_rate
      visualization: line_chart
      window: 5m
      alert: >5%
      
    - metric: latency_p95
      visualization: line_chart
      window: 5m
      alert: >5s
      
    - metric: active_requests
      visualization: gauge
      
  hourly:  # Hourly aggregation
    - metric: request_volume
    - metric: success_rate
    - metric: avg_cost
    - metric: tool_call_distribution
    
  daily:  # Daily aggregation
    - metric: unique_users
    - metric: satisfaction_score
    - metric: total_cost
    - metric: top_failure_reasons
```

---

## Logs Design

### Log Levels

| Level | Usage | Example |
|------|------|------|
| **DEBUG** | Development debugging | Full reasoning process |
| **INFO** | Normal operations | Request completed, tool calls |
| **WARN** | Potential issues | Retries, degradation |
| **ERROR** | Failures | Exceptions, timeouts |

### Structured Logging

```json
{
  "timestamp": "2024-01-15T10:30:00Z",
  "level": "INFO",
  "trace_id": "abc123",
  "span_id": "def456",
  
  "event": "tool_call_completed",
  
  "agent": {
    "agent_id": "customer_support_v2",
    "version": "2.3.1"
  },
  
  "tool": {
    "name": "search_knowledge_base",
    "parameters": {"query": "refund policy"},
    "latency_ms": 150,
    "status": "success",
    "result_count": 5
  },
  
  "context": {
    "user_id": "user_789",
    "session_id": "sess_012",
    "turn_number": 3
  }
}
```

### Sensitive Information Handling

| Field Type | Handling |
|----------|----------|
| User input | Sanitize or hash |
| PII | Auto-detect and redact |
| Tool parameters | Redact per config |
| Agent output | Redact or truncate |
| System Prompt | Never log |

---

## Debugging Tools

### 1. Trace Visualization

```
Request replay interface:
┌─────────────────────────────────────────────────────────────────┐
│ Trace: user_request_123                                         │
├─────────────────────────────────────────────────────────────────┤
│ [Timeline View]                                                 │
│                                                                 │
│ understand ████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░ 50ms        │
│ plan       ░░░░███░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░ 30ms        │
│ tool:search░░░░░░░████████████░░░░░░░░░░░░░░░░░░░░ 180ms       │
│ tool:analyze░░░░░░░░░░░░░░░░░████████████████████░ 450ms       │
│ respond    ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░████ 100ms       │
│                                                                 │
│ Total: 880ms | Cost: $0.015 | Tokens: 1,250                    │
└─────────────────────────────────────────────────────────────────┘
```

### 2. Reasoning Process Viewer

```
Reasoning Inspector:
┌─────────────────────────────────────────────────────────────────┐
│ Step 1: Understand                                              │
│ ────────────────────                                            │
│ User wants to know about refund policy for a specific order.    │
│ Intent: information_query (confidence: 0.95)                    │
│                                                                 │
│ Step 2: Plan                                                    │
│ ────────────────────                                            │
│ 1. Search knowledge base for refund policy                      │
│ 2. Look up the specific order                                   │
│ 3. Combine information and respond                              │
│                                                                 │
│ Step 3: Execute - Tool Call                                     │
│ ────────────────────                                            │
│ Tool: search_knowledge_base                                     │
│ Query: "refund policy"                                          │
│ Results: 5 documents (showing top 3)                            │
│   - Refund Policy Overview (score: 0.95)                        │
│   - Return Process Guide (score: 0.87)                          │
│   - ...                                                         │
│                                                                 │
│ Step 4: Synthesize & Respond                                    │
│ ────────────────────                                            │
│ [Final response shown]                                          │
└─────────────────────────────────────────────────────────────────┘
```

### 3. A/B Comparison

```
Comparison View:
┌────────────────────────────┬────────────────────────────┐
│ Version A (current)        │ Version B (candidate)      │
├────────────────────────────┼────────────────────────────┤
│ Response:                  │ Response:                  │
│ [Response A]               │ [Response B]               │
│                            │                            │
│ Steps: 3                   │ Steps: 2                   │
│ Tools: 2                   │ Tools: 1                   │
│ Latency: 880ms             │ Latency: 450ms             │
│ Cost: $0.015               │ Cost: $0.008               │
│ Quality: 4.2/5             │ Quality: 4.5/5             │
└────────────────────────────┴────────────────────────────┘
```

---

## Operations Management

### Version Management

```yaml
versioning:
  
  components:
    - name: system_prompt
      current: v2.3.1
      history: [v2.3.0, v2.2.5, ...]
      
    - name: skills
      current: v1.5.0
      
    - name: tools
      current: v3.1.0
      
  deployment:
    strategy: canary
    canary_percentage: 5
    promotion_criteria:
      - error_rate_delta: <1%
      - latency_delta: <10%
      - quality_delta: >-2%
    rollback_trigger:
      - error_rate: >10%
      - latency_p95: >10s
```

### Release Process

```
┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐
│ Develop │───►│ Staging │───►│ Canary  │───►│ Full    │
│         │    │  Test   │    │  (5%)   │    │ Release │
└─────────┘    └─────────┘    └─────────┘    └─────────┘
                   │              │              │
                   ▼              ▼              ▼
              Automated      Monitoring      Gradual
              Tests          Period (24h)    Rollout
```

### Feature Flags

```yaml
feature_flags:
  
  - name: new_reasoning_strategy
    enabled: false
    rollout_percentage: 0
    
  - name: enhanced_memory
    enabled: true
    rollout_percentage: 50
    user_segments: [beta_users]
    
  - name: multimodal_input
    enabled: true
    rollout_percentage: 100
```

### Rollback Strategy

```yaml
rollback:
  
  triggers:
    automatic:
      - condition: error_rate > 10%
        duration: 5m
      - condition: latency_p95 > 10s
        duration: 10m
        
    manual:
      - authorized_roles: [oncall, admin]
      
  process:
    - notify_oncall
    - switch_to_previous_version
    - preserve_current_state_for_debugging
    - monitor_recovery
    - post_mortem
```

---

## Alert Design

### Alert Severity Levels

| Level | Response Time | Notification | Example |
|------|----------|----------|------|
| **P0 Critical** | Immediate | Phone + SMS | Service unavailable |
| **P1 High** | 15 minutes | SMS + Slack | Error rate spike |
| **P2 Medium** | 1 hour | Slack | Latency increase |
| **P3 Low** | 1 day | Email | Cost over budget |

### Alert Rules

```yaml
alerts:
  
  - name: high_error_rate
    severity: P1
    condition: error_rate > 5%
    duration: 5m
    notification:
      - oncall_pager
      - slack_channel
      
  - name: latency_spike
    severity: P2
    condition: latency_p95 > 5s
    duration: 10m
    notification:
      - slack_channel
      
  - name: cost_anomaly
    severity: P2
    condition: hourly_cost > 2x_average
    notification:
      - slack_channel
      - email
      
  - name: quality_degradation
    severity: P2
    condition: satisfaction_score < 70%
    duration: 1h
    notification:
      - slack_channel
```

---

## Operations Specification Template

```markdown
## Operations Specification

### Monitoring Configuration

| Metric | Collection Frequency | Retention | Alert Threshold |
|------|----------|----------|----------|
| [metric] | [frequency] | [retention] | [threshold] |

### Alert Configuration

| Alert | Severity | Condition | Response |
|------|------|------|------|
| [name] | [P0-P3] | [condition] | [action] |

### Versioning Strategy

- Release frequency: [frequency]
- Canary percentage: [%]
- Observation period: [duration]
- Rollback trigger: [conditions]

### On-Call

- On-call rotation: [cycle]
- Response SLA: [time]
- Escalation path: [path]
```
