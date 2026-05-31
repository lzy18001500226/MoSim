# COAGENT-ARCH-LONGRUN-01 Evidence Label Doctor Design

Date: 2026-05-30
Status: design contract for `COAGENT-IMPL-NEXT-07`

## Purpose

CoAgent must not confuse design notes, offline demos, manual review, GUI
inspection, MCP execution, and real product evidence. The evidence-label doctor
should check that packets, proof packages, reports, and stress-test artifacts
use source labels honestly.

This is a design artifact. It does not implement the doctor, run simulations,
open GUI tools, call MCP, or promote any evidence claim.

## Core Rule

```text
the label must describe how the evidence was produced, not what the worker
wishes the evidence proved
```

Evidence labels are about provenance and strength. They are not marketing
terms.

## Labels

Initial allowed labels:

| Label | Meaning |
|---|---|
| `design_only` | design text, architecture blueprint, or requirement draft |
| `offline_script` | script-level computation without official tool execution |
| `manual_review` | human visual/semantic inspection |
| `MWORKS_MCP` | produced through Sysplorer/Syslab/MWORKS MCP execution |
| `MWORKS_GUI` | produced by manual or GUI MWORKS execution |
| `UE_MCP` | produced through Unreal Editor MCP execution |
| `UE_GUI` | produced by manual Unreal Editor GUI action |
| `Fab_manual_import` | asset import performed manually by user |
| `git_metadata` | Git status/diff/log metadata |
| `runtime_metadata` | CoAgent runtime, mailbox, packet, or transport state |
| `external_reference` | vendor article, paper, documentation, or local reference project |

Unknown labels fail unless added by design update.

## Inputs

The future doctor should accept:

```text
--path <file-or-directory>
--mode scan|strict|fixtures
--task-id <optional expected task id>
--json-output <optional path>
```

`scan` reports findings without blocking. `strict` rejects invalid labels,
inflation, missing evidence paths, and forbidden proof claims. `fixtures` runs
known positive and negative examples.

## Label Strength Order

Evidence strength is not a total order for every domain, but the doctor needs
a conservative escalation model:

```text
design_only
  < external_reference
  < offline_script
  < manual_review
  < UE_GUI / MWORKS_GUI / Fab_manual_import
  < UE_MCP / MWORKS_MCP
```

`runtime_metadata` and `git_metadata` prove process state only. They cannot
prove product behavior.

Manual review can confirm visual or acceptance observations. It cannot replace
numeric simulation evidence, scene collision truth, path feasibility, or
official-model execution.

## Required Evidence Fields

Each labeled evidence item should include:

| Field | Validation |
|---|---|
| `label` | one allowed label |
| `path` | project-local path or approved external source reference |
| `produced_by` | tool, script, human, or source name |
| `produced_at` | timestamp or `unknown_for_reference` |
| `claim_supported` | exact claim this item supports |
| `limitations` | known limits or `none` |
| `review_owner` | required for manual, design, and high-risk evidence |

For MCP/GUI labels, also require a command/probe/log/result path when
available. If a GUI action was manual and no log exists, record
`manual_review` plus `MWORKS_GUI` or `UE_GUI` only for the exact manually
observed claim.

## Rejection Rules

Reject or block if:

- label is unsupported;
- evidence path is missing;
- evidence path is outside project scope without approved exception;
- `design_only` is used to claim implemented behavior;
- `offline_script` is used to claim MWORKS/Sysplorer execution;
- screenshot or manual review is used as UE planning truth;
- runtime metadata is used to claim product correctness;
- Git metadata is used to claim tests passed;
- external reference is copied into policy without adoption proposal;
- MWORKS/UE/Fab label lacks tool/probe/manual-import evidence;
- label claims current tool capability when the tool run is stale or blocked.

## Output JSON

The future doctor should write:

```json
{
  "ok": false,
  "decision": "reject",
  "scanned_paths": ["CoAgent/tasks/example"],
  "finding_codes": ["EVD_LABEL_INFLATED"],
  "findings": [
    {
      "code": "EVD_LABEL_INFLATED",
      "severity": "error",
      "path": "Results/example/metrics.yaml",
      "label": "MWORKS_MCP",
      "message": "offline script output cannot be labeled MWORKS_MCP"
    }
  ],
  "next_action": "downgrade label to offline_script or provide MWORKS_MCP result evidence"
}
```

Allowed decisions:

- `pass`;
- `pass_with_warnings`;
- `needs_review`;
- `block`;
- `reject`.

## Stable Finding Codes

| Code | Meaning |
|---|---|
| `EVD_LABEL_MISSING` | evidence item has no label |
| `EVD_LABEL_UNSUPPORTED` | label not in allowed vocabulary |
| `EVD_PATH_MISSING` | evidence path absent |
| `EVD_PATH_OUT_OF_SCOPE` | path outside project without exception |
| `EVD_LABEL_INFLATED` | label is stronger than provenance supports |
| `EVD_DESIGN_CLAIMS_IMPLEMENTED` | design-only evidence claims implementation |
| `EVD_OFFLINE_AS_MWORKS` | offline output labeled MWORKS evidence |
| `EVD_SCREENSHOT_AS_TRUTH` | visual artifact used as planning truth |
| `EVD_RUNTIME_AS_PRODUCT` | runtime metadata used as product correctness |
| `EVD_GIT_AS_TEST` | Git metadata used as test evidence |
| `EVD_EXTERNAL_UNADOPTED` | external reference used as policy without adoption record |
| `EVD_TOOL_PROBE_MISSING` | tool/MCP/GUI capability label lacks probe or manual record |
| `EVD_REVIEW_OWNER_MISSING` | high-risk, design, or manual evidence lacks reviewer |
| `EVD_LIMITATIONS_MISSING` | evidence item lacks limitations |

## Fixture Matrix

Positive fixtures:

| Fixture | Expected |
|---|---|
| design document labeled `design_only` for architecture claim | `pass` |
| offline plot labeled `offline_script` with limitations | `pass` |
| Sysplorer MCP result labeled `MWORKS_MCP` with result path | `pass` |
| UE manual import labeled `Fab_manual_import` with user action record | `pass_with_warnings` |
| Git diff labeled `git_metadata` for changed-file inventory | `pass` |

Negative fixtures:

| Fixture | Expected Codes |
|---|---|
| missing label | `EVD_LABEL_MISSING` |
| unsupported label | `EVD_LABEL_UNSUPPORTED` |
| offline CSV labeled `MWORKS_MCP` | `EVD_OFFLINE_AS_MWORKS` |
| screenshot labeled UE planning truth | `EVD_SCREENSHOT_AS_TRUTH` |
| design doc claims live Candidate A proof passed | `EVD_DESIGN_CLAIMS_IMPLEMENTED` |
| runtime event used to prove controller quality | `EVD_RUNTIME_AS_PRODUCT` |
| git status used to prove tests passed | `EVD_GIT_AS_TEST` |
| external repo idea promoted without adoption proposal | `EVD_EXTERNAL_UNADOPTED` |
| UE_MCP claim without probe/log | `EVD_TOOL_PROBE_MISSING` |

## Integration With Other Contracts

- `verification_gate_hardening.md` requires evidence labels for PX4 and UE
  stress tests.
- `stress_test_artifact_validator_design.md` should use these labels when
  checking PX4 matrices and UE truth manifests.
- `common_proof_package_validator_design.md` should call this doctor for
  proof-package evidence manifests.
- `operating_metrics_snapshot_design.md` should count unsupported claims and
  label inflation as quality drift.
- `external_adoption_store_checker_design.md` should prevent
  `external_reference` from becoming policy without proposal lifecycle.

## Implementation Boundary

The first doctor must be read-only:

- no simulation;
- no UE or MWORKS launch;
- no MCP calls;
- no web crawling;
- no external repo import;
- no Git staging, commit, or push;
- no automatic label rewriting.

It may report suggested label downgrades, but changing labels must remain a
separate reviewed edit.

## Design Decision

`COAGENT-IMPL-NEXT-07` should be implemented before CoAgent accepts any
product-adjacent proof as more than design. This doctor is the guard that keeps
offline demos, manual reviews, and real MCP/GUI evidence from being mixed in
the final task closeout.
