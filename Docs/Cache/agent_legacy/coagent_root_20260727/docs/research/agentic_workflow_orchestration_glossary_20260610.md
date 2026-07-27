# Agentic Workflow Orchestration Glossary

> Research glossary for discussing workflow, DAG, durable execution, and
> agent-runtime architecture in MoSim/CoAgent. This is not an execution
> workflow and does not grant runtime, dispatch, or documentation authority.

Status: research glossary, 2026-06-10 CST.

Scope:

- Explain the terminology family around meta workflow, dynamic workflow,
  dynamic DAG, agentic workflow, LangGraph-style durable execution, DAG
  validators, and related paradigms.
- Map the terms to MoSim/CoAgent so future discussions do not mix governance,
  execution, validation, and evidence layers.
- Keep this as research context until promoted through a workflow/schema/checker
  patch.

## 1. Field Boundary

This topic is not one narrow discipline. It sits at the intersection of:

```text
workflow orchestration
business process modeling
graph theory and DAG scheduling
distributed systems and durable execution
data and ML pipeline orchestration
agentic AI runtimes
LLMOps / AgentOps / observability
policy-as-code and contract validation
```

A practical name for the combined field is:

```text
Agentic Workflow Orchestration
```

or, for engineering implementation:

```text
Agent Runtime Engineering
```

In MoSim terms, this is the control-plane knowledge needed to make Codex App
visible threads, packets, checkers, skills, MCP tools, and human review work
as one reliable operating system.

## 2. The Big Separation

Keep these four layers separate:

| Layer | Question It Answers | MoSim Examples |
|---|---|---|
| Meta workflow | How should this class of work be governed? | dispatch rules, dead-thread recovery, document promotion, R2/R3 failover |
| Dynamic workflow / dynamic DAG | How is this specific task instance running now? | one MWORKS/ROS2/UE task graph, current dispatch ticket, current failover branch |
| State machine | What state is this node/thread/window in? | idle, dispatched, lease missing, approval pending, returned, blocked |
| Evidence / event log | What happened and what proves it? | packet, runtime lease, checker output, screenshot manifest, result file |

The common failure is to put all four into prose. The reliable pattern is:

```text
meta workflow -> workflow/checker/schema/template
dynamic workflow -> ticket/DAG/task graph
state machine -> enum and transition rule
evidence -> packet/event/report
```

## 3. Core Workflow Terms

### Workflow

A workflow is an ordered or conditional set of steps. Use it for repeatable
task procedures, review processes, dispatch processes, and simulation evidence
processes. Do not use a plain workflow as a dumping ground for every incident
correction.

### Meta Workflow

A meta workflow is a workflow for maintaining or controlling other workflows.
It defines how tasks are classified, how dispatch is allowed, how failures are
escalated, how rules are promoted from discussion to canonical docs, and how
checkers/schemas/templates are updated.

MoSim examples:

```text
CoAgentOps patrol workflow
design-intake promotion workflow
dead-thread recovery ladder
capability-resolution governance
entry-document slimming process
```

Strength:

```text
good at long-term governance and preventing repeated mistakes
```

Risk:

```text
can become prose-heavy and slow execution if not converted into checkers,
schemas, templates, or concise role views
```

### Dynamic Workflow

A dynamic workflow is an execution workflow that can change while it runs. It
can add nodes, skip nodes, branch on evidence, insert human review, fail over
from R1 to R2, or stop and return a blocker.

MoSim example:

```text
dispatch to ROS2 R1
  -> immediate readback
  -> runtime lease missing
  -> classify dispatch surface
  -> send safe source-static diagnostic to ROS2 R2
  -> integrate R2 diagnostic
  -> wait for PMO restart decision
```

Strength:

```text
matches agent work where the plan changes after observation
```

Risk:

```text
without stable state enums and evidence records, dynamic changes become
unreviewable chat drift
```

### DAG

A DAG is a directed acyclic graph. It represents dependencies without cycles.

Example:

```text
task packet
  -> dispatch ticket
  -> runtime lease
  -> return packet
  -> checker
  -> PMO integration
```

Use it when task dependencies matter, parallel work is possible, or failure
location must be precise.

### Dynamic DAG

A dynamic DAG is a DAG that is updated while execution proceeds. It is useful
for agentic work because the agent does not know every branch before observing
tools, files, UI state, or blockers.

MoSim example:

```text
P0 objective
  -> MWORKS static source check
  -> MWORKS live gate
  -> if GUI/license blocker: human review node
  -> if source issue: R2 source_static node
  -> if live success: metrics extraction node
```

Rule of thumb:

```text
dynamic DAG = current task instance
meta workflow = rules for constructing and validating task instances
```

## 4. Graph And Process Modeling Terms

| Term | Meaning | Use When | Caution |
|---|---|---|---|
| Task graph | General graph of task nodes and dependencies. | Engineering task decomposition. | May allow cycles unless constrained. |
| Execution graph | The actual path that ran. | Audit and replay. | Must be evidence-backed. |
| Dataflow graph | Graph where data products flow between nodes. | Simulation logs -> metrics -> plots -> report. | Not ideal for human approvals. |
| Control-flow graph | Graph of possible control branches. | Conditionals, error handling. | Can become complex fast. |
| BPMN | Business Process Model and Notation. | Human-readable business/approval processes. | Heavy for lightweight Codex dispatch. |
| Petri net | Formal concurrent process model. | Resource contention and concurrency research. | Too formal for routine MoSim docs. |
| FSM / state machine | Finite states and transitions. | Thread/window/task status. | Weak for parallel dependencies. |
| Hierarchical state machine | Nested state machines. | App/thread/task sub-states. | Needs strict naming. |

MoSim should prefer:

```text
DAG for dependencies
FSM for status
packets/events for proof
workflow docs for repeatable procedure
```

## 5. Execution And Reliability Terms

| Term | Meaning | MoSim Mapping |
|---|---|---|
| Orchestrator | Central controller that decides what runs next. | PMO, bounded CoAgentOps. |
| Scheduler | Chooses when a task runs. | 10-minute patrol, dispatch SLO monitor. |
| Dispatcher | Sends the task to the execution surface. | Visible-thread send plus dispatch ticket. |
| Worker | Performs scoped work. | R1/R2/R3 visible thread. |
| Queue | Pending work list. | PMO board / dispatch backlog. |
| Lease | Time-bounded or nonce-backed proof of ownership/start. | Runtime lease under `Results/runtime_leases/`. |
| Heartbeat | Repeated proof that something is alive. | Only needed for long/live tasks, not every source-static task. |
| Checkpoint | Recoverable saved state. | Packet, lease update, task-local note, checker output. |
| Durable execution | Execution that can survive failures and resume from state. | MoSim approximates this with tickets, leases, packets, and evidence. |
| Retry | Run again after failure. | Only with idempotent/safe actions. |
| Backoff | Wait longer between retries. | Avoid retry loops. |
| Idempotency | Re-running is safe and does not duplicate damage. | Critical for dispatch, file writes, notifications. |
| Saga / compensation | Multi-step rollback or compensating action. | Useful for future live/runtime cleanup. |
| Replay | Reconstruct state from event history. | Future evidence/event log direction. |

For MoSim, durable execution does not mean importing a heavy runtime now. It
means every non-trivial visible-thread task must leave enough project-local
state to prove start, progress, blocker, or completion.

## 6. Agentic AI Terms

| Term | Meaning | MoSim Mapping |
|---|---|---|
| Agent | Model-driven executor with instructions, tools, and state. | A Codex visible thread or bounded subagent. |
| Agentic workflow | Workflow where the model chooses steps based on observations. | Dynamic PMO/department execution. |
| Tool calling | Model invokes tools. | Shell, MCP, Browser, Windows tools, GitHub plugin. |
| MCP | Protocol connecting models to external tools and data. | MWORKS, UE, ROS, GitHub, filesystem-style surfaces. |
| Skill | On-demand procedural capability. | MWORKS skills, window screenshot skill, GitHub skill. |
| Hook | Lifecycle interception or hard guardrail. | Preflight and path/action checks. |
| Guardrail | Constraint preventing unsafe or invalid action. | Hook, checker, schema, domain gate. |
| Handoff | Transfer of work or responsibility. | PMO -> R1, R1 blocker -> R2 diagnostic. |
| Subagent | Bounded helper, usually disposable. | Parallel research/review, not durable department. |
| Supervisor | Agent controlling or reviewing other agents. | PMO/CoAgentOps role, within authority. |
| Router | Chooses capability or target route. | `Docs/Index/capability_index.md`. |
| Planner-executor | Separate planning from acting. | PMO plans, department executes. |
| Orchestrator-workers | Central orchestrator with multiple workers. | PMO plus R1/R2/R3. |
| Evaluator-optimizer | Evaluate output, then revise. | Checker/reviewer return loop. |
| Human-in-the-loop | Human approval/review is part of execution. | User visual review, restart approval, final acceptance. |
| Reflection loop | Agent critiques its own work. | Useful only when bounded by evidence and stop conditions. |

Agentic does not mean autonomous chaos. In this project it means:

```text
model chooses local steps
within packet scope
using approved tools
while producing durable evidence
and stopping at declared blockers
```

## 7. Validation And Governance Terms

| Term | Meaning | MoSim Mapping |
|---|---|---|
| DAG validator | Checks graph validity. | No cycles, dependencies exist, owners and evidence gates present. |
| Schema validator | Checks JSON/YAML shape. | Task/result/dispatch packet schemas. |
| Contract checker | Checks semantic contract. | Department packet contract, native surface gate checker. |
| Policy as code | Rules encoded as executable checks. | Hooks, quality scripts, schemas. |
| Static analysis | Check without running target runtime. | Source-static checks, packet validation. |
| Preflight | Before-action safety check. | `CoAgent/hooks/preflight.py`. |
| Runtime monitor | Watches execution state. | CoAgentOps patrol. |
| Observability | Ability to inspect behavior. | Traces, packets, logs, screenshots, reports. |
| Trace | Ordered execution record. | Future event stream; current packet/checker history. |
| Evidence report | Compact report pointing to evidence. | Future NodeReport-like object. |
| Claim boundary | What can be claimed from evidence. | No `closed_loop` without runtime evidence. |
| Capability registry | Inventory of available capabilities. | Future machine-readable capability index. |
| Capability resolution | Proof that existing capabilities were considered. | Avoid recreating existing skills/scripts/workflows. |

The strongest MoSim pattern is:

```text
if a rule is checkable, implement it as a checker/schema/hook
if a rule is procedural, put it in a workflow/skill
if a rule is current status, put it on the board or ticket
if a rule is uncertain, keep it in research/design intake
```

## 8. Architecture Paradigms To Know

### Orchestration

One controller directs workers. MoSim fit: PMO dispatches R1/R2/R3 and
integrates results. Use it when authority, safety, and acceptance are complex.

### Choreography

Workers react to events without a central dispatcher for every step. MoSim can
use this later for event-triggered checker and board updates, after event
contracts are strong.

### Blackboard

Multiple agents read/write a shared state board. MoSim fit:
`Docs/Workflows/mainline_operations_board.md`. Shared boards become polluted
unless write regions and owners are strict.

### Actor Model

Independent actors hold state and communicate by messages. MoSim fit: visible
threads as actors with stable IDs and message surfaces. Each actor must expose
mailbox/readback/status/evidence, not just chat.

### Event Sourcing

Store every state change as an event, then rebuild state from events. Future
MoSim events could include task sent, readback seen, lease written, checkpoint
seen, blocker written, and return accepted.

### Pipeline

Mostly linear processing chain. MoSim fit:

```text
simulation -> logs -> metrics -> figures -> report
```

This is not enough for dead-thread recovery, approvals, or dynamic failover.

### Plan-Act-Observe Loop

Agent loop:

```text
plan -> act -> observe -> revise
```

MoSim requirement:

```text
observe must become evidence, not only chat memory
```

### Control Plane / Data Plane

Control plane decides and coordinates. Data plane does the technical work.

MoSim mapping:

```text
control plane:
  PMO, CoAgentOps, packets, dispatch tickets, checkers, workflows

data plane:
  MWORKS simulation, ROS2 topics, UE runtime, model files, result artifacts
```

Important warning:

```text
control-plane activity is not project progress unless it moves the data plane
or removes a real blocker
```

## 9. How These Terms Map To MoSim/CoAgent

| MoSim Object | General Term |
|---|---|
| `AGENTS.md` | Compact project instruction / constitution. |
| `new_conversation_context.md` | Startup context pack. |
| `mainline_operations_board.md` | Blackboard / current-state board. |
| `department_threads.json` | Actor registry / route registry. |
| Dispatch ticket | Delivery SLO record / task-control artifact. |
| Runtime lease | Durable-start proof / lease. |
| Return/blocker packet | Terminal event / evidence artifact. |
| `semantic_boundary` | Claim boundary / policy metadata. |
| `native_surface_gate` | Execution-surface selection record. |
| `capability_resolution` | Capability router audit. |
| CoAgentOps patrol | Runtime monitor / scheduler / bounded orchestrator. |
| PMO | Orchestrator / acceptance owner. |
| R1/R2/R3 | Workers / actors / failover lanes. |
| Checker scripts | Policy-as-code / contract validators. |
| Hooks | Preflight guardrails. |
| Skills | Progressive-disclosure procedures. |
| Design intake | Candidate memory / research staging area. |

## 10. Recommended Mental Model

Use this stack:

```text
Meta workflow
  defines how a class of work should operate.

Dynamic DAG
  represents one task instance and its dependencies.

State machine
  gives each node/thread/window a precise state.

Ticket/lease/packet/event
  proves what actually happened.

Checker/schema/hook
  enforces what should not depend on memory or prose.

Capability index/resolution
  makes existing tools discoverable before new assets are created.
```

For MoSim:

```text
Meta workflow = governance and reusable rule layer
Dynamic DAG = current dispatch/execution instance
FSM = per-thread/per-window/per-node status
Event/packet = evidence and recovery trail
Checker/schema/hook = hard guardrail
Capability router = tool/skill/plugin/workflow discovery
```

## 11. Practical Guidance For Future Design

1. Do not choose between meta workflow and dynamic DAG. Use both.
2. Do not make DAG nodes carry long policy prose. Nodes should point to
   workflow/checker/schema IDs.
3. Do not make meta workflows track current task status. Status belongs in
   tickets, boards, leases, and packets.
4. Use FSM enums for status words such as `blocked`, `healthy`, `started`, and
   `waiting`; avoid free text when dispatch or recovery depends on it.
5. Convert repeated rules into checkers/schemas/templates when possible.
6. Keep discussion-derived ideas in research/design intake until reviewed.
7. Treat external frameworks as vocabulary and pattern sources first; do not
   import runtime dependencies until the local control loop proves the need.

## 12. Source Pointers

Primary local context:

- `CoAgent/docs/research/agentic_software_engineering_operating_model_synthesis_20260610.md`
- `CoAgent/docs/research/context_documentation_governance_research_20260610.md`
- `CoAgent/dispatch/communication_contract.md`
- `Docs/Index/capability_index.md`

External primary sources worth consulting when this research is promoted:

- Apache Airflow DAG concepts: <https://airflow.apache.org/docs/apache-airflow/stable/core-concepts/dags.html>
- Argo Workflows DAG walkthrough: <https://argo-workflows.readthedocs.io/en/latest/walk-through/dag/>
- Temporal durable execution docs: <https://docs.temporal.io/>
- LangGraph overview and persistence docs: <https://docs.langchain.com/oss/python/langgraph/overview>
- OpenAI Agents SDK docs: <https://openai.github.io/openai-agents-python/>
- Anthropic Building Effective Agents: <https://www.anthropic.com/research/building-effective-agents>
- Model Context Protocol introduction: <https://modelcontextprotocol.io/docs/getting-started/intro>
- BPMN specification landing page: <https://www.omg.org/bpmn/>
