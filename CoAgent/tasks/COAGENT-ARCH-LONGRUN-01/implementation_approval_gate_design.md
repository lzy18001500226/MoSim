# COAGENT-ARCH-LONGRUN-01 Implementation Approval Gate Design

Date: 2026-05-30
Status: design contract for `COAGENT-IMPL-NEXT-31`

## Purpose

Define the read-only gate that decides whether a proposed CoAgent
implementation slice has explicit approval, valid phase entry evidence, safe
scope, and realistic exit evidence before any runtime, transport, schema,
tool, MCP, Git, scheduler, notification, or automation work starts.

This document extends:

- `implementation_sequence_and_release_plan.md`
- `post_design_implementation_backlog.md`
- `validator_shared_envelope_design.md`
- `goal_alignment_checker_design.md`
- `runbook_readiness_checker_design.md`
- `human_review_intervention_ux_design.md`

It is design-only. It does not approve implementation, mutate runtime state,
create tasks, dispatch conversations, create worktrees, stage Git, call
MCP/tools, send notifications, or edit Codex state.

## Core Rule

```text
backlog presence is not approval
```

An implementation slice may start only when the user or PMO has approved that
specific slice, the phase is allowed, the entry evidence is current, the scope
is bounded, and the forbidden actions match the project safety boundary.

## Approval Packet

The future checker should validate an approval packet:

```yaml
implementation_approval:
  approval_id: COAGENT-APPROVAL-YYYYMMDD-NN
  backlog_id: COAGENT-IMPL-NEXT-XX
  phase: R1 | R2 | R3 | R4 | R5 | R6 | R7 | R8
  user_or_pmo_approval:
    source: user_message | decision_record | review_packet
    text_excerpt: <explicit approval>
    timestamp: <timestamp if available>
  objective: <implementation outcome>
  non_goals:
    - <what this slice must not claim>
  scope:
    read_paths:
      - <project path>
    write_paths:
      - <project path>
    forbidden_actions:
      - <forbidden action>
  entry_evidence:
    - path: <file or report path>
      claim: <what it proves>
  dependency_reports:
    - path: <shared envelope report path>
      required_for: <why needed>
  expected_exit_evidence:
    - <validator report, fixture result, proof closeout, or blocker packet>
  rollback_or_stop_rule: <exact stop condition>
  review_owner: VerificationAgent | SafetyComplianceAgent | MainAgent
  integration_owner: <owner when mutable files are changed>
  claim_boundaries:
    - <what success does not prove>
```

## Required Checks

### Explicit Approval

Require approval that names:

- backlog id or exact implementation slice;
- phase or risk class;
- allowed scope;
- whether manual-risk execution is accepted.

Reject:

- "continue", "looks good", or broad design acceptance as implementation
  approval;
- phase-ladder order as approval;
- existence of a backlog item as approval;
- inferred approval from previous unrelated tasks.

### Phase Entry

Check that the requested phase is allowed by
`implementation_sequence_and_release_plan.md`.

Reject when:

- R2 starts before R1 shared envelope and goal-alignment basics are approved or
  explicitly waived;
- R3 starts before packet/blocker atoms are ready or waived;
- R4 starts without Candidate A preflight or explicit manual rehearsal
  approval;
- R6/R7 product work starts without route-specific proof gates;
- R8 automation starts before manual learning/retrospective loops have proof.

### Scope Boundary

Check:

- all paths are inside the project unless an explicit approved exception is
  recorded;
- write paths are narrow enough for the slice;
- forbidden actions include relevant gated operations;
- secrets, credentials, account caches, provider configs, and private Codex
  state are excluded unless the user explicitly approved an infrastructure
  repair.

Reject broad write scopes such as entire repository, all `CoAgent/`, all
`Scripts/`, or arbitrary external paths unless the slice is a documented
refactor with separate Git and safety gates.

### Dependency Evidence

Check that the packet cites the required reports or explains accepted gaps:

- shared validator envelope for any checker implementation;
- goal alignment for any task/goal/closeout implementation;
- evidence label doctor for any evidence claim;
- blocker validator for resumable stops or human review;
- tool capability health gate for MCP/UE/Fab/MWORKS/Codex/Git route work;
- runbook readiness checker before serious task package execution;
- worktree/Git checks before multi-worktree or Git-heavy implementation.

Missing dependencies should report `needs_dependency` for planning and
`fail_before_dispatch` or `blocked` before live execution.

### Exit Evidence

Require testable exit evidence:

- fixture pass/fail results;
- validator report;
- proof closeout;
- blocker packet;
- review packet;
- targeted command output;
- manual review record when the slice is manual.

Reject "code exists" or "docs updated" as sufficient exit evidence for runtime,
transport, schema, tool, MCP, Git, notification, scheduler, or product claims.

### Claim Boundaries

Every approval must state what success does not prove.

Examples:

- shared envelope implementation does not prove domain validators;
- result packet validator does not prove live dispatch;
- visibility repair does not prove Codex root-cause reliability;
- UE capability card does not prove planning truth;
- Git inventory does not approve staging or commit;
- manual review does not prove automation.

## Stable Finding Codes

| Code | Meaning |
|---|---|
| `APPROVAL_PACKET_MISSING` | approval packet is missing |
| `APPROVAL_EXPLICIT_TEXT_MISSING` | no explicit user/PMO approval |
| `APPROVAL_BACKLOG_ID_MISSING` | backlog id or slice id missing |
| `APPROVAL_PHASE_INVALID` | phase missing or not in R1-R8 |
| `APPROVAL_PHASE_DEPENDENCY_MISSING` | earlier required phase evidence missing |
| `APPROVAL_SCOPE_TOO_BROAD` | read/write scope is too broad |
| `APPROVAL_EXTERNAL_PATH_UNAPPROVED` | external path without approved exception |
| `APPROVAL_FORBIDDEN_ACTION_MISSING` | gated operation not forbidden or approved |
| `APPROVAL_SECRET_RISK` | credentials, account cache, provider config, or private state risk |
| `APPROVAL_DEPENDENCY_REPORT_MISSING` | required validator/proof report missing |
| `APPROVAL_EXIT_EVIDENCE_WEAK` | exit evidence is not testable |
| `APPROVAL_CLAIM_BOUNDARY_MISSING` | success boundary missing |
| `APPROVAL_BACKLOG_AS_AUTHORITY` | backlog or phase ladder used as approval |
| `APPROVAL_MANUAL_RISK_UNRECORDED` | manual-risk route lacks explicit acceptance |
| `APPROVAL_GIT_OR_TOOL_OVERREACH` | Git/tool/MCP/product work exceeds approved route |

## Fixture Matrix

Positive fixtures:

| Fixture | Expected |
|---|---|
| R1 shared validator envelope approval with narrow write scope and fixture exit evidence | `pass` |
| R2 result packet validator approval with dependency on shared envelope | `pass` |
| R4 manual Candidate A rehearsal with explicit missing-validator risk acceptance | `pass_with_warnings` |
| R6 UE proof validator approval with tool capability and evidence-label dependencies | `pass_with_warnings` or `needs_dependency` by reports |

Negative fixtures:

| Fixture | Expected Codes |
|---|---|
| backlog item exists but no approval packet | `APPROVAL_PACKET_MISSING` |
| "continue" used as implementation approval | `APPROVAL_EXPLICIT_TEXT_MISSING` |
| R4 starts without R1-R3 evidence or waiver | `APPROVAL_PHASE_DEPENDENCY_MISSING` |
| write scope is all `CoAgent/` for a small validator | `APPROVAL_SCOPE_TOO_BROAD` |
| external Codex config edit without infrastructure exception | `APPROVAL_EXTERNAL_PATH_UNAPPROVED`, `APPROVAL_SECRET_RISK` |
| approval omits forbidden Git/MCP/tool actions | `APPROVAL_FORBIDDEN_ACTION_MISSING` |
| exit evidence says only "implementation complete" | `APPROVAL_EXIT_EVIDENCE_WEAK` |
| approval claims shared envelope proves product tool readiness | `APPROVAL_CLAIM_BOUNDARY_MISSING` or `APPROVAL_GIT_OR_TOOL_OVERREACH` |

## Output

The checker should emit the shared validator envelope:

```json
{
  "schema_version": "coagent.validator_report.v1",
  "validator": "implementation_approval_gate",
  "task_id": "COAGENT-IMPL-NEXT-00",
  "mode": "preflight",
  "decision": "fail_before_dispatch",
  "ok": false,
  "finding_codes": ["APPROVAL_EXPLICIT_TEXT_MISSING"],
  "findings": [
    {
      "code": "APPROVAL_EXPLICIT_TEXT_MISSING",
      "severity": "error",
      "path": "implementation_approval.yaml",
      "message": "approval packet cites design acceptance but not explicit approval for this implementation slice",
      "remediation": "obtain or cite explicit user/PMO approval for COAGENT-IMPL-NEXT-00"
    }
  ],
  "dependency_reports": [],
  "evidence_paths": [
    "CoAgent/tasks/COAGENT-ARCH-LONGRUN-01/implementation_sequence_and_release_plan.md"
  ],
  "side_effects": {
    "declared": ["read_project_files", "write_validator_report"],
    "forbidden": ["runtime_mutation", "live_dispatch", "mcp_or_tool_call", "git_mutation", "goal_mutation"]
  },
  "claim_boundaries": [
    {
      "claim": "implementation slice is approved to start",
      "supported": false,
      "limitations": "gate does not implement the slice"
    }
  ],
  "next_action": "obtain explicit approval packet before implementation"
}
```

## Implementation Boundary

The first implementation should be read-only and fixture-backed. It may read
project task/backlog/approval files and write reports under
`Results/coagent_validators/`. It must not create, mutate, complete, or block
Codex goals; dispatch conversations; create conversations; edit runtime state;
call MCP/tools; create worktrees; stage, commit, or push Git changes; send
notifications; edit Codex state; inspect credentials or account caches; or
rewrite task documents automatically.
