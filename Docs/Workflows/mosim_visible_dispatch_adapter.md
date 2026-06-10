# MoSim Visible Dispatch Adapter

> Host-project adapter for MoSim visible-department dispatch. Portable packet,
> SLO, semantic-boundary, and local-planning fields live in
> `CoAgent/dispatch/communication_contract.md`. This file records the
> MoSim-specific domain gates that must stay with the host project when
> `CoAgent/` is migrated elsewhere.

Status: active adapter, 2026-06-10 CST.

## 1. Boundary

This adapter is not a replacement for the communication contract. It is the
host landing surface for rules that should not become generic CoAgent policy:

```text
MWORKS/Sysplorer/Syslab engineering evidence
ROS2/RViz2/FAST-LIO runtime boundaries
UE editor/runtime/build/review boundaries
Sunray150 asset/PBR and geometry freeze rules
MoSim thread ids, board rows, packet paths, and current PMO priorities
```

During migration, do not remove additional MoSim-specific rules from portable
CoAgent files until this adapter or another host document contains an audited
exact or equivalent copy and the migration map records the landing.

## 2. Source Map

| MoSim Domain Rule | Current Source | Adapter Role |
|---|---|---|
| Generic visible-thread packet fields, dispatch ticket SLO, semantic boundary, local goal, `subagent_plan`, durable-start requirement | `CoAgent/dispatch/communication_contract.md` | Reference only; remains portable. |
| R2/R3 failover scope and forbidden live actions | this adapter, `Docs/Workflows/coagent_ops_patrol_workflow.md` | Host specialization for MWORKS/ROS2/UE R1/R2/R3 route sets. |
| MWORKS live gate, activation/window/license blockers, phase screenshots, engineering-output requirements | this adapter, `Docs/Workflows/coagent_ops_patrol_workflow.md`, `Docs/Skills/Mworks/*` | Host-local; do not generalize into portable CoAgent policy. |
| ROS2/RViz2/FAST-LIO source-window, probe budget, forbidden-topic, cleanup, and planner/controller claim boundaries | this adapter, `Docs/Workflows/ros2_runtime_setup.md`, `Docs/Workflows/new_conversation_context.md` | Host-local runtime adapter. |
| UE source-static/build/editor/runtime/manual-review boundaries and no controller/planner-success claims | this adapter, `Docs/Workflows/unreal_renderer.md` | Host-local renderer/runtime adapter. |
| Sunray150 DAE/PBR/source asset route, geometry freeze, material-review evidence, no dynamics/extrinsic/controller changes | this adapter, `Docs/Workflows/new_conversation_context.md`, Sunray-specific design/workflow docs | Host-local asset adapter. |

## 3. Dispatch Packet Rule

Every non-trivial MoSim visible-department dispatch must include both:

```text
portable control-plane fields from CoAgent/dispatch/communication_contract.md
host domain gate from this adapter or the named MoSim workflow/skill
```

A packet is incomplete if it has only JSON/control-plane evidence for work that
requires engineering evidence. MWORKS, ROS2, UE, and Sunray/PBR departments
must return artifacts that match their domain claim: model files, checks,
simulations, logs, screenshots, runtime probes, build evidence, review images,
or blockers with the concrete failed gate.

## 4. Domain Gates

Use the matching MoSim domain gate in addition to the generic CoAgent
local-planning block. These gates must be present in the dispatch prompt, not
only remembered by PMO.

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

### MWORKS / Sysplorer / Syslab

For every task dispatched to a MWORKS/Sysplorer/Syslab department, the task
packet must include a MWORKS live gate. Routine activation/window-health patrol
is owned by `MoSim｜CoAgent运维平台` through its 10-minute automation, so MWORKS
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
work and use task-local API/check/simulation success only as license
sufficiency for that task. Do not claim permanent account activation unless an
API/result explicitly reports account activation status.

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

MWORKS window action split:

- Activation/license/login/window-health audit is an audit task, not ordinary
  phase evidence. It requires the reusable target main window to be foreground
  or maximized, because background capture can miss hidden login/license panes.
  If no reusable main window exists, CoAgentOps opens MWORKS directly and then
  captures/rechecks; it must not end the patrol by only reporting that the
  window is missing.
- Ordinary non-activation phase screenshots, diagram/layout captures, and
  approved low-risk background clicks should use the background Win32
  `PrintWindow` route and normally do not maximize the window. The canonical
  script is `Scripts/tools/capture_window_background.ps1`; it is not a Windows
  MCP foreground desktop screenshot. If the target was minimized and full-window
  review is required, use `-RestoreMinimized -Maximize -MaximizeWaitMs 500
  -MinimizeAfter`, then verify the manifest `dpi_awareness`, physical
  `capture_width`/`capture_height`, and that the window was minimized after
  capture. If the task only needs ordinary background evidence, do not maximize
  solely for appearance.
- Cold start screenshots are first evidence only. A first screenshot shortly
  after launch may show blank/loading content; take the first screenshot after
  5 seconds, then use bounded follow-up screenshots or sentinel/window evidence
  before declaring healthy or blocked.

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
foreground. Delegated departments must not perform login/license recovery
themselves; they return a blocker. PMO or CoAgentOps may perform a bounded
foreground recovery on the existing window first, then prove success before
live MWORKS work resumes. Login/license patrols require maximized
target-window evidence: the screenshot must visually show the target reusable
MWORKS/Sysplorer/Syslab main window, not Codex, another application, a
helper/proxy window, or incomplete background `PrintWindow` output. If no main
window exists, CoAgentOps opens MWORKS directly and rechecks. If the official
login action does not return or cannot complete on the existing window,
PMO/CoAgentOps may reopen MWORKS and log in through the official UI as a
bounded recovery.

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

## 5. Failover Adapter

Default R2 failover classes stay limited to:

```text
source_static
diagnostic_only
packet_contract_fix
rule_sync_only
checker/review
```

MoSim R2 failover must not perform:

```text
MWORKS live work
ROS2/RViz2/FAST-LIO live work
UE runtime/build/editor work
GUI clicks
login/authorization/save/restart actions
setpoint publication
```

R3 is reserve capacity only after PMO proposes or approves it because R2
failover still leaves a P0 partition idle or blocked.

## 6. Migration Safety

This adapter exists to prevent semantic loss during the CoAgent portable split.
Before any domain text is removed from `CoAgent/dispatch/communication_contract.md`
or a MoSim startup document, the editor must record an audit row:

```text
source block:
landing file and section:
status: exact | equivalent | intentionally_host_local | obsolete_superseded | missing
reviewer:
date:
```

If the status is `missing` or `equivalent` with weakened stop conditions,
restore the source block or patch the landing before slimming.
