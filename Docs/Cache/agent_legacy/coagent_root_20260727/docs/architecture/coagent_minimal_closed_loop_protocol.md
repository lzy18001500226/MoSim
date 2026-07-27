# CoAgent Minimal Closed Loop Protocol

Date: 2026-05-29

Status: protocol for manual-review proof. This document does not authorize
automatic Codex conversation creation, app-server transport, automatic
worktree creation, email, hooks, plugins, MCP expansion, or unattended
execution.

## Purpose

This protocol defines the smallest architecture-level closed loop that proves
CoAgent can handle one task without relying on chat memory.

The loop is:

```text
PMO intake
  -> Dispatch task charter
  -> shared task board
  -> team mailbox
  -> context pack
  -> scoped conversation packet
  -> result packet
  -> review packet
  -> context delta
  -> integration plan
  -> trace evaluation
  -> closeout summary
  -> retrospective record
  -> human review
```

## Scope

`COAGENT-MINILOOP-01` is file-level only.

Allowed:

- create templates for Dynamic Task Team V2 objects;
- create one sample task evidence bundle under `Results/coagent_miniloop/`;
- validate that required packets exist and reference each other;
- produce a human-review decision packet.

Forbidden:

- creating real Codex App or VSCode conversations;
- using Codex app-server transport;
- creating Git worktrees;
- changing runtime task-state schema;
- adding permanent departments;
- sending email or desktop notifications;
- changing hooks or MCP tools.

## Required Artifacts

One minimal closed-loop bundle must include:

| Artifact | Required path |
|---|---|
| Task charter | `task_charter.yaml` |
| Shared task board | `shared_task_board.yaml` |
| Team mailbox | `team_mailbox.yaml` |
| Context pack | `context_pack.yaml` |
| Scoped conversation packet | `scoped_conversation_packet.yaml` |
| Result packet | `result_packet.json` |
| Review packet | `review_packet.yaml` |
| Context delta | `context_delta.yaml` |
| Worktree binding | `worktree_binding.yaml` |
| Integration plan | `integration_plan.yaml` |
| Team trace eval | `team_trace_eval.yaml` |
| Workflow graph | `workflow_graph.yaml` |
| Closeout summary | `closeout_summary.md` |
| Retrospective record | `retrospective.md` |

## Acceptance

The loop is accepted when:

1. every artifact exists;
2. every artifact uses the same `task_id`;
3. the board reaches `completed`;
4. the mailbox has no open required response;
5. the result packet is terminal and includes evidence;
6. the review packet allows closeout;
7. the integration plan names accepted artifacts and checks;
8. the trace eval records process metrics;
9. the closeout summary states what was proven and what remains unimplemented;
10. the retrospective record captures lessons, remaining risks, and next
    process improvement;
11. the human-review packet is ready for user decision.

## Human Review Point

After the static check passes, PMO must ask the user to review:

- whether the artifact chain matches the intended operating model;
- whether this file-level proof is enough before real multi-conversation proof;
- whether the next task should be real visible conversation delivery, runtime
  support for V2 packets, or more design refinement.
