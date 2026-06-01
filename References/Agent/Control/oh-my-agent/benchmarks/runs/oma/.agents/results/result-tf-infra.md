# DevOps Review — oma-observability Observability Stack Files

## Status: COMPLETE — Verdict: MINOR FIXES

## Summary

Read-only DevOps review of six oma-observability skill files. No infrastructure changes were made. All math is correct. One HIGH issue (nonexistent container image tag) blocks apply. Three MEDIUM issues affect correctness. All other findings are LOW.

---

## Review Findings (DevOps Perspective)

### 1. 2-Tier Collector (DaemonSet + Deployment) — ACCURATE

`collector-topology.md` correctly separates agent and gateway responsibilities. Component placement table (§4) is correct. The Prometheus-receiver scrape-duplication caveat and target allocator remedy are accurate and often omitted in practice.

Issue (LOW): `collector-topology.md:99` — `limit_mib: 400` is too low for a DaemonSet also running `filelog` + `kubeletstats`. Recommend 600 MiB with a sizing note.

### 2. Flagger / Argo Rollouts / OpenFeature Versions — MOSTLY ACCURATE

- `boundaries/release.md:168` (MEDIUM) — OpenFeature labeled "CNCF Incubating, since Dec 2023." It joined Incubating in December 2022 and reached **CNCF Graduated in November 2024**. Correct to "CNCF Graduated (Nov 2024)."
- `boundaries/release.md:373` (LOW) — CNCF blog URL points to the Incubating announcement, not Graduated.
- Flagger `v1beta1` Canary CR and Argo Rollouts `v1alpha1` Rollout CR match current upstream API versions. No issue.

### 3. SLO Burn-Rate Math — CORRECT

- Fast: `2% / (1h/720h) = 14.4x` — correct.
- Slow: `5% / (6h/720h) = 6x` — correct.
- PromQL in `slo.md §7.3–7.4` and `observability-as-code.md §6` replicates the math without errors.

Issue (LOW): `observability-as-code.md:179` — Grafana Terraform rule uses `status=~"5.."` while `slo.md §4` defines the SLI via `status=~"2..|3.."`. Inversion is mathematically correct but add a comment clarifying the relationship.

### 4. YAML Apply-Readiness — ONE BLOCKER

- `resources/observability-as-code.md:320` (HIGH) — `otel/opentelemetry-collector-contrib:0.100.0` does not exist; contrib is at 0.122.x as of 2026-Q2. Would fail on `ImagePullBackOff` immediately. Update to a current tag or digest pin.
- `transport/collector-topology.md:178` (MEDIUM) — `insecure_skip_verify: true` will be denied by OPA Gatekeeper / Kyverno on hardened clusters. Mark dev/test only; document the `ca_file` alternative.
- `resources/observability-as-code.md:364` (LOW) — Helm chart `version = "0.65.0"` is outdated (current 0.78.x). Add "verified YYYY-MM-DD" comment.

### 5. GitOps Integration (Argo CD / Flux) — ACCURATE

App-of-apps pattern, Flux `Kustomization` with `prune: true`, and self-observability cross-reference are all correct and deployable. No issues.

### 6. Multi-Tenant 4-Tier Isolation — PRACTICAL WITH ONE CORRECTION

Tier structure and isolation tradeoffs are accurate. `routing_connector` alpha caveat is correctly cross-referenced. Noisy-neighbor controls (§11) are a strong addition.

Issue (MEDIUM): `boundaries/multi-tenant.md:260` — "Per-tenant ingress rate limit via `receiver_creator` with per-tenant token bucket." The `receiver_creator` is for dynamic receiver instantiation, not rate limiting on a shared OTLP endpoint. Correct mechanism: `rate_limiter` extension or a `filter` + `memory_limiter` per routing pipeline.

### Issue Table

| File | Line | Severity | Issue |
|------|------|----------|-------|
| `resources/observability-as-code.md` | 320 | HIGH | `otelcol-contrib:0.100.0` image does not exist; update to 0.122.x or use digest |
| `transport/collector-topology.md` | 178 | MEDIUM | `insecure_skip_verify: true` — mark dev/test only; document `ca_file` alternative |
| `boundaries/release.md` | 168 | MEDIUM | OpenFeature should be "CNCF Graduated (Nov 2024)" |
| `boundaries/multi-tenant.md` | 260 | MEDIUM | `receiver_creator` is wrong mechanism; use `rate_limiter` extension |
| `transport/collector-topology.md` | 99 | LOW | `limit_mib: 400` too low for combined agent workload; suggest 600 with sizing note |
| `resources/observability-as-code.md` | 179 | LOW | Add comment clarifying burn-rate PromQL numerator vs slo.md SLI |
| `resources/observability-as-code.md` | 364 | LOW | Helm chart `0.65.0` outdated (0.78.x current); add "verified YYYY-MM-DD" |
| `boundaries/release.md` | 373 | LOW | CNCF blog URL points to Incubating announcement, not Graduated |

### Acceptance Checklist (DevOps Review)

- [ ] `observability-as-code.md:320` — update image tag to current (HIGH)
- [ ] `boundaries/release.md:168` — correct OpenFeature status to "CNCF Graduated (Nov 2024)" (MEDIUM)
- [ ] `transport/collector-topology.md:178` — add dev/test caveat; document `ca_file` (MEDIUM)
- [ ] `boundaries/multi-tenant.md:260` — replace `receiver_creator` with `rate_limiter` extension reference (MEDIUM)
- [ ] `transport/collector-topology.md:99` — raise `limit_mib` default with sizing guidance (LOW)
- [ ] `resources/observability-as-code.md:179` — add inversion comment (LOW)
- [ ] `resources/observability-as-code.md:364` — add "verified date" comment (LOW)
- [ ] `boundaries/release.md:373` — update CNCF blog URL (LOW)

---

# Network Engineer Review — oma-observability Layer/Transport Files

## Status: COMPLETE

## Summary

Read-only technical review of six oma-observability skill files from a Network Engineer perspective. No infrastructure changes were made. Verdict: MINOR FIXES.

## Files Reviewed

- `/Users/gracefullight/workspace/oh-my-agent/.agents/skills/oma-observability/resources/layers/L3-network.md`
- `/Users/gracefullight/workspace/oh-my-agent/.agents/skills/oma-observability/resources/layers/L4-transport.md`
- `/Users/gracefullight/workspace/oh-my-agent/.agents/skills/oma-observability/resources/transport/udp-statsd-mtu.md`
- `/Users/gracefullight/workspace/oh-my-agent/.agents/skills/oma-observability/resources/transport/otlp-grpc-vs-http.md`
- `/Users/gracefullight/workspace/oh-my-agent/.agents/skills/oma-observability/resources/transport/collector-topology.md`
- `/Users/gracefullight/workspace/oh-my-agent/.agents/skills/oma-observability/resources/boundaries/cross-application.md` (propagator matrix, Section 3)

## Files Changed

None — review only.

## Validation Results

No Terraform HCL applicable; read-only review.

## Review Findings

### 1. Technical Accuracy

**L3-network.md:88** — RFC 8899 cited for "IPv6 DPLPMTUD." RFC 8899 is a generic Datagram PMTUD spec, not IPv6-specific. IPv6 PMTUD is governed by RFC 8201 (which obsoletes RFC 1981). The parenthetical "IPv6" is misleading. Fix: cite RFC 8201 for IPv6 PMTUD; use RFC 8899 only when DPLPMTUD is the explicit subject.

**L4-transport.md:134** — States minimum kernel `>= 4.14` for eBPF. Correct for basic eBPF, but Beyla relies on BTF (BPF Type Format) which requires kernel >= 5.2. A qualifying note is needed.

All MTU arithmetic is correct. MSS clamping formulas are correct. OTLP port assignments (4317/4318), gRPC behavior, CRD stability notes, and BMP RFC 7854 / TCP 11019 are accurate.

### 2. Completeness — Missing Topics

- **ECMP + gRPC/HTTP2**: Long-lived gRPC connections hash to a single ECMP path, causing uneven load distribution — a common NE incident pattern. Not mentioned in L4-transport.md or otlp-grpc-vs-http.md.
- **QUIC UDP firewall blocking**: L4-transport.md §7 covers 0-RTT and tool support but omits enterprise firewall UDP 443/8443 blocking — the most common reason QUIC fails to negotiate in corporate environments.
- **BMP port variance**: L3-network.md §6.3 states TCP 11019 correctly but does not note that Cisco IOS-XE early BMP defaults to port 7777, causing silent connection refusal in mixed environments.
- **Operator triage commands**: No `ss -s`, `netstat -s`, `ethtool -S`, or `tc` cheatsheet for real-time NE triage.

### 3. Consistency

MTU values are consistent across all files: 1472 (IPv4 Ethernet), 1452 (IPv6 Ethernet), 1432 (VPN/PPPoE), 8192 (UDS). No contradiction between L3-network.md §4 and udp-statsd-mtu.md §3.

Propagator names (`b3multi`, `tracecontext`, `awsxray`, `datadog`) match OTel SDK canonical names throughout cross-application.md §3.

OTel semconv version `1.27.0 (2024-11)` pinned consistently in all three frontmatter headers (L3, L4, cross-application).

### 4. Usefulness for NE During Incident

Strong for cloud-native NEs: PMTUD black hole symptom pattern (L3-network.md §4.2) and keepalive vs. ALB/NLB timeout table (L4-transport.md §6) provide concrete operational numbers. BGP/BMP pipeline (L3-network.md §6) is well-structured for ISP/CDN teams. Propagator matrix (cross-application.md §3) is clear but serves application engineers more than NEs. Weaker: absence of quick-triage commands reduces usefulness during active incidents.

### 5. Verdict: MINOR FIXES

| Priority | File | Location | Issue | Action |
|----------|------|----------|-------|--------|
| Required | L3-network.md | Line 88 | RFC 8899 cited as "IPv6 DPLPMTUD" — should be RFC 8201 for IPv6 PMTUD | Fix citation |
| Recommended | L4-transport.md | Line 134 | eBPF kernel minimum 4.14 understates BTF requirement for Beyla (>=5.2) | Add caveat |
| Recommended | otlp-grpc-vs-http.md or L4-transport.md | §6 / §3 | ECMP asymmetry with long-lived gRPC connections not addressed | Add note |
| Recommended | L4-transport.md | §7 | QUIC UDP 443/8443 firewall blocking missing from deployment considerations | Add note |
| Minor | L3-network.md | §6.3 | BMP port 11019 correct; Cisco IOS-XE port 7777 variant unmentioned | Add note |

## Acceptance Checklist

- [x] All six target files read in full
- [x] Technical accuracy verified against RFCs and OTel spec
- [x] MTU numbers cross-checked across all transport/layer files
- [x] Propagator naming checked against OTel SDK canonical names
- [x] Semconv version pin consistency confirmed across frontmatter
- [x] Verdict: MINOR FIXES — no blocking issues, no destructive changes required
- [x] No .agents/ files modified
- [x] No Terraform applied

---

# Result: oma-observability Skill — observability-as-code.md (Plan Task F1)

## Status

completed

## Summary

Created `resources/observability-as-code.md` for the `oma-observability` skill (plan task F1). File covers: Grafana Jsonnet/Grafonnet, Perses (CNCF Sandbox), PrometheusRule CRD, Alertmanager YAML, Terraform Grafana provider, OpenSLO YAML, OTel Collector via OTel Operator CRD (`v1beta1`), GitOps integration (Argo CD + Flux), burn-rate multi-window alerts (concrete PromQL), immutable review workflow, secrets management, environment separation, testing, and anti-patterns. 651 total lines.

Previously in this skill: `resources/signals/cost.md` (plan task D5), `resources/layers/mesh.md` (C3), `resources/layers/L3-network.md` (C1), and two transport files (B3, B4).

## Files Created / Modified

- `/Users/gracefullight/workspace/oh-my-agent/.agents/skills/oma-observability/resources/observability-as-code.md` (651 lines) — this session
- `/Users/gracefullight/workspace/oh-my-agent/.agents/skills/oma-observability/resources/signals/cost.md` (310 lines) — previous session
- `/Users/gracefullight/workspace/oh-my-agent/.agents/skills/oma-observability/resources/layers/mesh.md` (362 lines) — previous session
- `/Users/gracefullight/workspace/oh-my-agent/.agents/skills/oma-observability/resources/layers/L3-network.md` (280 lines) — previous session
- `/Users/gracefullight/workspace/oh-my-agent/.agents/skills/oma-observability/resources/transport/collector-topology.md` (294 lines) — previous session
- `/Users/gracefullight/workspace/oh-my-agent/.agents/skills/oma-observability/resources/transport/sampling-recipes.md` (291 lines) — previous session

## Validation Results

No Terraform HCL was provisioned in this task (the file contains Terraform HCL snippets as documentation examples only). No `terraform fmt`, `validate`, or `plan` applicable to doc generation.

Content validation against acceptance criteria (F1):

- [x] Grafana Jsonnet / Grafonnet example (Section 2.1)
- [x] Perses CNCF Sandbox (Sections 2.2 and 12)
- [x] PrometheusRule CRD (Sections 3.1 and 6)
- [x] Alertmanager YAML (Section 3.2)
- [x] Terraform Grafana provider (Section 3.3)
- [x] OpenSLO YAML manifest (Section 4.1)
- [x] Sloth YAML workflow (Section 4.2)
- [x] Pyrra k8s CRD (Section 4.3)
- [x] OTel Operator `OpenTelemetryCollector` CRD `v1beta1` (Section 5.1) with all 4 modes
- [x] Instrumentation CR cross-ref (Section 5.1)
- [x] Terraform helm_release + kubernetes_manifest (Section 5.2)
- [x] `otelcol validate` in CI (Section 5.3)
- [x] Burn-rate multi-window alert — fast 14.4x / 1h+5m, slow 6x / 6h+30m (Section 6)
- [x] Full PrometheusRule CRD YAML combining both alert pairs (Section 6)
- [x] Argo CD app-of-apps pattern (Section 7.1)
- [x] Flux Kustomization (Section 7.2)
- [x] Self-observability cross-ref to meta-observability.md (Section 7.3)
- [x] Immutable review workflow with CI gate table (Section 8)
- [x] Secrets management with ESO / Sealed Secrets (Section 9)
- [x] Environment separation via Kustomize / Helm values (Section 10)
- [x] Testing: promtool rule_test fixture, ephemeral Grafana API, otelcol_test (Section 11)
- [x] Perses CNCF Sandbox specifics (Section 12)
- [x] Matrix coverage note — cross-cutting, no dedicated row (Section 13)
- [x] Anti-patterns I-1 through I-5 (Section 14)
- [x] No secrets hardcoded; all credential refs use secretKeyRef
- [x] No future oma-X references
- [x] Content in English
- [x] Cross-refs use relative paths from resources/ root

### Previous sessions: collector-topology.md (B3)

- [x] OTel Operator v1beta1 CRD stability noted
- [x] Four modes: Deployment, DaemonSet, StatefulSet, Sidecar with use cases
- [x] Two-tier hybrid diagram: App -> DaemonSet Agent -> Deployment Gateway -> backend
- [x] Agent layer receivers: hostmetrics, filelog, kubeletstats, k8sattributes
- [x] Gateway layer: batch, tail_sampling, loadbalancing, memory_limiter
- [x] Sidecar exception table: Fargate, Cloud Run, per-pod isolation, multi-tenant
- [x] Warning: sidecar on regular k8s = N collectors
- [x] Component preference table (kubeletstats, filelog, hostmetrics -> DaemonSet; prometheus -> Deployment with caveats)
- [x] containerd/CRI-O: image pull metrics, container lifecycle, metric endpoints
- [x] cAdvisor integration via kubeletstats receiver
- [x] k8sattributes processor enrichment with full YAML example
- [x] loadbalancing exporter with consistent hashing YAML
- [x] Two-tier gateway pattern diagram
- [x] Federated/multi-cluster diagram with egress cost consideration
- [x] Anti-patterns table: sidecar on k8s, tail sampling in sidecar, single replica, missing memory_limiter
- [x] Primary sources cited inline

### sampling-recipes.md (B4)

- [x] Taxonomy table: head-based, tail-based, adaptive
- [x] Tail-based recipe: 100% errors + 100% cost/latency + 5-10% baseline
- [x] tail_sampling YAML with 4 policies
- [x] Cost-aware: genai.cost.total_usd, llm.request.cost_usd, $0.50 threshold
- [x] transform processor annotation pattern for numeric cost comparison
- [x] Tenant-aware: enterprise 100%, pro 20%, free 2%
- [x] routing_connector Option A with alpha stability warning
- [x] tail_sampling Option B with and sub-policies (stable, recommended for production)
- [x] Complete four-policy YAML combining all policies
- [x] Pitfalls table: head-based incomplete traces, memory exhaustion, decision wait, rate mismatch, routing_connector alpha caveat, missing loadbalancing exporter
- [x] Primary sources cited inline

## Plan / Apply Notes

No infrastructure was provisioned. These are skill documentation files only.

## Acceptance Checklist

### C3: mesh.md

- [x] Istio 1.22+ OTLP/HTTP direct export documented with Telemetry API CR YAML
- [x] Envoy 1.29+ OTLP tracer and custom sampler interface documented
- [x] Linkerd propagator headers (`l5d-ctx-trace`, `l5d-ctx-span`, `l5d-ctx-parent`, `l5d-ctx-deadline`) listed
- [x] W3C Trace Context as cross-mesh standard with Linkerd translation rule at boundary gateway
- [x] OTel Operator Instrumentation CR YAML with Java, NodeJS, Python, .NET, Go runtimes
- [x] Activation annotation `instrumentation.opentelemetry.io/inject-{language}` documented
- [x] 3 YAML CR snippets: Istio Telemetry CR, OTel Operator Instrumentation CR, PrometheusRule
- [x] Propagator header table, mesh options table, sampling table, anti-patterns table
- [x] All cross-refs use relative paths
- [x] No oma-X forward references
- [x] Content in English

### B3: collector-topology.md

- [x] OTel Operator v1beta1 CRD stability noted
- [x] Four modes: Deployment, DaemonSet, StatefulSet, Sidecar with use cases
- [x] Two-tier hybrid diagram: App -> DaemonSet Agent -> Deployment Gateway -> backend
- [x] Agent layer receivers: hostmetrics, filelog, kubeletstats, k8sattributes
- [x] Gateway layer: batch, tail_sampling, loadbalancing, memory_limiter
- [x] Sidecar exception table: Fargate, Cloud Run, per-pod isolation, multi-tenant
- [x] Warning: sidecar on regular k8s = N collectors
- [x] Component preference table (kubeletstats, filelog, hostmetrics -> DaemonSet; prometheus -> Deployment with caveats)
- [x] containerd/CRI-O: image pull metrics, container lifecycle, metric endpoints
- [x] cAdvisor integration via kubeletstats receiver
- [x] k8sattributes processor enrichment with full YAML example
- [x] loadbalancing exporter with consistent hashing YAML
- [x] Two-tier gateway pattern diagram
- [x] Federated/multi-cluster diagram with egress cost consideration
- [x] Anti-patterns table: sidecar on k8s, tail sampling in sidecar, single replica, missing memory_limiter
- [x] Primary sources cited inline

### B4: sampling-recipes.md

- [x] Taxonomy table: head-based, tail-based, adaptive
- [x] Tail-based recipe: 100% errors + 100% cost/latency + 5-10% baseline
- [x] tail_sampling YAML with 4 policies
- [x] Cost-aware: genai.cost.total_usd, llm.request.cost_usd, $0.50 threshold
- [x] transform processor annotation pattern for numeric cost comparison
- [x] Tenant-aware: enterprise 100%, pro 20%, free 2%
- [x] routing_connector Option A with alpha stability warning
- [x] tail_sampling Option B with and sub-policies (stable, recommended for production)
- [x] Complete four-policy YAML combining all policies
- [x] Pitfalls table: head-based incomplete traces, memory exhaustion, decision wait, rate mismatch, routing_connector alpha caveat, missing loadbalancing exporter
- [x] Primary sources cited inline
