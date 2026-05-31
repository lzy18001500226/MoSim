"use client";

import React, { useEffect, useState } from "react";
import { CloudOff } from "lucide-react";

import { flushPendingOps, pendingOpsCount } from "@/stores/blockstoreDispatch";

/**
 * PendingOpsBadge polls the local-storage queue every second. When it is
 * non-empty we render a persistent banner so users can see that their recent
 * edits are waiting to be flushed (either because of a network hiccup or a
 * 5xx from the server). Clicking the badge forces an immediate retry.
 */
export function PendingOpsBadge() {
  const [count, setCount] = useState(0);

  useEffect(() => {
    const tick = () => setCount(pendingOpsCount());
    tick();
    const id = window.setInterval(tick, 1000);
    return () => window.clearInterval(id);
  }, []);

  if (count === 0) return null;

  const handleClick = async () => {
    await flushPendingOps();
    setCount(pendingOpsCount());
  };

  return (
    <button
      type="button"
      onClick={handleClick}
      className="pointer-events-auto fixed bottom-6 left-6 z-50 flex items-center gap-2 rounded-full border border-amber-300 bg-amber-50 px-3 py-1.5 text-xs text-amber-900 shadow hover:bg-amber-100"
      title="Click to retry pending operations now"
    >
      <CloudOff className="h-3.5 w-3.5" />
      <span>{count} pending op{count === 1 ? "" : "s"}</span>
    </button>
  );
}
