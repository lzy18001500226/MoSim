/**
 * OTel Bridge for TelemetryCollector (Issue #256)
 *
 * Converts TelemetryEvents into OpenTelemetry spans, providing a
 * TelemetryTransport that can be registered via setTelemetryTransport().
 * Additive — the existing transport pipeline is unaffected.
 *
 * @module runtime/otel-bridge
 */

import { SpanStatusCode } from './otel-api.js';
import { getTracer } from './otel.js';
import type { TelemetryEvent, TelemetryTransport } from './telemetry.js';
import type { EventBus, UnsubscribeFn, SquadEvent } from './event-bus.js';

// ============================================================================
// Span mapping
// ============================================================================

function recordSpan(event: TelemetryEvent): void {
  const tracer = getTracer('squad-sdk');
  const attrs: Record<string, string | number | boolean> = {};

  if (event.properties) {
    for (const [k, v] of Object.entries(event.properties)) {
      attrs[k] = v;
    }
  }
  if (event.timestamp) {
    attrs['event.timestamp'] = event.timestamp;
  }

  switch (event.name) {
    case 'squad.init': {
      const span = tracer.startSpan('squad.init', { attributes: attrs });
      span.end();
      break;
    }

    case 'squad.agent.spawn': {
      const span = tracer.startSpan('squad.agent.spawn', { attributes: attrs });
      span.end();
      break;
    }

    case 'squad.error': {
      const span = tracer.startSpan('squad.error', { attributes: attrs });
      span.setStatus({ code: SpanStatusCode.ERROR, message: String(attrs['error'] ?? 'unknown') });
      span.addEvent('exception', {
        'exception.message': String(attrs['error'] ?? attrs['message'] ?? 'unknown error'),
        ...(attrs['stack'] ? { 'exception.stacktrace': String(attrs['stack']) } : {}),
      });
      span.end();
      break;
    }

    case 'squad.run': {
      // Root span for the entire session — start and immediately end
      // (the real duration would be managed by the caller if needed)
      const span = tracer.startSpan('squad.run', { attributes: attrs });
      span.end();
      break;
    }

    case 'squad.upgrade': {
      const span = tracer.startSpan('squad.upgrade', { attributes: attrs });
      span.end();
      break;
    }

    default: {
      // Forward unknown events as generic spans
      const span = tracer.startSpan(event.name, { attributes: attrs });
      span.end();
      break;
    }
  }
}

// ============================================================================
// Public API
// ============================================================================

/**
 * Create a TelemetryTransport that emits OTel spans for each event.
 *
 * Usage:
 * ```ts
 * import { setTelemetryTransport } from './telemetry.js';
 * import { createOTelTransport } from './otel-bridge.js';
 *
 * setTelemetryTransport(createOTelTransport());
 * ```
 *
 * The bridge ignores the `endpoint` parameter — OTel exporter config is
 * managed by the OTel provider initialized via `initializeOTel()`.
 */
export function createOTelTransport(): TelemetryTransport {
  return async (events: TelemetryEvent[], _endpoint: string): Promise<void> => {
    for (const event of events) {
      recordSpan(event);
    }
  };
}

/**
 * Subscribe an {@link EventBus} to OpenTelemetry, creating a span for every
 * event that flows through the bus.
 *
 * This is the **mid-level** OTel integration point — it wires the Squad
 * event bus directly into the OTel trace pipeline. If no `TracerProvider`
 * has been registered (e.g. via {@link initializeOTel}), all spans are
 * automatically no-ops with zero overhead.
 *
 * @param bus - The EventBus instance to bridge.
 * @returns An unsubscribe function. Call it to detach the bridge.
 *
 * @example
 * ```ts
 * import { EventBus, initializeOTel, bridgeEventBusToOTel } from 'squad-sdk';
 *
 * const bus = new EventBus();
 * initializeOTel({ endpoint: 'http://localhost:4318' });
 * const detach = bridgeEventBusToOTel(bus);
 *
 * // Later, to stop bridging:
 * detach();
 * ```
 */
export function bridgeEventBusToOTel(bus: EventBus): UnsubscribeFn {
  return bus.subscribeAll((event: SquadEvent) => {
    const tracer = getTracer('squad-sdk');
    const attrs: Record<string, string | number | boolean> = {
      'event.type': event.type,
    };
    if (event.sessionId) attrs['session.id'] = event.sessionId;
    if (event.agentName) attrs['agent.name'] = event.agentName;

    const span = tracer.startSpan(`squad.${event.type}`, { attributes: attrs });
    if (event.type === 'session:error') {
      span.setStatus({ code: SpanStatusCode.ERROR });
    }
    span.end();
  });
}
