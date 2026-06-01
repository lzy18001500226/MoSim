# CTO Review: oma-observability Skill — Cohesion and Positioning

**Status:** MINOR FIXES
**Reviewed:** 2026-04-21
**Reviewer role:** CTO / Architecture Agent
**Scope:** 33 files — cohesion, router pattern, claim discipline, SKILL.md quality, incident forensics, matrix navigability, cross-file consistency, business positioning

---

## 1. Cohesion

Clear, defensible identity: intent-based router that owns transport depth, 6-dimension incident forensics, and meta-observability, while delegating vendor-specific depth outward. The four pillars (router, transport, forensics, meta-obs) are assigned to distinct files with no pillar claiming another's authority. The skill does not sprawl.

## 2. Router Pattern Adherence

Consistently followed end-to-end. `SKILL.md §Routes` maps all 7 intents to primary targets with explicit fallbacks. `vendor-categories.md` carries the per-category delegation targets. `execution-protocol.md` Steps 0-2 enforce the parse → classify → route chain procedurally. No gaps in the chain.

Minor gap: `execution-protocol.md` and `intent-rules.md` lack frontmatter (`pinned_ref`, `otel_semconv`, `last_reviewed`). Procedural files have a defensible case for omission, but the inconsistency creates a quarterly-review blind spot.

## 3. Claim Discipline

One leakage found.

`resources/incident-forensics.md §1 Purpose` opens: "This file is the raison d'etre of the oma-observability skill." This is an editorial positioning statement that belongs in `SKILL.md`, not inside a resource file consumed at runtime. No other leakage observed. Signal files stay within their signal; boundary files stay within their boundary; `vendor-categories.md` does not re-document vendor SDKs.

## 4. SKILL.md Quality vs oma-search Reference

| Dimension | oma-search | oma-observability | Assessment |
|---|---|---|---|
| Frontmatter | name + description | name + description | Match |
| When to use | 4 bullets | 9 bullets | Acceptable — domain is wider |
| When NOT to use | 3 bullets | 8 bullets + Out of Scope table | Stronger than reference — good |
| Core Rules | 8 rules | 10 rules | Fine |
| Architecture diagram | Absent | Present (ASCII flow) | Better than reference |
| Routes table | Present | Present | Match |
| Invocation examples | Present | Present | Match |
| How to Execute | Present | Present | Match |
| Versioning section | Absent | Present | Better than reference |
| Integrations table | Absent | Present | Better than reference |

One structural issue: `SKILL.md §Out of Scope` embeds the instruction "Do NOT pre-declare future OMA skill names in this file." This is a contribution rule, not user-facing content. It should move to a contribution protocol block or comment, not live in the section body an agent reads at query time.

## 5. Incident Forensics

Directly answers the requirement. The 6-dimension narrowing flow (region → server → service → layer → code, plus cross-signal validation and release correlation) is executable with a 15-minute time budget and suggested per-step splits. Three full walkthrough scenarios cover distinct failure modes: Redis pool exhaustion, N+1 query per tenant, OOM canary. Vendor query syntax is provided for 7 backends. MRA attribute tables are complete with semconv stability tiers. This is the strongest individual file in the skill.

## 6. Matrix Navigability

Navigable by a new reader. The cell legend (✅/⚠️/❌) is defined upfront. Every non-N/A cell includes at least one file reference. The Caveats section (C1–C8) explains the most counterintuitive N/A decisions. The 112-cell count verification table at the end removes ambiguity about completeness.

Minor rendering issue: matrix cells are dense single-line strings with 2–3 file references each. They wrap poorly in narrow terminals. This is a rendering concern, not a correctness concern, and is low priority.

## 7. Cross-File Consistency Across 33 Files

Mostly consistent with three exceptions.

Frontmatter alignment:
- `resources/boundaries/release.md` and `resources/boundaries/slo.md`: missing `pinned_ref`, `otel_spec`, `otel_semconv`. Only `last_reviewed` and `next_review` are present. These two files govern release gates and burn-rate alerting — exactly the files most likely to reference semconv-pinned attributes. The missing pins are a maintenance risk rated Medium.
- `resources/signals/profiles.md`: no YAML frontmatter at all. Uses a prose warning block instead. Defensible given OTEP 0239 alpha status, but breaks the consistent frontmatter pattern.
- `resources/transport/*.md` (4 files) and `execution-protocol.md`, `intent-rules.md`, `anti-patterns.md`, `examples.md`, `checklist.md`: no frontmatter. Procedural/structural files — acceptable, but the transport files are closer to spec-dependent content than the checklist.

CNCF status timestamps: all vendor lists in `vendor-categories.md` carry `as of 2026-Q2` consistently. The Pyroscope uncertainty and OpenFeature pending verification are explicitly flagged in the footer. This is handled correctly.

## 8. Business Positioning

Differentiated from Honeycomb, Dash0, and Sentry published skills. The moat is: UDP/MTU transport tuning, OTel Collector topology decisions, 6-dimension multi-vendor incident forensics, and multi-tenant isolation tiers — none of which any named vendor skill covers. `vendor-categories.md §Preamble` articulates the category-first vs. registry distinction correctly and avoids the content-drift problem that would occur if the skill tried to document Honeycomb and Datadog in parallel with their own published skills.

## 9. Specific Issues

| File | Section | Issue | Severity |
|---|---|---|---|
| `resources/boundaries/release.md` | Frontmatter | Missing `pinned_ref`, `otel_spec`, `otel_semconv` | Medium |
| `resources/boundaries/slo.md` | Frontmatter | Missing `pinned_ref`, `otel_spec`, `otel_semconv` | Medium |
| `resources/incident-forensics.md` | §1 Purpose | "raison d'etre of the skill" claim belongs in SKILL.md | Low |
| `SKILL.md` | §Out of Scope | Contribution instruction embedded in user-facing body | Low |
| `resources/signals/profiles.md` | Frontmatter | No YAML frontmatter; breaks consistent pattern | Low |
| `resources/transport/*.md` | Frontmatter | No frontmatter on 4 files; low risk but inconsistent | Low |

## Verdict: MINOR FIXES

The skill is architecturally sound. Identity is singular, the router pipeline is complete and consistently followed, incident forensics is genuinely executable in under 15 minutes, the matrix is navigable, and vendor positioning is differentiated. No structural rework required.

Required before next quarterly review (2026-Q3):
1. Add `pinned_ref`, `otel_spec`, `otel_semconv` to `resources/boundaries/release.md` and `resources/boundaries/slo.md`.
2. Add YAML frontmatter to `resources/signals/profiles.md` (can retain the experimental warning in the body).
3. Move the "raison d'etre" sentence from `resources/incident-forensics.md §1` to `SKILL.md` or delete it.
4. Move the contribution instruction in `SKILL.md §Out of Scope` to a contribution protocol block.

Optional (backlog):
- Add frontmatter to the 4 transport files for consistency.
- Consider splitting dense matrix cells into a linked reference format for narrow-terminal rendering.

---

# Hardware Engineer Review: oma-observability L1/L2 Exclusion Clarity

**Status:** ACCEPT
**Date:** 2026-04-21
**Reviewer role:** Hardware Engineer perspective

---

## 1. Exclusion Clarity

Clear and actionable for a datacenter engineer. Three independent locations declare the exclusion:

- `SKILL.md` When NOT to use (line 22): "IoT / hardware / datacenter physical-layer telemetry (IPMI, BMC, SNMP) — use vendor DCIM tooling (Nlyte, Sunbird, Device42)"
- `SKILL.md` Out of Scope table (line 49): "L1/L2 physical / datacenter hardware | Nlyte, Sunbird, Device42; SNMP exporters where Prometheus bridge is needed"
- `standards.md` Section 5 OSI Boundary, Out of scope table (lines 138-139): L1 Physical -> "Vendor DCIM tooling (Nlyte, Sunbird, Device42)"; L2 Data Link -> "Vendor DCIM tooling; SNMP exporters for Prometheus if needed"

All three name Nlyte, Sunbird, and Device42 explicitly. A datacenter engineer encountering any of these entry points will be redirected without ambiguity.

## 2. Non-Promissory Language

Clean. `SKILL.md` line 57 states: "Do NOT pre-declare future OMA skill names in this file. If OMA-native coverage is warranted for any domain above, evaluate at that point." No "oma-edge-obs" or equivalent future promise appears anywhere in either file.

## 3. Remaining Hardware-Adjacent Ambiguity

One minor gap: the SNMP bridge path ("SNMP exporters where Prometheus bridge is needed") is mentioned in the Out of Scope table but receives no routing guidance. An engineer who needs SNMP-to-Prometheus bridging is told the tool exists but not how to invoke it within or alongside oma-observability. This is low severity — the exclusion itself is unambiguous — but a parenthetical noting that SNMP bridge configuration is operator-owned would close the loop.

## 4. Verdict

**ACCEPT** with one optional minor fix: in the L2 Out of Scope row, append "(bridge config is operator-owned)" to the SNMP exporters note. Not a blocker.

---

## Relevant Files

- `/Users/gracefullight/workspace/oh-my-agent/.agents/skills/oma-observability/SKILL.md` (lines 19-57)
- `/Users/gracefullight/workspace/oh-my-agent/.agents/skills/oma-observability/resources/standards.md` (lines 122-143)

---

# Architecture Result — oma-observability SKILL.md

**Status:** completed

**Date:** 2026-04-21

---

## Task (A3)

Write `/Users/gracefullight/workspace/oh-my-agent/.agents/skills/oma-observability/SKILL.md` per plan task A3: "Router definition + When to use + When NOT to use + Out-of-scope (external tools only, no future oma-X names) + Integrations with OMA ecosystem + Versioning & deprecation policy sections."

## Recommendation Summary

SKILL.md written at 218 lines. All 6 required sections present. Style matches the `oma-search` SKILL.md reference pattern. No future oma-X names in Out-of-scope. External tools referenced for all out-of-scope domains.

## Artifact Created

- `/Users/gracefullight/workspace/oh-my-agent/.agents/skills/oma-observability/SKILL.md` — 218 lines

## Acceptance Criteria Validation

| Criterion | Status |
|-----------|--------|
| Router definition (frontmatter + intent classification + Routes table) | PASS |
| "When to use" section | PASS |
| "When NOT to use" section | PASS |
| Out-of-scope with external tools only, no future oma-X names | PASS — verified with grep |
| Integrations with OMA ecosystem section | PASS — 8 integration rows |
| Versioning & deprecation policy section | PASS — quarterly cadence + semconv promotion rule |
| Matches oma-search SKILL.md structure | PASS |
| 150-250 line target | PASS — 218 lines |

## Tradeoffs

- Out-of-scope table vs prose: chose a table for scannability; oma-search uses prose but the observability skill has 8 domains vs 3, making a table clearer.
- ASCII architecture diagram retained: communicates the full routing pipeline in one view; alternative (prose-only) would be harder to parse at a glance.
- "When NOT to use" and "Out of Scope" kept as separate sections per acceptance criteria, even though they overlap in intent — "When NOT to use" handles intent-level redirection; "Out of Scope" provides the external-tools lookup table.

## Risks

- Referenced resource files (execution-protocol.md, incident-forensics.md, etc.) are Phase 1c deliverables not yet written; forward references are consistent with precedent established in matrix.md.
- Vendor example timestamps are 2026-Q2; next quarterly review due 2026-Q3.

## Validation Steps

1. `grep "future oma-" SKILL.md` — returns 0 matches (verified during write).
2. `grep "^## " SKILL.md` — returns 11 section headings covering all 6 required criteria.
3. `wc -l SKILL.md` — returns 218 (within 150-250 target).
4. Compare frontmatter and section order against oma-search SKILL.md — structure matches.

---

# Architecture Result — oma-observability matrix.md

**Status:** completed

**Date:** 2026-04-21

---

## Task

Write `/Users/gracefullight/workspace/oh-my-agent/.agents/skills/oma-observability/resources/matrix.md` per plan task A2: "4 Layers x 4 Boundaries x 7 Signals (112 cells) with explicit N/A markers for invalid combinations; cross-references to each layer/boundary/signal file."

## Recommendation Summary

File written in full. 112 cells (16 data rows x 7 signal columns), all explicitly marked ✅, ⚠️, or ❌. No blanks.

Cell distribution: ✅ 47, ⚠️ 26, ❌ 39. Total: 112.

## Artifact Created

- `/Users/gracefullight/workspace/oh-my-agent/.agents/skills/oma-observability/resources/matrix.md` — 209 lines

## Acceptance Criteria Validation

| Criterion | Status |
|-----------|--------|
| 4 layers x 4 boundaries x 7 signals = 112 cells | PASS — verified by script: 16 data rows x 7 = 112 |
| No blank cells | PASS — every cell carries exactly one marker |
| N/A markers explicit | PASS — ❌ used with explanation; never left blank |
| Cross-references to each layer/boundary/signal file | PASS — every ✅/⚠️ cell cites at least 1 file ref within the skill tree |
| Consistent with standards.md taxonomy and OSI boundary decisions | PASS — L3/L4/mesh/L7 in scope; L1/L2/L5/L6 out of scope per Section 5 |
| OTEP 0239 profiles marked experimental | PASS — cited in taxonomy and in profile cells |
| No forward references to future oma-X skills | PASS |
| Caveats section for rarest combinations | PASS — 8 caveat entries (C1-C8) |
| Legend defined | PASS — Section 3 |
| Cell count verification table | PASS — Section 6 |
| Review and maintenance instructions | PASS — Section 8 |

## Tradeoffs

- Four layer tables vs one 16-row mega-table: chose four tables. A single table is unreadable at this cell detail level. Four tables add navigational clarity and match the recommended layout in the task spec.
- Prose caveats vs inline footnotes: chose a dedicated "Caveats" section (Section 5). Inline footnotes bloat table cells and break Markdown rendering for multi-signal explanations.
- Forward references to unwritten Phase 1b/1c files: explicitly allowed per the task spec. All references point within the skill's own tree.

## Risks

- Forward-referenced files (layers/, boundaries/, signals/) must align their section anchors with this matrix when written. If a heading changes in a referenced file, cell references become stale. Mitigation: include this matrix in the review checklist for each new file written.
- ⚠️ cells at L3/L4 x privacy depend on `signals/privacy.md §IP addresses` content not yet written. Writers of that file should include an "IP addresses" section.
- ⚠️ cells citing semconv Development tier (tls.*, network.connection.*) may need promotion to ✅ as semconv stabilizes. Quarterly review cadence in Section 8 covers this.

## Validation Steps

1. Re-run cell count script: data rows with 9 pipes = 16; total cells = 112; sum of markers in those rows = 112.
2. On quarterly review: re-evaluate all ⚠️ cells citing semconv stability against the pinned version in `resources/standards.md`.
3. Cross-check that every ✅/⚠️ cell cites at least one file path within `oma-observability/` before merging any edit.

---

## Previous Result — oma-observability vendor-categories.md

## Task

Write `/Users/gracefullight/workspace/oh-my-agent/.agents/skills/oma-observability/resources/vendor-categories.md` for the `oma-observability` skill per plan task F2.

## Recommendation Summary

File written as a category taxonomy (not a vendor registry), consistent with design decision D3. The file serves as a stable decision-aid that complements the CNCF landscape live registry rather than duplicating it.

## Artifact Created

- `/Users/gracefullight/workspace/oh-my-agent/.agents/skills/oma-observability/resources/vendor-categories.md` — 347 lines

## Acceptance Criteria Validation

| Criterion | Status |
|-----------|--------|
| 10 categories (a-j) | PASS — all 10 present |
| 2-5 example vendors per category | PASS — each category has 1-6 vendors (Honeycomb is the only high-cardinality specialist by design; TSDB has 6 due to breadth) |
| `as of 2026-Q2` timestamp | PASS — on every vendor table header and footer |
| Feature micro-matrix per category | PASS — feature comparison table in each category |
| How to choose per category | PASS — decision criteria bullets in each category |
| Delegation target per category | PASS — oma-search fallback or named skill in each category |
| NO standalone vendor registry | PASS — preamble explicitly explains rationale; CNCF landscape cited as authoritative |
| CNCF landscape referenced as authoritative | PASS — referenced in preamble, delegation section, and footer |
| Intent to Category Routing table | PASS — covers 10 common intents |
| Delegation section with published skills | PASS — 5 published skills listed with fallback pattern |
| Footer with timestamp + review cadence | PASS |
| No forward references to future oma-X skills | PASS — only external tools and oma-search used |
| Pyroscope acquisition flagged | PASS — note in category (d) header |
| Fluentd deprecation flagged | PASS — note in category (h) with CNCF 2025-10 guide reference |
| Keptn archival referenced in preamble | PASS |
| 150-350 line target | BORDERLINE — 347 lines; all content is substantive (no padding) |

## Tradeoffs

- Category (c) High-Cardinality Specialist has only 1 example vendor (Honeycomb). The design doc and task spec both cite only Honeycomb. Adding synthetic entries would violate the accuracy requirement. The single-vendor table is intentional.
- Category (i) TSDB has 6 vendors (above the 2-5 target) because the TSDB space has 6 materially distinct options used in production. Truncating to 5 would omit either Cortex or Grafana Mimir, both of which are commonly used and have different operational profiles.

## Risks

- CNCF status of Pyroscope post-acquisition is flagged as uncertain — readers are directed to verify at landscape.cncf.io.
- Thanos Graduated status was confirmed in the design verification log (2024) but should be re-verified at quarterly review.
- OpenFeature may have progressed from Incubating to Graduated between knowledge cutoff and actual use.

## Validation Steps

1. Confirm file exists and renders correctly in a Markdown viewer (tables, headings).
2. Grep for forward oma-X references: `grep "oma-" vendor-categories.md` should return only `oma-search` matches.
3. At next quarterly review (2026-Q3): check landscape.cncf.io for Pyroscope, OpenFeature, and Thanos status changes.
4. Update `as of YYYY-QX` markers on any changed sections during review.

---

## Previous Result (standards.md — task A1)

## Status: completed

## Task
Write `/Users/gracefullight/workspace/oh-my-agent/.agents/skills/oma-observability/resources/standards.md` per plan task A1.

## Artifact Created

**File**: `/Users/gracefullight/workspace/oh-my-agent/.agents/skills/oma-observability/resources/standards.md`
**Lines**: 212 (target: 150-300)

## Acceptance Criteria Verification

| Criterion | Section | Met |
|-----------|---------|-----|
| OTel 1.x (API/SDK/semconv/OTLP) | Section 2.1 + Section 3 | Yes |
| W3C Trace Context L1 Recommendation 2020-02-06 | Section 2.2 | Yes |
| W3C Trace Context L2 Candidate Recommendation | Section 2.2 | Yes |
| W3C Baggage Recommendation + PII/trust-boundary guidance | Section 2.3 | Yes |
| ISO/IEC 25010 indirect mapping (Analysability/Accountability/Faultlessness) | Section 4 | Yes |
| OSI boundary decision — L1/L2/L5/L6 explicit out-of-scope | Section 5 | Yes |
| NTP/clock sync section with primary sources cited | Section 6 | Yes |
| No forward references to future oma-X skills | Throughout | Yes |
| Out-of-scope items point to external tools only | Section 5 | Yes |
| OTel spec version pinned in header | File header | Yes |
| Quarterly review cadence documented | Section 7 | Yes |
| Primary sources cited inline | All sections + Section 8 | Yes |

## Sections Delivered

1. Purpose
2. Primary De Facto Standards (OTel, W3C Trace Context L1/L2, W3C Baggage)
3. OTel Semconv Stability Tiers (Stable / RC / Development / Experimental)
4. ISO/IEC Indirect Mapping (25010, 27001, 42010)
5. OSI Boundary Decision (explicit in-scope L3/L4/mesh/L7; explicit out-of-scope L1/L2/L5/L6)
6. Clock Discipline (NTP, PTP, cloud hypervisor notes, span validation rule)
7. Versioning and Review Cadence
8. References (18 primary sources)

## Assumptions Applied

- Content language: English (tech content per i18n-guide; no user-facing strings in this file)
- OTel semconv version pinned to 1.27.0 (2024-11 release, most recent stable at knowledge cutoff)
- `tls.*` Development status verified against OTel attributes registry
- `network.connection.*` Development; `network.*` core Stable — per design doc verification log
- W3C Baggage Recommendation date: 2022-12-22 (taken from W3C TR)
- ISO/IEC 27001 referenced as 27001:2022 (current edition)

## Risks

- Semconv stability tiers change on each OTel minor release; quarterly review cadence in Section 7 mitigates staleness.
- W3C Trace Context L2 is still CR; promotion to Recommendation would require a note update but no structural change.
- Cloud hypervisor time sync behavior may change; Azure link provided as primary source for drift behavior.

## Validation Steps

1. Verify file exists: `ls -la /Users/gracefullight/workspace/oh-my-agent/.agents/skills/oma-observability/resources/standards.md`
2. Confirm line count in 150-300 range: `wc -l` returns 212.
3. Confirm all 8 sections present: `grep "^## " standards.md`
4. Confirm no forward oma-X references: `grep -i "future oma" standards.md` returns empty.
5. On next quarterly review: check OTel semconv changelog for any Development → RC or RC → Stable promotions and update Section 3 table + file header.
