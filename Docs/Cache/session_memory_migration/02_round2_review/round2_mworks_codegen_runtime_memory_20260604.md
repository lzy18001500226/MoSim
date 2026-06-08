# Round 2 MWORKS Codegen Runtime Memory Audit

Date: 2026-06-04 CST

Scope: verify long-session memory about MWORKS/Sysblock code generation,
generated C runtime shape, compile/runtime harness checks, and SIL smoke
evidence against current project files. This is cache-only. It does not promote
the PID demo result into a general controller-runtime claim.

## Status

```text
round: 2
topic: MWORKS code generation and generated controller runtime
status: mixed_round2_verified_and_needs_round3
risk: high
formal_docs_patched_this_round: none
cache_only: true
```

## Sources Re-Read

| Source | Finding |
|---|---|
| `Docs/Workflows/mworks_codegen_controller_runtime.md` | Current formal workflow separates `GenerateModelCode` from `TranslateModel`, records the PID demo generated runtime shape, and requires per-controller SIL before runtime authority. |
| `Scripts/mworks/check_codegen_runtime.py` | Pre-SIL checker enforces project-local paths, required generated files, `Init`/`Step`, input/output globals, sample time, C99 compile, and optional temporary runtime harness. |
| `Scripts/tests/test_mworks_codegen_runtime.py` | Regression test asserts schema, adapter shape, sample time, input/output fields, compile gate, temp cleanup, and project path guard. |
| `Scripts/mworks/check_codegen_sil_equivalence.py` | SIL smoke checker compares generated C runtime output to either an offline zero reference or MWORKS reference JSON. It records limitations and does not compare timestamps by default. |
| `Scripts/tests/test_mworks_codegen_sil_equivalence.py` | Regression test asserts zero-input smoke, nonzero sequence fails without MWORKS reference, and constant-input MWORKS reference passes under tolerance. |
| `Results/codegen_probe/AWFF_PID_Sysblock_Demo_api/runtime_check.json` | Current PID demo generated C has required files, `Step`/`Init`, input `z_error`, output `thrust_cmd`, sample time `0.01`, C99 compile ok, and runtime harness ok. |
| `Results/codegen_probe/AWFF_PID_Sysblock_Demo_api/sil_zero_input_check.json` | Zero-input smoke passes with max error `0.0`, but limitations state nonzero SIL remains required. |
| `Results/codegen_probe/AWFF_PID_Sysblock_Demo_api/mworks_constant_0p1_reference.json` | MWORKS MCP reference for constant `z_error=0.1`, variable `cmd_sum.y`, with check and simulate success. |
| `Results/codegen_probe/AWFF_PID_Sysblock_Demo_api/runtime_constant_0p1_check.json` | Generated C runtime harness for input sequence `0.1,0.1,0.1,0.1` and output order comparison data. |
| `Results/codegen_probe/AWFF_PID_Sysblock_Demo_api/sil_constant_0p1_check.json` | Nonzero constant-input PID demo SIL smoke passes with max error `8.934736470678217e-07` under tolerance `1e-5`. |
| `Docs/Design/09_UE_ROS_MWORKS无人机仿真架构重构.md` | Gate A already records the same limited status: compile/runtime/zero-input and nonzero constant-input PID demo passed; time-varying SIL remains open. |

## Round 2 Findings

### CODEGEN-MEM-001 - Official Codegen API Route

```text
round: 2
status: round2_verified_for_cache
risk: high
candidate_statement:
  The correct Sysplorer/Sysblock controller code-export route is
  `GetModelCodeGenerationOptions(modelName)` ->
  `SetModelCodeGenerationOptions(modelName, options)` ->
  `GenerateModelCode(modelName)`. `TranslateModel(modelName)` is not code
  export evidence.
current_evidence:
  - `Docs/Workflows/mworks_codegen_controller_runtime.md` records this route
    and explicitly rejects using current MCP `translate_model` as code-export
    proof.
  - `Docs/Design/09_*` records the architecture update that code generation is
    verified through `GenerateModelCode`, not only `TranslateModel`.
contradictions_or_history:
  Earlier `translate_model` success can be mistaken for generated C/C++ export.
  That interpretation remains rejected.
formal_target_if_promoted:
  Already represented in codegen workflow and architecture doc.
next_round_action:
  Round 3 can mark this already formalized unless the MCP/debug workflow needs
  a narrow "translate_model is not codegen" pointer.
```

### CODEGEN-MEM-002 - PID Demo Generated Runtime Shape

```text
round: 2
status: round2_verified_for_cache_pid_demo_only
risk: high
candidate_statement:
  Probe model `AWFF_PID_Sysblock_Demo` generated a C runtime with required
  files, `Step` and `Init`, global input/output structs, input field `z_error`,
  output field `thrust_cmd`, and sample time `0.01 s`.
current_evidence:
  - `runtime_check.json` has schema
    `mosim.mworks_codegen_runtime_check.v1`, no missing required files,
    functions `Step` and `Init`, input global
    `awff_pid_sysblock_demoGbIn.z_error`, output global
    `awff_pid_sysblock_demoGbOut.thrust_cmd`, and sample time `0.01`.
  - `Scripts/tests/test_mworks_codegen_runtime.py` asserts these fields.
contradictions_or_history:
  This shape is model-specific and codegen-option-specific. It must not be
  assumed for other controllers.
formal_target_if_promoted:
  Already represented in `Docs/Workflows/mworks_codegen_controller_runtime.md`.
next_round_action:
  Round 3 should keep this wording PID-demo-only.
```

### CODEGEN-MEM-003 - Pre-SIL Compile And Harness Gate

```text
round: 2
status: round2_verified_for_cache_pre_sil_only
risk: high
candidate_statement:
  `Scripts/mworks/check_codegen_runtime.py` is a reusable pre-SIL gate. It
  verifies generated files and runtime interface, compiles with C99, and can
  run a temporary harness without leaving build residue in evidence folders.
current_evidence:
  - `check_codegen_runtime.py` uses `project_path()` to reject paths outside
    the project boundary.
  - The compile and run harness use temporary directories under `Results/tmp`
    and record `object_dir_removed=true` / `temp_dir_removed=true`.
  - `runtime_check.json` and `runtime_constant_0p1_check.json` show compile and
    harness checks passed.
  - `test_codegen_runtime_compile_gate()` verifies compile and harness cleanup.
contradictions_or_history:
  A compile/harness pass proves generated C can be driven as a runtime
  candidate. It does not prove MWORKS equivalence for arbitrary inputs or
  controllers.
formal_target_if_promoted:
  Already represented in the codegen workflow and tests.
next_round_action:
  Round 3 can map this as already formalized or keep cache-only.
```

### CODEGEN-MEM-004 - Zero-Input SIL Smoke Is Limited

```text
round: 2
status: round2_verified_for_cache_limited_smoke
risk: high
candidate_statement:
  `sil_zero_input_check.json` passes `zero_input_sil_smoke` with max error
  `0.0`, but it is only a startup/reference smoke check.
current_evidence:
  - `sil_zero_input_check.json` has `gate_type=zero_input_sil_smoke`,
    input sequence `0,0,0`, tolerance `1e-12`, max error `0.0`, and `ok=true`.
  - Its limitations say it uses zero input only unless a MWORKS external-input
    injection reference is supplied, and nonzero SIL remains required.
  - `test_zero_input_sil_smoke_contract()` asserts the limitations.
contradictions_or_history:
  "SIL passed" without specifying zero-input smoke is unsafe.
formal_target_if_promoted:
  Existing workflow only.
next_round_action:
  Round 3 should record the accepted wording as "zero-input SIL smoke", not
  broad SIL completion.
```

### CODEGEN-MEM-005 - Nonzero Constant-Input PID Demo SIL

```text
round: 2
status: round2_verified_for_cache_pid_demo_only
risk: high
candidate_statement:
  The PID demo constant-input SIL smoke compares MWORKS/Sysblock output
  `cmd_sum.y` for `z_error=0.1` with generated C runtime output for
  `0.1,0.1,0.1,0.1`; current evidence passes with max absolute error
  `8.934736470678217e-07` under tolerance `1e-5`.
current_evidence:
  - `mworks_constant_0p1_reference.json` has `source_label=MWORKS_MCP`,
    `reference_variable=cmd_sum.y`, `input_mode=constant`,
    `input_value=0.1`, `check_model_ok=true`, and `simulate_model_ok=true`.
  - `runtime_constant_0p1_check.json` records generated C runtime rows for the
    same constant input sequence.
  - `sil_constant_0p1_check.json` has
    `source_label=MWORKS_MCP_PLUS_GENERATED_C_RUNTIME`, `gate_type=
    nonzero_input_sil_smoke`, `ok=true`, tolerance `1e-5`, and max error
    `8.934736470678217e-07`.
  - `test_nonzero_constant_mworks_reference_passes()` asserts this gate passes.
contradictions_or_history:
  This is PID-demo constant-input smoke evidence only. It cannot authorize all
  generated controllers or time-varying runtime behavior.
formal_target_if_promoted:
  Already represented in codegen workflow and architecture Gate A.
next_round_action:
  Round 3 should preserve the source label, tolerance, and timestamp-shift
  limitation if any formal wording is touched.
```

### CODEGEN-MEM-006 - Timestamp Shift Limitation

```text
round: 2
status: round2_verified_for_cache
risk: high
candidate_statement:
  Current constant-input SIL compares output order, not equal timestamps:
  MWORKS reports the first Sysblock output at `t=0`, while the generated C
  harness records after `Step()`, one sample later.
current_evidence:
  - `mworks_constant_0p1_reference.json` states the time-alignment note.
  - `sil_constant_0p1_check.json` limitations repeat the output-order
    comparison and one-sample timestamp shift.
  - `check_codegen_sil_equivalence.py` calls `compare_rows(...,
    compare_time=False)`.
contradictions_or_history:
  A result that passes by output order should not be described as a timestamp
  equality proof.
formal_target_if_promoted:
  Existing workflow already records the limitation.
next_round_action:
  Keep as cache guard unless a round-3 patch quotes the SIL metric.
```

### CODEGEN-MEM-007 - Time-Varying SIL Remains Open

```text
round: 2
status: round2_verified_open
risk: high
candidate_statement:
  Stronger SIL remains open: each target exported controller needs its own
  nonzero/time-varying input trace through MWORKS/Sysblock and generated C/C++
  runtime before it can be runtime-authoritative.
current_evidence:
  - `Docs/Workflows/mworks_codegen_controller_runtime.md` lists the remaining
    stronger SIL gate.
  - `Docs/Design/09_*` Gate A says time-varying input SIL remains open for
    final controller-runtime authority.
  - Project-local search found no newer time-varying controller SIL artifact in
    the current codegen/result paths.
contradictions_or_history:
  The PID demo constant-input pass can be overgeneralized. That is explicitly
  forbidden.
formal_target_if_promoted:
  Already represented in codegen workflow and architecture docs.
next_round_action:
  Round 3 should map this as open, not promoted.
```

### CODEGEN-MEM-008 - Generated Runtime Is Not MWORKS Evidence Before SIL

```text
round: 2
status: round2_verified_for_cache
risk: high
candidate_statement:
  Generated or external C/C++ runtime output is not official MWORKS/Sysplorer
  simulation evidence by itself. It must be labeled as generated-runtime or SIL
  evidence until per-controller equivalence passes.
current_evidence:
  - `Docs/Workflows/mworks_codegen_controller_runtime.md` says generated or
    external C/C++ results cannot replace MWORKS/Sysplorer simulation evidence
    before equivalence.
  - `AGENTS.md` simulation evidence rule separates MWORKS evidence from offline
    or generated validation data.
  - Existing MWORKS controller evidence round-2 cache already enforces source
    labeling.
contradictions_or_history:
  Older shorthand may imply generated runtime is already a replacement path.
  The verified state is a candidate path plus PID-demo smoke evidence.
formal_target_if_promoted:
  Already represented in workflow and AGENTS rules.
next_round_action:
  Coordinate with round-3 promotion/rejection map; avoid duplicate policy text.
```

## Rejected Or Superseded Historical Items

| Historical Item | Current Treatment |
|---|---|
| `translate_model` success as C/C++ code-export proof | Rejected. Use `GenerateModelCode`. |
| Zero-input SIL smoke as complete SIL | Rejected. It is startup/reference smoke only. |
| PID demo constant-input SIL as proof all generated controllers are valid | Rejected. PID-demo-only architecture evidence. |
| Output-order SIL as timestamp-equality proof | Rejected; current comparison has one-sample timestamp shift. |
| Generated C runtime output replacing MWORKS evidence before per-controller SIL | Rejected. |

## Round 3 Promotion Candidates

Only these narrow items are candidates for round 3:

1. A concise pointer in the round-3 map that the codegen route is already
   formalized: `GenerateModelCode`, not `TranslateModel`.
2. A concise pointer that current evidence is PID-demo-only:
   compile/runtime harness, zero-input SIL smoke, and nonzero constant-input
   SIL smoke passed, but time-varying/per-controller SIL remains open.
3. A rejected-pattern entry for overgeneralizing PID demo SIL into all
   controller runtimes.

No target controller runtime, generated C/C++ production authority, or
time-varying SIL claim is ready for promotion from this cache.

## Verification Needed Before Round 3

```text
1. Re-read `Docs/Workflows/mworks_codegen_controller_runtime.md` and the latest
   `Results/codegen_probe/**/sil_*` files before quoting metrics.
2. Search project-local codegen/result paths for newer target-controller or
   time-varying SIL artifacts.
3. If a target controller is involved, require that controller's own generated
   code hash, options snapshot, compile result, MWORKS reference trace, and SIL
   comparison.
4. Keep generated-runtime evidence separate from MWORKS/Sysplorer simulation
   evidence unless per-controller equivalence is complete.
```
