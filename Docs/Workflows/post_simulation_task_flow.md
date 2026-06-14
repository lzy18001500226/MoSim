# Post-Simulation Task Flow

> Purpose: define the task queue after a simulation run finishes. This file is
> the post-run control document that connects result extraction, metrics,
> quality gates, figures, evidence bundles, report updates, and the later UE
> replay/rendering route.

Status: active workflow, 2026-06-12 CST.

## 1. Scope

Use this workflow after any MWORKS/Sysplorer simulation, batch simulation,
formation run, diagnostic smoke run, or accepted historical result review.

This workflow does not authorize a simulation by itself. Live MWORKS,
Sysplorer, Syslab, ROS2, RViz, UE editor, UE build, or GUI actions still need
the authority declared by the current task, gate, or PMO decision.

The post-simulation queue is:

```text
simulation run or accepted historical result
  -> result inventory
  -> raw CSV extraction
  -> metric calculation
  -> quality classification
  -> figure/replay generation
  -> evidence bundle audit
  -> report/manual/update candidate
  -> transition decision:
       needs_iteration | accepted_for_report_candidate | ready_for_UE_replay
```

## 2. Required Inputs

Each post-run task starts with these inputs:

```yaml
post_simulation_job:
  scenario_config: Config/scenarios/<group>/<scenario>.yaml
  result_root: Results/<group>/<scene>/<experiment>/
  source_label: MWORKS_MCP | MWORKS_GUI | accepted_historical_review
  claim_scope: diagnostics_smoke | controller_performance | robustness | planning | formation
  expected_raw_files: []
  expected_metrics_files: []
  expected_figures: []
  report_target: optional string
  ue_replay_target: optional string
```

For live work, the evidence bundle must also include the MWORKS GUI/activation
preflight fields required by `Docs/Workflows/produce_simulation_evidence.md`.

## 3. Durable Start Artifact

Before a non-trivial post-run task proceeds, write a small start artifact under
the target result directory:

```text
Results/<group>/<scene>/<experiment>/logs/post_simulation_start.json
```

Minimum fields:

```json
{
  "workflow": "post_simulation_task_flow",
  "scenario_config": "",
  "result_root": "",
  "claim_scope": "",
  "started_at": "",
  "live_mworks_touched": false,
  "subagent_plan": {
    "decision": "available_but_not_useful",
    "reason": "single-thread execution requested"
  }
}
```

Exact no-write inspections may skip this artifact only when the user asks for a
quick answer and no state is changed.

## 4. Stage A: Result Inventory

Goal: confirm what the simulation produced before calculating or claiming
anything.

Check:

- scenario YAML exists and names the model/controller/result path;
- result root exists;
- raw, metrics, figures, logs, replay, screenshots, and native result folders
  are either present or explicitly absent;
- live-run screenshots and screenshot manifest exist when live work was done;
- MWORKS source label is present for formal report evidence.

Outputs:

```text
Results/<group>/<scene>/<experiment>/logs/result_inventory.json
Results/<group>/<scene>/<experiment>/logs/result_inventory.md
```

Pass condition:

```text
scenario/config/result_root are coherent
missing artifacts are listed
no report claim is made yet
```

Failure route:

| Failure | Next Action |
|---|---|
| result root missing | return `needs_rerun_or_wrong_path` |
| scenario YAML missing | return `scenario_contract_missing` |
| live screenshot manifest missing | mark `evidence_incomplete`, do not accept GUI-dependent claims |
| source label missing | mark `source_unlabeled`, do not report as formal evidence |

## 5. Stage B: Raw Extraction

Goal: ensure the raw CSV is available and reusable.

Use:

```text
Docs/Workflows/read_results.md
Scripts/mworks/extract_mcp_timeseries.py
Scripts/mworks/run_mworks_scenario.py
```

Required output for standard control claims:

```text
Results/<group>/<scene>/<experiment>/raw/<experiment>.csv
```

Required core columns:

```text
time
x, y, z
x_ref, y_ref, z_ref
roll, pitch, yaw
u1, u2, u3, u4
```

Formation runs must preserve `uav_id` or separated `uav_<id>/` raw traces as
defined in `Docs/Design/09_多机编队架构与数据设计.md`.

Pass condition:

```text
raw CSV exists
time column exists
core state/reference columns exist for the claim
row count > 10
no NaN in required core fields
```

Failure route:

| Failure | Next Action |
|---|---|
| variable missing | update or propose update to `Docs/Index/variable_mapping.md` |
| raw extraction impossible | keep native result/log evidence and mark `raw_extraction_blocked` |
| merged formation trace without `uav_id` | reject formation acceptance |

## 6. Stage C: Metrics

Goal: compute quantitative evidence from raw results.

Use:

```text
Docs/Workflows/calc_metrics.md
Scripts/results/calc_metrics.py
Scripts/results/calc_metrics.jl
Scripts/results/evaluate_result_quality.py
```

Required output:

```text
Results/<group>/<scene>/<experiment>/metrics/<experiment>.json
Results/<group>/<scene>/<experiment>/metrics/<experiment>.csv
```

Minimum metric families by claim:

| Claim Scope | Required Metrics |
|---|---|
| `diagnostics_smoke` | declared diagnostic summary, status, source labels |
| `controller_performance` | RMSE, max error, steady error, overshoot/settling where applicable, effort/saturation |
| `robustness` | nominal/disturbed labels, recovery time, performance retention, event window |
| `planning` | setpoint/trajectory validity, path length, minimum obstacle distance, fallback/stale status |
| `formation` | per-UAV error, formation RMSE, maximum formation error, minimum inter-UAV distance, collision/safety status |

Pass condition:

```text
metrics are reproducible from raw
metric JSON contains scenario/controller/source metadata
quality status is one of pass | smoke_only | needs_iteration | failed
```

Failure route:

| Failure | Next Action |
|---|---|
| metrics script fails | keep raw and error log, mark `metrics_blocked` |
| `needs_iteration` | preserve result, plan retune/rerun, do not report as accepted performance |
| metric/claim mismatch | narrow the claim or rerun the correct scenario |

## 7. Stage D: Quality Classification

Goal: decide the next engineering state without overstating the result.

Allowed states:

```text
accepted_for_report_candidate
needs_iteration
smoke_only
failed_evidence_preserved
blocked_missing_artifact
blocked_live_gate
```

Rules:

1. `check_model ok` and `simulate_model ok` only mean the run executed.
2. `quality_status=pass` is required for full controller-performance claims.
3. `quality_status=smoke_only` may validate automation or a diagnostic surface,
   not performance.
4. `needs_iteration` is useful evidence but not completion.
5. Planning, formation, ROS2, and UE claims need their own declared gates.

Outputs:

```text
Results/<group>/<scene>/<experiment>/logs/post_simulation_quality_decision.json
Results/<group>/<scene>/<experiment>/logs/post_simulation_quality_decision.md
```

## 8. Stage E: Figures, Replay, And Demo Assets

Goal: generate report-ready or review-ready visual assets from accepted raw and
metric files.

Use:

```text
Docs/Workflows/generate_report_figures.md
Scripts/results/plot_results.py
Scripts/results/plot_results.jl
Scripts/results/generate_replay_html.py
```

Required output folders:

```text
Results/<group>/<scene>/<experiment>/figures/
Results/<group>/<scene>/<experiment>/replay/
Results/<group>/<scene>/<experiment>/replay_html/
```

Figures and replay are supporting evidence. They do not replace raw CSV,
metrics, source labels, or acceptance gates.

Pass condition:

```text
expected figures exist
files have nonzero size
figure manifest lists source raw/metrics path
old report-selected figures were not overwritten by a failed generation
```

## 9. Stage F: Evidence Bundle Audit

Goal: make the result reviewable by a human or PMO without re-running it.

Required bundle:

```text
scenario/config path
model/controller identity
source label
raw CSV
metrics JSON/CSV
quality decision
figures/replay if visual claims are made
screenshots and screenshot manifest for live work
known exclusions and limitations
```

Use or add narrow checkers under:

```text
Scripts/quality/
Scripts/tests/
```

The audit output should live under the result directory or
`Results/static_audits/` when reviewing many runs.

## 10. Stage G: Report And Manual Update Candidate

A result may update `Docs/simulation_report.md`, `Docs/user_manual.md`, or a
candidate submission manifest only when:

- the evidence bundle is complete for the claim;
- `quality_status=pass` for performance claims, or the limitation is explicit;
- the report wording names the exact scenario, controller, and result path;
- `needs_iteration` and source-static-only rows are not promoted to acceptance.

Report updates are not final PMO acceptance. Final acceptance remains a
separate review decision.

## 11. Stage H: UE Transition Gate

Only enter UE replay/rendering work after the simulation evidence for the
selected run is at least `accepted_for_report_candidate` or the user explicitly
requests a diagnostic visualization.

For controller-performance visualization, a historical accepted matrix row is
not enough by itself. First rerun the selected candidate under the current clean
MWORKS GUI/preflight gate, refresh the metrics and candidate matrix, and keep
any `needs_iteration` reruns visible in the evidence bundle. Historical rows
may guide candidate selection, but they must not bypass the current-rerun gate.

The current-rerun gate may classify a selected run as UE-prep-ready only when
all of these are true:

```text
current clean MWORKS/preflight sentinel exists
selected candidate metrics source is MWORKS_MCP
selected candidate quality_status is pass and quality_pass is true
selected candidate has full-run raw rows and duration
metrics quality_checked_at is not older than the clean sentinel
raw, metrics, figures, and replay paths are present or explicitly scoped out
```

When this condition holds, the next UE task is still source-static replay input
preparation: map raw/replay fields, scene id, map id, unit conventions, and
render/review requirements. It is not UE runtime/editor/build authorization.

If the current candidate matrix has `accepted_candidate_count=0`, UE replay,
UE rendering, and multi-UAV transition are blocked for the controller-
performance line. Continue single-UAV controller/model iteration first, then
rerun the relevant MWORKS scenario(s), refresh acceptance, refresh the matrix,
and rebuild the closeout gate. A clean MWORKS GUI sentinel only permits the next
live MWORKS attempt; it does not by itself authorize UE transition.

UE entry inputs:

```text
raw CSV path
metrics path
scenario/scene id
map id when relevant
frame and unit convention
selected figure/replay target
render-only source labels
```

Use:

```text
Docs/Workflows/unreal_renderer.md
Docs/Workflows/generate_report_figures.md
Scripts/results/generate_replay_html.py
Scripts/UE5/stream_unreal_udp.py
Scripts/UE5/build_mworks_accepted_run_ue_replay_input_bundle.py
```

UE outputs can prove:

```text
visual replay generated
render path configured
scene/display asset produced
command/echo or editor/build gate passed when separately authorized
```

UE outputs cannot prove:

```text
MWORKS controller performance
plant truth
planner readiness
formation acceptance
runtime success without the declared UE gate
```

For the first UE handoff after an accepted MWORKS run, build a replay input
bundle before any runtime action:

```bash
python Scripts/UE5/build_mworks_accepted_run_ue_replay_input_bundle.py
```

Expected output:

```text
Results/ue_replay_input/<run_id>/ue_replay_input_bundle.json
Results/ue_replay_input/<run_id>/ue_replay_input_bundle.md
```

This bundle must state `source_static_only=true`, `ue_editor_opened=false`,
`ue_runtime_started=false`, and `udp_sent=false`. It may run
`stream_unreal_udp.py --dry-run --max-frames 1` to validate packet fields, but
it must not send UDP or start Unreal.

## 12. Long-Run Execution Slices

For a long single-thread run, use this order:

```text
Slice 1: write/update workflow and indexes
Slice 2: inventory current target scenarios and results
Slice 3: run or rerun only authorized MWORKS scenarios
Slice 4: extract raw outputs
Slice 5: calculate metrics and quality states
Slice 6: generate figures/replay assets
Slice 7: audit evidence bundles and gaps
Slice 8: if accepted, prepare UE replay/rendering route
Slice 9: report completion, blocker, or review-needed state
```

Sub-agent planning decision:

```text
default: no visible department dispatch while CoAgent architecture is under maintenance
disposable subagents: optional only for read-only review or disjoint static checks
parent responsibility: integrate every returned finding and preserve final authority
```

Current 12h+ single-thread execution gate:

```text
goal:
  finish the single-UAV MWORKS model/control simulation evidence loop before UE

subagent_plan:
  visible_subthreads: disabled while CoAgent architecture is under maintenance
  internal_roles:
    - model_iteration: inspect and patch the smallest model/controller surface
    - simulation_evidence: run check_model/SimulateModel-backed scenarios
    - quality_gate: refresh metrics, candidate matrix, and closeout gate
    - ue_gatekeeper: enter UE only after a current accepted single-UAV result

mandatory_order:
  1. write durable-start artifact for the target run
  2. make only the smallest model/controller change needed for the next test
  3. run smoke simulation before full 50 s simulation
  4. refresh metrics and quality gate from the new raw output
  5. refresh rotor1_loss15 candidate matrix and single-UAV closeout gate
  6. if quality_status is not pass, stay in single-UAV iteration
  7. if quality_status is pass and closeout gate is UE-prep-ready, prepare UE replay/rendering inputs without waiting for PMO idleness when the user has authorized direct continuation
```

UE must not be used as a workaround for an unfinished MWORKS controller result.
If the best current MWORKS result remains `needs_iteration`, the next task is
another bounded single-UAV model/controller iteration, not rendering.

## 13. Terminal Notification

When the post-simulation task reaches completion, blocker, or review-needed
state, send one short Chinese email through:

```bash
python Scripts/agent/send_gateway_email_alert.py --subject "<subject>" --body "<body>"
```

Do not email every intermediate observation.
