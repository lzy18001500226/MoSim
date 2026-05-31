# CoAgent Automation

## Purpose

This directory contains project-owned recurring automation definitions and a
minimal local runner.

The goal is not to replace Codex App automation UI.
The goal is to make recurring MoSim tasks durable and reproducible inside the
project.

## Current Components

| File | Purpose |
|---|---|
| `automation_tasks.json` | recurring automation definitions |
| `worker_policy.json` | lock TTL and concurrency limits for recoverable worker starts |
| `automation_runner.py` | local CLI to list automations and enqueue due tasks into CoAgent runtime |
| `guardrails.py` | lock, tool-scope, project-scope, prompt-injection, and review-gate checks for automation starts |

## Current Scope

Current runner supports:

- listing registered automations,
- filtering due automations by cadence,
- creating CoAgent runtime tasks from automation definitions.
- dry-run planning of transport dispatch for due automations,
- explicit enqueue plus dispatch-plan generation when a real runtime task is needed.
- explicit staged transport start for due automations when a real run is intended and guardrails pass.
- worker lock status reporting with stale-lock and concurrency policy.

Dry-run dispatch planning uses the same `CoAgent/transport/` adapter interface
as real dispatch. This keeps command construction and shadow Codex state
preparation out of the automation runner.

Current bundled automations include:

- agent architecture learning routed to `ExternalIntelligenceAgent`
- docs/workflow improvement routed to `KnowledgeSecretaryAgent`
- reference repo refresh routed to `ExternalIntelligenceAgent`
- knowledge index refresh routed to `ContextMemoryAgent`
- safety scan routed to `SafetyComplianceAgent`
- git cadence routed to `DevOpsReleaseAgent`

It does not yet:

- call Codex App automation APIs,
- schedule wall-clock wakeups,
- deduplicate across machines,
- dispatch tasks into conversations automatically; current transport bridge
  stops at dry-run planning or explicit staged dispatch.

## Guardrails

Every automation definition must declare:

- `tool_scope.allowed`
- `tool_scope.denied`
- `requires_human_review`

`plan-due-dispatch` reports guardrail status but does not acquire locks.
`start-due-dispatch` acquires an automation lock and refuses to launch an
unattended run when prompt-injection text, out-of-project paths, unknown tools,
duplicate locks, or missing review confirmation are detected.

`worker_policy.json` keeps unattended execution conservative:

- stale locks are reported after `lock_ttl_seconds`,
- only a small number of active automation locks may exist globally,
- each automation id has a per-id active run limit,
- each department has a per-department active run limit.

Stale locks are warning evidence, not automatic deletion. A human or a recovery
workflow should inspect and explicitly release or reclaim them.

Smoke tests must not mutate the live lock directory
`Results/coagent_automation/locks`. Use an isolated temporary lock directory
when testing guardrail concurrency; doctor and status-export checks can run in
parallel during long tasks.

High-impact automations that write docs, workflow state, reference indexes, or
Git planning records should keep `requires_human_review: true`. Low-risk index
refreshes that write only ignored `Results/` paths may set it to `false`.

## Current Commands

```bash
python CoAgent/automation/automation_runner.py list
python CoAgent/automation/automation_runner.py due --cadence daily
python CoAgent/automation/automation_runner.py guard-due --cadence daily
python CoAgent/automation/automation_runner.py worker-status
python CoAgent/automation/automation_runner.py enqueue-due --cadence daily
python CoAgent/automation/automation_runner.py plan-due-dispatch --cadence daily
python CoAgent/automation/automation_runner.py enqueue-and-plan-due --cadence daily
python CoAgent/automation/automation_runner.py start-due-dispatch --cadence daily --reviewed
```
