# CoAgent Doctor

`coagent_doctor.py` is the project-local health check for CoAgent.

It verifies the minimum recoverability surface before starting or resuming
long-running multi-conversation work:

- required CoAgent files exist,
- department thread registry is usable,
- registered department thread ids have matching local WSL Codex rollout files,
- reference index validates,
- learning audit records validate,
- CoAgent preflight passes,
- CoAgent preflight policy smoke tests pass,
- runtime and transport conversation graph smoke tests pass,
- fenced memory context and context-pack injection smoke test passes,
- automation guardrail smoke tests pass,
- transport adapter smoke tests pass,
- protocol compliance smoke tests pass,
- goal alignment smoke tests pass,
- automation dispatch planning smoke tests pass,
- runtime active queue is empty or contains only the explicitly allowed current
  implementation task,
- daily automation can build dispatch plans,
- knowledge index can build and search.

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

This tool is read-mostly. It may rebuild ignored indexes under `Results/`, but
it does not mutate Codex App internals, hidden session databases, or external
paths.
