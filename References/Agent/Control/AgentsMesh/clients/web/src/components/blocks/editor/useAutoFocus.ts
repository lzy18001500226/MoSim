"use client";

import { useEffect } from "react";

import { useBlockstoreStore } from "@/stores/blockstore";

/**
 * Returns true exactly once — the render immediately after someone called
 * requestFocus(blockID). The hook schedules a microtask to clear the signal
 * so the consumer block grabs the DOM focus and no other render re-triggers.
 */
export function useAutoFocusIfPending(blockID: string): boolean {
  const shouldFocus = useBlockstoreStore((s) => s.pendingFocusBlockID === blockID);
  const clear = useBlockstoreStore((s) => s.actions.clearPendingFocus);
  useEffect(() => {
    if (!shouldFocus) return;
    queueMicrotask(clear);
  }, [shouldFocus, clear]);
  return shouldFocus;
}
