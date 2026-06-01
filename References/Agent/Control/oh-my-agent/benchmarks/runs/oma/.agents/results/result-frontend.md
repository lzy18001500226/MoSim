# Frontend Agent Result

## Status

COMPLETED

## Summary

Reviewed `web-rum.md` (L7 Web RUM layer) and `vendor-categories.md` (RUM + Crash categories) for accuracy. Six of seven checklist items pass. One minor omission found in CSP syntax at `web-rum.md` line 191.

**Verdict: MINOR FIXES**

## Files Reviewed

- `/Users/gracefullight/workspace/oh-my-agent/.agents/skills/oma-observability/resources/layers/L7-application/web-rum.md`
- `/Users/gracefullight/workspace/oh-my-agent/.agents/skills/oma-observability/resources/vendor-categories.md`

## Findings

### PASS — Core Web Vitals 2024 (INP replacing FID)
`web-rum.md` lines 27, 35-37, 318: INP correctly stated as replacing FID in March 2024. Thresholds match Google published values. Anti-pattern G5 reinforces FID deprecation.

### PASS — Browser OTel SDK experimental notice
`web-rum.md` lines 72-73, frontmatter line 8: Distinguishes stable (`sdk-trace-web`, `sdk-metrics`) from experimental (CWV OTel plugin). Instrumentation table lines 76-82 correctly marks all four packages as Stable.

### PASS — Vendor comparison (Sentry / Faro / DD RUM)
`web-rum.md` lines 138-143: Sentry "Partial" OTel (uses envelope protocol), Faro "Yes" OTel (OTel-compatible signals), DD "Partial" (integration but not OTel-native). Fair and consistent with `vendor-categories.md` line 77.

### PASS — allowedTracingUrls / propagateTraceHeaderCorsUrls
`web-rum.md` lines 158-170: OTel JS regex pattern valid. Datadog `{ match, propagatorTypes }` matches DD RUM v5 API. Both correct.

### MINOR FIX — CSP `report-to` syntax (web-rum.md line 191)
`Reporting-Endpoints` header syntax is correct for Reporting API Level 1. SRI at lines 199-205 is correct. However, `report-uri` fallback directive is absent. Firefox did not support `Reporting-Endpoints` until 2023; older browsers silently drop `report-to`-only violation reports.

Recommended fix — add `report-uri` as fallback alongside `report-to`:
```http
Content-Security-Policy: default-src 'self';
  script-src 'self' https://cdn.trusted-vendor.com;
  report-to csp-violations;
  report-uri https://csp-reports.example.com/collect

Reporting-Endpoints: csp-violations="https://csp-reports.example.com/collect"
```

### PASS — Client-server error correlation
`web-rum.md` Section 5, lines 149-176: Working code for both SDKs, CORS prerequisite explained, anti-pattern G6 and circuit-breaker guidance cross-referenced. Actionable.

### PASS — Source map upload CI
`web-rum.md` lines 273-276: Two-step `sentry-cli sourcemaps inject` + `upload` matches current Sentry CLI v2 workflow. Auth token via environment variable is standard and omission is acceptable for documentation.

## Acceptance Criteria Checklist

- [x] INP replacing FID correctly stated
- [x] Browser OTel SDK experimental notice present and accurate
- [x] Vendor comparison (Sentry / Faro / DD RUM) fair
- [x] allowedTracingUrls / propagateTraceHeaderCorsUrls examples correct
- [ ] CSP `report-to` / SRI syntax — minor: `report-uri` fallback missing (web-rum.md line 191)
- [x] Client-server error correlation actionable
- [x] Source map upload CI realistic
- [x] Verdict rendered with specific file:line citations
