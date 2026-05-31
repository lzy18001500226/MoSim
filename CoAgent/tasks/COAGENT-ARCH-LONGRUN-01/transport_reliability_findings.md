# COAGENT-ARCH-LONGRUN-01 Transport Reliability Findings

Date: 2026-05-30
Status: active finding

## Observed Runs

### RuntimePlatformAgent

Task:

```text
COAGENT-ARCH-LONGRUN-01-RUNTIME-01
```

Result:

```text
blocked_no_result
```

The transport resumed the visible department conversation, copied the packet,
and the worker read multiple evidence files. It did not write the expected
result packet within the 60 second budget. The identified process was cleaned
up.

Evidence:

- `Results/coagent_transport/runs/COAGENT-ARCH-LONGRUN-01-RUNTIME-01.stdout.log`
- `Results/coagent_transport/runs/COAGENT-ARCH-LONGRUN-01-RUNTIME-01.stderr.log`
- runtime task state `COAGENT-ARCH-LONGRUN-01-RUNTIME-01`

Observed noise:

- remote plugin catalog sync warning;
- curated plugin Git clone timeout;
- plugin loader warning for missing `codex-session-tools@local`;
- state DB discrepancy slow path;
- MCP file operation reached write preparation but no packet appeared before
  timeout.

### VerificationAgent

Task:

```text
COAGENT-ARCH-LONGRUN-01-VERIFY-01
```

Result:

```text
result_written_but_schema_invalid_then_repaired
```

The transport eventually produced a result file, but the worker wrote nested
YAML and an unsupported canonical status. The current simple router parsed it
incorrectly and rejected it. MainAgent converted the substance into a
router-compatible flat result packet and imported it.

Evidence:

- `Results/agent_packets/COAGENT-ARCH-LONGRUN-01-VERIFY-01.yaml`
- `Results/agent_packets/reviews/COAGENT-ARCH-LONGRUN-01-VERIFY-01.review.json`
- `Results/coagent_transport/runs/COAGENT-ARCH-LONGRUN-01-VERIFY-01.stderr.log`

## Design Conclusions

1. Visible conversation transport is real but not yet reliable enough to be a
   default unattended execution mechanism.
2. A task packet saying "write required fields" is not strong enough; workers
   need an exact router-compatible template.
3. The 60 second rule is useful as a circuit breaker. It exposed startup noise
   and schema drift quickly.
4. Timeout cleanup must close dispatch edges and mark child tasks blocked.
5. Result repair is acceptable for design experiments, but implementation must
   reduce repair by validating or templating the packet before dispatch.

## Required Runtime Design Response

- keep automatic conversation dispatch gated;
- add a lean dispatch mode or configuration that avoids remote plugin sync when
  possible;
- keep startup logs and stdout/stderr as first-class evidence;
- create timeout blocker packets automatically;
- add packet template validation before dispatch;
- add post-dispatch reconcile that distinguishes:
  - no result file;
  - invalid result packet;
  - valid packet requiring review;
  - accepted packet.

## Not Proved

These runs do not prove:

- automatic conversation creation;
- app-server transport;
- unattended long-running execution;
- remote plugin reliability;
- nested YAML result packet support.
