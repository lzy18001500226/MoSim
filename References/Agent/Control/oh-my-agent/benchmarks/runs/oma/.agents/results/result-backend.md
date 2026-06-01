# System Engineer Review: oma-observability (2026-04-21)

**Status:** MINOR FIXES
**Reviewer role:** System Engineer

---

## Findings

### 1. NTP / Clock Skew Discipline

Mostly correct. `standards.md §6` correctly names chrony/NTP for Linux VMs and delegates clock inheritance to the host in Kubernetes. The < 100 ms drift tolerance is a standard practitioner threshold. GCP note says "inherit host clock" but does not note that GCP VMs also run `chronyd` by default against Google's internal time source — the verification command `timedatectl show` only reports whether the daemon is active, not offset quality. Azure entry references `time.windows.com` alongside Hyper-V IC timesync; in practice Hyper-V IC timesync takes precedence and NTP is a fallback for Linux guests without Hyper-V integration tools — the wording creates a false impression of two peer sources.

Issue 1: GCP verification command should be `chronyc sources -v`, not `timedatectl show`.
Issue 2: Azure entry conflates Hyper-V IC timesync with NTP; clarify that IC timesync is primary and NTP is the fallback for non-Hyper-V Linux guests.

### 2. hostmetrics Receiver Config

Correct for current contrib receiver (0.100+). `root_path: /hostfs` is the correct field name. Scrapers listed match available scrapers. The `process` scraper in `meta-observability.md §A5` uses `names` + `match_type: regexp` — valid syntax for hostmetricsreceiver >= 0.91. No issues.

### 3. Cardinality Guardrails

Rules in `meta-observability.md §C` are sound. The forbidden-label table is accurate and `replace_pattern` OTTL syntax is correct for Collector 0.95+. The per-service 5000-series budget is presented as a universal constant. High-throughput services legitimately run 20 k–100 k series; the number should be labeled a starting example, not a normative limit.

Issue 3: Document the 5000-series budget as a configurable example, not a hardcoded normative constant.

### 4. Retention Matrix

Numbers in `meta-observability.md §D1` are realistic. Metrics 15d/90d/2y aligns with Thanos/Mimir downsampling. Audit log 7y WORM is correct for SOX/financial; GDPR recital 65 citation is accurate. Traces 30d sampled is standard. Profiles 14d with no aggregation standard — correctly noted.

Issue 4 (minor): The Loki example in `§D3` shows both a `table_manager` block and a `compactor` block. `table_manager` was removed in Loki 3.x. Add a version annotation to avoid confusion for teams on Loki 3.

### 5. Continuous Profiling — OTEP 0239 Status

`profiles.md §5` marks OTEP 0239 as "alpha / in active development (2026-Q2)" and warns against building SLOs on it. `standards.md §3` lists it under Experimental tier. This is accurate; the wire format is not yet RC. Status is correctly marked.

### 6. eBPF Tooling

`L4-transport.md §5.1` tool table has one factual inconsistency:

Issue 5: Beyla is listed as "CNCF Sandbox" in `L4-transport.md §5.1`, but `profiles.md` line 54 correctly lists it as "CNCF Incubating". Beyla was promoted to Incubating in late 2024. The L4-transport file must be updated to be consistent.

Pixie Sandbox and Parca Sandbox are correct. Capability requirements (CAP_BPF, kernel >= 5.8) and GKE Autopilot/EKS Fargate constraints are accurate.

### 7. Verdict

**MINOR FIXES** — 5 issues, no structural rework required.

| # | Severity | File | Fix |
|---|----------|------|-----|
| 1 | MEDIUM | `standards.md §6` | GCP: change `timedatectl show` to `chronyc sources -v` |
| 2 | MEDIUM | `standards.md §6` | Azure: clarify Hyper-V IC timesync is primary, NTP is fallback |
| 3 | LOW | `meta-observability.md §C4` | Label 5000-series budget as a configurable example |
| 4 | LOW | `meta-observability.md §D3` | Add Loki version annotation — `table_manager` removed in Loki 3.x |
| 5 | MEDIUM | `layers/L4-transport.md §5.1` | Update Beyla CNCF status from Sandbox to Incubating |

## Acceptance Criteria

- [x] NTP/clock skew discipline reviewed — 2 issues found
- [x] hostmetrics receiver config verified — correct
- [x] Cardinality guardrails reviewed — 1 issue found
- [x] Retention matrix reviewed — 1 minor issue found
- [x] OTEP 0239 status reviewed — correctly marked alpha/experimental
- [x] eBPF tooling reviewed — 1 cross-file inconsistency found
- [x] Verdict issued: MINOR FIXES

---

# Data Pipeline Review — oma-observability (2026-04-21)

## Status: COMPLETE

## Summary

Data Pipeline Engineer review of three oma-observability spec files. Verdict: **MINOR FIXES** — no structural rework required, but two HIGH-severity issues must be resolved before the spec is considered production-safe.

## Files Reviewed (read-only)

- `/Users/gracefullight/workspace/oh-my-agent/.agents/skills/oma-observability/resources/signals/cost.md`
- `/Users/gracefullight/workspace/oh-my-agent/.agents/skills/oma-observability/resources/signals/traces.md` (messaging section)
- `/Users/gracefullight/workspace/oh-my-agent/.agents/skills/oma-observability/resources/boundaries/multi-tenant.md` (residency section)

## Findings

| # | Severity | File | Section | Issue |
|---|----------|------|---------|-------|
| 1 | MEDIUM | cost.md | §5 Unit Economics | Per-tenant PromQL joins `opencost_workload_cost_total` with `kube_namespace_labels` using `on(namespace) group_left(tenant_id)`. This requires `kube-state-metrics` to expose the custom `tenant_id` label via `--metric-labels-allowlist`. This dependency is undocumented; the join silently returns no data if the label is not allowlisted. |
| 2 | LOW | traces.md | §5 messaging.* table | `messaging.operation = "ack"` is not a valid enum value in OTel semconv 1.27.0. Valid values are `publish`, `receive`, `deliver`, `settle`. Replace `"ack"` with `"settle"` for Kafka commit acknowledgment. |
| 3 | MEDIUM | traces.md | §5.1 Kafka-Specific | No alerting threshold guidance for primary topic consumer lag. Only DLQ lag > 0 is specified. Production teams need a pattern for primary consumption topics (e.g., alert when lag exceeds N messages for M minutes). |
| 4 | HIGH | multi-tenant.md | §8 Data Residency | `tenant.region` routing is specified at the ingress gateway but the source of truth for this value is undefined. If `tenant.region` is derived from client-supplied baggage or a JWT claim without server-side validation, a misconfigured or adversarial client can self-assign a non-EU/KR region to bypass GDPR Chapter V and PIPA residency controls. The spec must state that `tenant.region` MUST be resolved from an internal tenant registry, never from client-supplied input. |
| 5 | HIGH | cost.md | §6 LLM Cost | `genai.cost.total_usd` uses the `genai.*` namespace, but OTel semconv uses `gen_ai.*` (with underscore after `gen`). OTel-native tooling and auto-instrumentation agents will not recognize `genai.cost.total_usd`. Additionally, the attribute table in §6 groups it with official `gen_ai.usage.*` attributes without a clear "custom extension" label in the table itself (prose notes "vendor-specific extension" but the table does not). Correct the namespace to `gen_ai.cost.total_usd` if tracking the upstream proposal, or use a custom prefix and mark it explicitly as non-OTel in the table. |

## Acceptance Criteria Checklist

- [x] OpenCost metric surface accurate — metrics match official OpenCost Prometheus exposition
- [x] FOCUS Spec 1.0 correctly scoped to cross-cloud billing column unification
- [x] Kafka PRODUCER/CONSUMER SpanKind with span links (not parent-child) — correct
- [x] DLQ trace continuity pattern correct — preserve original traceparent; no new trace_id on redrive
- [x] Kafka consumer lag correctly delegated to metrics signal (not trace attribute)
- [x] Data residency routing topology (EU/KR edge collectors, no cross-region export) is legally grounded
- [x] GDPR Art. 17 erasure on offboarding included
- [ ] kube_namespace_labels join dependency on kube-state-metrics label allowlist documented (Finding #1)
- [ ] messaging.operation "ack" corrected to "settle" (Finding #2)
- [ ] Primary topic consumer lag alerting threshold guidance added (Finding #3)
- [ ] tenant.region source of truth restricted to internal registry, not client-supplied input (Finding #4 — HIGH)
- [ ] genai.cost.total_usd namespace corrected to gen_ai.* and marked as custom extension in the attribute table (Finding #5 — HIGH)

## Verdict

**MINOR FIXES** — Two HIGH findings (#4, #5) must be addressed before this spec drives production implementations.

---

# Backend Result: multi-tenant.md (oma-observability skill, task E1)

## Status: completed

## Summary

Wrote the `resources/boundaries/multi-tenant.md` skill resource for the `oma-observability` skill. The file covers all 13 required sections: scope, OTel attribute conventions, 4-tier isolation strategy, tenant ID propagation, per-tenant sampling, per-tenant retention, cost attribution, data residency (GDPR/PIPA), onboarding/offboarding, dashboard isolation, noisy neighbor protection, matrix cells, and anti-patterns.

## Files Changed

- `/Users/gracefullight/workspace/oh-my-agent/.agents/skills/oma-observability/resources/boundaries/multi-tenant.md` — created (305 lines)

## Acceptance Criteria Checklist (plan task E1)

- [x] 4-tier isolation (soft / routing / dedicated-collector / dedicated-backend) — Section 3 table
- [x] Per-tenant sampling — Section 5 with `tail_sampling` YAML snippets for enterprise/pro/free tiers
- [x] Per-tenant retention — Section 6 table (Enterprise: 90d/1y/3y; Pro: 30d/90d; Free: 7d/30d)
- [x] Cost attribution (cross-ref cost.md) — Section 7 with OpenCost pod label example and cardinality cap
- [x] Residency (GDPR/PIPA) routing — Section 8 with per-region topology table and routing rules
- [x] 240-350 line target — 305 lines
- [x] Tables for isolation tiers, retention tiers, residency routing, dashboard isolation, noisy neighbor controls
- [x] YAML snippets for `tail_sampling` per-tenant policies
- [x] Cross-refs using `../` prefix throughout
- [x] `routing_connector` alpha caveat cross-referenced to `../transport/sampling-recipes.md §4`
- [x] Baggage PII trust-boundary warning with W3C Baggage spec citation
- [x] GDPR Art. 17 right to erasure in offboarding section
- [x] Anti-patterns section with 5 entries (candidates for `../anti-patterns.md §Multi-Tenant`)
- [x] Matrix cells section (Section 12) with L3/L7 multi-tenant coverage
- [x] No future oma-X references
- [x] Content in English, no emojis

---

# Backend Result: cross-application.md (oma-observability skill, task E2)

## Status: DONE

## Summary

Wrote `/Users/gracefullight/workspace/oh-my-agent/.agents/skills/oma-observability/resources/boundaries/cross-application.md` — the cross-application boundary reference file for the `oma-observability` skill. 325 lines, all 12 sections, propagator matrix table, 4-layer correlation table, baggage PII rules, DDD `service.namespace` guidance, and cross-refs using `../` prefix. Absorbed content from the former `propagators.md` and `multi-domain.md` per design decision D3.

## Files Changed

- `/Users/gracefullight/workspace/oh-my-agent/.agents/skills/oma-observability/resources/boundaries/cross-application.md` — created (325 lines)

## Acceptance Criteria Checklist (Plan Task E2)

- [x] 4-layer correlation model: `trace_id` / `request_id` / `causation_id` / baggage with propagation, cardinality, and purpose columns (Section 2)
- [x] Propagator matrix: W3C / B3 / AWS X-Ray / GCP / Azure / Datadog / Cloudflare / Istio+Envoy / Linkerd — all 9 ecosystems with headers and normalization notes (Section 3)
- [x] Multi-propagator ingress strategy with extract/inject order (Section 3.1)
- [x] DDD bounded context via `service.namespace` — examples, config YAML, anti-pattern (Section 5)
- [x] Baggage PII rules: W3C §Security citation, allowed vs prohibited table, trust-boundary filter rule, enforcement point (Section 4)
- [x] Cross-cloud trace continuity table (AWS / GCP / Azure / Jaeger W3C support status) (Section 6)
- [x] request_id to trace_id integration flow for customer support (Section 7)
- [x] Idempotency and event-driven trace lineage: HTTP pattern, Kafka pattern, DLQ replay (Section 8)
- [x] Trust boundary patterns table (Section 9)
- [x] Context inheritance in non-interactive sessions via `TRACEPARENT` env var (Section 10)
- [x] Matrix.md cells for cross-application boundary row (Section 11)
- [x] 6 anti-patterns for `../anti-patterns.md §Cross-application` (Section 12)
- [x] All cross-refs use `../` prefix
- [x] No future oma-X references
- [x] English content, 325 lines (target: 260-380)

---

# Backend Result: logs.md (oma-observability skill, task D2)

## Status: DONE

## Summary

Wrote `/Users/gracefullight/workspace/oh-my-agent/.agents/skills/oma-observability/resources/signals/logs.md` — the logs signal reference file for the `oma-observability` skill. 263 lines, all 13 required sections, JSON and YAML snippets, cross-refs using `../` prefix.

## Files Changed

- `/Users/gracefullight/workspace/oh-my-agent/.agents/skills/oma-observability/resources/signals/logs.md` — created (263 lines)

## Acceptance Criteria Checklist (Plan Task D2)

- [x] LogRecord data model — all 9 fields (Timestamp, ObservedTimestamp, SeverityText, SeverityNumber, Body, Attributes, TraceId, SpanId, Resource) with types and descriptions (Section 2)
- [x] Severity mapping — TRACE/DEBUG/INFO/WARN/ERROR/FATAL on 1–24 OTel normalized scale (Section 2)
- [x] OTLP logs exporter — gRPC :4317 / HTTP :4318/v1/logs (Section 2)
- [x] Structured logging with required fields — `timestamp`, `level`, `message`, `trace_id`, `span_id`, `service.name`, `service.version`, `deployment.environment` (Section 3)
- [x] JSON log format snippet (Section 3)
- [x] Metric correlation via shared labels (Section 3)
- [x] Events as LogRecords — `event.name` + `event.*`, use cases, distinction from metrics and logs (Section 4)
- [x] Events JSON snippet (Section 4)
- [x] systemd journal integration — `journaldreceiver` YAML, field mapping (_PID, _SYSTEMD_UNIT, MESSAGE, PRIORITY, _HOSTNAME), Kubernetes sources (Section 5)
- [x] Fluent Bit / OTel Collector options — comparison table with RAM, CNCF status, Fluentd deprecated (Section 6)
- [x] 2026 best practice topology: Fluent Bit DaemonSet → OTLP → OTel Collector gateway → backends (Section 6)
- [x] Trace ID injection rules — EVERY log line must carry trace_id + span_id; language table; verification rule (Section 7)
- [x] Log severity and sampling — tiered policy table, tail sampling cross-ref (Section 8)
- [x] Retention and compliance — operational/audit tiers, WORM, PII redaction at ingestion (Section 9)
- [x] OS-level log sources — journald, syslog, dmesg, auditd (Section 10)
- [x] Backends — Loki, Elasticsearch, OpenSearch, ClickHouse (Section 11)
- [x] Matrix.md cells for logs column — 10 cells across L3/L4/mesh/L7 (Section 12)
- [x] Anti-patterns — 5 items (A-L1 through A-L5) as candidates for anti-patterns.md (Section 13)
- [x] All cross-refs use `../` prefix
- [x] No future oma-X references
- [x] English content, 263 lines (target: 200–320)

---

# Backend Result: metrics.md (oma-observability skill, task D1)

## Status: DONE

## Summary

Wrote `/Users/gracefullight/workspace/oh-my-agent/.agents/skills/oma-observability/resources/signals/metrics.md` — the metrics signal reference file for the `oma-observability` skill. The file covers all 12 required sections with PromQL SLI snippets, OpenMetrics RFC 9416 snippet, YAML configuration examples, and cross-refs using `../` prefix.

## Files Changed

- `/Users/gracefullight/workspace/oh-my-agent/.agents/skills/oma-observability/resources/signals/metrics.md` — created (474 lines)

## Acceptance Criteria Checklist (Plan Task D1)

- [x] Counter / UpDownCounter / Gauge / Histogram / Summary instrument types with sync/async variants (Section 2)
- [x] Aggregation temporality: delta vs cumulative, `OTEL_EXPORTER_OTLP_METRICS_TEMPORALITY_PREFERENCE` (Section 2.6)
- [x] Prometheus exposition format: `# HELP` / `# TYPE` / metric lines, naming convention, label rules (Section 3)
- [x] OpenMetrics RFC 9416 snippet with `# EOF` terminator (Section 3.4)
- [x] Golden Signals, RED method, USE method with PromQL sketches (Section 4)
- [x] Availability SLI PromQL: `sum(rate(...{status=~"2..|3.."}[5m])) / sum(rate(...[5m]))` (Section 4.4)
- [x] Latency SLI PromQL: `histogram_quantile(0.99, ...)` (Section 4.4)
- [x] Healthcheck-to-metric wiring rule and anti-pattern (Section 4.5)
- [x] hostmetrics receiver: scraper YAML, 15 key metrics table, Node Exporter fallback (Section 5)
- [x] Kubernetes metric sources: kubeletstats, k8scluster, Prometheus operator + ServiceMonitor CRD (Section 6)
- [x] OTel SDK auto-instrumentation metrics and custom Meter API example (Section 7)
- [x] OpenCost metric surface: 6 key metrics, scrape config YAML (Section 8)
- [x] Cardinality budget: per-service alert PromQL, forbidden labels table, tenant top-N cap (Section 9)
- [x] Long-term storage backends: Prometheus, Thanos, Cortex, Grafana Mimir, VictoriaMetrics with CNCF status (Section 10)
- [x] Matrix.md cells for metrics column across all layers and boundaries (Section 11)
- [x] 6 anti-patterns for `../anti-patterns.md §Section B` (Section 12)
- [x] All cross-refs use `../` prefix (file is in `signals/`)
- [x] No future oma-X references
- [x] Content in English, no emojis

---

# Backend Result: intent-rules.md (oma-observability skill, task A5)

## Status: DONE

## Summary

Wrote `/Users/gracefullight/workspace/oh-my-agent/.agents/skills/oma-observability/resources/intent-rules.md`
covering all 7 intent categories (setup / migrate / investigate / alert / trace / tune / route)
with bilingual keyword tables (Korean + English), contextual signals, example queries (mixed Korean/English),
primary and secondary routing targets, tiebreak matching algorithm, and hook integration notes.
The file follows the oma-search intent-rules.md layout style.

## Files Changed

- `/Users/gracefullight/workspace/oh-my-agent/.agents/skills/oma-observability/resources/intent-rules.md` — created (320 lines)

## Acceptance Criteria Checklist (A5)

- [x] All 7 intent categories defined: setup, migrate, investigate, alert, trace, tune, route
- [x] English keywords: 8+ per intent
- [x] Korean keywords: 8+ per intent
- [x] Abbreviations / synonyms row per intent keyword table
- [x] Contextual signals section per intent (beyond raw keyword matching)
- [x] 5 example queries per intent (mix of Korean and English)
- [x] Primary route (files to consult) per intent
- [x] Secondary considerations per intent
- [x] Ambiguous / fallback section with worked examples table
- [x] Matching algorithm with tiebreak priority ordering
- [x] Override flags table (one flag per intent)
- [x] Integration with hooks section referencing triggers.json and execution-protocol.md
- [x] No future oma-X references
- [x] Tables used for keyword lists (readable format)
- [x] Style follows oma-search intent-rules.md layout

---

# Backend Result: meta-observability.md (oma-observability skill, task A7)

## Status: DONE

## Summary

Wrote `/Users/gracefullight/workspace/oh-my-agent/.agents/skills/oma-observability/resources/meta-observability.md`
covering the four A7 disciplines: pipeline self-health, clock skew/NTP, cardinality guardrails,
and retention matrix. The file also includes pipeline failure modes (Section E) and an alert/dashboard
scaffold (Section F) that feeds `resources/observability-as-code.md`.

## Files Changed

- `/Users/gracefullight/workspace/oh-my-agent/.agents/skills/oma-observability/resources/meta-observability.md` — created (603 lines)

## Acceptance Criteria Checklist (A7)

- [x] Pipeline self-health: `otelcol_*` metrics table, memory_limiter YAML, self-scrape config, golden delivery-ratio formula
- [x] Clock skew/NTP discipline: per-cloud NTP table, span validation rule, chrony offset metric + cron snippet, PTP note for sub-ms requirements
- [x] Cardinality guardrails: hard-rules table, route normalization YAML, PromQL measurement queries, per-service budget alert, attribute allow-list SDK example
- [x] Retention matrix: 7-row table with raw/aggregated/archive columns, rationale per row, WORM cross-ref, GDPR Art. 5(1)(e) cross-ref
- [x] Pipeline failure modes table with remediation steps (Section E)
- [x] Five golden meta-observability alerts with PrometheusRule CRD YAML (Section F)
- [x] Grafana dashboard panel blueprint cross-ref to observability-as-code.md
- [x] Cross-references valid for all skill-internal files referenced
- [x] No "future oma-X" references
- [x] Technical English; no emojis in content

---

# Backend Result: auto-score.sh bash 3.2 compatibility fix

## Status: DONE

## Summary

Replaced `declare -A` associative arrays with parallel indexed arrays and a
`lookup_check_field` helper function so the script runs on the default macOS
bash 3.2.57. No logic was changed — only the storage mechanism for intermediate
check results.

### Approach chosen

Parallel indexed arrays (`CHECK_IDS`, `CHECK_PASS`, `CHECK_SCORE`, `CHECK_MAX`,
`CHECK_EVIDENCE`) populated via `record_check()`, with `lookup_check_field()`
performing a linear search by check ID. Chosen over delimited strings because it
keeps each field readable and avoids fragile `IFS` parsing.

### bash 3.2 issues found and fixed

| Line (original) | Issue | Fix |
|---|---|---|
| 56 | `declare -A PASS SCORE MAX EVIDENCE` | Replaced with 5 parallel indexed arrays |
| 59-65 | `set_result()` writing to assoc arrays | Replaced with `record_check()` appending to indexed arrays |
| 285 | `${PASS[test-pass]:-false}` assoc lookup | Replaced with `lookup_check_field "test-pass" "pass"` |
| 303-306 | `${SCORE[$id]:-0}` / `${MAX[$id]:-0}` in totals loop | Replaced with `lookup_check_field` calls |
| 312-316 | `build_check_json()` reading assoc arrays | Replaced with `lookup_check_field` calls |

No other bash 3.2 incompatibilities were present. `$'\n'` in parameter
expansion, `${var#prefix}`, `${var:+default}`, `${!indirect}`, and `+=` on
indexed arrays all work on bash 3.2.

### Actual JSON output (empty-dir test)

```json
{
  "harness": "vanilla",
  "project_dir": "/tmp/auto-score-empty-test",
  "timestamp": "2026-04-11T09:57:18Z",
  "checks": {
    "setup-nextjs":   { "pass": false, "score": 0, "max": 2.5, "evidence": "package.json not found" },
    "setup-tailwind": { "pass": false, "score": 0, "max": 2.5, "evidence": "package.json not found" },
    "setup-r3f":      { "pass": false, "score": 0, "max": 2.5, "evidence": "package.json not found" },
    "setup-build":    { "pass": false, "score": 0, "max": 2.5, "evidence": "package.json not found" },
    "ai-api":         { "pass": false, "score": 0, "max": 5,   "evidence": "package.json not found" },
    "test-exists":    { "pass": false, "score": 0, "max": 2.5, "evidence": "package.json not found" },
    "test-pass":      { "pass": false, "score": 0, "max": 2.5, "evidence": "package.json not found" },
    "test-coverage":  { "pass": false, "score": 0, "max": 2.5, "evidence": "package.json not found" }
  },
  "auto_score_total": 0,
  "auto_score_max": 22.5,
  "errors": [
    "package.json not found in /tmp/auto-score-empty-test — all auto-checks scored 0"
  ]
}
```

### Acceptance criteria

- [x] `bash -n` passes (no syntax errors)
- [x] Empty-dir test produces valid JSON via `jq .`
- [x] All 8 check IDs present in output
- [x] All checks fail with `pass: false, score: 0` for empty directory
- [x] Final JSON schema identical to original (collect.sh compatible)
- [x] No logic changes — only storage mechanism altered

---

# Backend Result: auto-score.sh (original implementation)

## Status: COMPLETE

## Summary

Implemented `/benchmarks/scoring/auto-score.sh`, a pure bash script that runs all 8 automated benchmark checks against a given project directory and emits a structured JSON report to stdout.

## Files Changed

- `/Users/gracefullight/workspace/oh-my-agent/benchmarks/scoring/auto-score.sh` — created, executable

## Acceptance Criteria Checklist

- [x] Pure bash, uses `jq` for JSON output
- [x] `set -uo pipefail` (not `-e`) so individual check failures do not abort the script
- [x] All `max` values read from `checklist.json` via `jq` — not hardcoded
- [x] All 8 auto-scored checks implemented: `setup-nextjs`, `setup-tailwind`, `setup-r3f`, `setup-build`, `ai-api`, `test-exists`, `test-pass`, `test-coverage`
- [x] Each check uses `timeout 300` (5-minute limit); timeout scores 0 and appends to `errors`
- [x] `setup-build` and `test-*` checks run in a `cd "$PROJECT_DIR"` subshell
- [x] All stderr routed to `$PROJECT_DIR/auto-score.log`
- [x] Missing `package.json` handled: all checks score 0 with an error message
- [x] Output JSON matches the specified schema (`harness`, `project_dir`, `timestamp`, `checks`, `auto_score_total`, `auto_score_max`, `errors`)
- [x] Script is executable (`chmod +x` applied)
- [x] Bash syntax validated (`bash -n` exits 0)

## Decisions

- `test-coverage` parsing supports three formats: vitest/jest `All files | pct |` table, istanbul `Statements : pct` text, and `coverage/coverage-summary.json`. If none parse but exit code is 0 and `test-pass` passed, it is treated as a pass with a note.
- The `ai-api` grep searches `.ts`, `.tsx`, `.js`, `.jsx` under `src/` explicitly rather than all files to avoid false positives from `node_modules` or lock files.
- `bc` is used for floating-point addition of scores (e.g. 2.5 + 2.5) since bash arithmetic does not handle floats.
- `printf '%q'` is used when injecting `$PROJECT_DIR` into subshell strings to handle paths with spaces safely.

---

# Backend Result: run.sh

## Status: COMPLETE

## Summary

Implemented `/Users/gracefullight/workspace/oh-my-agent/benchmarks/run.sh`, a single bash script that creates isolated environments per harness, installs each harness, runs `claude -p` non-interactively, and writes per-harness and run-level manifests.

## Files Changed

- `/Users/gracefullight/workspace/oh-my-agent/benchmarks/run.sh` — created, executable

## Install Commands Found (verified via --help)

| Harness | Command |
|---|---|
| vanilla | (none) |
| oma | `CI=true HOME=$HOMEDIR bunx oh-my-agent@latest install` — `--yes` flag does NOT exist |
| omc | `HOME=$HOMEDIR claude plugin marketplace add https://github.com/Yeachan-Heo/oh-my-claudecode --scope user` then `HOME=$HOMEDIR claude plugin install oh-my-claudecode --scope user` |
| ecc | `git clone --depth 1 https://github.com/affaan-m/everything-claude-code /tmp/ecc-src-PID && cd ... && HOME=$HOMEDIR bash install.sh --profile full` |
| superpowers | Same plugin marketplace pattern as omc with `https://github.com/obra/superpowers` and plugin name `superpowers` |

## Harnesses That Cannot Be Auto-Installed Reliably

**omc and superpowers**: `claude plugin marketplace add` and `claude plugin install` have no `--yes` or `--non-interactive` flag. Whether they prompt interactively depends on the plugin manifest. The script attempts both steps; if either exits non-zero the harness is marked `install_status="failed"`, the run is skipped, and the benchmark continues.

**oma**: `oh-my-agent install` has no `--yes` flag (verified). The script uses `CI=true` (standard Node.js convention) which may or may not suppress prompts.

**ecc**: `install.sh --profile full` per design doc. If install.sh does not accept `--profile`, it will exit non-zero and be marked failed.

## Acceptance Criteria Checklist

- [x] Single file at `benchmarks/run.sh`
- [x] Executable (`chmod +x`)
- [x] `set -uo pipefail` (NOT -e)
- [x] Sequential execution only
- [x] Failure in one harness does not abort others
- [x] `claude`, `jq`, `git`, `bun` verified in PATH at start
- [x] `ANTHROPIC_API_KEY` verified at start
- [x] `--harness <id>` flag implemented
- [x] `--dry-run` flag implemented
- [x] `--base <path>` flag implemented
- [x] All 5 isolated HOME directories created
- [x] All 5 empty projects created with `git init -q`
- [x] Per-harness `*.manifest.json` written after each run
- [x] Final `run-manifest.json` written after all runs
- [x] BASE path printed to stdout at end
- [x] All 6 required claude control flags applied uniformly
- [x] 60-minute timeout per run (`timeout 3600`)
- [x] 5-minute timeout per install (`timeout 300`)
- [x] Investigation findings documented as comments at top of script
- [x] `OPENAI_API_KEY` passed through if set
- [x] bash syntax validated (`bash -n` exits 0)

---

# Backend Result: dependency install, Prisma setup, and seed (2026-05-06)

## Status: completed

## Summary

Installed all npm dependencies, generated the Prisma client, created the SQLite database via `prisma db push`, wrote the seed file at `prisma/seed.ts`, and successfully ran the seed to insert 3 sample worlds.

## Files Changed

- `/private/tmp/oma-loop-20260506-100111/projects/oma/prisma/seed.ts` — created

## Steps Completed

1. `npm install` — added 449 packages (33s). Two moderate vulnerabilities reported (non-blocking, peer dependency warnings only).
2. `npx prisma generate` — generated Prisma Client v6.19.3 to `node_modules/@prisma/client`.
3. `DATABASE_URL="file:./dev.db" npx prisma db push` — created `prisma/dev.db` SQLite database and synced schema.
4. `DATABASE_URL="file:./dev.db" npx tsx prisma/seed.ts` — inserted 1 `Child` row ("Sample Creator") and 3 `Project` rows (Enchanted Forest, Space Station, Ocean Discovery).

## Notes

- `DATABASE_URL` is in `.env.local` (Next.js convention). Prisma CLI only reads `.env` by default, so the env var was passed explicitly for CLI commands. Application runtime uses Next.js env loading which reads `.env.local` correctly.
- A `.env` file can be added alongside `.env.local` if Prisma CLI commands need to run without the explicit env prefix (e.g., `DATABASE_URL="file:./dev.db"` in `.env`).

## Acceptance Criteria Checklist

- [x] `npm install` completes without errors
- [x] `npx prisma generate` succeeds — Prisma Client v6.19.3 generated
- [x] `npx prisma db push` succeeds — `prisma/dev.db` created and schema synced
- [x] `prisma/seed.ts` created with exact content as specified
- [x] Seed script runs successfully — "Seed complete: created sample child and 3 sample worlds"
- [x] All 3 sample worlds inserted: Enchanted Forest, Space Station, Ocean Discovery
