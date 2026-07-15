# Agent Project Operating Layers And Research Plan

Status: promoted_to_canonical
Authority: superseded by `Docs/Workflows/agent_project_operating_layers.md`
Source: PMO discussion, local reference review, and initial official-doc calibration, 2026-06-10 CST
Target canonical doc: `Docs/Workflows/agent_project_operating_layers.md`
Promotion owner: PMO plus documentation-secretary/context-maintenance review
Do not treat this cache draft as workflow authority; use the canonical workflow.

## 1. Current Thesis

The project should not optimize for a beautiful department chart. The useful
system is a working agentic software-engineering operating loop:

```text
native execution surface
  -> durable task control loop
  -> capability discovery and routing
  -> context governance
  -> project-domain evidence
  -> human governance
```

Roles such as PMO, CoAgentOps, R1/R2/R3 departments, documentation secretary,
and disposable subagents are role views over this loop. They are not the core
architecture by themselves.

If the loop cannot reliably dispatch work, detect start/failure, find existing
capabilities, collect evidence, and surface blockers to the human PMO, the
architecture is not useful regardless of how clean the role diagram looks.

## 2. Practical Layering For MoSim

### Layer 1: Execution Surface

What actually executes:

```text
Codex App visible thread
shell / PowerShell / WSL
MCP and plugin tools
skills
desktop window surfaces
MWORKS / Sysplorer / Syslab
ROS2 / RViz / FAST-LIO
UE editor/runtime
Git and filesystem
```

Core questions:

```text
Can this surface execute now?
Can it read/write the intended project state?
Can it call the needed native tool?
Is it blocked by app/network/approval/window/license state?
What evidence proves the surface started?
```

### Layer 2: Task Control Loop

The project needs task-control artifacts before organization charts:

```text
dispatch ticket
task packet
runtime lease
readback observation
checkpoint
return packet
blocker packet
checker result
PMO board row
```

Core questions:

```text
Was the task really sent?
Did the target thread really start?
Did it write a durable artifact?
Is there a return, blocker, checkpoint, approval surface, or context surface?
Who owns the next action?
```

### Layer 3: Capability Discovery And Routing

Codex can fail by not knowing the project already has a skill, MCP route,
script, checker, or workflow. This layer must prevent duplicate creation and
wrong tool choice:

```text
capability index
capability_resolution block
skill index
MCP/plugin index
script index
workflow index
checker index
future machine-readable capability manifest
```

Core questions:

```text
What capability should this task use?
Where is the existing asset?
Is the existing asset enough?
If not, why is new work needed?
What is the authority ceiling and evidence requirement?
```

### Layer 4: Context Governance

This is the main difference from traditional software engineering. Multiple
long-lived agent conversations can hold different recent context, and thread
history/compression cannot be the only project state.

Relevant artifacts:

```text
AGENTS.md
Docs/Workflows/new_conversation_context.md
Docs/Workflows/mainline_operations_board.md
context pack
Docs/Cache/design_intake/
session-memory migration records
capability coverage map
project memory index
```

Core questions:

```text
What must a fresh or resumed thread read?
What must not be treated as authority?
Which facts are canonical, cached, rejected, or superseded?
How does one thread learn that another thread corrected an assumption?
How do we stop discussion notes from polluting startup context?
```

### Layer 5: Project Domain Layer

This is the actual MoSim deliverable:

```text
Models/
Config/
Scripts/
Results/
References/
UE5/
Docs/Design/
Docs/Workflows/ host adapters
MWORKS/ROS2/UE evidence
controller/planner/simulation outputs
```

Core questions:

```text
Does the UAV simulation work?
What evidence proves it?
Can UE run the map and show the vehicle?
Can ROS2 see real point cloud / TF / map / planner review surfaces?
Can MWORKS generate formal simulation and metrics?
```

### Layer 6: Human Governance

The human PMO is part of the operating system:

```text
approval
manual review
email notification
window/license/login intervention
accept/reject final evidence
direction correction
restart decision
```

Core questions:

```text
When should the system stop and ask?
How sparse should notification be?
What can be delegated safely?
What must remain human acceptance?
```

## 3. Why This Differs From Traditional Software Projects

Traditional project architecture usually assumes stable workers, deterministic
tools, and explicit CI/CD state. This project has additional execution risks:

```text
long-lived conversation context drift
thread dead/wedged states
hidden app approval surfaces
tool availability changes
skills/plugins that exist but are not invoked
half-promoted rules in conversation history
runtime evidence split across files, windows, and packets
```

Therefore the operating design should optimize for:

```text
durable evidence over chat claims
small task packets over broad instructions
capability discovery before asset creation
machine-checkable contracts over prose-only rules
cache-first design notes before canonical promotion
visible blocker over silent waiting
```

## 4. Existing Local Research To Reuse First

Before creating new research files, check these existing local files:

```text
CoAgent/docs/research/agentic_software_engineering_operating_research_plan_20260610.md
CoAgent/docs/research/context_documentation_governance_research_20260610.md
CoAgent/docs/research/REFERENCE_PROJECT_INDEX.md
CoAgent/docs/research/LEARNING_STRATEGY.md
CoAgent/docs/research/THREE_ROUND_STUDY_AND_DISCUSSION.md
Docs/Cache/design_intake/index.md
Docs/Cache/design_intake/inbox/20260610_capability_resolution_context_gap.md
```

The research workflow should be:

```text
read existing local research index
  -> identify missing question
  -> inspect local reference project if present
  -> use official docs/web only for current or missing facts
  -> write incremental notes into design intake or update an existing research file
  -> propose canonical promotion only after dedup review
```

Do not generate a new full research report if an existing file can be updated
or referenced.

## 5. Initial External Calibration Sources

These sources were used only to calibrate the research plan, not to create an
approved workflow:

| Source | Initial Lesson For MoSim |
|---|---|
| OpenAI Agents SDK docs | If the application owns orchestration, tool execution, approvals, and state, it needs explicit agent runtime patterns rather than ad hoc calls. |
| OpenAI Agents SDK tracing docs | Agent runs benefit from event traces for tool calls, handoffs, guardrails, and custom events. |
| Anthropic Claude Code autonomy article | Hooks, subagents, context management, and permission frameworks are first-class customization surfaces. |
| Gemini CLI extensions docs | Extensions package capabilities and MCP servers; installed capability is separate from when an agent should use it. |
| LangGraph overview / persistence / interrupts docs | Durable execution, checkpointing, streaming, and human-in-the-loop are central runtime concerns. |
| Local `okwinds/capability-runtime` | Capability systems should link protocol, runtime, report, manifest, evidence, and regression anchors. |

## 6. Research Goal

Research goal:

```text
Design a practical, non-duplicative, evidence-driven agentic software
engineering operating model for MoSim, using Codex App visible threads as the
current execution surface and CoAgent as a portable control-plane core.
```

The goal is not:

```text
create a polished department org chart
replace Codex App with a generic framework
write another large prose-only architecture document
import an external runtime dependency before the control loop is proven
```

## 7. Proposed Subagent Plan

This is a planning artifact. Do not spawn subagents from this draft without a
PMO-approved task packet.

### Subagent A: Local Reference Synthesizer

Scope:

```text
References/Agent/
CoAgent/docs/research/
Docs/Cache/design_intake/
```

Tasks:

1. Build a reuse map of already-reviewed local research.
2. Identify which local projects cover execution surfaces, durable workflow,
   capability runtime, skills/plugins, memory/context, and observability.
3. Produce an incremental gap list, not a new generic survey.

Expected output:

```text
local_research_reuse_map
source -> lesson -> already_recorded_where -> missing_followup
```

### Subagent B: Official Vendor Docs Synthesizer

Scope:

```text
official docs only unless PMO approves blog/community sources
OpenAI
Anthropic
Google Gemini CLI
LangGraph/LangChain
Microsoft/autogen or Agent Framework if locally relevant
```

Tasks:

1. Extract only operating primitives: tools, hooks, skills, memory, subagents,
   checkpoints, interrupts, tracing, approval, sessions.
2. Map each primitive to a MoSim layer.
3. Separate stable official docs from blog interpretations.

Expected output:

```text
official_source_matrix
source_url -> primitive -> MoSim implication -> confidence -> followup
```

### Subagent C: Open-Source Operating Pattern Analyst

Scope:

```text
capability-runtime
OpenHands
LangGraph
Hermes/OpenClaw/oh-my-codex family
SWE-agent/Aider/Cline/Continue where useful
```

Tasks:

1. Compare pattern implementation, not branding.
2. Extract object model: manifest, runtime, report, event log, queue, approval,
   context pack, memory, skill.
3. Mark each pattern as adopt, adapt, reference_only, or reject.

Expected output:

```text
pattern_adoption_matrix
project -> pattern -> adopt/adapt/reference_only/reject -> reason -> MoSim landing target
```

### Subagent D: MoSim Control-Loop Designer

Scope:

```text
CoAgent/dispatch/
CoAgent/protocol/
Docs/Index/capability_index.md
Scripts/quality/
Results/agent_packets/
Docs/Workflows/mainline_operations_board.md
```

Tasks:

1. Convert research into the smallest runnable control-loop increment.
2. Prioritize checker/schema/template changes over prose.
3. Keep MoSim P0 engineering progress separate from CoAgent architecture work.

Expected output:

```text
implementation_slices
slice -> files -> tests/checkers -> risk -> dependency -> acceptance
```

## 8. Suggested Immediate Research Phases

### Phase 0: Reuse Audit

Before any new research:

```text
read existing research files
read REFERENCE_PROJECT_INDEX
read design_intake cache
search local references by project/pattern
```

Output:

```text
what is already known
what is stale
what is missing
what should not be researched again
```

### Phase 1: Capability System

Question:

```text
How should MoSim represent capabilities so agents find and reuse existing
skills/workflows/scripts/checkers instead of recreating them?
```

Likely outputs:

```text
machine-readable capability manifest
coverage map
capability_resolution checker
promotion path from cache to canonical docs
```

### Phase 2: Durable Task Control Loop

Question:

```text
What minimum artifacts prove a Codex visible-thread task was delivered,
started, executed, blocked, or completed?
```

Likely outputs:

```text
dispatch ticket updates
runtime lease contract
return/blocker/evidence report alignment
dead-thread SLO tests
```

### Phase 3: Context Governance And Promotion

Question:

```text
How do discussion notes become project rules without polluting entry docs?
```

Likely outputs:

```text
design_intake review workflow
documentation-secretary patch proposal format
canonical promotion checklist
cache rejection/supersede records
```

### Phase 4: Host Runtime / Human Governance

Question:

```text
How should wait/resume/approval/restart/manual-review surfaces be represented
without pretending Codex App is a fully controllable runtime?
```

Likely outputs:

```text
host snapshot vocabulary
approval/review/provider state classes
manual notification boundary
restart validation packet contract
```

## 9. Link Collection Requests For User

Ask the user for more links only if a needed source is not already in local
`References/Agent/` or available from official docs.

Potential future link requests:

```text
private or removed repositories that inspired the current design
specific blog posts by the capability-runtime author
commercial-agent architecture posts the user considers high quality
Codex App issue/discussion links about thread state, automation, or context
```

Do not ask the user to crawl links already present under `References/Agent/`.

## 10. Non-Goals For This Draft

This draft does not:

1. approve runtime implementation,
2. change dispatch rules,
3. create or migrate visible threads,
4. change `AGENTS.md` or startup context,
5. adopt `capability-runtime` as a dependency,
6. claim MoSim MWORKS/ROS2/UE progress,
7. replace PMO/user acceptance with an automated framework.
