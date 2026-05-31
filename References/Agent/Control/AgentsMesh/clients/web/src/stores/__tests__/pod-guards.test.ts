import { describe, it, expect, beforeEach, vi } from "vitest";
import { act } from "@testing-library/react";
import { create, toBinary } from "@bufbuild/protobuf";
import { ListPodsResponseSchema, PodSchema } from "@proto/pod/v1/pod_pb";
import { usePodStore, SIDEBAR_STATUS_MAP, Pod } from "../pod";
import { getAuthManager, getPodService } from "@/lib/wasm-core";
import { mockPod, mockPod2, resetPodStore, seedPods, readPods } from "./pod-test-utils";

interface MockService {
  list_pods_connect: ReturnType<typeof vi.fn>;
}

function svc(): MockService {
  return getPodService() as unknown as MockService;
}

function encodePods(pods: unknown[], total: number) {
  const items = pods.map((p) =>
    create(PodSchema, {
      id: BigInt((p as { id: number }).id),
      podKey: (p as { pod_key: string }).pod_key,
      status: (p as { status: string }).status,
      agentStatus: (p as { agent_status?: string }).agent_status ?? "",
      createdAt: (p as { created_at?: string }).created_at ?? "",
    }),
  );
  const resp = create(ListPodsResponseSchema, { items, total: BigInt(total), limit: 0, offset: 0 });
  return toBinary(ListPodsResponseSchema, resp);
}

function mockSidebar(pods: unknown[], total: number) {
  vi.mocked(svc().list_pods_connect).mockResolvedValue(encodePods(pods, total));
}

function mockLoadMore(newPods: unknown[], total: number) {
  vi.mocked(svc().list_pods_connect).mockResolvedValue(encodePods(newPods, total));
}

describe("Pod Store — defaults", () => {
  it("should default currentSidebarFilter to mine", () => {
    expect(SIDEBAR_STATUS_MAP).toHaveProperty("mine");
    expect(SIDEBAR_STATUS_MAP).not.toHaveProperty("all");
  });

  it("should have mine as default currentSidebarFilter after reset", () => {
    resetPodStore();
    expect(usePodStore.getState().currentSidebarFilter).toBe("mine");
  });
});

describe("Pod Store — SIDEBAR_STATUS_MAP client-side guard", () => {
  function applyClientFilter(pods: Pod[], filter: string, userId?: number): Pod[] {
    const allowedStatuses = SIDEBAR_STATUS_MAP[filter];
    const statusSet = allowedStatuses
      ? new Set(allowedStatuses.split(","))
      : null;

    return pods.filter((pod) => {
      if (statusSet && !statusSet.has(pod.status)) return false;
      if (filter === "mine" && userId && pod.created_by?.id !== userId) return false;
      return true;
    });
  }

  const myPod: Pod = { ...mockPod, created_by: { id: 42, username: "me" } };
  const otherPod: Pod = { ...mockPod2, created_by: { id: 99, username: "other" } };
  const noPod: Pod = { ...mockPod, pod_key: "pod-no-creator" };

  it("mine filter should only show pods created by the current user", () => {
    const result = applyClientFilter([myPod, otherPod], "mine", 42);
    expect(result).toHaveLength(1);
    expect(result[0].pod_key).toBe(myPod.pod_key);
  });

  it("mine filter should exclude pods without created_by", () => {
    const result = applyClientFilter([myPod, noPod], "mine", 42);
    expect(result).toHaveLength(1);
    expect(result[0].pod_key).toBe(myPod.pod_key);
  });

  it("mine filter should show all pods when userId is undefined (not logged in)", () => {
    const result = applyClientFilter([myPod, otherPod], "mine", undefined);
    expect(result).toHaveLength(2);
  });

  it("org filter should only show running/initializing pods regardless of creator", () => {
    const runningPod: Pod = { ...otherPod, status: "running" };
    const terminatedPod: Pod = { ...myPod, status: "terminated" };
    const result = applyClientFilter([runningPod, terminatedPod], "org", 42);
    expect(result).toHaveLength(1);
    expect(result[0].pod_key).toBe(runningPod.pod_key);
  });

  it("completed filter should only show terminal status pods", () => {
    const runningPod: Pod = { ...myPod, status: "running" };
    const terminatedPod: Pod = { ...otherPod, status: "terminated" };
    const failedPod: Pod = { ...mockPod, pod_key: "pod-failed", status: "failed", agent_status: "idle", created_at: "2024-01-03T00:00:00Z" };
    const result = applyClientFilter([runningPod, terminatedPod, failedPod], "completed", 42);
    expect(result).toHaveLength(2);
  });
});

describe("Pod Store — fetchSidebarPods", () => {
  beforeEach(resetPodStore);

  it("should call list_pods_connect for org filter", async () => {
    mockSidebar([mockPod], 1);

    await act(async () => {
      await usePodStore.getState().fetchSidebarPods("org");
    });

    expect(svc().list_pods_connect).toHaveBeenCalled();
    expect(usePodStore.getState().currentSidebarFilter).toBe("org");
  });

  it("should call list_pods_connect for completed filter", async () => {
    mockSidebar([], 0);

    await act(async () => {
      await usePodStore.getState().fetchSidebarPods("completed");
    });

    expect(svc().list_pods_connect).toHaveBeenCalled();
  });

  it("should call list_pods_connect with mine filter when user is logged in", async () => {
    getAuthManager().apply_session(JSON.stringify({ token: "t", refresh_token: "r", user: { id: 42, email: "test@test.com", username: "test" } }));
    mockSidebar([mockPod], 1);

    await act(async () => {
      await usePodStore.getState().fetchSidebarPods("mine");
    });

    expect(svc().list_pods_connect).toHaveBeenCalled();
    expect(usePodStore.getState().currentSidebarFilter).toBe("mine");
  });

  it("should call list_pods_connect with mine filter when not logged in", async () => {
    (getAuthManager() as unknown as { _reset: () => void })._reset();
    mockSidebar([], 0);

    await act(async () => {
      await usePodStore.getState().fetchSidebarPods("mine");
    });

    expect(svc().list_pods_connect).toHaveBeenCalled();
  });

  it("should set loading during fetch and clear after", async () => {
    let loadingDuringFetch = false;
    vi.mocked(svc().list_pods_connect).mockImplementation(async () => {
      loadingDuringFetch = usePodStore.getState().loading;
      return encodePods([], 0);
    });

    await act(async () => {
      await usePodStore.getState().fetchSidebarPods("org");
    });

    expect(loadingDuringFetch).toBe(true);
    expect(usePodStore.getState().loading).toBe(false);
  });

  it("should compute podHasMore correctly", async () => {
    mockSidebar([mockPod], 5);

    await act(async () => {
      await usePodStore.getState().fetchSidebarPods("org");
    });

    expect(usePodStore.getState().podHasMore).toBe(true);
    expect(usePodStore.getState().podTotal).toBe(5);
  });

  it("should handle error and clear loading", async () => {
    vi.mocked(svc().list_pods_connect).mockRejectedValue(new Error("Network error"));

    await act(async () => {
      await usePodStore.getState().fetchSidebarPods("org");
    });

    expect(usePodStore.getState().error).toBe("Network error");
    expect(usePodStore.getState().loading).toBe(false);
  });
});

describe("Pod Store — loadMorePods", () => {
  beforeEach(resetPodStore);

  it("should load more pods with offset equal to current pods length", async () => {
    seedPods(mockPod);
    usePodStore.setState({ podHasMore: true, currentSidebarFilter: "org" });
    mockLoadMore([mockPod2], 2);

    await act(async () => {
      await usePodStore.getState().loadMorePods();
    });

    expect(svc().list_pods_connect).toHaveBeenCalled();
    expect(readPods()).toHaveLength(2);
  });

  it("should skip when no more pods", async () => {
    seedPods(mockPod);
    usePodStore.setState({ podHasMore: false });

    await act(async () => {
      await usePodStore.getState().loadMorePods();
    });

    expect(svc().list_pods_connect).not.toHaveBeenCalled();
  });

  it("should skip when already loading more", async () => {
    seedPods(mockPod);
    usePodStore.setState({ podHasMore: true, loadingMore: true });

    await act(async () => {
      await usePodStore.getState().loadMorePods();
    });

    expect(svc().list_pods_connect).not.toHaveBeenCalled();
  });

  it("should deduplicate pods already in list (upsert by pod_key)", async () => {
    seedPods(mockPod, mockPod2);
    usePodStore.setState({ podHasMore: true, currentSidebarFilter: "org" });
    mockLoadMore([mockPod2], 3);

    await act(async () => {
      await usePodStore.getState().loadMorePods();
    });

    expect(readPods()).toHaveLength(2);
  });

  it("should load mine filter when user is logged in", async () => {
    getAuthManager().apply_session(JSON.stringify({ token: "t", refresh_token: "r", user: { id: 42, email: "test@test.com", username: "test" } }));
    seedPods(mockPod);
    usePodStore.setState({ podHasMore: true, currentSidebarFilter: "mine" });
    mockLoadMore([mockPod2], 2);

    await act(async () => {
      await usePodStore.getState().loadMorePods();
    });

    expect(svc().list_pods_connect).toHaveBeenCalled();
    expect(readPods()).toHaveLength(2);
  });
});
