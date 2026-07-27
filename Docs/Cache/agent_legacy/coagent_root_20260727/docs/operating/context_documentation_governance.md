# Context And Documentation Governance

> Portable CoAgent policy for deciding which context source is authoritative,
> where documentation belongs, and how context-maintenance agents may propose
> updates without silently changing project truth.

Status: split-audited portable core, 2026-06-10 CST.

Host-specific startup files, board state, route ids, project memory indexes,
and cache folders belong in the host adapter. For MoSim, use
`Docs/Workflows/new_conversation_context.md`,
`Docs/Index/project_work_memory_index.md`,
`Docs/Workflows/session_memory_migration.md`, and
`CoAgent/dispatch/department_threads.json`.

## 1. Authority Ladder

When context sources conflict, use this order:

```text
current user or PMO decision for this task
-> hard hook/checker/schema boundary
-> task packet scope and semantic boundary
-> current project source, board, result packet, or evidence file
-> current workflow, skill, design, or index
-> reviewed project cache or migration record
-> global memory or old chat-derived hint
```

Global memory, old thread history, and compressed summaries are retrieval hints.
They should point to current project files to verify, not become project truth
by themselves.

## 2. Document Responsibilities

| Class | Should Own | Should Not Own |
|---|---|---|
| entry document | hard boundaries, startup order, authority map, source-of-truth pointers | detailed patrol ladders, domain procedures, status logs, task history |
| short startup context | current recovery entry, accepted/rejected route summary, next read order | full historical trace, all workflow details |
| PMO or operations board | current state, next dispatch action, waiting/blocking items | archival evidence, long decisions, broad policy |
| operating workflow | reusable procedure, role view, recovery ladder, interpretation rule | current board state or host-specific facts unless adapter-scoped |
| host workflow/adapter | project-specific domain gates, evidence rules, route bindings | portable CoAgent OS policy |
| skill | task-family procedure, required probes, tool sequence, stop actions | broad project policy or current PMO priority |
| capability index | route selection and owner pointers | authorization, acceptance, or health claims without evidence |
| schema/checker/hook | enforceable fields, path/safety gates, deterministic contract checks | ambiguous prose policy |
| context pack | compact startup state for a bounded task | raw transcript or unrelated facts |
| project memory context | fenced background recall with sources | instructions, acceptance, or current-state truth |
| result packet/evidence | task outcome, blocker, proof, artifact path | reusable policy unless promoted through review |

Shorthand:

```text
entry documents do not hold procedures
procedures do not hold current board state
indexes do not grant permission
memory does not prove facts
evidence packets do not silently create policy
```

## 3. Context Intake

A new or resumed conversation should read the smallest current chain that can
restore the task:

```text
entry document
startup context
current board or task packet
route registry, if dispatch is involved
topic-specific workflow/skill/index
ledger or old cache only when trace-back is required
```

Do not make raw session dumps, old chat exports, plugin caches, or broad memory
search the routine recovery route.

## 4. Workflow And Skill Norms

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

A skill is a procedure, not permission. A task still needs user/PMO permission,
task-packet scope, workflow authority, or checker/schema coverage when the
action can change project state.

## 5. Capability Routing

Route tool choice through the capability index:

```text
task intent
-> capability index row
-> owning workflow or skill
-> task packet scope and semantic boundary
-> current tool health or checker
-> action
-> evidence or blocker
```

Capability existence is not authorization. A plugin, MCP server, script,
visible thread, sub-agent, or checker may be relevant while the current task is
still read-only, blocked, or outside authority.

## 6. Documentation Secretary Boundary

A documentation-secretary or context-maintenance role may:

- collect candidate updates;
- deduplicate repeated wording;
- prepare reviewable patches;
- maintain indexes and startup pointers;
- check whether a rule belongs in portable core or host adapter;
- record missing landing files and stale references.

It may not:

- change product priority or acceptance;
- approve new runtime/tool authority;
- silently rewrite PMO decisions;
- promote old chat claims without the memory-migration gate;
- delete host-local semantics before a no-loss landing row exists.

## 7. Project-Owned Memory

Project-owned memory is a retrieval layer, not a truth store.

Rules:

1. Keep recalled memory fenced or clearly labeled as background.
2. Include source paths or retrieval hints.
3. Verify current-impact claims against current project files, packets,
   checkers, or runtime evidence before acting.
4. Promote remembered claims only through
   `CoAgent/docs/operating/session_memory_migration.md` or another reviewed
   evidence path.
5. Do not store private auth material, full session dumps, account state, or
   unrelated personal data in project memory.

## 8. No-Loss Documentation Migration

Before slimming an entry or operating document:

```text
identify source block
verify landing file
copy or restate semantics
record status: exact | equivalent | intentionally_host_local | obsolete_superseded | missing
update indexes
only then remove or shorten source text
```

If the landing file is missing or stop conditions weaken, restore the source
block or patch the landing before reporting completion.

## 9. Completion Criteria

A context/documentation governance update is complete when:

- the authoritative owner for each rule class is clear;
- indexes point to the owning workflow, skill, checker, schema, or host
  adapter;
- old-chat or memory-derived claims remain cache-only until reviewed;
- documentation-secretary changes are reviewable and scoped;
- portable CoAgent docs do not absorb host-local board state, route ids, or
  product facts;
- host adapters retain project-specific evidence and route details.
