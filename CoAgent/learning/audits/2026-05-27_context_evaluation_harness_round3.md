# Context, Evaluation, and Harness Round 3

## source_slice

- Local Agent Skills for Context Engineering focused on context optimization,
  degradation, evaluation, and harness engineering.
- Official Anthropic Engineering articles focused on context engineering,
  long-running harnesses, and practical agent design.
- Current CoAgent implementation surfaces that must carry these lessons:
  context packs, result packets, result review gates, doctor checks, bootstrap
  handoffs, and learning audits.

## read_files_or_urls

- `Docs/Skills/Agent/Agent-Skills-for-Context-Engineering/skills/context-optimization/SKILL.md`
- `Docs/Skills/Agent/Agent-Skills-for-Context-Engineering/skills/context-degradation/SKILL.md`
- `Docs/Skills/Agent/Agent-Skills-for-Context-Engineering/skills/evaluation/SKILL.md`
- `Docs/Skills/Agent/Agent-Skills-for-Context-Engineering/skills/harness-engineering/SKILL.md`
- `https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents`
- `https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents`
- `https://www.anthropic.com/engineering/building-effective-agents`

## architecture_claims

1. CoAgent should treat context as an explicitly budgeted resource, not as a
   place to accumulate raw chat history. Dedicated long-running conversations
   should start from compact context packs whose size and risk can be measured.
2. Long-running agent work needs harness surfaces with different permissions:
   locked checks, editable artifacts, append-only logs, and human-controlled
   irreversible actions. A worker must not accept its own output simply because
   it produced a syntactically valid result packet.
3. Evaluation should start with deterministic structure and end-state checks,
   then escalate to human or model judgment only for quality questions that
   cannot be mechanically verified.
4. Handoff packets should include the current task, scope, blocker, evidence,
   expected result path, and recovery route. Raw transcripts and large source
   trees should stay behind retrieval/index tools unless directly needed.
5. The practical agent-design lesson for MoSim is to keep the smallest useful
   workflow that can be measured and recovered. More agents, UI, or autonomous
   loops should be added only when the task boundary and review gate are clear.

## adopt_now

- Keep `CoAgent/context/context_pack.py` as the required context entry point
  for dedicated task conversations, and keep character/token/section/memory
  budget metrics visible in bootstrap outputs.
- Keep `CoAgent/result_router/result_router.py` review metadata as the first
  result acceptance gate. Runtime import means "received"; acceptance requires
  evidence, next action, blocker detail when blocked, and no unresolved risk.
- Keep `CoAgent/doctor/coagent_doctor.py`, `CoAgent/hooks/preflight.py`, smoke
  tests, learning-audit validation, and reference-index validation as locked
  harness surfaces. Workers may read failures and propose fixes but should not
  weaken these gates to declare success.
- Keep bootstrap transport plans file-backed. `--packet-file` should point to a
  full handoff/context pack so the receiving visible conversation can recover
  from project state without hidden chat memory.
- Keep learning audits append-only by source slice. This prevents the main
  conversation from repeatedly rediscovering the same external-project lessons.

## adapt_later

- Calibrate context warning/failure thresholds from real MoSim long-running
  conversations instead of treating current character limits as final.
- Add explicit rejected-attempt logs and novelty checks for source-to-skill or
  source-to-runtime learning loops so CoAgent does not repeat failed designs.
- Add richer per-dimension result review after deterministic gates pass:
  correctness, evidence quality, scope discipline, tool economy, and recovery
  readiness.
- Add a harness-run directory format for unattended research loops with
  `THREAD.md`, source queue, proposal files, append-only result logs, and
  locked rubric references.

## portable_only

- Prefix/KV-cache optimization is valuable for hosted or API-level deployments,
  but the current local Codex App/CLI workflow does not expose a stable
  project-owned cache-control surface.
- Generic Slack/Discord/GitHub-style gateway patterns remain useful if CoAgent
  is migrated to another project, but MoSim should continue using Codex App as
  the visible frontend for now.
- A fully general LLM-as-judge framework may be portable later. MoSim currently
  needs deterministic gates and human review before broad model-judged scoring.

## reject

- Do not load the full `References/Agent` or `Docs/Skills/Agent` corpus into
  every task context. Use bounded audits, indexes, and retrieval.
- Do not let a department worker modify locked validation gates and then use
  the modified gate as proof that its own task passed.
- Do not accept result packets with `DONE` status but no evidence or next
  action as completed work. They may be imported for recovery, but the review
  gate should keep them in `needs_review`.
- Do not create more permanent department conversations just because a pattern
  exists in an external multi-agent framework. Conversation count increases
  coordination risk unless the task has a clear owner, scope, and result packet.

## unknowns

- The best practical context size for GPT-5.5 on MoSim engineering tasks is
  still empirical. Current metrics are safety rails, not tuned final thresholds.
- The right balance between human review and model-judge review for result
  packets remains open until more real department-task packets are collected.
- Direct Codex app-server integration may eventually provide better thread
  control, but current evidence still favors project-owned files plus visible
  Codex App review.

## required_patch

- Use the existing context quality metrics in `CoAgent/context/context_pack.py`
  as the first implementation of explicit context budgeting.
- Use the existing result review gate in
  `CoAgent/result_router/result_router.py` as the first implementation of
  deterministic acceptance separation.
- Keep `CoAgent/bootstrap/task_bootstrap.py --include-transport-plan` as the
  standard handoff proof because it sends full handoff/context via
  `--packet-file`.
- Update CoAgent status/progress/ledger so future work treats context metrics,
  result review, and locked harness gates as adopted architecture, not
  incidental tests.

## verification

```bash
python3 CoAgent/tests/test_task_bootstrap.py
python3 CoAgent/tests/test_memory_context.py
python3 CoAgent/tests/test_lifecycle_smoke.py
python3 CoAgent/tests/test_result_router.py
python3 CoAgent/learning/learning_indexer.py validate --strict
python3 CoAgent/knowledge/knowledge_indexer.py build
python3 CoAgent/doctor/coagent_doctor.py
python3 CoAgent/hooks/preflight.py
```

## next_trigger

- Revisit this audit after the first real PX4-log parameter-identification
  dedicated task conversation runs through bootstrap, transport, result import,
  review, and knowledge persistence.
- Revisit this audit when adding unattended research loops, source-to-skill
  proposal loops, or model-judged packet quality scoring.
- Revisit this audit if Codex App/CLI transport changes expose a stable
  app-server integration path or prompt-cache control surface.
