import { renderHook, act, waitFor } from "@testing-library/react";
import { describe, it, expect, vi, beforeEach } from "vitest";
import * as envBundleConnect from "@/lib/api/facade/envBundleConnect";
import * as agentConnect from "@/lib/api/facade/agentConnect";

vi.mock("@/lib/api/facade/envBundleConnect", () => ({
  listEnvBundles: vi.fn(),
  createEnvBundle: vi.fn(),
  updateEnvBundle: vi.fn(),
  deleteEnvBundle: vi.fn(),
  setPrimaryEnvBundle: vi.fn(),
  getEnvBundle: vi.fn(),
}));
const mockListEnvBundles = vi.mocked(envBundleConnect.listEnvBundles);
const mockCreateEnvBundle = vi.mocked(envBundleConnect.createEnvBundle);
const mockUpdateEnvBundle = vi.mocked(envBundleConnect.updateEnvBundle);

const mockListAgents = vi.fn();

// Keep useCurrentOrg stable across renders — returning a fresh object on
// every call breaks the useCallback memoization in useAgentCredentials and
// causes an infinite re-render loop in the test.
const STABLE_ORG = { slug: "test-org" };
vi.mock("@/stores/auth", async (importOriginal) => {
  const actual = await importOriginal<typeof import("@/stores/auth")>();
  return {
    ...actual,
    useCurrentOrg: () => STABLE_ORG,
  };
});

import { useAgentCredentials } from "../useAgentCredentials";
import type { CredentialFormData } from "../types";

const mockTranslate = (key: string) => key;

describe("useAgentCredentials - handleSaveProfile error handling", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockListEnvBundles.mockResolvedValue({ items: [], total: 0 });
    mockListAgents.mockResolvedValue({
      builtin_agents: [{ name: "Claude", slug: "claude-code", is_builtin: true, is_active: true }],
      custom_agents: [],
      agents: [],
    });

    vi.spyOn(agentConnect, "listAgents").mockImplementation(mockListAgents);
  });

  it("should propagate API errors from create to caller", async () => {
    mockCreateEnvBundle.mockRejectedValue(new Error("Network error"));

    const { result } = renderHook(() => useAgentCredentials(mockTranslate));
    await waitFor(() => expect(result.current.loading).toBe(false));

    const formData: CredentialFormData = {
      name: "Test Bundle",
      description: "",
      credentials: { ANTHROPIC_API_KEY: "sk-test" },
    };

    await expect(
      act(async () => {
        await result.current.handleSaveProfile("claude-code", formData, null);
      })
    ).rejects.toThrow("Network error");
  });

  it("should propagate API errors from update to caller", async () => {
    mockUpdateEnvBundle.mockRejectedValue(new Error("Unauthorized"));

    const { result } = renderHook(() => useAgentCredentials(mockTranslate));
    await waitFor(() => expect(result.current.loading).toBe(false));

    const editingProfile = {
      id: 5,
      user_id: 1,
      agent_slug: "claude-code",
      name: "Existing",
      is_runner_host: false,
      is_default: false,
      is_active: true,
      created_at: "2024-01-01",
      updated_at: "2024-01-01",
    };

    const formData: CredentialFormData = {
      name: "Updated",
      description: "",
      credentials: { ANTHROPIC_API_KEY: "sk-new" },
    };

    await expect(
      act(async () => {
        await result.current.handleSaveProfile("claude-code", formData, editingProfile);
      })
    ).rejects.toThrow("Unauthorized");
  });

  it("should set success message and call loadData on successful create", async () => {
    // The hook reads back `EnvBundle` shape after a successful create — give it
    // a minimal one that satisfies the projection.
    mockCreateEnvBundle.mockResolvedValue({
      $typeName: "proto.env_bundle.v1.EnvBundle",
      id: BigInt(1), ownerScope: "user", ownerId: BigInt(1), name: "New Bundle",
      agentSlug: "claude-code",
      kind: "credential", kindPrimary: false, isActive: true,
      configuredFields: [], configuredValues: {},
      createdAt: "x", updatedAt: "x",
    });

    const { result } = renderHook(() => useAgentCredentials(mockTranslate));
    await waitFor(() => expect(result.current.loading).toBe(false));

    const formData: CredentialFormData = {
      name: "New Bundle",
      description: "",
      credentials: { ANTHROPIC_API_KEY: "sk-test" },
    };

    await act(async () => {
      await result.current.handleSaveProfile("claude-code", formData, null);
    });

    expect(mockCreateEnvBundle).toHaveBeenCalledTimes(1);
    expect(result.current.success).toBe("settings.agentCredentials.profileCreated");
    // Loaded once at mount + once after save.
    expect(mockListEnvBundles).toHaveBeenCalledTimes(2);
  });
});
