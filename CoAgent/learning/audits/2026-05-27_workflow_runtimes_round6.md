# Workflow Runtimes Round 6

## source_slice

- Local workflow/runtime references under `References/Agent`: Temporal,
  TaskWeaver, OpenSpec, and OKWinds Skills Runtime SDK.
- Focused read on durable history, mutable workflow state, worker tasks,
  planner/executor plugins, spec/action workflows, capability inventories, and
  quality gates for coding agents.
- Current CoAgent target surfaces: runtime events, automation schedules,
  worker recovery, task bootstrap, result review, and future replay/pause/cancel
  semantics.

## read_files_or_urls

- `References/Agent/temporal/docs/architecture/workflow-lifecycle.md`
- `References/Agent/TaskWeaver/website/docs/overview.md`
- `References/Agent/OpenSpec/docs/workflows.md`
- `References/Agent/okwinds/skills-runtime-sdk/docs_for_coding_agent/README.md`
- `References/Agent/openclaw/docs/automation/taskflow.md`

## architecture_claims

1. Durable workflows are event histories plus mutable state, not only queues.
   Temporal's lifecycle clarifies why CoAgent should keep JSONL event streams
   and SQLite state separate but linked.
2. Tasks and workflows are different levels. OpenClaw task flow and Temporal
   workflow/activity separation support CoAgent's distinction between
   automation schedules, runtime tasks, visible worker conversations, and result
   packets.
3. Code-first planner/executor systems need plugin boundaries, verification,
   logs, metrics, and sandboxing. TaskWeaver supports CoAgent's direction:
   project-specific tools should be declared, testable, and logged before
   autonomous use.
4. Spec/action workflows are more realistic than rigid phases. OpenSpec's
   action-oriented model supports CoAgent's PMO/DispatchCenter approach:
   tasks should be able to explore, propose, implement, verify, pause, and
   archive without pretending every task follows a single waterfall.
5. Coding-agent documentation packs should provide shortest path, capability
   inventory, tests, and proof of completion without reading the whole repo.
   OKWinds supports CoAgent's coverage/audit/index strategy.

## adopt_now

- Keep runtime SQLite state plus JSONL events as the durable workflow seed.
- Keep automation schedules separate from task state and visible worker
  conversations.
- Keep task bootstrap as the standard workflow-start surface for long-running
  dedicated conversations.
- Keep source-family coverage and audit files as the coding-agent "do not read
  whole repo first" mechanism.
- Keep deterministic checks before acceptance: preflight, doctor, learning
  validate/coverage, reference index, knowledge build/search, and result review.

## adapt_later

- Add workflow replay support that reconstructs task state from event logs and
  result packets, then compares it to SQLite state.
- Add explicit pause, cancel, retry, mirror, and resume semantics to runtime
  tasks and conversation edges.
- Add workflow-level revision/conflict handling when multiple sources try to
  advance the same task.
- Add per-task capability inventories so worker dispatch can verify required
  tools before starting.

## portable_only

- Full Temporal-style service architecture is excessive for local MoSim but is
  useful if CoAgent is later deployed as a team service.
- TaskWeaver's data-analytics plugin execution model is useful for future
  Syslab/MWORKS analytical workflows, but it should not become CoAgent's
  general runtime core.
- OpenSpec command packs are useful for other repositories; MoSim should keep
  its project-specific task/result packet contracts.

## reject

- Do not replace the CoAgent runtime with a full workflow engine at this stage.
- Do not use workflow labels as proof of state. State transitions need events,
  result packets, and validation output.
- Do not let automation schedules directly mutate project files without task
  packets, guardrails, and review gates.
- Do not make every task follow a heavy spec workflow; simple bounded tasks
  should stay lightweight.

## unknowns

- The event schema for replay is not final. Current JSONL events are enough for
  recovery hints, not yet full deterministic replay.
- The correct granularity for task pause/cancel is open: runtime task,
  conversation edge, transport process, or all three.
- Whether CoAgent needs workflow revision conflict detection depends on how many
  concurrent department workers are actually used.

## required_patch

- Add this workflow-runtime audit record to close the `workflow_runtimes`
  source-family coverage gap.
- Keep the existing runtime/event/automation separation as adopted architecture
  and document the replay/pause/cancel work as later-phase.
- No external workflow engine import is justified by this source slice.

## verification

```bash
python3 CoAgent/learning/learning_indexer.py coverage
python3 CoAgent/learning/learning_indexer.py validate --strict
python3 CoAgent/knowledge/knowledge_indexer.py build
python3 CoAgent/knowledge/knowledge_indexer.py search --query workflow_runtimes --limit 10
python3 CoAgent/doctor/coagent_doctor.py
python3 CoAgent/hooks/preflight.py
```

## next_trigger

- Revisit this audit before adding replay, pause/cancel, or retry semantics.
- Revisit this audit before enabling unattended automation loops beyond guarded
  staged dispatch.
