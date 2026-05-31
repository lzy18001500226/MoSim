// EventSubscriptionManager — thin TS facade over the wasm-side
// `WasmEventsManager`, which now owns the Connect server-streaming
// connection, reconnect state machine, and idle detection (see
// clients/core/crates/events). The TS layer's only job is to bridge
// subscribe / unsubscribe and event payload conversion.
//
// Previously this class held its own WebSocket transport + reconnect
// timer + ping/pong loop. All of that moved to Rust core in R5-11.

import { getApiClient } from "@/lib/wasm-core";
import type { WasmEventsManager } from "@/lib/wasm-core";
import type {
  EventType,
  EventHandler,
  RealtimeEvent,
  ConnectionState,
} from "./types";

export interface EventSubscriptionManagerOptions {
  onConnectionStateChange?: (state: ConnectionState) => void;
}

export class EventSubscriptionManager {
  private wasm: WasmEventsManager | null = null;
  private connectionState: ConnectionState = "disconnected";
  private connectionStateListeners: Set<(state: ConnectionState) => void> = new Set();

  // wasm subscription ids → TS unsubscribe handles for cleanup tracking.
  // Per-event-type fan-out is server-side; the wasm callback hands us the
  // event JSON, we dispatch to the registered handler set.
  private handlers: Map<EventType, Set<EventHandler>> = new Map();
  private globalHandlers: Set<EventHandler> = new Set();
  // ID of the single underlying "subscribe-all" subscription we register
  // with wasm. We dispatch from TS to per-type handlers ourselves; this
  // keeps the wasm boundary small (one callback, one event-type filter).
  private wasmAllSubId: number | null = null;
  private wasmStateSubId: number | null = null;

  constructor(options: EventSubscriptionManagerOptions = {}) {
    if (options.onConnectionStateChange) {
      this.connectionStateListeners.add(options.onConnectionStateChange);
    }
  }

  private ensureWasm(): WasmEventsManager {
    if (!this.wasm) {
      this.wasm = getApiClient().create_events_manager();
    }
    // Property writes don't narrow `this.wasm`'s union — the assignment
    // above guarantees non-null at this point.
    return this.wasm!;
  }

  private setConnectionState(state: ConnectionState): void {
    if (this.connectionState === state) return;
    this.connectionState = state;
    this.connectionStateListeners.forEach((listener) => {
      try { listener(state); }
      catch (error) {
        console.error("[EventSubscriptionManager] state listener error:", error);
      }
    });
  }

  async connect(): Promise<void> {
    const w = this.ensureWasm();

    if (this.wasmAllSubId === null) {
      this.wasmAllSubId = await w.subscribe_all((eventJson: string) => {
        try {
          const event = JSON.parse(eventJson) as RealtimeEvent;
          this.dispatch(event);
        } catch (error) {
          console.error("[EventSubscriptionManager] parse event:", error);
        }
      });
    }

    if (this.wasmStateSubId === null) {
      this.wasmStateSubId = await w.on_connection_state_change((stateStr: string) => {
        this.setConnectionState(stateStr as ConnectionState);
      });
    }

    await w.connect();
  }

  async disconnect(): Promise<void> {
    const w = this.wasm;
    if (!w) return;
    if (this.wasmAllSubId !== null) {
      await w.unsubscribe(this.wasmAllSubId);
      this.wasmAllSubId = null;
    }
    if (this.wasmStateSubId !== null) {
      await w.unsubscribe(this.wasmStateSubId);
      this.wasmStateSubId = null;
    }
    await w.disconnect();
    this.setConnectionState("disconnected");
  }

  subscribe<T = unknown>(eventType: EventType, handler: EventHandler<T>): () => void {
    if (!this.handlers.has(eventType)) this.handlers.set(eventType, new Set());
    this.handlers.get(eventType)!.add(handler as EventHandler);
    return () => { this.handlers.get(eventType)?.delete(handler as EventHandler); };
  }

  subscribeAll(handler: EventHandler): () => void {
    this.globalHandlers.add(handler);
    return () => { this.globalHandlers.delete(handler); };
  }

  getConnectionState(): ConnectionState { return this.connectionState; }

  onConnectionStateChange(listener: (state: ConnectionState) => void): () => void {
    this.connectionStateListeners.add(listener);
    listener(this.connectionState);
    return () => { this.connectionStateListeners.delete(listener); };
  }

  private dispatch(event: RealtimeEvent): void {
    this.handlers.get(event.type)?.forEach((handler) => {
      try { handler(event); }
      catch (error) {
        console.error(`[EventSubscriptionManager] handler error for ${event.type}:`, error);
      }
    });
    this.globalHandlers.forEach((handler) => {
      try { handler(event); }
      catch (error) {
        console.error("[EventSubscriptionManager] global handler error:", error);
      }
    });
  }
}
