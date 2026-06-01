/**
 * Resilient @opentelemetry/api wrapper (Issue #247)
 *
 * Re-exports the subset of @opentelemetry/api that Squad uses, with
 * automatic no-op fallbacks when the package is not installed.  This
 * makes telemetry truly optional at runtime — the SDK never crashes
 * due to a missing OpenTelemetry dependency.
 *
 * @module runtime/otel-api
 */

import { createRequire } from 'node:module';

// ---------------------------------------------------------------------------
// Dynamic load — graceful fallback when @opentelemetry/api is absent
// ---------------------------------------------------------------------------

let _api: typeof import('@opentelemetry/api') | undefined;
try {
  const _require = createRequire(import.meta.url);
  _api = _require('@opentelemetry/api');
} catch {
  // @opentelemetry/api not installed — all telemetry becomes no-op
}

// ---------------------------------------------------------------------------
// No-op implementations (mirror the @opentelemetry/api surface we use)
// ---------------------------------------------------------------------------

/* eslint-disable @typescript-eslint/no-explicit-any */

const _noopSpan: any = {
  end() {},
  setStatus() { return _noopSpan; },
  setAttribute() { return _noopSpan; },
  setAttributes() { return _noopSpan; },
  addEvent() { return _noopSpan; },
  recordException() { return _noopSpan; },
  isRecording() { return false; },
  updateName() { return _noopSpan; },
  spanContext() { return { traceId: '', spanId: '', traceFlags: 0 }; },
};

const _noopTracer: any = {
  startSpan() { return _noopSpan; },
  startActiveSpan(...args: any[]) {
    const fn = args[args.length - 1];
    if (typeof fn === 'function') return fn(_noopSpan);
  },
};

const _noopInstrument: any = {
  add() {},
  record() {},
  addCallback() {},
  removeCallback() {},
};

const _noopMeter: any = {
  createCounter() { return _noopInstrument; },
  createUpDownCounter() { return _noopInstrument; },
  createHistogram() { return _noopInstrument; },
  createObservableCounter() { return _noopInstrument; },
  createObservableUpDownCounter() { return _noopInstrument; },
  createObservableGauge() { return _noopInstrument; },
  createGauge() { return _noopInstrument; },
};

/* eslint-enable @typescript-eslint/no-explicit-any */

// ---------------------------------------------------------------------------
// Exports — real API when available, no-ops otherwise
// ---------------------------------------------------------------------------

/** Span status codes. */
export const SpanStatusCode: { readonly UNSET: 0; readonly OK: 1; readonly ERROR: 2 } =
  _api?.SpanStatusCode ?? ({ UNSET: 0, OK: 1, ERROR: 2 } as const);

/** Trace API entry point. */
export const trace = _api?.trace ?? {
  getTracer(): typeof _noopTracer { return _noopTracer; },
};

/** Metrics API entry point. */
export const metrics = _api?.metrics ?? {
  getMeter(): typeof _noopMeter { return _noopMeter; },
};

/** Diagnostics API. */
export const diag: any = _api?.diag ?? { // eslint-disable-line @typescript-eslint/no-explicit-any
  setLogger() {},
  disable() {},
  verbose() {},
  debug() {},
  info() {},
  warn() {},
  error() {},
};

/** Diagnostics console logger class. */
export const DiagConsoleLogger: any = _api?.DiagConsoleLogger ?? class NoopDiagLogger {}; // eslint-disable-line @typescript-eslint/no-explicit-any

/** Diagnostics log level enum. */
export const DiagLogLevel: any = _api?.DiagLogLevel ?? { // eslint-disable-line @typescript-eslint/no-explicit-any
  NONE: 0, ERROR: 30, WARN: 50, INFO: 60, DEBUG: 70, VERBOSE: 80, ALL: 9999,
};

/** Whether @opentelemetry/api was successfully loaded. */
export const otelApiAvailable: boolean = _api !== undefined;

// Type re-exports — compile-time only, erased at runtime
export type Tracer = import('@opentelemetry/api').Tracer;
export type Meter = import('@opentelemetry/api').Meter;
