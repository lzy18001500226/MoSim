import { describe, it, expect, vi, beforeEach } from "vitest";

const mockCallConnect = vi.fn();
vi.mock("@/lib/connect/transport", () => ({
  callConnect: (...args: unknown[]) => mockCallConnect(...args),
  ConnectError: class ConnectError extends Error {},
}));

import {
  listSkillRegistries,
  createSkillRegistry,
  syncSkillRegistry,
  deleteSkillRegistry,
} from "../adminSkillRegistries";

function fakeProtoRegistry(id: number) {
  return {
    id: BigInt(id),
    repositoryUrl: "https://github.com/org/repo",
    branch: "main",
    sourceType: "auto",
    compatibleAgents: [],
    authType: "none",
    syncStatus: "pending",
    skillCount: 0,
    isActive: true,
    createdAt: "2026-01-01T00:00:00Z",
    updatedAt: "2026-01-01T00:00:00Z",
  };
}

describe("Admin API - Skill Registries (Connect-RPC)", () => {
  beforeEach(() => vi.clearAllMocks());

  it("listSkillRegistries returns snake_case items with total", async () => {
    mockCallConnect.mockResolvedValue({
      items: [fakeProtoRegistry(1), fakeProtoRegistry(2)],
      total: 2n,
    });
    const out = await listSkillRegistries();
    expect(mockCallConnect.mock.calls[0][0]).toBe("proto.extension.v1.SkillRegistryAdminService");
    expect(mockCallConnect.mock.calls[0][1]).toBe("ListSkillRegistries");
    expect(out.total).toBe(2);
    expect(out.items[0]).toMatchObject({
      id: 1,
      organization_id: null,
      repository_url: "https://github.com/org/repo",
      sync_status: "pending",
      skill_count: 0,
      is_active: true,
    });
  });

  it("createSkillRegistry sends camelCase repositoryUrl + branch", async () => {
    mockCallConnect.mockResolvedValue(fakeProtoRegistry(1));
    const out = await createSkillRegistry({
      repository_url: "https://github.com/org/repo",
      branch: "develop",
    });
    expect(mockCallConnect.mock.calls[0][1]).toBe("CreateSkillRegistry");
    expect(mockCallConnect.mock.calls[0][4]).toEqual({
      repositoryUrl: "https://github.com/org/repo",
      branch: "develop",
    });
    expect(out.id).toBe(1);
  });

  it("syncSkillRegistry sends bigint id and unwraps registry", async () => {
    mockCallConnect.mockResolvedValue({ message: "sync completed", registry: fakeProtoRegistry(7) });
    const out = await syncSkillRegistry(7);
    expect(mockCallConnect.mock.calls[0][1]).toBe("SyncSkillRegistry");
    expect(mockCallConnect.mock.calls[0][4]).toEqual({ id: 7n });
    expect(out.message).toBe("sync completed");
    expect(out.registry.id).toBe(7);
  });

  it("syncSkillRegistry throws when backend omits registry", async () => {
    mockCallConnect.mockResolvedValue({ message: "sync completed" });
    await expect(syncSkillRegistry(7)).rejects.toThrow(/missing registry/);
  });

  it("deleteSkillRegistry sends bigint id and resolves to void", async () => {
    mockCallConnect.mockResolvedValue({});
    await expect(deleteSkillRegistry(9)).resolves.toBeUndefined();
    expect(mockCallConnect.mock.calls[0][1]).toBe("DeleteSkillRegistry");
    expect(mockCallConnect.mock.calls[0][4]).toEqual({ id: 9n });
  });
});
