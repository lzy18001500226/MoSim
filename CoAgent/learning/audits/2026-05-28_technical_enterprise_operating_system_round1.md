# Technical Enterprise Operating System Round 1

## source_slice

- Engineering-management and technical-organization operating models relevant
  to CoAgent but not limited to agent implementation.
- Focused on preserving intent, accountability, decision quality, fast flow,
  incident learning, release stability, and organizational memory.
- This audit is a learning record. It does not approve CoAgent runtime,
  transport, automation, schema, or department implementation.

## read_files_or_urls

- `https://handbook.gitlab.com/handbook/people-group/directly-responsible-individuals/`
- `https://handbook.gitlab.com/handbook/engineering/development/growth/engineering_dri/`
- `https://www.atlassian.com/team-playbook/examples/making-decisions`
- `https://sre.google/sre-book/postmortem-culture/`
- `https://sre.google/resources/practices-and-processes/incident-management-guide/`
- `https://dora.dev/guides/dora-metrics/`
- `https://dora.dev/insights/dora-metrics-history/`
- `https://www.atlassian.com/devops/frameworks/team-topologies`
- `https://learn.microsoft.com/azure/well-architected/architect-role/architecture-decision-record`
- `https://www.aboutamazon.com/news/workplace/an-insider-look-at-amazons-culture-and-processes`
- `CoAgent/docs/architecture/technical_enterprise_operating_system.md`

## architecture_claims

1. Accountability must be single-owner even when execution is collaborative.
   GitLab's DRI model and Atlassian's DACI pattern both separate contributors
   from the person accountable for decision or delivery. CoAgent should do the
   same for every non-trivial task.
2. Task intent must be captured before execution. Amazon's working-backwards
   practice is valuable because it forces the desired customer/user outcome to
   be debated before implementation details dominate.
3. Recovery and learning are operating-system features. Google SRE treats
   incident response and blameless postmortems as a way to prevent recurring
   failure. CoAgent should treat repeated agent failures as system defects that
   update process, hooks, skills, tests, or documentation.
4. Fast flow requires team-boundary design, not only harder work. Team
   Topologies shows that supporting/platform/enabling responsibilities should
   reduce cognitive load for stream-aligned delivery. CoAgent departments
   should exist only when they reduce task load or risk.
5. Delivery health needs balanced measures. DORA metrics combine speed and
   stability; CoAgent should avoid optimizing only throughput. It should also
   track rework, failed handoffs, blocked time, recovery time, and review
   escapes.
6. Architecture memory must be explicit. ADR practice records significant
   decisions, rejected alternatives, consequences, and revisit conditions.
   CoAgent should not rely on chat memory for major design choices.
7. Management controls must be lightweight but mandatory at the right gates.
   Every task should not need a heavy RFC, but high-impact or ambiguous tasks
   need design review, stop conditions, and user checkpoints before execution.

## adopt_now

- Add the technical-enterprise operating model as a first-class CoAgent
  learning document.
- Treat every durable task as requiring one accountable owner, even if multiple
  departments contribute.
- Add intent, definition of done, non-goals, risk, and escalation conditions
  to task-start thinking before implementation resumes.
- Treat checkpoint frequency as proportional to uncertainty and risk.
- Treat repeated task drift, failed handoff, broken session sync, missing
  evidence, and late discovery of wrong objectives as incidents that deserve
  after-action review.
- Use ADR/design-note style records for high-impact architecture decisions.

## adapt_later

- Add lightweight DORA-inspired internal metrics for CoAgent work: lead time
  from task request to accepted result, failed handoff rate, review escape
  rate, recovery time after blocked/stale state, and rework count.
- Add a task-start template that distinguishes simple tasks from tasks needing
  pre-mortem, design review, or user checkpoint.
- Add an after-action-review template for agent failures and repeated process
  drift.
- Add a decision authority table mapping PMO, Dispatch, Engineering,
  Verification, Security, Documentation, and DevOps to accountable decisions.

## portable_only

- Full Team Topologies stream-aligned/platform/enabling/complicated-subsystem
  structure is useful for larger human organizations, but MoSim should keep a
  smaller department set and borrow only the cognitive-load principle.
- Full SRE incident tooling is excessive now, but the incident-state and
  blameless postmortem concepts are portable if CoAgent becomes a team service.
- Formal DACI/RACI ceremonies are useful references, but CoAgent should encode
  the minimum fields in task packets instead of creating ceremony overhead.

## reject

- Do not let speed metrics override correctness, evidence, safety, or user
  intent.
- Do not make every task require an RFC/ADR; that would kill flow and cause
  process avoidance.
- Do not treat department boundaries as static task boundaries. Keep stable
  responsibility, but allow explicit cross-functional assistance.
- Do not let a department self-certify high-risk work without independent
  verification or security review.
- Do not allow a task to run for hours without checkpointing when the objective
  or feasibility is uncertain.

## unknowns

- The right checkpoint interval for MoSim long tasks needs empirical tuning.
- The minimum useful CoAgent metric set should be chosen after several real
  task lifecycles, not before.
- The exact threshold for requiring ADR versus a smaller decision note is still
  open.
- Whether PMO and Dispatch should be separate visible conversations or logical
  roles remains a communication-reliability question.

## required_patch

- Add this audit record.
- Keep `CoAgent/docs/architecture/technical_enterprise_operating_system.md` as the
  management-model entry point.
- No runtime or automation implementation in this pass.

## verification

```bash
python3 CoAgent/learning/learning_indexer.py validate --strict
python3 CoAgent/doctor/check_design_gate.py
```

## next_trigger

- Before changing task-start templates, owner fields, checkpoint rules,
  after-action-review rules, ADR policy, or department decision authority.
- Before approving unattended long-running department work.
- Before adding CoAgent delivery metrics or status dashboards.
