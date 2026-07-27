# CoAgent Doctor

`coagent_doctor.py` is the project-local health check for CoAgent.

Default mode is `quick`. Use `--mode full` when a human-review checkpoint needs
the standard executable smoke suite. Add `--include-heavy` only when the
checkpoint specifically needs slower packaging or split-Git integration smoke
tests.

It verifies the minimum recoverability surface before starting or resuming
long-running multi-conversation work:

- required CoAgent files exist,
- department thread registry is usable,
- registered department thread ids have matching local WSL Codex rollout files,
- reference index validates,
- learning audit records validate,
- CoAgent preflight passes,
- CoAgent runtime output ignore rules cover local review/runtime artifacts,
- CoAgent Git workspace preflight detects index locks, staged runtime outputs,
  staged reference-tree batches, and broad staged sets,
- runtime SQLite events and JSONL event stream are auditable for recovery,
- runtime CLI output redacts claim tokens and other sensitive fields by
  default,
- runtime active queue is empty or contains only the explicitly allowed current
  implementation task,
- daily automation can build dispatch plans,
- knowledge index can build and search.

Full mode additionally runs the policy, graph, memory, context, automation,
runtime event audit, transport, result-router, gateway, review queue and
closeout verification, protocol, lifecycle, bootstrap, dispatch-plan,
blocker-packet, evidence refresh-command, evidence-manifest, and status-export
smoke tests. `--include-heavy` adds the slower split-Git dry-run/apply-plan and
review-package smoke tests.

Run:

```bash
python3 CoAgent/doctor/coagent_doctor.py
```

Validate only the current design approval gate:

```bash
python3 CoAgent/doctor/check_design_gate.py
```

This prints the current decision status, whether implementation is allowed,
the user review entry, the durable decision record, copyable decision
templates, and the next action.

For machine-readable output:

```bash
python3 CoAgent/doctor/coagent_doctor.py --json --output Results/coagent_doctor/latest.json
```

For the full suite:

```bash
python3 CoAgent/doctor/coagent_doctor.py --mode full --json --output Results/coagent_doctor/latest_full.json
```

For the slower extended suite:

```bash
python3 CoAgent/doctor/coagent_doctor.py --mode full --include-heavy --json --output Results/coagent_doctor/latest_full_heavy.json
```

Each check records `elapsed_seconds`. If a long-running checkpoint times out,
inspect the last JSON report or rerun full mode to identify the slow check.

This tool is read-mostly. It may rebuild ignored indexes under `Results/`, but
it does not mutate Codex App internals, hidden session databases, or external
paths.
