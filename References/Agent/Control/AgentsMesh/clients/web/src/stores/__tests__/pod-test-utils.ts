import { vi } from "vitest";
import { usePodStore, usePods, useCurrentPod, Pod } from "../pod";
import { getPodService } from "@/lib/wasm-core";

export { usePods, useCurrentPod };

export const mockPod: Pod = {
  id: 1,
  pod_key: "pod-abc-123",
  status: "running",
  agent_status: "executing",
  created_at: "2024-01-01T00:00:00Z",
  runner: {
    id: 1,
    node_id: "runner-1",
    status: "online",
  },
};

export const mockPod2: Pod = {
  id: 2,
  pod_key: "pod-def-456",
  status: "running",
  agent_status: "waiting",
  created_at: "2024-01-02T00:00:00Z",
  runner: {
    id: 1,
    node_id: "runner-1",
    status: "online",
  },
};

export function readPods(): Pod[] {
  return JSON.parse(getPodService().pods_json()) as Pod[];
}

export function readCurrentPod(): Pod | null {
  const json = getPodService().current_pod_json();
  if (!json) return null;
  return JSON.parse(json as string) as Pod;
}

export function resetPodStore() {
  vi.clearAllMocks();
  usePodStore.setState({
    _tick: 0,
    loading: false,
    error: null,
    initProgress: {},
    podTotal: 0,
    podHasMore: false,
    loadingMore: false,
    currentSidebarFilter: "mine",
  });
}

export function seedPods(...pods: Pod[]) {
  const store = usePodStore.getState();
  for (const p of pods) store.upsertPod(p);
}

export function seedPodsWithCurrent(current: Pod, ...extra: Pod[]) {
  const store = usePodStore.getState();
  for (const p of [current, ...extra]) store.upsertPod(p);
  store.setCurrentPod(current);
}
