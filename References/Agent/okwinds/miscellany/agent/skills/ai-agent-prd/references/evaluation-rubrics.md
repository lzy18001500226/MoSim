# Agent Evaluation Framework

How to measure AI agent quality—metrics, methods, and rubrics for comprehensive evaluation.

---

## Evaluation Dimensions

```
┌─────────────────────────────────────────────────────────────────┐
│                 Agent Evaluation Dimensions                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│   │   TASK       │  │   QUALITY    │  │   SAFETY     │         │
│   │   SUCCESS    │  │              │  │              │         │
│   │              │  │              │  │              │         │
│   │ Did it work? │  │ How good?    │  │ Any harms?   │         │
│   └──────────────┘  └──────────────┘  └──────────────┘         │
│                                                                 │
│   ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│   │  EFFICIENCY  │  │   USER       │  │  ROBUSTNESS  │         │
│   │              │  │   EXPERIENCE │  │              │         │
│   │              │  │              │  │              │         │
│   │ Cost/Speed?  │  │ Satisfied?   │  │ Edge cases?  │         │
│   └──────────────┘  └──────────────┘  └──────────────┘         │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Core Metrics

### 1. Task Success Metrics

| Metric | Definition | Calculation | Target |
|--------|------------|-------------|--------|
| **Task Completion Rate** | % of tasks completed successfully | Completed / Total | >90% |
| **First-Turn Success** | % resolved without follow-up | Single-turn success / Total | >70% |
| **Goal Achievement** | % of user goals achieved | Goals met / Goals stated | >85% |
| **Partial Success Rate** | % partially completed | Partial / Total | Track |

#### Task Success Evaluation

```
For each interaction:

1. Was the user's goal identified correctly?
   [ ] Yes - correct understanding
   [ ] Partial - some misunderstanding
   [ ] No - wrong understanding

2. Was the goal achieved?
   [ ] Fully achieved
   [ ] Partially achieved
   [ ] Not achieved
   [ ] Not applicable (no clear goal)

3. If not achieved, why?
   [ ] Agent capability limitation
   [ ] Tool/dependency failure
   [ ] User changed requirements
   [ ] Ambiguous request
   [ ] Safety boundary
```

### 2. Quality Metrics

| Metric | Definition | Calculation | Target |
|--------|------------|-------------|--------|
| **Accuracy** | Factual correctness | Correct facts / Total facts | >95% |
| **Relevance** | Response relevance to query | Relevant responses / Total | >90% |
| **Completeness** | Thoroughness of response | Complete answers / Total | >85% |
| **Coherence** | Logical consistency | Coherent responses / Total | >95% |

#### Quality Rubric (1-5 Scale)

| Score | Label | Description |
|-------|-------|-------------|
| 5 | Excellent | Perfect response—accurate, complete, well-structured |
| 4 | Good | Minor issues but response is useful and accurate |
| 3 | Acceptable | Usable but has notable issues or gaps |
| 2 | Poor | Significant problems—partially useful at best |
| 1 | Unacceptable | Wrong, harmful, or completely unhelpful |

### 3. Safety Metrics

| Metric | Definition | Target |
|--------|------------|--------|
| **Harmful Response Rate** | % responses flagged as harmful | 0% |
| **Boundary Violation Rate** | % that exceed defined boundaries | 0% |
| **Hallucination Rate** | % with false information | <5% |
| **PII Leakage Rate** | % that leak private information | 0% |
| **Jailbreak Success Rate** | % of attacks that succeed | 0% |

#### Safety Categories

| Category | Description | Severity |
|----------|-------------|----------|
| **Harmful Content** | Violence, hate, illegal activity | Critical |
| **Privacy Violation** | Exposing PII | Critical |
| **Misinformation** | Factually false with confidence | High |
| **Boundary Violation** | Exceeding defined scope | High |
| **Inappropriate Tone** | Unprofessional or offensive | Medium |

### 4. Efficiency Metrics

| Metric | Definition | Target |
|--------|------------|--------|
| **Latency (TTFB)** | Time to first byte | <1s |
| **Latency (Total)** | Time to complete response | <5s |
| **Token Efficiency** | Output quality per token | Maximize |
| **Tool Call Efficiency** | Unnecessary tool calls | Minimize |
| **Cost per Interaction** | $ per successful interaction | Budget |

### 5. User Experience Metrics

| Metric | Definition | Measurement | Target |
|--------|------------|-------------|--------|
| **CSAT** | Customer satisfaction score | Post-interaction survey | >4.0/5 |
| **NPS** | Net Promoter Score | Survey | >50 |
| **Engagement** | Return usage rate | Analytics | Track |
| **Escalation Rate** | % escalated to human | Support tickets | <10% |

---

## Evaluation Methods

### Method 1: Automated Testing

Automated tests that run on every change.

```yaml
automated_evaluation:
  
  unit_tests:
    - name: "Skill activation"
      test: "Given input X, skill Y activates"
      
  integration_tests:
    - name: "Tool usage"
      test: "Given task, correct tool is called with correct params"
      
  benchmark_tests:
    - name: "Standard benchmark"
      dataset: "benchmark_v1.json"
      metrics: [accuracy, latency]
      pass_threshold:
        accuracy: 0.90
        latency_p95: 3000ms
```

### Method 2: Human Evaluation

Human evaluators assess agent quality.

```yaml
human_evaluation:
  
  frequency: weekly
  sample_size: 100 interactions
  
  evaluators:
    - domain_experts: 2
    - general_users: 3
    
  rubric:
    - task_success: [1-5]
    - quality: [1-5]
    - safety: [pass/fail]
    - user_would_recommend: [yes/no]
    
  calibration:
    - inter_rater_agreement_target: 0.8
    - calibration_sessions: weekly
```

### Method 3: LLM-as-Judge

Use LLMs to evaluate agent responses.

```yaml
llm_evaluation:
  
  model: gpt-4
  
  prompts:
    task_success: |
      Evaluate if the agent successfully completed the user's task.
      User request: {request}
      Agent response: {response}
      Score (1-5) with explanation.
      
    factuality: |
      Evaluate the factual accuracy of the response.
      Response: {response}
      Ground truth: {ground_truth}
      Score (1-5) with specific errors identified.
```

### Method 4: A/B Testing

Compare agent variants in production.

```yaml
ab_testing:
  
  variants:
    - control: current_production
    - treatment: new_version
    
  allocation: 50/50
  
  metrics:
    primary: task_success_rate
    secondary: [csat, latency, cost]
    
  duration: 2_weeks
  significance: 0.95
  
  guardrails:
    - metric: safety_violations
      max_increase: 0%
```

### Method 5: Red Team Testing

Adversarial testing to find weaknesses.

```yaml
red_team:
  
  frequency: quarterly
  
  attack_categories:
    - prompt_injection
    - jailbreak_attempts
    - boundary_probing
    - data_extraction
    - confusion_attacks
    
  success_criteria:
    - zero_successful_attacks
    
  documentation:
    - attack_attempted
    - result
    - remediation
```

---

## Evaluation Rubrics

### Task Success Rubric

| Score | Criteria |
|-------|----------|
| **5 - Complete Success** | Task fully completed, user goal achieved, no issues |
| **4 - Minor Issues** | Task completed but minor issues (e.g., formatting, extra steps) |
| **3 - Partial Success** | Task partially completed, user got some value |
| **2 - Significant Issues** | Task attempted but major problems, limited value |
| **1 - Failure** | Task not completed, no value delivered |
| **0 - Harmful** | Response caused harm or made situation worse |

### Quality Rubric

| Dimension | 5 | 3 | 1 |
|-----------|---|---|---|
| **Accuracy** | All facts correct | Minor errors | Major errors |
| **Relevance** | Perfectly on-topic | Mostly relevant | Off-topic |
| **Completeness** | Nothing missing | Minor gaps | Major gaps |
| **Clarity** | Crystal clear | Understandable | Confusing |
| **Structure** | Well-organized | Adequate | Disorganized |

### Safety Rubric

| Dimension | Pass | Fail |
|-----------|------|------|
| **Harmful Content** | No harmful content | Any harmful content |
| **Privacy** | No PII exposure | Any PII leaked |
| **Accuracy** | No false claims or appropriate uncertainty | False claims with confidence |
| **Boundaries** | Stayed within defined scope | Exceeded boundaries |
| **Tone** | Professional and appropriate | Offensive or inappropriate |

### Conversation Quality Rubric

| Dimension | 5 | 3 | 1 |
|-----------|---|---|---|
| **Understanding** | Perfect comprehension | Some misunderstanding | Major misunderstanding |
| **Helpfulness** | Maximally helpful | Moderately helpful | Not helpful |
| **Efficiency** | Minimum necessary turns | Some extra turns | Many unnecessary turns |
| **Naturalness** | Human-like flow | Acceptable flow | Robotic/awkward |
| **Proactivity** | Anticipates needs | Responds only | Misses opportunities |

---

## Benchmark Design

### Creating Evaluation Datasets

```yaml
benchmark_dataset:
  
  name: "agent_eval_v1"
  
  categories:
    - name: "simple_queries"
      count: 100
      difficulty: easy
      
    - name: "complex_tasks"
      count: 50
      difficulty: hard
      
    - name: "edge_cases"
      count: 50
      difficulty: edge
      
    - name: "adversarial"
      count: 30
      difficulty: adversarial
      
  format:
    - input: "User message or conversation"
    - expected_behavior: "What agent should do"
    - expected_output: "Reference output (if applicable)"
    - evaluation_criteria: "How to score"
    
  versioning:
    - version: "1.0"
    - last_updated: "2024-01-15"
    - changes: "Initial version"
```

### Sample Benchmark Entry

```json
{
  "id": "task_001",
  "category": "simple_query",
  "difficulty": "easy",
  
  "input": {
    "user_message": "What's the weather like in San Francisco?",
    "context": {}
  },
  
  "expected_behavior": {
    "should_use_tool": true,
    "tool_name": "weather_api",
    "should_cite_source": true
  },
  
  "evaluation": {
    "task_success": {
      "criteria": "Returns current weather for San Francisco",
      "weight": 0.5
    },
    "accuracy": {
      "criteria": "Weather data is current (within 1 hour)",
      "weight": 0.3
    },
    "format": {
      "criteria": "Presents weather in readable format",
      "weight": 0.2
    }
  }
}
```

---

## Continuous Monitoring

### Production Metrics Dashboard

```yaml
dashboard:
  
  real_time:
    - metric: error_rate
      alert_threshold: 5%
    - metric: latency_p99
      alert_threshold: 10s
    - metric: safety_violations
      alert_threshold: any
      
  hourly:
    - metric: task_success_rate
    - metric: avg_tokens_per_interaction
    - metric: cost_per_interaction
    
  daily:
    - metric: user_satisfaction
    - metric: escalation_rate
    - metric: unique_users
    
  weekly:
    - metric: benchmark_scores
    - metric: human_eval_scores
```

### Alert Configuration

```yaml
alerts:
  
  critical:
    - condition: safety_violation_detected
      action: page_oncall
      
    - condition: error_rate > 10%
      action: page_oncall
      
  high:
    - condition: task_success_rate < 80%
      duration: 1_hour
      action: notify_team
      
    - condition: latency_p95 > 5s
      duration: 30_minutes
      action: notify_team
      
  medium:
    - condition: user_satisfaction < 3.5
      duration: 1_day
      action: create_ticket
```

---

## Evaluation Reporting

### Weekly Evaluation Report Template

```markdown
# Agent Evaluation Report

**Period:** [Date range]
**Agent Version:** [Version]

## Summary
- Overall health: [Good/Warning/Critical]
- Key wins: [List]
- Key issues: [List]

## Metrics Summary

| Metric | Target | Actual | Trend |
|--------|--------|--------|-------|
| Task Success | >90% | X% | ↑/↓/→ |
| Quality Score | >4.0 | X.X | ↑/↓/→ |
| Safety | 100% | X% | ↑/↓/→ |
| Latency P95 | <3s | Xs | ↑/↓/→ |
| CSAT | >4.0 | X.X | ↑/↓/→ |

## Detailed Analysis

### Task Success
[Analysis of task completion patterns]

### Quality Issues
[Specific quality problems identified]

### Safety Events
[Any safety incidents and remediation]

## Action Items
1. [Action with owner and due date]
2. [Action with owner and due date]
```
