# Round 1 MWORKS Codegen Runtime Memory Cache

Date: 2026-06-04 CST

Scope: first cache pass for long-session memory about MWORKS/Sysblock
controller code generation, generated C runtime shape, and SIL evidence. This
is cache-only. It does not promote the PID demo result into a general
controller-runtime claim.

## Status

```text
round: 1
topic: MWORKS code generation and generated controller runtime
status: candidate_cache_created
risk: high
formal_docs_patched_this_round: none
cache_only: true
source_pointers_re_read:
  - Docs/Workflows/mworks_codegen_controller_runtime.md
  - PROGRESS.md
  - Docs/Workflows/agent_task_ledger.md
  - Results/codegen_probe/AWFF_PID_Sysblock_Demo_api/runtime_check.json
  - Results/codegen_probe/AWFF_PID_Sysblock_Demo_api/sil_zero_input_check.json
  - Results/codegen_probe/AWFF_PID_Sysblock_Demo_api/mworks_constant_0p1_reference.json
  - Results/codegen_probe/AWFF_PID_Sysblock_Demo_api/runtime_constant_0p1_check.json
  - Results/codegen_probe/AWFF_PID_Sysblock_Demo_api/sil_constant_0p1_check.json
```

Round 2 must still perform a focused verification pass before any formal
promotion. In particular, re-read the current workflow, scripts/tests, generated
code evidence, and result JSONs in the same round that decides whether an item
is verified, rejected, superseded, or ready for round 3.

## Candidate Items

### CODEGEN-MEM-001 - Official Codegen API Route

```text
round: 1
status: candidate
risk: high
candidate_statement:
  The correct Sysplorer/Sysblock controller code-export route is
  `GetModelCodeGenerationOptions(modelName)` ->
  `SetModelCodeGenerationOptions(modelName, options)` ->
  `GenerateModelCode(modelName)`.
known_sources:
  - `Docs/Workflows/mworks_codegen_controller_runtime.md` records this API
    route as the current workflow.
  - `PROGRESS.md` says the current MCP `translate_model` wrapper calls
    `TranslateModel(modelName)` and is not code-export evidence.
contradictions_or_history:
  Earlier use of `translate_model` can be mistaken for generated C/C++ export.
  That interpretation is rejected for this project.
current_evidence_needed:
  Round 2 should verify the current workflow text and any MCP/tool changes
  before saying the wrapper is still missing a dedicated codegen surface.
formal_target_if_promoted:
  `Docs/Workflows/mworks_codegen_controller_runtime.md` or
  `Docs/Workflows/debug_mcp.md` only if the current wording lacks the warning.
next_round_action:
  Re-read current MCP wrappers/tool index and classify this as already
  formalized or as a narrow MCP-improvement candidate.
```

### CODEGEN-MEM-002 - PID Demo Generated Runtime Shape

```text
round: 1
status: candidate
risk: high
candidate_statement:
  Probe model `AWFF_PID_Sysblock_Demo` generated C/H runtime files under
  `Results/codegen_probe/AWFF_PID_Sysblock_Demo_api/AWFF_PID_Sysblock_Demo/`.
  The current generated runtime exposes `Init()`, `Step()`, global input/output
  structs, input field `z_error`, output field `thrust_cmd`, and sample time
  `0.01 s`.
known_sources:
  - `Docs/Workflows/mworks_codegen_controller_runtime.md`.
  - `Results/codegen_probe/AWFF_PID_Sysblock_Demo_api/runtime_check.json`.
  - Generated source/header files under
    `Results/codegen_probe/AWFF_PID_Sysblock_Demo_api/AWFF_PID_Sysblock_Demo/`.
contradictions_or_history:
  Runtime shape is model-specific and codegen-option-specific. Do not assume
  the same globals, field names, or sample time for other controllers.
current_evidence_needed:
  Round 2 should re-read `runtime_check.json`, generated headers, and the
  reusable check script before recording this as verified cache.
formal_target_if_promoted:
  Existing codegen workflow, not algorithm design docs.
next_round_action:
  Verify fields and sample time against current generated code and classify the
  result as PID-demo-only.
```

### CODEGEN-MEM-003 - Pre-SIL Runtime Harness Gate

```text
round: 1
status: candidate
risk: high
candidate_statement:
  `Scripts/mworks/check_codegen_runtime.py` is the reusable pre-SIL gate. It
  checks required generated files, confirms `Init`/`Step`, input/output globals,
  sample time, C99 compile status, and an optional temporary harness run without
  polluting generated evidence folders.
known_sources:
  - `Docs/Workflows/mworks_codegen_controller_runtime.md`.
  - `Results/codegen_probe/AWFF_PID_Sysblock_Demo_api/runtime_check.json`.
  - `Results/codegen_probe/AWFF_PID_Sysblock_Demo_api/runtime_constant_0p1_check.json`.
contradictions_or_history:
  A compile/harness smoke pass proves that generated C can be driven as a
  runtime candidate. It does not prove equivalence to MWORKS for arbitrary
  inputs or controllers.
current_evidence_needed:
  Round 2 should inspect the current script/test behavior and confirm temporary
  artifacts are removed.
formal_target_if_promoted:
  Existing codegen workflow or test workflow only.
next_round_action:
  Verify current script output schema and classify as pre-SIL gate, not final
  runtime acceptance.
```

### CODEGEN-MEM-004 - Zero-Input SIL Smoke Is Limited

```text
round: 1
status: candidate
risk: high
candidate_statement:
  `sil_zero_input_check.json` passes `zero_input_sil_smoke` for the PID demo
  with max error `0.0`, but it is only a startup/reference check and not a
  complete SIL proof.
known_sources:
  - `Results/codegen_probe/AWFF_PID_Sysblock_Demo_api/sil_zero_input_check.json`.
  - `Docs/Workflows/mworks_codegen_controller_runtime.md`.
contradictions_or_history:
  Old shorthand such as "SIL passed" is unsafe unless the input class,
  reference source, tolerance, and limitations are stated.
current_evidence_needed:
  Round 2 should re-read the JSON limitations and script behavior before
  quoting the result.
formal_target_if_promoted:
  Existing codegen workflow already records this boundary.
next_round_action:
  Mark as verified only with the explicit `zero_input_sil_smoke` qualifier.
```

### CODEGEN-MEM-005 - Nonzero Constant-Input PID Demo SIL

```text
round: 1
status: candidate
risk: high
candidate_statement:
  The PID demo constant-input SIL check compares MWORKS/Sysblock reference
  output for `z_error = 0.1` against generated C runtime output for input
  sequence `0.1,0.1,0.1,0.1`. Current cache evidence says it passes with
  `max_abs_error = 8.934736470678217e-07` under tolerance `1e-5`.
known_sources:
  - `Models/QuadrotorControllerBlocks/AWFF_PID_Sysblock_Demo_SIL_Constant.mo`.
  - `Results/codegen_probe/AWFF_PID_Sysblock_Demo_api/mworks_constant_0p1_reference.json`.
  - `Results/codegen_probe/AWFF_PID_Sysblock_Demo_api/runtime_constant_0p1_check.json`.
  - `Results/codegen_probe/AWFF_PID_Sysblock_Demo_api/sil_constant_0p1_check.json`.
  - `PROGRESS.md` architecture validation checkpoint.
contradictions_or_history:
  This validates the architecture path for the PID demo only. It does not make
  every generated controller runtime-authoritative.
current_evidence_needed:
  Round 2 should re-read both reference and comparison JSONs, confirm
  `source_label=MWORKS_MCP_PLUS_GENERATED_C_RUNTIME`, and preserve the
  timestamp-shift limitation.
formal_target_if_promoted:
  Existing codegen workflow and architecture gate notes only.
next_round_action:
  Verify as `PID demo constant-input SIL smoke/pass`, not as broad controller
  acceptance.
```

### CODEGEN-MEM-006 - Time-Varying SIL Remains Open

```text
round: 1
status: candidate
risk: high
candidate_statement:
  Stronger SIL remains open: each target exported controller must compare the
  same nonzero/time-varying input trace through MWORKS/Sysblock and generated
  C/C++ runtime before its runtime can replace or stand beside MWORKS evidence.
known_sources:
  - `Docs/Workflows/mworks_codegen_controller_runtime.md`.
  - `PROGRESS.md` says stronger time-varying input SIL remains open before
    claiming all generated controllers are runtime-authoritative.
contradictions_or_history:
  A passed PID demo constant-input check can be overgeneralized. That is
  explicitly forbidden.
current_evidence_needed:
  Round 2 should check whether any newer time-varying SIL artifacts exist.
formal_target_if_promoted:
  Existing codegen workflow and any future controller-runtime acceptance
  checklist.
next_round_action:
  Search only project-local codegen/result paths for newer time-varying SIL
  evidence; otherwise keep this as open.
```

### CODEGEN-MEM-007 - Generated Runtime Cannot Replace MWORKS Before SIL

```text
round: 1
status: candidate
risk: high
candidate_statement:
  Generated or external C/C++ runtime output is not official MWORKS simulation
  evidence and cannot replace MWORKS/Sysplorer results before per-controller
  SIL equivalence is complete. It should be labeled as generated-runtime or SIL
  evidence with explicit source labels.
known_sources:
  - `Docs/Workflows/mworks_codegen_controller_runtime.md`.
  - `Docs/Cache/session_memory_migration/02_round2_review/round2_mworks_controller_evidence_memory_20260604.md`.
  - `AGENTS.md` simulation evidence rule.
contradictions_or_history:
  Long-session architecture work discussed runtime handoff to ROS2/PX4/V6X.
  That future route still needs per-controller evidence and must not blur
  source labels.
current_evidence_needed:
  Round 2 should cross-check evidence-source workflow wording and current
  result manifests.
formal_target_if_promoted:
  Existing codegen workflow or simulation evidence workflow if a concise
  cross-reference is missing.
next_round_action:
  Verify source-label wording and decide whether this is already formalized.
```

## Rejected Or Superseded Historical Items

```text
REJ-CODEGEN-001:
  Treating Sysplorer MCP `translate_model` as C/C++ code-export evidence is
  rejected for current MoSim codegen claims.

REJ-CODEGEN-002:
  Treating compile-only or harness-only generated C success as SIL equivalence
  is rejected.

REJ-CODEGEN-003:
  Treating zero-input SIL smoke as complete SIL is rejected.

REJ-CODEGEN-004:
  Treating the PID demo constant-input result as proof that all generated
  controllers are runtime-authoritative is rejected.

REJ-CODEGEN-005:
  Replacing MWORKS/Sysplorer simulation evidence with generated C runtime
  output before per-controller SIL is rejected.
```

## Round 2 Backlog

1. Re-read `Docs/Workflows/mworks_codegen_controller_runtime.md` and the
   current generated-code scripts/tests.
2. Re-read the current generated headers and result JSONs under
   `Results/codegen_probe/AWFF_PID_Sysblock_Demo_api/`.
3. Check whether newer time-varying SIL artifacts or per-controller SIL bundles
   exist in project-local result paths.
4. Classify each item as `round2_verified`, `already_formalized`,
   `rejected`, `superseded`, or `needs_user_review`.
5. Only after round 2, update
   `round3_promotion_rejection_map_20260604.md` with narrow promotion or
   rejection decisions.

## Do Not Promote Yet

- Any claim that all generated MWORKS controllers are runtime-authoritative.
- Any claim that `translate_model` is sufficient code export.
- Any target-controller runtime acceptance without that controller's own SIL
  bundle.
- Any replacement of official MWORKS/Sysplorer simulation evidence by generated
  C runtime output without explicit source labels and per-controller SIL.
