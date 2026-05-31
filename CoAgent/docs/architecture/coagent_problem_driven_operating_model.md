# CoAgent Problem-Driven Operating Model

Date: 2026-05-29

Status: problem expansion and design input. This document does not approve
runtime, transport, automatic conversation creation, automatic worktree
creation, unattended automation, or notification integration.

## Purpose

CoAgent design should start from real tasks and likely failure modes, then
borrow from strong agent systems and strong engineering-management systems.

The wrong order is:

```text
collect many agent ideas
  -> draw a generic architecture
  -> try to force real tasks into it
```

The right order is:

```text
real task pressure
  -> failure modes
  -> required coordination mechanism
  -> matching external pattern
  -> CoAgent rule / packet / hook / skill / review gate
```

This document expands the current issue register with concrete problems from
two stress-test task families:

1. PX4 log based simulator-parameter identification.
2. UE scene truth, SLAM/planning/navigation, disturbance/fault experiments,
   and RflySim-like simulation productization.

## Reference Pattern Legend

| Pattern | What It Contributes |
|---|---|
| Anthropic orchestrator-workers | parallel research/execution only when decomposition is real |
| Anthropic context engineering | context budget, scoped context, evaluator loops |
| OpenAI Agents SDK handoff modes | separate manager-as-tool from real control-transfer handoff |
| Codex thread/worktree model | visible work surfaces and file-isolation surfaces |
| A2A task/artifact states | distinguish messages, durable tasks, artifacts, history, `input_required`, `auth_required` |
| LangGraph / Temporal | durable state, interrupts, replay, resumable workflow |
| Google ADK / Semantic Kernel | topology selection: sequential, parallel, loop, handoff, group/review modes |
| Hermes / OpenClaw | runtime/UI split, context engine, hooks, notifications, recovery surfaces |
| GitLab DRI / DACI | one accountable owner and explicit decision authority |
| Shape Up | appetite, circuit breaker, stop unbounded work |
| Google SRE | incident response, postmortem, escalation, recovery |
| DORA / SPACE | evaluate flow and quality with balanced metrics, not activity count |
| Team Topologies | capability boundaries should reduce cognitive load, not create handoff theater |

## Scenario A: PX4 Log To Simulator Parameters

### Task Shape

Example user request:

```text
Here is a PX4 log. Identify simulator parameters from it and tune the
simulation so the aircraft behavior matches the log.
```

This is not one coding task. It is a multi-stage engineering task:

1. understand the log,
2. classify what can be identified,
3. research methods and prior art,
4. estimate parameters,
5. map estimates to simulator parameters,
6. run simulations,
7. tune/calibrate,
8. verify against the log,
9. document uncertainty and non-identifiable parameters,
10. integrate code, evidence, and docs.

### A1: Task Framing Can Be Wrong

Failure mode:

The system assumes "identify parameters" means all simulator parameters are
recoverable from a single log. Many are not identifiable without inputs,
excitation, wind information, actuator data, or vehicle geometry.

External patterns:

- Shape Up appetite and problem shaping.
- GitLab DRI / DACI decision clarity.
- Anthropic context engineering: explicitly state assumptions and non-goals.

CoAgent need:

Every task starts with a `Task Charter` containing:

```text
known goal
unknowns
assumptions
non-goals
identifiability risk
required evidence
first checkpoint
circuit breaker
```

### A2: Log Quality May Make The Task Impossible

Failure mode:

The log may lack actuator commands, motor RPM, wind estimate, good timestamps,
high-excitation maneuvers, or clean flight windows. An agent may still try to
fit parameters and produce false confidence.

External patterns:

- A2A task states: `input_required`, artifacts, history.
- Google SRE: stop, classify, escalate when evidence is insufficient.
- Anthropic evals: evaluate evidence quality before output quality.

CoAgent need:

Create an early `Data Sufficiency Gate`:

```text
status: blocked | input_required | proceed_with_limitations
artifact: log_audit_report
required_user_input: additional logs / vehicle config / actuator data
allowed_claims: only parameters supported by available evidence
```

### A3: Method Research Can Drift Forever

Failure mode:

The research conversation keeps reading papers and repos without producing a
usable decision.

External patterns:

- Shape Up appetite and circuit breaker.
- Anthropic orchestrator-worker: workers return artifacts, not open-ended
  conversation.
- DORA/SPACE: activity is not progress.

CoAgent need:

Research slices must have an appetite and output table:

```text
method
required signals
estimated parameters
assumptions
implementation complexity
fit for current log
recommended / reject / later
```

### A4: Identifiable And Non-Identifiable Parameters Need Separate Outputs

Failure mode:

The agent reports one parameter list without distinguishing measured,
estimated, calibrated, guessed, and impossible-to-infer values.

External patterns:

- A2A artifacts and task history.
- Scientific traceability / evidence gates.
- Review gate separate from result import.

CoAgent need:

Parameter outputs need categories:

```text
directly_observed
estimated_from_log
calibrated_in_simulation
assumed_from_vehicle_spec
not_identifiable_from_current_data
requires_human_or_experiment
```

### A5: Estimator Code And Simulation Tuning Are Different Work

Failure mode:

One conversation tries to implement estimators, tune MWORKS/Syslab models, and
validate flight behavior simultaneously. Context overload and confirmation bias
follow.

External patterns:

- OpenAI Agents SDK: manager-as-tool vs handoff.
- Google ADK / Semantic Kernel: topology selection.
- Codex worktrees: isolated file surfaces.

CoAgent need:

Likely task team topology:

```text
LogAudit conversation
MethodResearch conversation
Identifiability conversation
EstimatorImplementation conversation
SimulatorMapping conversation
SimulationTuning conversation
Verification conversation
DevOpsIntegration conversation
```

Not all conversations start at once. The task coordinator opens later slices
only after gates pass.

### A6: Simulator Activation Or License Can Block Execution

Failure mode:

MWORKS/Syslab license or login expires. The simulation worker retries,
hangs, or wastes time.

External patterns:

- A2A `auth_required` / `input_required`.
- LangGraph / Temporal interrupts and resume.
- Google SRE incident escalation.
- OpenClaw/Hermes notification and recovery ideas.

CoAgent need:

Auth/license failure becomes a blocker packet:

```text
state: auth_required
blocked_surface: MWORKS | Syslab | UE | Epic | network
evidence: log excerpt / screenshot path / command output
human_action_required: login / activate / open GUI / approve
resume_command:
resume_context_pack:
timeout_before_escalation:
notification_policy:
```

No worker may keep retrying indefinitely after an auth-required classification.

### A7: Parameter Fit May Pass Metrics But Fail Flight

Failure mode:

The identified parameters minimize one trajectory error but produce unstable
flight in another scenario.

External patterns:

- Anthropic evaluator loops.
- DORA stability metrics, not only throughput.
- Independent verification lane.

CoAgent need:

Verification must include:

```text
fit_metrics_on_source_log
holdout_log_or_scenario
flight_stability_check
controller_sensitivity_check
known_failure_cases
approved_usage_scope
```

### A8: Tuning Can Become Endless

Failure mode:

The tuning conversation keeps making small changes with no stop condition.

External patterns:

- Shape Up circuit breaker.
- SRE incident timeout/escalation.
- SPACE balanced quality and flow.

CoAgent need:

Simulation tuning must define:

```text
appetite
max_iterations
metric_target
acceptable_error_band
stop_if_no_improvement_after_n_trials
escalate_if_model_structure_mismatch
```

## Scenario B: UE Scene Truth And RflySim-Like Simulation Product

### Task Shape

The target product line is a simulation system similar in spirit to RflySim:

- selectable UE maps,
- map truth for planning,
- robot/sensor deployment,
- FastLIO or other state estimation,
- path planning and obstacle avoidance,
- wind and actuator-efficiency degradation experiments,
- UI controls for maps, algorithms, wind, faults, and tasks,
- later cluster/batch execution.

### B1: Rendering Success Is Not Simulation Readiness

Failure mode:

The scene looks good but lacks collision truth, semantics, occupancy, routes,
spawn points, sensor geometry, or planner-ready exports.

External patterns:

- Artifact-oriented acceptance.
- Verification gate separate from visual inspection.
- DORA quality/stability over activity.

CoAgent need:

Scene acceptance requires artifacts:

```text
map_load_evidence
collision_truth
semantic_truth
occupancy_grid_or_navigation_mesh
spawn_land_pad_definitions
planner_coordinate_transform
sensor_visibility_notes
manual_visual_review
```

### B2: Fab/UE GUI Access Can Be A Human Gate

Failure mode:

Epic/Fab/UE requires login, manual import, unsupported asset version, GUI
selection, or license acceptance. Automation keeps trying and fails.

External patterns:

- A2A `auth_required` / `input_required`.
- SRE escalation and incident state.
- Hermes/OpenClaw notifications.

CoAgent need:

GUI/auth blockers become first-class:

```text
blocked_surface: Epic | Fab | UE Editor | plugin | asset import
human_action: click/import/login/select project
safe_resume_point:
fallback_route: local project / manual import / commandlet / editor python
```

### B3: MCP Tool Availability Is Not Capability Availability

Failure mode:

MCP inventory lists a UE tool, but the editor listener is not reachable, the
map is wrong, the plugin crashed, or the current world is Entry.

External patterns:

- Tool preflight / capability cards.
- SRE health checks before action.
- Hooks as hard gates.

CoAgent need:

Each tool surface needs a capability card:

```text
tool_name
transport_health
current_project
current_level
read_capabilities
write_capabilities
known_crash_risks
last_successful_probe
fallback_route
```

### B4: UE Crashes Must Become Incidents, Not Just Failures

Failure mode:

UE crashes after a reversible probe or actor spawn issue. The agent repeats
the same probe and causes more crashes.

External patterns:

- Google SRE incident and postmortem.
- OpenClaw/Hermes doctor/recovery.
- Hook-based dangerous-action block.

CoAgent need:

UE crash creates an `Incident Packet`:

```text
incident_type: ue_crash
last_action
crash_log_path
suspected_cause
blocked_tools
safe_next_probe
requires_manual_editor_restart
postmortem_required: yes/no
```

### B5: Scene Import And Planner Truth Are Coupled But Not The Same

Failure mode:

The asset import conversation declares success, while the planner-truth
conversation cannot use the scene because scales, collision, semantics, or
coordinate frames are wrong.

External patterns:

- Integration owner and review owner separation.
- A2A artifacts.
- Team Topologies: reduce handoff ambiguity with explicit interfaces.

CoAgent need:

Scene team produces an interface contract:

```text
map_id
ue_level_path
world_to_planner_transform
unit_scale
collision_source
semantic_labels
occupancy_resolution
known_unmapped_assets
truth_export_command
truth_validation_command
```

### B6: FastLIO / Planning / UE Integration Has Cross-Team Coupling

Failure mode:

FastLIO assumes one sensor frame, planner assumes another, UE exporter uses a
third, and each conversation thinks its part is correct.

External patterns:

- Shared context delta.
- Architecture review gate.
- Interface contract as artifact.

CoAgent need:

Cross-team contracts must include:

```text
coordinate frames
time bases
sensor noise model
vehicle dimensions
map origin
planner input/output schema
failure modes
```

Changes to these require a `Context Delta` broadcast to affected conversations.

### B7: UI Productization Can Hide Research Debt

Failure mode:

The RflySim-like UI adds sliders and algorithm selectors before underlying
simulation evidence is valid.

External patterns:

- Working Backwards / product discovery.
- DORA quality gates.
- Review gate before product surface.

CoAgent need:

UI features must map to validated backend capabilities:

```text
control: wind slider
backend: wind model parameter injection
evidence: batch experiment with expected response
status: available | experimental | mocked | blocked
```

### B8: Cluster Execution Multiplies Bad Assumptions

Failure mode:

A flawed simulation setup is scaled to a cluster, producing many invalid
results.

External patterns:

- SRE rollout safety.
- DORA change failure rate.
- Temporal durable workflow with replay.

CoAgent need:

Cluster/batch gate:

```text
single_run_evidence
reproducibility_seed
artifact_path_policy
resource_budget
failure_recovery
sample_size_plan
stop_on_invalid_evidence
```

## Cross-Cutting Problems To Add To The Issue Register

### C1: Task Topology Is Dynamic

Problem:

The number of conversations is not known at task start. A task may start with
one analysis conversation and later split into research, implementation,
verification, incident, DevOps, and documentation conversations.

Need:

Topology must be revisable through controlled events:

```text
propose_new_conversation
approve_new_conversation
close_conversation
merge_conversation_result
collapse_back_to_main
```

### C2: Context Quality Must Be Measured, Not Assumed

Problem:

A context pack can be too short, too long, stale, biased, or missing critical
negative lessons.

Need:

Context packs need quality fields:

```text
token_estimate
source_coverage
freshness
forbidden_assumptions
open_questions
decision_refs
evidence_refs
known_risks
```

### C3: Contradictions Must Be First-Class

Problem:

Two conversations may return conflicting conclusions. If Dispatch simply
summarizes both, the final answer becomes incoherent.

Need:

Introduce `Contradiction Packet`:

```text
claim_a
claim_b
evidence_a
evidence_b
impact
resolver
resolution_deadline
decision_record
```

### C4: Human Notification Is A Separate Capability

Problem:

The system may need to notify the user when licenses, GUI login, long jobs,
or manual review are required. Email or desktop notification is useful, but it
is security-sensitive.

Need:

Notification policy:

```text
allowed_channels: main_chat | codex_app | email_later | local_desktop_later
notification_owner
secret_boundary
rate_limit
message_template
ack_required
resume_link_or_command
```

### C5: Long Tasks Need Anti-Loop Controls

Problem:

Agents can enter semantic loops: repeatedly trying the same failing MCP probe,
retuning parameters without improvement, or rereading the same sources.

Need:

Anti-loop controls:

```text
attempt_counter
novelty_requirement
last_failure_signature
max_same_failure_retries
circuit_breaker
required_escalation
postmortem_trigger
```

### C6: Skills Are Lessons, Hooks Are Enforcement

Problem:

A failed task may produce a useful lesson, but putting everything into skills
will not enforce safety. Conversely, turning every lesson into a hook will
block normal work.

Need:

Postmortem classification:

```text
skill_update
hook_update
checklist_update
doctor_check
test_case
documentation_note
do_not_repeat_rule
```

### C7: Worktree Merge Needs A Review Economy

Problem:

One task team may produce many worktrees. Reviewing all diffs can become
slower than the work itself.

Need:

Merge strategy must distinguish:

```text
discard
cherry_pick
merge_whole
manual_rewrite
compare_two_candidates
request_rework
```

### C8: Capability Claims Need Proof

Problem:

An agent/conversation may say it can run UE, MWORKS, tests, Git, or email, but
the tool or environment may be unavailable.

Need:

Capability proof:

```text
declared_capability
last_verified_at
probe_command
probe_result
scope_limit
fallback
```

### C9: Task Value Can Change Midstream

Problem:

A route may become less valuable after a cheaper fallback appears, such as
manual Fab import being faster than full automation.

Need:

Task re-shaping event:

```text
original_route
new_route
reason
saved_cost
lost_capability
user_decision_required
```

### C10: Knowledge Promotion Needs Quality Gates

Problem:

Bad conclusions can be promoted into docs, skills, or context packs and poison
future tasks.

Need:

Promotion gate:

```text
source_evidence
reviewer
scope_of_validity
expiration_or_revisit_condition
conflicting_evidence
```

## Candidate New Issue Register Entries

The following should be added or cross-linked to the issue register:

| New Issue | Summary | Related Existing Issues |
|---|---|---|
| CAI-016 Task topology revision | Task teams must support dynamic split/merge/close events | CAI-002, CAI-003 |
| CAI-017 Context quality metrics | Context packs need measurable quality and freshness fields | CAI-004 |
| CAI-018 Contradiction resolution | Conflicting conversation outputs require an explicit packet and owner | CAI-005, CAI-008 |
| CAI-019 Human notification policy | Auth/manual-review blockers need safe notification and ack rules | CAI-009, CAI-015 |
| CAI-020 Anti-loop controls | Repeated failed attempts must trip circuit breakers | CAI-008, CAI-015 |
| CAI-021 Skill/hook promotion rules | Lessons need classification into docs, skills, hooks, tests, or doctor checks | CAI-014 |
| CAI-022 Worktree review economy | Multi-worktree tasks need merge/discard/review strategy | CAI-006 |
| CAI-023 Capability proof | Conversation/tool capability must be probed, not assumed | CAI-010, CAI-012 |
| CAI-024 Task reshaping | Tasks need an explicit path for cheaper fallback or route change | CAI-007, CAI-009 |
| CAI-025 Knowledge promotion safety | Durable memory and skills need evidence and validity scope | CAI-004, CAI-014 |

## Next Discussion Order

For design discussion, the most useful order is:

1. canonical task record,
2. task topology selector and revision events,
3. context pack and context quality,
4. packet protocol including contradictions and blockers,
5. capability proof and tool health,
6. human interrupt / notification policy,
7. worktree review and merge economy,
8. postmortem-to-skill/hook/test promotion.
