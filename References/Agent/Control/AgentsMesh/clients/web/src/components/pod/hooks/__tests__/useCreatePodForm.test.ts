import { renderHook, act } from "@testing-library/react";
import { describe, it, expect, vi, beforeEach } from "vitest";
import * as podConnect from "@/lib/api/facade/podConnect";
import * as envBundleConnect from "@/lib/api/facade/envBundleConnect";

vi.mock("@/lib/api/facade/envBundleConnect");
const mockListEnvBundles = vi.mocked(envBundleConnect.listEnvBundles);

vi.mock("@/lib/api/facade/podConnect");
const mockCreatePod = vi.mocked(podConnect.createPod);

vi.mock("@/stores/auth", () => ({
  readCurrentOrg: () => ({ slug: "test-org" }),
  useAuthStore: () => ({}),
}));

vi.mock("@/stores/podCreation", () => ({
  usePodCreationStore: () => ({
    lastAgentSlug: null,
    lastRepositoryId: null,
    lastCredentialName: "",
    lastRuntimeBundleNames: [],
    lastBranchName: null,
    setLastChoices: vi.fn(),
    clearLastChoices: vi.fn(),
    _hasHydrated: true,
    setHasHydrated: vi.fn(),
  }),
}));

import { useCreatePodForm } from "../useCreatePodForm";

const mockAgents = [
  { name: "Claude Code", slug: "claude-code", is_builtin: true, is_active: true },
];

describe("useCreatePodForm - bundle via agentfile_layer (SSOT)", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockListEnvBundles.mockResolvedValue({ items: [], total: 0 });
  });

  it("omits USE_ENV_BUNDLE from agentfile_layer when no bundle is selected", async () => {
    mockCreatePod.mockResolvedValue({
      pod: { pod_key: "test-pod", id: 1, status: "initializing", agent_status: "idle" } as never,
    });

    const { result } = renderHook(() => useCreatePodForm(mockAgents, []));

    act(() => {
      result.current.setSelectedAgent("claude-code");
    });

    expect(result.current.selectedCredentialName).toBe("");
    expect(result.current.selectedRuntimeBundleNames).toEqual([]);

    await act(async () => {
      await result.current.submit(1, {}, { cols: 80, rows: 24 });
    });

    expect(mockCreatePod).toHaveBeenCalledTimes(1);
    const [, createArg] = mockCreatePod.mock.calls[0];
    expect(createArg).not.toHaveProperty("credential_profile_id");
    const layer = createArg.agentfile_layer ?? "";
    expect(layer).not.toContain("USE_ENV_BUNDLE");
  });

  it("includes USE_ENV_BUNDLE — credential first then runtime in selection order", async () => {
    const credBundle = {
      $typeName: "proto.env_bundle.v1.EnvBundle" as const,
      id: BigInt(42), ownerScope: "user", ownerId: BigInt(1), agentSlug: "claude-code", name: "My API Key",
      kind: "credential", kindPrimary: false, isActive: true,
      configuredFields: [], configuredValues: {},
      createdAt: "x", updatedAt: "x",
    };
    const runtimeBundle = {
      $typeName: "proto.env_bundle.v1.EnvBundle" as const,
      id: BigInt(43), ownerScope: "user", ownerId: BigInt(1), agentSlug: "claude-code", name: "production-debug",
      kind: "runtime", kindPrimary: false, isActive: true,
      configuredFields: [], configuredValues: {},
      createdAt: "x", updatedAt: "x",
    };
    // useEnvBundles loads credential and runtime in parallel; first call =
    // credential, second = runtime. Order of mockResolvedValueOnce matters.
    mockListEnvBundles.mockReset();
    mockListEnvBundles.mockResolvedValueOnce({ items: [credBundle], total: 1 });
    mockListEnvBundles.mockResolvedValueOnce({ items: [runtimeBundle], total: 1 });
    mockCreatePod.mockResolvedValue({
      pod: { pod_key: "test-pod", id: 1, status: "initializing", agent_status: "idle" } as never,
    });

    const { result } = renderHook(() => useCreatePodForm(mockAgents, []));

    act(() => {
      result.current.setSelectedAgent("claude-code");
    });
    await act(async () => {});

    act(() => {
      result.current.setSelectedCredentialName("My API Key");
      result.current.setSelectedRuntimeBundleNames(["production-debug"]);
    });

    await act(async () => {
      await result.current.submit(1, {}, { cols: 80, rows: 24 });
    });

    expect(mockCreatePod).toHaveBeenCalledTimes(1);
    const [, createArg] = mockCreatePod.mock.calls[0];
    expect(createArg).not.toHaveProperty("credential_profile_id");
    const layer: string = createArg.agentfile_layer ?? "";
    const useLines = layer.split("\n").filter((l) => l.startsWith("USE_ENV_BUNDLE"));
    // Credential always first, then runtime bundles.
    expect(useLines).toEqual([
      'USE_ENV_BUNDLE "My API Key"',
      'USE_ENV_BUNDLE "production-debug"',
    ]);
  });

  it("always sends agentfile_layer via API (SSOT)", async () => {
    mockCreatePod.mockResolvedValue({
      pod: { pod_key: "test-pod", id: 1, status: "initializing", agent_status: "idle" } as never,
    });

    const { result } = renderHook(() => useCreatePodForm(mockAgents, []));

    act(() => {
      result.current.setSelectedAgent("claude-code");
    });

    await act(async () => {
      await result.current.submit(1, {}, { cols: 80, rows: 24 });
    });

    const [, createArg] = mockCreatePod.mock.calls[0];
    expect(createArg).toHaveProperty("agent_slug", "claude-code");
    expect(createArg).not.toHaveProperty("credential_profile_id");
    expect(createArg).not.toHaveProperty("repository_id");
    expect(createArg).not.toHaveProperty("interaction_mode");
    expect(createArg).not.toHaveProperty("branch_name");
    expect(createArg).not.toHaveProperty("prompt");
    expect(createArg).not.toHaveProperty("config_overrides");
  });
});
