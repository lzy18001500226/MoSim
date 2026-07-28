# AGENTS.md

> Project instructions for Codex / AI assistants working on MoSim, the A8
> quadrotor attitude and position-control project.

This file is the compact project constitution. Keep durable hard boundaries
here. Put executable procedures, MWORKS window rules, runtime checks, and
domain-specific workflows in the linked documents below.

## Current Task

Fast entry cue, 2026-07-28 CST: G0 of the user-authorized 48-controller
MWORKS closed-loop line passed. `Px4CtrlFormalRunner` completed `ClimbPath`
for 50 s with a native `CheckModel` diagnostic of 0 errors and 0 warnings;
the original baseline evidence is
`Results/control_platform/px4ctrl_baseline_verification/` (RMSE 0.276705 m,
terminal position error 0.002734 m). The bounded px4ctrl graphical-completion
subgate also passed: the native `PX4CTRL_Original_OuterLoop_Graphical_Sysblock`
diagram has reviewable components and wires, and the hash-bound equation-bridge
runner replayed `ClimbPath` for 50 s with 5001 finite samples, RMSE 0.276705 m,
and terminal position error 0.002734 m. Its evidence is
`Results/control_platform/px4ctrl_graphical_completion_20260728/`; this remains
MWORKS equation-bridge closure evidence only, not PX4, Gazebo, ROS, or C++
deployment equivalence. G1-0 reconciled the 48-entry catalog;
G1 Batch 1 then added seven linear/robust controller routes and passed native
`CheckModel` for its eight Bridges and seven Adapters without source drift.
G1 Batch 2 then added five nonlinear/adaptive routes and passed native
`CheckModel` for its five Bridges and five Adapters without source drift; its
evidence is `Results/control_platform/g1_batch2_checkmodel_20260728/`. G1
Batch 3 then added five approved sliding-mode routes and passed native
`CheckModel` for all five Bridges and five Adapters without source drift; its
evidence is `Results/control_platform/g1_batch3_checkmodel_20260728/`. G1
Batch 4 then added six approved predictive/optimization routes through one
shared kernel, six named Bridges, and six Adapters; native `CheckModel` passed
all 13 classes without source drift, with evidence at
`Results/control_platform/g1_batch4_checkmodel_20260728/`. G1 Batch 5 then
added `SE3 Basic`, `DFBC Basic`, `DFBC SmoothRobust` attitude/body-rate, and
`DFBC HighOrder` body-rate routes as five named Bridges and five thin Adapters;
native `CheckModel` passed all 10 classes without source drift, with evidence
at `Results/control_platform/g1_batch5_checkmodel_20260728/`. G1 Batch 6 then
added the `GainScheduled PID`, `Fuzzy PID`, `Neural PID`, and `RL GainScheduler`
routes as four Bridges and four thin Adapters; native `CheckModel` passed all
eight classes without source drift, with evidence at
`Results/control_platform/g1_batch6_checkmodel_20260728/`. G1 is structurally
complete. The user-authorized G1 FormalRunner-completion subgate has passed
native `CheckModel` for 40 named 100 Hz whole-aircraft runners and four
reusable interface templates: 29 `ATTITUDE_THRUST`, eight `ROTOR_COMMAND`,
two `BODY_RATE_THRUST`, and one `WRENCH`. The final check-only evidence is
`Results/control_platform/g1_formal_runner_checkmodel_20260728/attempt_02_after_rotor_annotation_fix/CHECK_MODEL_RESULTS.json`
(44/44 passed; no simulation started and no source drift). G1 remains under
review. On 2026-07-29 CST, the user explicitly authorized one bounded exception:
run only `OfficialPidFormalRunner` and `Px4CtrlFormalRunner` against all seven
versioned profiles (14 MWORKS runs), retaining valid and invalid evidence alike.
At that point the exception did not authorize G2, other-controller runs, gain
tuning, code export, Gazebo/ROS runtime validation, G7, or R1.


The six-candidate recovery record at
`Results/control_platform/champion_candidate_recovery_20260727/` predates the
shared reference-velocity/reference-acceleration repair. Its `ClimbPath`
passes and RMSE are trace-back evidence only, not a valid ranking for the
current source. The user-approved seven-scenario contract is now bound through
the Plant and four shared Runner classes; the Official PID has a 0.01 s
external hold harness. Static validation and native `CheckModel` passed for
eight trajectories, four shared Runners, Official PID, and six champion Formal
Runners. The static preflight evidence is
`Results/control_platform/seven_scenario_preflight_20260727/`. The active
evidence root is `Results/control_platform/seven_scenario_ab/`. All 14 scoped
records now exist: six px4ctrl cases are valid; the px4ctrl motor-fault case and
all seven Official PID cases are retained as invalid evidence. The 14-row
matrix is `SCENARIO_RMSE_MATRIX.pending_syslab.json`; the raw-trace injection
checks retain both passed and not-evaluable states. Commit, push, send the
review email, and stop. Do not launch further MWORKS cases on this line.

On 2026-07-29 CST, the user subsequently authorized G2: one nominal 50 s
`ClimbPath` attempt for every one of the 48
`MoSimQuadrotorModel.Experiment.Runners.Formal.*` entries, with no scenario
injection, gain tuning, model edits, or seven-scenario work. The batch is
complete at `Results/control_platform/phase2_full_48_climbpath/`: all 48
routes have terminal records against frozen matrix
`a9f85d8cb8b4b942b88056bf4eb336ba17a9c40b26fe1ae5d21ab12649599d80`.
Seventeen passed the terminal-error gate and 31 failed: 10 terminal-error
violations, four simulation-API failures, nine MCP timeouts, and eight
dedicated Sysplorer-session startup failures. This is a result-screening
record, not authorization to repair failures, enter G3, rerun any route, tune
gains, export code, or start a new scenario. Commit the exact G2 evidence
index, push, send the Chinese review email, and wait for the next instruction.
`Docs/Workflows/mainline_operations_board.md` is the sole task authority and
contains the exact scope, evidence, and stopping/handoff conditions. Update this
cue whenever that board's current action or next executable gate changes; it is
an entry summary, not a second task source.

## 0. Start Here

For every new or resumed MoSim conversation:

```text
1. AGENTS.md
2. Docs/Workflows/new_conversation_context.md
3. Docs/Workflows/mainline_operations_board.md
4. Docs/Workflows/single_thread_operating_model.md when operating mode is unclear
5. Topic-specific workflow / skill / design docs only as needed
```

Use `PROGRESS.md` only for newest active entries, not as a full transcript.
Read `Docs/Workflows/agent_task_ledger.md` only for legacy trace-back during
old multi-thread cleanup or historical packet audit.

Do not load raw Codex session JSONL files or old chat dumps as routine context.
Historical chat claims must go through
`Docs/Workflows/session_memory_migration.md` before becoming project
truth; MoSim cache paths are documented in
`Docs/Workflows/session_memory_migration.md`.

## 1. Hard Boundaries

1. Work only inside `C:\Users\HP\Desktop\MoSim` unless the user explicitly
   approves a named infrastructure action outside the repository. Project-local
   means do not read or modify sibling personal directories, token files,
   browser profiles, SSH folders, other drives, `/home/linux`, or WSL/user
   home paths unless the approved infrastructure task names that path and why.
2. MoSim uses one active coordinating Codex thread. The coordinating thread can
   use official temporary subagents for independent, bounded work when
   parallelism materially helps. Legacy multi-thread routing, visible-thread
   dispatch, and related automation are archive-only material: use them only for
   explicit trace-back or cleanup, and do not restore them without user approval.
3. The coordinating thread owns product priority, scope, integration, manual/GUI
   action decisions, restart decisions, and blocker escalation to the user. If
   the current task needs an architecture or scope decision not already covered
   by the board or a design document, stop and report it to the user; do not
   make that decision independently.
4. Non-trivial work should record a local goal, inspect the smallest relevant
   context, run targeted checks, and keep evidence in normal project paths.
   This is local planning only, not a legacy multi-agent dispatch requirement.
   Temporary official subagents need an independent bounded scope and a parent
   integration point; parallel writes, Git mutations, GUI, MCP, or live runtime
   work need explicit ownership and coordination in the parent task.
5. Sparse Chinese email is the default human notification channel. When any
   named small task, goal, gate, or project conversation reaches a completion,
   blocker, or review-required terminal state, send one short Chinese email
   through `Scripts/agent/send_gateway_email_alert.py`. Do not email every
   ordinary chat reply, status update, or intermediate observation. Use a
   task-specific cooldown key, and disable cooldown for explicit terminal
   notices when needed so separate small tasks are not suppressed. Deleted
   WeChat gateway/message-path threads are historical only and must not be
   scanned, no-oped, recovered, or used unless the user explicitly restores a
   scoped WeChat diagnosis route.
6. The current P0 is always the action declared by
   `Docs/Workflows/mainline_operations_board.md`. The ROS1/Sunray/Gazebo/PX4/
   MAVROS/px4ctrl/RViz lane is the current runtime evidence authority when the
   board and its workflow select runtime work. UE/frontend remains a display and
   experiment-platform layer, not control-loop authority. Do not use the old
   ROS2/PX4/x500 route, replacement FAST-LIO source, fake point clouds, or an
   equivalent-substitute runtime as current evidence. Support lanes cannot mask
   the active engineering blocker.
7. MWORKS login/license/authorization/GUI-error/unknown blocking states must
   stop solver/model work and become clear blockers. Bounded login recovery is
   allowed only when the user explicitly authorizes it and credential
   redaction, screenshot, and stop-condition rules are satisfied.
8. Desktop window observation and desktop window action are separate skills:
   screenshot/capture ability does not imply click/action authority.
9. For normal MoSim mainline work, request `gpt-5.5` and `thinking=high` when
    the native tool accepts those settings.
10. Live/runtime waits must follow the bounded wait policy in the current
    runtime workflow or execution checklist. Do not let a live probe become an
    unbounded blocking loop without explicit user authorization and durable
    partial evidence.
11. Temporary broad `.gitignore` rules for reference imports are only a drain
    queue. Durable ignores must be class/exact-risk decisions, not a hidden
    backlog of ordinary source, docs, scripts, configs, or small assets.
12. Do not delete or move executable legacy runtime, hook, checker, protocol,
    skill, or automation code until a separate dependency audit proves it is
    unused or updates all references. The current cleanup target is active
    documentation and startup context first.
13. A task is not complete while task-owned changes remain uncommitted or
    unpushed. Before reporting terminal success, inspect only the task paths,
    run the relevant checks, stage exact paths, commit, push, and verify the
    upstream state. A noisy unrelated worktree or a large `References/` backlog
    is not a reason to defer normal source, script, config, model, or document
    changes. If ownership is unclear, checks fail, or publication is blocked,
    report a Git blocker instead of claiming completion. Never sweep unrelated
    user changes into the task commit to satisfy this gate.

## 2. Current Operating Mode

Current MoSim work is coordinated by one active thread. It follows
`Docs/Workflows/mainline_operations_board.md` and only the relevant domain
workflow; temporary subagents may own independent bounded slices. Historical
multi-thread material stays in `Docs/Cache/agent_legacy/` unless trace-back or
cleanup is explicitly requested.

## 3. Operating Documents

| Need | Source Of Truth |
|---|---|
| Current PMO board and next action | `Docs/Workflows/mainline_operations_board.md` |
| Current coordinating-thread operating model | `Docs/Workflows/single_thread_operating_model.md` |
| Declared ROS1 Sunray/Gazebo/PX4/MAVROS/px4ctrl runtime evidence lane | `Docs/Design/架构.md`; `Docs/Workflows/mainline_operations_board.md`; `Docs/Workflows/sunray_ros1_current_runtime_lane.md`; execution checklist at `Docs/Workflows/sunray_ros1_execution_checklist.md`; source index at `Docs/Index/sunray_migration_index.md` |
| Legacy AgentOS / multi-thread cleanup review | `Docs/Cache/agent_legacy/legacy_coagent_cleanup_plan_20260624.md` |
| Document placement, migration, and archive rules | `Docs/Workflows/documentation_governance.md` |
| Session-memory promotion/rejection | `Docs/Workflows/session_memory_migration.md` |
| Workflow index | `Docs/Index/workflow_index.md` |
| Historical/recovery project memory index | `Docs/Index/project_work_memory_index.md` |
| API/MCP index | `Docs/Index/api_index.md` |
| MCP/tooling/native hook governance | `Docs/Workflows/tooling_assets_governance.md`; hook code remains at current executable paths until audited |
| Desktop window screenshot evidence and explicitly authorized UI actions | `Docs/Skills/Desktop/window-capture-evidence/SKILL.md`; `Docs/Skills/Desktop/window-ui-action-control/SKILL.md` |
| Final competition packaging checklist | `Docs/Workflows/pre_submit_check.md` |

## 4. Project Direction

MoSim is for the A8 quadrotor competition. The main contribution is robust
quadrotor attitude and position control, not a general robotics navigation
stack.

Current delivery convergence:

```text
completed: canonical model root, D1-D3 review contract, and the frozen
           46-route current-root evidence matrix
  -> six nominal-family champion test-harness promotion and minimum
     whole-aircraft closure
  -> same-parameter Official PID seven-scenario A/B for accepted champions
  -> G7 safety, fault, fixed-formation, and Syslab evidence
  -> accepted candidate export and declared ROS1/Sunray runtime validation
  -> report and software-documentation evidence
  -> R1 old-root archival only after a dependency audit
```

Core principles:

1. Keep control as the main line.
2. Keep planning, formation, MCP automation, safety filtering, fault injection,
   and metrics as replaceable modules.
3. Every claim needs evidence: source, simulation logs, result files, metrics,
   screenshots, figures, or packets.
4. Documentation fixes are not project completion unless the task is explicitly
   docs-only; after correcting a workflow, return to the smallest executable
   evidence gate that moves the current mainline forward.
5. Prefer reproducible workflows and report-ready outputs.
6. Do not guess APIs; consult docs, workflows, skills, or MCP documentation.

## 5. Domain Evidence Boundaries

MWORKS/Sysplorer/Syslab is the formal controller/model evidence source.
Current runtime plant, sensor, and flight-control evidence comes from
Ubuntu-20.04 / ROS1 Noetic / Sunray / Gazebo Classic / PX4 / MAVROS / px4ctrl.
RViz is the current point-cloud, trajectory, map, and frame review surface.
UE/frontend work is a display, experiment-platform, video, and review
enhancement layer; it does not replace Gazebo/PX4/MAVROS/RViz/log evidence and
does not own controller, localization, or planner success. ROS2/RViz2/PX4 x500
routes are historical/future reference unless explicitly reopened. None of
these layers may claim final closed-loop success without the evidence required
by its current workflow.

Important MWORKS rules:

- Use MCP first for model-level operations when live MWORKS work is authorized.
- Check current MWORKS activation/window evidence before live MWORKS work.
- Activation/login/license/authorization acceptance needs foreground or
  maximized target-main-window evidence when a hidden UI blocker is possible.
- Ordinary live-simulation phase screenshots use the DPI-aware background
  capture route. If the target is minimized, restore it only enough to paint,
  capture, validate size/content, and minimize after; do not maximize except
  for activation/login/license/authorization evidence.
- Ordinary graphical/layout/result-window review uses DPI-aware screenshot
  evidence plus written observations in the coordinating thread. Temporary
  subagents do not own GUI review unless the current task explicitly scopes it.
- Do not close or restart reusable Sysplorer/Syslab/MWORKS windows unless the
  user/PMO explicitly authorizes it or a documented blocker requires it.

Important ROS/Sunray/UE rules:

- Do not claim `planner_ready`, `closed_loop`, runtime success, controller
  performance, or final material/scene acceptance without the declared evidence
  gate.
- Unreal Mapping Window Rule: active point-cloud/map review belongs to
  RViz/RViz2 or an equivalent native robotics viewer, with the current runtime
  evidence lane using ROS1 RViz. Browser HTML is not an accepted active
  point-cloud/map review surface.
  Global UE collision/occupancy truth is a validation oracle only.
- Do not publish setpoints, run extra live probes, open foreground RViz/manual
  review, or start UE editor/build/runtime work unless the current user
  instruction, local goal, and owning workflow explicitly authorize that live
  scope.
- Use local references first for matching UE/UAV simulation behavior patterns
  before online research.

## 6. Skills And Workflows

Use project-local MWORKS skills before generic upstream skills:

| Need | Skill / Workflow |
|---|---|
| MCP/session operations | `Docs/Skills/Mworks/mworks-mcp-operations/SKILL.md` |
| Model/component context | `Docs/Skills/Mworks/mworks-model-context/SKILL.md` |
| Simulation evidence | `Docs/Skills/Mworks/mworks-simulation-evidence/SKILL.md` |
| Runtime diagnostics | `Docs/Skills/Mworks/mworks-runtime-diagnostics/SKILL.md` |
| Sysblock graphical modeling | `Docs/Skills/Mworks/mworks-sysblock-graphical-modeling/SKILL.md` |
| Syslab/MATLAB porting | `Docs/Skills/Mworks/mworks-syslab-porting/SKILL.md` |
| Tests and review | `Docs/Skills/Mworks/mworks-test-quality/SKILL.md` |
| Report figures/replay | `Docs/Skills/Mworks/mworks-report-visualization/SKILL.md` |
| Current Sunray ROS1 / Gazebo / RViz runtime review | `Docs/Workflows/sunray_ros1_current_runtime_lane.md`; `Docs/Workflows/sunray_ros1_execution_checklist.md` |
| UE/frontend visualization enhancement, S11 display, and review media | `Docs/Workflows/unreal_renderer.md` |
| Historical/future ROS2 runtime | `Docs/Workflows/ros2_runtime_setup.md` |
| Parameter identification | `Docs/Workflows/identify_quadrotor_parameters.md` |

Use only the workflow/skill needed for the current task. Do not bulk-load large
documentation trees.

## 7. Git And Documentation Hygiene

For normal project changes:

```text
inspect status -> inspect relevant diff -> run targeted checks -> path-limited
git add -> git diff --cached --check -> commit -> push if auth works
```

Rules:

1. Use path-limited Git commands; do not use broad `git add -A`, force push,
   reset, clean, or bulk destructive commands unless explicitly approved.
2. Do not commit secrets, private tokens, local credentials, or generated files
   above GitHub limits.
3. When a task reveals a reusable command, workflow correction, or operating
   constraint, update the appropriate project document before reporting
   completion.
4. Keep `AGENTS.md` small. If a rule becomes executable or detailed, move it
   to a workflow, skill, checker, packet template, or index and leave only a
   pointer here.
5. The per-task Git closeout gate in `Docs/Workflows/pre_submit_check.md` is
   mandatory for every task that changes project files.

## 8. Directory Map

| Directory | Purpose |
|---|---|
| `Docs/Design/` | Algorithm, architecture, scope, and evidence design. |
| `Docs/Workflows/` | Repeatable procedures, current coordinating-thread operating rules, and domain workflows. |
| `Docs/Cache/` | Review caches, migration notes, archived workflow bodies, and non-startup historical material. |
| `Docs/Skills/` | Project-local and reference skills. |
| `Docs/Index/` | Documentation, API, memory, and workflow indexes. |
| `Models/` | Project-owned MWORKS/Sysplorer models. |
| `References/` | Official/reference projects and upstream examples. |
| `Config/` | Machine-readable project config: scenarios, ExperimentProfiles, capability index, and legacy/design protocol snapshots. |
| `Scripts/` | Automation, quality checks, evidence scripts, and tests. |
| `Results/` | Reproducible outputs, packets, metrics, logs, figures, and review assets. |

## 9. Final Development Policy

When uncertain:

1. Prefer current project documents over chat memory.
2. Prefer small targeted checks over broad assumptions.
3. Prefer source/current evidence over inherited claims.
4. Prefer modular, reversible changes over coupled rewrites.
5. Prefer clear blockers over overclaiming completion.
6. For runtime/integration failures, do not switch to a substitute mainline to
   make progress look successful. First inspect local source and official
   docs; if still unclear, search relevant blogs/community notes. If the issue
   remains unresolved, the next step would change the agreed architecture, or
   the fix requires a broad/high-risk runtime change, stop, report the blocker,
   and ask the user before changing direction.

The project is successful when it forms a reproducible loop:

```text
scenario configuration
  -> model simulation
  -> result extraction
  -> metric calculation
  -> figure/replay generation
  -> report conclusion
```
