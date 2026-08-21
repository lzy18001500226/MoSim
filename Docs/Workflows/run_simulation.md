# Run Simulation Workflow

> Purpose: run one MWORKS quadrotor simulation through Sysplorer MCP, export results, and prepare data for metrics and figures.

> **Current model entry rule (2026-08-21):** load only
> `Models/MoSimQuadrotorModel/package.mo`. Use current `Experiment/SingleUav`,
> `Experiment/Baselines`, `Experiment/Formation`, or `Experiment/OpenBlocks`
> entries and their `Control` cores. Any `Experiment.Runners.*` path appearing
> in older examples is historical provenance only; do not restore it from an
> archive. The current structural CheckModel batch is recorded in
> `Results/architecture_verification_20260821/CHECKMODEL_MWORKS_MCP.json`.

---

## Current Phase 1 Minimum Closure

Use this workflow only when the current user's direct request scopes the Phase
1 46-route minimum-closure matrix. The matrix owner is
`Scripts/mworks/run_phase1_minimum_closure.py`; its contract test is
`Scripts/tests/test_phase1_minimum_closure.py`.

Run only the frozen 50 s `ClimbPath` routes through the named driver. It writes
the matrix, per-route `RUN_RECORD.json`, metrics, and status below
`Results/control_platform/phase1_minimum_closure/`. A missing truthful adapter
is a terminal failure record, never a substituted controller-only simulation.
Do not use this section for champion selection, seven-scenario A/B, export, or
runtime validation.

---

## 1. Goal

Run a specified scene and controller, then save raw simulation results for analysis.

Example task:

```text
Run the figure8 scene with pid_baseline and save results to Results/official/example3_figure8/official_example3_pid_baseline/raw/official_example3_pid_baseline.csv.
```

---

## 2. Inputs

Required inputs:

```text
scene_id
controller_id
model_path or model_name
simulation_start_time
simulation_stop_time
result_output_path
```

Optional inputs:

```text
disturbance_config
trajectory_file
controller_params_file
result_variables
```

Recommended config format:

```yaml
experiment_id: official_example3_pid_baseline
scene_id: official_example3
controller_id: pid_baseline
model_name: MoSimQuadrotorModel.Vehicle.Examples.Example3
start_time: 0
stop_time: 30
step_size: 0.01

result:
  raw_file: Results/official/example3_figure8/official_example3_pid_baseline/raw/official_example3_pid_baseline.csv
  metrics_file: Results/official/example3_figure8/official_example3_pid_baseline/metrics/official_example3_pid_baseline.json
  figure_dir: Results/official/example3_figure8/official_example3_pid_baseline/figures

variables:
  - time
  - x
  - y
  - z
  - vx
  - vy
  - vz
  - roll
  - pitch
  - yaw
  - u1
  - u2
  - u3
  - u4
  - x_ref
  - y_ref
  - z_ref
```

---

## 3. Required MCP Tools

Use Sysplorer MCP tools in this order:

```text
activation sentinel / maximized target-window screenshot
  -> if clean, continue
  -> if login/license blocks live work, stop and return a blocker unless user-authorized bounded recovery is active
  -> stop on authorization error, GUI error-report, visible unknown, unavailable, or unsafe recovery state
session_manager
  → load_library
  → model_manager
  → check_model
  → simulate_model
  → result_manager
```

Optional tools:

```text
plot_manager
get_api_document
get_lib_model_document
resources_retrieval
```

Interactive model inspection, model checking, single-scenario simulation, and
GUI animation review must use MCP tools directly when MCP is healthy. Do not
wrap interactive `model_manager`, `check_model`, `simulate_model`,
`plot_manager`, or `result_manager` operations in project scripts. Project
scripts such as `run_mworks_scenario.py` and `run_sysplorer_mcp_smoke.py` are
only for batch execution, reproducible export, metrics, summaries, and
regression automation.

When driving the Sysplorer MCP wrapper through JSON-RPC, always perform the MCP
handshake first:

```text
initialize(protocolVersion="2024-11-05")
notifications/initialized
session_manager(action="health")
```

Calling `tools/list` or `tools/call` before this handshake can return
`Invalid request parameters` even when the wrapper and Sysplorer session are
healthy.

### Direct MCP Review For The px4ctrl Graphical Architecture

For manual review of `MoSimQuadrotorModel.Experiment.Templates.Architecture.CompleteSystemGraphical`,
use this direct MCP sequence:

```text
python Scripts\agent\check_mworks_gui_sentinel.py --output Results\mworks_gui_incidents\<request_id>\sentinel.json
capture a maximized or foreground screenshot of the target reusable Sysplorer/MWORKS main window, and verify the image content actually shows that target window
session_manager(action="health")
model_manager(action="load_file", file_path="C:\\Users\\HP\\Desktop\\MoSim\\Models\\MoSimQuadrotorModel\\package.mo", force_reload=true, auto_load_deps=true)
model_manager(action="open", model_name="MoSimQuadrotorModel.Experiment.Templates.Architecture.CompleteSystemGraphical")
check_model(model_name="MoSimQuadrotorModel.Experiment.Templates.Architecture.CompleteSystemGraphical", stop_on_error=false)
```

Background `PrintWindow` capture, including
`Scripts\tools\capture_window_background.ps1 -RestoreMinimized`, is auxiliary
window-state evidence only for activation/license checks. Do not accept a
minimized/background capture, a broad TitleRegex helper/proxy capture, or a
desktop screenshot that actually shows Codex/another application as proof that
MWORKS is activated. If the target reusable Sysplorer/MWORKS main window cannot
be maximized or the screenshot content does not match it, stop before live MCP
work and return a license/window-evidence blocker.

Load the canonical root package once. Its embedded `Plant` package contains the
official baseline plant and resources, so do not load an external
`QuadrotorModel` package or any legacy facade alongside it. Mixing roots can
cause `错误(1401): 模型重复定义`. The public px4ctrl graphical architecture
entry is `MoSimQuadrotorModel.Experiment.Templates.Architecture.CompleteSystemGraphical`; it extends
`Experiment.Templates.Architecture.CompleteSystemGraphical`, whose
`Sunray150CompleteSystemGraphical_Sysblock` template retains the V6X, ORIN NX,
GPS + Mid360, ESC, four-motor and Sunray150 hierarchy. Its central
`Px4CtrlControllerModule` is composed from the active
`Px4CtrlAttitudeThrustAdapter` and `OfflineAttitudeRateAllocator` classes.
`MoSimQuadrotorModel.Experiment.SingleUav.Px4Ctrl.Px4CtrlRunner` remains the separate
whole-aircraft Runner entry and is not substituted for this review diagram.

Review-result interpretation:

| Result | Meaning | Action |
|---|---|---|
| `open ok=true` and no `1401` | The review model loads and opens | Continue visual review |
| `错误(1401): 模型重复定义` | A duplicate standalone model file exists or was loaded | Delete the standalone file and load only the package |
| `组件的类型 MoSimQuadrotorModel.Vehicle... 查找不到` | The canonical package did not finish loading | Force-reload only `Models/MoSimQuadrotorModel/package.mo`, then inspect its internal `Plant` entry and package order. Do not add a second package root. |
| `组件的类型 PX4CTRL_Core_AttitudeThrust_EquationBridge_Sysblock 查找不到` | The canonical package did not finish loading or its internal px4ctrl controller order is stale | Force-reload only `Models/MoSimQuadrotorModel/package.mo`, then inspect the internal `Control/Implementations/Sysblocks` package order. Do not load a standalone controller file as a second root. |

Graphical layout acceptance for this model:

```text
1. Resource images are copied directly from References/CUAV/ to Models/MoSimQuadrotorModel/Vehicle/Resources/Images/ and keep transparent PNG alpha.
2. Do not convert transparent images to white-background RGB files.
3. GPS and Mid360 must be separate top-level modules, not one combined perception picture block. GPS feeds the flight-controller position input; Mid360 feeds local position and obstacle margin into mission computing.
4. Top-level hardware module placements must use equal x/y scaling unless there is a model-level reason; otherwise the bitmap icon is visibly stretched.
5. Module connector extents should stay small, for example {{-5,-5},{5,5}}, because top-level component scaling also scales connector arrows.
6. Keep the layout compact with clear columns, but make cross-module connection lines visible enough for review and route them around hardware images when possible.
```

If this sequence discovers a new error, update this workflow and the relevant
design/report note before committing, so the next run does not repeat the same
mistake.

### Planning Model GUI Review Variables

For `MoSimQuadrotorModel.Experiment.OpenBlocks.LinearMpc.SingleUav.Sunray150OpenBlocksLinearMPCRunner`,
the reference trajectory is exported from `planningReference`, not from the
official Example1 `climbePath`. When using `run_sysplorer_mcp_smoke.py` for
GUI review or reproducible export, override the reference aliases explicitly:

```text
--override-variable x_ref=planningReference.position_command[1]
--override-variable y_ref=planningReference.position_command[2]
--override-variable z_ref=planningReference.position_command[3]
```

If these overrides are omitted, the runner may look for
`climbePath.position_command[*]`, producing empty or failed exports even when
`check_model` and `simulate_model` themselves are healthy. Treat that as a
workflow-variable mapping issue, not an MCP connectivity failure.

For complete-system failsafe scenarios, export event logs from
`system_failsafe_event_code`, not the legacy `system_event_code`. Sysplorer
has shown stale/constant export behavior for the older name in complete-system
models, while `system_failsafe_event_code` is verified against
`system_safety_status` and the active failsafe trigger. Scenario YAML files
under `Config/scenarios/system/` must therefore map:

```yaml
extra_variables:
  event_code: system_failsafe_event_code
```

`Scripts/results/generate_event_log.py` preserves event codes 60-64 for return/failsafe
modes; it must not collapse all `flight_mode=6` rows to `DEGRADED_NAV`.

---

## 4. Procedure

### Step 0: Confirm the MCP wrapper

Before running a real MWORKS simulation, verify that the wrapper can start the
Sysplorer MCP server from the current shell. The runner auto-detects these
locations:

```text
Docs/Skills/Mworks/mworks-mcp-operations/wrappers/sysplorer_mcp.cmd  (Windows)
Scripts/mworks/sysplorer_mcp_wsl_bridge.sh
/home/linux/mcp-wrappers/sysplorer_mcp.sh
~/mcp-wrappers/sysplorer_mcp.sh
~/mcp-wrappers/sysplorer_mcp.bat
~/mcp-wrappers/sysplorer_mcp.cmd
~/mcp-wrappers/sysplorer_mcp.ps1
```

In WSL/Codex, prefer `Scripts/mworks/sysplorer_mcp_wsl_bridge.sh` because it starts
the Windows MCP server through `/init ... cmd.exe /c`. Directly executing
Windows `.exe` or `.cmd` files from WSL may fail with `Exec format error`.

For a non-standard location, use either:

```powershell
$env:SYSPLORER_MCP_WRAPPER="C:\path\to\sysplorer_mcp.cmd"
python scripts\run_mworks_scenario.py scenarios\official\example1_pid_baseline.yaml
```

or pass it per run:

```powershell
python scripts\run_mworks_scenario.py scenarios\official\example1_pid_baseline.yaml --wrapper "C:\path\to\sysplorer_mcp.cmd"
```

If the wrapper directly `exec`s a Windows `python.exe` from WSL and WSL reports
`cannot execute binary file: Exec format error`, the simulation cannot be
launched from the current shell. In that case:

```text
1. Do not label the attempted run as MWORKS evidence.
2. Remove any partial raw/metrics/log directories created by the failed attempt.
3. Keep the scenario inactive with inactive_reason describing the wrapper block.
4. Re-run from a Windows-capable shell or repair the wrapper so WSL can launch it.
```

If `simulate_model` returns `ok=true` but the payload contains
`simulate_api_reported_failure=true`, treat the run as failed. The MCP wrapper
may still probe one variable with `GetVarValueAt`, but `GetVarsValues` can later
return empty arrays. Do not overwrite evidence or claim a successful simulation
from this state; fix the model or scenario and rerun until `simulate_model`
does not report the API failure flag.

### Step 1: Check MCP status

Run `/mcp` in Codex.

Success criteria:

```text
sysplorer Tools include:
session_manager
load_library
model_manager
check_model
simulate_model
result_manager
```

If tools are not listed, follow `Docs/Workflows/debug_mcp.md`.

---

### Step 2: Check MWORKS activation and GUI state

Before any `session_manager`, model load, check, translate, simulate, plot,
animation, or graphical review, inspect the existing reusable window:

```powershell
python Scripts\agent\check_mworks_gui_sentinel.py `
  --output Results\mworks_gui_incidents\<request_id>\sentinel.json
powershell -NoProfile -ExecutionPolicy Bypass `
  -File Scripts\tools\capture_window_background.ps1 `
  -TitleRegex "Sysplorer|MWORKS|Quadrotor|AWFF" `
  -OutDir Results\mworks_background_capture\<request_id>
```

If the sentinel or screenshot shows a login/license/activation prompt, the
current active thread stops model/check/simulation work and returns a
`license_or_login` blocker. Bounded official MWORKS/Sysplorer/Syslab login
recovery is allowed only under the user-authorized recovery rules below;
normal engineering work must not type credentials or click login.

Bounded login recovery is allowed only for MWORKS/Sysplorer/Syslab activation
or account prompts that block live simulation:

```text
1. Use foreground or maximized target-main-window evidence before recovery.
2. Use only the user-provided secure credential source; never write credentials
   into docs, logs, packets, screenshot manifests, email, or terminal output.
3. Do not capture screenshots with password text visible.
4. After login, capture foreground/maximized evidence that the target window is
   back to a usable main-window state, then return to the normal background
   phase-screenshot route.
5. Stop and escalate on MFA/captcha, account/password error, abnormal
   authorization, unknown modal/window, crash/error-report, save/overwrite
   prompt, non-MWORKS credential surface, or any uncertainty about the target.
```

If the sentinel or screenshot shows authorization failure, GUI error-report
dialog, mixed blocking license state, visible unknown window, unavailable
tooling, or unknown sentinel state, stop live MWORKS work and return a
`license_or_login` or GUI blocker. Hidden Qt/browser-proxy/helper windows with
no license/error text are risk evidence, not standalone blockers. Do not tune
solver/model code while a login/license/GUI incident is open.
For activation/license/login/authorization/GUI-error incidents, PMO must send a
sparse email alert for the open incident. WeChat is optional and
diagnostic-only unless the user explicitly asks for it.

The task return or blocker packet must include:

```text
activation_sentinel_before
gui_sentinel_before
background_screenshot_before
activation_state_observation
license_state
will_not_click_activation_login=true for normal engineering work
bounded_login_recovery_user_authorized_when_applicable
mworks_window_evidence_touched=true
live_mworks_touched
mworks_phase_screenshots when live_mworks_touched=true
mworks_phase_observations when live_mworks_touched=true
```

For live simulation, continue background screenshots during the task, not only
at preflight. Capture and inspect phase screenshots after model load/check and
after simulate/plot/animation phases when those phases run. Ordinary phase
screenshots use DPI-aware background capture and must keep the target paintable:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass `
  -File Scripts\tools\capture_window_background.ps1 `
  -TitleRegex "Sysplorer|MWORKS|Quadrotor|AWFF" `
  -OutDir Results\mworks_background_capture\<request_id> `
  -RestoreMinimized `
  -MinimizeAfter
```

Do not use `-Maximize` for ordinary phase screenshots. Use maximize/foreground
only for activation/login/license/authorization evidence or when a task packet
explicitly requests full-window graphical review.

Every formal simulation result bundle should include:

```text
Results/<group>/<scene>/<experiment>/screenshots/
Results/<group>/<scene>/<experiment>/logs/screenshot_manifest.json
```

The manifest records phase, capture mode, target title/process, source capture
path, copied/indexed evidence path, width, height, DPI-awareness mode,
blank/cropped/ambiguous status, and reviewer observation. If a phase screenshot
is blank, cropped, wrong-window, or ambiguous, retry once with a safer capture
mode. If activation/license evidence fails, stop. If ordinary phase evidence
fails but MCP result export is valid, record `screenshot_incomplete=true` and
do not claim GUI/layout/animation acceptance from that phase. If graphical
layout or wiring evidence fails, do not claim graphical acceptance.

If a phase screenshot shows a missing/changed window, activation/login prompt,
authorization issue, GUI error-report dialog, or demo/mixed license state, stop
live work and route the incident through the bounded recovery/blocker path
instead of continuing solver/model trials.

Run the packet through the live-gate checker before accepting it:

```powershell
python Scripts\quality\check_mworks_live_gate.py `
  Results\agent_packets\returns\<request_id>.json `
  --kind return
```

Older MWORKS business packets that predate this field set remain historical
evidence only. They must not be reused as templates for new MWORKS/Sysplorer/
Syslab dispatches.

---

### Step 3: Connect to Sysplorer

Use `session_manager`.

Recommended action:

```text
Probe existing Sysplorer session.
If no session exists, start or connect to Sysplorer.
```

Expected output:

```text
session connected
platform label visible
Sysplorer version available
```

---

### Step 4: Load required libraries

Use `load_library`.

Load:

```text
Modelica Standard Library
MWORKS quadrotor model library
project custom controller library
```

If library loading fails:

1. Check model path.
2. Search `resources_retrieval`.
3. Query API with `get_api_document`.
4. Do not continue simulation before library loading succeeds.

---

### Step 5: Open target model

Use `model_manager`.

Tasks:

```text
open model
inspect model components
verify controller component exists
verify input/output ports exist
```

Required checks:

```text
quadrotor body component exists
controller component exists
motor/electric drive component exists
sensor component exists
trajectory/reference input exists
```

---

### Step 5: Check model

Use `check_model`.

Rules:

```text
Always run check_model before simulate_model.
Do not run simulation if check_model fails.
Save error messages into Results/{group}/{scene}/{experiment}/logs/ if possible.
```

Success criteria:

```text
model instantiation succeeds
no blocking compile errors
required variables can be generated
```

---

### Step 6: Run simulation

Use `simulate_model`.

Recommended simulation parameters:

```text
start_time = 0
stop_time = scenario-defined
step_size = scenario-defined
solver = default unless project specifies otherwise
```

Required outputs:

```text
result file path
simulation status
runtime logs
```

For normal-size GUI review, the runner must use the official Python API
`ModelingPy.SimulateModel(..., path=...)` to generate the Sysplorer native
result, then explicitly call `OpenResult(Result.msr)` before creating tracking
plots and animation. Do not use MCP `simulate_model` with `ext_res_path` for
GUI review: that path has produced results that `result_manager` can read but
Sysplorer GUI cannot bind with `OpenResult/CreatePlot`. The native
`Result.msr` is retained only as a local review asset, not as a manual fallback
when automation fails. The manual review target is the actual quadrotor 3D
animation plus tracking curves; seeing only static propeller geometry, only a
blank result viewer, or only parameter curves is not enough to mark visual
review complete.

For single-UAV planning/navigation scenarios, the 3D animation must also show
the model-level navigation context. Do not use offline HTML replay as a
substitute. The closed-loop model should include `PlanningNavigationDisplay` or
an equivalent component:

```text
actual pose input     = sensors1_1.PosMea
local plan input      = planningReference.position_command
local map source      = planner YAML obstacle semantics rendered as pillar clusters
display policy        = rolling local costmap + short-horizon local plan
```

Acceptance for manual review:

```text
1. Random obstacle map appears as compact pillar clusters plus volumetric terrain columns covering the map. The current `planning_open_blocks` review model uses 0.2 m static STL terrain cells, no boundary walls, 1000 random obstacle pillars, and 8 standard L/T wall groups. Obstacles are objective environment objects, but the visual layer must emphasize local sensing: cells and obstacles inside the current local radius are bright/highlighted, while unsensed areas are muted and update with the UAV. The path must come from local-window receding A*, not from manually placed obstacles that leave a preselected corridor. The planner may only use obstacles already discovered inside the current local sensing window and not occluded by L/T wall boxes; wall faces hit by the current line of sight are discoverable, but objects behind the wall remain unknown until the UAV moves around the occluder. Undiscovered truth obstacles are allowed in the rendered environment only for review and collision evaluation.
2. Blue local plan segment starts at the UAV actual position and shows only the short forward horizon inside the local 5x5 map window, not the full global path or far-future regions.
3. Current actual and reference markers are small enough not to cover the UAV or path.
4. Actual flown trajectory is inspected from MWORKS/native result or a separate viewer,
   not from dynamic history states injected into the closed-loop model.
```

Planning scenarios have one extra gate: tracking quality is not enough. Before
claiming obstacle avoidance, run the display/trajectory collision check against
the same pillar map rendered in Sysplorer:

```bash
uv run python Scripts/planning/check_planning_display_collision.py \
  Models/MoSimQuadrotorModel/Guidance/Planning/Sunray150PlanningOpenBlocksLinearMPCSysblockClosedLoop.mo \
  --required-clearance-m 0.35
```

If this check fails, the scenario may still be useful for controller tracking
or GUI display review, but it must not be reported as successful autonomous
obstacle avoidance. Fix the planner data source, generated waypoints, or local
map injection first.

Do not implement actual history trails inside the Modelica/Sysplorer display
component with `sample/pre` or `delay()`. In this project, `sample/pre`
history once changed the planning open-blocks RMSE from about `0.1667 m` to
about `70.08 m`, and a `delay()` history variant triggered
`simulate_api_reported_failure=true`. Display logic must not perturb the
closed-loop controller evidence. Actual flown history should be reviewed from
raw/native result or a separate non-control viewer.

```text
python3 Scripts/mworks/run_mworks_scenario.py <scenario.yaml>
```

The expected native result path is:

```text
Results/{group}/{scene}/{experiment}/native_result/{ModelName}/Result.msr
```

If that Windows path is too long for reliable MWORKS `OpenResult/CreatePlot`
binding, the runner automatically writes the native result to:

```text
Results/native_result_cache/{experiment}/{ModelName}/Result.msr
```

Before writing a GUI-bound native result, the runner must delete only the exact
target `{ModelName}` native result folder. Sysplorer otherwise creates
`{ModelName}-1`, `{ModelName}-2`, ... when the folder already exists, while the
GUI opener still targets stale `{ModelName}/Result.msr`; this produces
`OpenResult returned False` / `错误(4007)` even though simulation and CSV export
passed. This is an automation bug, not a valid reason to ask the user to open
the `.msr` manually.

and leaves a project-local mapping file at:

```text
Results/{group}/{scene}/{experiment}/native_result/native_result_manifest.json
```

For headless regression, batch runs, or a known GUI/license issue, skip native
viewer generation explicitly:

```text
python3 Scripts/mworks/run_mworks_scenario.py <scenario.yaml> --no-gui-result-viewer
```

For one-at-a-time manual GUI review, avoid mixing old and current windows:

```text
python3 Scripts/mworks/run_mworks_scenario.py <scenario.yaml> --gui-reset-windows
```

This keeps the Sysplorer session open, but closes existing plot/animation
windows before opening the current result. The tracking plot is created with
the current `Result.msr` path explicitly bound; the animation window is then
created for the active simulated result. The script still does not call
`RunAnimation()` by default.

For long/heavy planning displays, do not create the animation from the full
high-rate native result. A full 327 s `planning_open_blocks` native result at
the controller output rate can exceed 1 GB and block `CreateAnimation()` even
when `OpenResult/CreatePlot` succeed. Keep full numerical evidence from the
scenario-defined time span, but create a separate full-duration native result
for GUI visual audit with a coarser output interval:

```text
python3 Scripts/mworks/run_mworks_scenario.py <scenario.yaml> \
  --gui-review-full-time \
  --gui-review-interval 0.5 \
  --gui-review-native-result-dir Results/native_result_cache/gui_review_current_planning_open_blocks_full_0p5s \
  --gui-reset-windows
```

In this mode the full run still writes raw CSV and metrics for the full target
time, while the 3D animation and plot are also bound to a full-time native
review result. The only reduction is the GUI review output interval, so the
animation timeline remains complete and suitable for manual review.

Short GUI review runs are diagnostics only. Use them to check whether the
`OpenResult/CreatePlot/CreateAnimation` chain is working before spending time
on a full GUI review:

```text
python3 Scripts/mworks/run_mworks_scenario.py <scenario.yaml> \
  --gui-review-stop-time 3 \
  --gui-review-native-result-dir Results/native_result_cache/gui_review_current_planning_open_blocks_3s \
  --gui-reset-windows
```

Do not mark manual visual review complete from a shortened run. If any separate
review directory is already open in Sysplorer and Windows locks `Result.msr`,
the runner must switch to a timestamped sibling directory instead of failing
with `PermissionError`.

Important: a successful MCP `call_code` response is not sufficient evidence
that the GUI plot or animation opened. Inspect the nested `run_script_result`
fields:

```text
run_script_result.create_plot == true
run_script_result.create_animation == true
```

If the log contains `错误(4007): 结果文件 ... Result.msr 未打开`, the native
result exists on disk but was not opened/bound by the current Sysplorer GUI
session. First verify whether Sysplorer wrote the current run to a suffixed
folder such as `{ModelName}-1`; if so, fix the runner/cleanup path and rerun,
do not ask the user to manually open the `.msr`. If no suffix mismatch exists,
rerun through the normal scenario runner so it can switch to
`Results/native_result_cache/` and bind the shorter `Result.msr` path. Treat the
numerical simulation as valid only if `check_model`, raw CSV, and quality gates
passed; treat GUI visual review as incomplete until both nested statuses are
true:

```text
GUI plot: True
GUI animation: True
```

For large 3D planning displays, do not add dynamic Modelica components just to
make the map look smoother. The stable pattern is a static STL terrain/obstacle
asset plus a small dynamic overlay. The current `planning_open_blocks` review
model uses 0.2 m static STL terrain columns, 1000 static random obstacle pillars,
8 dynamic standard wall groups, radial local-map recoloring, body axes, and a
short local plan segment. If the GUI freezes, stop retrying animation creation,
keep the numerical evidence, reduce display load, and rerun a short
`check_model`/`simulate_model` smoke before any full run.

For video capture that needs the full colored global map, open
`MoSimQuadrotorModel.Guidance.Planning.Sunray150PlanningOpenBlocksColorMapReview`. This model is
a thin review-only extension of
`Sunray150PlanningOpenBlocksLinearMPCSysblockClosedLoop`: it keeps the same
controller, vehicle, path, local sensing overlay, and timing, but enables
`navigationDisplay.show_static_map_layers=true` and disables dynamic terrain
blocks. Do not use this review variant as the source of numerical performance
claims; use it only for recording the global colored static-map visualization.

Every `modelica://.../Resources/Visualization/*.stl` URI must point to an
existing file even if the component length/width/height is zero or a layer is
disabled. Sysplorer model check still validates shape resources. For
`PlanningNavigationDisplay`, the split terrain-band STL files plus the obstacle
STL are the active display assets; `static_map_mesh_uri` must still reference a
real STL to avoid the check-window error:

```text
navigationDisplay.static_map_mesh cannot identify shape / file not found
```

When the planning model uses terrain-following altitude, the planner must write
`altitude_profile.mode=terrain_follow_agl`, keep `smoothing.type=quintic_segment`,
and synchronize the Sysplorer model through
`Scripts/planning/update_planning_open_blocks_model.py`. The expected online output
interval is `0.05 s` so raw CSV aligns with the 20 Hz controller/local-sensing
rate without producing oversized native results.

For terrain-following planning scenes, start and goal phases must be explicit.
`Scripts/planning/update_planning_open_blocks_model.py` inserts a ground takeoff segment
and a ground landing segment from the same terrain-height function used for
the static map. Do not hand-edit `p_z` arrays in the generated Modelica file;
regenerate the planner report and rerun the sync script instead. A high-speed
stress case may raise `velocity_reference_m_s`, but report it separately from
the low-speed precision evidence because tracking error can increase sharply.

For `Sunray150PlanningOpenBlocksLinearMPCSysblockClosedLoop`, keep planning
radius and GUI radar radius separate. The planner currently discovers
obstacles with `local_planning.window_radius_m=3.0`, while the Sysplorer GUI
review uses `visualization.radar_radius_m=6.0` and
`visualization.radar_fade_radius_m=9.0`: objects inside 6 m keep original
color, objects in the 6-9 m band are gray-white, and farther objects are
hidden. The full-duration GUI review default is `1.0 m` display cells
(`361` local dynamic cells for a 9 m fade radius), with a `2.0 m` local terrain center update step to reduce full-layer refresh stutter. A `0.2 m` display grid is
allowed for high-detail radar review, but it creates `8281` local dynamic
cells at the same radius; run a 3-5 s GUI smoke first and only increase the
duration if the viewer remains responsive. Static STL/map layers should stay
disabled in the online review model unless a separate static-map screenshot is
being generated.

The online review model must not hide all terrain height. With static map
layers disabled, `PlanningNavigationDisplay.local_sensed_ground` renders the
currently visible radar cells as local 3D terrain blocks using the same
deterministic terrain-height function as the planner/static map. The intended
visual contract is: `0-6 m` local ground uses sky-blue blocks with terrain
height, `6-9 m` uses gray-white terrain-height blocks, and farther terrain has
zero length/width/height. If the local radar area appears as one flat sheet,
check `local_sensed_ground_height` and `local_sensed_ground_position.z` before
changing the static STL map settings.

The durable evidence remains raw CSV, metrics JSON/CSV, logs, figures, and
replay JSON. Native result files support human review but are intentionally not
tracked.

If the GUI viewer opens but the 3D quadrotor animation is missing, keep the
raw/metrics/log evidence, record the GUI issue in the task notes, and run an
automated GUI binding diagnosis against the exact native result path:

```text
Results/{group}/{scene}/{experiment}/native_result/{ModelName}/Result.msr
```

Do not ask the user to manually open this `.msr`. If automation cannot open it,
the next action is to diagnose the native result folder, MCP session state,
Sysplorer activation, and animation API response. A user-side manual open is
not a valid fallback because it exercises the same broken result binding path.

GUI windows must be interpreted separately:

```text
model/diagram window: structure and connection review only
plot/result window: tracking curve and signal review only
3D animation window: visual flight review only
```

When several windows are already open, identify the active experiment from the
model name, MCP log path, or native result path before judging the result. If
the UAV appears to run out of view in the 3D animation but the quality gate
passes, first adjust the view/camera/zoom or reopen the matching native result;
do not mark the controller failed from view framing alone. If the quality gate
also fails, preserve the evidence as a negative sample and iterate the
controller or scenario.

Do not keep retrying MCP if the window shows a login/activation prompt or a
large set of unrelated library errors. Save the current work and request manual
login/activation.

The runner should not call blocking playback commands such as `RunAnimation()`
by default. It may create the animation window, but the human reviewer starts
playback in the GUI. If animation-window creation blocks MCP health checks,
disable GUI animation for the next batch and use the native result file for
manual review.

Native Sysplorer result files are local GUI assets. They are intentionally
ignored by Git:

```text
Results/**/native_result/
Results/native_result_cache/
*.msr
```

Do not run shortened `--stop-time` smoke checks into existing formal evidence
paths. Use a dedicated smoke scenario/result path, or explicitly pass
`--allow-overwrite-evidence` only when replacing those results is intended.

After smoke tests or temporary probes, delete `.running`, `.tmp`, `__pycache__`,
and ad-hoc probe logs before committing.

For system-mode/failsafe scenarios, do not judge the result with trajectory
RMSE gates. Use a `quality_profile: system_mode` scenario and verify the
exported mode signals instead:

```text
gps_valid toggles healthy/dropout
degraded_nav_active reaches 1
flight_mode reaches 6
active_setpoint_source reaches 90
safety_status reaches 3
event_log.json contains DEGRADED_NAV
```

MWORKS/Sysplorer may fold or omit isolated top-level diagnostic equations that
do not participate in the executable data flow. Put mode/failsafe logic inside
a component such as `SystemSupervisorModule`, export the component or bridged
top-level variables, and probe raw CSV before claiming a state-machine result.
If a nominal `event_code` variable stays constant while `flight_mode` changes,
derive the event-log label from `flight_mode` and document that mapping.

If Sysplorer/MWORKS suddenly reports unexplained license, activation, login,
bulk library load failures, solver startup errors, or GUI/MCP errors after
previously passing, do not start by retuning the model or controller. Preserve
current file changes, clean temporary files, rerun the MWORKS GUI sentinel and
target-window evidence capture, and classify the issue first. If the evidence
shows login/license/activation/authorization or an unknown GUI blocker, stop
the MCP sequence and return a blocker unless the user explicitly authorizes
bounded login/activation recovery. Do not repeatedly retry the solver.

If simulation fails:

1. Save error message.
2. Check model again.
3. Reduce scenario complexity.
4. Run a short hover smoke test.
5. Do not fabricate results.

---

### Step 7: Read result variables

Use `result_manager`.

Required variables:

```text
time
x, y, z
x_ref, y_ref, z_ref
roll, pitch, yaw
u1, u2, u3, u4
```

Optional variables:

```text
vx, vy, vz
p, q, r
thrust
torque_x, torque_y, torque_z
disturbance_hat_x, disturbance_hat_y, disturbance_hat_z
motor_efficiency
formation_error
min_obstacle_distance
```

If a variable is missing:

1. Use `result_manager` to list available variables.
2. Map model variable names to standard result fields.
3. Update `Docs/Index/api_index.md` if a useful mapping is found.

---

### Step 8: Export raw results

Save to:

```text
Results/{group}/{scene}/{experiment}/raw/{scene_id}_{controller_id}.csv
```

CSV should include:

```csv
time,x,y,z,vx,vy,vz,roll,pitch,yaw,u1,u2,u3,u4,x_ref,y_ref,z_ref
```

If direct CSV export is unavailable, save the native result file and document the conversion method.

---

### Step 9: Evaluate result quality

Run the quality gate after metrics are available:

```bash
python3 Scripts/results/evaluate_result_quality.py Config/scenarios/official/example3_awff_sysblock.yaml --write-metrics
```

The scenario runner does this automatically unless `--no-quality-gate` is set:

```bash
python3 Scripts/mworks/run_mworks_scenario.py Config/scenarios/official/example3_awff_sysblock.yaml
```

Interpretation:

```text
quality_status=pass             result can support the stated performance claim
quality_status=smoke_only       chain check only; do not use for full performance
quality_status=needs_iteration  preserve evidence, revise controller/scenario, rerun
```

Execution success is not enough. A result with worse RMSE than its baseline,
failed 8 字形 shape check, excessive error, low health score, or missing duration
must be treated as unfinished even when MWORKS reports no runtime error.

---

### Step 8.1: Reference/Replay Fallback

If MWORKS or Sysplorer MCP is unavailable, do not fabricate simulated states.
Instead, generate only the official reference trajectory and replay scaffold:

```bash
python3 Scripts/results/generate_reference.py --scene all
```

Outputs:

```text
Results/official/example1_step/reference_official_example1/raw/reference_official_example1.csv
Results/official/example2_helix/reference_official_example2/raw/reference_official_example2.csv
Results/official/example3_figure8/reference_official_example3/raw/reference_official_example3.csv
Results/official/example1_step/reference_official_example1/replay/reference_official_example1.json
Results/official/example2_helix/reference_official_example2/replay/reference_official_example2.json
Results/official/example3_figure8/reference_official_example3/replay/reference_official_example3.json
```

These files are valid for P0 trajectory inspection and video/replay pipeline
development. They are not a substitute for controller simulation metrics; once
Sysplorer simulation results are available, export measured `x,y,z` and compute
metrics against the reference columns.

Official scenario configs:

```text
Config/scenarios/official/example1_pid_baseline.yaml  -> MoSimQuadrotorModel.Vehicle.Examples.Example1
Config/scenarios/official/example2_pid_baseline.yaml  -> MoSimQuadrotorModel.Vehicle.Examples.Example2
Config/scenarios/official/example3_pid_baseline.yaml  -> MoSimQuadrotorModel.Vehicle.Examples.Example3
```

Smoke logs may cover only a short interval such as 0-1 s. Full official
baseline metrics require the scenario stop times in `Config/scenarios/official/*.yaml`.

---

## 5. Output Requirements

For every successful simulation, create:

```text
Results/{group}/{scene}/{experiment}/raw/{scene_id}_{controller_id}.csv
Results/{group}/{scene}/{experiment}/logs/{scene_id}_{controller_id}.log
```

For every reported experiment, later create:

```text
Results/{group}/{scene}/{experiment}/metrics/{scene_id}_{controller_id}.json
Results/{group}/{scene_id}/figures/{controller_id}/trajectory.png
Results/{group}/{scene_id}/figures/{controller_id}/error.png
```

---

## 6. Smoke Test Variant

Use this for fast validation:

```yaml
experiment_id: official_example1_mcp_smoke
scene_id: official_example1
controller_id: pid_baseline
model_name: MoSimQuadrotorModel.Vehicle.Examples.Example1
stop_time: 1
step_size: 0.01
```

Pass conditions:

```text
simulation finishes
result file exists
time exists
x/y/z exist
no NaN values
z remains non-negative
motor commands are not all zero
```

---

## 7. Failure Handling

| Failure | Action |
|---|---|
| MCP tools missing | Follow `Docs/Workflows/debug_mcp.md` |
| session_manager fails | Restart Sysplorer and retry |
| load_library fails | Check library path and model installation |
| check_model fails | Fix model before simulation |
| simulate_model fails | Run smoke test and inspect logs |
| result variable missing | Use result_manager to list variables |
| output file missing | Save native result and document path |

---

## 8. Report Notes

When using simulation results in the report, record:

```text
scene_id
controller_id
model version
simulation time
step size
disturbance parameters
controller parameters
result file path
metrics file path
figure path
```

Never make performance claims without metrics or figures.
