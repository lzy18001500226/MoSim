"use client";

import { useEffect, useCallback, useRef, useState } from "react";
import {
  getEventSubscriptionManager,
  resetEventSubscriptionManager,
  onManagerReset,
  type EventType,
  type EventHandler,
  type RealtimeEvent,
  type ConnectionState,
} from "@/lib/realtime";
import { useCurrentUser, useCurrentOrg } from "@/stores/auth";

/**
 * Manages the realtime events connection.
 *
 * After R5-11 the underlying transport is Connect-RPC server streaming
 * driven by the wasm-side `WasmEventsManager`. The hook only triggers
 * connect/disconnect lifecycle around (currentOrg, user) identity —
 * reconnect, auth refresh, and heartbeat live inside Rust core.
 *
 * Used once at the app root level (RealtimeProvider).
 */
export function useRealtimeConnection() {
  const [connectionState, setConnectionState] =
    useState<ConnectionState>("disconnected");
  const currentOrg = useCurrentOrg();
  const user = useCurrentUser();
  const managerRef = useRef(getEventSubscriptionManager());

  // deps use `user?.id` (not `user`) on purpose: useCurrentUser() returns a
  // fresh object reference on every store tick, so the login flow ticks
  // several times in quick succession (token set → user populated → org
  // list fetched → user-me roundtrip). Comparing primitives keeps the
  // effect pinned to actual identity changes (user switch, org switch).
  useEffect(() => {
    if (!currentOrg || !user) {
      void managerRef.current.disconnect();
      return;
    }

    resetEventSubscriptionManager();
    const manager = getEventSubscriptionManager();
    managerRef.current = manager;
    void manager.connect();

    const unsubscribe = manager.onConnectionStateChange(setConnectionState);

    return () => {
      unsubscribe();
      // Delay disconnect to avoid killing connection during React Strict
      // Mode re-mount.
      const currentManager = manager;
      setTimeout(() => {
        if (managerRef.current === currentManager) {
          void currentManager.disconnect();
        }
      }, 100);
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [currentOrg?.id, user?.id]);

  const reconnect = useCallback(() => {
    resetEventSubscriptionManager();
    managerRef.current = getEventSubscriptionManager();
    void managerRef.current.connect();
  }, []);

  return {
    connectionState,
    reconnect,
  };
}

/**
 * Subscribe to a specific event type.
 */
export function useEventSubscription<T = unknown>(
  eventType: EventType,
  handler: EventHandler<T>,
  deps: React.DependencyList = []
) {
  const handlerRef = useRef(handler);

  useEffect(() => {
    handlerRef.current = handler;
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [handler, ...deps]);

  useEffect(() => {
    const wrappedHandler: EventHandler<T> = (event) => {
      handlerRef.current(event);
    };

    let unsubscribe = getEventSubscriptionManager().subscribe(eventType, wrappedHandler);

    const unsubscribeReset = onManagerReset((newManager) => {
      unsubscribe();
      unsubscribe = newManager.subscribe(eventType, wrappedHandler);
    });

    return () => {
      unsubscribe();
      unsubscribeReset();
    };
  }, [eventType]);
}

/**
 * Subscribe to all events.
 */
export function useAllEventsSubscription(
  handler: EventHandler,
  deps: React.DependencyList = []
) {
  const handlerRef = useRef(handler);

  useEffect(() => {
    handlerRef.current = handler;
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [handler, ...deps]);

  useEffect(() => {
    const wrappedHandler: EventHandler = (event) => {
      handlerRef.current(event);
    };

    let unsubscribe = getEventSubscriptionManager().subscribeAll(wrappedHandler);

    const unsubscribeReset = onManagerReset((newManager) => {
      unsubscribe();
      unsubscribe = newManager.subscribeAll(wrappedHandler);
    });

    return () => {
      unsubscribe();
      unsubscribeReset();
    };
  }, []);
}

/**
 * Get the latest event of a specific type as React state.
 */
export function useLatestEvent<T = unknown>(
  eventType: EventType
): RealtimeEvent<T> | null {
  const [latestEvent, setLatestEvent] = useState<RealtimeEvent<T> | null>(null);

  useEventSubscription<T>(
    eventType,
    (event) => {
      setLatestEvent(event as RealtimeEvent<T>);
    },
    []
  );

  return latestEvent;
}
