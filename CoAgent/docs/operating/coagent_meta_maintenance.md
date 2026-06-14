# CoAgent Meta-Maintenance Checklist

> Portable maintenance workflow for keeping a CoAgent deployment's registry,
> operating documents, capability inventory, recurring checks, and incident
> records current without creating unnecessary standing departments.

Status: split-audited portable core, 2026-06-10 CST.

Host-specific automation ids, visible-thread titles, deleted routes, product
priorities, GUI incidents, and notification wording belong in the host adapter.
For MoSim, use `Docs/Workflows/coagent_meta_maintenance.md`,
`CoAgent/dispatch/department_threads.json`, and
`Docs/Workflows/coagent_ops_patrol_workflow.md`.

## 1. Scope

Meta-maintenance owns the health of the operating system around the work. It
does not own product priority or acceptance.

It covers:

- visible-route registry hygiene;
- stale workflow, skill, and index detection;
- capability inventory and missing-index reports;
- recurring automation or wakeup records;
- packet/schema/checker drift reports;
- incident follow-up and rule deduplication;
- migration and portability audit records.

It does not:

- approve product scope or final acceptance;
- perform live domain work outside a task packet;
- recreate deleted routes or automations from old assumptions;
- replace current board, result packet, or evidence review;
- mutate runtime, schema, hooks, or transport without the relevant approval
  gate.

## 2. Maintenance Cadence

A host project should define its own cadence and owner, but the recurring
checklist should stay bounded:

| Area | Check |
|---|---|
| Route registry | Only current, explicitly active routes are dispatchable. Archived, deleted, or missing routes are not treated as failures. |
| Operating docs | Entry documents point to detailed workflows instead of copying dated incident blocks. |
| Packet contracts | Current templates and checkers still require return/blocker paths, surface gates, semantic boundary, evidence, and owner fields. |
| Capability index | New plugin, MCP, script, skill, or visible-thread capability has an owner and a claim ceiling. |
| Automations | Every recurring task has a current owner, purpose, cadence, evidence path, and stop condition. |
| Incident records | Closed incidents have a packet, audit entry, root-cause note, and a reusable rule only if the rule is still current. |
| Portability | Portable CoAgent docs do not accumulate host ids, local paths, product priorities, or domain evidence rules. |

## 3. Patrol Alignment

Executable patrol and recovery state machines live in
`CoAgent/docs/operating/coagent_ops_patrol_workflow.md`. Meta-maintenance may
audit that the patrol workflow is current, but it should not duplicate the full
patrol ladder.

When a patrol incident creates a reusable lesson:

```text
incident packet
  -> audit note
  -> decide whether the lesson is host-local or portable
  -> patch the owning workflow/checker/schema once
  -> update the index pointer
  -> avoid adding another dated hotfix block elsewhere
```

If a host needs emergency instructions in an automation prompt, keep the prompt
compact and point to the workflow for details.

## 4. Registry Hygiene

Registry review must distinguish these cases:

| Case | Action |
|---|---|
| current active route | keep dispatchable if the host registry marks it active |
| archived or deleted route | keep as historical evidence only if needed; do not patrol or no-op |
| missing route | not a failure unless current board or packet explicitly requires it |
| renamed route | update aliases in the registry or host org adapter |
| replacement route request | require PMO/user or host authority approval |

Do not keep a separate implicit blacklist when the registry can express current
status directly.

## 5. Capability Inventory

Capability records should answer "what surface should be considered for this
task?" They do not grant permission.

Recommended fields:

```text
capability_id:
surface_type: native | plugin | MCP | script | skill | visible_thread | subagent | checker
use_when:
owner_workflow_or_skill:
required_scope_field:
forbidden_actions:
health_or_checker:
claim_ceiling:
last_verified:
```

When a new capability is discovered, classify it before promotion:

```text
adopt
adapt
reference_only
reject
blocked
```

Promotion requires a narrow smoke check or documented reason that no runtime
check is needed.

## 6. Automation Records

Recurring automations and wakeups are records, not proof of work.

Each record should include:

```text
automation_id:
owner:
cadence:
target route or scope:
purpose:
allowed actions:
forbidden actions:
evidence path:
last verified:
stop condition:
```

After a user deletes or resets an automation, do not recreate it from memory.
Use explicit current approval or a host PMO decision.

## 7. Incident Follow-Up

Every real operating incident should produce one of:

- return packet;
- blocker packet;
- recovery packet;
- audit note linked to the packet;
- explicit "not a project fault" note.

An incident follow-up is complete only when:

1. the symptom and surface are classified;
2. the owner and next step are named;
3. any user notification is recorded separately from recovery;
4. reusable learning is patched into one owning workflow, checker, schema, or
   index;
5. obsolete duplicated wording is not left in entry documents.

## 8. Stale-Rule Prevention

When a workflow gets longer because of repeated incidents, apply this cleanup
rule:

```text
keep the current state machine
keep current stop triggers
keep current evidence requirements
move host facts to host adapters
move examples to audit or appendix
delete superseded incident prose only after a landing row exists
```

Entry documents should receive only the pointer or hard boundary needed for a
fresh conversation.

## 9. Output

Meta-maintenance outputs should be reviewable and narrow:

```text
missing_index_report:
stale_rule_report:
registry_delta_proposal:
capability_inventory_delta:
automation_record_delta:
incident_audit:
portability_split_audit:
```

If the finding requires product judgment, route it to the host PMO or owning
role instead of silently changing product priority.

## 10. Completion Criteria

A meta-maintenance pass is complete when:

- route and automation records match current host truth;
- stale or duplicate operating rules are either removed with a landing row or
  left with an explicit owner and reason;
- indexes point to the owning workflow, skill, checker, or schema;
- no deleted/archived route is treated as active work;
- any required incident packet or blocker exists;
- the pass does not claim product progress unless an engineering owner returned
  evidence through the normal contract.
