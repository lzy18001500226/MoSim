# CoAgent Conversation Protocol V1

Date: 2026-05-28

Status: design baseline for `COAGENT-DESIGN-08`.

## Purpose

This protocol defines how CoAgent uses conversations as work surfaces without
turning them into uncontrolled agent swarms.

## Approved Conversation Roles

The table below is the V1 protocol vocabulary and historical compatibility
layer. The current concrete 11-agent role design is defined in
`CoAgent/docs/architecture/coagent_concrete_agent_design.md`.

| Role | Lifetime | Primary Work | Must Not Do |
|---|---|---|---|
| `MainPMO` | project-long | user dialogue, priority, final integration | hidden long worker queues |
| `DispatchCenter` | project-long | task packets, state board, owner assignment, result intake | feature implementation |
| `Engineering` | project-long | implementation and technical investigation | final acceptance or Git release |
| `Verification` | project-long | independent evidence and reproducibility | write the feature under test |
| `Security` | project-long | path, secret, license, destructive-action, GUI/MCP gates | product preference decisions |
| `Documentation` | project-long | directive records, decisions, docs consistency | global task-state ownership |
| `DevOps` | project-long | Git hygiene, commits, releases, ignore/LFS | feature design |
| `DedicatedTask` | task-long | one high-context task under a parent department | create child durable agents without approval |
| `Subagent` | one-shot | bounded research, review, or execution slice | own durable state |

Existing user-facing thread labels remain governed by
`Docs/Workflows/org_operating_model.md`.

## Current Concrete Agent Profiles

The current dispatchable MoSim visible conversations are the user-confirmed
allowlist in `CoAgent/dispatch/department_threads.json`:

1. `MoSim｜主线 PMO`
2. `MoSim｜DevOps 发布`
3. `MoSim｜UE实验控制台与场景交互部`
4. `MoSim｜Sunray150资产与PBR审核部`
5. `MoSim｜MWORKS动力学与控制验证部`
6. `MoSim｜ROS2感知定位与规划运行部`
7. `MoSim｜微信网关运维部`
8. `MoSim｜Codex 环境迁移部`
9. `MoSim｜开源项目探针`
10. `MoSim｜CoAgent运维平台`
11. `MoSim｜开源项目学习部`
12. `MoSim｜Codex 上下文维护部`
13. `MoSim｜WechatCodex`

`MoSim｜WechatCodex` is a message path for WeChat-side inbound refresh, not a
gateway-operations owner. Testing, security, documentation-secretary, and
toolchain/MCP upkeep are task-local gates or CoAgent meta-maintenance duties
unless PMO explicitly creates a scoped visible thread for a high-impact task.

These agents are governed by:

```text
CoAgent/docs/architecture/coagent_department_capability_model.md
CoAgent/docs/architecture/coagent_conversation_mapping.md
CoAgent/docs/architecture/coagent_concrete_agent_design.md
CoAgent/protocol/templates/agent_profile.yaml
CoAgent/protocol/templates/task_scoped_agent_profile.yaml
```

If this protocol and older concrete-agent design artifacts conflict, use the
current allowlist registry and `Docs/Workflows/org_operating_model.md` for live
routing. Older design files may remain as historical architecture material, but
they do not make absent old thread IDs dispatchable.

## Creation Criteria

### Department Conversation

A permanent department conversation is allowed only when:

- the responsibility repeats across many tasks,
- the risk or state is high enough to justify separation,
- the role has a durable owner lane,
- DispatchCenter can route task packets to it,
- result packets can be imported back into project state.

### Dedicated Task Conversation

A dedicated task conversation is allowed only when:

- `task_id` exists,
- parent department exists,
- canonical task goal exists,
- context pack exists,
- stop condition exists,
- result-packet path exists,
- DispatchCenter records `conversation_linked`,
- at least one checkpoint is expected before terminal result.

### Short-Lived Subagent

A subagent is allowed when:

- the task is bounded,
- the output can be summarized into one result,
- no durable visible continuity is needed,
- the parent remains accountable,
- the subagent cannot mutate broad state unless explicitly scoped.

## Naming Rule

Visible permanent conversations use:

```text
MoSim｜<department name>
```

Dedicated task conversations use:

```text
MoSim｜专项｜<task name>
```

Conversation names are UI labels, not the source of truth. The source of truth
is the registry row or task ledger entry that links:

```text
thread_id
task_id
department
role
state
created_at
closed_at
result_packet
```

## Lifecycle

```text
planned
  -> linked
  -> working
  -> checkpointed
  -> result_received
  -> review_required or completed
  -> closed
```

Every lifecycle transition must be represented by an event or packet in project
state. A visible App/VSCode sidebar entry alone is not enough.

## Worktree Binding

A visible conversation may be bound to a Codex App worktree, but the binding is
not the authority source.

The registry or task ledger should record:

```text
thread_id
task_id
department
worktree_path
branch_or_base
write_scope
merge_owner
review_gate
close_condition
```

Use worktrees to isolate file changes and Git state. Do not use worktrees to
create independent goals, hidden authority, or untracked peer-to-peer work.

Recommended mapping:

| Conversation | Worktree Use |
|---|---|
| Main / PMO | normally no separate worktree; keeps integration view |
| DispatchCenter | normally no separate worktree; owns state and routing |
| Engineering | separate worktree for larger implementation streams |
| Verification | separate read-mostly worktree when reproducibility needs clean state |
| Security | separate read-mostly worktree when auditing high-risk diffs |
| Documentation | shared or small docs worktree depending conflict risk |
| DevOps | dedicated integration worktree for staged Git work |
| DedicatedTask | dedicated worktree when edits are substantial or long-running |

## Goal Inheritance

A conversation objective must be derived from the canonical task goal.

Allowed:

```text
Canonical Task Goal:
  "Define the Agent design protocol v1."

Conversation Objective:
  "Draft the context-pack contract section and list acceptance checks."
```

Forbidden:

```text
Conversation Objective:
  "Implement unattended automation because it seems useful."
```

If the local objective needs to change the task goal, return a checkpoint with
`review_required` and proposed goal change.

## Authority Boundaries

| Action | Authority |
|---|---|
| Create canonical task goal | DispatchCenter with PMO/user record |
| Create permanent department | PMO/user approval plus repeated queue pressure |
| Create dedicated task conversation | DispatchCenter under parent department |
| Close dedicated task conversation | DispatchCenter after result import/review |
| Accept task result | PMO or assigned reviewer gate |
| Block unsafe action | Security/hook/policy |
| Commit/release | DevOps |

## Failure Modes

Stop and escalate when:

- two conversations claim ownership of the same canonical task,
- a conversation lacks task id or result-packet path,
- a context pack is raw transcript rather than curated context,
- a department tries to create another durable department,
- a worker changes goal or scope without a recorded event,
- Codex App/VSCode sync is unstable enough that task state would be lost.
