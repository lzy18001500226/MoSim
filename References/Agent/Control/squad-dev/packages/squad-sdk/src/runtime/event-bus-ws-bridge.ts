/**
 * EventBus to WebSocket Bridge (Issue #304)
 *
 * Broadcasts EventBus events over a WebSocket server so external
 * consumers (e.g., SquadOffice visualization) can subscribe to
 * real-time SDK events without coupling to OTel.
 *
 * @module runtime/event-bus-ws-bridge
 */

import { WebSocketServer, WebSocket } from 'ws';
import type { EventBus, SquadEvent, UnsubscribeFn } from './event-bus.js';

export interface WSBridgeOptions {
  /** WebSocket server port. Defaults to 6277. */
  port?: number;
  /** Optional host to bind to. Defaults to '127.0.0.1'. */
  host?: string;
}

export interface WSBridgeHandle {
  /** Stop the bridge and close the WebSocket server. */
  close: () => Promise<void>;
  /** The port the WebSocket server is listening on. */
  port: number;
}

/**
 * Start a WebSocket server that broadcasts every EventBus event
 * as a JSON message to all connected clients.
 *
 * Message format matches the SquadOffice WSMessage envelope:
 * ```json
 * { "kind": "event", "payload": { ...SquadEvent... } }
 * ```
 *
 * @returns A handle to close the bridge.
 */
export function startWSBridge(
  bus: EventBus,
  options: WSBridgeOptions = {},
): WSBridgeHandle {
  const port = options.port ?? 6277;
  const host = options.host ?? '127.0.0.1';

  const wss = new WebSocketServer({ port, host });

  const unsubscribe: UnsubscribeFn = bus.subscribeAll((event: SquadEvent) => {
    const message = JSON.stringify({
      kind: 'event',
      payload: serializeEvent(event),
    });

    for (const client of wss.clients) {
      if (client.readyState === WebSocket.OPEN) {
        client.send(message);
      }
    }
  });

  return {
    port,
    close: () =>
      new Promise<void>((resolve, reject) => {
        unsubscribe();
        wss.close((err?: Error) => (err ? reject(err) : resolve()));
      }),
  };
}

/** Serialize a SquadEvent for JSON transport (Date to ISO string). */
function serializeEvent(event: SquadEvent): Record<string, unknown> {
  return {
    type: event.type,
    sessionId: event.sessionId,
    agentName: event.agentName,
    payload: event.payload,
    timestamp: event.timestamp.toISOString(),
  };
}
