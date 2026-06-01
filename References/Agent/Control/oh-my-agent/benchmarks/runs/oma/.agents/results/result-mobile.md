# Mobile Agent Result

## Status
COMPLETED

## Summary (C5 — mobile-rum.md)
Wrote `mobile-rum.md` for the `oma-observability` skill, covering all 12 required sections from plan task C5.

## Files Changed (C5)

- `/Users/gracefullight/workspace/oh-my-agent/.agents/skills/oma-observability/resources/layers/L7-application/mobile-rum.md` (created, 275 lines)

## Acceptance Criteria Checklist (C5)

- [x] Offline-first telemetry queuing: Section 3 — disk cap, TTL, dedup, backoff, clock skew note, Keychain/Keystore encryption
- [x] Battery impact: Section 5 — BGAppRefreshTask, WorkManager, low-power detection, Doze, Battery Historian, Kepler reference
- [x] App lifecycle events: Section 4 — iOS/Android/React Native/Flutter hook table, custom semconv, Swift + Kotlin code snippets
- [x] iOS/Android SDK comparison: Section 7 — two tables with coverage, platform breadth, and notes; vendor-categories.md cross-ref
- [x] W3C traceparent propagation to backend: Section 9 — propagation flow diagram, SpanKind.CLIENT/SERVER pairing, session span challenge, cross-app boundary cross-ref

## Additional Sections Delivered (C5)

- OTel mobile SDK status (Section 2) — maturity gap documented
- Network egress observability (Section 6) — cellular throttle, coalescing, cert pinning, PII in URLs
- React Native and Flutter (Section 8) — SDK table, symbolication reference to crash-analytics.md
- Performance metrics table (Section 10) — cold/warm/hot start, ANR, Hang rate, CFR cross-ref
- Matrix cells (Section 11) — L7 x multi-tenant/cross-app/slo/privacy with mobile-specific caveats
- Anti-patterns (Section 12) — 6 candidates for anti-patterns.md Section G

## Out-of-Scope Dependencies Noted (C5)

- `crash-analytics.md` (sibling): symbolication pipeline, CFR computation, dSYM/ProGuard upload
- `web-rum.md` (sibling): in-app WebView telemetry
- `../../boundaries/cross-application.md`: full propagator matrix
- `../../meta-observability.md`: clock skew handling
- `../../signals/privacy.md`: PII field masking detail
- `../../vendor-categories.md`: crash analytics vendor taxonomy

---

## Summary (C6 — crash-analytics.md)
Created `crash-analytics.md` for the `oma-observability` skill, covering all 12 required sections from plan task C6.

## Files Changed (C6)

- `/Users/gracefullight/workspace/oh-my-agent/.agents/skills/oma-observability/resources/layers/L7-application/crash-analytics.md` (created, 358 lines)

The `L7-application/` subdirectory was created by the C5 task and already existed.

## Acceptance Criteria Checklist (C6)

- [x] Crash-Free Rate (CFR) — Session CFR and User CFR formulas with targets by category (99.5%+, 99.9%+)
- [x] Symbolication pipelines — iOS dSYM, Android ProGuard/R8/NDK, React Native (Hermes-aware), Flutter (--split-debug-info), Web sourcemap, Backend OTel exception.*
- [x] Release tracking — `service.version` marker, CI automation requirement, Sentry CLI example, canary rollback cross-reference to `../../boundaries/release.md`
- [x] Vendor comparison matrix — Firebase Crashlytics, Sentry, Bugsnag, Embrace, Datadog Error Tracking with Mobile/Web/Backend/OSS columns and differentiators
- [x] Scope section distinguishing crash analytics from RUM (different KPIs, different pipelines)
- [x] Crash pipeline flow diagram — end-to-end from crash to alert
- [x] ANR (Android, 0.47% threshold) and Hang (iOS, 250ms) detection section
- [x] Breadcrumbs and context section
- [x] Privacy / PII redaction — Sentry `beforeSend` TypeScript snippet, Crashlytics allowlist, Datadog pattern; cross-ref `../../signals/privacy.md`
- [x] CI symbol upload — GitHub Actions conceptual YAML snippet with `service.version` tagging; cross-ref `../../observability-as-code.md`
- [x] Matrix.md cell cross-references (L7 row, 4 cells: multi-tenant/release/privacy/cross-application)
- [x] Anti-patterns section with 6 candidates for `../../anti-patterns.md §Section G`
- [x] All cross-references use `../../` prefix (file is in `layers/L7-application/`)
- [x] No future oma-X skill references
- [x] English content throughout
- [x] Line count: 358 (within 220-360 target)
- [x] Tables for vendor comparison, platform pipelines, anti-patterns, breadcrumbs, context fields
- [x] Code snippets: Sentry `beforeSend` (TypeScript), CI upload (YAML)

---

## Review: oma-observability Mobile Content Audit

### Status
COMPLETED — Verdict: MINOR FIXES

### Files Reviewed

- `/Users/gracefullight/workspace/oh-my-agent/.agents/skills/oma-observability/resources/layers/L7-application/mobile-rum.md`
- `/Users/gracefullight/workspace/oh-my-agent/.agents/skills/oma-observability/resources/layers/L7-application/crash-analytics.md`
- `/Users/gracefullight/workspace/oh-my-agent/.agents/skills/oma-observability/resources/vendor-categories.md` (Crash Analytics section only)

### Checklist Findings

1. **Offline telemetry queuing — BGAppRefreshTask / WorkManager**: ACCURATE. `BGAppRefreshTask` for iOS batch sends and `WorkManager` with network constraint for Android are both correct. The 15-minute minimum OS interval note for `BGAppRefreshTask` is accurate per Apple Background Tasks documentation. Doze mode and App Standby bucket awareness are correctly flagged for Android.

2. **iOS/Android SDK comparison (Sentry Cocoa/Android, DD, Firebase)**: ACCURATE with one minor gap. Sentry Cocoa covering visionOS is correct (added in SDK 8.x). Firebase Crashlytics noting "ANR via NDK" on iOS is slightly misleading — ANR is an Android-only concept; iOS has Hang Rate instead. The iOS Crashlytics row should clarify "breadcrumbs only; no ANR" since ANR does not exist on iOS.

3. **Symbolication pipelines — dSYM / ProGuard/R8 / NDK / RN / Flutter**: ACCURATE. Bitcode deprecation in Xcode 14 is correct. The Hermes bytecode extra sourcemap layer for React Native is correct and an important nuance. Flutter `--split-debug-info` + `--obfuscate` flag requirement is accurate. NDK `.so` debug-info stripping and `--build-id` linkage requirement are correct. No issues found.

4. **CFR, ANR Rate, Hang Rate definitions**: ACCURATE. Session CFR and User CFR formulas are correct. ANR definition (main thread > 5s input dispatch, or > 200ms broadcast) matches Android documentation. iOS Hang threshold of 250ms for Xcode Organizer is correct. MetricKit `MXHangDiagnostic` (iOS 14+) is accurate.

5. **React Native / Flutter sourcemap + native symbol workflow**: ACCURATE. The three-artifact requirement for React Native (JS sourcemap, iOS dSYM, Android mapping.txt) is realistic and matches production workflows. Flutter platform-channel crash caveat requiring both Dart symbols AND native symbols is correct and commonly missed — good to call out explicitly.

6. **Play Store 0.47% ANR threshold**: ACCURATE. The 0.47% of sessions threshold for bad-behavior flagging in Play Console matches current Google Play vitals documentation. The consequence (search suppression / Play Console warning) is also correctly described.

7. **W3C traceparent mobile-to-backend propagation**: ACCURATE. `SpanKind.CLIENT` for mobile outbound and `SpanKind.SERVER` for backend receipt is correct per OTel spec. The session-root-span-in-memory (not disk) guidance to avoid stale context on OS-kill is practical and correct. `tracestate` carrying the sampling decision is correct.

8. **Verdict**: MINOR FIXES

### Specific Issues

- **`mobile-rum.md` Section 7, iOS table, Firebase Crashlytics row**: Coverage lists "ANR (via NDK)" for iOS. ANR is an Android-specific concept (ActivityManager timeout). On iOS the equivalent is Hang Rate. The iOS row should read "Crashes, breadcrumbs" without ANR mention, or explicitly clarify "no ANR equivalent on iOS; see Hang Rate."

- **`crash-analytics.md` Section 2, ANR Rate definition**: The ANR definition in Section 10 (main thread > 5s input dispatch OR > 200ms broadcast) is accurate, but Section 2 omits the broadcast-receiver variant. For completeness add: "or broadcast receiver not completing within 200ms (foreground)."

- No major inaccuracies found. Both files are production-ready with the above minor corrections applied.
