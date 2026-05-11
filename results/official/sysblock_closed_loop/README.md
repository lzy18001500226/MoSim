# Official Sysblock Closed-Loop Evidence

Updated: 2026-05-11

This directory records the batch-level evidence for the active official AWFF Sysblock closed-loop validation.

The 2026-05-11 rerun used one reusable Sysplorer MCP wrapper process:

```bash
python3 scripts/run_mworks_batch.py --reuse-mcp-process --continue-on-failure \
  scenarios/official/example1_awff_sysblock.yaml \
  scenarios/official/example2_awff_sysblock_helix_tuned.yaml \
  scenarios/official/example3_awff_sysblock.yaml
```

Batch initialization log:

```text
results/official/sysblock_closed_loop/logs/mcp_reuse_batch_official_sysblock_20260511.jsonl
```

Per-scenario evidence bundles:

| Scenario | Model | Duration | Quality | RMSE |
|---|---|---:|---|---:|
| Example1 step | `QuadrotorExperiments.Example1AWFFSysblockClosedLoop` | 50 s | pass | 0.2662166046 |
| Example2 helix | `QuadrotorExperiments.Example2HelixTunedAWFFSysblockClosedLoop` | 50 s | pass | 0.4748504939 |
| Example3 figure8 | `QuadrotorExperiments.Example3AWFFSysblockClosedLoop` | 120 s | pass | 0.1666690665 |

The inactive `official_example2_awff_sysblock` result is retained as historical diagnostic evidence; the active official matrix uses `official_example2_awff_sysblock_helix_tuned`.
