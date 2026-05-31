import { create } from "zustand";
import { useMemo } from "react";
import { ApiError } from "@/lib/api/api-types";
import { reconnectRegistry } from "@/lib/realtime";
import { readCurrentOrg, readCurrentUser } from "@/stores/auth";
import { getErrorMessage } from "@/lib/utils";
import { initWasmCore, getPodState } from "@/lib/wasm-core";
import {
  listPods as listPodsConnect,
  getPod as getPodConnect,
  terminatePod as terminatePodConnect,
  updatePodAlias as updatePodAliasConnect,
  updatePodPerpetual as updatePodPerpetualConnect,
} from "@/lib/api/facade/podConnect";
import type { PodState, Pod } from "./podTypes";
import { SIDEBAR_STATUS_MAP, SIDEBAR_PAGE_SIZE } from "./podTypes";

export type { Pod } from "./podTypes";
export { SIDEBAR_STATUS_MAP } from "./podTypes";

function orgSlug(): string {
  return readCurrentOrg()?.slug ?? "";
}

function sidebarStatusParam(filter: string): string | undefined {
  return SIDEBAR_STATUS_MAP[filter];
}

export function usePods(): Pod[] {
  const tick = usePodStore((s) => s._tick);
  return useMemo(() => JSON.parse(getPodState().pods_json()) as Pod[], [tick]);
}

export function usePod(podKey: string | undefined): Pod | undefined {
  const tick = usePodStore((s) => s._tick);
  return useMemo(() => {
    if (!podKey) return undefined;
    const json = getPodState().get_pod_json(podKey);
    if (!json) return undefined;
    return JSON.parse(json as string) as Pod;
  }, [tick, podKey]);
}

export function useCurrentPod(): Pod | null {
  const tick = usePodStore((s) => s._tick);
  return useMemo(() => {
    const json = getPodState().current_pod_json();
    if (!json) return null;
    return JSON.parse(json as string) as Pod;
  }, [tick]);
}

const fetchPodInflight = new Map<string, Promise<void>>();
const bump = () => usePodStore.setState((s) => ({ _tick: s._tick + 1 }));

export const usePodStore = create<PodState>((set, get) => ({
  _tick: 0, loading: false, error: null, initProgress: {},
  podTotal: 0, podHasMore: false, loadingMore: false, currentSidebarFilter: "mine",

  fetchPods: async (filters) => {
    await initWasmCore();
    set({ error: null });
    try {
      const { items } = await listPodsConnect(orgSlug(), {
        status: filters?.status,
      });
      getPodState().set_pods(JSON.stringify(items));
      bump();
    } catch (error: unknown) {
      set({ error: getErrorMessage(error, "Failed to fetch pods") });
    }
  },

  fetchPod: async (podKey) => {
    const inflight = fetchPodInflight.get(podKey);
    if (inflight) return inflight;
    const promise = (async () => {
      await initWasmCore();
      try {
        const pod = await getPodConnect(orgSlug(), podKey);
        getPodState().upsert_pod(JSON.stringify(pod));
        bump();
      } catch (error: unknown) {
        console.warn("[PodStore] fetchPod failed for", podKey, error);
        throw error;
      } finally { fetchPodInflight.delete(podKey); }
    })();
    fetchPodInflight.set(podKey, promise);
    return promise;
  },

  fetchSidebarPods: async (statusFilter) => {
    await initWasmCore();
    set({ loading: true, error: null, currentSidebarFilter: statusFilter });
    try {
      const uid = statusFilter === "mine" ? readCurrentUser()?.id ?? null : null;
      const { items, total } = await listPodsConnect(orgSlug(), {
        status: sidebarStatusParam(statusFilter),
        created_by_id: uid ?? undefined,
        limit: SIDEBAR_PAGE_SIZE,
        offset: 0,
      });
      getPodState().set_pods(JSON.stringify(items));
      const hasMore = items.length < total;
      set({ podTotal: total, podHasMore: hasMore, loading: false, _tick: get()._tick + 1 });
    } catch (error: unknown) {
      set({ error: getErrorMessage(error, "Failed to fetch pods"), loading: false });
    }
  },

  loadMorePods: async () => {
    const { podHasMore, loadingMore, currentSidebarFilter } = get();
    if (!podHasMore || loadingMore) return;
    await initWasmCore();
    set({ loadingMore: true });
    try {
      const uid = currentSidebarFilter === "mine" ? readCurrentUser()?.id ?? null : null;
      const existing: Pod[] = JSON.parse(getPodState().pods_json());
      const { items: newPods, total } = await listPodsConnect(orgSlug(), {
        status: sidebarStatusParam(currentSidebarFilter),
        created_by_id: uid ?? undefined,
        limit: SIDEBAR_PAGE_SIZE,
        offset: existing.length,
      });
      const state = getPodState();
      for (const pod of newPods) state.upsert_pod(JSON.stringify(pod));
      const allCount = (JSON.parse(state.pods_json()) as Pod[]).length;
      const hasMore = allCount < total;
      set((s) => {
        if (s.currentSidebarFilter !== currentSidebarFilter) return { loadingMore: false };
        return { podTotal: total, podHasMore: hasMore, loadingMore: false, _tick: s._tick + 1 };
      });
    } catch (error: unknown) {
      set({ error: getErrorMessage(error, "Failed to load more pods"), loadingMore: false });
    }
  },

  terminatePod: async (podKey) => {
    try {
      await terminatePodConnect(orgSlug(), podKey);
      getPodState().update_pod_status(podKey, "terminated", undefined, undefined, undefined);
    } catch (error: unknown) {
      const msg = error instanceof Error ? error.message : String(error);
      const isNotFound = (error instanceof ApiError && error.status === 404) || msg.includes("404");
      if (!isNotFound) { set({ error: getErrorMessage(error, "Failed to terminate pod") }); throw error; }
    }
    bump();
  },

  upsertPod: (pod) => {
    getPodState().upsert_pod(JSON.stringify(pod));
    bump();
  },

  setCurrentPod: (pod) => {
    getPodState().set_current_pod(pod ? JSON.stringify(pod) : "");
    bump();
  },

  updatePodStatus: (podKey, status, agentStatus, errorCode, errorMessage) => {
    getPodState().update_pod_status(podKey, status, agentStatus ?? undefined, errorCode ?? undefined, errorMessage ?? undefined);
    bump();
  },

  updateAgentStatus: (podKey, agentStatus) => {
    getPodState().update_agent_status(podKey, agentStatus);
    bump();
  },

  updatePodTitle: (podKey, title) => {
    getPodState().update_pod_title(podKey, title);
    bump();
  },

  updatePodAliasFromEvent: (podKey, alias) => {
    getPodState().update_pod_alias(podKey, alias ?? "");
    bump();
  },

  updatePodAlias: async (podKey, alias) => {
    await initWasmCore();
    try {
      await updatePodAliasConnect(orgSlug(), podKey, alias);
      getPodState().update_pod_alias(podKey, alias ?? "");
      bump();
    } catch (error: unknown) {
      console.warn("[PodStore] updatePodAlias failed, reverting", error);
      bump();
      throw error;
    }
  },

  updatePodPerpetualFromEvent: (podKey, perpetual) => {
    const raw = getPodState().get_pod_json(podKey);
    if (!raw) return;
    const pod = JSON.parse(String(raw)) as Pod;
    getPodState().upsert_pod(JSON.stringify({ ...pod, perpetual }));
    bump();
  },

  updatePodPerpetual: async (podKey, perpetual) => {
    await initWasmCore();
    try {
      await updatePodPerpetualConnect(orgSlug(), podKey, perpetual);
      const raw = getPodState().get_pod_json(podKey);
      if (raw) {
        const pod = JSON.parse(String(raw)) as Pod;
        getPodState().upsert_pod(JSON.stringify({ ...pod, perpetual }));
      }
      bump();
    } catch (error: unknown) {
      set({ error: getErrorMessage(error, "Failed to update perpetual") });
      throw error;
    }
  },

  updatePodInitProgress: (podKey, phase, progress, message) => {
    set((state) => ({ initProgress: { ...state.initProgress, [podKey]: { phase, progress, message } } }));
  },

  clearInitProgress: (podKey) => {
    set((state) => {
      const { [podKey]: _removed, ...rest } = state.initProgress;
      return { initProgress: rest };
    });
  },

  clearError: () => set({ error: null }),
}));

reconnectRegistry.register({
  name: "pod:sidebar",
  fn: () => {
    const s = usePodStore.getState();
    s.fetchSidebarPods?.(s.currentSidebarFilter);
  },
  priority: "immediate",
});
