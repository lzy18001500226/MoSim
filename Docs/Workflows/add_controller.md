# Add Controller Workflow

> Status: reusable controller-addition workflow. Its G9 family sequence is
> historical trace-back, while current evidence rules are defined by
> `Docs/Workflows/controller_evidence_closeout.md` and the current user's scope.
> This workflow is static-first. It does not start ROS, Gazebo, PX4, MAVROS,
> RViz, UE, or MWORKS unless the current user request explicitly opens that live
> scope.

## 1. Purpose

Add one controller or one bounded augmentation to MoSim without breaking the
frozen G8 generated-core baseline or the Diff-Planner single/three-UAV runtime
baseline.

Historical G9 first batch:

```text
G9-0: controller registry, ExperimentProfile, Launch Plan, Run Manifest, static gates
G9-A: official PID baseline
G9-B: SE3 Basic
G9-C: DFBC Basic or DFBC-Jerk
G9-D: Classical or boundary-layer SMC
G9-E: INDI / PID-INDI bounded augmentation
G9-F: NMPC outer loop
```

The current user's direct request selects whether this workflow may run; this
workflow does not select work by itself.
Before promoting a new controller into the active evidence matrix, read
`Docs/Workflows/controller_evidence_closeout.md` for the frozen model-root,
claim boundary, and G1-G7 gates. Do not restart historical G9/G10/G11
sequences unless the current user explicitly reopens that evidence.

Do not treat a roadmap entry or a `ControllerProfile` entry as an implemented
controller. Planned controllers must stay blocked by `C-CTRL-01` until source
audit, implementation, interface evidence, and first run packet evidence exist.

## 2. Required Entry Points

Before implementation, read only the minimum relevant set:

```text
Docs/Design/需求.md
Docs/Design/架构.md
Docs/Design/架构/00_架构与任务/任务路线图.md
Docs/Design/架构/00_架构与任务/ExperimentProfile与兼容性矩阵.md
Docs/Design/架构/01_控制器平台/统一控制接口.md
Docs/Design/架构/01_控制器平台/控制器管理与配置.md
Docs/Design/架构/01_控制器平台/controllers/<controller>.md
Docs/Design/架构/03_测试调参与证据/测试与评价.md
Config/profiles/README.md
```

Use `Docs/Design/架构/01_控制器平台/控制增强与容错.md` when the task is an
augmentation, observer, safety filter, or fault-tolerance module rather than a
nominal controller.

## 3. Source-Basis Gate

Every G9 controller starts with a source-basis packet, not code.

For G9.5/G9.6 and later controller work, the source-basis gate is also the
anti-drift gate. The agent must first look for usable paper formulas, author
code, local reference projects, MATLAB/Simulink examples, C/C++ implementations,
official documentation, or targeted public engineering notes before writing new
controller logic. Hand-written code is allowed only after recording why the
available references are incomplete, incompatible with the MoSim control-chain
position, or unsafe to adopt directly.

Minimum packet fields:

```text
controller_id
G9 task id
controller family
nominal controller vs augmentation vs allocator vs safety filter
control-chain position
required state fields
required reference order
output interface
PX4 inner-loop reuse policy
MWORKS/Sysblock/CFunction/codegen route
ROS/Sunray adapter route
open-source implementation references
paper/formula references
known failure modes
forbidden claims
first ExperimentProfile id
first evidence directory target
```

If the API, formula, or implementation route is unclear, inspect local
references first, then official docs or targeted web/community material. Do not
hand-write a controller from memory when suitable source material exists.

The packet must explicitly separate evidence levels:

```text
source/formula evidence:
  proves only that the controller law and assumptions were identified.

static/unit evidence:
  proves only that the platform-independent core compiles and satisfies local
  interface or numerical checks.

offline replay evidence:
  proves only same-input behavior against the selected formula, model, or
  generated code path.

Gazebo/Sunray/PX4/MAVROS evidence:
  is the first evidence level that may support a controller performance claim.
```

Static gates are required, but a static gate cannot be reported as "control
effect improved", "paper reproduced", "Gazebo closed loop passed", "MWORKS
codegen passed", or "ready for display". Those claims require the matching
runtime or codegen evidence packet.

## 4. Profile Gate

Register the controller in:

```text
Config/profiles/catalog.json
```

Required `ControllerProfile` fields:

```text
controller_id
implementation
implementation_status
g9_task
controller_family
chain_position
output_interface
rate_hz
required_state
required_reference
optional_reference
compatible_adapters
compatible_safety
compatible_augmentations
source_basis_required
source_basis
mworks_codegen_route
acceptance_tiers
evidence_level
```

Use these statuses:

```text
planned: registered but not runnable; active ExperimentProfile must reject with C-CTRL-01
implemented: code/model exists and interface checks pass; runtime evidence still pending
accepted: user-reviewed evidence baseline is frozen
```

Candidate ExperimentProfiles for unreleased controllers live under:

```text
Config/profiles/candidates/
```

Runnable ExperimentProfiles live under:

```text
Config/profiles/experiments/
```

Do not move a G9 candidate into `experiments/` until `implementation_status` is
`implemented` or `accepted`.

## 5. Interface Contract

First-stage G9 uses the existing `ATTITUDE_THRUST` path unless a later user
decision explicitly opens another output layer:

```text
state:
  position
  velocity
  attitude
  angular_velocity

reference:
  position
  velocity
  acceleration
  yaw
  optional yaw_rate / jerk / snap

output:
  desired_attitude_quaternion
  desired_collective_thrust_N
  controller_status
  controller_diagnostics
```

Rules:

```text
Controller core does not publish MAVROS topics directly.
Planner does not own MAVROS control publishing.
Adapter maps controller output to MAVROS/PX4 command semantics.
Safety and limiter logic stay outside the nominal controller unless the
controller family explicitly owns that layer.
INDI, L1, DOB/ESO, AWFF, NN/Fuzzy, safety filters, and fault allocation are not
ordinary peer nominal controllers.
```

## 6. Implementation Sequence

Use the same shape for every G9 controller:

```text
1. Source-basis packet
2. Controller card update
3. ControllerProfile registration as planned
4. Candidate ExperimentProfile under Config/profiles/candidates/
5. Static rejection proof with C-CTRL-01
6. Implement C++/MWORKS/Sysblock/CFunction route
7. Unit/interface test
8. Offline replay consistency against controller formula/source basis
9. MWORKS check/codegen gate where applicable
10. Generated C/C++ wrapper through IController
11. Single-UAV Gazebo A/B against G8 runtime template
12. Diff-Planner single-UAV regression
13. Diff-Planner three-UAV regression when the single-UAV gate passes
14. Acceptance tier assignment
15. Update docs, profile status, and evidence links
```

G9.5/G9.6/G10/G11 must keep this sequence, with the following additions:

```text
G9.5/G9.6:
  reproduce the two selected papers as source-basis and runnable candidates;
  compare against px4ctrl, SE3 Basic, DFBC Basic, and NMPC outer on identical
  Gazebo trajectories before claiming improvement.

G10:
  frozen backlog after the earlier G9.5/G9.6/G10 probes. Historical evidence
  records the G9 family codegen and runtime reinjection route as closed for the
  current ATTITUDE_THRUST generated-family path, a reopened enhancement must
  start with minimal Gazebo evidence for its own contribution. Implement
  augmentation modules as bounded layers with explicit compatibility,
  enable/disable, reset, saturation, and ablation evidence; do not disguise an
  augmentation as a separate nominal controller.

G11:
  remains the evidence chain for promoting implemented/accepted controller or
  enhancement modules through MWORKS/codegen/offline-equivalence/ROS-Sunray
  reinjection/Gazebo regression. Do not codegen only the current best
  candidate, and do not treat generated source or static adapter shape as
  runtime replacement.

  Historical G9 family codegen evidence has three completed static/offline gates:
  MWORKS GenerateModelCode at
  `Results/g9/controller_family_attitude_thrust_v1/g9_family_mworks_codegen_20260630_work`,
  generated-C equivalence at
  `Results/g9/controller_family_attitude_thrust_v1/g9_family_generated_c_gate_20260630_195728/RUN_MANIFEST.json`,
  and static ROS/Sunray adapter-shape validation at
  `Results/g9/controller_family_attitude_thrust_v1/g9_family_ros_sunray_adapter_gate_20260630_200721/RUN_MANIFEST.json`.
  These gates prove only generated source, same-input numerical equivalence,
  and px4ctrl/MAVROS attitude-target command shape. Historical records also show the
  later official-PID generated-family build, Diff single-UAV, and Diff
  three-UAV runtime reinjection evidence. That closes the historical
  generated-family route; new work must be explicitly scoped by the user rather
  than inferred from this closure sequence.

G12/G13:
  UE map import, QGC secondary development, and RflySim-like display are
  post-G11 display-platform work. They may prepare interfaces early, but must
  not become the active control evidence path.
```

## 7. Acceptance Tiers

Do not force every controller to beat px4ctrl or meet a single cm-level target.
Each finished G9 run must end in one of:

```text
PASS:
  Meets the declared threshold and is eligible as a baseline candidate.

REPORT:
  Runs safely and produces useful comparison evidence, but does not meet the
  target threshold or has known limitations.

CANDIDATE:
  Interface and partial evidence exist, but runtime, robustness, or codegen
  evidence is incomplete.
```

Failed runs are still useful if the evidence packet is complete and the review
explains the failure mode. Do not hide failed evidence by rerunning into the
same result directory.

## 8. Static Checks

Default active experiments must pass:

```powershell
python Scripts/quality/check_experiment_profile.py --all
python Scripts/quality/build_experiment_preflight.py --all
```

A planned G9 candidate must be checked explicitly and must fail closed:

```powershell
python Scripts/quality/check_experiment_profile.py Config/profiles/candidates/g9_se3_basic_figure8_candidate_v1.json
```

Expected before G9-B implementation:

```text
ok=false
reason_code=C-CTRL-01
control_started=false
```

After a controller is implemented, update `implementation_status`, move or copy
the approved ExperimentProfile into `experiments/`, then rerun the default
static checks and the targeted controller tests.

## 9. Runtime Evidence Gate

For each implemented controller, start with the smallest real run:

```text
takeoff-hover-land
figure-eight
spiral
step
Diff-Planner single-UAV
Diff-Planner three-UAV only after single-UAV passes
```

Every run must write a unique `Results/runs/<run_id>` packet with:

```text
LaunchPlan.json
RUN_MANIFEST.json
source_hashes.json
runtime_export_manifest.json
runtime_log_manifest.json
controller_source_audit.json
controller_profile_snapshot.json
tracking.csv
metrics.json
threshold_report.json
review.md
screenshots/
logs/
raw/
```

Run evidence through:

```powershell
python Scripts/quality/check_run_evidence.py Results/runs/<run_id>
```

## 10. Safety Rules

1. Preserve px4ctrl and G8 generated-core baselines.
2. Keep one active controller backend per run.
3. Do not retune the frozen runtime baseline to hide a new controller defect.
4. Do not overwrite successful evidence with failed reruns.
5. Do not use Gazebo truth as formal control state unless the profile is debug
   or an explicitly declared height surrogate.
6. Do not claim MWORKS codegen, Gazebo closed loop, Diff-Planner regression, or
   PX4-native uORB deployment without the matching evidence gate.
7. Stop on MWORKS login/license/authorization/GUI-error blockers; do not click
   activation or login controls without explicit user authorization.
8. If a non-license MWORKS internal error, crash dump, missing-wire dialog, or
   graphical-model error appears during an authorized live gate, capture the
   exact error evidence, perform at most the bounded restart/repair allowed by
   the relevant MWORKS workflow, and then either continue with new evidence or
   return a blocker. Do not silently retry until success.
9. Do not keep working only in static simulation after a controller has a
   runnable core. The next required gate is the smallest Gazebo/Sunray runtime
   scenario that can falsify the claim.
10. Prefer existing paper formulas, author code, local reference projects,
    MATLAB/Simulink examples, C/C++ implementations, official docs, and
    targeted public engineering notes before writing new controller logic.
    Hand-written logic must record why the available references could not be
    adopted directly.
11. G9.5/G9.6/G10/G11 are not display or report tasks. UE map import, QGC
    secondary development, and full UI work may define interfaces early, but
    their evidence cannot replace Gazebo/Sunray/PX4/MAVROS or MWORKS/codegen
    gates.
12. If MWORKS live work shows login, license, authorization, GUI-error, or an
    unknown blocking window, stop live model/codegen work and return a blocker.
    If the issue is a non-license crash, dump, missing-wire dialog, or model
    error, capture the exact evidence before any bounded restart or repair.
