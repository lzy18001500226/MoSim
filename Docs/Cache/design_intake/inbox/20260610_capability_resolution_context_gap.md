# Capability Resolution And Context Gap

Status: cache_draft
Authority: none
Source: PMO discussion and CoAgentOps correction, 2026-06-10 CST
Target canonical doc: `CoAgent/dispatch/communication_contract.md`,
`CoAgent/protocol/templates/capability_resolution.json`,
`Docs/Index/capability_index.md`, future checker under `Scripts/quality/`
Promotion owner: PMO plus documentation-secretary review
Do not treat as workflow authority until promoted.

## Problem

The project already had these portable window skills:

```text
CoAgent/skills/window-capture-evidence/SKILL.md
CoAgent/skills/window-ui-action-control/SKILL.md
```

They were also already indexed from `AGENTS.md`,
`Docs/Workflows/new_conversation_context.md`, and
`Docs/Index/capability_index.md`.

However, a PMO answer still described the screenshot skill as if it needed to
be newly created. That is a multi-thread context-management failure:

```text
correct asset exists
index exists
current responding thread did not resolve existing capability first
answer proposed duplicate planning
```

The directory split alone does not solve this. The project needs a task-level
capability-resolution mechanism that makes "reuse existing asset before
creating new asset" explicit and checkable.

## Design Principle

Do not solve this by adding more prose to `AGENTS.md` or
`Docs/Workflows/new_conversation_context.md`.

Solve it at the dispatch/task boundary:

```text
task objective
  -> capability index lookup
  -> existing asset reuse decision
  -> explicit create-new justification if needed
  -> checker-visible packet field
```

## Proposed Minimal Patch

Current repository, before physical CoAgent restructuring:

```text
CoAgent/dispatch/communication_contract.md
CoAgent/protocol/templates/capability_resolution.json
CoAgent/protocol/templates/visible_thread_dispatch_packet.json
Docs/Index/capability_index.md
Scripts/quality/check_capability_resolution.py     # future implementation
Scripts/tests/test_capability_resolution.py        # future implementation
```

The first implementation should be small:

1. Add a `capability_resolution` packet block.
2. Add stable capability ids in `Docs/Index/capability_index.md`.
3. Require new asset creation to name searched existing assets and why they
   are insufficient.
4. Later, add a checker that fails duplicate creation when a matching existing
   capability is declared as reusable.

## Proposed Packet Block

```json
{
  "capability_resolution": {
    "required": true,
    "capability_index_consulted": true,
    "consulted_index_path": "Docs/Index/capability_index.md",
    "matched_capability_ids": [
      "desktop.window.capture_evidence"
    ],
    "matched_capabilities": [
      "Desktop window screenshot evidence"
    ],
    "existing_assets_to_reuse": [
      "CoAgent/skills/window-capture-evidence/SKILL.md"
    ],
    "searched_existing_assets": [
      "Docs/Index/capability_index.md",
      "CoAgent/skills/",
      "Docs/Skills/",
      "Scripts/"
    ],
    "create_new_assets": [],
    "reason_existing_assets_insufficient": "",
    "do_not_recreate": [
      "window capture skill",
      "desktop screenshot evidence skill"
    ],
    "unresolved_capabilities": []
  }
}
```

## Intended Checker Direction

A future `Scripts/quality/check_capability_resolution.py` should check:

1. If a packet declares capability-sensitive work, `capability_resolution`
   must exist.
2. If `create_new_assets` includes a skill, workflow, script, checker, or MCP
   adapter, the packet must include `searched_existing_assets` and
   `reason_existing_assets_insufficient`.
3. If `do_not_recreate` conflicts with `create_new_assets`, fail.
4. If `matched_capability_ids` points to a known existing asset, new creation
   of the same capability requires explicit insufficiency reasoning.

This checker should not become an authorization mechanism. It only prevents
context-drift and duplicate planning. Authority still comes from task scope,
PMO/user approval, workflows, hooks, schema, and domain gates.

## Gap Analysis Against `okwinds/capability-runtime`

Local reference:

```text
References/Agent/Workflow/okwinds/capability-runtime
```

That project uses a clearer long-term model:

```text
Protocol -> Runtime -> Report
```

MoSim/CoAgent is moving in the same direction, but still has these gaps.

### Gap 1: Capability Index Is Still Mostly Human-Readable

Current state:

```text
Docs/Index/capability_index.md
```

This is useful for humans and agents, but it is not a machine-readable
capability manifest. It cannot reliably drive validation, duplicate detection,
health checks, or route selection.

Needed later:

```text
CoAgent/capabilities/capability_index.json
```

or equivalent manifest with:

```text
stable_id
human_name
owner_doc
primary_skill_or_workflow
scripts
checker_or_test_anchor
evidence_contract
authority_ceiling
stop_actions
health_status
```

### Gap 2: Capability Resolution Has A Template But No Checker Yet

Current state:

```text
CoAgent/protocol/templates/capability_resolution.json
```

This records the expected packet block, but no checker enforces it yet.

Needed later:

```text
Scripts/quality/check_capability_resolution.py
Scripts/tests/test_capability_resolution.py
```

The checker should catch cases like:

```text
existing skill is indexed
task proposes creating the same skill again
no insufficiency reason is provided
```

### Gap 3: No Capability Coverage Map With Regression Anchors

`capability-runtime` has a coverage map that links:

```text
capability area -> public entry -> primary source -> example -> regression anchor
```

MoSim has the beginnings of this in `Docs/Index/capability_index.md`, but the
links are not yet systematic. For each major capability, MoSim should know:

```text
stable capability id
human entry doc
skill/workflow
script or MCP surface
checker/test
evidence path/class
known stop conditions
```

This would reduce multi-thread context drift because a thread can resolve a
capability through one table instead of guessing from memory.

### Gap 4: Report/Evidence Is Still Split Across Packets And Results

Current evidence is spread across:

```text
return packet
blocker packet
dispatch ticket
runtime lease
screenshot manifest
checker output
PMO board
Results subdirectories
```

This is workable, but not yet equivalent to a single `NodeReport`-like
structured report. A future evidence aggregator could produce a compact
task-level report that points to all evidence without replacing the underlying
files.

Do not rush this into runtime implementation. The near-term improvement is to
make packet/checker/evidence references consistent.

### Gap 5: Host Wait/Resume/Approval Surfaces Are Not Unified

The project has practical handling for:

```text
approval/review/provider UI
context-compression surface
dead-thread recovery
manual review
email notification
restart validation
```

But these are still distributed across patrol workflow, communication contract,
board state, packets, and operational memory. A future host protocol could
standardize:

```text
wait state
resume intent
approval ticket
manual review decision
restart/recovery result
```

This should remain a design target. It should not bypass current PMO authority
or domain gates.

### Gap 6: Context Intake Exists, But Promotion Is Not Automated

Current state:

```text
Docs/Cache/design_intake/
```

This gives the project a safe place for discussion-derived drafts. The missing
piece is a periodic review workflow that classifies drafts as:

```text
promote to canonical
keep in cache
reject
supersede
needs PMO decision
```

This review should be done by the documentation-secretary/context-maintenance
route as a patch proposal, not as silent authority changes.

### Gap 7: Runtime Object Model Is Still Conceptual

The desired object model exists in design discussion:

```text
TaskPacket
DispatchTicket
RuntimeLease
CapabilityResolution
ReturnPacket
BlockerPacket
EvidenceReport
HostSnapshot
CheckerResult
```

But the repository still stores these across multiple documents and scripts.
That is acceptable before physical CoAgent restructuring. The immediate rule
is: do not invent a new runtime dependency just to make the tree look cleaner.

## Recommended Priority

Near-term, before physical restructuring:

1. Keep using `capability_resolution` in new task/dispatch packets when tool
   or asset selection matters.
2. Add a machine-readable capability manifest only after the stable id list is
   reviewed.
3. Implement `check_capability_resolution.py` before relying on this mechanism
   for enforcement.
4. Build a capability coverage map before moving skill/workflow/script files.
5. Keep design discussion in `Docs/Cache/design_intake/` until the promotion
   target is clear.

Do not adopt `capability-runtime` as a dependency yet. Its value for MoSim is
as a reference pattern for capability manifests, runtime/report separation,
coverage maps, and evidence-first results.

## Cache Status

This note records the motivation and desired mechanism. It is not yet a
complete implementation and must not be treated as dispatch authority.
