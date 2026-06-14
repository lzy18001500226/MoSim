# Context And Documentation Governance Research

> Research note on Codex App context sources, MoSim documentation structure,
> skill/MCP/plugin/workflow routing, and project-owned memory boundaries.

Status: research note, 2026-06-10 CST. This file is not an execution workflow,
not an authority grant, and not an entry document. Promote any rule here through
the normal review path before treating it as current policy.

## 1. Research Question

MoSim uses Codex App visible threads, automations, goals, skills, plugins, MCP
servers, project hooks, project documents, and memory/context helpers. The
question is how to structure project documents so Codex receives enough context
to work, but does not confuse old chat, global memory, capability listings, or
workflow drafts with current project truth.

The key problem is not raw tool-calling ability. The problem is controlling
which project-owned context layer is authoritative for a given decision.

## 2. Prompt And Context Sources

Based on official documentation and local observation, a Codex turn may involve
these context categories:

| Source | Project Control | Research Interpretation |
|---|---|---|
| product/system/developer context | not directly controlled | The full product prompt stack is not public or stable. |
| tool schemas and MCP instructions | partially controlled | Tools must be routed through task scope and capability selection. |
| `AGENTS.md` and startup docs | controlled | These should stay short and stable. |
| skills and plugin skill descriptors | partially controlled | Skills are progressively disclosed; load only the needed skill body. |
| workflow and operating docs | controlled | Store repeatable procedures and interpretation rules here. |
| thread history and compression | not fully controlled | Do not make thread history the only project state. |
| Codex goal or automation payload | partially controlled | Execution lifecycle input, not project fact storage. |
| official/global Codex memory | not project-scoped | Recall hints and user-preference background only. |
| project-owned memory/context helpers | controlled | Fenced, sourced, and subordinate to current rules. |

Confirmed public mechanisms include `AGENTS.md`, skills, MCP, automations,
goals, tool schemas, and memories. The exact Codex App prompt assembly order
and hidden product messages should be treated as unavailable implementation
detail.

## 3. Proposed Authority Ladder

This ladder is the research recommendation, not yet a new enforced rule:

```text
current user or PMO decision for this task
-> hard hook/checker/schema boundary
-> task packet scope and semantic boundary
-> current project source, board, result packet, or evidence file
-> current workflow, skill, design, or index
-> reviewed project cache or migration record
-> global Codex memory or old chat-derived hint
```

Global memory, old thread history, and compressed summaries should only point to
project files that still need to be opened or checked.

## 4. Recommended Document Responsibilities

| Class | Should Own | Should Not Own |
|---|---|---|
| `AGENTS.md` | hard boundaries, startup order, authority map, source-of-truth pointers | detailed patrol ladders, domain procedures, status logs, task history |
| short startup context | current recovery entry, accepted/rejected route summary, next read order | full historical trace, all workflow details |
| PMO board | current state, next dispatch action, waiting/blocking items | archival evidence, long decisions, broad policies |
| operating workflow | reusable procedure, role view, recovery ladder, interpretation rule | current board state or host-specific facts unless adapter-scoped |
| host workflow/adapter | project-specific domain gates, evidence rules, route bindings | portable CoAgent OS policy |
| skill | task-family procedure, required probes, tool sequence, stop actions | broad project policy or current PMO priority |
| capability index | route selection and owner pointers | authorization, acceptance, or tool health claims without evidence |
| schema/checker/hook | enforceable fields, path/safety gates, deterministic contract checks | ambiguous prose policy |
| context pack | compact startup state for a bounded task | raw transcript, unrelated facts, credentials, or permanent memory |
| project memory context | fenced background recall with sources | instructions, acceptance, or current-state truth |
| result packet/evidence | task outcome, blocker, proof, artifact path | reusable policy unless promoted through review |

The useful shorthand is:

```text
entry documents do not hold procedures
procedures do not hold current board state
indexes do not grant permission
memory does not prove facts
evidence packets do not silently create policy
```

## 5. Workflow And Skill Writing Norms

Recommended workflow fields:

```text
when to use it
owner
required inputs
allowed actions
forbidden actions
stop triggers
evidence required
checker or schema gate
output paths
index update rule
```

Recommended skill fields:

```text
trigger condition
minimum files or docs to read
tool or MCP sequence
preflight health check
forbidden actions
expected artifacts
acceptance or smoke check
common failure and blocker wording
```

The important distinction is that a skill is a procedure, not permission. A
task still needs user/PMO permission, task-packet scope, workflow authority, or
checker/schema coverage when the action can change project state.

## 6. Capability, MCP, Plugin, And Tool Routing

Recommended route:

```text
task intent
-> capability index row
-> owning workflow or skill
-> task packet scope and semantic boundary
-> current tool health or checker
-> action
-> evidence or blocker
```

Capability existence is not authorization. A plugin, MCP server, script, or
visible thread may be listed because it is relevant, while the current task may
still be read-only, blocked, or outside authority.

Useful fields for future capability cards:

```text
surface name
use when
forbidden or stop actions
owner workflow or skill
health/checker evidence
claim ceiling
```

## 7. Project-Owned Memory

Project-owned memory should be a retrieval layer, not a truth store.

Recommended behavior:

1. Keep recalled memory fenced as `<memory-context>`.
2. Label it as background evidence only.
3. Include source paths or retrieval hints.
4. Do not paste raw chat, private Codex session data, browser profiles,
   credentials, license files, or account state.
5. Promote a remembered claim only through session-memory migration or another
   reviewed evidence path.
6. If the claim affects current work, verify it against current project files,
   packets, checkers, or runtime evidence before acting.

Official/global Codex memories under user-level memory storage are useful for
finding likely files or preferences, but they are lower authority than
project-owned current state.

## 8. External Project Lessons

External frameworks should be mined for patterns, not adopted wholesale:

| Source Pattern | Useful CoAgent Shape |
|---|---|
| durable state machine and checkpoints | board, dispatch ticket, runtime lease, result/blocker packet |
| action/observation event stream | packet evidence, tool output manifests, recovery records |
| visible human/agent collaboration room | Codex visible departments plus PMO/CoAgentOps routing |
| task guardrails | JSON schema, quality checker, hook, semantic boundary |
| skill packages and memory search | `SKILL.md`, capability index, fenced project memory context |

The current research does not justify replacing Codex App visible threads with
a general autonomous swarm runtime.

## 9. Proposed Promotion Path

If this research is accepted, the lowest-risk promotion path would be:

```text
research note
-> PMO/user review
-> narrow operating workflow or schema/checker update
-> capability/workflow index pointer
-> entry-document pointer only if fresh conversations require it
```

Do not promote this file by adding it to startup read order unless the user/PMO
explicitly accepts it as an operating document.
