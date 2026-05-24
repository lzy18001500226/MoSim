# External Repository Audit Workflow

> Use this before importing, adapting, or relying on a third-party repository.

## Goal

Decide whether a repository is useful for this project, and exactly what should
be reused:

- editable Unreal scene assets;
- simulator architecture;
- planning/control/perception algorithms;
- skills/workflow patterns;
- test or benchmark structure;
- documentation only.

## Audit Steps

1. Confirm path is inside the project, usually under `references/` or `Docs/Skills/`.
2. Run the local scanner:

```bash
python3 scripts/reference/audit_external_repo.py references/AirSim/spear --output results/audits/spear_audit.json --markdown results/audits/spear_audit.md
```

3. Read project metadata:
   - `README*`
   - `LICENSE*`
   - `.uproject`
   - `package.xml`, `CMakeLists.txt`, `pyproject.toml`, `package.json`
   - `Docs/`, `examples/`, `issues` notes if available locally.
4. Classify usefulness:

```text
directly runnable
editable asset source
algorithm reference
workflow reference
agent-runtime-reference
skill-packaging-reference
workflow-pattern-reference
spec-coverage-reference
documentation only
not useful
```

5. Record migration risk:
   - engine version mismatch;
   - binary-only dependency;
   - missing plugin source;
   - files over GitHub 100 MB;
   - license or attribution requirement;
   - hard-coded simulator assumptions.

## Output

Each audit should produce:

```text
repo purpose:
usable parts:
not usable parts:
editable assets:
runtime-only assets:
build/run entry:
license:
large-file risk:
integration recommendation:
next validation:
```

For agent, skill, or workflow-runtime repositories, use the three-pass audit
structure from `Docs/Workflows/agent_orchestration.md`:

```text
PASS 1 inventory:
PASS 2 reusable patterns:
PASS 3 comparison with project docs:
required doc patches:
do not adopt:
risks:
```

If the user explicitly asks for `学习+更新文档三遍`, `三轮学习并更新`,
`learn and update docs three times`, or an equivalent phrase, the audit must be
three separate learn-and-update rounds:

```text
ROUND 1 inventory/relevance learning:
  read source identity, capability inventory, licenses, and top-level docs
  update durable source-of-truth routing and do-not-adopt guardrails

ROUND 2 orchestration/WAL/delegation learning:
  read workflow, event, run-log, sub-agent, and approval patterns
  update templates, checklists, delegation contracts, and event schemas

ROUND 3 validation/coverage/resume learning:
  read test strategy, coverage maps, doctor/preflight, resume, stale-state docs,
  reviewer workflows, and pollution-prevention guidance
  update consistency rules, coverage gates, stale-ledger recovery guidance,
  reviewer lanes, and rejected-pattern lists
```

Each round must produce a doc patch before the next round starts. A single
"read everything, then patch once" pass does not satisfy this request.

For official-tooling and agent-workflow audits, classify every finding before
promoting it into project rules:

```text
confidence:
  official_verified | local_reference | third_party_unverified | do_not_adopt
schema_verified:
  true | false | unknown
official_source_url:
unsupported_claims:
```

Do not promote third-party or local-reference schemas into `AGENTS.md` or
runtime config until they are verified against official docs for the installed
tool version. If Claude Code, Codex, opencode, or another agent tool uses a
similar term with different semantics, name the provider explicitly.

Before closing the audit, perform a consistency pass:

```text
round coverage:
  round 1 source paths + changed docs
  round 2 source paths + changed docs
  round 3 source paths + changed docs

source-to-doc coverage:
  source evidence path
  adopted project rule or workflow text
  validation/manual review gate
  rejected pattern and reason

stale-ledger recovery:
  matching task objective
  terminal event or explicit blocker
  no pending approval/tool state
  next safe action recorded
```

If a prior ledger row or old audit says the work is done but lacks this
coverage, treat it as prior evidence only and run the missing round.

The audit must explicitly list contradictions with current project docs and
the exact files that should be patched. Do not import full external runtimes
when the useful output is only a workflow or validation pattern.

Round 3 must add a validation coverage table to the audit notes or final report:

```text
source path:
source finding:
project rule added or confirmed:
target doc:
fresh verification:
future drift detector:
not adopted:
```

Treat "fresh verification" as a current-turn check, not an old success memory.
For documentation-only audits, use scoped source re-read, target diff review,
path/link sanity checks, and `git diff --check`. For executable claims, require
the relevant test/build/MCP check from the owning workflow.

For reviewer-agent patterns, keep review as a separate read-only lane unless a
new write set is assigned:

```text
spec/compliance review:
  source coverage, requested scope, forbidden paths, acceptance criteria
quality/risk review:
  correctness, regression, secrets/large files, reproducibility, recovery
```

Reviewer findings must be evaluated against project rules before adoption.
Reject feedback that expands scope, imports unapproved runtimes, or conflicts
with the current permission boundary.

For documentation pollution prevention, explicitly check:

```text
no copied tool schemas or provider configs unless verified:
no secret-bearing logs or full prompts:
no raw SSE/UI/PTY streams pasted as durable docs:
no duplicated policy text that belongs in AGENTS.md or a workflow:
no external runtime setup steps promoted as project requirements:
```

For `Docs/Skills/okwinds/**`, treat the useful source of truth as local reference
material for workflow process, not an execution dependency:

```text
Agently:
  useful for structured output, observable actions, TriggerFlow, pause/resume,
  and task-graph concepts
skills-runtime-sdk:
  useful for Skills-first organization, approvals, sandbox vocabulary,
  WAL/events, coverage maps, and offline validation patterns
capability-runtime:
  useful for narrow public runtime surface, NodeReport evidence, host
  wait/resume, service-facade, and capability coverage mapping
agentskills:
  useful for skill packaging/specification and skill validation concepts
miscellany:
  useful as a catalog of local skill patterns and safety warnings
wkteam-api-sdk:
  mostly not relevant to quadrotor control; borrow only spec/TDD/coverage
  discipline if needed
```

Do not adopt from OKWinds by default:

```text
provider configuration or API credentials
Studio/web UI stack
hosted runtime service
third-party API client code
OpenSkills installation flow
runtime dependency tree
external approval/sandbox implementation
Agently/capability-runtime as project runtime
Loopback driver or self-repeating Codex sessions as default workflow
skill_exec/actions module as a project automation requirement
raw NodeReport/WAL schemas as normative without project adaptation
```

For `Docs/Skills/Agent/**`, treat curated skills and subagent catalogs as
third-party workflow references:

```text
awesome-codex-subagents:
  useful for role taxonomy, read-only reviewer posture, task-distributor and
  coordinator contracts, and explicit Codex delegation examples
awesome-codex-skills:
  useful for concise skill design, plan shape, PR/CI triage flow, and tool
  schema verification habits
superpowers:
  useful for evidence-before-claims, two-lane review, plan execution discipline,
  and stop-contract thinking
```

Do not adopt from `Docs/Skills/Agent/**` by default:

```text
global `~/.codex/agents` installation changes
unverified `.toml` config keys as project policy
Claude-specific hooks, commands, or worktree cleanup behavior
Composio/Datadog/Jira/GitHub credentialed workflows
automatic PR comment posting or CI mutation
skill metadata/frontmatter beyond what the current Codex runtime supports
```

Do not commit broad imported trees until the Git/quality stream verifies
large-file and nested-repository risks.
