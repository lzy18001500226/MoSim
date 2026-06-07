# CoAgent Communication Contract V1

Date: 2026-05-28

Status: active communication contract, updated 2026-06-06.

## Purpose

This contract defines how work moves between visible Codex department
conversations and workers. The current operating model is PMO-led direct
dispatch: PMO sends work to a reusable visible thread or creates a new visible
thread when the work needs durable specialty context. CoAgent dispatch/runtime
tools support packet generation, recovery, validation, and result import; they
are not a mandatory scheduling middle office for ordinary MoSim work.

The rule is:

```text
conversation is UI and working surface
packet is durable communication
event log is recovery truth
```

## Durable Communication Units

| Unit | Created By | Consumed By | Purpose |
|---|---|---|---|
| task packet | PMO or CoAgent helper | owner conversation | start or update durable work |
| context pack | PMO / runtime helper | dedicated task conversation | compact startup state |
| checkpoint packet | owner conversation | PMO / owner department | recoverable progress, risk, blocker |
| result packet | owner conversation | result router / reviewer | terminal or reviewable output |
| review note | Verification/Security/Docs/DevOps/PMO | PMO / owner | accept, reject, or request changes |
| event log entry | runtime/helper | all recovery flows | state transition evidence |

Plain chat may explain work, but it is not sufficient for handoff or
acceptance.

## Standard Task Dispatch

```text
PMO/main:
  frames user objective
  creates task_id
  records canonical_task_goal
  records native Codex surface gate before choosing the delivery route
  assigns accountable_owner
  records worktree binding when file isolation is required
  writes task packet
  sends packet to an existing visible department thread or creates a new
  visible department thread when no reusable one exists

Owner conversation:
  receives task packet
  works within read/write scope
  emits checkpoint or result packet

Result router/reviewer:
  imports packet
  marks review metadata

PMO/main:
  reports accepted result or escalation
```

## Native Surface Gate

Before a non-trivial task is dispatched, PMO records why the work belongs to a
native Codex surface, a visible department thread, a bounded sub-agent, or
CoAgent packet/evidence glue. This is a routing decision, not a task result.

Task packets should include:

```yaml
native_surface_gate:
  selected_native_surface: [visible_thread, coagent_packet_glue]
  surface_selection_reason: durable department context plus packet return is required
  rejected_surfaces:
    subagent: disposable context is insufficient
    codex_exec: hidden formal dispatch is not accepted without visible delivery
  worktree_required: false
  worktree_decision: read-only planning task; no isolated worktree needed
expected_return_path: Results/agent_packets/returns/<request_id>.json
blocker_return_path: Results/agent_packets/blockers/<request_id>.json
```

## Department Local Planning Template

For every non-trivial visible-department assignment, PMO should include the
same local-planning block, and the target department must derive and report it
before deep business work. This is a planning and scheduling decision
requirement, not a requirement to use at least one sub-agent:

```text
department_local_goal
critical_path_steps
parallelizable_slices
subagent_plan
subagent_plan_reason
subagents_used
verification_gates
manual_review_or_blocker_triggers
```

The `department_local_goal` should be short and bounded to the current task
packet. Prefer the next concrete engineering gate over broad research,
large-scale cleanup, or workflow redesign. If a workflow, skill, MCP, or
documentation issue is discovered, record it as a parallel/follow-up action
unless the current engineering gate cannot safely proceed without that fix.

`subagent_plan` must be one of `used`, `available_but_not_useful`,
`unavailable`, or `unsafe`. `subagents_used=[]` is acceptable when the
department runtime has no sub-agent surface, no independent slice exists, or
serial execution is safer. If a department uses disposable sub-agents, they
must be bounded, task-local, evidence-returning helpers; they must not become
hidden durable departments or create/fork/rename/archive visible threads.

## Department Execution And Acceptance Contract

After local planning, the department owns execution inside the declared scope.
PMO should not have to decompose every internal step. The department must run
the task-specific infrastructure preflight before business work, then continue
through the critical path until it has either produced the declared engineering
output or hit a real blocker.

Task-specific preflights include, for example:

- MWORKS/Sysplorer/Syslab sentinel and background screenshots for MWORKS work;
- ROS2 stale-process, topic, source-window, and cleanup checks for ROS2 work;
- UE source/static/build-scope checks for UE work;
- Blender/source-asset availability and render-output checks for asset/PBR
  work.

If a preflight, GUI, license, runtime, build, tool-surface, source-data, or
permission issue blocks the task, the department must stop the domain work and
return a blocker promptly. It must not spend the turn producing unrelated JSON,
tuning parameters, retrying solver/runtime/model steps, or turning the symptom
into a completed metadata packet.

Completed work must include domain evidence that matches the task:

- model/simulation/layout/package work: `.mo` or `package.mo` edits,
  `check_model`, `SimulateModel`, native result/`.msr`, metrics,
  diagram/layout screenshots, or wiring observations;
- ROS2 runtime work: topic/process/source-window/log/cleanup evidence and
  bounded runtime artifacts when live probing is in scope;
- UE work: source/static/build/runtime evidence according to the task scope;
- asset/PBR work: Blender/UE asset files, rendered review images, material
  manifests, or visual-review artifacts.

JSON task/result/blocker packets, ledger rows, and progress notes are
control-plane evidence. They count as the engineering deliverable only when the
task is explicitly `diagnostic_only`, `rule_sync_only`,
`preflight_drill_only`, `dispatch_surface_diagnostic`, or
`static_inventory_only`.

For long or live tasks, the return/blocker packet must include phase
checkpoints: what phase ran, what evidence was inspected, what changed, and
what remains blocked. If a task produces a user-review artifact such as an
image, video, native result viewer, or model diagram, the department should
request PMO display/review instead of returning only a path.

PMO may reject completed packets that lack the declared engineering outputs,
omit the required local-planning/sub-agent decision fields, or report a real
infrastructure blocker as completed work.

PMO should run the generic visible-department packet gate before integrating
non-trivial return/blocker packets:

```powershell
python Scripts\quality\check_department_packet_contract.py `
  Results\agent_packets\returns\<request_id>.json
```

This gate is a shared backstop. It checks the local-planning fields,
`subagent_plan` decision, `actual_engineering_outputs`, and `claim_boundary`.
Domain-specific gates such as the MWORKS live gate still apply on top of it.

## Domain Dispatch Gates

Use the matching domain gate in addition to the generic local-planning block.
These gates should be present in the dispatch prompt, not only remembered by
PMO.

### ROS2 / RViz2 / FAST-LIO

ROS2 runtime work must treat every live graph as a scarce, bounded probe. If
the task says existing-evidence-only or no-rerun, the department must not
launch ROS2; it closes from the existing evidence or returns a blocker.

Before any live ROS2 graph, the department records a runtime preflight:

```text
ROS2 environment/source status
stale MoSim/FAST-LIO/planner process check
expected source-window and topic contract
forbidden topic list
probe_count budget
cleanup plan
```

Return/blocker packets for ROS2 runtime work must include the relevant runtime
evidence, not only packet metadata:

```text
ros2_preflight_before
probe_count
source_window_evidence
topic_evidence
FAST-LIO or planner evidence when in scope
forbidden_topic_absence
cleanup_summary
claim_boundary
```

If source timestamps regress, FAST-LIO callback loop-back remains, required
topics are absent, stale processes cannot be cleaned, or the one-probe budget
is exhausted, the department stops and returns a blocker. It must not rerun
until PMO issues a new task. A diagnostic FAST-LIO/source gate must not advance
into RViz2, planner/EGO, PositionCommand, 20 Hz adapter, TF/RViz readiness, or
controller claims unless the task packet explicitly opens that phase and the
previous gate passed.

### UE Experiment Console / Scene Interaction

UE work must classify its scope as source-static, build, editor/runtime, or
manual-review before execution. Completed UE work needs evidence that matches
that scope: source/schema edits with tests, build/log evidence, runtime
echo/transport evidence, or review screenshots/packets. A scene registry row,
command schema, or JSON packet is not runtime ack.

UE remains the operator/review/render surface. It must not teleport UAV pose,
feed full UE truth to planners, or label controller/planner success without
MWORKS/ROS2 evidence. If the task creates a review image/video/window, the
department asks PMO to display it or send a concise review prompt instead of
returning only a path.

### Sunray150 Asset / PBR

Sunray150 visual work must follow the DAE-derived Blender asset route and the
Sunray PBR workflow. The department starts with source asset availability,
component identity, material evidence, UV/material-slot limitations, and
intended review outputs.

Completed asset work must produce Blender/UE asset edits, material manifests,
rendered close-ups/contact sheets, texture/PBR map evidence, or explicit
failed-review images. A whole-aircraft Base Color pass or a JSON packet is not
material progress. Asset/PBR work must not change geometry assembly, rotor
centers, mass/inertia/motor/thrust constants, FAST-LIO extrinsics, ROS2/MWORKS
runtime behavior, controller, or planner files unless PMO issues a separate
task.

For every task dispatched to a MWORKS/Sysplorer/Syslab department, the task
packet must include a MWORKS live gate. Routine activation/window-health patrol
is owned by `MoSim｜CoAgent运维平台` through its 30-minute automation, so MWORKS
R1/R2 should reference the latest patrol and focus the business turn on
engineering evidence. The target department must not spend the turn repeatedly
proving activation or return only sentinel JSON as engineering progress.

```yaml
mworks_live_gate:
  live_mworks_touched: true
  mworks_window_policy: reuse_existing_session_default
  activation_patrol_owner: CoAgentOps
  recent_patrol_required: true
  max_patrol_age_minutes: 30
  required_return_fields:
    - mworks_activation_patrol_reference
    - mworks_activation_patrol_age_minutes when known
    - mworks_phase_screenshots
    - mworks_phase_observations
    - will_not_click_activation_login=true
    - live_mworks_touched
  blocker_on:
    - demo edition
    - unactivated software
    - login or activation prompt
    - authorization/equation-limit failure
    - GUI error-report dialog
    - mixed or visible-unknown blocking MWORKS/Sysplorer/Syslab windows
    - no recent patrol and required bounded live check unavailable
```

If no recent CoAgentOps patrol exists and the MWORKS task needs live MCP/GUI
work, the department may run at most one bounded current-turn sentinel/API
check or return a blocker. If it collects current-turn sentinel/capture
evidence for a real incident, it must inspect the JSON/capture/window-title
evidence and include `activation_state_observation`, `license_state`, and
`mworks_window_evidence_touched=true`. Static file-only MWORKS work may set
`live_mworks_touched=false` and proceed without touching live MWORKS when it
does not make live GUI/MCP claims.

Important correction: a visible `Sysplorer [教育版]` title is only an
edition/window marker. It does not by itself prove the account is activated,
because both activated and unactivated states can show the education-edition
title. It is also not by itself a stop signal. If no demo/login/authorization/
error marker exists, continue with the requested model/check/simulation/layout
work and use task-local API/check/simulation success only as license sufficiency
for that task. Do not claim permanent account activation unless an API/result
explicitly reports account activation status.

Live MWORKS work must still provide evidence for the engineering claim. If
`live_mworks_touched=true` and the claim includes result-viewer, plot,
animation, Smart Layout, wiring, or graphical review, the owner department must
capture and inspect phase screenshots or request PMO/CoAgentOps foreground
review of the existing window. R1 simulation/control tasks capture after
load/check and after simulate/plot/animation phases when those visuals are
claimed. R2 graphical/model-audit tasks capture during or after layout review
and inspect missing wires, disconnected blocks, unreadable routing, wrong
active windows, and new license/login/GUI-error prompts. The return/blocker
packet must include `mworks_phase_screenshots` and
`mworks_phase_observations`; the observations must say what the screenshots/
window titles showed, not only list artifact paths.

A MWORKS department return/blocker packet is incomplete if it omits the latest
patrol reference or a current-turn sentinel/capture set for a real incident,
the no-click pledge, live-touch flag, declared engineering outputs, or the live
phase screenshot/observation fields required for claimed GUI evidence. When
current-turn sentinel/capture evidence is included,
`activation_state_observation` must say what the sentinel, window title, or
screenshot actually showed, such as a single education-mode window, demo
marker, login/activation prompt, mixed state, visible unknown window, hidden
helper-window risk count, or unavailable evidence. It is not enough to return a
path or empty manifest reference.

Do not treat a clean-looking background screenshot as sufficient if other
evidence indicates demo/login/authorization risk. Sysplorer can hide the
login/license pane until the existing window is maximized or brought to
foreground. Departments must not perform that recovery themselves; they return
a blocker. PMO or CoAgentOps may perform a user-authorized bounded foreground
recovery or full layout screenshot on the existing window first, then prove
success before live MWORKS work resumes. Login/license patrols require
maximized target-window evidence: the screenshot must visually show the target
reusable MWORKS/Sysplorer/Syslab main window, not Codex, another application,
a helper/proxy window, or incomplete background `PrintWindow` output. If the
official login action does not return or cannot complete on the existing
window, PMO/CoAgentOps may reopen MWORKS and log in through the official UI as
a bounded recovery.

`license_state`, when reported, must be a concrete classification, for example
`education_window_observed_activation_unverified`,
`license_api_recorded_education_version_only`,
`mixed_education_and_demo_blocked`, `demo_blocked`, `login_required`,
`authorization_failed`, `gui_error_report_blocked`,
`sentinel_unavailable_blocked`, or `unknown_blocked`. Vague values such as
`ok`, `normal`, or `looks_fine` are not acceptable because they hide the exact
activation/session state.
When multiple Sysplorer/MWORKS windows are visible and any relevant reusable
window is in demo edition, login/activation, authorization-failed, GUI-error,
mixed, or visible-unknown blocking state, delegated departments must stop
before MCP/model retries and return an auth/license blocker for PMO
classification. The packet status must be `blocked`, with a concrete observed
state, not a completed return that merely mentions the problem. They must not
close windows, open a fresh session, click login or activation controls, or
tune solver/model code to bypass the symptom. Hidden Qt/browser-proxy/helper
windows with no license/error text are risk evidence and must be counted by
CoAgentOps patrol, but they do not alone block live work.

MWORKS department packets must declare `expected_engineering_outputs`. For
model optimization, package/model cleanup, simulation, or graphical/layout
work, expected and completed outputs must include real engineering artifacts:
`.mo`/`package.mo` changes, `check_model`, `SimulateModel`, native result/
`.msr`, metrics, diagram/layout screenshots, or wiring observations as
applicable. JSON task/result/blocker packets, progress notes, and ledger rows
are control-plane evidence only. They do not count as MWORKS engineering
progress unless the task is explicitly `diagnostic_only`, `rule_sync_only`,
`preflight_drill_only`, `dispatch_surface_diagnostic`, or
`static_inventory_only`.
Activation/license/login/authorization/GUI-error evidence from CoAgentOps
patrol or from current MWORKS work is a P0 MWORKS infrastructure incident, not
a solver/model issue. The department must stop live work and return a blocker.
CoAgentOps/PMO sends the sparse email alert for the open incident and keeps it
open until a later patrol or recovery check proves a reusable session.
Human-facing alerts stay short and Chinese; paths, screenshots, and command
details belong in packets and evidence files.
Use `Scripts/tools/capture_window_background.ps1 -OutDir ...`; `-OutputDir` is
not a valid parameter for the current project script.

PMO should reject or return-for-fix any live MWORKS task packet or
return/blocker packet that fails the machine gate:

```powershell
python Scripts\quality\check_mworks_live_gate.py `
  Results\agent_packets\<request_id>.json --kind task --expect department
python Scripts\quality\check_mworks_live_gate.py `
  Results\agent_packets\returns\<request_id>.json --kind return --expect department
```

Use `--expect static` only for compatibility checks on non-department,
explicitly file-only packets that do not inspect MWORKS windows. Use
`--expect department` for MWORKS R1/R2 dispatches, graphical review packets,
and static model-organization work owned by a MWORKS department. The current
gate accepts a recent CoAgentOps patrol reference or a current-turn
sentinel/capture set for a real incident; it still rejects JSON-only completed
returns and missing engineering outputs.

For compatibility with existing runtime packets, the same object may be stored
under `metadata.native_surface_gate`. New JSON task packets should be checked
before dispatch with:

```powershell
python Scripts\quality\check_agent_task_native_surface_gate.py `
  Results\agent_packets\<request_id>.json --strict
```

## Worktree-Aware Dispatch

When a task uses a separate Codex App worktree or Git worktree, the dispatch
packet must carry:

```yaml
worktree_path:
branch_or_base:
write_scope:
merge_owner:
review_gate:
close_condition:
```

Worktree state is part of execution context, not acceptance. A result is still
accepted only through result packet evidence and review metadata.

Worktree closeout requires:

- result packet imported,
- review state known,
- Git state summarized,
- merge or discard decision recorded,
- no untracked broad artifacts left unexplained.

## Checkpoint Contract

Checkpoint content:

```yaml
task_id:
canonical_task_goal:
conversation_objective:
owner:
current_state:
evidence_found:
files_changed:
commands_run:
blockers:
risks:
decision_needed:
next_step:
continue_or_stop:
```

Checkpoint required when:

- a long task reaches its checkpoint interval,
- appetite or circuit breaker may be exceeded,
- evidence contradicts the plan,
- the worker needs user input,
- the worker wants to change owner, scope, or goal,
- an irreversible step is near.

## Result Packet Contract

A result packet must include:

- task id,
- task class,
- canonical status,
- summary,
- owner/role,
- files changed,
- commands run,
- evidence,
- acceptance state,
- review status,
- known exclusions,
- residual risks,
- next recommended action.

Terminal result without evidence should be imported as `needs_review` or
`rejected`, not accepted.

## Support Work

Supporting departments do not change the canonical task goal.

Support flow:

```text
accountable owner requests support
PMO or CoAgent helper records child/support task or review request when needed
support owner returns result packet or review note
accountable owner integrates
PMO accepts, rejects, or escalates
```

## Owner Change

Owner change requires:

- current owner checkpoint,
- reason for handoff,
- new accountable owner,
- updated task packet or context pack,
- event log entry,
- unresolved risks.

No worker may silently hand work to another durable conversation.

## Goal Change

Goal change requires:

- evidence that current goal is wrong or incomplete,
- proposed replacement canonical task goal,
- affected scope and acceptance changes,
- PMO/user decision record, optionally backed by CoAgent runtime metadata,
- event log entry.

Until accepted, the task remains under the old canonical task goal and should
usually be `review_required` or `blocked`.

## Communication Failure

Treat communication as failed when:

- the target conversation is not visible or recoverable,
- no task packet was delivered,
- the packet was delivered only through a shadow/local Codex home while the
  user expected a front-end-visible department message,
- no result packet can be found,
- the worker result exists only in chat,
- the task id or canonical goal does not match,
- packet evidence paths are missing,
- review metadata is absent for high-risk work.

Recovery action:

```text
stop dispatch
record blocker
repair registry or context pack
retry only with a fresh packet or explicit recovery note
```

If the accountable owner falls back to local execution after department
transport fails, the fallback must be reported as a coordination failure, not
as successful department execution. A visible department status message should
be sent and synced before claiming that the department conversation has been
updated.

## V1 Constraint

V1 communication is PMO-led and packet-based. The durable authority is the
recorded task packet, return/blocker packet, ledger/runtime entry, and evidence
path, not a chat reply or a hidden helper process. Departments may request work
from each other only when they include origin thread id, request id, expected
return/blocker paths, and responsible owner. PMO does not have to be an
intermediate chat hop for every support request, but it remains accountable for
integration and may audit or override routing when the task affects the project
goal, Git state, evidence claims, user review, credentials, GUI/license state,
or safety boundary.
