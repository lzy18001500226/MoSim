# Round 2 Core Competition / Report / Docs Memory

Date: 2026-06-04 CST

Scope: supplemental recovery cache for important historical workstreams that
were already represented in formal docs and result folders, but needed clearer
routing from the long-conversation recovery index.

This file is cache-only. It does not create new performance claims and does
not promote raw chat memory. Current claims must still be checked against the
named result files, model files, scenario configs, and quality gates.

## 1. Controller And Scenario Evidence

Status: `round2_verified_as_formal_doc_routed`

Current formal owners:

```text
Docs/simulation_report.md
Docs/Design/03_控制系统架构.md
Docs/Design/07_场景扰动与测试矩阵.md
Docs/Design/08_仿真指标与自动评估.md
Docs/Workflows/run_simulation.md
Docs/Workflows/produce_simulation_evidence.md
Docs/Workflows/calc_metrics.md
```

Current source surfaces:

```text
Models/QuadrotorControllerBlocks/
Models/QuadrotorExperiments/
Config/controllers/
Config/scenarios/official/
Config/scenarios/robustness/
Config/scenarios/planning/
Config/scenarios/formation/
Config/scenarios/system/
Results/official/
Results/robustness/
Results/planning/
Results/test_reports/
```

Recovery rule:

- Treat `quality_status=pass` as required for a positive performance claim.
- Treat `smoke_only` as automation-chain evidence only.
- Treat `needs_iteration` as negative/boundary evidence unless a later result
  path with the same scenario/controller has passed quality review.
- Do not infer current controller ranking from old chat; re-read the metrics
  JSON and `Docs/simulation_report.md`.

Known important result review:

```text
Results/test_reports/evidence_bundle_audit_20260515.md
Results/test_reports/evidence_bundle_audit_20260515.json
Results/人工审核清单.csv
```

The report says the 2026-05-15 evidence-bundle audit checked 76 scenarios with
zero issue count, but this remains a report/documented-audit fact. Future
report updates must rerun or re-audit if the scenario set changes.

## 2. Report, Replay, Native Result, And Video Assets

Status: `round2_verified_as_formal_doc_routed`

Current formal owners:

```text
Docs/user_manual.md
Docs/simulation_report.md
Docs/Workflows/generate_report_figures.md
Docs/Workflows/produce_simulation_evidence.md
Docs/Workflows/run_simulation.md
```

Recovery rule:

- `replay JSON/HTML` is a report/video/display asset, not controller proof.
- `native_result/Result.msr` is a local GUI review asset and must not be
  committed.
- Sysplorer native animation and curve windows are manual-review evidence only
  when bound to the current run's `Result.msr`.
- If a result path is redirected because of Windows path-length or stale-result
  issues, use the experiment's `native_result/native_result_manifest.json`.

Do not revive old browser/HTML point-cloud or replay routes as active
simulation evidence. Browser output is allowed only as explicitly requested
offline report preview.

## 3. Official MWORKS Documentation Conversion

Status: `round2_verified_current_path_corrected`

The current repository contains converted/scanned MWORKS documentation under:

```text
Docs/MworksDocs/
Docs/MworksDocs/converted/
Docs/MworksDocs/scan/
Docs/MinerU/mineru_precise_api.md
```

Several older docs still used the design-time path `Docs/Mworks/`. For fresh
conversation recovery, use `Docs/MworksDocs/` unless the repository is later
renamed and the indexes are updated.

Current formal owners:

```text
Docs/Index/doc_index.md
Docs/Index/api_index.md
Docs/Index/mathworks_to_mworks_migration.md
Docs/Workflows/translate_mathworks_to_mworks.md
Docs/Workflows/pre_submit_check.md
```

Recovery rule:

- Use `Docs/Index/doc_index.md` as the documentation entry point.
- Use `Docs/MworksDocs/scan/relevant_index.md` before opening large converted
  documents.
- Do not paste official document dumps into `AGENTS.md` or workflow files.
- Never store MinerU tokens in the repo; use `MINERU_API_TOKEN`.

## 4. Tests And Quality Gates

Status: `round2_verified_as_formal_doc_routed`

Current formal owners:

```text
Docs/Workflows/run_tests.md
Docs/Workflows/regression_test.md
Docs/Workflows/code_review.md
Docs/Workflows/pre_submit_check.md
Docs/Skills/Mworks/mworks-test-quality/SKILL.md
```

Current source surfaces:

```text
Scripts/tests/
Scripts/quality/
Scripts/results/evaluate_result_quality.py
Scripts/quality/audit_evidence_bundle.py
```

Recovery rule:

- For narrow changes, run the smallest relevant `Scripts/tests/test_*.py`.
- For result/evidence changes, run or re-run the quality/evidence audit that
  owns that result family.
- Do not use `check_model ok` or `simulate_model ok` alone as final quality
  evidence.

## 5. Planning And UE Scene Truth History

Status: `round2_verified_as_formal_doc_routed`

Current formal owners:

```text
Docs/Design/05_路径规划与轨迹生成.md
Docs/Design/08_仿真指标与自动评估.md
Docs/Workflows/unreal_renderer.md
Docs/simulation_report.md
```

Current source surfaces:

```text
Config/planners/
Config/scenarios/planning/
Scripts/planning/
Scripts/UE5/scene_truth_pipeline.py
Results/planning/
Results/unreal_scene_mapping/
```

Recovery rule:

- Planning claims must remain trackability-aware and closed-loop-evidence
  aware.
- UE collision/occupancy truth can validate but must not be fed to the planner
  as known global map.
- The old planning GUI/display tuning history is useful only when it links to a
  current MWORKS/UE evidence bundle or a formal workflow section.

## 6. Disposition

This cache supports a narrow update to:

```text
Docs/Index/project_work_memory_index.md
Docs/Index/doc_index.md
Docs/Index/api_index.md
Docs/Index/mathworks_to_mworks_migration.md
Docs/Workflows/translate_mathworks_to_mworks.md
Docs/Workflows/pre_submit_check.md
```

No new controller, scene, parameter, CoAgent, FAST-LIO, or codegen claim is
promoted by this supplemental cache.
