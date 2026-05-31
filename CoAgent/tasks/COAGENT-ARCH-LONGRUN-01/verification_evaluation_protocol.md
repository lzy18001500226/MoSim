# COAGENT-ARCH-LONGRUN-01 Verification And Evaluation Protocol

Date: 2026-05-30
Status: phase 2 draft

## Purpose

Define how CoAgent verifies both:

1. the product/task output is correct;
2. the multi-agent operating process did not drift, waste time, or hide risk.

## Evidence Classes

| Evidence Class | Question Answered |
|---|---|
| source evidence | what files/docs/tools were actually inspected |
| execution evidence | what commands/tools/simulations ran |
| product evidence | whether the delivered artifact meets task acceptance |
| process evidence | whether the task team operated correctly |
| review evidence | who accepted/rejected the result and why |
| residual-risk evidence | what remains uncertain |

## Architecture Decision Review

A design decision can be marked accepted only if it has:

- problem statement;
- considered alternatives;
- selected rule;
- reason;
- affected files/protocols;
- known risks;
- next experiment if uncertain.

If evidence is weak, the decision state must be:

- `needs_experiment`;
- `needs_user_decision`;
- `deferred_gated`.

## Product Stress-Test Review

### PX4 Parameter Identification

Verify:

- log sufficiency was checked first;
- identifiable and non-identifiable parameters are separated;
- method choice matches available data;
- estimator uncertainty is recorded;
- simulation mapping is explicit;
- residual tuning requirement is not hidden;
- MWORKS/Sysplorer evidence is separated from offline demos.

### UE Scene Truth / RflySim-Like Simulation

Verify:

- scene source is known;
- UE/MCP capability is proved or blocked;
- map truth is not replaced by screenshots;
- collision/navmesh/occupancy coordinates are defined;
- planning/navigation consumers receive valid artifacts;
- manual visual review points are explicit;
- Fab/license/large-asset issues are gated.

## Process Metrics

| Metric | Meaning | Red Flag |
|---|---|---|
| critical_path_time | time spent on the slowest necessary path | no owner or no checkpoint |
| blocked_time | time blocked on user/tool/license/Git | repeated retries without blocker |
| fake_parallelism_count | spawned conversations with no independent output | activity without evidence |
| serial_collapse_count | all work silently falls back to one lane | departments exist but do not function |
| handoff_failure_count | packet/context/result missing required fields | worker asks for hidden context |
| context_refresh_latency | time to update affected conversations after decision | stale assumptions continue |
| rework_count | work redone due to bad assumption or drift | late review catches basic scope error |
| review_escape_count | issue found after acceptance | weak review gate |
| closeout_latency | accepted work not integrated or documented | task appears done but cannot be reused |

## Drift Detection

Trigger `review_required` if:

- a worker cannot restate the canonical task goal;
- a result omits required evidence;
- research produces broad summaries without a decision table;
- implementation starts before sufficiency gate;
- a conversation keeps asking for context already in the pack;
- a worker changes task scope locally;
- three attempts hit the same blocker.

## Minimal Closed-Loop Acceptance

For a CoAgent architecture proof to count, it must show:

1. canonical task created;
2. context pack generated;
3. at least one scoped or department conversation receives a packet;
4. worker returns result packet;
5. result is imported or reviewed;
6. context delta or decision update is recorded;
7. closeout state is visible.

If a proof only opens a conversation or writes a prompt, it does not count.
