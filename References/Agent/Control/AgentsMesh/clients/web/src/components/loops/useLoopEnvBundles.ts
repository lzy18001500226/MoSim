"use client";

import { useEffect, useState } from "react";
import { listEnvBundles, type EnvBundle } from "@/lib/api/facade/envBundleConnect";
import type { EnvBundleSummary } from "@/lib/viewModels/envBundleSummary";

/**
 * useLoopEnvBundles — fetch credential + runtime EnvBundles for the selected
 * agent. Reactive to dialog `open` state and the agent slug; cancels in-flight
 * loads when either changes so we never set state on a stale request.
 *
 * Mirrors `useEnvBundles` in CreatePodForm: both kinds load in parallel so one
 * empty/failed list doesn't suppress the other.
 */
export function useLoopEnvBundles(args: {
  open: boolean;
  agentSlug: string | null;
}): {
  envBundles: EnvBundleSummary[];
  loadingBundles: boolean;
} {
  const { open, agentSlug } = args;
  const [envBundles, setEnvBundles] = useState<EnvBundleSummary[]>([]);
  const [loadingBundles, setLoadingBundles] = useState(false);

  useEffect(() => {
    if (!open || !agentSlug) {
      setEnvBundles([]);
      return;
    }
    let cancelled = false;
    const load = async () => {
      setLoadingBundles(true);
      try {
        const [credRes, runtimeRes] = await Promise.all([
          listEnvBundles({ kind: "credential", agentSlug }).catch(() => ({ items: [] })),
          listEnvBundles({ kind: "runtime", agentSlug }).catch(() => ({ items: [] })),
        ]);
        if (cancelled) return;
        const mapBundle = (b: EnvBundle): EnvBundleSummary => ({
          id: Number(b.id),
          name: b.name,
          agent_slug: b.agentSlug ?? agentSlug,
          kind: b.kind,
          kind_primary: b.kindPrimary,
          configured_fields:
            b.configuredFields.length > 0 ? b.configuredFields : undefined,
        });
        const credBundles: EnvBundleSummary[] = (credRes.items ?? []).map(mapBundle);
        const runtimeBundles: EnvBundleSummary[] = (runtimeRes.items ?? []).map(mapBundle);
        setEnvBundles([...credBundles, ...runtimeBundles]);
      } catch {
        if (!cancelled) setEnvBundles([]);
      } finally {
        if (!cancelled) setLoadingBundles(false);
      }
    };
    load();
    return () => {
      cancelled = true;
    };
  }, [open, agentSlug]);

  return { envBundles, loadingBundles };
}
