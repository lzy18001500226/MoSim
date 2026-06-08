# Round 2 MWORKS Controller Evidence Memory Audit

Date: 2026-06-04 CST

Scope: verify the long-session memory around MWORKS/Sysplorer/Syslab
simulation evidence, controller claims, smoke metrics, and graphical Sysblock
counterparts. This is a cache-only round 2 audit. It does not promote any old
chat claim as final controller or simulation performance.

## Status

```text
round: 2
topic: MWORKS controller and simulation evidence boundary
status: round2_verified_for_cache
risk: high
formal_docs_patched_this_round: none
cache_only: true
```

## Sources Re-Read

| Source | Finding |
|---|---|
| `AGENTS.md` | Current non-negotiable rules separate `source=MWORKS_MCP`, `source=MWORKS_GUI`, and `source=offline_script`; formal controller claims need MWORKS evidence and behavior-equivalent graphical Sysblock counterparts. |
| `Docs/Workflows/run_simulation.md` | Interactive MWORKS model load/check/sim/plot/result work must use MCP when healthy. `check_model ok` and `simulate_model ok` are execution evidence only, not controller-quality evidence. |
| `Docs/Workflows/produce_simulation_evidence.md` | Formal evidence bundles require source labels, raw CSV, metrics, figures/replay, and `quality_status=pass` for full-performance claims. `quality_status=smoke_only` is chain validation only. |
| `Docs/Workflows/calc_metrics.md` | Metrics are reproducibility artifacts computed from raw results; they do not replace source labels or simulation provenance. |
| `Docs/Workflows/build_sysblock_graphical_controller.md` | Graphical Sysblock topology must be built/repaired through official Sysplorer/Sysblock APIs and accepted only when `structure_ok=true` and `behavior_equivalence_ok=true` or a gap is explicitly marked. |
| `Docs/Skills/Mworks/mworks-simulation-evidence/SKILL.md` | Repeats evidence classes and acceptance checks; offline CSV/HTML replay must not be presented as official MWORKS simulation evidence. |
| `Results/unreal_scene_mapping/factoryenvironmentcollect/mworks_smoke/metrics/*.json` | Factory scene-control evidence is `source=MWORKS_MCP`, but `quality_status=smoke_only`; it validates automation chain only. |
| `Results/unreal_scene_mapping/derelictcorridormegascans/mworks_smoke/metrics/*.json` | Derelict scene-control evidence is also `source=MWORKS_MCP` and `quality_status=smoke_only`. |

## Round 2 Findings

### MWORKS-MEM-001 - Evidence Source Labels

```text
round: 2
status: round2_verified_for_cache
risk: high
candidate_statement:
  New conversations must recover the evidence-source boundary first:
  `source=MWORKS_MCP` and `source=MWORKS_GUI` are real MWORKS/Sysplorer
  evidence routes; `source=offline_script` is design/reference validation and
  must not be described as official MWORKS simulation evidence.
current_evidence:
  - `AGENTS.md` simulation evidence rule.
  - `Docs/Workflows/produce_simulation_evidence.md` valid source labels.
  - `Docs/Skills/Mworks/mworks-simulation-evidence/SKILL.md` evidence classes.
contradictions_or_history:
  Earlier generated CSV, HTML replay, offline point clouds, and Python/Julia
  demos may be useful, but they cannot be promoted as official MWORKS evidence
  unless the official model was run through MWORKS/Sysplorer/MCP or GUI.
formal_target_if_promoted:
  Already represented in `AGENTS.md` and MWORKS evidence workflows.
next_round_action:
  Round 3 should probably mark this as already formalized unless a shorter
  recovery pointer is needed.
```

### MWORKS-MEM-002 - Smoke Metrics Are Not Full Controller Performance

```text
round: 2
status: round2_verified_for_cache
risk: high
candidate_statement:
  Factory and Derelict `mworks_smoke` runs are real Sysplorer/MCP smoke
  evidence, but they are not full controller-performance claims because their
  metrics files explicitly set `quality_status=smoke_only`.
current_evidence:
  - `factoryenvironmentcollect/mworks_smoke/metrics/...json`:
    `source=MWORKS_MCP`, `evidence_level=real_sysplorer_mcp_ue_scene_control_smoke`,
    `quality_status=smoke_only`.
  - `derelictcorridormegascans/mworks_smoke/metrics/...json` has the same
    source and smoke-only boundary.
  - `produce_simulation_evidence.md` says `smoke_only` is only automation-chain
    validation.
contradictions_or_history:
  High scores in a smoke metrics JSON do not by themselves support final
  performance claims. The `quality_status` field governs claim scope.
formal_target_if_promoted:
  Already represented in evidence workflow; round 3 may only add a pointer if
  new sessions keep misreading smoke metrics.
next_round_action:
  Round 3 must re-read the exact metrics file before quoting a result and must
  state both source and quality status.
```

### MWORKS-MEM-003 - `check_model` / `simulate_model` Scope

```text
round: 2
status: round2_verified_for_cache
risk: high
candidate_statement:
  `check_model ok` and `simulate_model ok` prove the model loaded/checked/ran;
  they do not prove the controller is good. Controller quality requires raw
  variables, metrics, quality gate, and claim-specific acceptance.
current_evidence:
  - `Docs/Workflows/produce_simulation_evidence.md` explicitly says this.
  - `Docs/Workflows/run_simulation.md` includes the same warning and quality
    status meanings.
contradictions_or_history:
  Old chat summaries may have shortened "simulation ran" into "scenario
  completed". That is unsafe without quality status and metrics.
formal_target_if_promoted:
  Already represented in workflow docs.
next_round_action:
  Round 3 can mark as already formalized.
```

### MWORKS-MEM-004 - Graphical Sysblock Counterpart Requirement

```text
round: 2
status: round2_verified_for_cache
risk: high
candidate_statement:
  A formal controller simulation claim needs a behavior-equivalent graphical
  Sysblock counterpart, or the result must be labeled as equation-bridge
  evidence with the graphical model task still open.
current_evidence:
  - `AGENTS.md` says formal controller simulation claims must maintain a
    graphical Sysblock model that exposes signal paths, saturation, filtering,
    discrete state, delay, mode logic, fault logic, and allocation behavior.
  - `build_sysblock_graphical_controller.md` acceptance requires
    `structure_ok=true` and `behavior_equivalence_ok=true` or an explicit gap.
  - `run_simulation.md` documents current review handling for
    `Sunray150CompleteSystemGraphical_Sysblock` and the equation-controller
    workaround for an embedded graphical Sysblock multi-input port limitation.
contradictions_or_history:
  A graphical model that is only a screenshot wrapper, empty shell, or
  non-equivalent display artifact does not satisfy the controller-deliverable
  rule.
formal_target_if_promoted:
  Already formalized in `AGENTS.md` and
  `Docs/Workflows/build_sysblock_graphical_controller.md`.
next_round_action:
  Round 3 should check current graphical status before claiming a specific
  controller is complete.
```

### MWORKS-MEM-005 - MCP-First Interactive MWORKS Work

```text
round: 2
status: round2_verified_for_cache
risk: medium
candidate_statement:
  When Sysplorer/Syslab MCP tools are healthy, interactive model loading,
  checking, simulation, plotting, animation, and GUI review should go through
  MCP directly. Project scripts remain for batch export, metrics, summaries,
  regression automation, and wrapper diagnostics.
current_evidence:
  - `AGENTS.md` MCP minimal-impact rule.
  - `Docs/Workflows/run_simulation.md` direct MCP tool sequence and wrapper
    handshake notes.
contradictions_or_history:
  Long chat history contains many script-level probes. Those are useful for
  automation but should not replace healthy MCP for interactive model work.
formal_target_if_promoted:
  Already represented in `AGENTS.md` and `run_simulation.md`.
next_round_action:
  Mark as already formalized unless a new MCP failure reveals a reusable repair
  route.
```

## Rejected Or Superseded Historical Items

| Historical Item | Current Treatment |
|---|---|
| Offline generated CSV/HTML/point-cloud as official MWORKS evidence | Rejected unless clearly labeled `source=offline_script`. |
| `check_model ok` or `simulate_model ok` as proof of controller quality | Rejected; needs metrics and quality gate. |
| `quality_status=smoke_only` as full performance success | Rejected; smoke-only validates automation chain. |
| Graphical Sysblock screenshot wrapper as controller deliverable | Rejected; must expose behavior-equivalent topology or be marked incomplete. |
| Equation bridge as replacement for graphical Sysblock | Rejected; equation bridge can be executable evidence but graphical counterpart remains open. |

## Round 3 Promotion Candidates

Most stable rules are already formalized. Round 3 should avoid duplicating
them and only promote a short recovery pointer if needed:

1. Always state both `source` and `quality_status` when carrying MWORKS result
   memory into a new conversation.
2. Treat `mworks_smoke` as automation-chain validation, not final controller
   performance.
3. Before claiming a controller scenario complete, check graphical Sysblock
   counterpart status and behavior-equivalence evidence.

No new controller-performance claim is ready for promotion from this cache.

## Verification Needed Before Round 3

```text
1. Re-read the exact scenario metrics JSON and MCP log before quoting any
   numeric result.
2. Confirm `quality_status=pass` before using a result for full-performance
   claims.
3. Confirm the graphical Sysblock counterpart has structure and behavior
   evidence before saying a controller is complete.
4. Keep offline script output, UE/RViz visual evidence, and MWORKS simulation
   evidence in separate categories.
```
