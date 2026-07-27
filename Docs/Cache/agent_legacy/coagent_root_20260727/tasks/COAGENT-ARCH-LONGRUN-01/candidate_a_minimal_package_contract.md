# COAGENT-ARCH-LONGRUN-01 Candidate A Minimal Package Contract

Date: 2026-05-30
Status: design contract for Candidate A fixture generation

## Purpose

Candidate A has a proof-package design, fixture specification, validator
execution design, and dependency graph. The remaining gap is the exact minimal
file contract a future generator or human should produce before validation.
This document defines the smallest complete Candidate A package, field by
field, so later implementation is deterministic.

This is design-only. It does not create proof-package files, run validators,
dispatch conversations, call tools, create worktrees, stage Git, or change
runtime schemas.

## Core Rule

```text
Candidate A proves coordination mechanics, not product work
```

The package must contain only architecture packet-chain material: task charter,
curated context, handoffs, workflow graph, result or blocker packet placeholders,
review, trace evaluation, context delta, and closeout. It must not include
UE, MWORKS, Fab, Git merge, notification, automatic conversation creation, or
worktree creation nodes.

## Canonical Package Root

Future proof or fixture packages should use:

```text
Results/coagent_proofs/COAGENT-PROOF-CANDIDATE-A/
```

Fixture packages may use:

```text
CoAgent/tests/fixtures/proof_packages/candidate_a/<fixture-name>/
```

All paths inside the contract are relative to the package root unless stated
otherwise.

## Minimum Directory Layout

```text
task_charter.yaml
context_pack.md
workflow_graph.yaml
handoffs/
  context_memory.yaml
  verification.yaml
  knowledge_secretary.yaml
packets/
  context_result.txt
  knowledge_result.txt
  context_delta.yaml
blockers/
  .gitkeep-or-empty
reviews/
  verification_review.yaml
  trace_eval.yaml
validator_reports/
  .gitkeep-or-empty
closeout.md
```

`blockers/` and `validator_reports/` may be empty in a valid preflight package,
but the directories should exist so post-dispatch closeout has known locations.

## Shared Constants

The package should use these values exactly unless the design contract is
versioned:

```yaml
task_id: COAGENT-PROOF-CANDIDATE-A
candidate_id: candidate_a_packet_chain
task_class: architecture_packet_chain_proof
canonical_task_goal: >
  Prove that CoAgent can coordinate a minimal multi-conversation architecture
  packet chain using curated context, handoff records, result or blocker
  packets, review, trace evaluation, context delta, and closeout without
  product-tool execution or gated automation.
review_owner: VerificationAgent
dispatch_owner: DispatchAgent
close_owner: MainAgent
```

The canonical goal must be identical in `task_charter.yaml`,
`workflow_graph.yaml`, and all handoff files. The validator should compare the
normalized text and reject semantic narrowing or expansion.

## `task_charter.yaml`

Required fields:

```yaml
task_id: COAGENT-PROOF-CANDIDATE-A
candidate_id: candidate_a_packet_chain
task_class: architecture_packet_chain_proof
canonical_task_goal: <shared constant>
owner: DispatchAgent
review_owner: VerificationAgent
close_owner: MainAgent
risk_level: medium
context_pack_path: context_pack.md
workflow_graph_path: workflow_graph.yaml
required_handoffs:
  - handoffs/context_memory.yaml
  - handoffs/verification.yaml
  - handoffs/knowledge_secretary.yaml
required_outputs:
  - packets/context_result.txt
  - packets/knowledge_result.txt
  - packets/context_delta.yaml
  - reviews/verification_review.yaml
  - reviews/trace_eval.yaml
  - closeout.md
forbidden_actions:
  - UE_MCP_or_GUI_execution
  - MWORKS_or_Sysplorer_execution
  - Fab_or_Epic_account_access
  - Git_stage_commit_push_or_worktree_creation
  - automatic_conversation_creation
  - app_server_transport
  - email_or_desktop_notification
  - external_path_write
done_conditions:
  - required_handoffs_validate
  - at_least_two_non_main_result_or_blocker_packets_exist
  - context_delta_exists
  - verification_review_terminal
  - trace_eval_records_missing_instrumentation_or_metrics
  - closeout_lists_proven_failed_gated_next_work
```

Reject if forbidden actions are absent. Candidate A is safe only because its
negative scope is explicit.

## `context_pack.md`

Required sections:

```text
# Context Pack
Task ID
Canonical Goal
Relevant Design Sources
Required Packet Contract
Required Context Rules
Required Review Rules
Forbidden Actions
Known Risks
Expected Outputs
Stop Conditions
Excluded Material
```

Rules:

- cite source files by project-local path;
- include `result_packet_contract_hardening.md`;
- include `context_lifecycle_schema.md` or `context_delta_checker_design.md`;
- include `candidate_a_packet_chain_blueprint.md`;
- exclude raw full transcript;
- exclude private Codex DB paths, credentials, account caches, and unrelated
  project history;
- include at least one rejected assumption:
  `more conversations do not prove better coordination`.

## `workflow_graph.yaml`

Required graph shape:

```yaml
workflow_id: COAGENT-PROOF-CANDIDATE-A-WF
task_id: COAGENT-PROOF-CANDIDATE-A
candidate_id: candidate_a_packet_chain
canonical_task_goal: <shared constant>
created_by: DispatchAgent
nodes:
  - node_id: charter
    node_type: artifact
    owner: DispatchAgent
    objective: define canonical proof package
    input_packets: []
    output_packets:
      - task_charter.yaml
    state: completed
  - node_id: context_memory_review
    node_type: agent
    owner: ContextMemoryAgent
    objective: review context sufficiency and produce context result
    input_packets:
      - context_pack.md
      - handoffs/context_memory.yaml
    output_packets:
      - packets/context_result.txt
      - packets/context_delta.yaml
    state: pending
  - node_id: verification_review
    node_type: review
    owner: VerificationAgent
    objective: review packet chain and evidence quality
    input_packets:
      - context_pack.md
      - packets/context_result.txt
    output_packets:
      - reviews/verification_review.yaml
      - reviews/trace_eval.yaml
    state: pending
  - node_id: knowledge_promotion
    node_type: agent
    owner: KnowledgeSecretaryAgent
    objective: identify promotion candidate or reject promotion
    input_packets:
      - context_pack.md
      - packets/context_delta.yaml
    output_packets:
      - packets/knowledge_result.txt
    state: pending
  - node_id: closeout
    node_type: artifact
    owner: MainAgent
    objective: summarize proven mechanism, failures, gates, and next slice
    input_packets:
      - packets/context_result.txt
      - packets/knowledge_result.txt
      - packets/context_delta.yaml
      - reviews/verification_review.yaml
      - reviews/trace_eval.yaml
    output_packets:
      - closeout.md
    state: pending
edges:
  - from: charter
    to: context_memory_review
    edge_type: depends_on
  - from: context_memory_review
    to: verification_review
    edge_type: handoff
  - from: context_memory_review
    to: knowledge_promotion
    edge_type: handoff
  - from: verification_review
    to: closeout
    edge_type: review_gate
  - from: knowledge_promotion
    to: closeout
    edge_type: depends_on
review:
  required_review_nodes:
    - verification_review
  final_review_owner: VerificationAgent
close_condition:
  terminal_nodes:
    - closeout
  required_artifacts:
    - closeout.md
  required_decision: accepted_or_needs_review
```

Reject if a node type is `tool`, `merge`, or `human_interrupt` without explicit
user approval for a different proof. Candidate A should not test those paths.

## Handoff Files

All handoff files must share this shape:

```yaml
handoff_id: <unique id>
task_id: COAGENT-PROOF-CANDIDATE-A
candidate_id: candidate_a_packet_chain
canonical_task_goal: <shared constant>
mode: department_lane
from_owner: DispatchAgent
to_owner: <ContextMemoryAgent|VerificationAgent|KnowledgeSecretaryAgent>
authority_transfer: scoped_execution
context_pack_path: context_pack.md
expected_result_packet_path: <packet or review path>
input_filter:
  include:
    - canonical_goal
    - context_pack
    - expected_output_path
    - forbidden_actions
    - stop_condition
  exclude:
    - raw_transcript
    - secrets
    - unrelated_project_history
review_gate: VerificationAgent
return_path: DispatchAgent
cancellation_or_resume_rule: >
  Stop with a valid blocker packet if required context, result path, or
  review evidence is missing.
acceptance:
  reviewer: VerificationAgent
  terminal_states:
    - completed
    - review_required
    - blocked
    - rejected
forbidden_actions:
  - product_tool_execution
  - git_stage_commit_push
  - notification_send
```

Expected output paths:

- `handoffs/context_memory.yaml` -> `packets/context_result.txt`
- `handoffs/verification.yaml` -> `reviews/verification_review.yaml`
- `handoffs/knowledge_secretary.yaml` -> `packets/knowledge_result.txt`

## Result Packet Placeholders

In preflight fixtures, result packet files may be absent only if the mode is
explicitly `preflight`. In post-dispatch fixtures, each required result must be
present or have a matching blocker under `blockers/`.

`packets/context_result.txt` and `packets/knowledge_result.txt` must follow the
flat result packet contract from `result_packet_contract_hardening.md`.

Minimum flat fields:

```text
[MoSim Result Packet]
task_id: COAGENT-PROOF-CANDIDATE-A
status: completed
canonical_status: completed
task_class: architecture_packet_chain_proof
owner: <owner>
role: <role>
summary: <single paragraph>
read_scope: [...]
write_scope: [...]
files_changed: []
commands_run: []
evidence: [...]
risks: [...]
blockers: []
review_status: <not_required|needs_review>
acceptance_state: <met|partially_met|unknown>
continue_or_stop: continue
next_recommended_action: <action>
events: []
```

Reject nested YAML result packets until the result router or validator version
explicitly supports them.

## `packets/context_delta.yaml`

Required fields:

```yaml
context_delta_id: CTXD-CANDIDATE-A-001
task_id: COAGENT-PROOF-CANDIDATE-A
source_result_packet: packets/context_result.txt
created_by: ContextMemoryAgent
created_at: <ISO timestamp or fixture timestamp>
context_pack_id: candidate_a_context_pack
context_pack_version_or_hash: <hash or fixture value>
change_type: lesson
summary: Candidate A requires explicit result/blocker packets and cannot rely on raw chat.
supersedes:
  - assumption: raw chat can be used as durable cross-conversation state
affected_slices:
  - verification_review
  - knowledge_promotion
affected_departments:
  - VerificationAgent
  - KnowledgeSecretaryAgent
acknowledgement_required: false
acknowledgement_state: not_required
pause_until_refresh: false
reviewer: VerificationAgent
resume_condition: no acknowledgement required for this fixture delta
evidence_paths:
  - packets/context_result.txt
```

## `reviews/verification_review.yaml`

Required fields:

```yaml
task_id: COAGENT-PROOF-CANDIDATE-A
review_owner: VerificationAgent
review_status: accepted
acceptance_state: met
canonical_goal_preserved: true
required_packets_present: true
context_delta_present: true
forbidden_actions_detected: false
missing_dependencies: []
findings: []
risks: []
next_recommended_action: close_candidate_a_or_run_next_gate
```

If validators are missing, `missing_dependencies` must list them rather than
pretending the proof is fully automated.

## `reviews/trace_eval.yaml`

Required fields:

```yaml
task_id: COAGENT-PROOF-CANDIDATE-A
metrics:
  result_packet_count:
    value: 2
    classification: measured
  blocker_packet_count:
    value: 0
    classification: measured
  context_delta_count:
    value: 1
    classification: measured
  unsupported_claim_count:
    value: 0
    classification: measured
  missing_dependency_count:
    value: 0
    classification: measured
needs_instrumentation: []
```

Metrics may be `needs_instrumentation`, but the reason must be explicit.

## `closeout.md`

Required sections:

```text
# Candidate A Closeout
Task ID
Canonical Goal
What Was Proven
What Was Not Proven
Packets And Evidence
Context Delta
Review Decision
Missing Dependencies
Gated Follow-On Work
Recommended Next Approval
```

Closeout must not claim:

- unattended multi-conversation execution is proven;
- product tools are reliable;
- PX4/UE/Git/auth proofs passed;
- validators are implemented if they were manually emulated;
- automatic dispatch, worktree creation, notification, or app-server transport
  is enabled.

## Preflight Validity

A package is preflight-valid when:

- required files exist;
- shared constants match;
- all paths are package-local or approved `Results/` paths;
- handoffs have expected result paths;
- workflow has review and closeout nodes;
- context pack is curated;
- forbidden actions are explicit;
- no product/tool/Git/notification nodes exist.

## Post-Dispatch Validity

A package is post-dispatch-valid when:

- every required worker output exists or has a valid blocker;
- result packets validate under the flat packet contract;
- context delta exists and is valid;
- verification review is terminal;
- trace evaluation exists;
- closeout maps proven, failed, gated, and next work;
- missing validators are recorded as dependencies, not hidden.

## Design Decision

`candidate_a_minimal_package_contract.md` is the source of truth for future
Candidate A fixture generation. `candidate_a_fixture_spec.md` defines which
fixtures must pass or fail; this contract defines the exact minimal package
shape those fixtures should instantiate.
