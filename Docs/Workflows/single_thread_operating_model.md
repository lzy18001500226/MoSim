# Coordinating-Thread Operating Model

> Current operating rule for MoSim work. This is a practical work loop, not a
> second architecture document or a historical dispatch handbook.

## 1. Ownership

One coordinating Codex thread owns task scope, engineering priority,
integration, user communication, and final claims. Official temporary
subagents may handle independent bounded research, inspection, or verification;
the coordinating thread still owns integration and may not use them as durable
departments, hidden acceptance owners, or parallel writers of shared paths.

Former visible-thread dispatch, patrol automation, R1/R2/R3 departments, and
task-ledger routing are historical only. Their records belong in `Docs/Cache/`.

## 2. Normal Work Loop

```text
user objective
  -> local goal and owner layer
  -> smallest relevant source/design/workflow/result context
  -> one bounded edit, check, or runtime gate
  -> evidence or precise blocker
  -> update the owner document only when a reusable fact changed
```

The current board selects the task. Topic workflows explain how to act after a
task is selected; they do not create priority or authorize unrelated work.

## 3. Avoid Process Inflation

Do not turn a straightforward task into a chain of new plans, smoke tests,
packages, scripts, or progress documents.

Before creating any new artifact, identify all three:

1. its reader or executable consumer;
2. the specific decision, contract, or evidence gap it owns;
3. why an existing owner file, model, profile, script, test, or result path
   cannot own it.

If a focused inspection produces no new factual finding, stop widening the
search. Choose one of: a small observable probe, targeted source/official
research, an existing recovery action, or the next independent task. Do not
repeat the same diagnosis or add paperwork to appear active.

New experiments use the canonical model root, existing configuration/profile
layout, and `Results/` evidence layout. A single experiment never justifies a
second top-level Modelica package or a new project-wide workflow.

## 4. Quality And Stop Rules

- Use the narrowest relevant check before broad changes.
- Separate source/static, GUI/review, and live-runtime claims.
- Stop for architecture changes, unapproved broad deletion/moves, unknown
  license/login/authorization state, or a required live action outside scope.
- For a recoverable tool/UI issue, try the documented local recovery first;
  report a blocker only after the bounded recovery path has produced evidence.
- Record durable evidence in `Results/`, not in a growing operations narrative.

## 5. Completion

For a changed project path: inspect the scoped diff, run the relevant checks,
stage exact files, commit, push, and verify publication. A documentation cleanup
does not imply runtime, controller, planner, or simulation acceptance.
