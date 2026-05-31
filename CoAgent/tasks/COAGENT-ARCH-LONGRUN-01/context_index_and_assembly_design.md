# COAGENT-ARCH-LONGRUN-01 Context Index And Assembly Design

Date: 2026-05-30
Status: design contract for context indexing and new-conversation assembly

## Purpose

CoAgent needs new conversations that understand the task without receiving the
full transcript. Existing context documents define what a context pack contains
and how stale context is acknowledged. This design adds the missing indexing
and assembly layer:

```text
task request
  -> required context slices
  -> indexed evidence retrieval
  -> bounded context assembly
  -> stale/rejected material filter
  -> dispatch-ready context pack
```

This is a design artifact. It does not implement a vector database, crawler,
automatic context generation, or automatic conversation dispatch.

## Core Principle

```text
retrieve by task need, not by recency or transcript volume
```

The right context pack is not the longest summary. It is the smallest pack that
lets a target conversation:

1. restate the canonical task goal;
2. know its scoped objective;
3. know what is accepted, rejected, pending, or gated;
4. find authoritative files;
5. avoid known stale assumptions;
6. produce a valid result packet or blocker.

## Context Index Families

| Index Family | Owner | Source Examples | Use |
|---|---|---|---|
| `task_index` | DispatchAgent | task charter, task board, runtime task state | canonical goal, topology, owners, open blockers |
| `decision_index` | KnowledgeSecretaryAgent | decision records, accepted/rejected ideas, review packets | accepted policy and stale alternatives |
| `context_index` | ContextMemoryAgent | context packs, context deltas, acknowledgements | freshness, supersession, required refresh |
| `evidence_index` | VerificationAgent | result packets, proof packages, audit commands, test outputs | what is actually proven versus designed |
| `safety_index` | SafetyComplianceAgent | blocker packets, gated-feature list, human-intervention protocol | forbidden actions and manual-review gates |
| `worktree_git_index` | DevOpsReleaseAgent | worktree bindings, integration packets, Git-heavy proof docs | file ownership, merge risk, large-change policy |
| `tool_capability_index` | ToolchainMCPAgent | MCP health, capability cards, failure findings | tool availability and fallback boundaries |
| `external_adoption_index` | ExternalIntelligenceAgent + KnowledgeSecretaryAgent | adoption queue and proposal contract | external ideas accepted, rejected, deferred, or portable-only |
| `product_scope_index` | ProductStrategyAgent | product appetite, stress-test proof packages | scope, non-goals, product acceptance |

Each index family may be implemented later as files, YAML manifests, SQLite,
or another reviewed store. The design requirement is the same: context assembly
must cite index records, not raw memory.

## Context Slice Types

| Slice | Required When | Source |
|---|---|---|
| `goal_slice` | every conversation | task charter, runtime task |
| `role_slice` | every conversation | task packet, department mapping |
| `authority_slice` | every conversation | AGENTS, status, gate docs |
| `accepted_decisions_slice` | every conversation | decision index |
| `rejected_assumptions_slice` | every high-risk or repeated task | decision index, external adoption rejections |
| `evidence_slice` | proof, review, implementation, product tasks | evidence index |
| `tool_capability_slice` | MCP/UE/MWORKS/Fab/tool tasks | tool capability index |
| `safety_slice` | any tool, external path, credential, GUI, Git, or destructive-risk task | safety index |
| `worktree_slice` | multi-conversation code work or Git-heavy tasks | worktree_git_index |
| `external_learning_slice` | research/adoption tasks | external_adoption_index |
| `product_scope_slice` | PX4, UE, RflySim-like product, competition tasks | product_scope_index |
| `closeout_slice` | all scoped conversations | required result packet, review owner, close condition |

## Assembly Inputs

Dispatch or ContextMemoryAgent must know:

```yaml
task_id:
canonical_task_goal:
conversation_objective:
conversation_role:
proof_path: A | B | C | D | E | custom
risk_level: low | medium | high
read_scope:
write_scope:
expected_result_path:
review_owner:
tool_surfaces:
worktree_binding:
known_blockers:
```

If these inputs are missing, the output is not a context pack. It is a blocker
or intake-repair request.

## Assembly Algorithm

1. Load the canonical task record and task board.
2. Determine required slice types from task class, proof path, risk level,
   tool surfaces, and write scope.
3. Query each index family for the smallest source-linked records that match
   the slice.
4. Mark each retrieved record as `accepted`, `pending`, `rejected`,
   `superseded`, `blocked`, or `unknown`.
5. Drop or quarantine records marked `superseded` unless they explain a
   rejected assumption the worker must avoid.
6. Prefer pointers to long files over copied text.
7. Include direct text only for task goal, stop condition, current blockers,
   accepted decisions, rejected assumptions, and result contract.
8. Compute context budget class.
9. Emit the context pack plus a retrieval manifest.
10. If the pack exceeds budget, split the task or require a pre-discovery slice
    instead of pasting more history.

## Retrieval Manifest

Every assembled context pack should have a retrieval manifest:

```yaml
context_pack_id:
task_id:
assembled_at:
assembled_by:
target_conversation:
budget_class:
included_slices:
  - slice_type:
    index_family:
    source_paths:
    status:
    reason_included:
excluded_records:
  - source_path:
    status:
    reason_excluded:
stale_risk:
  stale_context_found:
  acknowledgement_required:
  blocking_delta_ids:
```

The manifest lets Verification review why a conversation received specific
context and why other material was excluded.

## Budget Classes

Use the V1 context-pack size guidance as hard design input:

| Class | Size | Action |
|---|---|---|
| `compact` | under 8k chars | preferred |
| `standard` | 8k-14k chars | allowed for normal complex work |
| `large_justified` | 14k-22k chars | allowed only with explicit reason |
| `oversized` | over 22k chars | fail; split into smaller slices |

Budget pressure should change task topology before it bloats context. If a PX4
parameter task needs literature review, log audit, estimator design, simulation
mapping, and verification, those should become scoped conversations with
different slices, not one overloaded pack.

## Stale And Rejected Material Filter

The assembler must not revive old mistakes. It must:

- exclude superseded context packs unless cited as history;
- include rejected assumptions when the target worker is likely to repeat them;
- block dispatch when a required acknowledgement is missing;
- distinguish `design_only` evidence from implemented proof;
- distinguish manual visual review from planning truth;
- distinguish offline demo evidence from MWORKS/UE/MCP evidence;
- keep gated automation as forbidden until separately approved.

## Context Fit Checks

Before dispatch, the context pack should pass:

| Check | Question |
|---|---|
| `goal_fit` | can the worker restate the canonical task goal and local objective? |
| `scope_fit` | are read/write/tool/worktree boundaries explicit? |
| `evidence_fit` | are claims linked to evidence, design docs, or unknown status? |
| `stale_filter_fit` | are superseded/rejected assumptions handled? |
| `budget_fit` | is the pack compact enough for reliable reasoning? |
| `review_fit` | is result path, review owner, and close condition explicit? |
| `safety_fit` | are forbidden actions and manual gates explicit? |

If any high-risk check fails, Dispatch sends an intake-repair or context-refresh
packet instead of starting work.

## Example: PX4 Parameter Identification

Required slices:

- `goal_slice`: identify which parameters can and cannot be derived;
- `product_scope_slice`: no overclaim that one log can solve all simulator
  parameters;
- `evidence_slice`: identifiability matrix template and evidence-label rules;
- `tool_capability_slice`: MWORKS/MCP health only if simulation tuning starts;
- `safety_slice`: license/manual blocker rules;
- `closeout_slice`: result packet must separate observed, estimated, assumed,
  calibrated, non-identifiable, and needs-experiment parameters.

Rejected assumptions to include:

- "all parameters can be identified from one PX4 log";
- "offline fit is MWORKS evidence";
- "simulation tuning can start before data sufficiency and tool health gates".

## Example: UE Scene Truth

Required slices:

- `goal_slice`: scene truth and planning readiness, not visual rendering only;
- `tool_capability_slice`: UE/MCP/Fab capability card;
- `evidence_slice`: scene truth artifact manifest;
- `worktree_git_index`: large asset and generated-output policy;
- `safety_slice`: manual Fab import, GUI, license, and external path gates;
- `closeout_slice`: planning readiness requires collision/navmesh/occupancy/SDF
  or equivalent truth artifacts.

Rejected assumptions to include:

- "rendered map means planning truth exists";
- "manual import can be omitted from the manifest";
- "large asset changes can be staged broadly".

## Future Implementation Slice

Add a later implementation item:

```text
COAGENT-IMPL-NEXT-21: Context Index And Assembly Checker
```

Scope:

- define a retrieval manifest schema;
- add fixtures for compact, oversized, stale, missing-review, and missing
  rejected-assumption cases;
- check that context packs cite source paths and statuses;
- check that high-risk tasks include stale/rejected-assumption filters;
- do not implement vector search, automatic conversation creation, or runtime
  dispatch.

Acceptance:

- valid compact pack passes;
- oversized pack fails with split recommendation;
- stale context without acknowledgement fails;
- high-risk PX4/UE packs fail if rejected assumptions are absent;
- no private Codex SQLite/JSONL, credentials, account cache, or raw transcript
  content is included in context output.

## Open Questions

- What exact context size gives best model performance for each task type is
  unknown. Use the budget classes until measured.
- Whether retrieval should later use lexical indexes, embeddings, SQLite, or
  plain manifests is an implementation decision.
- Context assembly should be measured by downstream result quality, not by the
  number of files cited.
