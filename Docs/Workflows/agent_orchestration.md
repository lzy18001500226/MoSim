# Agent Orchestration Workflow

> MoSim compatibility entrypoint. The portable CoAgent OS source of truth is
> `CoAgent/docs/operating/agent_orchestration.md`; keep reusable task graph,
> sub-agent, checkpoint, SLO, review, and long-running-task rules there first,
> then mirror only MoSim-specific workflow adapters here.

> Use this when a task is large enough that sub-agents, long Git work, or
> reference-repository audits could continue across user turns.

## 0. Canonical CoAgent Protocol

The current approved protocol entry is `CoAgent/protocol/README.md`. New task
packets, result packets, context packs, and workflow text must use that
vocabulary unless they explicitly document a temporary runtime alias.

Canonical interaction classes:

```text
simple_message
durable_task
long_running_task
checkpoint
result
```

Canonical task-intake classes:

```text
simple_message
clear_task
complicated_task
complex_task
chaotic_incident
disordered_task
long_running_task
```

Canonical states:

```text
planned
ready
working
input_required
auth_required
review_required
blocked
failed
completed
canceled
rejected
superseded
```

Goal hierarchy:

```text
Project Goal -> Canonical Task Goal -> Conversation Objective -> Subagent Objective
```

Task/worktree/review surface selection is defined in
`CoAgent/docs/architecture/coagent_task_surface_model.md`. Use that document before
deciding whether work stays in the main thread, moves to a department
conversation, becomes a task team with scoped task conversations, or needs an
isolated worktree.

Review acceptance, merge ownership, and worktree closeout are further defined
in `CoAgent/docs/architecture/coagent_review_merge_protocol.md`.

Codex native capability selection happens before CoAgent expansion. Use this
surface gate in PMO planning:

| Need | Preferred Surface |
|---|---|
| Hard mechanical guardrail | Native hook plus `CoAgent/hooks/preflight.py` |
| Durable project rule | `AGENTS.md` |
| One task procedure | One task-specific workflow or skill |
| Live external tool or GUI operation | MCP/app/plugin, Browser, or Windows MCP |
| Durable specialty context | Visible Codex thread |
| Bounded parallel research/review/execution | Short-lived sub-agent |
| Independent write stream | Visible thread or task conversation with isolated worktree when practical |
| Code-review gate | `codex review` or scoped review sub-agent |
| Clear background one-shot | `codex exec` |
| Recurring check/reminder | Codex App automation/thread wakeup after local verification |
| User-facing long-task intervention | Sparse email by default; WeChat only for explicit retry or gateway diagnosis |
| MoSim-specific return/evidence glue | CoAgent packet, ledger, result import, or doctor helper |

Do not add CoAgent runtime, queue, schema, or department machinery until this
native surface gate shows a real gap.

CoAgent gated-change rule: before changing `CoAgent/` runtime, transport,
automation, task-state schema, task/result packet schema, permanent department
conversation design, tool/MCP surfaces, or broad hooks, read `CoAgent/STATUS.md`
and the current decision record. As of this workflow, only explicitly approved
implementation scopes such as `COAGENT-IMPL-MINILOOP-01` may proceed. Later
app-server transport, unattended automation, new permanent departments, broad
hook rewrites, and tool/MCP expansion require their own approved task.

PMO dispatch priority: MoSim P0 mainline work is MWORKS R1/R2, ROS2 R1, and
UE gate progress, with Sunray active only when the user reopens asset work.
Reference-study/probe work is a support lane for named source-first questions.
It must not be counted as mainline progress and must not suppress
`dispatch_needed` for an idle P0 engineering thread.

Codex App context-compression exception: when a visible thread appears stalled
but the App UI itself shows an abnormal context-compression state, for example
`Context Left 100.0%` and manual slash-command compression is needed, classify
the first incident as `codex_context_compression_surface`. Notify the user and
use the user-confirmed manual recovery path: switch the affected conversation
to `gpt-5.4` with `high`, type `/`, select compression, wait for completion,
then switch back to `gpt-5.5` with `high`. Only after that run the normal
no-op or expected-packet validation. Do not immediately create a replacement
thread or trigger Codex++ restart for this specific surface issue.

For every PMO-dispatched non-trivial task, write the gate decision into the
task graph or packet before dispatch. The record should name the selected
surface, the rejected alternatives when relevant, the worktree decision, and
the expected result/blocker packet path. This prevents visible-thread work,
sub-agents, `codex exec`, WeChat, and CoAgent packet glue from being mixed
without an explicit reason.

Multi-conversation task-team architecture is defined in
`CoAgent/docs/architecture/coagent_task_team_architecture.md`. Use it before splitting
one long task across several conversations or worktrees.

V1 maximum durable nesting:

```text
PMO/main -> visible department or task team -> scoped task conversation -> short-lived subagent
```

The old "DispatchCenter as mandatory middle office" model is deprecated for
ordinary MoSim work. PMO directly creates or reuses visible Codex department
threads and sends task packets with explicit return contracts. CoAgent runtime,
dispatch, result-router, doctor, and queue tools remain available as support
infrastructure when a task needs durable queue state, packet generation,
visibility diagnosis, result import, or evidence validation.

No department-internal durable agent swarms, unrecorded peer-to-peer worker
state, app-server transport, or unattended write automation are allowed in V1
without a later approved task.

## 1. Task Graph First

Planning is mandatory before execution. For any non-trivial task, the main
agent must first create or update a task graph, even when the next action looks
obvious. Do not spawn agents, copy large trees, run simulations, or start Git
batches before this planning pass exists in chat or in a recoverable intake /
ledger record.

Before spawning agents, write a short task graph:

```text
critical path:
parallel streams:
write ownership:
blocking risks:
verification:
git/quality owner:
```

Runtime guard: any interactive Codex thread bootstrap, external GUI probe, MCP
probe, or unclear-progress command gets a 60 second timeout by default. On
timeout, terminate only the directly related child process, record what was
created or not created, and return to the task graph. Do not spend multi-minute
turns waiting for a bootstrap command unless the user explicitly approved that
wait.

The 60 second rule applies to interactive or unclear-progress attempts, not to
known long-running simulations, builds, conversions, or validated live-runtime
tasks that declare their expected runtime and checkpoint cadence. Long tasks
must poll/checkpoint rather than silently wait.

Minimum planning gate:

```text
objective:
current repo / tool state:
native Codex surfaces to use:
critical path:
parallelizable side work:
owners and write scopes:
worktree / thread / sub-agent / exec / review selection:
verification gates:
Git strategy:
stop / ask conditions:
```

Execution may begin only after the plan identifies the next local critical-path
step and any delegated streams. If the user says "continue", recover the
current plan from `PROGRESS.md`, `Docs/Workflows/agent_task_ledger.md`,
`Results/tmp/task_intake/`, or `Results/agent_runs/*` before acting.

For a learn-and-update audit, the task graph must also declare the round
boundaries:

```text
round 1 source slice:
round 1 doc patch target:
round 2 source slice:
round 2 doc patch target:
round 3 source slice:
round 3 doc patch target:
do-not-adopt guardrails:
```

Keep the main agent on the critical path. Delegated work should be independent
and material, not a copy of the same work the main agent is doing.

For long tasks, convert the graph into a task queue. The queue is the work
source; chat memory is not the work source. A task is ready only when it has:

```text
task_id:
task_class:
project_goal:
canonical_task_goal:
conversation_objective:
objective:
read scope:
write set:
owner role:
accountable_owner:
dependencies:
acceptance check:
definition_of_done:
non_goals:
required_evidence:
reviewer role:
appetite:
circuit_breaker:
checkpoint_plan:
escalation_conditions:
next task on success:
next task on blocker:
```

An owner agent may continue taking the next ready task in its assigned queue
without waiting for a new user message, provided the next task is inside the
same write set and does not require new approval. If the next task changes
write ownership, touches external paths, requires GUI/login/license action, or
needs destructive Git/history operations, the owner must stop and report the
blocker.

Queue-pull owner contract:

```text
queue_source:
claim_rule:
max_items_per_checkpoint:
checkpoint_cadence:
terminal_event_required:
reviewer_role:
stop_on_scope_change:
stop_on_missing_evidence:
stop_on_permission_or_gui_requirement:
```

The owner may process the next ready item only when it remains inside the same
declared read/write scope and acceptance gate. Otherwise it must return a
handoff instead of silently expanding its task.

Sub-agent communication topology:

```text
main agent
  -> child owner
  -> reviewer owner
  -> git owner
  -> optional grandchild workers
```

Sub-agents cannot be assumed to communicate with each other. All cross-agent
coordination, review routing, and follow-up instructions must go through the
main agent or a single explicitly assigned parent owner. If a child owner uses
grandchild workers, the main agent must still receive the parent owner's
checkpoint, decide the next instruction, and distribute any reviewer feedback.
Do not leave one agent waiting for another agent's result unless the dependency
is recorded in the ledger and the main agent owns the handoff.

Nested delegation is allowed only when all of these are true:

```text
max_depth has been intentionally enabled for the session:
the parent owner has a queue and WAL:
child agents are read-only or have disjoint worktrees/write sets:
the parent records child WAL locators:
the main agent remains responsible for final integration:
```

Default to main-agent chaining instead of uncontrolled nested delegation. If a
tool/runtime does not support nested subagents, split the queue from the main
agent instead.

Provider-specific note: Codex subagents are explicitly spawned by the main
agent. Do not assume Claude-style automatic subagent routing. Runtime spawn
arguments such as `reasoning_effort` are not the same as persistent Codex config
keys such as `model_reasoning_effort`; mark unverified config keys as
unsupported until checked against official docs for the installed version.

Codex subagents are not the same thing as durable workers. In this project they
are short-lived capability calls: useful for a bounded audit, focused research,
or a one-batch execution, but not reliable as Git departments, permanent
reviewers, test daemons, secretaries, or cross-turn supervisors. They have
isolated context and must return evidence to the main agent; they cannot be the
source of truth for task state.

Visible department conversations are also not the same thing as internal
Codex subagents. If the user asks to send work to `MoSim｜DevOps 发布部`,
`MoSim｜ROS2感知定位与规划运行部`, `MoSim｜MWORKS动力学与控制验证部`, or another visible
department thread, do not use an internal `spawn_agent` call and claim the
department received it. Dispatch to the real visible thread with
`codex exec resume <thread_id>` and capture the last response with
`--output-last-message`. Internal subagents may still be used for one bounded
private analysis slice, but they are not acceptable evidence of department
communication.

PMO may also create a new visible department thread when no existing reusable
thread matches the work and the task needs durable specialty context across
turns. Current lifecycle authority is restricted to user-approved mainline
threads. Approved mainline threads are `MoSim｜主线 PMO`
(`019e9868-83ea-70f0-92c5-a3a408bd78c6`) and `MoSim｜CoAgent运维平台`
(`019e9bc1-ea9f-7102-b41a-4ef9b2308992`). These mainline threads may call
native Codex visible-thread tools such as `list_threads`, `read_thread`,
`send_message_to_thread`, `create_thread`, `fork_thread`, `set_thread_title`,
and `set_thread_archived` when those tools are exposed in the current session.
They may also create, update, view, or delete Codex App automations through the
native `automation_update` tool after checking that the task is recurring and
has a safe scope. Other visible departments may recommend a new department or
write a blocker packet, but they must not create, fork, rename, archive, create
automation tasks, or delegate creation of visible threads.

The earlier `MoSim｜CoAgent运维平台`
(`019e74d1-72fa-7d33-8783-90584035ae92`) was created through an older
WSL/non-App-native conversation path, lacked reliable native thread/automation
tool surfaces, and was deleted by the user on 2026-06-06. Do not route new
native thread or automation work to it; dispatch those tasks to
`MoSim｜CoAgent运维平台` and recover history only from project packets/docs.

Recurring work does not justify duplicate departments. If an existing
App-native visible department needs scheduled checks or wakeups, keep that
department and configure native Codex App automation against it. As of
2026-06-06, the gateway, context, open-source probe, and open-source learning
departments were replaced with App-native visible threads after their reusable
old conversation content was landed into canonical project documents. Use the
current active IDs and status values in
`CoAgent/dispatch/department_threads.json`; old IDs are superseded and must not
receive new work. The former `MoSim｜微信网关运维部` route is archived after the
email-only notification switch and must not receive periodic checks, no-op
probes, canaries, or gateway work unless PMO/user explicitly restores WeChat
diagnosis through a new bounded task.

If a mainline thread cannot see the native thread or automation tools in its
current Codex surface, it must first search the tool surface (`tool_search`
querying for `create_thread`, `send_message_to_thread`, `read_thread`, and
`automation_update`). If the native tool is still unavailable, it must write a
blocker packet with the requested operation, intended target thread or
automation definition, and why GUI clicking/private App state edits were not
used.

Visible departments are not passive prompt sinks. When a department receives a
non-trivial task packet, it owns a department-local goal and must plan the work
before execution. The prompt must use this standard local-planning block rather
than an ad hoc reminder:

```text
Before any non-trivial business work, derive and record a department-local
task graph. This is a planning requirement, not a requirement to use at least
one sub-agent.

department_local_goal:
critical_path_steps:
parallelizable_slices:
subagent_plan: used | available_but_not_useful | unavailable | unsafe
subagent_plan_reason:
subagents_used:
verification_gates:
manual_review_or_blocker_triggers:
```

The department-local goal should be short and bounded to the task packet. Do
not let a broad documentation, skill, MCP, workflow, or architecture cleanup
become the reason the department does not run the next declared engineering
gate. If a reusable-rule problem is found while dispatching, record the fix as
parallel/follow-up work unless the current task would be unsafe or invalid
without it.

`subagents_used` may be empty, but only after the department records the
explicit `subagent_plan` decision and a concrete reason. If the department uses
disposable Codex sub-agents, each entry must include objective, read scope,
write scope or read-only status, stop condition, returned evidence path, and
whether the department accepted or rejected the result. A department may use
such sub-agents only for bounded research/review/execution slices supported by
its current tool surface. It must not use sub-agents as durable queues, as
hidden department replacements, or as a way to create/rename/archive visible
threads. PMO remains responsible for cross-department routing, visible thread
lifecycle, and final integration.

Dispatch-packet rule: PMO must include an explicit local-planning and
sub-agent-decision clause for every non-trivial visible-department assignment.
If the work has an independent read-only audit, reference comparison, file-level
review, or disjoint write slice, the target department should use a disposable
sub-agent when its runtime exposes one. If it cannot use one, the packet and
return/blocker should record `available_but_not_useful`, `unavailable`, or
`unsafe` with the concrete resource or coupling reason. PMO must not phrase
this as "use at least one sub-agent"; the requirement is to plan the task graph
and make the sub-agent scheduling decision consistently.

When PMO dispatches MWORKS R1/R2 work or a disposable MWORKS sub-agent that
needs screenshots, include the current screenshot skill boundary: ordinary
simulation/check/layout phase evidence should prefer the DPI-aware
`capture_window_background.ps1 -RestoreMinimized -Maximize` route against the
real main Sysplorer/MWORKS window, while activation/login/license/
authorization and complete GUI acceptance still require foreground or
maximized target-window visual evidence. PMO must not force every child thread
to rediscover helper/proxy windows, DPI scaling, or the `PrintWindow` limits.
If a MWORKS task produces a graphical simulation, wiring/layout, Smart Layout,
result viewer, or animation artifact that needs audit, route the review to
MWORKS R2 as a bounded review task. The expected output is the screenshot plus
observations, not a path-only report.

Department execution and acceptance rule: after planning, the visible
department owns the task execution inside the declared read/write scope. It must
run the task-specific infrastructure preflight before business work and must
stop promptly with a blocker when that gate fails. It must not continue by
generating unrelated JSON, tuning solvers, changing parameters, retrying
runtime/model steps, or filing a completed packet that only proves control-plane
activity. Completed packets must contain domain engineering evidence matching
the task type: MWORKS `.mo`/`package.mo`, `check_model`, `SimulateModel`,
native result/`.msr`, metrics, diagram/layout screenshots, or wiring
observations; ROS2 topic/process/source-window/log/runtime evidence; UE
source/static/build/runtime evidence according to scope; or Blender/UE asset,
rendered review, material-manifest, or visual-review evidence for asset work.
JSON packets, ledger rows, and progress notes are not engineering output unless
the task is explicitly diagnostic/rule-sync/preflight/dispatch-surface/static
inventory work. PMO must reject completed returns that lack the declared
engineering outputs, omit the local plan/sub-agent decision, or convert a real
blocker into completed metadata.

Before PMO integrates a non-trivial visible-department return/blocker packet,
run the generic department contract gate:

```powershell
python Scripts\quality\check_department_packet_contract.py `
  Results\agent_packets\returns\<request_id>.json
```

Use the blocker path instead when the department returns a blocker. This gate
checks the department-local goal/task graph, `subagent_plan` decision,
`actual_engineering_outputs`, and `claim_boundary`. It is a shared backstop
only; domain gates still apply, especially `check_mworks_live_gate.py` for
MWORKS/Sysplorer/Syslab work.

Domain dispatch templates:

```text
ROS2/RViz2/FAST-LIO:
  preflight: ROS2 environment/source status, stale MoSim/FAST-LIO/planner
    processes, source-window/topic contract, forbidden topics, probe_count
    budget, cleanup plan
  return evidence: source-window/topic stamps, rates/counts, FAST-LIO/planner
    evidence when in scope, forbidden-topic absence, cleanup_summary,
    claim_boundary
  stop: no-rerun/existing-evidence-only tasks, timestamp regression, callback
    loop-back, missing required topics, stale cleanup failure, exhausted
    one-probe budget

UE experiment console / scene interaction:
  preflight: classify source-static, build, editor/runtime, or manual-review
    scope
  return evidence: source/schema edits and tests, build/log proof, runtime
    echo/transport proof, or review screenshots/packets
  stop: missing build/runtime evidence, treating schema/registry JSON as
    runtime ack, teleport/pose override/global-truth planner shortcut

Sunray150 asset / PBR:
  preflight: DAE-derived Blender asset availability, component identity,
    material source evidence, UV/material-slot limits, planned review renders
  return evidence: Blender/UE asset edits, material manifests, rendered
    close-ups/contact sheets, PBR texture/map evidence, or failed-review images
  stop: unclear part identity/license/UV/export/review issue, Base Color-only
    coloring, or any attempted geometry/dynamics/extrinsic/controller/planner
    change outside scope
```

Current MWORKS split: `MoSim｜MWORKS动力学与控制验证部-R1`
(`019e9be5-334b-76b1-93f9-8b02caebf376`) is the primary MWORKS mainline route
for dynamics/control/model-integration evidence. `MoSim｜MWORKS动力学与控制验证部-R2`
(`019e9999-b0d3-7682-bccd-faef08fcf1df`) is an auxiliary route for model
organization, graphical simulation interface completeness, connection
correctness, line-layout/readability, diagram hygiene, and graphical/result
review using the approved screenshot route. R2 had historical
dispatch-surface instability, so its first business task requires a bounded
synchronization/no-op validation return packet; until then, use R1 for
production MWORKS work. Historical packets may preserve older R2 labels for the
current R1 thread, but current routing follows `CoAgent/dispatch/department_threads.json`.

Mainline ownership rule: `MoSim｜主线 PMO` and `MoSim｜CoAgent运维平台` are
coordination owners, not the best specialist for every domain problem. Route
domain incidents to the responsible visible department first whenever its
thread surface is healthy. If the responsible department is listable/readable
but cannot start a turn, the mainline owner records the dispatch failure,
writes the initial blocker, routes bounded diagnosis/recovery to CoAgentOps,
and continues unrelated or critical-path business work through healthy
surfaces. PMO does not own the department's no-op/list/read/send/codex-exec
diagnosis ladder and must not use the failed department as an accident-sample
worker. The only exception is when CoAgentOps itself is the failed surface; in
that case PMO executes the documented dual-mainline recovery. Do not leave
urgent work waiting solely because the specialist thread is stuck, and do not
permanently bypass the specialist after CoAgentOps restores it.

Default model/effort rule: normal mainline, visible department, sub-agent,
thread creation, department dispatch, automation, and spawn calls should request
`model=gpt-5.5` plus `thinking=high` or the tool-equivalent
`reasoning_effort=high` whenever the current native surface accepts explicit
settings. Do not wake healthy existing threads merely to mutate settings.
Dead-thread recovery no-op probes omit model/thinking overrides unless the
specific recovery task is testing settings update behavior.

Human review artifact rule: if a task produces review images, videos, native
MWORKS result viewers, `.msr` assets, or other user-facing audit artifacts, PMO
must open/display the artifact directly while the user is online or send a
concise sparse email review prompt when direct display is not practical.
WeChat is reserved for explicit WeChat retry or gateway-diagnosis scope. Do
not treat a pasted path as sufficient review delivery. Exact paths stay in
result packets and project evidence; the user-facing prompt stays short and
Chinese.

A new department thread is appropriate for recurring ownership such as
ROS2 runtime integration, MWORKS dynamics evidence, UE experiment-console
implementation, PX4/SIL-HIL integration, evidence/report quality, or gateway
operations. It is not needed for a small one-off read-only audit that can be
handled by a disposable subagent.

Before creating or dispatching to a department, classify the work:

```text
one-shot subagent:
  bounded private slice, one result, no durable context expected
existing visible department thread:
  recurring specialty already exists and is not blocked by another active task
new visible department thread:
  recurring specialty is missing, the task will need checkpoints/reuse/manual
  inspection, and a clear department charter can be written now
```

Decision table:

| Use Surface | Choose It When | Required Evidence | Do Not Claim |
|---|---|---|---|
| Current thread | The task is inside the current thread's owner boundary, has a small write set, and can be completed with local checks | Changed files, local verification, result/blocker packet when durable state matters | Do not claim another department reviewed or received the task. |
| Short-lived subagent | The work is a bounded research/review/execution slice, can return one structured result, and does not need durable visible context | Subagent objective, read/write scope, stop condition, returned evidence, acceptance/rejection by parent | Do not call it a visible department, durable owner, Git/test daemon, or cross-turn supervisor. |
| Existing visible thread | The task needs durable specialty context, repeated follow-up, manual inspection, or owner accountability and the thread is in the current allowlist registry | Target thread id, request packet, expected return/blocker path, visible delivery evidence, result/blocker packet | Do not use an internal subagent or local packet and claim the visible thread received it. |
| New visible thread | No current allowlist thread fits and the task has recurring ownership, a clear charter, stop condition, and PMO/user authority | PMO-created thread id, registry update, role prompt, return contract, user-visible confirmation when required | Do not let non-PMO departments create, fork, rename, archive, or delegate creation of visible threads. |
| `codex review` or review subagent | The need is an independent bounded review gate, especially docs/code risk review | Findings with file/line evidence and owner acceptance/rejection | Do not treat review as implementation or as a standing test department. |
| CoAgent packet/runtime glue | The need is MoSim-specific task/result/blocker/evidence/recovery bookkeeping | Packet path, schema/gate result, ledger/status update | Do not add runtime/transport/schema machinery when a native Codex surface already covers the need. |

Practice rule: every dispatch packet must explicitly state the selected surface
and why the alternatives were not used. If the selected surface is not a
visible thread, do not include `target_thread_id` for a durable department. If
the selected surface is a visible thread, do not replace it with a hidden
subagent and call the task dispatched.

Manual-intervention rule: when a required external document, webpage, login,
license, GUI permission, or browser-only source cannot be accessed after the
documented local route, write a blocker packet and send one sparse email
blocker notification through `Scripts/agent/send_gateway_email_alert.py`.
There is no active WeChat gateway operations route. `MoSim｜微信网关运维部`
(`019e9c7d-a8bd-7dd1-ad94-6feef5a07e9c`) and `MoSim｜WechatCodex`
(`019e8358-86b4-7070-8fd6-a2b4f4d2af97`) were deleted by the user on
2026-06-08 after the email-only notification switch. They are historical
evidence only: do not dispatch, patrol, no-op, recover, or treat absence as an
outage unless the user explicitly restores WeChat diagnosis with a new scoped
route. Use sparse email for blockers and intervention notices.

Email body-format rule: send short Chinese status text only. Do not include
concrete English file names, long paths, JSON/log names, or raw evidence lists
in the email body; keep those locators in result/blocker packets, ledger
entries, and evidence files. Routine completion can use `【MoSim 进度】`.
Manual intervention, incident, auth/license, GUI crash, or dead-thread
messages should start with an obvious alert header such as
`!!! MoSim 需要人工介入 !!!`. If WeChat is explicitly requested, apply the same
body-format rule to the WeChat body.

When manual thread creation/coordination is useful, PMO should send a sparse
email note with its own thread id and the proposed department charter so the
user can inspect the thread creation. If the next action is clear, PMO may
create or dispatch directly using the available thread-management tooling, then
record the new thread id in `PROGRESS.md` and
`Docs/Workflows/agent_task_ledger.md`.
Do not repurpose a long-running department that already owns an active task;
currently `019e74de-a452-7a50-99e7-ca9a247b32f1` is reserved for its existing
long work unless the user explicitly redirects it.

If PMO is unsure which visible-thread command or thread-management route to
use, it may ask `019e0198-a041-77f1-84d0-c5524bfd4b81`
(`MoSim｜四旋翼控制系统设计`) for an architecture/coordination opinion or for a
thread charter. That thread must return advice or a blocker only; PMO performs
the actual visible-thread operation from the context where thread-management
tools are exposed.

Any PMO visible-thread creation prompt must include PMO's origin thread id, the
desired department title, role prompt, project root, communication mechanism,
expected return path, and forbidden actions. It must address the newly-created
thread as the department itself: use "你就是该部门线程，请初始化自己", not "请创建
线程". Never place a visible-thread creation request inside the initial prompt
of another newly-created thread.

Known visible department dispatch command pattern:

```bash
codex exec resume <department_thread_id> \
  -m gpt-5.5 \
  -c model_reasoning_effort='"high"' \
  --dangerously-bypass-approvals-and-sandbox \
  --output-last-message /tmp/<task_id>_result.txt \
  - < /tmp/<task_id>_packet.txt
```

Use `codex_app.send_message_to_thread` only as a convenience path. If it returns
an app/agent-loop internal error but `read_thread` still works, treat this as
an App forwarding failure. PMO must not then run its own `codex exec resume`
or no-op delivery ladder against the failed department. PMO writes the initial
blocker, routes the incident to CoAgentOps, and continues unrelated work
through healthy surfaces. Only CoAgentOps performs bounded delivery/no-op
diagnosis for a failed department, except when CoAgentOps itself is the failed
surface and PMO must execute the documented dual-mainline recovery.

`waitingOnApproval` is a separate branch. If `read_thread`, Codex App UI, or
the target department state shows `waitingOnApproval`, pending approvals, or a
permission prompt, do not treat the condition as a normal missing-packet stall
or dead-thread solely from elapsed time. First classify it as
`approval_pending_or_ui_blocked`, and when practical use Windows MCP
foreground/screenshot evidence of the Codex App or target thread to confirm
whether a manual permission prompt is visible. Confirmed approval surfaces
should be recorded in the blocker/ledger with `approval_state=pending` and
`error_kind=permission` or `approval_denied` as appropriate. Business dispatch
to that department stays paused until the user or an approved route decides
the prompt. Do not loop no-op probes, trigger Codex++ restart, or create a
replacement thread just because the approval prompt prevented the expected
packet from being written.

Elapsed time is only a stale-response trigger. If a short dispatch has no
final reply or expected packet after about five minutes, inspect the target
with `read_thread` and packet lookup before classifying it. Keep the target
`busy_in_progress` when the latest turn shows agent output, tool activity,
file changes, or checkpoint commentary. Use
`dispatch_surface_or_agent_loop_failure` only for unreadable threads, failed
start-turns, agent-loop errors, completed turns with no agent output or
expected packet, or inProgress turns with no readable activity beyond the
bounded validation window.

Provider or review UI is the same control-plane branch, not a dead-thread
shortcut. If the visible thread or user/operator screenshot shows a provider
gateway error such as `502 Bad Gateway`, reconnect banner, generated-file
review pending state, `审核`/review button, approval button, or similar manual
review surface, classify it as `provider_gateway_or_pending_review` or
`approval_pending_or_ui_blocked`. Record the UI state and stop the affected
business dispatch until it is cleared or explicitly approved. Do not treat a
provider/review surface as proof of MWORKS/ROS2/UE business failure, do not
run repeated no-op probes while the UI is waiting for review, and do not
trigger Codex++ restart or replacement unless a separate start-turn/agent-loop
failure persists after the provider/review surface is cleared.

If a visible department is readable but cannot receive messages, especially
with `failed to update thread settings: internal error; agent loop died
unexpectedly`, `failed to start turn: internal error; agent loop died
unexpectedly`, or user-side `Error submitting message`, treat it first as a
visible-thread dispatch-surface incident, not as a business-domain failure. PMO
must record a blocker packet and route a bounded diagnosis/recovery task to
`MoSim｜CoAgent运维平台` before replacement is considered. The diagnosis should distinguish at least these surfaces:
readability, cross-thread native delivery, in-thread UI composer/manual submit,
settings/model override, and automation/thread-wakeup delivery. If the critical
path must continue before diagnosis finishes, PMO may continue the work locally
or explicitly authorize a replacement in parallel, but the replacement packet
must first identify which old-thread reusable content has been landed in
canonical docs, result/blocker packets, or this ledger. Do not assume the
thread is permanently dead: a later
cross-thread no-op healthcheck may succeed after the App/agent-loop state
recovers. That is only partial recovery if the user still sees `Error
submitting message` from inside the target thread's own UI composer. A
partially recovered thread remains quarantined until PMO explicitly approves a
bounded CoAgentOps validation ladder; production dispatch stays blocked or on
an explicitly authorized replacement. After the user repairs, archives, deletes, or PMO
reclassifies the old thread, update `Docs/Workflows/agent_task_ledger.md` and
`PROGRESS.md` with the exact outcome and never dispatch production work to the
old thread id unless PMO has explicitly restored it.

PMO must not reuse the failed visible department as an "accident sample" worker
after the dispatch-surface failure is observed. The only allowed PMO-side work
before CoAgentOps classification is: write the initial blocker, notify/route the
incident to CoAgentOps, and continue unrelated business work through healthy
surfaces. Any additional no-op/list/read/send diagnosis, restart decision, or
replacement recommendation belongs to CoAgentOps unless the user explicitly
overrides this ownership for that incident.

If CoAgentOps confirms the same start-turn/agent-loop failure after bounded
list/read/no-op/metadata/no-op diagnosis, the next default action is to write a
durable blocker/recovery packet, attempt one sparse email notification,
record the audit result, and restart Codex++ through the
authorized manager after only a short manual-restart window, then wait for a
post-restart no-op validation. The notifications let an online user restart
faster; they do not create an indefinite approval wait. Do not keep
retrying the same failed delivery surface, and do not create a replacement conversation by default. A replacement
requires explicit PMO/user approval, repeated failed restart recovery, or a
critical path that cannot wait.

Heartbeat fail-close rule: after such a recovery packet exists, any PMO or
CoAgentOps heartbeat that sees the packet still waiting for notifications,
restart, post-restart validation, or reporting `still_quarantined` must treat
that as an active P0 incident. It must not summarize the item as ordinary
pending work, return `DONT_NOTIFY`, or run lower-priority optimization. The
heartbeat must execute the next authorized recovery step. For
notification/restart-pending dead-thread recovery, that means sending a sparse
email alert, recording the audit, and triggering the authorized Codex++
restart route after a short manual-restart window if no explicit
deferral arrives. It writes a blocker/request packet with `NOTIFY` only
when a required tool/surface is unavailable, the notification/restart action
fails, or an explicit PMO/user-approved deferral packet pauses this fail-close
behavior.

The user-authorized Codex++ restart surface for this case is:

```text
D:\Program Files\Codex++\codex-plus-plus-manager.exe
```

Use it only after a dead-thread blocker has been written and one sparse email
notification has been attempted. If email is unavailable, record the failure
before continuing. If notification is unavailable,
or if notification is sent and no explicit manual deferral or visible
intervention is available after a short window, CoAgentOps may trigger the
Codex++ restart action through this manager. This will terminate the current
conversation, so any recovery attempt must leave a durable packet first and rely
on the 10-minute CoAgentOps heartbeat or the next healthy PMO interactive turn to resume validation
after Codex++ comes back. The post-restart gate is still a no-op delivery check
plus routing-status classification; restart alone is not task completion. In
normal dead-thread recovery, validated restart recovery keeps using the same
visible thread id instead of creating another department conversation.

Recovery validation must distinguish execution-surface recovery from task
completion. A previously blocked thread is restored at the
`thread_execution_surface_restored` layer when the same visible thread starts a
new turn and produces agent output, an expected packet, or an explicit
user-requested ACK. Exact no-op text is still valid when that is the stated
probe, but it is not the only recovery proof once the target clearly executes.
Native list/read/send success without agent output remains insufficient. A
restored execution surface only reopens routing; it does not prove the
department completed the patrol, wrote the expected return/blocker packet, or
delivered any MWORKS/ROS2/UE engineering evidence.

Observed restart behavior: on 2026-06-06, a Codex App crash/restart changed
several readable-but-unsendable threads back into no-op-sendable threads. This
supports the working diagnosis that many "dead thread" events are caused by
transient App or agent-loop lifecycle state across the forwarding/start-turn
surface. It is not enough evidence to claim the internal root cause, and it is
not enough to move production work back to an old thread. PMO should classify
post-restart success as `partial_recovery` until cross-thread no-op,
settings-override no-op, user UI composer, and any required heartbeat/wakeup
surfaces are all validated for that specific thread.

Do not launch formal department tasks through unattended background
`codex exec resume` until the project has a verified visible-delivery and
controlled-stop workflow. Background CLI dispatch can leave the target
conversation running or visually stale in Codex App, and PMO cannot rely on it
as durable department communication without a returned packet and user-visible
state. If both App forwarding and safe CLI dispatch are unavailable, mark the
task `dispatch-blocked-tool`, keep the task packet ready, and ask the user to
open/send the task manually or keep the work PMO-local.

Use a 60 second outer timeout only for probes and short packets. Formal tasks
must either run in a user-visible department conversation or be executed
locally by PMO with explicit ledger ownership; do not start hidden long-running
department agents as a workaround for a broken dispatch surface.

For long Git or large-tree tasks, split the task into path-scoped batches and
require the department owner to return a checkpoint/result packet instead of
waiting on a full-tree scan. Communication is proven only when the visible
thread returns a department result. The first accepted DevOps communication
probe returned:
`DEVOPS_COMM_OK｜received_from_main｜task_id=comm-probe-20260526-01`.

### Cross-Thread Request / Return Protocol

Codex App cross-thread send is a one-way task delivery surface. It is not a
request/response RPC channel, and it does not guarantee that the target
thread's reply is propagated back to the origin thread. Do not treat a visible
App forward banner such as "sent from another conversation" as task completion.

Every cross-thread request must carry an explicit return contract. This applies
to every department, not only PMO. The department that sends the request must
identify itself with both a human-readable title and the concrete visible
thread id so the target department can return the result to the right origin.

```yaml
request_id: <stable unique request id>
origin_thread: <origin visible thread title>
origin_thread_id: <origin visible thread id>
target_thread: <target visible thread title>
target_thread_id: <target visible thread id>
responsible_department: <department accountable for completion or blocker>
task_id: <ledger/runtime task id>
expected_return_path: Results/agent_packets/returns/<request_id>.json
blocker_return_path: Results/agent_packets/blockers/<request_id>.json
definition_of_done: <observable completion condition and evidence required>
checkpoint_deadline: <time or condition for first packet>
```

The target thread must write a result packet or blocker packet under the project
tree. A chat reply alone is not a durable return surface.

Result packets go here:

```text
Results/agent_packets/returns/<request_id>.json
```

Blocker packets go here:

```text
Results/agent_packets/blockers/<request_id>.json
```

Minimum packet schema:

```json
{
  "request_id": "DEVOPS-GIT-SPLIT-20260606-001",
  "task_id": "DEVOPS-GIT-SPLIT-20260606",
  "origin_thread": "MoSim｜主线 PMO",
  "origin_thread_id": "019e9868-83ea-70f0-92c5-a3a408bd78c6",
  "target_thread": "MoSim｜DevOps 发布",
  "target_thread_id": "019e74de-a452-7a50-99e7-ca9a247b32f1",
  "responsible_department": "DevOps 发布",
  "status": "completed",
  "summary": "Finished inventory-only Git split plan; no files staged.",
  "changed_files": [],
  "evidence_paths": [
    "Results/agent_packets/returns/DEVOPS-GIT-SPLIT-20260606-001.json"
  ],
  "next_action": "PMO review split plan and approve first path-limited commit batch.",
  "needs_user_action": false,
  "created_at": "2026-06-06T00:00:00+08:00"
}
```

Allowed `status` values are `completed`, `blocked`, `failed`, and
`review_required`. The target department must first try to resolve issues
inside its own scope: inspect its own logs, docs, tools, task state, and
previous packets before escalating. If it cannot solve the issue without
external action, it writes a blocker packet back to the `origin_thread_id` and
records the responsible surface clearly. If the packet is missing by the
checkpoint deadline, the origin department opens a blocker against the target
department/thread. PMO may audit or integrate the result, but PMO is not the
only owner of return handling. The responsibility belongs to the target
department until it writes a valid return or blocker packet. Sparse email is
the default alert channel for completion, blocker, or manual review; it is not
the source of truth and not the return channel. WeChat remains diagnostic or
explicit-use only.

Codex App / VSCode visibility and CLI communication use different metadata
contracts. Keep WSL-side thread metadata CLI-compatible for communication:
`source=cli`, `thread_source=user`, and lowercase WSL `cwd`. Keep Windows App
metadata UI-compatible for display: `source=vscode`, `thread_source=vscode`,
and canonical `/mnt/c/Users/HP/Desktop/MoSim` `cwd`. If both sides are forced
to `vscode`, `codex exec resume` may fail with `unknown thread source: vscode`.
If both sides are forced to `cli`, the department conversation may disappear
from the App/VSCode task list. After each visible-thread dispatch, copy or
materialize the updated rollout to the Windows session store and update the
Windows index/state preview; do not mutate the WSL source away from `cli/user`.
Accepted regression probe:
`DEVOPS_VISIBLE_ACK｜task_id=DEVOPS-VISIBLE-PROBE-20260526-03`.

Durable department behavior must be implemented by MoSim-owned infrastructure:
a persistent task queue, append-only event stream, path/security hooks, explicit
claim/heartbeat/terminal events, and human-readable recovery surfaces in this
workflow, `PROGRESS.md`, and `Docs/Workflows/agent_task_ledger.md`. Subagents may
help inspect or execute one queue item, but the queue and state machine are not
owned by the subagent runtime.

The first project-local implementation is
`CoAgent/runtime/mosim_agent_runtime.py`. It is deliberately a local state tool:
SQLite task queue plus JSONL event stream. It does not call model APIs, does not
spawn Codex, and does not open GUI tools. Use it to make long work recoverable
before assigning one-shot Codex subagents or manual workers.

Project-owned architecture and migration status live under `CoAgent/`.
Use `CoAgent/docs/architecture/ARCHITECTURE.md` for the layered design, and
`CoAgent/docs/research/REFERENCE_PROJECT_INDEX.md` before scanning large external repos under
`References/`.

Minimum runtime commands:

```bash
python CoAgent/runtime/mosim_agent_runtime.py create \
  --objective "Review current UE MCP design" \
  --role ArchitectureReviewer \
  --read-scope Docs/Skills/Unreal \
  --write-scope Results/agent_runs \
  --acceptance "structured review event recorded" \
  --stop-condition "done, blocked, or failed with evidence"

python CoAgent/runtime/mosim_agent_runtime.py claim --owner ArchitectureReviewer
python CoAgent/runtime/mosim_agent_runtime.py checkpoint --task-id <id> --actor ArchitectureReviewer --summary "read first slice"
python CoAgent/runtime/mosim_agent_runtime.py complete --task-id <id> --actor ArchitectureReviewer --summary "review complete"
```

Runtime state aliases exist during migration. Treat `queued` as `ready`,
`claimed`/`running` as `working`, `done` as `completed`,
`done_with_concerns` as `review_required`, and `cancelled` as `canceled`.
New documentation should use the canonical state names.

User-facing task UI:

Use the VSCode/Codex App task/conversation list as the front end. The user may
manually create/open conversations, but PMO is also allowed to create or dispatch
visible department threads when the task graph calls for durable specialty
ownership. The main agent provides a standard task packet for each conversation,
or dispatches it with `codex exec resume <thread_id>` when the target visible
thread id is known, and records the task in the MoSim runtime/ledger. Do not
build a separate web dashboard unless the VSCode/Codex task UI becomes
insufficient.

Current operational boundary: multi-conversation scheduling is PMO-led and
allowed only through visible threads with explicit return contracts. The main
agent owns packet preparation, new-thread charter quality, result import,
ledger updates, integration, and automatic sparse email notifications after
completion, review-required, blocker, or incident states. CoAgent helpers may
prepare envelopes, validate packets, diagnose visibility, and import results,
but they are not a mandatory dispatch center. Do not claim autonomous dispatch
is working unless the target conversation is visible or successfully created
and a result/blocker packet has been returned through the approved transport.

Completion notification rule:

```bash
python CoAgent/result_router/result_router.py import \
  --packet Results/agent_packets/<task_id>.yaml \
  --notify-email \
  --send-email
```

For `canonical_status=completed`, `--notify-email` generates a
`completion_notification` packet and routes it through
`Scripts/agent/send_gateway_email_alert.py` or the current project email
adapter. This is required even when
`requires_human_review=false`, because task completion is the user's unified
out-of-band progress signal while multi-dialog scheduling remains manual.
The generated email body must stay Chinese and compact; evidence paths remain
inside the packet and are not copied into the human-facing message. Use
WeChat notification flags only for explicit WeChat retry or gateway-diagnosis
tasks.

Conversation classes:

| Class | Owner | Purpose | Examples |
|---|---|---|---|
| Primary conversation | MainAgent | User dialogue, goal, integration, final decisions | current WSL-backed project thread |
| Department conversation | Department owner | Recurring work inside one broad responsibility | `MoSim｜DevOps 发布`, `MoSim｜ROS2感知定位与规划运行部`, `MoSim｜MWORKS动力学与控制验证部` |
| Task team | PMO + parent department | One long-running task containing multiple scoped visible conversations with shared canonical goal | `Sunray150 参数识别`, `UE Fab 场景导入` |
| Scoped task conversation | Task team owner | One bounded slice inside a long-running task team | log audit, estimator implementation, verification slice |
| One-shot subagent | MainAgent or parent owner | Bounded research/review/execution slice returning one result | one repo audit slice, one doc review |

Use a task team instead of a one-shot subagent when the task:

```text
will take multiple turns or manual review cycles
needs to preserve technical context across many messages
has iterative user feedback
requires independent progress visibility in Codex App
would fail if treated as a single disposable subagent call
```

The PX4-log-based Sunray150 parameter identification task is the canonical
example: it should be a task team under the Project Department, not a one-shot
subagent, because it needs literature/code audit, log-field requirements,
user-provided data, estimator design, MWORKS parameter mapping, and
verification across multiple visible conversations.

Each scoped task conversation inside a task team must start from a compact
context pack rather than raw accumulated chat. Use
`CoAgent/docs/research/LEARNING_STRATEGY.md` for the current context-pack fields. At minimum,
include:

```text
task_id:
parent_goal:
owner_department:
objective:
read_scope:
write_scope:
current_state:
relevant_decisions:
known_blockers:
required_tools:
acceptance:
stop_condition:
result_packet_path:
knowledge_search_queries:
```

After the task returns a result packet, summarize useful context into runtime
events, run summaries, knowledge sources, workflows, or progress notes, then
release the task-specific conversation context. Do not let an old transcript
become the only memory of why a technical decision was made.

Current CoAgent implementation is frozen at the design-review boundary. Before
adding new runtime, transport, automation, department, or packet-schema work,
confirm the checklist in
`CoAgent/docs/decisions/coagent_design_discussion_packet.md`. Use
`CoAgent/docs/research/THREE_ROUND_STUDY_AND_DISCUSSION.md` as the supporting
evidence packet.

Generate the current project-owned format with:

```bash
python CoAgent/context/context_pack.py --task-id <id>
```

For a recoverable handoff, write it under `Results/context_packs/`:

```bash
python CoAgent/context/context_pack.py --task-id <id> --output Results/context_packs/<id>.md
```

Conversation communication protocol:

```text
MainAgent responsibilities:
  1. Keep the top-level goal accurate.
  2. Decide whether work stays local, goes to a department conversation, becomes
     a dedicated task conversation, or is a one-shot subagent call.
  3. Create or update the durable task record directly when the task needs one.
  4. Produce one complete task packet for the target visible conversation, or
     dispatch it through the known visible thread id.
  5. Continue the main critical path without waiting unless the result blocks it.
  6. Parse returned result packets, update runtime/ledger, and integrate or reject.

CoAgent support-tool responsibilities:
  1. Generate task packets, context packs, and result/blocker packet templates
     when PMO needs a durable artifact.
  2. Maintain optional task tickets, conversation registry, and department
     status views when a task is large enough to need them.
  3. Diagnose visible-thread metadata drift and transport failures.
  4. Validate and import result packets for PMO integration.

Responsible-thread documentation responsibilities:
  1. Record directives, decisions, corrections, and manual-review outcomes.
  2. Patch durable docs after stable decisions.
  3. Run or request docs-quality review.
  4. Avoid becoming the global dispatcher or hidden implementation worker.

User responsibilities:
  1. Open the Codex conversation manually when asked.
  2. Paste the task packet exactly.
  3. Keep the conversation visible for manual progress inspection when desired.
  4. Paste the returned result packet back to MainAgent when integration is needed.
```

Task packet template:

```text
[MoSim Task Packet]
task_id:
request_id:
origin_thread:
origin_thread_id:
target_thread:
target_thread_id:
role:
objective:
native_surface_gate:
  selected_native_surface:
  surface_selection_reason:
  rejected_surfaces:
  worktree_required:
  worktree_decision:
read_scope:
write_scope:
allowed_actions:
forbidden_actions:
acceptance:
stop_condition:
required_checks:
expected_return_path:
blocker_return_path:
return_format:
  summary:
  files_changed:
  evidence:
  blockers:
  next_recommended_action:
```

### Prompt And Task-Packet Semantic Sanity Gate

```text
1. Read the instruction once as the target thread would read it.
2. Check for typos, wrong object relationships, inverted ownership, stale thread
   names, ambiguous pronouns, and contradictory verbs.
3. Check that native Codex capability wording is directionally correct:
   correct: "不要在 CoAgent 中重复实现 Codex 已经原生支持的能力"
   wrong:   "不要重复手搓 CoAgent 已由 Codex 原生支持的能力"
4. If a bad prompt is found before dispatch, fix it before sending.
5. If a bad prompt has already been sent, immediately send a correction packet
   with the same request_id, mark the old wording as superseded, and update the
   relevant workflow if the mistake is reusable.
```

Semantic boundary gate:

```text
1. If the instruction uses words like healthy, normal, blocked, review, 审核,
   window, live, done, or continue, check whether it defines the decision
   boundary for that word.
2. The prompt/packet must include decision_scope, state_class,
   evidence_minimum, allowed_actions, forbidden_actions, stop_triggers, and
   next_owner.
3. For visible-thread patrols, choose one concrete state_class:
   routable, approval_pending_or_ui_blocked,
   provider_gateway_or_pending_review,
   dispatch_surface_or_agent_loop_failure, or unknown_blocked.
4. For MWORKS patrol/live-task routing, choose one concrete state_class:
   window_patrol_clean, helper_only_nonblocking, login_or_license_blocked,
   authorization_blocked, gui_error_blocked, visible_unknown_blocked,
   live_attach_blocked, or unknown_blocked.
5. If the state is not one of the known values, define the new value inside
   the packet before dispatch. Do not let the receiving thread invent what
   "healthy" or "blocked" means.
6. Reject instructions or packets whose only classification is ok, normal,
   healthy, looks fine, still running, probably blocked, or similar free text.
```

For JSON task packets, `native_surface_gate` may live at the top level or under
`metadata.native_surface_gate` during the compatibility period. New PMO-created
non-trivial task packets should pass:

```bash
python Scripts/quality/check_agent_task_native_surface_gate.py \
  Results/agent_packets/<request_id>.json --strict
```

Current local runtime export command:

```bash
python CoAgent/runtime/mosim_agent_runtime.py task-packet --task-id <id>
```

Or build a department-ready dispatch envelope with:

```bash
python CoAgent/dispatch/dispatch_helper.py dispatch-envelope \
  --department ProjectOwner \
  --task-id <id>
```

For a copy-paste department assignment message, use:

```bash
python CoAgent/dispatch/dispatch_helper.py department-task-text \
  --department ProjectOwner \
  --task-id <id>
```

Result packet requirements:

```text
[MoSim Result Packet]
task_id:
status: completed | review_required | input_required | auth_required | blocked | failed | canceled | rejected | superseded
canonical_status:
task_class:
canonical_task_goal:
conversation_objective:
summary:
files_changed:
commands_run:
evidence:
risks:
blockers:
review_status:
acceptance_state:
continue_or_stop:
next_recommended_action:
```

Older runtime packets may still say `done`, `done_with_concerns`, or
`cancelled`; importers should map those aliases to `completed`,
`review_required`, and `canceled`.

Current local runtime export command:

```bash
python CoAgent/runtime/mosim_agent_runtime.py result-packet --task-id <id>
```

To import a returned packet into runtime state:

```bash
python CoAgent/dispatch/dispatch_helper.py import-result \
  --packet /abs/path/result_packet.json
```

For a human review handoff, use:

```bash
python CoAgent/dispatch/dispatch_helper.py review-brief --task-id <id>
```

Do not rely on a side conversation's memory as project state. A conversation is
only an execution/review surface; durable state remains in the runtime database,
JSONL events, `Docs/Workflows/agent_task_ledger.md`, and `PROGRESS.md`.

Department status board entry:

```text
[MoSim Status Board Entry]
task_id:
parent_goal:
department:
owner_conversation:
task_conversation:
state:
read_scope:
write_scope:
dependencies:
next_action:
human_needed:
last_checkpoint:
evidence:
review_status:
git_status:
```

Current local runtime snapshot command:

```bash
python CoAgent/runtime/mosim_agent_runtime.py status-board
```

Before wide-scope CoAgent runtime or dispatch work, run:

```bash
python CoAgent/hooks/preflight.py
```

Daily/recurring Codex App automations may be used only after their behavior is
verified for the current installed App version. Until then, model them as
normal task tickets:

```text
Workflow/skills gap repair:
  owner: responsible frontline task thread, with PMO/CoAgentOps recording recurring gaps
  action: update workflow/skill docs only when actual execution exposes repeated misunderstanding, missing template, or rule conflict

Daily external repository update:
  owner: DevOpsDepartment + KnowledgeDepartment
  action: pull/update tracked reference repos within ignored/reference scope,
  summarize changes, and flag useful upstream fixes

Context documentation drift check:
  owner: MoSim｜文档秘书部, or responsible task thread
  action: compare PROGRESS/ledger/workflows against current task state

Security constraint scan:
  owner: task owner with preflight/harness checks
  action: large files, secrets, external paths, destructive-operation residues
```

Do not assume App automations replace durable MoSim status records. They can
trigger or remind; they are not the project state source.

Automation prompt size rule: keep native Codex App automation prompts short and
stable. A heartbeat or cron prompt should name the owner, entry documents,
high-level gate, and required return/blocker behavior. Do not grow the
automation prompt into a full policy manual after every incident; update
`AGENTS.md`, workflow docs, skills, packet templates, or checker scripts
instead. Only edit an existing working automation when cadence, owner,
destination, routing, or high-level trigger behavior is wrong.

Native automation creation method:

1. Search for the native tool before acting:
   `tool_search` query `automation_update create update view delete heartbeat cron`.
2. Use `automation_update`, not GUI clicks or private Codex App database edits.
3. For this-thread followups, prefer heartbeat automations with
   `kind="heartbeat"`, `destination="thread"`, `targetThreadId=<thread id>`,
   and an RRULE such as `FREQ=MINUTELY;INTERVAL=30` for short followups.
4. For detached recurring workspace jobs, use cron automations with
   `kind="cron"`, `executionEnvironment="local"` or `worktree`, `cwds` set to
   the project workspace, `model`, `reasoningEffort`, and an RRULE such as
   `FREQ=HOURLY;INTERVAL=4`.
5. Preserve existing automation fields during updates unless the user requests
   a change. Prefer updating an existing matching automation over creating a
   duplicate.
6. A created automation is only a trigger. Each run must still write a durable
   result or blocker packet under `Results/agent_packets/`.

Provider behavior matrix:

| Capability | Codex policy here | Claude Code note |
|---|---|---|
| Subagent trigger | Explicitly spawned by main agent/user-authorized task graph; one bounded result expected | May auto-delegate from descriptions |
| Durable workers | Use MoSim task queue/runtime, not Codex subagent chat state | Claude subagents still need external state for reliability |
| Nested delegation | Avoid for durable work; depth 2 only for bounded read-only or disjoint-scope batches with WAL | Do not assume named subagents can spawn subagents |
| Worktrees | Prefer one Git owner; use isolated worktrees only for disjoint branches/scopes | Claude has separate worktree-isolation concepts |
| Custom schemas | Treat local `.toml` examples as unverified until official Codex docs confirm | Claude frontmatter is not Codex syntax |
| Background tools | Record pending/denied tool state in WAL | Claude background behavior may deny prompt-required tools |

For long-running execution streams such as Git batching, Unreal project smoke
tests, simulator bring-up, large reference audits, and repeated documentation
learning passes, create a durable queue item first. A Codex subagent may process
one bounded item, but it must not be left as the only holder of continuation
state. If the task needs to continue after a checkpoint, the next item must be
recorded in the MoSim queue/ledger, then explicitly dispatched again.

The main agent must not treat a missing or closed subagent as task completion.
Completion is defined only by the durable queue state and required evidence. If
a subagent returns a useful checkpoint, consume it, update the queue/ledger, and
either dispatch the next bounded task or mark the durable task blocked/done.

Management analogy for long work:

```text
main agent:
  director / general manager; owns objective, priorities, queue, approvals,
  integration, verification, and final report
TaskSecretary:
  role definition for MoSim runtime, not a Codex subagent job by default;
  records instructions, checkpoints, blockers, task state, review requirements,
  and supervision signals
MoSim runtime worker:
  durable worker process; claims queue items, emits heartbeat/events, returns
  terminal evidence, and can survive chat/session loss
Codex subagent:
  short-lived specialist; executes one explicit batch and returns evidence
reviewer:
  durable queue role when ongoing; Codex subagent only for one bounded review
```

The detailed department model lives in
`Docs/Workflows/org_operating_model.md`. Use it when a task needs company-style
division of labor: PMO/director, documentation secretary, project owners,
testing, security, DevOps, architecture, knowledge management, and incident
review.

The director should not grind through every worker task when the queue is
large, but Codex subagents are not the replacement for a real worker pool. The
director should update durable state, enqueue bounded items, review returned
evidence, and use Codex subagents only as disposable specialists until a
MoSim-owned runtime worker exists.

For visible department conversations, the director must not operate the
department as a synchronous sub-process by sending repeated step-by-step
``continue`` ticks. Send one complete department charter instead: objective,
context pack, allowed scope, forbidden actions, evidence format, result packet
path, checkpoint cadence, and stop conditions. The department conversation owns
its own goal, plan, execution, checkpoints, and result packet. The director only
does visible dispatch, periodic status collection, integration review, and
human escalation. If a visible department times out on a command, send at most
one corrective charter that changes operating policy, then let the department
continue autonomously or return a blocker.

The complete charter must also name the task-specific infrastructure preflight
and expected engineering outputs. This prevents "packet-only" progress from
being accepted as work. For example, a MWORKS model task is not complete until
it has model/check/simulation/layout evidence or a valid blocker; a ROS2 runtime
task is not complete until it has topic/process/log/runtime evidence or a valid
blocker; a UE task is not complete until it has source/static/build/runtime
evidence inside scope or a valid blocker; and an asset/PBR task is not complete
until it has rendered/asset/material evidence or a valid blocker. If the
department cannot run the required preflight because its tool surface is
missing, it returns a blocker; PMO then fixes routing or infrastructure instead
of asking the department to keep trying the domain task.

Department-owned planning is mandatory for broad tasks. The department should
not wait for PMO to decompose every internal step. It should create a local
task graph, decide whether a disposable sub-agent can safely accelerate a
bounded slice, and report that decomposition in the packet. If the department's
runtime lacks sub-agent tools, it should record `subagents_used=[]` and continue
serially rather than inventing invisible workers.

For every non-trivial department assignment, the packet must include an
explicit sub-agent decision, even when no sub-agent is used:

```text
subagent_plan: used | available_but_not_useful | unavailable | unsafe
subagent_plan_reason:
```

`used` is expected when a material read-only audit, reference comparison,
visual/file review, or disjoint implementation slice can run while the
department advances the critical path. `available_but_not_useful` requires a
specific reason such as tight coupling, single-file triviality, resource lock,
or urgent critical-path dependency. `unavailable` records the missing runtime
tool. `unsafe` records the conflicting simulator, ROS topic, GUI/MCP session,
worktree, credential, or privacy risk. A packet that says only
`subagents_used=[]` is incomplete for broad work.

Current Codex CLI limitation: a foreground `timeout 60s codex exec resume ...`
is only a bounded visible message/probe. If the command is killed by the outer
timeout, the department is not continuing autonomously in the background. For
real long-running department work, pair the visible charter with the
project-owned background dispatch runner (`CoAgent/dispatch/codex_transport.py
start-dispatch`) and recover through `poll-dispatch` or `finalize-timeout`.
Until app-server transport is explicitly approved, treat this as two surfaces:
visible thread for user/auditor visibility, and background runner/result packet
for execution evidence.

The TaskSecretary is not an implementation worker. It should:

```text
record:
  user directives, changed priorities, owner assignments, checkpoints,
  blockers, and manual-review decisions
supervise:
  whether owners are still progressing, waiting, blocked, or missing evidence
review:
  whether returned work matches scope, stop condition, and required evidence
fan out review:
  when several independent reviews are required, spawn the same number of
  read-only secretary/reviewer grandchildren with disjoint review scopes
```

Secretary intake is mandatory for volatile instructions. Every new user
directive, correction, manual-review result, sub-agent return, blocker, or work
checkpoint must be captured in `Results/tmp/task_intake/`, promoted to
`Docs/Workflows/agent_task_ledger.md` or `PROGRESS.md` when stable, and only then
treated as recoverable state. Chat memory alone is not state.

Testing is a separate gate, not an always-on department by default. For small
checks, the task thread runs targeted tests and records evidence. For
independent review, a Codex `TestOwner` subagent is acceptable only for one
bounded review or test-analysis slice; it must return evidence and cannot
remain the test department of record. For ROS2/UE/MWORKS runtime checks, use one
owning thread with explicit resource locks so parallel test work does not
compete for topics, ports, GUI/MCP sessions, worktrees, or simulator processes.

Skills are work instructions, not task owners. Agents use skills to execute a
role; the orchestration ledger decides who owns the task, what evidence is
required, and when the task is complete.

## 2. Ledger Requirement

Record every long-running delegated task in `Docs/Workflows/agent_task_ledger.md`.
For runs lasting more than one turn, also write JSONL events under:

```text
Results/agent_runs/<run_id>/events.jsonl
```

If a sub-agent disappears, recover from the ledger. Do not infer state from old
chat memory or nicknames.

## 2.1 JSONL Event Schema

Use an append-only event log for runs that span multiple user turns or involve
multiple agents. Required fields:

```json
{
  "event_id": "GIT-20260521-OKWINDS-0001",
  "ts": "2026-05-21T11:20:00+08:00",
  "task_id": "GIT-20260521-OKWINDS",
  "agent_role": "GitIntegrator",
  "event_type": "agent_spawned",
  "summary": "Started safe integration of Docs/Skills/okwinds and branch cleanup",
  "paths_read": ["Docs/Workflows/agent_task_ledger.md"],
  "paths_written": [],
  "artifact_refs": [],
  "wal_locator": "",
  "parent_run_id": "",
  "resume_from_event_id": "",
  "resume_from_line_index": "",
  "terminal_event": "",
  "approval_state": "none",
  "tool_state": "none",
  "error_kind": "",
  "risk": "",
  "next_action": "scan large files and commit safe batches"
}
```

`event_id` order must be stable and monotonic within each `task_id`. When
resuming from a WAL, treat `resume_from_line_index` as 0-based and preserve the
old event ids in `artifact_refs` or `summary` instead of renumbering history.

Allowed `event_type` values:

```text
task_started
plan_updated
round_started
round_learned
round_doc_patched
agent_spawned
skill_injected
checkpoint
handoff_received
evidence_saved
human_request
human_response
approval_requested
approval_decided
tool_call_started
tool_call_finished
blocked
resumed
forked
completed
superseded
run_terminal
```

Use `round_started`, `round_learned`, and `round_doc_patched` for explicit
three-round learn-and-update work. A round is complete only after the doc patch
for that round exists or the event records a blocker.

The event log is not a replacement for Git history or simulation evidence. It
is the recovery trail for orchestration state.

Use these shared state values:

```text
approval_state = none | requested | approved | denied | pending
tool_state = none | requested | finished | pending | failed
error_kind = timeout | validation | permission | approval_denied |
             sandbox_denied | mcp_unavailable | gui_blocked |
             gui_crash_report | license_or_login | result_binding_failed |
             git_push_rejected | pack_too_large | unknown
```

Artifact refs should use:

```json
{"path":"Results/.../metrics.json","source":"MWORKS_MCP","sha256":"","bytes":0,"role":"metrics"}
```

Do not paste secret-bearing payloads or full GUI event streams into WAL.
Record paths, hashes, sizes, and claim roles instead.

For Sysplorer / Syslab / MWORKS GUI error-report dialogs, the delegated
department must stop the active MCP/model sequence and return a blocker packet
instead of continuing hidden retries. The packet or WAL event must include:
screenshot path under `Results/`, visible dialog text, triggering command or
task step, MWORKS error-report path or visible path prefix, whether the dialog
offers restart/send-report actions, `error_kind=gui_crash_report`, and the next
safe recovery step. Do not click restart, send report, confirm/close, or read
external `Documents/MWORKS/log` report files unless PMO/user explicitly
authorizes that cleanup or diagnostic read.

MWORKS session reuse is the default. A delegated MWORKS task should attach to
the existing logged-in Sysplorer / Syslab / MWORKS window through MCP health or
session ensure, then use background screenshot/sentinel evidence if the window
must be inspected without disturbing the user's desktop. Do not start a new
MWORKS/Sysplorer window simply to make a task cleaner, get a fresh splash-free
state, or avoid reasoning about current session evidence. A new window or full
restart is a last resort after a blocker, and requires PMO/user approval unless
the existing process is frozen or opening duplicate sessions uncontrollably.

PMO dispatch packets for MWORKS department work must include a
`mworks_live_gate` object before delivery, but the activation/window-health
owner is now CoAgentOps' 10-minute automation rather than each engineering
thread. Required task fields are `live_mworks_touched`,
`mworks_window_policy`, `activation_patrol_owner`,
`recent_patrol_required`, `max_patrol_age_minutes`, `required_return_fields`,
`blocker_on`, and `expected_engineering_outputs`. For live MCP/GUI work,
`activation_patrol_owner` should be `CoAgentOps`; for static file-only work,
set `live_mworks_touched=false` and do not turn the task into an activation
probe.

For MWORKS patrols and review routing, `window health` must not be used as a
standalone conclusion. The patrol/review packet must classify:

```text
main_window_identified: true | false
helper_or_proxy_windows: counted_and_nonblocking | blocking_text_seen | not_checked
state_class: window_patrol_clean | helper_only_nonblocking |
  login_or_license_blocked | authorization_blocked | gui_error_blocked |
  visible_unknown_blocked | live_attach_blocked | unknown_blocked
evidence_minimum_met: true | false
next_owner: CoAgentOps | PMO | MWORKS_R1 | MWORKS_R2 | user
```

`window_patrol_clean` requires a real target main MWORKS/Sysplorer/Syslab
window and no visible login/license/demo/authorization/error-report or
blocking unknown window. `helper_only_nonblocking` means helper/proxy/Qt/IME/
docsearch windows were observed or counted but showed no blocking text and did
not replace the target main-window evidence. `live_attach_blocked` means the
GUI may look usable but MWORKS MCP/session attach still cannot prove no-new-
window reuse; R1/R2 live `check_model`, `SimulateModel`, package-browser, and
graphical live audit remain blocked until attach-only validation exists.

The return or blocker packet should carry `mworks_activation_patrol_reference`
and, when known, `mworks_activation_patrol_age_minutes`, plus
`will_not_click_activation_login=true` and `live_mworks_touched`. If no recent
CoAgentOps patrol is available and the work is live MCP/GUI work, the
department may run one bounded current-turn sentinel/API check or return a
blocker; it must not loop on activation checks, open a fresh MWORKS window, or
produce only JSON/sentinel metadata as a completed engineering result. If the
department does run current-turn sentinel/capture evidence for a real incident,
it must inspect that evidence and include the concrete observed state in
`activation_state_observation` and `license_state`.

Important correction: a visible `Sysplorer [教育版]` title is only an edition
marker, not proof that the account is activated. It is also not by itself a
reason to stop engineering work. If no demo/login/authorization/error marker
exists, continue with the requested model/check/simulation/layout task and
record task-local API/check/simulation license sufficiency where available. Do
not claim permanent account activation unless the API/result explicitly exposes
activation/account status.

Background screenshot evidence has a known blind spot: it may capture a normal
main window while the login/license pane is only visible after the existing
Sysplorer/MWORKS window is maximized or brought to foreground. CoAgentOps or
PMO owns that foreground recovery/review route. Delegated departments block
and return evidence when demo/login/authorization/error risk appears; they do
not click login, activation, save, close, restart, send-report, or error-dialog
controls. Login/license patrols should use maximized-window evidence when a
hidden login pane is possible; minimized/background captures are not enough for
that case. PMO/CoAgentOps first uses the existing maximized foreground window.
If the official login action does not return or cannot complete on the existing
window, PMO/CoAgentOps may reopen MWORKS and log in through the official UI as
a bounded recovery. Successful recovery closes only the license/login dialog
and keeps the reusable main window open when possible.

Run the machine gate before dispatching or accepting MWORKS packets:

```powershell
python Scripts\quality\check_mworks_live_gate.py `
  Results\agent_packets\<request_id>.json --kind task --expect department
python Scripts\quality\check_mworks_live_gate.py `
  Results\agent_packets\returns\<request_id>.json --kind return --expect department
```

If the return is a blocker, pass the blocker packet path to the same
`--kind return --expect department` check. The gate accepts either a recent
CoAgentOps patrol reference or a current-turn sentinel/capture set for an
incident. It still rejects missing no-click pledge, missing `live_mworks_touched`,
missing declared engineering outputs, JSON-only completions, and missing
phase screenshots/observations for tasks that claim graphical/layout/result
viewer evidence.
The general pre-dispatch native surface checker also enforces this for
MWORKS/Sysplorer/Syslab department task packets: when
`Scripts/quality/check_agent_task_native_surface_gate.py --strict` sees a
MWORKS target department/thread, it requires the same `mworks_live_gate` task
contract before the packet is dispatchable.

If a CoAgentOps patrol or current task evidence shows mixed or uncertain MWORKS license state, such
as one Sysplorer window in education mode and another relevant window in demo
mode, the safe blocker category is `license_or_login`, but `license_state`
must still use a concrete observed-state value such as
`mixed_education_and_demo_blocked`, `demo_blocked`, `login_required`,
`authorization_failed`, `sentinel_unavailable_blocked`, or `unknown_blocked`
until PMO/user identifies a valid reusable session or resolves the stale/demo
window. Departments must return the blocker with `status=blocked` and
screenshot/sentinel evidence if collected. They may continue only with
file-level static work that explicitly avoids MWORKS MCP/GUI.
For MWORKS/Sysplorer/Syslab tasks, this is an all-window gate: any relevant
window in demo, login/activation, authorization-failed, GUI-error, mixed, or
visible unknown state blocks the whole task even if another window is clean or
education-mode. Hidden Qt/browser-proxy/helper windows with no license/error
text are risk evidence and must be counted in the manifest, but they do not
alone prove authorization loss. Do not close or ignore a real suspect window
and continue.

Every MWORKS department task packet must also declare
`expected_engineering_outputs`. For model/simulation/layout/package work, the
expected outputs must be concrete engineering artifacts such as `.mo` or
`package.mo` edits, `check_model`, `SimulateModel`, native result/`.msr`,
metrics, diagram/layout screenshots, or wiring observations. JSON packets,
ledger updates, and progress notes are control-plane evidence only; they do
not count as engineering progress unless the task is explicitly
`diagnostic_only`, `rule_sync_only`, `preflight_drill_only`,
`dispatch_surface_diagnostic`, or `static_inventory_only`. Completed MWORKS
returns that only produce JSON must be rejected or reclassified as diagnostic
metadata, not accepted as model optimization.

GUI crash detection must not depend only on an agent noticing a foreground
dialog. Use a sentinel before/after MWORKS GUI-affecting steps:

1. Preferred: Windows MCP plus project-local Win32/UI Automation window-title
   and child-text inspection, including all MWORKS/Sysplorer/Syslab windows.
   Computer Use is deprecated for MoSim desktop GUI monitoring/recovery and
   must not be used as the MoSim desktop GUI route.
2. Project-local Win32 background evidence scripts: use
   `Scripts/tools/capture_window_background.ps1` for window-level Sysplorer /
   MWORKS screenshots before falling back to foreground desktop capture. If a
   minimized window must be inspected, use `-RestoreMinimized`; for
   login/license patrols or suspected hidden panes, use `-Maximize` as well.
   The script may briefly restore or maximize the existing target main window,
   capture through `PrintWindow`, then restore/minimize depending on flags. It
   lists helper/proxy windows by default but does not restore or maximize them;
   use `-IncludeHelperWindows` or `-MaximizeAllMatches` only for a bounded
   PMO/CoAgentOps helper diagnostic. Use `-OutDir` for the output directory;
   `-OutputDir` is not a valid parameter for the current script. This is GUI
   incident evidence, not simulation success evidence. Background
   `PrintWindow` capture is also not a full-GUI acceptance tool: without
   `-RestoreMinimized` it can produce only a tiny minimized title fragment,
   and even with maximize it can miss composite Qt/browser-proxy surfaces such
   as the right MWORKS AI panel. Return packets must treat the script output as
   window-state/preflight evidence unless a human/foreground/Windows-MCP visual
   check confirms the complete GUI.
3. Windows UI Automation / EnumWindows style title/text detector for
   `MWORKS错误报告`, `Sysplorer 遇到错误，需要关闭`, login/license prompts, and
   Sysplorer/MWORKS window titles. This can detect incidents even when no image
   capture is available.
4. Approved bounded background click: only PMO or `MoSim｜CoAgent运维平台` may use
   `Scripts/tools/invoke_window_background_click.ps1` for one explicitly
   approved low-risk UI action, such as opening an AI/helper panel. Delegated
   departments must not use it for login, activation, save, close, restart,
   send-report, or crash/error-dialog recovery controls; they should collect
   evidence and return a blocker.
5. Evidence screenshot fallback: Windows MCP `Snapshot`/`Screenshot` or another
   full-desktop capture only when the relevant window/dialog is visible. This
   is foreground desktop evidence support, not a reliable hidden-window
   detector.
6. Avoid virtual-desktop isolation unless PMO/user explicitly approves it; it
   can disrupt manual review and does not by itself prove background screenshot
   capture.

If no sentinel is available, write `gui_sentinel=unavailable` in the task packet
or return and avoid unattended MWORKS GUI evidence claims.

For delegated runs, record child WAL locators as artifacts:

```json
{"path":"Results/agent_runs/<child_run>/events.jsonl","source":"agent_wal","sha256":"","bytes":0,"role":"child_wal"}
```

Do not treat UI/SSE projection events as the source of truth. Prefer terminal
tool results, result files, metrics, artifact manifests, child WAL locators,
and NodeReport-style terminal summaries.

## 2.2 Resume Rule

Before resuming a long-running task, inspect the latest ledger row and, when
available, the latest `events.jsonl`. Summarize:

```text
latest_terminal_event:
pending_approvals:
pending_tool_calls:
latest_artifact_refs:
error_kind:
next_safe_action:
```

Do not infer completion from missing chat context or a missing sub-agent id.

## 2.3 Task Secretary Intake

Use a `TaskSecretary` record when the user is steering a long session, when
many sub-agents are active, or when instructions arrive as corrections across
multiple turns. The secretary role is a planner/recorder, not a hidden worker.

The secretary's job is to turn user messages and agent returns into a durable
task queue:

```text
message_id/time:
raw_user_directive:
interpreted_task:
goal:
owner_role:
read_scope:
write_scope:
acceptance:
state:
next_action:
needs_user_review:
```

Write current-turn intake drafts under:

```text
Results/tmp/task_intake/YYYY-MM-DD.md
```

Promote only stable items into `Docs/Workflows/agent_task_ledger.md` or
`PROGRESS.md`. Do not paste entire session dumps into durable docs.

Trigger a secretary update when any of these happen:

```text
new user instruction or correction
user says a previous interpretation was wrong
sub-agent returns DONE / DONE_WITH_CONCERNS / BLOCKED
manual review result changes task status
Git/MCP/simulator task reaches a blocker
the current goal is too broad or stale
```

The main agent remains responsible for decisions. The secretary record only
preserves the task state and makes the next safe action explicit.

## 2.4 Goal Assignment

Do not use one broad goal to hide unrelated streams. Assign goals at the level
where completion can be verified.

Codex `/goal` is a completion contract, not a request to "run longer". Use it
only when the task needs multiple autonomous turns and has a clear, testable,
auditable stop condition while the exact path is still uncertain. Do not use a
Codex goal for short explanations, one-line edits, simple suggestions, routine
code review comments, or vague aims such as "optimize performance" or "make the
project better" unless they have been rewritten into evidence-backed completion
criteria.

Before creating or continuing a Codex goal, write this contract in the task
graph, task packet, or intake record:

```text
outcome:
verification_surface:
constraints:
boundaries:
iteration_policy:
blocked_stop_condition:
evidence_to_record_each_round:
```

Good goal wording names what must be true at the end and how PMO or the user
can verify it. Weak goal wording names only an activity. If the only natural
completion signal is "I answered the question" or "one file was patched", keep
it as a normal prompt or ledger task instead of a Codex goal.

Recommended goal split:

| Layer | Goal Scope | Completion Evidence |
|---|---|---|
| Main agent | Orchestrate current project objective, integrate results, and keep the ledger accurate | Current plan, intake record, ledger updates, final verification |
| Git owner | Classify every path group as pushed, ignored, needs-user-decision, or blocked | Pushed branch refs, commit hashes, large-file scan, residual table |
| TaskSecretary | Convert user instructions and agent returns into recoverable tasks | `Results/tmp/task_intake/*` plus promoted ledger/PROGRESS rows |
| Research owner | Complete bounded source audit or parameter-identification research | Source list, evidence/inference/unknowns, patch plan or report |
| Reviewer | Review Docs/code/model changes without implementing | Findings with file references and residual risk |

Every sub-agent prompt for this project should include a concrete goal and
terminal condition. If runtime support allows it, request `model=gpt-5.5` and
`reasoning_effort=high` explicitly at spawn time.

If a goal record becomes malformed, stale, over-narrow, or impossible to update
through the available goal tools, do not let it block execution. Reset/delete
the bad goal record and recreate only the durable total objective. Single
implementation steps belong in this ledger or the active task queue, not in the
top-level goal.

Codex thread goals are display and recovery metadata for one visible
conversation. They are not the CoAgent task-control plane. For project tasks,
record cancellation through `CoAgent/runtime/mosim_agent_runtime.py cancel` or
through a validated result packet with status `canceled`; keep the tombstone and
audit history. Ask the user to clear a Codex goal only when the visible
conversation itself is blocked by stale UI goal state. Do not assume another
conversation can clear its own Codex goal automatically; that requires a
separate proven app-server or CLI primitive and visible-front-end verification.

## 2.5 Git Owner Stop Condition

A Git owner is not done after pushing one small branch unless that was the
entire assigned objective. For broad repository convergence, the terminal table
must classify each path group:

```text
pushed
ignored/excluded
needs-user-decision
blocked
```

Minimum path groups:

```text
Docs/Workflows/AGENTS/PROGRESS
Docs/Skills/Mworks
Docs/Skills/Agent and Docs/Skills/okwinds
Scripts/tests
Models/scenarios
References/AirSim
References/Lab
References/PX4
References/Sunray/CUAV
References/MWORKS/RflySim
UE5/UE source/config
Results/tmp and generated outputs
```

If a full `git status` is too slow, the Git owner must use path-limited
commands and clean-branch strategies. Do not push polluted aggregate branches.

For stale-ledger recovery, use this order:

```text
1. Read the ledger row for objective, write scope, and last checkpoint.
2. Read the latest events.jsonl if it exists.
3. Trust only terminal task/run events for completion and WAL locators.
4. Treat pending approvals, pending tool calls, missing terminal events, or
   expired UI/SSE after_id cursors as diagnostic state, not as success.
5. If the user requested three learn-and-update rounds, verify all three
   round_doc_patched checkpoints before continuing from "done".
```

If the ledger says `done` but the event log lacks a terminal event or round
patch checkpoints, mark the row stale and resume from the last confirmed safe
checkpoint.

## 3. Standard Sub-Agent Contract

Each delegated task must state:

```text
role:
objective:
depends_on:
read scope:
write set:
side_effect_policy:
stop condition:
expected output:
expected evidence:
forbidden actions:
```

For queue-owning agents, also state:

```text
queue source:
claim rule:
max tasks per checkpoint:
checkpoint cadence:
review trigger:
handoff condition:
```

Use stable role names such as `GitIntegrator`, `SceneResearcher`,
`SimulationReviewer`, `ParameterIdentificationResearcher`, and
`DocsWorkflowAuditor`. Do not rely on arbitrary nicknames for recovery.

For documentation-discovery or external skill/workflow audit agents, include:

```text
round:
source slice:
patch target:
do-not-adopt candidates:
contradictions to current docs:
minimum evidence paths:
```

For write-capable agents, the write set must be disjoint. Use only one
Git/quality agent at a time.

## 3.1 Reviewer Agents

After a write-capable agent reports completion, run review through either the
main agent or a dedicated read-only reviewer. The reviewer must use at least the
relevant subset of these six angles:

```text
requirements fit:
interface and integration:
runtime/performance:
evidence and reproducibility:
Git/large-file/secrets:
documentation and recovery:
```

Reviewer agents are read-only by default. They do not fix issues unless the
main agent assigns a separate write set.

For documentation changes, run a dedicated `DocsQualityReviewer` before
declaring the task complete. It must check:

```text
policy vs workflow separation:
no accidental pasted XML/HTML/questionnaire/config fragments:
no unsupported tool/config claims without verification note:
no duplicated or contradictory rules:
AGENTS.md remains concise and policy-level:
workflow files contain detailed mechanics:
PROGRESS.md contains live state only:
links in Docs/Index/workflow_index.md still resolve:
```

If the reviewer finds contamination or misplaced detail, fix the docs and run
the review again.

Use two reviewer lanes when the task changed rules, workflows, or generated
artifacts:

```text
spec/compliance reviewer:
  checks requested scope, forbidden paths, source coverage, and acceptance gates
quality/risk reviewer:
  checks correctness, regression risk, security/secrets, and recovery evidence
```

For small documentation-only patches, the same read-only reviewer may cover
both lanes, but the final note must state which lane checks were performed. Do
not treat a worker self-review as either reviewer lane.

Before accepting a review finding, evaluate it against local project facts:

```text
review finding:
confirmed file/line or source path:
does it match current AGENTS/workflow constraints:
would the fix add unsupported scope or YAGNI behavior:
accept / reject / needs user decision:
evidence:
```

External reviewer feedback is input to evaluate, not an order to apply. Push
back or record `do_not_adopt` when the suggested fix imports an external runtime,
changes provider semantics, writes outside the approved path, or lacks evidence.

## 4. Evidence Format

Returned results must separate:

```text
confirmed evidence:
inference:
unknowns:
risks:
recommended next validation:
changed paths:
```

Do not merge a high-impact conclusion if the sub-agent did not provide evidence.

Use this NodeReport-style terminal summary for long tasks:

```text
task_id:
role:
status:
confirmed evidence:
artifacts:
commands/checks:
paths changed:
unknowns:
risks:
next reviewer action:
resume point:
```

GUI windows, plots, animations, and UI streams are review surfaces. They are
not the audit source. The stable audit source is the tool result, result path,
metrics, logs, native-result locator, artifact manifest, and Git commit.

For agent/workflow audits, use a capability coverage map before declaring a
process complete:

```text
capability or rule:
source evidence path:
project doc target:
workflow/checklist entry:
validation gate or manual review:
known gap:
```

Documentation-only changes may use manual review and `git diff --check` as the
validation gate, but they must still identify which future check would detect
drift.

Completion claims require fresh verification evidence from the current turn or
current resumed run. Before saying a task is done, record:

```text
claim:
verification command or manual review gate:
fresh output / exit status:
files or artifacts checked:
known gaps:
```

For documentation-only work, acceptable fresh gates are scoped source coverage
review, target-file diff review, link/path checks, and `git diff --check`.
For code, model, or simulation work, documentation review is not enough; use the
project's targeted test, build, model check, or simulation evidence route.

## 4.1 Round 3 Validation Gates

For the third learn-and-update round, add a source-to-doc coverage matrix before
declaring completion:

```text
source slice:
finding:
adopted rule:
target file:
validation gate:
future drift detector:
do_not_adopt:
```

The matrix should cover at least:

```text
multi-agent scheduling / queue ownership:
reviewer agent lanes:
WAL and stale-state recovery:
goal/task completion evidence:
documentation pollution prevention:
unsupported external runtime patterns:
```

If a source was read but produced no project change, include it with
`adopted rule: none` and explain the rejected pattern. This prevents silent
"read but unused" claims.

## 5. Long Git Work

Large `git add`, large-file scans, and reference import cleanup should be
delegated to `GitIntegrator` when an agent slot is available. The main agent
continues architecture, implementation, or review while Git runs.

Git delegation is not limited to huge imports. If Git is slow, has LFS/hook
side effects, stale `index.lock`, old polluted branches, broad untracked trees,
or any repeated blocker, the main agent must treat Git as a separate DevOps
stream. In that state, even a small Markdown commit should be assigned to
`GitIntegrator`; the main agent's role is to give scope, review the result, and
continue the engineering critical path.

Normal small commits may be done by the main agent only when all of these are
true:

```text
git status is fast enough to inspect safely
no stale .git/index.lock exists
no LFS hook is known to scan the whole repository
the staged scope is explicit and small
the commit/push is expected to finish quickly
no other Git owner is active on the same worktree or branch
```

If any condition is false, spawn or reuse `GitIntegrator` and record the Git
task in the ledger.

`GitIntegrator` may:

- inspect status and diffs;
- update `.gitignore` for generated or over-limit files;
- stage, commit, and push approved project files;
- report exact blockers.

`GitIntegrator` must not:

- force push;
- rewrite history;
- delete user source material;
- commit files over GitHub's hard size limit;
- submit nested repositories as gitlinks unless explicitly requested.

For large imported repositories, prefer isolated worktrees or throwaway clones
when parallelizing Git analysis:

```text
git worktree add ../Quadrotor-git-<scope> <base-branch>
```

Use this only inside the project parent path approved by the user or a
project-local worktree directory. Each worktree owner must have a disjoint
branch and scope. Never run two write-capable Git agents against the same
working tree or branch. The main agent or single `GitIntegrator` owns final
integration and push ordering.

When splitting Git work, use content-family branches:

```text
Docs/workflows
Docs/Skills/*
References/AirSim/*
References/Lab/*
References/RflySim/*
UE5/*
```

Each branch must pass large-file and gitlink checks before push. If a branch
push fails because the pack is too large, split by narrower repository group
instead of retrying the same pack repeatedly.

Large batch default strategy:

```text
1. Put the whole incoming tree behind `.gitignore`, or keep it outside the
   repository until the queue is ready.
2. Build an inventory grouped by source repo, content type, and expected value.
3. Open one narrow batch by adding a precise negative `.gitignore` rule or by
   copying only that slice into the tracked target.
4. Run the batch gates: >100 MB scan, gitlink scan, LFS pointer scan, secret
   scan, generated-artifact scan, and path-count sanity check.
5. Stage only the reviewed slice with path-limited `git add`.
6. Run `git diff --cached --check` as a hard gate and explicitly inspect the
   command exit code before any commit. Do not chain `git diff --cached --check`
   and `git commit` in a way that lets the commit continue after whitespace or
   path-check failures; if the gate fails, unstage the slice, narrow or defer
   the failing files, then rerun the gate.
7. Commit and push that slice before opening the next slice.
8. Cache the completed review in the task evidence or ledger, including the
   exact committed paths, gate results, commit hash, and push state. Future Git
   passes must not repeat full gates for that exact committed slice unless its
   path status changes, a temporary throttle is being narrowed for that path,
   or the remote/branch state contradicts the recorded commit.
9. Record skipped paths and the next batch in the ledger.
10. Drain the temporary ignore rules themselves. The final state must not keep
   broad "hide the incoming tree" rules just because the source-control view is
   quiet. Convert each temporary rule into committed tracked content, a narrow
   long-term ignore for a justified class, or a documented manifest-only skip.
11. Record the drain state. Each temporary throttle must have an owner task,
    intended next batch, and closeout decision in the ledger/result packet. If a
    rule has no drain owner, treat it as unfinished Git work rather than release
    hygiene.
```

For crawled open-source reference projects, the default unit is the source
project directory, not individual source files. A normal project under
`References/` or `Docs/Skills/` should be opened as a project or major
subdirectory, scanned for oversized files and durable exclude classes, and then
committed in as few reviewed batches as the 1000-file limit allows. Do not grow
`.gitignore` with ordinary source, docs, scripts, configs, or small assets just
because a batch is inconvenient or a whitespace check fails. Record such files
as deferred review evidence and either submit them in a later reviewed batch or
ask for an explicit normalization/import policy. Durable ignores should stay
small and class-based: oversized individual files, operator-local settings,
dependency folders, generated/build/cache/runtime outputs, missing LFS assets,
or explicitly manifest-only asset classes.

Do not turn `.gitignore` into a per-file backlog for a crawled project. A
hundreds-line ignore block for ordinary reference material is a release hygiene
failure, not a completed split. Missing-LFS sets must be represented by concise
class or directory manifest-only rules with evidence and a later restoration
note. Per-file ignores are reserved for a small number of known over-limit files
when no safe class rule exists.

Generic generated/dependency/archive/binary rules belong at the reference-tree
class level, not under each crawled project. Prefer one `References/**` final
guard for nested repositories, dependency directories, build/dist/out/cache
folders, virtual environments, bytecode, compiled binaries, and archive formats
over repeated `References/<project>/**` copies. Place the final guard after
project unignore rules when necessary so a broad whitelist does not reopen
archives or build outputs. Keep project-specific exceptions only for reviewed
source/config directories that share a normally generated name, for example PX4
board `dist` inputs.

A source project being hundreds of MB as a directory is not a durable-ignore
reason. The durable decision is file/class based: individual files at or above
100 MiB, private local config, dependency/build/cache/runtime outputs, missing
LFS payloads, or manifest-only assets stay ignored; normal source, docs,
examples, configs, and small binary assets should be reopened at
project/subdirectory granularity and committed in reviewed batches. If a
temporary intake block grows past a few hundred lines, treat that as a
release-hygiene smell and schedule drain batches instead of adding more ordinary
source exceptions.

Operational closeout checklist for crawled repositories:

```text
temporary ignore owner recorded:
path-limited inventory recorded:
batch path list written under Results/coagent_status/git_batches/<task>/:
batch file count < 1000:
single-file >=100 MiB check passed or blockers recorded:
credentials/local settings/generator/dependency/cache/runtime classes excluded:
actual content staged with pathspec, not broad git add:
git diff --cached --check passed or exact third-party exceptions recorded:
commit hash and push state recorded:
temporary ignore removed, narrowed, or explicitly blocked:
```

A `.gitignore`-only batch can be a throttle or cleanup commit, but it is not a
content-drain batch. After such a commit, the next action must name the source
project/subdirectory to reopen, the durable class rule to keep, or the blocker
that prevents draining it.

When using PowerShell with temporary indexes and `git commit-tree`, native Git
gate commands must be checked through `$LASTEXITCODE` before `git write-tree`
or `git update-ref`. In particular, after `git diff --cached --check`, stop the
batch if `$LASTEXITCODE` is nonzero even when the PowerShell script itself
continues running. Do not let a commit-tree/update-ref step run after a failed
diff-check gate.

Do not treat IDE visibility settings as a substitute for this strategy.
Specifically, do not solve a huge untracked surface by setting
`git.showUntrackedChanges=false`, `git.showIgnoredFiles=false`,
`files.exclude`, `files.watcherExclude`, or broad `search.exclude` entries for
the incoming trees. Those settings hide evidence from the operator and can make
the file explorer/source-control surface misleading. Use `.gitignore` or a
project-local exclude file for temporary Git isolation, then drain the ignore
rules with reviewed small batches.

This strategy is mandatory when any of these are true:

```text
incoming file count is roughly 1000+:
source tree contains external simulator/game/asset repositories:
GitHub rejected a push for file size or pack size:
git status/add/commit becomes slow because untracked trees are huge:
the user explicitly says to use the previous divide-and-conquer method:
```

Do not solve a large import by repeatedly retrying one aggregate branch. The
correct recovery is to ignore the aggregate, reopen one reviewed slice, and
push slice-by-slice. If the batch is important but too large for Git, keep it
ignored under `References/` and commit only a manifest plus usage notes.
Do not declare completion from `git ls-files --others --exclude-standard`
returning 0 or from an IDE source-control pane becoming quiet. That only proves
untracked visibility is controlled. A release Git task is complete only after
temporary large-tree ignore rules have been drained or justified as long-term
ignore rules, and tracked modifications have been committed, intentionally
left for a documented later task, or escalated as a blocker.

For ten-thousand to hundred-thousand file surfaces, treat chat output, shell
argument length, hook scans, and GitHub limits as first-class constraints:

```text
1. Do not print full path lists to chat. Write reviewed path lists under
   Results/coagent_status/git_batches/<task>/.
2. Stage from files with `git add --pathspec-from-file=<paths-file>` or an
   equivalent path-limited command instead of reconstructing huge pathspecs in
   the shell.
3. Keep each batch well under 1000 files unless a prior dry-run proves the
   repo, hooks, and transport handle that specific slice.
4. Scan every opened batch for files at or above GitHub's 100 MiB hard limit.
   Use Git LFS only for approved binary assets that genuinely belong in the
   project; otherwise keep large assets ignored and commit a manifest.
5. If a giant tree is already tracked, `.gitignore` alone will not remove it
   from Git. First stop new generated/untracked mass with ignore rules, then
   decide whether the tracked tree should remain, be split by future commits,
   move to manifest-only/LFS, or be removed through an explicit reviewed task.
   File renames or directory moves can create 10k+ tracked changes; handle them
   as tracked-change batches with path-limited `git diff --name-only -- <path>`
   or `git ls-files -m -- <path>`, not with broader ignore rules.
   Do not close a Git split task just because visible untracked files are 0:
   drain temporary ignore rules and separately commit or explicitly block every
   tracked-change family.
6. Treat reviewed committed slices as cached evidence. Reuse the recorded
   result packet, pathspec file, ledger row, and commit hash instead of
   rescanning the same slice from scratch. This cache applies only to the exact
   committed paths; it does not certify a broad parent directory and does not
   close ignored backlog.
7. For local performance, consider Git's large-repo features only as bounded
   helpers: sparse checkout or partial clone for fresh analysis clones, and
   split-index/untracked-cache/fsmonitor only after recording the local config
   change and confirming it does not hide files from the release audit.
```

Known local Git incident pattern:

```text
git commit can hang in git-lfs post-commit because git-lfs runs
git ls-files -z --others --cached --exclude-standard over the whole large
working tree.
```

When this recurs, `GitIntegrator` should:

1. confirm no live Git process is using `.git/index.lock`;
2. remove only stale zero-byte `.git/index.lock` after process check;
3. prefer path-limited status/diff commands;
4. avoid broad `git status` during large external-repo staging;
5. if a single small commit is blocked only by slow hooks, use a documented
   hook-bypass or Git plumbing path and report the exact command;
6. push and report commit hash, branch, skipped paths, and residual state.

Do not let the main agent spend multiple minutes debugging Git unless the user
explicitly asks it to. Git blocker diagnosis belongs to `GitIntegrator`, with
main-agent review of the final evidence.

## 5.1 AirSim Batch Migration With Nested Agents

Use this section when importing external AirSim-family repositories from a
source directory such as `C:\Users\HP\Desktop\AirSim` into
`References/AirSim/`.

Do not copy the whole source tree into the repository in one operation. Treat
AirSim migration as a queue-backed Git task:

If the source has already been copied into the repo and produces thousands of
untracked files, immediately ignore the whole target subtree first. Then
unignore or re-copy one AirSim content family at a time. This prevents the
whole repository from becoming hostage to one failed bulk add/push.

```text
parent role:
  AirSimMigrationCoordinator
child role:
  AirSimGitBatchOwner:<content_family>
grandchild role:
  AirSimBatchWorker:<batch_id>
```

The parent owns the migration plan, ledger, integration order, and final Git
state. The child owner owns one content family and may spawn grandchildren only
for single-batch scan/migrate/verify tasks. Grandchildren must not spawn more
agents.

Recommended content families:

```text
AirSimCore
CosysAirSim
ProjectAirSim
PegasusSimulator
UnrealCV
SPEAR
IsaacSim
CarlaUE
LabPlanning
DocsAndExamples
GeneratedOrBinaryArtifacts
```

Each batch must declare:

```text
batch_id:
source_paths:
target_paths:
excluded_paths:
write_set:
large_file_scan:
gitlink_scan:
lfs_pointer_scan:
secret_scan:
expected_commit_branch:
rollback_note:
next_batch_hint:
```

Hard gates before commit:

```text
no file > 100 MB:
no nested repository committed as gitlink:
no broken Git LFS pointer files:
no Binaries/Intermediate/Saved/DerivedDataCache unless explicitly approved:
no copied credentials, tokens, or local IDE/user config:
path count and pack size small enough for one push:
```

If a batch fails due to GitHub pack size, LFS missing objects, or slow status,
split by narrower repository group or file type. Do not retry the same failed
aggregate branch.

External source exception:

```text
source:
  C:\Users\HP\Desktop\AirSim
target:
  C:\Users\HP\Desktop\MoSim\References\AirSim
scope:
  read and copy only from that source into the target
forbidden:
  deleting source files, force push, history rewrite, writing outside target
```

Review every migrated batch with a read-only reviewer before merging it into
`main`. The reviewer must check at least:

```text
requirements fit:
file-size and GitHub limit:
gitlink/LFS correctness:
generated artifact pollution:
license/attribution notes:
recovery and rollback:
```

## 5.2 Agent Log Analysis

For long-running agents, parse their WAL/run logs before changing the queue.
Track:

```text
tasks assigned:
tasks completed:
blocked tasks:
retries:
elapsed time by task:
missing evidence:
review failures:
```

Use these fields to improve the next assignment: split oversized scopes,
tighten stop conditions, add missing acceptance checks, or route the task to a
reviewer instead of another worker.

When analyzing WAL/logs, classify noisy stream events separately from stable
evidence:

```text
stable evidence:
  terminal tool results, exit codes, artifacts, commits, metrics, terminal reports
diagnostic only:
  streaming deltas, SSE/UI projection events, progress chatter, labels, raw PTY spam
pollution to exclude:
  secrets, credentials, full prompts with private data, base64 media, huge logs
```

Keep summaries path-rich and payload-light: record locators, hashes, byte
counts, and roles instead of pasting full logs into workflow docs.

## 6. External Repository Audits

When many repositories are present under `References/`, split audits by
technical domain:

| Stream | Examples |
|---|---|
| UE/rendering | AirSim, ProjectAirSim, RflySim, SPEAR, UnrealCV |
| Planning/trajectory | ego-planner, GCOPTER, Fast-Racing, SUPER |
| Perception/mapping | FAST-LIO, FAST-LIVO2, Point-LIO |
| Docs/Skills/workflow | Codex skills, subagent catalogs, agent runtime repos |
| Git/quality | large-file scan, secret scan, nested repo cleanup |

Use `Docs/Workflows/audit_external_repo.md` and `Scripts/reference/audit_external_repo.py` for
repeatable summaries.

## 7. Skills / Workflow Runtime Audits

When auditing external agent, skill, or workflow-runtime repositories, use one
owner audit agent and require three passes before changing project rules:

```text
PASS 1 inventory:
  repo purpose, useful modules, irrelevant modules, local evidence paths

PASS 2 extraction:
  reusable orchestration, WAL, evidence, validation, delegation, resume,
  doctor, and capability-coverage patterns

PASS 3 comparison:
  current project docs already covered, missing updates, contradictions,
  stale ledger rows, and exact doc patch list
```

The owner agent must return a `DO NOT ADOPT` list. Do not import full runtime
dependencies only to copy a workflow pattern.

If the user asks for `学习+更新文档三遍` or equivalent, the three passes above
become three separate learn-and-update rounds. Patch project docs after each
round:

```text
ROUND 1:
  learn inventory/relevance/source-of-truth
  patch durable routing and do-not-adopt guardrails

ROUND 2:
  learn orchestration/WAL/delegation/event patterns
  patch task graph, sub-agent contract, WAL schema, templates, and checklists

ROUND 3:
  learn validation/coverage/resume/doctor/document-pollution patterns
  patch consistency gates, stale-ledger recovery, coverage review rules,
  reviewer lanes, and rejected-pattern lists
```

Do not mark the audit done until the final summary lists the changed paths and
what each round updated.

For Round 3, prefer source slices that were not already used in Rounds 1/2:

```text
validation-before-completion and reviewer workflows:
subagent/task-distributor/reviewer definitions:
skills-runtime testing, capability coverage, and applied workflow gates:
skill/repo compliance audit checklists:
log-noise and prompt/output pollution warnings:
loop/goal/task stop contracts:
```

### 7.1 Recurring Learning Owner

External Docs/skills learning is a recurring workflow, not a one-time cleanup.
Start a fresh recurring-learning row when any trigger below occurs:

```text
sub-agent disappears, waits indefinitely, or is closed without checkpoint
task plan exists but the conversation ends before the plan is recoverable
Git, MCP, simulator, or docs workflow fails in a repeated pattern
new major tool, skill pack, MCP server, simulator, or reference repo is added
user identifies a recurring workflow mistake
major milestone completes and the workflow should be simplified or hardened
```

Recurring-learning output must be small and actionable:

```text
trigger:
source_slice:
observed_project_failure:
adopt:
reject:
target_docs:
patch_or_no_patch:
review_required:
next_trigger:
```

Use `Docs/Index/external_learning_index.md` as the compact source inventory.
Do not store raw session dumps, prompts, provider configs, secrets, or huge
logs in durable docs. If no project rule improves, record `patch_or_no_patch:
no_patch` with evidence and stop.
