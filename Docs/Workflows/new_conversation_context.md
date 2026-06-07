# New Conversation Context

> Purpose: give a fresh Codex conversation enough current context to continue
> MoSim work without loading the old 2 GB chat transcript.

Status: current recovery entry, 2026-06-04 CST.

2026-06-07 automation prompt size hotfix: keep recurring automation prompts as
small triggers that read `AGENTS.md`, this file, the ledger, and the relevant
workflow/skill docs at runtime. Do not encode every incident rule into the
automation body. When a reusable rule changes, update the canonical document or
template; update an automation only when its cadence, owner, routing, or
high-level trigger is wrong.

2026-06-07 Sunray150 visual material acceptance hotfix: the user clarified
that the Sunray/PBR 005 DAE-derived Blender material route was already manually
reviewed and acceptable as the current visual asset baseline. Do not resume
broad Sunray150 texture/PBR optimization from the later 006 whole-aircraft
grey-CAD pass. The 006 pass is a regression/rollback incident, not an accepted
baseline. Treat `pbr006_*` objects/materials/overlays and 006 manifests as
rejected experiment evidence unless a future user review explicitly accepts
them. Recovery target is the 005-approved Blender audit asset with zero
`pbr006_*` objects/materials, plus a concise rollback closeout packet.

2026-06-07 context-compression surface hotfix: a stalled visible thread may be
caused by Codex App context-compression UI state rather than a failed
department agent loop. If the UI shows an abnormal compression state such as
`Context Left 100.0%` and the user/manual operator can see that slash-command
compression is needed, notify the user and record the issue as
`codex_context_compression_surface`, not as an immediate dead-thread restart
case. User-confirmed recovery steps: switch to `gpt-5.4` + `xhigh`, type `/`,
choose the compression command, wait for compression, then switch back to
`gpt-5.5` + `xhigh`. After recovery, use one no-op or expected-packet check to
restore routing. Do not use Computer Use for this path.

2026-06-07 email-default notification hotfix: WeChat outbound can lose usable
send context after several hours, so MoSim user notifications now default to
sparse Chinese email. P0 dead-thread recovery and MWORKS/Sysplorer/Syslab
activation, login, license, authorization, hidden-login-pane, or GUI-error
incidents must attempt sparse email and record the email audit. WeChat is not a
routine progress, completion, human-intervention, or restart-notice channel; use
it only for explicit WeChat gateway diagnosis, a user-requested WeChat retry,
or a current task that specifically validates the WeChat gateway. Before any
planned Codex++ restart for a dead-thread incident, the still-healthy mainline
must write the recovery packet, attempt email, and record the audit. The
notification is a handoff window, not an approval wait: if the user is online,
the user may restart Codex++ manually faster; otherwise, after the email
attempt is recorded, the still-healthy mainline continues the authorized
restart route unless PMO/user has explicitly written a deferral.

2026-06-07 WeChat gateway retirement hotfix: the user archived
`MoSim｜微信网关运维部` (`019e9c7d-a8bd-7dd1-ad94-6feef5a07e9c`) after moving
MoSim notifications to email-only. PMO and CoAgentOps must not schedule or run
periodic WeChat gateway self-checks, no-op probes, canaries, or `ret=-2`
recovery. The archived gateway thread and `MoSim｜WechatCodex` are historical
only unless the user explicitly restores WeChat diagnosis as a new scoped task.

2026-06-07 MWORKS activation evidence hotfix: any activation, login, license,
authorization, or hidden-login-pane patrol claim requires maximized or
foreground visual evidence of the target reusable MWORKS/Sysplorer/Syslab main
window. The screenshot content must match that target window; screenshots that
show Codex App, another application, a helper/proxy window, or only minimized/
background `PrintWindow` output are auxiliary evidence and cannot prove
activation. If target-window content match is missing, classify the state as
unknown/blocked or ask PMO/CoAgentOps for a proper foreground review before
restoring live MWORKS routing.

2026-06-07 model-effort default: MoSim mainline, visible department, and
disposable sub-agent creation/dispatch should use `gpt-5.5` with `xhigh`
thinking whenever the current Codex tool or runtime accepts explicit settings.
Do not wake healthy existing threads just to rewrite settings; apply the rule
to future create/dispatch/automation/spawn calls. Dead-thread no-op probes keep
settings omitted unless the recovery task explicitly tests settings update.

2026-06-07 dispatch-surface incident ownership hotfix: visible department
start-turn or agent-loop failures belong to `MoSim｜CoAgent运维平台`
(`019e9bc1-ea9f-7102-b41a-4ef9b2308992`) after PMO writes the initial blocker.
PMO must not keep using the failed department as an accident-sample worker or
continue business validation there before CoAgentOps classifies the surface.

2026-06-07 heartbeat fail-close hotfix: an open P0 dead-thread recovery packet
is not a routine pending item. If a PMO/CoAgentOps heartbeat sees pending
notifications, pending restart, pending post-restart validation, or
`still_quarantined`, it must execute the next authorized recovery step. For a
notification/restart-pending visible-thread death, it must attempt sparse
email, record the audit, and trigger the authorized Codex++ restart route. It
writes blocker/request and `NOTIFY` only when a required
tool/surface is unavailable, the action fails, or PMO/user explicitly deferred
the incident. It must not finish as healthy, return
`DONT_NOTIFY`, or proceed to P1 meta-optimization until the P0 path is closed
or explicitly deferred by PMO/user.

2026-06-07 completed-without-response hotfix: native `read_thread` and
`send_message_to_thread` success are only transport evidence. They do not
prove a department is recovered or routable. If a visible thread receives a
turn but does not produce an agent final reply, exact no-op text, or the
expected result/blocker packet within the bounded validation window, treat it
as a dispatch-surface/agent-loop failure. A turn marked `completed` with only
the user prompt and no agent response is not healthy; keep that thread
quarantined and let the still-healthy mainline own recovery.

2026-06-07 visible-title normalization hotfix: active visible-thread names and
statuses come from `CoAgent/dispatch/department_threads.json`. The former
WeChat gateway thread `MoSim｜微信网关运维部`
(`019e9c7d-a8bd-7dd1-ad94-6feef5a07e9c`) is archived by user decision after
MoSim notifications moved to email-only, and `MoSim｜WechatCodex` is also not a
dispatchable route. The current ROS2 runtime production thread is
`MoSim｜ROS2感知定位与规划运行部-R1`. Historical R3/WeChat task IDs and evidence
labels are history only; do not use them for new active routing, automation
prompts, or replacement recommendations unless the user explicitly reopens
WeChat gateway diagnosis.

2026-06-07 large-Git ignore-drain hotfix: new conversations that resume Git
work must not infer completion from quiet untracked output or a quiet IDE
source-control pane. For crawled `References/` and `Docs/Skills/` projects,
temporary `.gitignore` throttles must be drained: reopen one source project or
major subdirectory at a time, check each batch for files at or above 100 MiB,
credentials, dependency/build/cache/runtime outputs, missing LFS payloads, and
generated artifacts, then stage/commit/push under the small-batch limit. The
final `.gitignore` should keep only durable class/exact-risk rules, not a
per-file backlog of ordinary source/docs/scripts/configs/small assets.

2026-06-07 DevOps closeout correction: for crawled open-source project intake,
do not solve backlog by adding more ordinary file or source-extension ignores
such as Python, Markdown, C/C++, config, example, or small asset files. The
working rule is one source project or major subdirectory at a time: keep only
single files at or above 100 MiB, operator-local files, nested `.git`,
dependency folders, generated/build/cache/runtime output, archives, compiled
binaries, missing LFS payloads, or explicitly manifest-only asset classes
ignored; force-add and commit the remaining ordinary project content in
reviewed pathspec batches under the file-count ceiling. Generic classes such
as `*.zip`, `*.7z`, `node_modules`, `build`, `dist`, `.venv`, `__pycache__`,
`*.exe`, `*.dll`, `*.lib`, `*.pdb`, and `*.obj` belong in concise
`References/**` / `Docs/Skills/**` class guards, not repeated under each
project. A directory being hundreds of MB total is not a durable-ignore reason
when no individual file crosses the GitHub hard limit.

This file records only current effective decisions and known rejected routes.
It does not promote old chat history by itself. If a newly opened conversation
finds a historical claim that is not represented here or in the linked source
documents, route it through `Docs/Workflows/session_memory_migration.md` before
using it as project truth.

## 1. Read Order For A Fresh Conversation

Start with this short chain:

```text
1. AGENTS.md
2. Docs/Workflows/new_conversation_context.md
3. Docs/Index/project_work_memory_index.md
4. PROGRESS.md only for the newest active entries, not as a full transcript
5. Docs/Workflows/agent_task_ledger.md only for active delegated tasks
6. Topic-specific workflow/design docs linked below
```

Do not read raw Codex session JSONL files or old chat dumps as the first
recovery route. The current long MoSim conversation file is too large and can
destabilize Codex App / VSCode plugin rendering.

## 1.1 Historical Context Coverage

The long MoSim conversation has been migrated into a cache-first recovery set
for the currently identified important topic set. A new conversation should be
able to recover project direction, accepted/rejected routes, current evidence
boundaries, and active workflow routing from:

```text
Docs/Cache/session_memory_migration/coverage_matrix_20260604.md
Docs/Cache/session_memory_migration/round3_promotion_rejection_map_20260604.md
Docs/Cache/session_memory_migration/completion_audit_20260604.md
Docs/Cache/session_memory_migration/round2_core_competition_report_docs_memory_20260604.md
```

This does not certify every line of an old Codex JSONL transcript. It means the
identified important topics have cache files, current-evidence review, and
round-3 promote/reject/cache-only dispositions. If a new conversation discovers
a useful historical claim that is not covered by the files above or by the
topic-specific docs, route it through `Docs/Workflows/session_memory_migration.md`
before treating it as project truth.

## 2. Current Product Direction

MoSim is being developed as an RflySim-like UAV simulation system with strict
authority boundaries:

| Layer | Authority | Current Rule |
|---|---|---|
| MWORKS/Sysplorer/Syslab | dynamics, controller, planner, truth, metrics, report evidence | This is the formal simulation source. |
| UE5 / MoSimSceneLibrary | high-quality scene rendering, UAV visual, camera, video, sensor/collision oracle | UE must not decide controller/planner success. |
| ROS2 / RViz2 / FAST-LIO | LiDAR/IMU transport, TF, localization/map/planner review windows | Use native robotics windows, not HTML/browser point-cloud demos. |
| CoAgent / WeChat | sparse progress and human-intervention channel | Useful but not the current MoSim technical mainline. |

Current agent/runtime entry point:

```text
primary Codex conversation/config/history: Windows-native VSCode/Codex under C:\Users\HP\.codex
project workspace: C:\Users\HP\Desktop\MoSim
WSL runtime lane: ROS2, RViz2, FAST-LIO-family, rosbridge, Linux-native robotics tools
```

Do not move ROS2/FAST-LIO execution into Windows-native PowerShell unless a
later workflow explicitly approves a Windows ROS route.

Codex native global hooks are configured for MoSim through:

```text
C:\Users\HP\.codex\hooks.json
CoAgent/hooks/codex_native_hook.py
CoAgent/hooks/preflight.py
```

The hook adapter acts only when the current `cwd` is inside this repository. It
can block hard tool-use risks and inject a concise startup reminder, but it does
not replace this file, `AGENTS.md`, task-specific workflows, result packets, or
manual review gates. If a new Codex surface asks to trust the hook, use `/hooks`
after verifying the paths above.

Primary architecture references:

```text
Docs/Design/10_架构边界与当前状态ADR.md
Docs/Design/12_MoSimQuadrotorModel模型归档与迁移计划.md
Docs/Index/project_work_memory_index.md
Docs/Design/00_系统总体设计.md
Docs/Design/09_UE_ROS_MWORKS无人机仿真架构重构.md
Docs/Workflows/unreal_renderer.md
Docs/Workflows/ros2_runtime_setup.md
Docs/Workflows/identify_quadrotor_parameters.md
```

## 3. Current Valid Sunray150 Geometry State

Current accepted geometry comes from the user-reviewed DAE/Blender assembly
manifest:

```text
Results/unreal_scene_mapping/sunray150_dae_assembly_parameters_20260604.json
```

Effective rotor centers now used by MWORKS/SDF geometry:

| Rotor | Role | Position in body frame, m |
|---|---|---|
| rotor_0 | front-right | `(0.053745, -0.05374, -0.014052)` |
| rotor_1 | back-left | `(-0.053761, 0.05376, -0.014052)` |
| rotor_2 | front-left | `(0.053746, 0.053759, -0.014052)` |
| rotor_3 | back-right | `(-0.053761, -0.053739, -0.014052)` |

Other current geometry candidates from the same manifest:

```text
front camera: (0, 0.1032, 0.0185, 0, 0, 0)
down camera:  (0, 0.0145, -0.0263, 0, 1.5707963, 3.14)
base collision box pose: (0, 0.001574, 0.044965, 0, 0, 0)
base collision box size: (0.211502, 0.214651, 0.16193)
```

Important limits:

- Geometry migration changed rotor/camera/collision geometry only.
- It did not change mass, inertia, motor constants, thrust constants,
  controller gains, timing, or identified-parameter status.
- Current values remain `source=SDF_migration` unless a later ULog/bench
  identification bundle proves otherwise.

## 4. Current MID-360 Boundary

Do not collapse these quantities into one number:

```text
mechanical mount pose
point-cloud coordinate origin
built-in IMU position
FAST-LIO extrinsic_T
Gazebo/Sunray ray-sensor pose
```

Current confirmed Livox manual fact:

```text
MID-360 built-in IMU position in point-cloud frame:
(11.0, 23.29, -44.12) mm

FAST-LIO LiDAR pose in IMU body frame if axes are aligned:
[-0.011, -0.02329, 0.04412] m
```

Do not write a DAE mechanical mount center directly into FAST-LIO extrinsics.
Any MID-360 extrinsic change requires a separate coordinate-frame review.

## 5. Current MWORKS Dynamics State

Formal package ownership:

```text
References/MWORKS/QuadrotorModel/package.mo
  -> official/upstream baseline and regression reference; do not destructively
     rewrite it for MoSim-specific plant experiments.

Models/MoSimQuadrotorModel/package.mo
  -> project-owned formal Sunray150/MoSim quadrotor package. New formal
     dynamics, mission, controller, planning, robustness, scene-trace, system,
     formation, and support entry points should move here.

Models/QuadrotorExperiments/package.mo
  -> legacy experiment pool and compatibility source. Keep old flat names as
     aliases during migration so existing scenario YAML, scripts, reports, and
     evidence bundles do not break in one step.
```

The first `MoSimQuadrotorModel` package skeleton is intentionally an
`extends`/alias layer. It classifies existing experiments under stable
project-owned categories before destructive file moves or class renames. Each
later migration batch must update references, keep source/provenance labels,
and pass targeted `check_model` evidence before the old alias can be retired.

Main baseline file:

```text
References/MWORKS/QuadrotorModel/package.mo
```

Current `QuadrotorModel.Mechanics.QuadChassis` is still a simplified plant:

| Item | Current State |
|---|---|
| mass/inertia | `m=1.0`, `Ixx=0.0085`, `Iyy=0.0085`, `Izz=0.012` |
| rotor inertias | `m=0.005`, `Ixx=9.75e-7`, `Iyy=0.000173104`, `Izz=0.000174004` |
| thrust | per-rotor `WorldForce`, `lift_cofficient=0.000854858` |
| coefficient provenance | Sunray `motorConstant=8.54858e-06` scaled by `rotorVelocitySlowdownSim^2=100` |
| missing/weak | motor lag, command-to-speed mapping, yaw reaction torque, rotor gyroscopic moment, body drag, angular damping, contact/fault parameter layers |

RflySim is local and should be used as structure reference:

```text
References/RflySim/RflySimAdv3Full/4.HILApps/RflySimAPIs/RflySimAPIsPers.zip
  RflySimAPIs/4.RflySimModel/3.CustExps/e0_AdvApiExps/1.inCtrlExt/1.Matlab/
    MulticopterNoCtrl.slx
    MulticopterNoCtrl_init.m
    MulticopterModel.zip
```

Do not replace Sunray150 parameters with RflySim sample parameters. Use RflySim
to migrate model structure into a new wrapper or experimental chassis first,
then validate hover/yaw/step response before replacing the baseline.

Current MWORKS GUI/activation operating boundary:

```text
CoAgentOps 30-minute automation
  -> owns routine MWORKS/Sysplorer/Syslab activation and window-health patrol
MWORKS R1/R2 engineering departments
  -> reference the latest patrol and focus on model/check/sim/layout evidence
PMO or CoAgentOps
  -> may bring the existing MWORKS window foreground/maximized for full
     screenshot review or official login/license recovery when needed
```

Do not make every MWORKS engineering dispatch spend its turn repeatedly proving
activation. A `[教育版]` title is not activation proof, but it is also not a
standalone blocker. Departments stop only when the current task or patrol shows
demo/login/authorization/error evidence, or when no recent patrol exists and a
live MCP/GUI operation cannot be safely checked. Login/license patrols need
maximized-window evidence when a hidden login pane is possible; minimized
background captures are not enough for that case. Use the existing maximized
foreground window first. If official login does not return or cannot complete
on the existing window, PMO/CoAgentOps may reopen MWORKS and log in through the
official UI as a bounded recovery.

## 6. Current UE Vehicle Visual State

Accepted:

- DAE-derived geometry/assembly is the source route.
- Three-blade `sunray_cw.stl` visual propeller route is the current accepted
  visual propeller basis.
- Primitive UAV, giant cylinder, cube/cylinder fallback, MWORKS STL runtime
  animation, and procedural runtime vehicle mesh are not accepted vehicle
  review evidence.

Pending:

- Material/texture realism is not final. Previous broad PBR/simple-color
  attempts were rejected or remain audit candidates.
- Before UE export/import is called final, component-specific material closeups
  must be reviewed: MID-360, carbon frame, screws/standoffs, cameras,
  electronics/connectors/cables, motors/propellers, battery/payload, landing
  gear/guards.

Authoritative workflow:

```text
Docs/Workflows/unreal_renderer.md
Docs/Skills/Unreal/sunray-pbr-material-workflow/SKILL.md
```

## 7. Current UE/ROS2/FAST-LIO State

Rejected product routes:

- keyboard/grid-cell pose movement;
- fake/static point clouds;
- 2D-only grid map as UAV local map;
- browser/HTML point-cloud review as active evidence;
- hand-polishing RViz display parameters while the UAV/sensor stack is wrong.

Current accepted direction:

```text
MWORKS continuous truth/state
  -> UE scene/sensor oracle
  -> ROS2 LiDAR/IMU/TF
  -> native FAST-LIO / RViz2 windows
  -> truth-error and topic-rate evidence
```

Factory Gate B has passed a headless same-source/body-frame FAST-LIO gate and
opens manual UE/RViz review only. It does not prove final controller
integration, planner performance, scene acceptance, or product completion.

Before making a FAST-LIO/current-runtime claim, read:

```text
Docs/Workflows/ros2_runtime_setup.md
Docs/Design/09_UE_ROS_MWORKS无人机仿真架构重构.md
Results/unreal_scene_mapping/factoryenvironmentcollect/
```

## 8. Current CoAgent And WeChat Boundary

CoAgent is not the immediate MoSim technical mainline. Existing CoAgent docs
are useful for task orchestration, but new runtime/transport/schema/department
expansion remains gated.

Current multi-conversation operation is PMO-led direct dispatch. The main PMO
conversation sends complete task packets to existing visible Codex department
threads, or creates a new visible department thread when no reusable specialty
thread exists and durable context is needed. Treat visible threads as reusable
department surfaces, not disposable subagents. CoAgent dispatch/runtime tools
are supporting infrastructure for packet formatting, registry/visibility
checks, result import, recovery, and evidence validation; they are not a
mandatory dispatch-center middle layer for ordinary MoSim work.

Every cross-thread task packet must include at least:

```text
request_id
origin_thread and origin_thread_id
target_thread and target_thread_id when known
expected_return_path
blocker_return_path
read/write scope
forbidden actions
definition_of_done
```

The return surface is the project file packet under
`Results/agent_packets/returns/` or `Results/agent_packets/blockers/`. Chat
replies and email/WeChat messages are useful notifications, but they are not the
durable return channel.

Notifications are sparse Chinese human-facing email summaries. WeChat is no
longer a routine project notification channel because outbound context can
expire after several hours; keep it for explicit gateway diagnosis,
user-requested retry, or gateway validation tasks only. Notification delivery is
not proof, and email must not mirror transcripts or logs.

Thread route distinction:

```text
019e8358-86b4-7070-8fd6-a2b4f4d2af97 = MoSim｜WechatCodex
  Historical WeChat-side message path only. Not dispatchable under the current
  email-only notification policy.

019e9c7d-a8bd-7dd1-ad94-6feef5a07e9c = MoSim｜微信网关运维部
  Archived by user decision on 2026-06-07 after MoSim notifications moved to
  email-only. Do not dispatch or patrol this thread unless the user explicitly
  reopens WeChat gateway diagnosis.
```

Gateway route:

```text
CoAgent/gateway/cc_connect_weixin.py
```

If WeChat send fails during an explicit gateway-diagnosis task, diagnose once
according to `AGENTS.md` and record the failure under
`Results/coagent_gateway/`; do not retry in a tight loop or block ordinary
notifications on WeChat recovery.

## 9. Historical Routes Not To Resume

Do not continue these unless the user explicitly asks for an audit of the old
route:

| Route | Status |
|---|---|
| Reading the old 2 GB chat transcript as context | forbidden as routine recovery |
| Promoting old chat numeric parameters | forbidden without current file/result recheck |
| Manual propeller/radar tuning by eye as final assembly | superseded by DAE/source/manifest route |
| MWORKS STL / MWORKS animation as UE runtime UAV visual | rejected |
| Primitive cube/cylinder UAV fallback | rejected |
| Simple whole-aircraft coloring as "texture" | rejected |
| Opening `.blend` through Windows file association / Ansys / Visual Studio Blend routes | forbidden after wrong app dialogs |
| Directly treating RflySim parameters as Sunray150 truth | rejected |
| Directly treating DAE MID-360 mount pose as FAST-LIO extrinsic | rejected |
| HTML/browser point cloud as active mapping review surface | rejected |
| Fake point cloud / toy 2D grid / grid-cell movement | rejected except smoke/debug |
| Broad Git add over huge external trees | forbidden; use path-limited split batches |

## 10. Current Best Next Engineering Moves

Recommended next work after opening a new conversation:

```text
1. Do not resume from old chat memory.
2. Pick one active topic and read its workflow/design doc.
3. If working on dynamics:
   - create a new RflySim-style MWORKS wrapper/chassis first;
   - add motor lag and yaw torque before drag/gyro/contact;
   - validate hover, yaw, step, and short trajectory.
4. If working on UE vehicle:
   - use DAE-derived StaticMesh/FBX/GLB route;
   - keep geometry locked;
   - handle materials component by component.
5. If working on FAST-LIO:
   - start from latest same-source/body-frame Gate B evidence;
   - keep native RViz2 windows and truth-error gate.
6. If a historical claim appears useful:
   - add it to session-memory cache;
   - verify current files;
   - promote narrowly or mark rejected/superseded.
```

New conversations should treat this file as the short context pack and the
linked documents as the source of truth.

## 11. Codex Native Feature Use

Prefer Codex-native surfaces before expanding CoAgent:

| Need | Preferred Surface |
|---|---|
| Hard command/file guardrail | Native hook plus `CoAgent/hooks/preflight.py` |
| Durable project rule | `AGENTS.md` |
| Task-specific procedure | One workflow or skill loaded on demand |
| Live GUI/web/private-tool operation | Native plugin/app/MCP/Browser/Windows MCP |
| Recurring health check or reminder | Codex App automation or verified external scheduler |
| Durable specialty context | Visible Codex thread with result/blocker packet |
| Bounded parallel research/review | Sub-agent with explicit scope and stop condition |

Current dead-thread recovery policy: after CoAgentOps confirms a persistent
visible-thread start-turn/agent-loop failure through the bounded ladder, it
should write a blocker/recovery packet, attempt one sparse email notification,
record the audit result, then use the user-authorized Codex++ manager restart
surface when restart remains the
preferred recovery action and no explicit user/PMO deferral has arrived. The
notifications are meant to let an online user restart manually faster, not to
make the automation wait indefinitely. Do not create a replacement conversation by
default; replacement requires explicit PMO/user approval, repeated failed
restart recovery, or a critical path that cannot wait.

```text
D:\Program Files\Codex++\codex-plus-plus-manager.exe
```

Restart ends the current conversation. The 30-minute PMO/CoAgentOps heartbeat
automations are therefore the expected post-restart recovery route: read the
latest blocker, run no-op validation, and classify the affected thread as
`partial_recovery`, `restored`, or `still_quarantined`.

Heartbeat fail-close rule: before a heartbeat reports normal completion or
enters any P1 optimization audit, it must scan the current recovery packets for
open P0 dead-thread states such as notification-pending, restart-pending,
post-restart-validation-pending, or `still_quarantined`. Such a state blocks
`DONT_NOTIFY`. The heartbeat either continues the recovery under the documented
notification-before-restart order, including only a short manual-restart
window after the email notification is attempted, or writes a blocker/request packet only when
execution is blocked by missing tools, failed notification/restart action, or
an explicit PMO/user deferral; that packet must name the owner and next action.

CoAgentOps heartbeat must also actively look for new dead-thread surfaces in
the current visible allowlist. It should list/read current active departments
and only send a minimal no-op when there is evidence of dispatch-surface risk
or an explicit revalidation need. A confirmed start-turn/agent-loop failure is
itself a P0 fail-close incident: write recovery packet, send sparse email,
record the audit, give the user a brief chance to restart manually, and
otherwise trigger the authorized Codex++ restart. Because the
restart ends the current conversation, the next heartbeat owns post-restart
no-op validation and sends a concise PMO thread update with the restored /
partial / still-quarantined classification.

Self-dead limitation: if CoAgentOps itself is the dead thread, it cannot send
the notifications or trigger the restart from inside that failed turn. PMO or
another still-healthy mainline recovery surface must read the latest
blocker/heartbeat packet, attempt the mandatory sparse email notification, run the
authorized Codex++ restart route, and let the post-restart heartbeat revalidate
CoAgentOps with one no-op. Do not rely on the dead CoAgentOps thread to
self-rescue.
The same-thread CoAgentOps heartbeat is normal maintenance, not self-dead
protection. Current policy is dual-mainline cross-check only: PMO and
CoAgentOps each run their own thread-attached heartbeat, and whichever mainline
is still healthy handles blocker, sparse email notification,
short manual-restart window, Codex++ restart if no explicit deferral arrives,
and one post-restart no-op validation for the other. Detached
cron `mosim-coagentops`
and Windows scheduled task `MoSim-CoAgentOps-OuterWatchdog` were removed after
user review because they create a separate automation context and can pollute
the project or restart from indirect stale heuristics. If both mainlines or the
whole Codex App are dead, the user manually restarts Codex++; do not recreate an
external automatic watchdog by default. `Scripts/agent/codex_outer_watchdog.ps1`
is retained only as a manually authorized emergency helper for a written
incident.

Foreground desktop caution: Windows MCP `Snapshot` / `Screenshot` are not
background capture. They observe the user's active desktop and can catch
whatever the user is typing or viewing. For Codex++ restart and ordinary GUI
maintenance, use UI Automation/PowerShell/app APIs first; use visible desktop
screenshots only after warning the user or when explicitly authorized.
MoSim desktop GUI caution: Computer Use is deprecated for MoSim desktop GUI
monitoring, screenshots, recovery, and click workflows. Use Windows MCP,
Win32/UI Automation, and project-local PowerShell/Python scripts instead;
Browser remains the route for browser/local web targets.

Email notification format: keep the subject and body as short Chinese status
text. Do not copy concrete English file names, long paths, JSON/log names, or
raw evidence lists into user-facing notifications; those stay in
result/blocker packets and project evidence. Routine completion can use
`【MoSim 进度】`; manual intervention, incident, auth/license, GUI crash, or
dead-thread messages should use a clearly different header such as
`!!! MoSim 需要人工介入 !!!`.

Do not create CoAgent runtime machinery when a native Codex surface already
covers the need. CoAgent remains project glue for packets, evidence manifests,
gateway wrappers, recovery checks, and MoSim-specific orchestration conventions.
