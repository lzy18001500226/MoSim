# CoAgent Docs

Legacy note, 2026-06-24: MoSim has moved back to single-thread execution.
This tree is historical CoAgent / AgentOS reference material, not active
startup or operating instructions. Do not add new long-form operating/design
policy here unless the user explicitly asks for legacy CoAgent cleanup or
audit.

This folder is the human-readable CoAgent map. Runtime code lives in sibling
module folders such as `runtime/`, `dispatch/`, `context/`, and `transport/`.

## Reading Order

For a new conversation, read in this order:

1. `../STATUS.md`
2. `operating/agent_os_operating_model.md`
3. `operating/README.md`
4. `architecture/coagent_architecture_issue_register.md`
5. `architecture/coagent_problem_driven_operating_model.md`
6. `architecture/coagent_department_capability_model.md`
7. `architecture/coagent_conversation_mapping.md`
8. `architecture/coagent_concrete_agent_design.md`
9. `architecture/coagent_vendor_gap_review_2026_05_29.md`
10. `architecture/coagent_dynamic_agent_codex_feature_gap_2026_05_29.md`
11. `architecture/coagent_dynamic_task_team_v2_design.md`
12. `architecture/coagent_minimal_closed_loop_protocol.md`
13. `architecture/coagent_solution_synthesis.md`
14. `architecture/coagent_user_intervention_ux.md`
15. `architecture/COMPONENT_MAP.md`
16. `architecture/coagent_task_team_architecture.md`
17. `decisions/coagent_post_approval_backlog.md`

## Folders

| Folder | Use |
|---|---|
| `architecture/` | Current design model, architecture issues, task/team/context/worktree protocols |
| `operating/` | Portable operating model, organization, patrol/recovery, orchestration, tooling governance, and migration map |
| `decisions/` | Approval records, review briefs, readiness audits, backlog, completion audits |
| `research/` | Learning strategy, external project index, URL seeds, synthesis notes |
| `status/` | Migration and status snapshots |

## Key Files

| File | Purpose |
|---|---|
| `architecture/ARCHITECTURE.md` | Layered CoAgent architecture and runtime boundaries |
| `operating/agent_os_operating_model.md` | Portable CoAgent agent-OS entrypoint and source map |
| `operating/MIGRATION_MAP.md` | Map from former MoSim workflow paths to CoAgent canonical operating docs |
| `architecture/COMPONENT_MAP.md` | Map from concepts to files, modules, and current gaps |
| `architecture/coagent_architecture_issue_register.md` | Open design questions that must not be treated as solved |
| `architecture/coagent_problem_driven_operating_model.md` | Problem-driven matrix from PX4 parameter identification and UE/navigation simulation workflows |
| `architecture/coagent_department_capability_model.md` | Portable CoAgent department capability model and conversation mapping |
| `architecture/coagent_conversation_mapping.md` | Mapping from 20 capability departments to required, conditional, hosted, and task-scoped conversations |
| `architecture/coagent_concrete_agent_design.md` | Concrete profiles for the 11 permanent agents, conditional agents, and task-scoped agents |
| `architecture/coagent_vendor_gap_review_2026_05_29.md` | Gap review from model-vendor and framework patterns back into the current 11-agent design |
| `architecture/coagent_dynamic_agent_codex_feature_gap_2026_05_29.md` | Dynamic agent-team and Codex feature-use gap review covering Claude agent teams, Kimi Agent Swarm, Codex thread/worktree/goal/review/hooks/plugins capabilities |
| `architecture/coagent_dynamic_task_team_v2_design.md` | Dynamic Task Team V2 design: task intake, shared board, mailbox, context shards, fork/worktree policy, review/integration, human intervention, and metrics |
| `architecture/coagent_minimal_closed_loop_protocol.md` | File-level manual-review proof protocol for the first full CoAgent architecture loop |
| `architecture/coagent_solution_synthesis.md` | Problem-to-solution synthesis, topology selector, context/communication/worktree/human-intervention baseline |
| `architecture/coagent_user_intervention_ux.md` | Manual intervention, blocker notification, email-ready packet, and resume UX design |
| `architecture/coagent_task_team_architecture.md` | Task-first multi-conversation team model |
| `architecture/coagent_vendor_pattern_mapping.md` | Vendor/framework pattern mapping into CoAgent objects |
| `decisions/coagent_design_decision_record.md` | Durable design approval record |
| `decisions/coagent_post_approval_backlog.md` | Sequenced approved/backlogged design and implementation tasks |
| `decisions/coagent_miniloop_01_human_review.md` | Human review packet for the first file-level closed-loop architecture proof |
| `research/LEARNING_STRATEGY.md` | How to audit and absorb external projects |
| `research/REFERENCE_PROJECT_INDEX.md` | Stable index for external projects under `References/` |
| `status/codex_cli_entrypoint.md` | Verified WSL Codex CLI entrypoint and Node 20 launch command |
| `status/MIGRATION_STATUS.md` | What CoAgent has absorbed and what remains |

## Rule

Do not put every new CoAgent note at the root. Place it by purpose:

- design claim or architecture model -> `architecture/`
- reusable operating workflow or agent-OS rule -> `operating/`
- user decision, gate, backlog, approval, closeout -> `decisions/`
- external source study or source index -> `research/`
- migration/status snapshot -> `status/`
- structured source audit -> `../learning/audits/`
