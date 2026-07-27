# CoAgent Design Synthesis Round 10

## source_slice

- CoAgent first-pass official principle audit, concept boundary document, and
  URL seed list.
- CoAgent second-pass local runtime audit and Hermes/Codex/OpenClaw/LangGraph
  design matrix.
- Existing MoSim operating documents for organization, dispatch, visible
  department conversations, task packets, result packets, and context packs.
- The user's architecture correction: learn before implementing, keep
  departments sparse, use Codex App/VSCode as UI, and make durable
  communication explicit rather than relying on hidden subagents.

## read_files_or_urls

- `CoAgent/learning/audits/2026-05-27_official_multi_agent_principles_round8.md`
- `CoAgent/learning/audits/2026-05-27_local_runtime_architecture_round9.md`
- `CoAgent/docs/architecture/agent_concept_boundaries.md`
- `CoAgent/docs/architecture/local_runtime_design_matrix.md`
- `CoAgent/docs/research/THREE_ROUND_STUDY_AND_DISCUSSION.md`
- `CoAgent/docs/research/LEARNING_STRATEGY.md`
- `CoAgent/docs/architecture/ARCHITECTURE.md`
- `CoAgent/docs/architecture/COMPONENT_MAP.md`
- `Docs/Workflows/agent_orchestration.md`
- `Docs/Workflows/org_operating_model.md`
- `CoAgent/dispatch/department_threads.json`

## architecture_claims

1. CoAgent should be a project-owned workflow control plane. Codex App and
   VSCode are excellent UI/review surfaces, but durable communication must be
   task packets, result packets, context packs, event logs, and status boards.
2. A visible department conversation is not a subagent. It is a durable
   responsibility lane with scope, allowed work, task state, stop condition,
   result contract, and review rules.
3. A short-lived subagent is useful for bounded reading or one-shot analysis,
   but it is not reliable for Git, documentation, testing, safety, or other
   long-running queues because its context and state disappear after return.
4. The PMO/main conversation should own user alignment and final integration.
   DispatchCenter should own task tickets, state transitions, routing, and
   result intake. These are logically separate even when operated by the same
   assistant at first.
5. Departments must stay sparse. More departments increase stale context,
   cross-thread synchronization risk, and duplicated work. New departments
   require repeated queue pressure or a strong safety boundary.
6. Skills are selectively loaded procedures. Hooks and policies are hard
   runtime enforcement. Memory/search is background evidence. MCP/tools are
   callable capability surfaces. Mixing these concepts causes unsafe and
   unpredictable behavior.
7. Human review is a state transition, not a chat remark. `review_required`,
   `input_required`, `auth_required`, `blocked`, `approved`, `rejected`, and
   `completed` should be explicit task states.
8. Communication should be append-only first. A department should receive a
   task packet and return a result packet. Derived summaries and status boards
   can be rebuilt from those artifacts.
9. Long scientific or engineering tasks, such as PX4 log parameter
   identification or UE scene truth generation, should use dedicated task
   conversations when they need sustained context and repeated review.
10. The immediate next phase should finalize philosophy and contracts before
    adding more runtime automation or broad app-server integration.

## adopt_now

- Use `CoAgent/docs/decisions/coagent_design_discussion_packet.md` as the next
  discussion entry point before implementation.
- Keep the current durable conversation set small: main/user control,
  DispatchCenter, Documentation Secretary, Engineering, Verification,
  Security, and DevOps.
- Treat Engineering as the default execution lane, not a reason to create many
  narrow permanent departments.
- Treat DevOps as a permanent department because Git work is high-risk,
  state-heavy, and can be extremely large.
- Treat Documentation, Verification, and Security as independent gates, not
  implementation owners.
- Require any dedicated task conversation to have parent department, task id,
  read/write scope, stop condition, expected result packet, and review gate.
- Keep task/result/context/event artifacts as the cross-conversation
  communication substrate.
- Continue the study-first gate: no new runtime features until this synthesis
  is discussed.

## adapt_later

- Convert the discussion packet into a stable CoAgent operating spec after the
  user approves the philosophy and department boundaries.
- Add a compact task-state schema after the event/status vocabulary is agreed.
- Add app-server integration only after file/CLI transport reliability and
  protocol stability are verified.
- Add scheduled workflow optimization and repo-update automation only after
  hooks and review gates are enforced.
- Add richer memory/knowledge promotion after the first real long-task
  conversations show what context is repeatedly missing.

## portable_only

- A larger department hierarchy may be useful for future team-scale projects,
  but MoSim should start with a small control-plane and gate set.
- A full A2A-compatible or LangGraph-compatible backend may be useful if
  CoAgent becomes a reusable framework, but not before MoSim's local contracts
  stabilize.
- Hermes/OpenClaw multi-channel gateway ideas remain portable references, not
  immediate MoSim implementation targets.

## reject

- Do not use hidden subagents as evidence that a visible department received
  work.
- Do not create a permanent department for every technical topic.
- Do not let Documentation Secretary own the whole status board. Documentation
  records decisions; DispatchCenter owns task state.
- Do not let PMO/main conversation silently become the worker for long Git,
  test, docs, safety, or research queues.
- Do not rely on raw chat history as the communication protocol.
- Do not implement new automation or app-server integration before the design
  discussion closes the open questions.

## unknowns

- Whether PMO and DispatchCenter should remain two visible conversations or
  only two logical roles until communication stabilizes.
- Whether Engineering should stay as one general execution department or split
  later into simulator, control, UE, and data-analysis departments.
- The minimum event schema needed for robust replay and status-board rebuilds.
- The best persistence split between human-readable JSONL/Markdown and indexed
  SQLite state.
- The exact threshold for creating a dedicated task conversation instead of
  using Engineering or a one-shot subagent.

## required_patch

- Add this synthesis audit.
- Add `CoAgent/docs/decisions/coagent_design_discussion_packet.md`.
- Update the three-round discussion draft to point at the new local runtime
  matrix and discussion packet.
- Validate learning index and coverage.

## verification

```bash
python3 CoAgent/learning/learning_indexer.py validate --strict
python3 CoAgent/learning/learning_indexer.py coverage
python3 - <<'PY'
from pathlib import Path
paths = [
    Path('CoAgent/learning/audits/2026-05-27_coagent_design_synthesis_round10.md'),
    Path('CoAgent/docs/decisions/coagent_design_discussion_packet.md'),
]
for path in paths:
    text = path.read_text(encoding='utf-8')
    assert 'DispatchCenter' in text
    assert 'Hooks' in text or 'hooks' in text
    assert 'Skills' in text or 'skills' in text
    assert 'department' in text.lower()
print('coagent synthesis docs OK')
PY
```

## next_trigger

- Use this before the user discussion about CoAgent design philosophy.
- Use this before changing department boundaries or visible thread names.
- Use this before adding app-server transport, task replay, standing orders, or
  unattended automation.
