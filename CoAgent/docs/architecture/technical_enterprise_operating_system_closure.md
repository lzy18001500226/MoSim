# Technical Enterprise Operating System Closure

Date: 2026-05-28

Status: enterprise-management baseline closed. This is not approval for new
runtime, transport, automation, or department-expansion implementation.

## Closure Decision

The enterprise-management design is now sufficient to stop open-ended
management discussion and use it as the baseline for later CoAgent agent-system
design.

This closure answers how MoSim should manage complex technical work:

- how a user request becomes a controlled task,
- who owns the integrated outcome,
- when work should stop or escalate,
- what evidence is required before acceptance,
- how departments cooperate without hiding authority,
- how failures become process improvements instead of repeated mistakes.

It does not answer the lower-level implementation questions of conversation
creation, Codex App synchronization, context-pack generation, transport,
scheduling, or automated worker lifecycle. Those belong to the next Agent
design layer.

## Frozen Management Decisions

1. Work is task-first, not department-first.

   A user request must first be framed as an objective with definition of done,
   non-goals, evidence, risks, appetite, and stop conditions. Department routing
   comes after task framing.

2. One task has one accountable owner.

   Departments may support the work, but only one owner is accountable for the
   integrated result at a time. Support departments return evidence, blockers,
   or review findings; they do not silently take over the canonical goal.

3. PMO/main and DispatchCenter are logically separate.

   PMO/main owns user alignment, priority, final integration, and user-facing
   decisions. DispatchCenter owns task tickets, owner assignment, state,
   routing, checkpoints, and result-packet intake. They may share one physical
   conversation early, but their responsibilities must stay separate.

4. Department count stays small by default.

   Permanent lanes are PMO/main, DispatchCenter, Engineering, Verification,
   Security, Documentation Secretary, and DevOps. Architecture review,
   technical research, incident review, and special testing are created only
   when the task justifies them.

   Update 2026-05-29: this was the historical startup baseline for the first
   implementation checkpoint. The portable capability-department model is now
   defined in
   `CoAgent/docs/architecture/coagent_department_capability_model.md`, which
   expands the capability map to 20 departments and separates department
   capability from visible conversation count.

5. Boundaries are dynamic at execution time, stable at accountability time.

   A task may pull in DevOps, Security, Verification, Documentation, or
   Architecture support as evidence demands. That does not change who owns the
   integrated outcome unless DispatchCenter records a goal or owner change.

6. Long or uncertain tasks need appetite and circuit breakers.

   A task that may consume significant time or context must define how much
   effort it is worth and what condition stops blind continuation.

7. Acceptance requires evidence.

   A task is not accepted because a chat says it is done. It needs the work
   product or decision, evidence path or reproducible command, known exclusions,
   residual risk, review state, and terminal or next-action state.

8. Durable state beats chat memory.

   Task tickets, status boards, decision records, result packets, evidence
   paths, and retrospectives are the system of record. Chat is an interface and
   discussion trace, not the authority for ownership, acceptance, or goal
   change.

9. Safety and release gates can stop work.

   Security blocks path, secret, license, account, destructive, and unsafe GUI
   boundaries. DevOps controls Git/release state. Verification can reject
   claims that lack reproducible evidence.

10. Retrospectives change the system.

    Repeated failures must update rules, skills, hooks, tests, workflows, or
    checklists. The purpose is to improve the operating system, not to preserve
    a perfect-looking process.

## Standard Management Flow

```text
user need
  -> PMO frames objective and acceptance
  -> DispatchCenter records task and owner
  -> accountable owner executes or requests support
  -> supporting departments return evidence or blockers
  -> Verification/Security/Docs/DevOps gates run when relevant
  -> PMO integrates result and reports to user
  -> Documentation records durable decisions
  -> retrospective updates the operating system when needed
```

## Department Contract

This table is the historical startup contract used for the first checkpoint.
For the current portable department-capability model, use
`CoAgent/docs/architecture/coagent_department_capability_model.md`.

| Lane | Owns | Must Not Own |
|---|---|---|
| PMO / main | user alignment, priority, final integrated answer, accepted direction | hidden long worker queues |
| DispatchCenter | task ticket, state board, owner assignment, routing, result intake | feature implementation or silent scope changes |
| Engineering | technical implementation, investigation, prototypes, integration | global priority or final acceptance |
| Verification | independent tests, reproducibility, evidence quality | writing the feature under test |
| Security | path, credential, license, destructive-action, account, GUI/MCP risk gates | product preference or general code quality |
| Documentation Secretary | user directives, decisions, durable records, docs consistency | global task board ownership |
| DevOps | Git, branch, ignore/LFS, commit/push/release hygiene | feature design or broad implementation |

## Task Intake Contract

Every durable task must classify itself as one of:

```text
simple_message
clear_task
complicated_task
complex_task
chaotic_incident
disordered_task
long_running_task
```

The class determines how much process is required. Clear work stays light.
Complex work starts with discovery. Chaotic work stabilizes first. Long-running
work receives a durable boundary, appetite, checkpoint plan, and recovery path.

## Management Acceptance Criteria

The enterprise-management layer is closed because the current docs answer these
questions with stable rules:

- What is the objective and definition of done?
- Who is accountable for the integrated outcome?
- Which department supports which part of the work?
- What evidence is required before acceptance?
- When should the system stop and escalate?
- Where is durable state recorded?
- How are Git, safety, verification, and documentation gates applied?
- How do repeated failures become process changes?
- When is a new department or long-running task conversation justified?
- What must not be solved by adding more agents?

## Source Documents

This closure consolidates the following source documents:

- `CoAgent/docs/architecture/technical_enterprise_operating_system.md`
- `CoAgent/docs/architecture/task_intake_and_governance.md`
- `CoAgent/docs/architecture/enterprise_to_agent_mapping.md`
- `CoAgent/docs/architecture/coagent_complexity_control.md`
- `Docs/Workflows/org_operating_model.md`
- `Docs/Workflows/agent_orchestration.md`

It also incorporates the two enterprise-management audit rounds:

- `CoAgent/learning/audits/2026-05-28_technical_enterprise_operating_system_round1.md`
- `CoAgent/learning/audits/2026-05-28_technical_enterprise_operating_system_round2_gap_analysis.md`

## Moved To Agent Design

The following topics are intentionally not closed here:

- how to create, name, repair, and retire visible Codex conversations,
- how to synchronize WSL/VSCode/Codex App state without corrupting sessions,
- how to construct compact context packs for a new task conversation,
- how to set project, task, conversation, and subagent goals in runtime state,
- how to transport task packets and result packets reliably,
- how to schedule recurring learning, Git, workflow, or health-review jobs,
- how to implement department-internal workers without hidden authority.

These are Agent-system design and implementation questions. They must inherit
this management baseline rather than reopen it by default.

## Next Gate

The next design step should be a CoAgent conversation, goal, and context
protocol that implements this management model with the smallest reliable
control plane.

Do not add new permanent departments, peer-to-peer worker communication,
unattended automation, or app-server transport as a shortcut. Add complexity
only when a real repeated failure demonstrates that the closed management model
cannot be executed with the current V1 controls.
