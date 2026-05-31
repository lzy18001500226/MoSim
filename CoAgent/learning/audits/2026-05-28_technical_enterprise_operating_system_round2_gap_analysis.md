# Technical Enterprise Operating System Round 2 Gap Analysis

## source_slice

- Additional management and engineering-operating-system sources for gaps not
  covered by the first DRI/SRE/DORA/ADR-oriented pass.
- Focused on scope control, complexity sense-making, product discovery,
  psychological safety, secure-by-design delivery, strategy deployment, and
  productivity measurement pitfalls.
- This audit is a learning record only. It does not approve CoAgent runtime,
  automation, transport, or task-schema implementation.

## read_files_or_urls

- `https://basecamp.com/shapeup/2.2-chapter-08`
- `https://basecamp.com/shapeup/2.1-chapter-07`
- `https://www.microsoft.com/en-us/research/publication/the-space-of-developer-productivity-theres-more-to-it-than-you-think/`
- `https://csrc.nist.gov/projects/ssdf`
- `https://rework.withgoogle.com/en/guides/understanding-team-effectiveness`
- `https://www.atlassian.com/devops/frameworks/team-topologies`
- `https://cynefin.io/index.php/Cynefin`
- `https://www.lean.org/lexicon-terms/strategy-deployment/`
- `https://www.svpg.com/books/empowered-ordinary-people-extraordinary-products/`
- `https://www.atlassian.com/team-playbook/plays/it-project-poster`
- `CoAgent/docs/architecture/technical_enterprise_operating_system.md`

## architecture_claims

1. Scope must be constrained by appetite, not estimated into infinity. Shape
   Up's betting, cooldown, and circuit-breaker ideas address the exact failure
   mode where work runs for hours or days because no one capped downside or
   forced scope tradeoffs.
2. Not every problem should use the same management mode. Cynefin's clear,
   complicated, complex, chaotic, and disorder framing suggests CoAgent should
   classify tasks before choosing execution style: automate clear tasks,
   analyze complicated tasks, probe complex tasks, stabilize chaotic tasks,
   and clarify disordered tasks.
3. Strategy deployment is a missing layer between long-term vision and daily
   tasks. Hoshin-style thinking says a small number of breakthrough objectives
   should guide project selection, otherwise many local optimizations can still
   drift from the system goal.
4. Product discovery and delivery must be separated but connected. SVPG's
   product-operating-model framing and Atlassian's project poster both point
   to the need to validate problem, assumptions, and outcome before committing
   execution capacity.
5. Team effectiveness requires psychological safety plus structure and clarity.
   Google re:Work's Project Aristotle summary warns against solving only for
   process. A system where agents cannot surface uncertainty or contradiction
   will silently drift.
6. Developer productivity should be measured multidimensionally. SPACE warns
   against single-metric productivity management; CoAgent should not optimize
   only number of tasks, commits, or tool calls.
7. Secure software delivery must be built into organization practice, not added
   as a final checklist. NIST SSDF groups practices around preparing the
   organization, protecting software, producing secure software, and responding
   to vulnerabilities; this maps directly to CoAgent security hooks, evidence,
   and response loops.
8. Team boundaries should reduce cognitive load, not create ticket handoff
   bureaucracy. Team Topologies reinforces that platform/enabling/specialist
   roles exist to make stream-aligned work faster and safer, not to fragment
   ownership.

## adopt_now

- Add task complexity classification before choosing execution mode:
  `clear`, `complicated`, `complex`, `chaotic`, or `disordered`.
- Add appetite and circuit-breaker thinking to long-task starts: define how
  much time/effort the task is worth before continuing.
- Require ambiguous tasks to start with problem framing and assumption/risk
  validation before execution.
- Treat uncertainty surfacing as a required behavior, not a weakness. A worker
  should be rewarded for early escalation when evidence contradicts the plan.
- Keep productivity metrics balanced: speed, quality, collaboration, flow,
  satisfaction/friction, and recovery.
- Treat security/compliance as lifecycle practice, not final review only.
- Preserve a small set of breakthrough objectives so local tasks can be tested
  against the larger MoSim direction.

## adapt_later

- Add a task-start checklist with fields for complexity domain, appetite,
  circuit breaker, discovery/delivery split, and strategy alignment.
- Add a lightweight project-poster/RFC format for high-uncertainty tasks:
  problem, affected users/systems, assumptions, options, constraints, risks,
  evidence, and next probe.
- Add an internal CoAgent productivity dashboard only after several real task
  lifecycles provide baseline data.
- Add secure-development practice mapping from SSDF to CoAgent hooks,
  preflight checks, review gates, and evidence records.
- Add a quarterly or milestone-level strategy review that prunes low-value
  work and refreshes breakthrough objectives.

## portable_only

- Shape Up's six-week cycle is too large for current MoSim agent work, but the
  concepts of appetite, betting, cooldown, and circuit breaker are directly
  portable at smaller time scales.
- Full Hoshin Kanri deployment is excessive for one project, but the small set
  of breakthrough objectives is useful.
- Full product operating model transformation is a human organization problem;
  CoAgent should borrow the focus on empowered teams solving problems rather
  than feature tickets.
- Full SSDF implementation may be needed for regulated delivery later; for now
  use it as a secure-by-design checklist source.

## reject

- Do not manage CoAgent with one productivity number such as tasks closed,
  commits made, or hours spent.
- Do not let backlogs become a dumping ground that creates false obligation.
  Old ideas should earn renewed attention by returning as shaped, relevant
  pitches.
- Do not let psychological safety become lack of accountability. Safety means
  surfacing risk early; accountability means integrating and resolving it.
- Do not apply heavy discovery ceremonies to clear, low-risk tasks.
- Do not treat chaotic incidents as normal tasks. Stabilize first, then analyze.

## unknowns

- The practical CoAgent time-box/appetite scale is open: minutes, hours, or
  task-complexity-dependent budgets.
- The minimum useful complexity classifier should be tested on real MoSim
  tasks before making it mandatory everywhere.
- The right source of strategy objectives is still the user's MoSim roadmap;
  CoAgent should not invent product strategy without user review.
- How to measure agent psychological safety is unclear; the immediate proxy is
  whether workers report uncertainty, contradictions, and blockers early.

## required_patch

- Add this gap-analysis audit.
- Update the technical-enterprise operating model with the newly identified
  missing management mechanisms.
- No runtime, automation, or task-schema implementation in this pass.

## verification

```bash
python3 CoAgent/learning/learning_indexer.py validate --strict
python3 CoAgent/learning/learning_indexer.py coverage --strict
python3 CoAgent/doctor/check_design_gate.py
```

## next_trigger

- Before adding task-start templates, strategy alignment checks, productivity
  metrics, complexity classification, or secure-development lifecycle gates.
- Before letting long tasks run without appetite and circuit-breaker fields.
